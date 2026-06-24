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

## Facturation électronique — roadmap

- Réforme obligatoire France : septembre 2026
- Repo à réintégrer en août 2026 : https://github.com/akretion/fr-einvoicing (branche 18.0)
  - Nécessite fork Akretion d'OCA/edi : branche `18-account_invoice_facturx-ctc`
  - Dépendance Python : `pyfrctc>=0.10`
  - Remplacera les modules OCA facturx actuels
