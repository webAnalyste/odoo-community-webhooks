# REST API Connector — Odoo 18 Community

API REST JSON pour piloter Odoo depuis l'extérieur (n8n, Make, scripts, etc.).

## Authentification

Toutes les requêtes nécessitent le header :
```
X-API-Key: <votre_cle>
```

### Configurer la clé API
Odoo → Paramètres → Technique → Paramètres système → chercher `rest_api_connector.api_key`
- Si elle n'existe pas : créer une nouvelle entrée
- Clé : `rest_api_connector.api_key`
- Valeur : votre token secret (ex: `rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0`)

### Changer la clé
Modifier la valeur dans Paramètres système → redémarrage Odoo non nécessaire.

---

## Filtres disponibles

⚠️ **Les opérateurs utilisent DEUX underscores** : `champ__like`, `champ__gte`, `champ__lte`

Les filtres fonctionnent sur **n'importe quel champ** du modèle.

Pour tous les endpoints GET liste :
- `champ=valeur` → égalité exacte (ex: `city=Paris`, `stage_id=3`)
- `champ__like=valeur` → contient, insensible à la casse (ex: `name__like=dupont`, `partner_name__like=veolia`)
- `champ__gte=valeur` → supérieur ou égal (ex: `expected_revenue__gte=1000`)
- `champ__lte=valeur` → inférieur ou égal (ex: `expected_revenue__lte=5000`)
- `limit=100` → nombre de résultats (max 500, défaut 100)
- `offset=0` → pagination

---

## Entreprises — `/api/v1/companies`

### Lister toutes les entreprises
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/companies" | jq
```

### Rechercher par nom
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/companies?name__like=dupont" | jq
```

### Filtrer par ville
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/companies?city=Paris&limit=50" | jq
```

### Filtrer par TVA ou SIRET
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/companies?vat=FR05481862662" | jq
```

### Pagination
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/companies?limit=20&offset=40" | jq
```

### Obtenir une entreprise par ID
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/companies/42" | jq
```

### Créer une entreprise
```bash
curl -s -X POST \
  -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ma Nouvelle Société",
    "email": "contact@masociete.fr",
    "phone": "01 23 45 67 89",
    "street": "12 rue de la Paix",
    "city": "Paris",
    "zip": "75001",
    "country_id": 75,
    "vat": "FR12345678901"
  }' \
  "https://odoo.webanalyste.com/api/v1/companies" | jq
```

### Mettre à jour une entreprise
```bash
curl -s -X PUT \
  -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "01 99 88 77 66",
    "website": "https://masociete.fr"
  }' \
  "https://odoo.webanalyste.com/api/v1/companies/42" | jq
```

### Archiver une entreprise
```bash
curl -s -X DELETE \
  -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/companies/42" | jq
```

---

## Contacts — `/api/v1/contacts`

### Lister tous les contacts
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/contacts" | jq
```

### Contacts d'une entreprise (par parent_id)
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/contacts?parent_id=42" | jq
```

### Rechercher un contact par email
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/contacts?email=jean.dupont@example.com" | jq
```

### Rechercher par nom
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/contacts?name__like=dupont" | jq
```

### Obtenir un contact par ID
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/contacts/123" | jq
```

### Créer un contact lié à une entreprise
```bash
curl -s -X POST \
  -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jean Dupont",
    "email": "jean.dupont@masociete.fr",
    "phone": "06 12 34 56 78",
    "function": "Directeur Commercial",
    "parent_id": 42,
    "type": "contact"
  }' \
  "https://odoo.webanalyste.com/api/v1/contacts" | jq
```

### Mettre à jour un contact
```bash
curl -s -X PUT \
  -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nouveau@email.fr",
    "mobile": "07 98 76 54 32"
  }' \
  "https://odoo.webanalyste.com/api/v1/contacts/123" | jq
```

### Archiver un contact
```bash
curl -s -X DELETE \
  -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/contacts/123" | jq
```

---

## Opportunités CRM — `/api/v1/crm/leads`

### Lister toutes les opportunités
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/crm/leads" | jq
```

### Filtrer par entreprise
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/crm/leads?partner_id=42" | jq
```

### Filtrer par étape
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/crm/leads?stage_id=3" | jq
```

### Filtrer par équipe commerciale
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/crm/leads?team_id=1" | jq
```

### Devis/opportunités créés depuis N jours (relances)
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/crm/leads?created_after=2026-06-01" | jq
```

### Opportunités modifiées récemment
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/crm/leads?updated_after=2026-07-01" | jq
```

### Opportunités créées entre deux dates
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/crm/leads?created_after=2026-01-01&created_before=2026-06-30" | jq
```

