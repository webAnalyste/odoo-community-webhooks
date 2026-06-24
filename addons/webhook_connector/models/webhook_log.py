from odoo import fields, models


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
    create_date = fields.Datetime(string='Date', readonly=True)
