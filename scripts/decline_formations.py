"""
Décline les formations sans variantes complètes en 4 combinaisons :
Inter/Intra × Présentiel/Distanciel

Critère : produits catégorie Formation, 1 seule variante, code sans suffixe inter/intra.
Le script ajoute les 2 lignes d'attributs manquantes via l'ORM Odoo (XML-RPC).
"""
import sys
sys.path.insert(0, '/Users/fscan/Documents/odoo/imports')
from config import DB, USERNAME, PASSWORD, get_connection, make_helpers

uid, obj = get_connection()
sr, create, write, call = make_helpers(uid, obj)

# IDs des attributs et valeurs
ATTR_SESSION_ID = 1   # Type de session
ATTR_MODALITE_ID = 2  # Modalité
VAL_INTER_ID = 1
VAL_INTRA_ID = 2
VAL_PRESENTIEL_ID = 3
VAL_DISTANCIEL_ID = 4

# Formations à décliner (1 variante, code sans suffixe inter/intra)
formations = sr('product.template',
    [('categ_id.complete_name', 'like', 'Formation'),
     ('product_variant_count', '=', 1)],
    ['id', 'name', 'default_code', 'product_variant_ids'],
)

# Filtrer ceux sans suffixe inter/intra
to_decline = [
    f for f in formations
    if f['default_code']
    and '-inter-' not in f['default_code']
    and '-intra-' not in f['default_code']
]

print(f"Formations à décliner : {len(to_decline)}")
for f in to_decline:
    print(f"  [{f['id']}] {f['name']} ({f['default_code']})")

print()
confirm = input(f"Décliner ces {len(to_decline)} formations ? (oui/non) : ")
if confirm.strip().lower() != 'oui':
    print("Annulé.")
    sys.exit(0)

for f in to_decline:
    tmpl_id = f['id']
    name = f['name']
    code = f['default_code']
    print(f"\n→ {name} ({code})")

    # Vérifie si les lignes d'attributs existent déjà
    existing_lines = sr('product.template.attribute.line',
        [('product_tmpl_id', '=', tmpl_id)],
        ['id', 'attribute_id'],
    )
    existing_attr_ids = [l['attribute_id'][0] for l in existing_lines]

    # Ajoute Type de session si manquant
    if ATTR_SESSION_ID not in existing_attr_ids:
        create('product.template.attribute.line', {
            'product_tmpl_id': tmpl_id,
            'attribute_id': ATTR_SESSION_ID,
            'value_ids': [(4, VAL_INTER_ID), (4, VAL_INTRA_ID)],
        })
        print(f"  ✓ Attribut 'Type de session' ajouté (Inter / Intra)")
    else:
        print(f"  — 'Type de session' déjà présent")

    # Ajoute Modalité si manquant
    if ATTR_MODALITE_ID not in existing_attr_ids:
        create('product.template.attribute.line', {
            'product_tmpl_id': tmpl_id,
            'attribute_id': ATTR_MODALITE_ID,
            'value_ids': [(4, VAL_PRESENTIEL_ID), (4, VAL_DISTANCIEL_ID)],
        })
        print(f"  ✓ Attribut 'Modalité' ajouté (Présentiel / Distanciel)")
    else:
        print(f"  — 'Modalité' déjà présente")

    # Mise à jour des références des variantes générées
    variants = sr('product.product',
        [('product_tmpl_id', '=', tmpl_id)],
        ['id', 'product_template_attribute_value_ids', 'default_code'],
    )
    print(f"  → {len(variants)} variantes générées")

    for v in variants:
        attr_vals = sr('product.template.attribute.value',
            [('id', 'in', v['product_template_attribute_value_ids'])],
            ['id', 'name'],
        )
        suffixes = []
        for av in attr_vals:
            n = av['name'].lower()
            if n == 'inter':
                suffixes.append('inter')
            elif n == 'intra':
                suffixes.append('intra')
            elif n == 'présentiel':
                suffixes.append('presentiel')
            elif n == 'distanciel':
                suffixes.append('distanciel')

        # Ordre : session d'abord, puis modalité
        session = next((s for s in suffixes if s in ('inter', 'intra')), '')
        modalite = next((s for s in suffixes if s in ('presentiel', 'distanciel')), '')
        new_code = f"{code}-{session}-{modalite}" if session and modalite else None

        if new_code and v['default_code'] != new_code:
            write('product.product', [v['id']], {'default_code': new_code})
            print(f"    • Variante {v['id']} → {new_code}")

print("\n✓ Terminé.")
