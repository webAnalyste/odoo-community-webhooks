#!/bin/bash
# Déploie un ou plusieurs modules custom sur le VPS
# Usage: ./scripts/deploy_addons.sh custom_display custom_terms webhook_connector
set -e

SSH_KEY=~/.ssh/contabo_key
VPS=root@207.180.202.230
VOL=/var/lib/docker/volumes/gm7iq81galclkuzhm0bnwbxu_odoo-extra-addons/_data
ADDONS_DIR="$(cd "$(dirname "$0")/../addons" && pwd)"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <module> [module2 ...]"
    exit 1
fi

for MODULE in "$@"; do
    SRC="$ADDONS_DIR/$MODULE"
    if [ ! -d "$SRC" ]; then
        echo "ERREUR : module '$MODULE' introuvable dans $ADDONS_DIR"
        exit 1
    fi
    echo "→ Déploiement de $MODULE..."
    scp -q -i "$SSH_KEY" -r "$SRC" "$VPS:/tmp/_deploy_$MODULE"
    ssh -i "$SSH_KEY" "$VPS" "
        rm -rf $VOL/$MODULE &&
        cp -r /tmp/_deploy_$MODULE $VOL/$MODULE &&
        chown -R 101:101 $VOL/$MODULE &&
        rm -rf /tmp/_deploy_$MODULE &&
        echo '  OK $MODULE'
    "
done

echo ""
echo "Déploiement terminé. Étapes suivantes dans Odoo :"
echo "  Paramètres > Apps > [module] > Mettre à jour"
