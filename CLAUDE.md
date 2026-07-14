# CLAUDE.md — Projet Odoo sur mesure

## Contexte

Odoo 18 Community déployé via Coolify sur VPS `vmi1771117`.
Migration depuis Axonaut. URL : https://odoo.webanalyste.com/

Container : `odoo-gm7iq81galclkuzhm0bnwbxu`
Volume addons : `/mnt/extra-addons` (persistant Coolify)
DB : PostgreSQL 16-alpine, user `fscan`

## Apps installées dans Odoo

- Facturation, Vente, CRM, Contacts, Calendrier, Discussion, Tableaux de bord

## Modules OCA installés

Facturation électronique France (dans `/mnt/extra-addons`) :
- `l10n_fr_account_invoice_facturx`, `l10n_fr_siret`
- `account_invoice_facturx`, `base_facturx`, `account_einvoice_generate`
- `uom_unece`, `base_unece`, `account_tax_unece`, `account_payment_unece`
- `account_payment_method_base`
- Dépendance Python : `factur-x`

PEPPOL actif : `9957:FR05481862662`

## Banque

BoursoBank — flux manuel uniquement :
- Export BoursoBank → import fichier (OFX préféré, sinon CSV/XLSX) → rapprochement Odoo
- Aucun connecteur bancaire automatique, aucun identifiant bancaire dans Odoo

## Règles de développement

### Ajouter un module
1. Copier le module dans `/mnt/extra-addons/<nom_module>/`
2. Vérifier `__manifest__.py` à la racine + lire `depends`
3. Copier les dépendances manquantes
4. `chown -R odoo:odoo /mnt/extra-addons`
5. Restart Odoo via Coolify
6. Odoo → Apps → Mettre à jour la liste
7. Installer le module
8. Tester

### Structure correcte d'un module custom
```
/mnt/extra-addons/mon_module/
├── __manifest__.py
├── __init__.py
├── models/
├── views/
├── security/
└── static/ (si assets)
```

### Emplacements
- `/mnt/extra-addons` — modules déployés (source de vérité)
- `/mnt/extra-addons/_oca_src` — clones Git sources OCA
- Ne jamais développer dans `/tmp`, `/root`, `/usr/lib/python3/...`

### Ne pas faire
- Import ZIP via l'interface Odoo (utiliser CLI)
- Désinstaller un module sans audit des données liées
- Installer des connecteurs bancaires online
- Toucher `account`, `account_payment`, `l10n_fr_account` sans sauvegarde préalable

## Rapprochement bancaire — modules OCA cibles

Depuis OCA/account-reconcile :
- `account_statement_base`
- `account_reconcile_oca`
- `account_reconcile_model_oca`

Depuis OCA/bank-statement-import :
- `account_statement_import_base`
- `account_statement_import_file`
- `account_statement_import_file_reconcile_oca`
- `account_statement_import_ofx`
- `account_statement_import_sheet_file`

Ordre d'installation : dans cet ordre exactement (dépendances d'abord).

## Scripts d'intervention locale (méthode privilégiée)

**Toute intervention sur les données Odoo se fait via scripts Python locaux utilisant l'API XML-RPC.**
Ne jamais modifier la DB en SQL brut sans passer par l'ORM Odoo (les champs computed stored ne se recalculent pas en SQL).

### Structure
```
/Users/fscan/Documents/odoo/
├── imports/
│   ├── config.py          ← configuration centrale (URL, DB, clé API)
│   ├── fix_*.py           ← scripts de correction de données
│   └── import_*.py        ← scripts d'import
└── scripts/
    ├── backup_odoo_db.sh  ← script backup (déployé sur VPS)
    └── backup_odoo_db.py  ← backup depuis Mac (usage ponctuel)
```

### Connexion API XML-RPC
```python
import sys
sys.path.insert(0, '/Users/fscan/Documents/odoo/imports')
from config import DB, USERNAME, PASSWORD, get_connection, make_helpers

uid, obj = get_connection()
sr, create, write, call = make_helpers(uid, obj)
```

### Forcer le recalcul d'un champ computed stored
Les champs `qty_invoiced`, `invoice_status` sur `sale.order.line` sont stored.
Après modification SQL directe, ils ne se recalculent pas — passer par l'ORM :
```python
# Unlink + relink la invoice_line pour déclencher le recalcul
obj.execute_kw(DB, uid, PASSWORD, 'sale.order.line', 'write',
    [[line_id], {'invoice_lines': [(3, il_id)]}], {})
obj.execute_kw(DB, uid, PASSWORD, 'sale.order.line', 'write',
    [[line_id], {'invoice_lines': [(4, il_id)]}], {})
# Ou forcer directement si invoice_lines est vide :
obj.execute_kw(DB, uid, PASSWORD, 'sale.order.line', 'write',
    [[line_id], {'qty_invoiced': 0.0}], {})
```

### SSH sur le VPS
```bash
ssh -i ~/.ssh/contabo_key root@207.180.202.230
```

### Containers Docker (Coolify)
| Rôle | Nom container |
|------|--------------|
| Odoo 18 | `odoo-gm7iq81galclkuzhm0bnwbxu` |
| PostgreSQL 16 | `postgresql-gm7iq81galclkuzhm0bnwbxu` |
| Proxy (Traefik) | `coolify-proxy` |

