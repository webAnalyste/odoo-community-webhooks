# 07_TEST_RESULTS — Résultats tests Phase 7 (EN16931 / Factur-X)

**Date** : 2026-10-13
**Environnement** : staging uniquement

---

## Prérequis configurés avant les tests

### Company (res.partner id=1 — Franck Scandolera EI WEBANALYSTE)
| Champ | Valeur configurée |
|-------|------------------|
| `fr_directory_entity_type` | `private` (Private VAT Registered) |
| `fr_directory_siren` | `481862662` |
| `fr_directory_siret` | `48186266200030` |
| `fr_directory_last_sync_date` | `2026-10-13` (fictif — pas de PA connectée) |

### Company (res.company id=1)
| Champ | Valeur configurée |
|-------|------------------|
| `fr_ctc_accredited_platform` | `superpdp` |
| `fr_ctc_send_invoice_format` | `facturx` |
| `fr_ctc_send_out_invoice` | `all` |
| `fr_ctc_auth_method` | vide (credentials SUPER PDP non configurés) |

### Taxes UNECE (29 taxes actives configurées)
| Catégorie UNECE | Taxes concernées | VATEX |
|-----------------|-----------------|-------|
| S (Standard) — id=74 | 20% G, 20% F, 20% S, 8.5% G, 10% G, 5.5% G, 2.1% G, variantes INC et R E | — |
| E (Exempt) — id=64 | 0% EXEMPT G, 0% EXEMPT S | VATEX-EU-132 (id=159) |
| Z (Zero rated) — id=75 | 0% EX G, 0% EX S, 0% EX, 20% EX, 20% EX O EU | VATEX-EU-G (id=215) |
| K (EEA) — id=70 | 0% EU G, 0% EU S, 20% EU G, 20% EU S | VATEX-EU-IC (id=217) |

**Source UNECE** : `account_tax_unece` 18.0.2.3.0 (OCA/community-data-files — mis à jour depuis 18.0.1.1.0 qui manquait `unece_vatex_id`)

---

## T01 — Facture B2B française, TVA 20%, simple

| Paramètre | Valeur |
|-----------|--------|
| Partenaire | La Boutique Officielle (id=23165) — VAT FR71451876783 |
| Journal | FAC (Customer Invoices, id=1) |
| Ligne | TEST T01 — Prestation de conseil EN16931 |
| Qté / PU | 1 × 1000.00 € |
| Taxe | 20% G (categ S, UNECE VAT) |
| HT | 1000.00 € |
| TVA | 200.00 € |
| TTC | 1200.00 € |
| Numéro | **FA00908** |
| État Odoo | **posted** |

### Génération Factur-X

| Étape | Résultat |
|-------|----------|
| `action_post` (validation facture) | ✓ OK |
| Wizard `account.invoice.en16931.generate` | ✓ OK |
| Format | Factur-X (CII/PDF-A3) |
| Taille PDF | 74 913 bytes |
| Taille XML extrait | 7 949 bytes |
| Filename dans PDF | `factur-x.xml` |

### Validation XML

| Validation | Résultat |
|-----------|----------|
| Profil déclaré | `urn:cen.eu:en16931:2017#conformant#urn:factur-x.eu:1p0:extended` |
| XSD (`check_xsd=True`, facturx 7.6) | ✓ **PASSÉ** (aucune erreur) |
| Structure vendeur | ✓ SIRET 48186266200030, SIREN 481862662, TVA FR05481862662 |
| Structure acheteur | ✓ TVA FR71451876783, adresse présente |
| Ligne de facture | ✓ 1000.00 EUR, TypeCode=380, CategoryCode=S, Rate=20% |
| Totaux | ✓ HT 1000.00, TVA 200.00, TTC 1200.00 |
| Date facture | ✓ 20261013 |
| Date échéance | ✓ 20261112 (30 jours) |

**Résultat T01 : VALIDÉ ✓**

---

## T02 — Facture B2B, taxe réduite 10%

| Paramètre | Valeur |
|-----------|--------|
| Numéro | **FA00909** | Partenaire | La Boutique Officielle |
| Ligne | TEST T02 — Prestation taux réduit 10%, 1 × 500.00€ |
| Taxe | 10% G (categ S) | HT | 500.00€ | TVA | 50.00€ | TTC | 550.00€ |
| XSD | ✓ OK | TypeCode | 380 (Facture) | Taxes XML | S10% |

**Résultat T02 : VALIDÉ ✓**

---

## T03 — Facture B2B, ligne exonérée TVA

| Paramètre | Valeur |
|-----------|--------|
| Numéro | **FA00910** | Partenaire | La Boutique Officielle |
| Ligne | TEST T03 — Formation professionnelle exonérée TVA, 1 × 2000.00€ |
| Taxe | 0% EXEMPT G (categ E, VATEX-EU-132) | HT | 2000.00€ | TVA | 0.00€ | TTC | 2000.00€ |
| XSD | ✓ OK | TypeCode | 380 (Facture) | Taxes XML | E0% |