### Filtrer par nom d'opportunité
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/crm/leads?name__like=formation" | jq
```

### Obtenir une opportunité par ID
```bash
curl -s -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/crm/leads/789" | jq
```

### Créer une opportunité (champs standard)
```bash
curl -s -X POST \
  -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Formation React - Ma Société",
    "partner_id": 42,
    "stage_id": 1,
    "expected_revenue": 3500.0,
    "email_from": "jean.dupont@masociete.fr",
    "phone": "01 23 45 67 89"
  }' \
  "https://odoo.webanalyste.com/api/v1/crm/leads" | jq
```

### Créer une opportunité avec champs custom formation
```bash
curl -s -X POST \
  -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Formation React - Ma Société",
    "partner_id": 42,
    "stage_id": 1,
    "expected_revenue": 3500.0,
    "x_participants": 8,
    "x_date_debut": "2026-09-15",
    "x_date_fin": "2026-09-19",
    "x_nb_heures": 35.0,
    "x_contact_id": 123,
    "x_stagiaires": "Alice Martin\nBob Durand",
    "x_stagiaires_emails": "alice@masociete.fr\nbob@masociete.fr"
  }' \
  "https://odoo.webanalyste.com/api/v1/crm/leads" | jq
```

### Mettre à jour une opportunité (changer étape, revenus)
```bash
curl -s -X PUT \
  -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  -H "Content-Type: application/json" \
  -d '{
    "stage_id": 4,
    "expected_revenue": 4200.0,
    "probability": 80
  }' \
  "https://odoo.webanalyste.com/api/v1/crm/leads/789" | jq
```

### Mettre à jour les tags (liste d'IDs)
```bash
curl -s -X PUT \
  -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  -H "Content-Type: application/json" \
  -d '{"tag_ids": [1, 3, 7]}' \
  "https://odoo.webanalyste.com/api/v1/crm/leads/789" | jq
```

### Archiver une opportunité
```bash
curl -s -X DELETE \
  -H "X-API-Key: rac_Kj9mX2pL7vQnR4wT8yF3dH6bN1sE5uA0" \
  "https://odoo.webanalyste.com/api/v1/crm/leads/789" | jq
```

---

## Champs disponibles

### Entreprises (`res.partner` is_company=True)
| Champ | Type | Filtrable |
|-------|------|-----------|
| `name` | char | `name__like` |
| `email` | char | oui |
| `phone` | char | oui |
| `mobile` | char | oui |
| `website` | char | oui |
| `vat` | char | oui |
| `siret` | char | oui |
| `street`, `street2` | char | oui |
| `city` | char | `city__like` |
| `zip` | char | oui |
| `country_id` | integer (ID) | oui |
| `state_id` | integer (ID) | oui |
| `lang` | char | oui |
| `active` | boolean | oui |

### Contacts (`res.partner` is_company=False)
Mêmes champs + `parent_id` (ID entreprise), `function`, `type`, `comment`.

### Opportunités CRM (`crm.lead`)
| Champ | Type | Notes |
|-------|------|-------|
| `name` | char | obligatoire à la création |
| `partner_id` | integer (ID) | entreprise liée |
| `stage_id` | integer (ID) | étape pipeline |
| `user_id` | integer (ID) | commercial assigné |
| `team_id` | integer (ID) | équipe commerciale |
| `priority` | char | `0`, `1`, `2`, `3` |
| `probability` | float | 0-100 |
| `expected_revenue` | float | |
| `email_from` | char | |
| `phone`, `mobile` | char | |
| `date_deadline` | date | format `YYYY-MM-DD` |
| `tag_ids` | liste d'IDs | ex: `[1, 2, 3]` |
| `x_participants` | integer | nb stagiaires |
| `x_date_debut` | date | format `YYYY-MM-DD` |
| `x_date_fin` | date | format `YYYY-MM-DD` |
| `x_nb_heures` | float | durée formation |
| `x_contact_id` | integer (ID) | contact client |
| `x_stagiaires` | text | liste des stagiaires |
| `x_stagiaires_emails` | text | emails stagiaires |

---

## Codes de réponse

| Code | Signification |
|------|---------------|
| `200` | Succès |
| `201` | Créé avec succès |
| `400` | Données invalides (champ requis manquant) |
| `401` | Header X-API-Key manquant |
| `403` | Clé API invalide |
| `404` | Ressource introuvable |

---

## Notes techniques

- `auth='api_key'` **n'existe pas** en Odoo 18 Community (module OCA tiers requis)
- Basic Auth HTTP ne fonctionne pas non plus en Community sur les controllers custom
- Solution retenue : `auth='public'` + `@require_api_key` + validation via `ir.config_parameter`
- Les suppressions sont toujours des **archivages** (`active=False`), jamais des suppressions définitives
- Le `country_id=75` correspond à la France
