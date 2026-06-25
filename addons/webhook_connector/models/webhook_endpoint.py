import json
import logging
import requests
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

ODOO_MODEL_SELECTION = [
    ('res.partner', 'Contact (res.partner)'),
    ('account.move', 'Facture (account.move)'),
    ('sale.order', 'Commande vente (sale.order)'),
    ('crm.lead', 'Opportunité CRM (crm.lead)'),
]

CRUD_ACTION_SELECTION = [
    ('create', 'Création'),
    ('write', 'Modification'),
    ('unlink', 'Suppression'),
]

HTTP_METHOD_SELECTION = [
    ('POST', 'POST'),
    ('PUT', 'PUT'),
    ('PATCH', 'PATCH'),
]


class WebhookEndpoint(models.Model):
    _name = 'webhook.endpoint'
    _description = 'Webhook Endpoint'
    _order = 'odoo_model, crud_action, name'

    name = fields.Char(string='Nom', required=True)
    active = fields.Boolean(default=True)
    odoo_model = fields.Selection(
        selection=ODOO_MODEL_SELECTION,
        string='Modèle Odoo',
        required=True,
    )
    crud_action = fields.Selection(
        selection=CRUD_ACTION_SELECTION,
        string='Action déclenchante',
        required=True,
    )
    url = fields.Char(string='URL Webhook', required=True)
    http_method = fields.Selection(
        selection=HTTP_METHOD_SELECTION,
        string='Méthode HTTP',
        default='POST',
        required=True,
    )
    secret_token = fields.Char(
        string='Token secret',
        help='Envoyé dans le header X-Webhook-Token',
    )
    timeout = fields.Integer(
        string='Timeout (secondes)',
        default=10,
    )
    log_ids = fields.One2many(
        comodel_name='webhook.log',
        inverse_name='endpoint_id',
        string='Historique',
    )
    log_count = fields.Integer(
        string='Nb appels',
        compute='_compute_log_count',
    )

    @api.depends('log_ids')
    def _compute_log_count(self):
        for rec in self:
            rec.log_count = len(rec.log_ids)

    def _build_headers(self):
        headers = {'Content-Type': 'application/json'}
        if self.secret_token:
            headers['Authorization'] = 'Bearer %s' % self.secret_token
        return headers

    def _build_payload(self, record, action):
        """Construit le payload JSON envoyé au webhook."""
        # Pour les vrais records Odoo, on force un refresh pour garantir les données à jour
        is_real_record = hasattr(record, '_name')
        if is_real_record:
            record.invalidate_recordset()

        payload = {
            'action': action,
            'model': self.odoo_model,
            'record_id': record.id if hasattr(record, 'id') else None,
            'record_name': record.display_name if hasattr(record, 'display_name') else None,
            'database': self.env.cr.dbname,
        }
        # Champs supplémentaires selon le modèle
        if self.odoo_model == 'res.partner':
            payload.update({
                'name': record.name,
                'email': record.email,
                'phone': record.phone,
                'company_type': record.company_type,
            })
        elif self.odoo_model == 'account.move':
            payload.update({
                'name': record.name,
                'move_type': record.move_type,
                'state': record.state,
                'partner_id': record.partner_id.id,
                'partner_name': record.partner_id.display_name,
                'amount_total': record.amount_total,
                'currency': record.currency_id.name,
                'invoice_date': str(record.invoice_date) if record.invoice_date else None,
            })
        elif self.odoo_model == 'sale.order':
            payload.update({
                'name': record.name,
                'state': record.state,
                'partner_id': record.partner_id.id,
                'partner_name': record.partner_id.display_name,
                'amount_total': record.amount_total,
                'date_order': str(record.date_order) if record.date_order else None,
            })
        elif self.odoo_model == 'crm.lead':
            payload.update({
                'name': record.name,
                'stage_id': record.stage_id.id,
                'stage_name': record.stage_id.name,
                'partner_id': record.partner_id.id if record.partner_id else None,
                'partner_name': record.partner_id.display_name if record.partner_id else None,
                'expected_revenue': record.expected_revenue,
                'probability': record.probability,
            })
        return payload

    def fire(self, record, action):
        """Appelle le webhook et enregistre le log."""
        self.ensure_one()
        if not self.active:
            return
        payload = self._build_payload(record, action)
        payload_str = json.dumps(payload, default=str)
        status_code = None
        response_text = ''
        success = False
        try:
            resp = getattr(requests, self.http_method.lower())(
                self.url,
                data=payload_str,
                headers=self._build_headers(),
                timeout=self.timeout,
            )
            status_code = resp.status_code
            response_text = resp.text[:2000]
            success = resp.ok
        except requests.exceptions.RequestException as e:
            response_text = str(e)
            _logger.warning('Webhook %s (%s) failed: %s', self.name, self.url, e)

        self.env['webhook.log'].sudo().create({
            'endpoint_id': self.id,
            'action': action,
            'record_id': record.id if hasattr(record, 'id') else 0,
            'payload': payload_str,
            'status_code': status_code,
            'response': response_text,
            'success': success,
        })

    def action_test(self):
        """Bouton de test : envoie un payload fictif."""
        self.ensure_one()

        class FakeRecord:
            id = 0
            display_name = '[TEST]'
            name = '[TEST]'
            email = 'test@example.com'
            phone = ''
            company_type = 'company'
            move_type = 'out_invoice'
            state = 'draft'
            partner_id = type('p', (), {'id': 0, 'display_name': '[TEST]'})()
            amount_total = 0.0
            currency_id = type('c', (), {'name': 'EUR'})()
            invoice_date = None
            date_order = None
            stage_id = type('s', (), {'id': 0, 'name': '[TEST]'})()
            expected_revenue = 0.0
            probability = 0.0

        self.fire(FakeRecord(), 'test')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Webhook testé',
                'message': 'Appel envoyé — vérifiez l\'historique ci-dessous.',
                'type': 'success',
                'sticky': False,
            },
        }

    def action_view_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Historique — %s' % self.name,
            'res_model': 'webhook.log',
            'view_mode': 'list,form',
            'domain': [('endpoint_id', '=', self.id)],
            'context': {'default_endpoint_id': self.id},
        }
