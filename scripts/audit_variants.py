"""
Audit complet des variantes formations : templates + variantes + attributs.
Affiche l'état exact de chaque formation et de ses variantes.
"""
import sys
sys.path.insert(0, '/Users/fscan/Documents/odoo/imports')
from config import DB, USERNAME, PASSWORD, get_connection, make_helpers

uid, obj = get_connection()
sr, create, write, call = make_helpers(uid, obj)

# Tous les templates formation
templates = sr('product.template',
    [('categ_id.complete_name', 'like', 'Formation')],
    ['id', 'name', 'default_code', 'product_variant_count'],
)
print(f"{len(templates)} templates formations\n")
print(f"{'ID':>6}  {'CODE_TMPL':<20}  {'NB':>3}  {'NOM'}")
print("-" * 80)

no_code_tmpl = []
partial_refs = []

for tmpl in sorted(templates, key=lambda t: t['name']):
    tmpl_id = tmpl['id']
    base_code = tmpl['default_code'] or ''
    nb = tmpl['product_variant_count']

    variants = sr('product.product',
        [('product_tmpl_id', '=', tmpl_id)],
        ['id', 'default_code', 'product_template_attribute_value_ids'],
    )

    codes = [v['default_code'] or 'NULL' for v in variants]
    has_null = any(c == 'NULL' for c in codes)
    has_code = any(c != 'NULL' for c in codes)
    partial = has_null and has_code

    flag = ''
    if not base_code:
        flag = ' ⚠ TMPL SANS CODE'
        no_code_tmpl.append(tmpl)
    if partial:
        flag += ' ⚠ PARTIEL'
        partial_refs.append(tmpl)

    print(f"{tmpl_id:>6}  {base_code:<20}  {nb:>3}  {tmpl['name']}{flag}")
    for v in variants:
        ptav_ids = v['product_template_attribute_value_ids']
        attr_names = []
        if ptav_ids:
            ptavs = sr('product.template.attribute.value',
                [('id', 'in', ptav_ids)],
                ['product_attribute_value_id'],
            )
            pav_ids = [p['product_attribute_value_id'][0] for p in ptavs]
            pavs = sr('product.attribute.value', [('id', 'in', pav_ids)], ['name'])
            attr_names = [p['name'] for p in pavs]
        ref = v['default_code'] or 'NULL'
        mark = '✓' if v['default_code'] else '✗'
        print(f"         {mark} [{v['id']:>6}]  {ref:<35}  attrs={attr_names}")

print("\n" + "=" * 80)
print(f"Templates SANS default_code : {len(no_code_tmpl)}")
for t in no_code_tmpl:
    print(f"  [{t['id']}] {t['name']}")
print(f"\nTemplates avec variantes partiellement codées : {len(partial_refs)}")
for t in partial_refs:
    print(f"  [{t['id']}] {t['name']} (code={t['default_code']})")
