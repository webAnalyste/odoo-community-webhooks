# Odoo Community Webhooks

Module Odoo 18 Community qui déclenche des webhooks HTTP externes sur les actions CRUD des objets métier clés (Contacts, Factures, Commandes, Opportunités CRM).

Compatible avec **Make**, **n8n**, **Zapier**, **Activepieces** ou tout endpoint HTTP.

---

## Fonctionnalités

- Configuration par endpoint : modèle Odoo × action (create / write / unlink) × URL
- Payload JSON automatique avec les champs métier pertinents
- Authentification par token secret (`X-Webhook-Token`)
- Historique complet des appels (code HTTP, réponse, succès/erreur)
- Bouton **Rejouer** sur les logs en erreur
- Filtres et recherche dans toutes les vues
- Bouton **Tester** depuis le formulaire endpoint

---

## Modèles supportés

| Modèle Odoo | Label |
|---|---|
| `res.partner` | Contact |
| `account.move` | Facture |
| `sale.order` | Commande vente |
| `crm.lead` | Opportunité CRM |

---

## Installation

### 1. Copier le module dans le conteneur

```bash
# Option A — depuis le VPS via Git
docker exec -it -u root odoo-<id> bash
git clone https://github.com/webAnalyste/odoo-community-webhooks.git /mnt/extra-addons/_webhook_src
cp -r /mnt/extra-addons/_webhook_src/addons/webhook_connector /mnt/extra-addons/
chown -R odoo:odoo /mnt/extra-addons/webhook_connector

# Option B — depuis le poste local via scp + docker cp
scp -r addons/webhook_connector user@vps:/tmp/
docker cp /tmp/webhook_connector odoo-<id>:/mnt/extra-addons/
docker exec -u root odoo-<id> chown -R odoo:odoo /mnt/extra-addons/webhook_connector
```

### 2. Redémarrer Odoo

Via Coolify : **Service Odoo → Restart**

### 3. Installer dans Odoo

1. Odoo → **Apps** → **Mettre à jour la liste des applications**
2. Rechercher `Webhook Connector`
3. Cliquer **Installer**

---

## Configuration

Menu : **Paramètres → Technique → Webhooks → Endpoints**

Créer un endpoint :

| Champ | Description |
|---|---|
| Nom | Label lisible (ex: `Nouveau contact → Make`) |
| Modèle Odoo | Le modèle à surveiller |
| Action déclenchante | `create`, `write` ou `unlink` |
| URL Webhook | URL complète de votre endpoint externe |
| Méthode HTTP | `POST` (défaut), `PUT` ou `PATCH` |
| Token secret | Optionnel — envoyé dans le header `X-Webhook-Token` |
| Timeout | Délai max en secondes (défaut : 10) |

---

## Format du payload

Exemple pour `res.partner` / `create` :

```json
{
  "action": "create",
  "model": "res.partner",
  "record_id": 42,
  "record_name": "Acme Corp",
  "database": "odoo_prod",
  "name": "Acme Corp",
  "email": "contact@acme.com",
  "phone": "+33 1 23 45 67 89",
  "company_type": "company"
}
```

Exemple pour `account.move` / `write` :

```json
{
  "action": "write",
  "model": "account.move",
  "record_id": 101,
  "record_name": "INV/2026/00042",
  "database": "odoo_prod",
  "name": "INV/2026/00042",
  "move_type": "out_invoice",
  "state": "posted",
  "partner_id": 42,
  "partner_name": "Acme Corp",
  "amount_total": 1200.00,
  "currency": "EUR",
  "invoice_date": "2026-06-25"
}
```

---

## Intégrations

### Make (ex-Integromat)

1. Créer un scénario avec le module **Webhooks → Custom webhook**
2. Copier l'URL générée par Make
3. Coller dans le champ URL de l'endpoint Odoo
4. Utiliser le bouton **Tester** pour envoyer un payload de test à Make

### n8n

1. Créer un workflow avec le nœud **Webhook**
2. Copier l'URL de production
3. Coller dans l'endpoint Odoo
4. Activer le workflow n8n avant d'activer l'endpoint Odoo

### Zapier / Activepieces

Même principe — utiliser le webhook de type **Catch Hook** et coller l'URL.

---

## Mise à jour

```bash
# Sur le VPS
docker exec -it -u root odoo-<id> bash
cd /mnt/extra-addons/_webhook_src && git pull
cp -r addons/webhook_connector /mnt/extra-addons/
chown -R odoo:odoo /mnt/extra-addons/webhook_connector
```

Puis dans Odoo : **Apps → Webhook Connector → Mettre à jour**

---

## Structure du module

```
addons/webhook_connector/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── _webhook_mixin.py      # dispatcher central
│   ├── webhook_endpoint.py    # config, payload, fire()
│   ├── webhook_log.py         # historique + retry
│   ├── res_partner.py
│   ├── account_move.py
│   ├── sale_order.py
│   └── crm_lead.py
├── views/
│   ├── webhook_endpoint_views.xml
│   ├── webhook_log_views.xml
│   └── menu.xml
└── security/
    └── ir.model.access.csv
```

---

## Licence

LGPL-3
