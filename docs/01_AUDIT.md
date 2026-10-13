# 01_AUDIT — État de l'installation Odoo avant intégration e-invoicing

**Date d'audit** : 2026-10-13
**Auditeur** : Claude Sonnet 4.6
**Instance** : https://odoo.webanalyste.com/
**Statut** : AUDIT TERMINÉ — Gate 1 franchissable sous réserve des points d'attention

---

## 1. Infrastructure

| Composant | Valeur |
|-----------|--------|
| Odoo version | 18.0-20260609 (build du 9 juin 2026) |
| Image Docker | `odoo:18` |
| Python | 3.12.3 |
| PostgreSQL | 16.14 (Alpine, dans container `postgresql-gm7iq81galclkuzhm0bnwbxu`) |
| OS container Odoo | Ubuntu 24.04.4 LTS (Noble Numbat) |
| OS hôte VPS | Linux 5.4.0-105-generic (Ubuntu) |
| Docker | 26.0.0 |
| Reverse proxy | Traefik (Coolify) |
| Espace disque hôte | 588 Go total / 89 Go utilisés / 470 Go libres (16%) |

### Volumes Docker

| Volume | Destination container | Usage |
|--------|-----------------------|-------|
| `gm7iq81galclkuzhm0bnwbxu_odoo-extra-addons` | `/mnt/extra-addons` | Modules custom et OCA |
| `gm7iq81galclkuzhm0bnwbxu_odoo-web-data` | `/var/lib/odoo` | Filestore + sessions |
| `gm7iq81galclkuzhm0bnwbxu_odoo-config` | `/etc/odoo` | odoo.conf |

### Configuration Odoo (odoo.conf)

```ini
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
data_dir = /var/lib/odoo
dbfilter = ^odoo$
list_db = False
admin_passwd = [hashé pbkdf2-sha512]
```

### Sauvegarde automatique

- Script : `/opt/odoo/backup_odoo_db.sh` sur l'hôte VPS
- Cron : toutes les 12h (2h et 14h)
- Destination : S3 `s3://wa-odoo/data/coolify/odoo/db_backup/` (rétention 15 jours)
- Backup Coolify natif : inutilisable (backup `postgres` vide)

---

## 2. Société

| Champ | Valeur |
|-------|--------|
| Raison sociale | Franck Scandolera - EI WEBANALYSTE |
| TVA intracommunautaire | FR05481862662 |
| SIREN | 048186266 (déduit du numéro TVA) |
| APE | 7022Z |
| Adresse | 62 rue Pierre Lescot, 19100 BRIVE-LA-GAILLARDE |
| Email contact PEPPOL | franck@webanalyste.com |

**SIRET** : non renseigné dans la base (`res_company.siret` n'existe pas — le module `l10n_fr_siret` n'est pas installé).

---

## 3. État PEPPOL actuel

| Paramètre | Valeur |
|-----------|--------|
| `account_peppol.edi.mode` | `prod` |
| `account_peppol_proxy_state` | `receiver` |
| Identifiant PEPPOL | `9957:FR05481862662` |
| Mode | **Réception uniquement** |

> **Point important** : PEPPOL est configuré en mode `receiver` (réception) via le proxy Odoo Enterprise IAP (`account_edi_proxy_client` installé, mode `demo`). Ce canal PEPPOL est distinct de la réforme française CTC (Chorus Pro / Plateformes Agréées). Il ne remplace pas l'intégration `fr-einvoicing` Akretion.

---

## 4. Modules installés dans Odoo (102 modules)

### 4.1 Modules natifs Odoo pertinents pour l'e-invoicing

