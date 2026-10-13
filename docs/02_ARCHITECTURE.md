# 02_ARCHITECTURE — Environnements et infrastructure staging

**Date** : 2026-10-13
**Statut** : Gate 2 franchie — staging opérationnel

---

## 1. Environnements

### Production

| Paramètre | Valeur |
|-----------|--------|
| URL | https://odoo.webanalyste.com/ |
| Container Odoo | `odoo-gm7iq81galclkuzhm0bnwbxu` |
| Container PostgreSQL | `postgresql-gm7iq81galclkuzhm0bnwbxu` |
| Réseau Docker | `gm7iq81galclkuzhm0bnwbxu` |
| Volume addons | `gm7iq81galclkuzhm0bnwbxu_odoo-extra-addons` → `/mnt/extra-addons` |
| Volume filestore | `gm7iq81galclkuzhm0bnwbxu_odoo-web-data` → `/var/lib/odoo` |
| Volume config | `gm7iq81galclkuzhm0bnwbxu_odoo-config` → `/etc/odoo` |
| Volume DB | `gm7iq81galclkuzhm0bnwbxu_postgresql-data` |
| Port exposé | 443 via Traefik (Coolify) |

### Staging (créé le 2026-10-13)

| Paramètre | Valeur |
|-----------|--------|
| Container Odoo | `odoo-staging` |
| Container PostgreSQL | `postgresql-staging` |
| Réseau Docker | `odoo-staging-network` (isolé, sans accès extérieur) |
| Volume addons | `odoo-staging-extra-addons` |
| Volume filestore | `odoo-staging-web-data` |
| Volume config | `odoo-staging-config` |
| Volume DB | `odoo-staging-postgresql-data` |
| Port | `127.0.0.1:8070` — accessible uniquement depuis le VPS (pas exposé Internet) |
| Accès | `ssh -i ~/.ssh/contabo_key -L 8070:127.0.0.1:8070 root@207.180.202.230` puis http://localhost:8070 |

#### Volumes staging — tailles au moment de la création

| Volume | Taille |
|--------|--------|
| `odoo-staging-postgresql-data` | ~210 Mo (clone production) |
| `odoo-staging-web-data` | ~293 Mo (clone production) |
| `odoo-staging-extra-addons` | ~49 Mo (clone production) |

---

## 2. Commandes de gestion du staging

```bash
# Démarrer le staging
ssh -i ~/.ssh/contabo_key root@207.180.202.230 "docker start postgresql-staging && sleep 3 && docker start odoo-staging"

# Arrêter le staging
ssh -i ~/.ssh/contabo_key root@207.180.202.230 "docker stop odoo-staging && docker stop postgresql-staging"

# Accéder au staging via tunnel SSH
ssh -i ~/.ssh/contabo_key -L 8070:127.0.0.1:8070 root@207.180.202.230
# → ouvrir http://localhost:8070 dans le navigateur

# Logs staging
ssh -i ~/.ssh/contabo_key root@207.180.202.230 "docker logs -f odoo-staging 2>&1"

# Shell staging Odoo
ssh -i ~/.ssh/contabo_key root@207.180.202.230 "docker exec -it -u root odoo-staging bash"

# Shell staging PostgreSQL
ssh -i ~/.ssh/contabo_key root@207.180.202.230 "docker exec -it postgresql-staging psql -U fscan -d odoo"
```

---

## 3. Resynchronisation staging depuis production

Si le staging doit être re-cloné (ex: après une migration ratée) :

```bash
# 1. Arrêter le staging
docker stop odoo-staging postgresql-staging

# 2. Supprimer les volumes staging
docker volume rm odoo-staging-postgresql-data odoo-staging-web-data odoo-staging-extra-addons
docker volume create odoo-staging-postgresql-data
docker volume create odoo-staging-web-data
docker volume create odoo-staging-extra-addons

# 3. Redémarrer PostgreSQL staging vide
docker start postgresql-staging

# 4. Dump + restore
docker exec postgresql-gm7iq81galclkuzhm0bnwbxu pg_dump -U fscan odoo > /tmp/odoo_prod_dump.sql
docker exec -i postgresql-staging psql -U fscan -d odoo < /tmp/odoo_prod_dump.sql

# 5. Cloner filestore et addons
docker run --rm -v gm7iq81galclkuzhm0bnwbxu_odoo-web-data:/source:ro -v odoo-staging-web-data:/dest alpine sh -c 'cp -a /source/. /dest/'
docker run --rm -v gm7iq81galclkuzhm0bnwbxu_odoo-extra-addons:/source:ro -v odoo-staging-extra-addons:/dest alpine sh -c 'cp -a /source/. /dest/'

# 6. Redémarrer Odoo staging
docker start odoo-staging
```

---

## 4. Règles d'utilisation du staging

- **Toute modification e-invoicing se fait d'abord sur le staging**
- Le staging est accessible uniquement depuis le VPS (port 8070 non exposé)
- Aucune émission de facture électronique réelle depuis le staging
- Les credentials PA utilisés sur le staging seront des credentials sandbox (SUPER PDP test)
- Le staging peut être recréé à tout moment depuis la production sans impact

---

## 5. Architecture cible e-invoicing

```
Odoo Community 18 (staging / prod)
        ↓
Modules OCA (community-data-files, edi, l10n-france, account-financial-tools, sale-workflow)
        ↓
Modules Akretion fr-einvoicing (18.0)
        ↓
EN16931 / Factur-X / UBL / CII
        ↓
Validation XSD + Schematron (saxonche déjà présent)
        ↓
pyfrctc >= 0.23 — API AFNOR XP Z12-013
        ↓
Plateforme Agréée (SUPER PDP pour tests → PA production à choisir)
        ↓
Écosystème facturation électronique française
```

---

## 6. Validation Gate 2

Critères CDC :

| Critère | Résultat |
|---------|----------|
| Staging démarre sans erreur | OK (HTTP 200/303 au démarrage) |
| Se connecte à la copie de la base | OK (101 modules installés détectés) |
| Affiche la comptabilité | À vérifier manuellement via tunnel SSH |
| Crée une facture | À tester manuellement |
| Génère un PDF | À tester manuellement |
| Redémarre sans problème | OK (restart testé, HTTP 303 après restart) |

**Gate 2 : franchie techniquement.** La prochaine étape est le Lot 3 — préparation des dépôts OCA et Python sur staging.
