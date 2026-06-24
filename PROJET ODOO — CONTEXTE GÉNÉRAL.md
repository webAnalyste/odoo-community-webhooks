PROJET ODOO — CONTEXTE GÉNÉRAL

Installation :
- Odoo Community v18 installé via Coolify sur un VPS.
- URL Odoo : https://odoo.webanalyste.com/
- Image Docker utilisée : odoo:18
- Odoo tourne dans un conteneur Docker géré par Coolify.

Conteneur Odoo identifié :
- Nom du conteneur : odoo-gm7iq81galclkuzhm0bnwbxu

Apps déjà installées / contexte fonctionnel :
- Facturation
- Vente / Ventes
- Discussion
- Calendrier
- Contacts
- CRM
- Tableaux de bord

Objectif initial :
- Migrer depuis Axonaut vers Odoo.
- Configurer Odoo progressivement.
- Mettre en place le rapprochement bancaire entre factures clients et rentrées bancaires.

Banque :
- BoursoBank.

Choix fonctionnel retenu :
- Ne pas faire de synchronisation bancaire automatique pour l’instant.
- Ne pas connecter BoursoBank directement à Odoo.
- Ne pas saisir d’identifiants BoursoBank dans Odoo.
- Utiliser un flux manuel/semi-automatique :
  BoursoBank → export fichier bancaire → import dans Odoo → rapprochement avec les factures.

Différence avec Axonaut :
- Axonaut propose une synchronisation bancaire automatique.
- Odoo Community + OCA, dans ce projet, fonctionne par import de fichiers bancaires.
- Le rapprochement peut être assisté, mais la récupération bancaire n’est pas automatique.

Formats bancaires privilégiés :
1. OFX si BoursoBank le propose.
2. CSV/XLSX si OFX indisponible.
3. CFONB uniquement si BoursoBank le fournit.
4. PDF à éviter.

Sécurité :
- Import manuel = plus sécurisé qu’un connecteur bancaire automatique.
- Aucun identifiant bancaire dans Odoo.
- Aucun agrégateur bancaire tiers au départ.
- Les fichiers bancaires restent sensibles : ne pas les envoyer par email, ne pas les stocker dans un dossier public, limiter les accès Odoo à la compta.
RÈGLE GÉNÉRALE POUR LES APPS ODOO ET DÉVELOPPEMENTS SUR MESURE

Méthode propre pour ajouter une app :
1. Ne pas privilégier l’import ZIP via l’interface Odoo.
2. Ajouter les modules directement dans /mnt/extra-addons.
3. Avoir un dossier par module.
4. Vérifier la présence de __manifest__.py à la racine de chaque module.
5. Corriger les droits.
6. Redémarrer Odoo via Coolify.
7. Dans Odoo : Apps → Mettre à jour la liste des applications.
8. Installer uniquement les modules nécessaires.

Source de vérité des modules ajoutés :
- /mnt/extra-addons

Dossier de stockage des sources Git/OCA :
- /mnt/extra-addons/_oca_src

Structure correcte d’un module :
/mnt/extra-addons/mon_module/
├── __manifest__.py
├── __init__.py
├── models/
├── views/
├── security/
└── ...

Structure à éviter :
/mnt/extra-addons/nom-du-repo-github/mon_module/__manifest__.py

Exception :
- Cette structure imbriquée est acceptable seulement si le sous-dossier du dépôt est ajouté explicitement dans addons_path.
- Pour éviter les problèmes, copier directement chaque module utile dans /mnt/extra-addons.

Principe important :
- Module présent dans /mnt/extra-addons ≠ module installé dans Odoo.
- Un module présent dans les fichiers ne modifie rien tant qu’il n’est pas installé dans la base Odoo.
- Ne pas désinstaller des modules au hasard : une désinstallation peut supprimer des données liées.

Modules non installés :
- Les modules visibles mais non installés dans Apps ne posent pas problème.
- Ils peuvent rester disponibles sans être actifs.

