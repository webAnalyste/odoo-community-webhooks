import json
import requests
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class WebhookLog(models.Model):
    _name = 'webhook.log'
    _description = 'Historique des appels webhook'
    _order = 'create_date desc'
    _rec_name = 'create_date'

    endpoint_id = fields.Many2one(
        comodel_name='webhook.endpoint',
        string='Endpoint',
        ondelete='cascade',
        required=True,
        index=True,
    )
    action = fields.Char(string='Action', readonly=True)
    record_id = fields.Integer(string='ID enregistrement', readonly=True)
    payload = fields.Text(string='Payload envoyé', readonly=True)
    status_code = fields.Integer(string='Code HTTP', readonly=True)
    response = fields.Text(string='Réponse', readonly=True)
    success = fields.Boolean(string='Succès', readonly=True)
    retry_count = fields.Integer(string='Tentatives', default=0, readonly=True)
    create_date = fields.Datetime(string='Date', readonly=True)

    def action_retry(self):
        """Rejoue le même payload sur le même endpoint."""
        for log in self:
            endpoint = log.endpoint_id
            if not endpoint:
                continue
            status_code = None
            response_text = ''
            success = False
            try:
                resp = getattr(requests, endpoint.http_method.lower())(
                    endpoint.url,
                    data=log.payload,
                    headers=endpoint._build_headers(),
                    timeout=endpoint.timeout,
                )
                status_code = resp.status_code
                response_text = resp.text[:2000]
                success = resp.ok
            except requests.exceptions.RequestException as e:
                response_text = str(e)
                _logger.warning('Webhook retry %s failed: %s', endpoint.name, e)

            log.sudo().write({
                'status_code': status_code,
                'response': response_text,
                'success': success,
                'retry_count': log.retry_count + 1,
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Webhook rejoué',
                'message': 'Résultat mis à jour dans le log.',
                'type': 'success' if success else 'warning',
                'sticky': False,
            },
        }