| Module | Version installée | Rôle |
|--------|------------------|------|
| `account` | — | Comptabilité de base |
| `account_edi_ubl_cii` | installé | Génération UBL/CII natif Odoo |
| `account_edi_ubl_cii_payment_unece` | installé | Extension paiement UNECE |
| `account_edi_ubl_cii_tax_extension` | installé | Extension taxe UBL/CII |
| `account_edi_proxy_client` | installé (mode demo) | Client proxy PEPPOL Odoo |
| `account_peppol` | installé | PEPPOL réception/émission |
| `account_peppol_response` | installé | Gestion réponses PEPPOL |
| `account_peppol_selfbilling` | installé | Self-billing PEPPOL |
| `l10n_fr` | installé | Localisation France |
| `l10n_fr_account` | installé | Comptabilité France |
| `l10n_fr_facturx_chorus_pro` | 18.0.1.0 installé | Chorus Pro + Factur-X natif |
| `sale_edi_ubl` | installé | UBL ventes |

### 4.2 Modules OCA installés (e-invoicing / import)

| Module | Version | État | Source |
|--------|---------|------|--------|
| `account_invoice_facturx` | — | présent dans `/mnt/extra-addons` | OCA/edi 18.0 |
| `account_invoice_import` | 18.0.1.1.0 | **installé** | OCA/edi 18.0 |
| `account_invoice_import_facturx` | 18.0.1.0.0 | **installé** | OCA/edi 18.0 |
| `account_invoice_import_ubl` | — | non installé | OCA/edi 18.0 |
| `l10n_fr_account_invoice_facturx` | — | **non installé** | OCA/l10n-france 18.0 |
| `l10n_fr_siret` | — | **non installé** | OCA/l10n-france 18.0 |
| `account_einvoice_generate` | — | présent/installé | OCA/edi 18.0 |
| `base_facturx` | — | **installé** | OCA/edi 18.0 |
| `base_edi` | — | présent | OCA/edi 18.0 |
| `base_business_document_import` | — | **installé** | OCA/edi 18.0 |
| `base_business_document_import_phone` | — | **installé** | OCA/edi 18.0 |
| `base_ubl` | présent | non installé | OCA/edi 18.0 |
| `base_ubl_generate` | présent | non installé | OCA/edi 18.0 |
| `base_ubl_parse` | présent | non installé | OCA/edi 18.0 |
| `uom_unece` | — | **installé** | OCA/community-data-files 18.0 |
| `account_tax_unece` | — | **installé** | OCA/community-data-files 18.0 |
| `account_payment_unece` | — | **installé** | OCA/community-data-files 18.0 |
| `base_unece` | — | **installé** | OCA/community-data-files 18.0 |
| `account_payment_method_base` | — | **installé** | OCA/account-payment 18.0 |

### 4.3 Modules OCA installés (rapprochement bancaire)

| Module | État |
|--------|------|
| `account_reconcile_oca` | installé |
| `account_reconcile_model_oca` | installé |
| `account_statement_base` | installé |
| `account_statement_import_base` | installé |
| `account_statement_import_file` | installé |
| `account_statement_import_file_reconcile_oca` | installé |
| `account_statement_import_ofx` | installé |
| `account_statement_import_sheet_file` | installé |

### 4.4 Modules custom

| Module | État |
|--------|------|
| `webhook_connector` | installé |
| `rest_api_connector` | installé |
| `custom_display` | installé |
| `custom_terms` | installé |

### 4.5 Modules présents dans /mnt/extra-addons mais NON installés

