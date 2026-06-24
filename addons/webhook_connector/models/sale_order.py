from odoo import api, models
from ._webhook_mixin import _fire_webhooks

_MODEL = 'sale.order'


class SaleOrder(models.Model):
    _inherit = 'sale.order'

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
        snapshots = [(r.id, r.display_name, r.name, r.state,
                      r.partner_id.id, r.partner_id.display_name,
                      r.amount_total, r.date_order)
                     for r in self]
        result = super().unlink()
        for (rec_id, rec_name, name, state, pid, pname,
             amount, date_order) in snapshots:
            fake = type('D', (), {
                'id': rec_id, 'display_name': rec_name, 'name': name,
                'state': state,
                'partner_id': type('p', (), {'id': pid, 'display_name': pname})(),
                'amount_total': amount,
                'date_order': date_order,
            })()
            _fire_webhooks(self.env, _MODEL, fake, 'unlink')
        return result
