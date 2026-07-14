"""
Répare les références internes des variantes formations.
Stratégie :
  1. Pour chaque template : déduire le base_code depuis les variantes existantes
     ou depuis le default_code du template (s'il est propre).
  2. Écrire le bon default_code sur le template s'il est absent/erroné.
  3. Écrire les refs manquantes sur toutes les variantes.

SUFFIX_MAP : session/modalite → suffixe ref
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

# Connu manuellement depuis l'audit : base_codes pour les templates sans code
# extraits depuis les variantes qui ont déjà une ref partielle
KNOWN_CODES = {
    2244: 'form-as4',       # Formation Apps Script 4
    2284: 'form-as0',       # Formation Apps Script parcours
    2282: 'form-bq3',       # Formation Big Query 3
    2283: 'form-bq0',       # Formation Big Query parcours
    2248: 'form-chgpta2',   # Formation ChatGTP Analytics 2
    2287: 'form-ds0',       # Formation Data Studio parcours
    2251: 'form-ga1',       # Formation Google Analytics 1
    2285: 'form-ga0',       # Formation Google Analytics parcours
    2257: 'form-gs0',       # Formation Google Sheets parcours
    2286: 'form-gtm0',      # Formation Google Tag Manager parcours
    2288: 'form-make3',     # Formation Make 3
    2289: 'form-make0',     # Formation Make parcours
    2290: 'form-pw0',       # Formation Piwik Pro parcours
    2277: 'form-search1',   # Formation SEO GEO AEO 1
}

# Cas spécial : Formation Matomo Analytics parcours (2267) — template a pris
# une ref de variante, on la corrige aussi
KNOWN_CODES[2267] = 'form-ma0'

templates = sr('product.template',
    [('categ_id.complete_name', 'like', 'Formation')],
    ['id', 'name', 'default_code'],
)

updated_tmpl = 0
updated_variants = 0
skipped = 0
errors = []

for tmpl in templates:
    tmpl_id = tmpl['id']
    tmpl_code = tmpl['default_code'] or ''

    # Déterminer le base_code
    if tmpl_id in KNOWN_CODES:
        base_code = KNOWN_CODES[tmpl_id]
    else:
        # Vérifier que le default_code du template ne ressemble pas à une ref de variante
        # (contient -inter- ou -intra- → c'est un bug)
        if tmpl_code and ('-inter-' in tmpl_code or '-intra-' in tmpl_code):
            # Extraire le base_code depuis la ref corrompue
            parts = tmpl_code.split('-')
            # Chercher l'index de 'inter' ou 'intra'
            base_parts = []
            for p in parts:
                if p in ('inter', 'intra'):
                    break
                base_parts.append(p)
            base_code = '-'.join(base_parts)
            print(f"  [WARN] Template {tmpl_id} '{tmpl['name']}' a code corrompu '{tmpl_code}' → base_code déduit: '{base_code}'")
        else:
            base_code = tmpl_code

    if not base_code:
        print(f"  [SKIP] Template {tmpl_id} '{tmpl['name']}' — base_code inconnu")
        skipped += 1
        continue

    # Corriger le default_code du template si nécessaire
    if tmpl_code != base_code:
        write('product.template', [tmpl_id], {'default_code': base_code})
        print(f"  [TMPL] {tmpl_id} '{tmpl['name']}' : '{tmpl_code or 'NULL'}' → '{base_code}'")
        updated_tmpl += 1

    # Parcourir toutes les variantes
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
            errors.append(f"  [ERR] Variante {v['id']} attrs={names} — pas session/modalite")
            continue

        new_code = f"{base_code}-{session}-{modalite}"
        if v['default_code'] != new_code:
            write('product.product', [v['id']], {'default_code': new_code})
            print(f"    [{v['id']}] '{v['default_code'] or 'NULL'}' → '{new_code}'")
            updated_variants += 1

print(f"\n{'='*60}")
print(f"Templates corrigés : {updated_tmpl}")
print(f"Variantes mises à jour : {updated_variants}")
print(f"Skipped (base_code inconnu) : {skipped}")
if errors:
    print(f"\nERREURS ({len(errors)}) :")
    for e in errors:
        print(e)