Présents dans le volume mais avec `state != 'installed'` ou absents de la DB :
- `l10n_fr_siret`
- `l10n_fr_account_invoice_facturx`
- `account_invoice_import_ubl`
- `account_invoice_facturx` (présent mais `l10n_fr_account_invoice_facturx` le remplace normalement)
- Série complète OCA account-reconcile non installée (seulement les 3 modules utiles l'ont été)
- Modules UBL : `base_ubl`, `base_ubl_generate`, `base_ubl_parse`, `sale_order_import_ubl`, etc.
- Modules import/export factures : `account_invoice_export`, `account_invoice_download`, etc.

---

## 5. Dépendances Python

### 5.1 Packages pertinents installés

| Package | Version | Requis par CDC |
|---------|---------|----------------|
| `factur-x` | **3.16** | >=7.3 requis — **INCOMPATIBLE** |
| `lxml` | 6.1.1 | OK |
| `Unidecode` | 1.3.8 | OK |
| `pypdf` | 6.14.2 | OK |
| `PyPDF2` | 2.12.1 | OK (legacy) |
| `reportlab` | 4.1.0 | OK |
| `saxonche` | 13.0.0 | OK (XSLT/XSD) |
| `pyfrctc` | **ABSENT** | >=0.23 requis — **MANQUANT** |

### 5.2 Analyse critique des versions Python

**BLOQUANT 1** : `factur-x==3.16`
Le CDC exige `factur-x>=7.3`. La version installée est la **3.16**, soit une version majeure en retard (7.3 vs 3.16). La bibliothèque `factur-x` a changé d'interface entre ces versions. Les modules Akretion `fr-einvoicing` qui importent `facturx` risquent de ne pas fonctionner avec la version actuelle.
→ Mise à jour nécessaire sur le staging avant tout test.

**BLOQUANT 2** : `pyfrctc` absent
La bibliothèque `pyfrctc>=0.23` est la dépendance centrale d'Akretion pour les API AFNOR XP Z12-013 (émission, réception, cycle de vie, e-reporting). Elle n'est pas installée du tout.
→ Installation nécessaire sur le staging.

---

## 6. Volume de données en base

| Type | Nombre |
|------|--------|
| Écritures comptables (`entry`) | 788 |
| Factures clients (`out_invoice`) | 263 |
| Avoirs clients (`out_refund`) | 17 |
| **Total `account_move`** | **1 068** |

> **Bonne nouvelle** : volume très faible (1 068 écritures). Le risque de recalcul massif signalé dans le CDC pour les grandes bases ne s'applique pas ici. L'installation des modules Akretion ne devrait pas provoquer de timeout de migration.

---

## 7. Analyse des risques

### R1 — CRITIQUE : `factur-x` en version 3.16 au lieu de >=7.3

L'API Python a changé de façon incompatible entre les séries 3.x et 7.x. Le module `base_facturx` OCA actuellement installé utilise peut-être l'ancienne API. La mise à jour devra être testée en staging avec une validation des modules OCA déjà installés (`account_invoice_facturx`, `l10n_fr_facturx_chorus_pro`).

### R2 — CRITIQUE : `pyfrctc` absent

Requis pour toute interaction avec les API AFNOR / Plateformes Agréées. Sans lui, les modules `l10n_fr_einvoicing`, `l10n_fr_ereporting` etc. ne peuvent pas fonctionner.

### R3 — MOYEN : `l10n_fr_siret` non installé

Le SIRET de la société n'est pas renseigné dans Odoo. Le module `l10n_fr_siret` ajoute le champ SIRET sur `res.company` et `res.partner`. Ce champ est probablement requis par `l10n_fr_einvoicing` pour générer des factures conformes. À installer en priorité.

### R4 — MOYEN : `l10n_fr_account_invoice_facturx` non installé

Présent dans `/mnt/extra-addons` mais non installé. Ce module OCA est le complément France de `account_invoice_facturx`. Son rôle sera à reconsidérer lorsque Akretion `fr-einvoicing` sera installé (risque de conflit).

### R5 — MOYEN : coexistence PEPPOL Odoo natif + Akretion fr-einvoicing

Les modules `account_peppol`, `account_edi_ubl_cii` et `l10n_fr_facturx_chorus_pro` sont installés et actifs. Akretion `fr-einvoicing` implémente une autre couche EDI. Il faudra vérifier en staging l'absence de conflits entre les deux systèmes EDI (notamment sur les `account.edi.format`).

### R6 — FAIBLE : mode `account_edi_proxy_client` = `demo`

Le proxy PEPPOL Odoo est en mode `demo`. Cela n'affecte pas l'architecture Akretion, mais il faudra ne pas confondre les deux canaux lors des tests.

### R7 — FAIBLE : PR OCA non fusionnées à vérifier

Le CDC identifie deux PR potentiellement encore ouvertes :
- PR OCA/edi #1426 (`account_invoice_import`)
- PR OCA/l10n-france #810 (`l10n_fr_account_invoice_import`)

L'état actuel de ces PR est **inconnu** — à vérifier au moment de l'installation (Phase 3 du CDC).

---

## 8. Ce qui est déjà en place (acquis positifs)

- Infrastructure Docker stable, espace disque largement suffisant (470 Go libres)
- Sauvegarde automatique S3 toutes les 12h
- `account_invoice_import` + `account_invoice_import_facturx` installés (base import factures fournisseurs)
- `base_facturx` installé (mais version `factur-x` trop ancienne)
- Stack UNECE complète installée (`uom_unece`, `account_tax_unece`, etc.)
- `base_business_document_import` installé (dépendance Akretion)
- PEPPOL actif en réception (identifiant `9957:FR05481862662`)
- `saxonche` (Saxon XSLT/XSD) disponible — utile pour la validation XSD
- `lxml` 6.1.1, `Unidecode` 1.3.8, `pypdf` OK
- Volume de données faible (1 068 account.move) — pas de risque de recalcul massif

---

## 9. Modules Akretion fr-einvoicing requis — état des prérequis

| Module Akretion | Dépendances OCA | Prérequis Python | Prêt ? |
|----------------|----------------|-----------------|--------|
| `account_invoice_en16931` | OCA/edi, OCA/community-data-files | `factur-x>=7.3` | NON (`factur-x` trop ancien) |
| `l10n_fr_account_invoice_en16931` | `account_invoice_en16931`, `l10n_fr_siret` | — | NON (`l10n_fr_siret` absent) |
| `l10n_fr_einvoicing` | `l10n_fr_account_invoice_en16931` | `pyfrctc>=0.23` | NON (`pyfrctc` absent) |
| `l10n_fr_einvoicing_import` | `l10n_fr_einvoicing`, `account_invoice_import` | — | NON (dépend des blocs A/B) |
| `l10n_fr_einvoicing_sale` | `l10n_fr_einvoicing` | — | NON |
| `l10n_fr_einvoicing_purchase` | `l10n_fr_einvoicing` | — | NON |
| `l10n_fr_ereporting` | `l10n_fr_einvoicing` | `pyfrctc>=0.23` | NON |

---

## 10. Livrables suivants (plan d'action)

Conformément à la roadmap CDC :

| Lot | Action | Prérequis |
|-----|--------|-----------|
| **Lot 2** | Créer un environnement staging (clone DB + filestore + addons) | Gate 1 = ce rapport validé |
| **Lot 3 — Phase Python** | Mettre à jour `factur-x` vers >=7.3, installer `pyfrctc>=0.23` | Sur staging uniquement |
| **Lot 3 — Phase modules** | Cloner `akretion/fr-einvoicing` branche 18.0, figer SHA | Après Python OK |
| **Lot 3 — Bloc A** | Installer `account_invoice_en16931` + `l10n_fr_account_invoice_en16931` | Après Python |
| **Lot 3 — Bloc B** | Installer `l10n_fr_einvoicing` | Après Bloc A validé |
| **Lot 4** | Annuaire + configuration PA SUPER PDP | Après Bloc B validé |

---

## 11. Décision Gate 1

**Gate 1 : architecture comprise — OUI**

Les points bloquants identifiés (versions Python) sont normaux à ce stade et seront traités en staging.
**Aucune modification ne doit être effectuée sur la production** avant la validation du staging (Gate 2).

La prochaine étape est la création de l'environnement staging (Lot 2).