### Volume extra-addons — chemin réel sur l'hôte
```
/var/lib/docker/volumes/gm7iq81galclkuzhm0bnwbxu_odoo-extra-addons/_data/
```
> ⚠️ `/mnt/extra-addons` est le chemin **dans le container**, pas sur l'hôte.  
> `scp` vers `/mnt/extra-addons` sur l'hôte = mauvais répertoire, le container ne le voit pas.

### Déployer un fichier modifié sur le VPS

```bash
# 1. Copier le fichier en local vers /tmp sur le VPS
scp -i ~/.ssh/contabo_key chemin/local/fichier.py root@207.180.202.230:/tmp/fichier.py

# 2. Injecter dans le container (méthode correcte)
ssh -i ~/.ssh/contabo_key root@207.180.202.230 \
  "docker cp /tmp/fichier.py odoo-gm7iq81galclkuzhm0bnwbxu:/mnt/extra-addons/module/controllers/fichier.py"

# 3. Copier aussi dans le volume persistant (pour survie aux redémarrages)
ssh -i ~/.ssh/contabo_key root@207.180.202.230 \
  "cp /tmp/fichier.py /var/lib/docker/volumes/gm7iq81galclkuzhm0bnwbxu_odoo-extra-addons/_data/module/controllers/fichier.py"

# 4. Redémarrer Odoo
ssh -i ~/.ssh/contabo_key root@207.180.202.230 "docker restart odoo-gm7iq81galclkuzhm0bnwbxu"
```

### REST API Connector
- **URL base** : `https://odoo.webanalyste.com/api/v1/`
- **Header auth** : `X-API-Key: <valeur>`
- **Clé API** : stockée dans Odoo → Paramètres → Clé `rest_api_connector.api_key`
- **Générateur d'URL** : https://odoo.webanalyste.com/api/v1/doc

### Connexion PostgreSQL (depuis VPS)
```bash
ssh -i ~/.ssh/contabo_key root@207.180.202.230 \
  "docker exec postgresql-gm7iq81galclkuzhm0bnwbxu psql -U fscan -d odoo -c 'SELECT version();'"
```

## Backup automatique

### Architecture
- **Script** : `/opt/odoo/backup_odoo_db.sh` sur le VPS
- **Cron VPS** : `0 2,14 * * *` (2h et 14h heure serveur, toutes les 12h)
- **Destination** : S3 `s3://wa-odoo/data/coolify/odoo/db_backup/`
- **Rétention** : 15 jours glissants (suppression auto sur S3)
- **Logs** : `/var/log/backup_odoo.log` sur le VPS

### Fonctionnement
1. `pg_dump` dans le container `postgresql-gm7iq81galclkuzhm0bnwbxu` → `/tmp/`
2. Upload S3 `eu-west-3` via `awscli`
3. Nettoyage fichiers S3 > 15 jours

### Credentials S3
- Access Key : voir `scripts/.env` (local, non versionné — copier depuis `scripts/.env.example`)
- Fichier local : `/Users/fscan/Documents/odoo/scripts/.env`

### Vérifier / relancer manuellement
```bash
ssh -i ~/.ssh/contabo_key root@207.180.202.230 "bash /opt/odoo/backup_odoo_db.sh"
ssh -i ~/.ssh/contabo_key root@207.180.202.230 "tail -50 /var/log/backup_odoo.log"
```

### Note : backup Coolify inutilisable
Coolify backup la DB `postgres` (vide) au lieu de `odoo` — fichiers 1KB non valides. Ne pas utiliser.

## Commandes essentielles

```bash
# Entrer dans le conteneur
docker exec -it -u root odoo-gm7iq81galclkuzhm0bnwbxu bash

# Vérifier les modules présents
find /mnt/extra-addons -maxdepth 2 -name "__manifest__.py" | sort

# Corriger les droits
chown -R odoo:odoo /mnt/extra-addons
```

## Doctrine

- Module présent dans `/mnt/extra-addons` ≠ module installé dans Odoo
- Contrôler ce qui est installé, pas seulement ce qui est présent
- Avant tout module touchant compta/factures/ventes : lire `__manifest__.py`, vérifier dépendances, faire une sauvegarde
- Préférer CLI à l'interface graphique pour les opérations sur les modules

## ⛔ RÈGLE ABSOLUE — LIRE AVANT DE JUGER

**NE JAMAIS proposer de refactoring, déplacement ou suppression de code sans avoir :**
1. Lu **tous** les fichiers du module concerné
2. Tracé **toutes les dépendances** (qui appelle quoi, qui consomme quoi)
3. Vérifié que le code jugé "hors-sujet" n'est pas utilisé indirectement ailleurs

**Exemple de catastrophe évitée :** `webhook_connector/models/product_template.py` génère les `default_code` des variantes formation (ex: `form-as1-inter-distanciel`). Ces codes sont remontés dans le payload webhook `product_codes`. Supprimer ce fichier aurait cassé tous les webhooks CRM silencieusement.

**Un nom de fichier ne dit pas ce qu'il fait dans le système. Lire le code, toujours.**

## Facturation électronique — roadmap

- Réforme obligatoire France : septembre 2026
- Repo à réintégrer en août 2026 : https://github.com/akretion/fr-einvoicing (branche 18.0)
  - Nécessite fork Akretion d'OCA/edi : branche `18-account_invoice_facturx-ctc`
  - Dépendance Python : `pyfrctc>=0.10`
  - Remplacera les modules OCA facturx actuels
