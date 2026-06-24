from odoo import api, models
from ._webhook_mixin import _fire_webhooks

_MODEL = 'account.move'


class AccountMove(models.Model):
    _inherit = 'account.move'

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
        snapshots = [(r.id, r.display_name, r.move_type, r.state,
                      r.partner_id.id, r.partner_id.display_name,
                      r.amount_total, r.currency_id.name, r.invoice_date)
                     for r in self]
        result = super().unlink()
        for (rec_id, rec_name, move_type, state, pid, pname,
             amount, currency, inv_date) in snapshots:
            fake = type('D', (), {
                'id': rec_id, 'display_name': rec_name, 'name': rec_name,
                'move_type': move_type, 'state': state,
                'partner_id': type('p', (), {'id': pid, 'display_name': pname})(),
                'amount_total': amount,
                'currency_id': type('c', (), {'name': currency})(),
                'invoice_date': inv_date,
            })()
            _fire_webhooks(self.env, _MODEL, fake, 'unlink')
        return result
