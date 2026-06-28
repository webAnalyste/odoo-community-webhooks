from odoo import api, models
from ._webhook_mixin import _fire_webhooks

_MODEL = 'res.partner'


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_name(self):
        """Pour les contacts enfants (type=contact), affiche nom [tags] sans préfixe société."""
        if self.type == 'contact' and self.parent_id and not self.is_company:
            name = self.name or ''
            tags = ', '.join(self.category_id.mapped('name'))
            return '%s [%s]' % (name, tags) if tags else name
        return super()._get_name()

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
