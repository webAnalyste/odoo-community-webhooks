from odoo import api, models
from ._webhook_mixin import _fire_webhooks

_MODEL = 'res.partner'


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            _fire_webhooks(self.env, _MODEL, record, 'create')
        return records

    def write(self, vals):
        result = super().write(vals)
        for record in self:
            _fire_webhooks(self.env, _MODEL, record, 'write')
        return result

    def unlink(self):
        # Capture les données avant suppression
        snapshots = [(r.id, r.display_name) for r in self]
        result = super().unlink()
        for rec_id, rec_name in snapshots:
            fake = type('D', (), {'id': rec_id, 'display_name': rec_name,
                                  'name': rec_name, 'email': None,
                                  'phone': None, 'company_type': None})()
            _fire_webhooks(self.env, _MODEL, fake, 'unlink')
        return result
