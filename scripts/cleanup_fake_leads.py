"""
Supprime les fausses opportunités créées automatiquement par la passerelle email.
Critères de suppression : toutes les opps avec expected_revenue == 0
et dont le nom ne commence pas par 'forma-' ou 'prest-'.
Affiche d'abord la liste pour validation avant suppression.
"""
import sys
sys.path.insert(0, '/Users/fscan/Documents/odoo/imports')
from config import DB, USERNAME, PASSWORD, get_connection, make_helpers

uid, obj = get_connection()
sr, create, write, call = make_helpers(uid, obj)

# Recherche toutes les opps suspectes : revenu 0 et nom ne commence pas par nos préfixes
leads = sr('crm.lead',
    [('expected_revenue', '=', 0.0), ('type', '=', 'opportunity')],
    ['id', 'name', 'email_from', 'stage_id', 'create_date'],
    limit=0,
)

# Filtre : exclure les vraies opps (préfixes connus)
PREFIXES = ('forma-', 'prest-')
fake = [l for l in leads if not any(l['name'].lower().startswith(p) for p in PREFIXES)]

print(f"Total opps revenue=0 : {len(leads)}")
print(f"Fausses opps à supprimer : {len(fake)}")
print()

for l in fake[:30]:
    print(f"  [{l['id']}] {l['name'][:70]} | {l['email_from']}")

if len(fake) > 30:
    print(f"  ... et {len(fake) - 30} autres")

print()
confirm = input(f"Supprimer ces {len(fake)} opportunités ? (oui/non) : ")
if confirm.strip().lower() != 'oui':
    print("Annulé.")
    sys.exit(0)

ids_to_delete = [l['id'] for l in fake]

# Suppression par batch de 50
batch_size = 50
deleted = 0
for i in range(0, len(ids_to_delete), batch_size):
    batch = ids_to_delete[i:i+batch_size]
    obj.execute_kw(DB, uid, PASSWORD, 'crm.lead', 'unlink', [batch], {})
    deleted += len(batch)
    print(f"  Supprimé {deleted}/{len(ids_to_delete)}...")

print(f"\nTerminé — {deleted} fausses opportunités supprimées.")
