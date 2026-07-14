"""
Assigne les références internes manquantes aux variantes de formations.
Pattern : {base_code}-{session}-{modalite}
"""
import sys
sys.path.insert(0, '/Users/fscan/Documents/odoo/imports')
from config import DB, USERNAME, PASSWORD, get_connection, make_helpers

uid, obj = get_connection()
sr, create, write, call = make_helpers(uid, obj)

SUFFIX_MAP = {
    'Inter': 'inter', 'Intra': 'intra',
    'Présentiel': 'presentiel', 'Distanciel': 'distanciel',
}

# Toutes les variantes de formations (avec ou sans ref) pour reconstruire proprement
templates = sr('product.template',
    [('categ_id.complete_name', 'like', 'Formation'),
     ('default_code', '!=', False)],
    ['id', 'default_code'],
)

print(f"{len(templates)} templates formations avec base_code")
updated = 0

for tmpl in templates:
    tmpl_id = tmpl['id']
    base_code = tmpl['default_code']

    variants = sr('product.product',
        [('product_tmpl_id', '=', tmpl_id)],
        ['id', 'default_code', 'product_template_attribute_value_ids'],
    )

    for v in variants:
        ptav_ids = v['product_template_attribute_value_ids']
        if not ptav_ids:
            continue

        ptavs = sr('product.template.attribute.value',
            [('id', 'in', ptav_ids)],
            ['product_attribute_value_id'],
        )
        pav_ids = [p['product_attribute_value_id'][0] for p in ptavs]
        pavs = sr('product.attribute.value', [('id', 'in', pav_ids)], ['name'])
        names = [p['name'] for p in pavs]

        session = next((SUFFIX_MAP[n] for n in names if n in ('Inter', 'Intra')), None)
        modalite = next((SUFFIX_MAP[n] for n in names if n in ('Présentiel', 'Distanciel')), None)

        if not session or not modalite:
            continue

        new_code = f"{base_code}-{session}-{modalite}"
        if v['default_code'] != new_code:
            write('product.product', [v['id']], {'default_code': new_code})
            print(f"  [{v['id']}] {v['default_code'] or 'NULL'} → {new_code}")
            updated += 1

print(f"\n✓ {updated} références mises à jour")
