from odoo import api, models
from ._webhook_mixin import _fire_webhooks

_MODEL = 'crm.lead'


class CrmLead(models.Model):
    _inherit = 'crm.lead'

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
        snapshots = [(r.id, r.display_name, r.name,
                      r.stage_id.id, r.stage_id.name,
                      r.partner_id.id if r.partner_id else None,
                      r.partner_id.display_name if r.partner_id else None,
                      r.expected_revenue, r.probability, r.description)
                     for r in self]
        result = super().unlink()
        for (rec_id, rec_name, name, sid, sname,
             pid, pname, revenue, prob, description) in snapshots:
            fake = type('D', (), {
                'id': rec_id, 'display_name': rec_name, 'name': name,
                'stage_id': type('s', (), {'id': sid, 'name': sname})(),
                'partner_id': type('p', (), {'id': pid, 'display_name': pname})() if pid else None,
                'expected_revenue': revenue,
                'probability': prob,
                'description': description,
            })()
            _fire_webhooks(self.env, _MODEL, fake, 'unlink')
        return result