**Résultat T03 : VALIDÉ ✓**

---

## T04 — Avoir (credit note) B2B

| Paramètre | Valeur |
|-----------|--------|
| Numéro | **FA00893** | Type | out_refund (Avoir) |
| Partenaire | La Boutique Officielle |
| Ligne | TEST T04 — Avoir partiel sur prestation, 1 × 300.00€ |
| Taxe | 20% G (categ S) | HT | 300.00€ | TVA | 60.00€ | TTC | 360.00€ |
| XSD | ✓ OK | TypeCode | **381 (Avoir)** | Taxes XML | S20% |

**Résultat T04 : VALIDÉ ✓**

---

## T05 — Facture multilignes, taxes mixtes

| Paramètre | Valeur |
|-----------|--------|
| Numéro | **FA00911** | Partenaire | La Boutique Officielle |
| Ligne 1 | Conseil EN16931 (20%), 2 × 750.00€ |
| Ligne 2 | Formation exonérée TVA (0% EXEMPT), 1 × 1500.00€ |
| Ligne 3 | Support 10%, 3 × 200.00€ |
| HT | 3600.00€ | TVA | 360.00€ | TTC | 3960.00€ |
| XSD | ✓ OK | TypeCode | 380 | Taxes XML | S20%+E0%+S10% |

**Résultat T05 : VALIDÉ ✓**

---

## T06 — Facture intracommunautaire UE (partenaire étranger)

| Paramètre | Valeur |
|-----------|--------|
| Numéro | **FA00912** | Partenaire | TEST GmbH Berlin (DE, VAT DE123456788) |
| Ligne | Livraison intracommunautaire UE, 1 × 1200.00€ |
| Taxe | 0% EU G (categ K, VATEX-EU-IC) | HT | 1200.00€ | TVA | 0.00€ | TTC | 1200.00€ |
| XSD | ✓ OK | TypeCode | 380 | Taxes XML | K0% |
| Note | `fr_directory_entity_type = 'no'` requis pour partenaires étrangers sans SIREN |

**Résultat T06 : VALIDÉ ✓**

---

## T07 — Import facture Factur-X fournisseur

### Fichier test
- XML CII Factur-X Extended généré manuellement
- Fournisseur fictif : ACME SARL TEST (SIREN 552100554, TVA FR84552100554)
- Acheteur : Franck Scandolera EI WEBANALYSTE (SIRET 48186266200030)
- N° facture : FTEST-2026-001, date 2026-10-13, échéance 2026-11-12
- 1 ligne : Prestation de service informatique, 1 × 800.00€, TVA 20%
- XSD validation : ✓ passée avant génération du PDF

### Prérequis résolus
| Problème | Solution |
|----------|----------|
| `multi_xpath_helper` AttributeError | `account_invoice_import_facturx` 18.0.1.0.0 incompatible avec `account_invoice_import` 18.0.2.0.0 → mis à jour vers **18.0.1.1.0** depuis OCA/edi PR#1426 |

### Résultat import

| Paramètre | Valeur |
|-----------|--------|
| Module utilisé | `account_invoice_import` + `account_invoice_import_facturx` |
| Wizard | `account.invoice.import` |
| Message Odoo | `1 vendor bill(s) created` |
| ID créé | account.move id=2373 |
| move_type | in_invoice ✓ |
| État | draft (à vérifier/valider manuellement) |
| Ref | FTEST-2026-001 ✓ |
| Date | 2026-10-13 ✓ |
| Échéance | 2026-11-12 ✓ |
| HT | 800.00€ ✓ |
| TVA | 160.00€ ✓ |
| TTC | 960.00€ ✓ |
| Ligne | "Prestation de service informatique" 1 × 800.00€ ✓ |
| Fournisseur | Non résolu (ACME SARL TEST inconnu dans DB) — comportement normal |

**Résultat T07 : VALIDÉ ✓**

---

## Problèmes rencontrés et résolus (suite)

5. **`account_invoice_import_facturx` `multi_xpath_helper` manquant** → version 18.0.1.0.0 (OCA standard) incompatible avec `account_invoice_import` 18.0.2.0.0 (Akretion PR#1426) → mis à jour vers 18.0.1.1.0 depuis le clone OCA/edi PR#1426

---

## Problèmes rencontrés et résolus

1. **`fr_directory_entity_type` vide** → défini à `private` + `fr_directory_last_sync_date` requis simultanément
2. **Taxes sans `unece_type_id`** → configuré UNECE type/categ sur les 29 taxes actives
3. **`unece_vatex_id` AttributeError** → `account_tax_unece` 18.0.1.1.0 manquait le champ → mis à jour vers 18.0.2.3.0 depuis OCA/community-data-files
4. **Taxes E/Z/K sans VATEX** → configuré VATEX-EU-132 (E), VATEX-EU-G (Z), VATEX-EU-IC (K)
