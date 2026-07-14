from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    x_terms_sale_order = fields.Html(
        string='Conditions générales — Devis',
        related='company_id.x_terms_sale_order',
        readonly=False,
    )
    x_terms_invoice = fields.Html(
        string='Conditions générales — Facture',
        related='company_id.x_terms_invoice',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    x_terms_sale_order = fields.Html(
        string='Conditions générales — Devis',
        sanitize=True,
    )
    x_terms_invoice = fields.Html(
        string='Conditions générales — Facture',
        sanitize=True,
    )
