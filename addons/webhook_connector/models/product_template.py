from odoo import fields, models

ATTR_SESSION = 'Type de session'
ATTR_MODALITE = 'Modalité'
VAL_SESSION = ['Inter', 'Intra']
VAL_MODALITE = ['Présentiel', 'Distanciel']

SUFFIX_MAP = {
    'Inter': 'inter', 'Intra': 'intra',
    'Présentiel': 'presentiel', 'Distanciel': 'distanciel',
}


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_has_formation_variants = fields.Boolean(
        string='Décliné (4 variantes)',
        compute='_compute_x_has_formation_variants',
        store=False,
    )

    def _compute_x_has_formation_variants(self):
        for tmpl in self:
            is_formation = 'Formation' in (tmpl.categ_id.complete_name or '')
            already_declined = tmpl.product_variant_count >= 4
            # Masquer le bouton si pas une formation OU déjà décliné
            tmpl.x_has_formation_variants = not is_formation or already_declined

    def action_decline_formation_variants(self):
        """Ajoute les valeurs manquantes aux lignes d'attributs formation
        et assigne les refs internes aux variantes qui n'en ont pas.
        Ne supprime jamais les lignes existantes pour préserver les refs."""
        self.ensure_one()

        def get_or_create_attr(name):
            attr = self.env['product.attribute'].search([('name', '=', name)], limit=1)
            if not attr:
                attr = self.env['product.attribute'].create({'name': name})
            return attr

        def get_or_create_val(attr, name):
            val = self.env['product.attribute.value'].search(
                [('attribute_id', '=', attr.id), ('name', '=', name)], limit=1)
            if not val:
                val = self.env['product.attribute.value'].create(
                    {'attribute_id': attr.id, 'name': name})
            return val

        attr_session = get_or_create_attr(ATTR_SESSION)
        attr_modalite = get_or_create_attr(ATTR_MODALITE)
        vals_session = self.env['product.attribute.value'].concat(
            *[get_or_create_val(attr_session, v) for v in VAL_SESSION])
        vals_modalite = self.env['product.attribute.value'].concat(
            *[get_or_create_val(attr_modalite, v) for v in VAL_MODALITE])

        # Trouver les lignes existantes pour chaque attribut
        line_session = self.attribute_line_ids.filtered(
            lambda l: l.attribute_id.id == attr_session.id)
        line_modalite = self.attribute_line_ids.filtered(
            lambda l: l.attribute_id.id == attr_modalite.id)

        if line_session:
            # Ajouter les valeurs manquantes sans toucher aux existantes
            line_session.write({'value_ids': [(4, vid) for vid in vals_session.ids]})
        else:
            self.env['product.template.attribute.line'].create({
                'product_tmpl_id': self.id,
                'attribute_id': attr_session.id,
                'value_ids': [(6, 0, vals_session.ids)],
            })

        if line_modalite:
            line_modalite.write({'value_ids': [(4, vid) for vid in vals_modalite.ids]})
        else:
            self.env['product.template.attribute.line'].create({
                'product_tmpl_id': self.id,
                'attribute_id': attr_modalite.id,
                'value_ids': [(6, 0, vals_modalite.ids)],
            })

        # Nommer uniquement les variantes sans ref interne
        self.env.cr.flush()
        self.invalidate_recordset()
        variants = self.env['product.product'].search(
            [('product_tmpl_id', '=', self.id)], order='id')

        # Déduire le base_code : d'abord depuis le template, sinon depuis
        # une variante existante qui a déjà une ref (ex: form-as0-inter-presentiel → form-as0)
        base_code = self.default_code or ''
        if not base_code:
            for v in variants:
                if v.default_code:
                    parts = v.default_code.split('-')
                    suffix_parts = []
                    for p in parts:
                        if p in ('inter', 'intra'):
                            break
                        suffix_parts.append(p)
                    if suffix_parts:
                        base_code = '-'.join(suffix_parts)
                        break

        named = 0
        for variant in variants:
            if variant.default_code:
                continue  # déjà nommée, on ne touche pas
            if not base_code:
                continue
            ptavs = variant.product_template_attribute_value_ids
            pav_names = ptavs.mapped('product_attribute_value_id.name')
            session = next(
                (SUFFIX_MAP[n] for n in pav_names if n in ('Inter', 'Intra')), '')
            modalite = next(
                (SUFFIX_MAP[n] for n in pav_names if n in ('Présentiel', 'Distanciel')), '')
            if session and modalite:
                variant.default_code = f"{base_code}-{session}-{modalite}"
                named += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '4 variantes prêtes',
                'message': f'Variantes Inter/Intra × Présentiel/Distanciel OK.{" " + str(named) + " référence(s) assignée(s)." if named else ""}',
                'type': 'success',
                'sticky': False,
            },
        }