Développement sur mesure :
- Tout développement custom doit aussi aller dans /mnt/extra-addons.
- Ne pas développer dans /tmp, /root ou /usr/lib/python3/dist-packages/odoo/addons.
- Vérifier que /mnt/extra-addons est bien un volume persistant Coolify.
COMMANDES DE BASE — VPS / CONTENEUR

Depuis le VPS, lister les conteneurs Odoo :
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" | grep -i odoo

Entrer dans le conteneur Odoo en root :
docker exec -it -u root odoo-gm7iq81galclkuzhm0bnwbxu bash

Si bash ne marche pas :
docker exec -it -u root odoo-gm7iq81galclkuzhm0bnwbxu sh

Vérifier l’utilisateur :
whoami

Vérifier les addons :
ls -la /mnt/extra-addons

Créer le dossier des sources OCA :
mkdir -p /mnt/extra-addons/_oca_src

Installer git dans le conteneur si nécessaire :
apt-get update
apt-get install -y git

Vérifier git :
git --version

Vérifier les modules détectables :
find /mnt/extra-addons -maxdepth 2 -name "__manifest__.py" | sort

Vérifier les modules OCA utiles :
find /mnt/extra-addons -maxdepth 2 -name "__manifest__.py" | sort | grep -E "account_statement_base|account_reconcile|account_statement_import"

Corriger les droits :
chown -R odoo:odoo /mnt/extra-addons

Redémarrage :
- De préférence via Coolify : Service Odoo → Restart.
- Alternative Docker :
docker restart odoo-gm7iq81galclkuzhm0bnwbxu

Après redémarrage :
- Odoo → Apps → Mettre à jour la liste des applications.
RAPPROCHEMENT BANCAIRE — MODULES OCA RETENUS

Dépôt OCA account-reconcile :
https://github.com/OCA/account-reconcile/tree/18.0

Modules utiles depuis account-reconcile :
- account_statement_base
- account_reconcile_oca
- account_reconcile_model_oca

Dépôt OCA bank-statement-import :
https://github.com/OCA/bank-statement-import/tree/18.0

Modules utiles depuis bank-statement-import :
- account_statement_import_base
- account_statement_import_file
- account_statement_import_file_reconcile_oca
- account_statement_import_ofx
- account_statement_import_sheet_file

Modules optionnels :
- account_statement_import_fr_cfonb si export CFONB disponible.
- account_statement_import_camt / camt54 uniquement si un format CAMT est réellement disponible et utile.

Modules à éviter pour l’instant :
- account_statement_import_online
- account_statement_import_online_gocardless
- account_statement_import_online_plaid
- account_statement_import_online_ponto
- account_statement_import_online_paypal
- account_statement_import_online_stripe
- account_statement_import_online_wise
- l10n_es_account_statement_import_n43 sauf besoin Espagne.
COMMANDES — INSTALLATION OCA BANK STATEMENT IMPORT

Entrer dans le conteneur :
docker exec -it -u root odoo-gm7iq81galclkuzhm0bnwbxu bash

Préparer les sources :
mkdir -p /mnt/extra-addons/_oca_src
cd /mnt/extra-addons/_oca_src

Cloner le dépôt :
git clone --depth 1 --branch 18.0 https://github.com/OCA/bank-statement-import.git

Copier les modules utiles :
cp -r /mnt/extra-addons/_oca_src/bank-statement-import/account_statement_import_base /mnt/extra-addons/
cp -r /mnt/extra-addons/_oca_src/bank-statement-import/account_statement_import_file /mnt/extra-addons/
cp -r /mnt/extra-addons/_oca_src/bank-statement-import/account_statement_import_file_reconcile_oca /mnt/extra-addons/
cp -r /mnt/extra-addons/_oca_src/bank-statement-import/account_statement_import_ofx /mnt/extra-addons/
cp -r /mnt/extra-addons/_oca_src/bank-statement-import/account_statement_import_sheet_file /mnt/extra-addons/

Option CFONB :
cp -r /mnt/extra-addons/_oca_src/bank-statement-import/account_statement_import_fr_cfonb /mnt/extra-addons/

Corriger les droits :
chown -R odoo:odoo /mnt/extra-addons

