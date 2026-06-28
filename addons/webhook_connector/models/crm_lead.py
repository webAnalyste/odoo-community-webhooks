from odoo import api, fields, models
from ._webhook_mixin import _fire_webhooks

_MODEL = 'crm.lead'


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_participants = fields.Integer(string='Nombre de participants')

    x_contact_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact client',
        domain="[('parent_id', '=', partner_id), ('type', '=', 'contact')]",
        tracking=True,
    )

    @api.onchange('x_contact_id')
    def _onchange_x_contact_id(self):
        if self.x_contact_id:
            self.email_from = self.x_contact_id.email
            self.phone = self.x_contact_id.phone or self.x_contact_id.mobile

    @api.onchange('partner_id')
    def _onchange_partner_id_reset_contact(self):
        """Réinitialise x_contact_id si l'entreprise change."""
        if self.x_contact_id and self.x_contact_id.parent_id != self.partner_id:
            self.x_contact_id = False

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
                      r.expected_revenue, r.probability, r.description,
                      r.x_contact_id.id if r.x_contact_id else None,
                      r.x_contact_id.name if r.x_contact_id else None,
                      r.x_contact_id.email if r.x_contact_id else None)
                     for r in self]
        result = super().unlink()
        for (rec_id, rec_name, name, sid, sname,
             pid, pname, revenue, prob, description,
             xcid, xcname, xcemail) in snapshots:
            fake = type('D', (), {
                'id': rec_id, 'display_name': rec_name, 'name': name,
                'stage_id': type('s', (), {'id': sid, 'name': sname})(),
                'partner_id': type('p', (), {'id': pid, 'display_name': pname})() if pid else None,
                'expected_revenue': revenue,
                'probability': prob,
                'description': description,
                'x_contact_id': type('x', (), {'id': xcid, 'name': xcname, 'email': xcemail})() if xcid else None,
            })()
            _fire_webhooks(self.env, _MODEL, fake, 'unlink')
        return result