Vérifier :
find /mnt/extra-addons -maxdepth 2 -name "__manifest__.py" | sort | grep account_statement_import
COMMANDES — INSTALLATION OCA ACCOUNT RECONCILE

Entrer dans le conteneur :
docker exec -it -u root odoo-gm7iq81galclkuzhm0bnwbxu bash

Préparer les sources :
mkdir -p /mnt/extra-addons/_oca_src
cd /mnt/extra-addons/_oca_src

Cloner le dépôt :
git clone --depth 1 --branch 18.0 https://github.com/OCA/account-reconcile.git

Copier les modules utiles :
cp -r /mnt/extra-addons/_oca_src/account-reconcile/account_statement_base /mnt/extra-addons/
cp -r /mnt/extra-addons/_oca_src/account-reconcile/account_reconcile_oca /mnt/extra-addons/
cp -r /mnt/extra-addons/_oca_src/account-reconcile/account_reconcile_model_oca /mnt/extra-addons/

Corriger les droits :
chown -R odoo:odoo /mnt/extra-addons

Vérifier :
find /mnt/extra-addons -maxdepth 2 -name "__manifest__.py" | sort | grep -E "account_statement_base|account_reconcile"
ORDRE D’INSTALLATION DANS ODOO

Après copie des modules :
1. Redémarrer Odoo depuis Coolify.
2. Aller dans Odoo → Apps.
3. Mettre à jour la liste des applications.
4. Retirer le filtre “Apps” ou “Installé” si nécessaire.
5. Chercher les noms techniques.

Ordre d’installation conseillé :
1. account_statement_base
2. account_reconcile_oca
3. account_reconcile_model_oca si pas déjà installé
4. account_statement_import_base
5. account_statement_import_file
6. account_statement_import_file_reconcile_oca
7. account_statement_import_ofx
8. account_statement_import_sheet_file

Ne pas installer les connecteurs online au départ.
PROBLÈME DÉJÀ RENCONTRÉ

Erreur :
“Vous essayez d'installer le module account_statement_import_base qui dépend du module account_statement_base. Mais ce dernier n'est pas disponible sur votre système.”

Cause :
- account_statement_base n’était pas présent dans /mnt/extra-addons.
- L’import ZIP account-reconcile-18.0 via l’interface Odoo n’a pas rendu account_statement_base disponible dans Apps.

Solution :
- Ne plus compter sur l’import ZIP.
- Cloner OCA/account-reconcile en CLI.
- Copier account_statement_base directement dans /mnt/extra-addons.
- Redémarrer Odoo.
- Mettre à jour la liste des apps.
RÈGLES DE PRUDENCE

Ne pas supprimer :
- account
- account_payment
- l10n_fr_account
- account_reconcile_model_oca
- modules déjà installés sans audit précis

Ne pas nettoyer les dossiers OCA juste parce qu’il y a beaucoup de modules.
- Un dossier module non installé ne change pas la base.
- On contrôle ce qui est installé dans Odoo, pas forcément tout ce qui est présent dans /mnt/extra-addons.

Avant toute app sensible :
- vérifier __manifest__.py
- lire depends
- installer les dépendances d’abord
- faire une sauvegarde si le module touche à la compta, factures, ventes, paiements ou clients

Pour la comptabilité :
- ne pas bricoler à l’aveugle
- ne pas installer de modules bancaires online ou connecteurs tiers sans audit
- tester d’abord sur une période courte, par exemple un mois d’export BoursoBank
DOCTRINE PROJET

/mnt/extra-addons = source de vérité pour les modules ajoutés
/mnt/extra-addons/_oca_src = stockage des dépôts sources
Odoo Apps = installation dans la base
Coolify = gestion du service, redémarrage, persistance, déploiement
Docker conteneur = environnement d’exécution

La méthode standard pour tout ajout futur :
1. Identifier le module.
2. Identifier ses dépendances dans __manifest__.py.
3. Copier le module dans /mnt/extra-addons.
4. Copier les dépendances nécessaires.
5. Vérifier les __manifest__.py.
6. Corriger les droits.
7. Redémarrer Odoo.
8. Mettre à jour la liste des apps.
9. Installer dans Odoo.
10. Tester.