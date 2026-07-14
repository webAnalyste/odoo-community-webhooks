#!/usr/bin/env python3
"""
Backup Odoo DB → S3
- pg_dump via SSH sur le VPS
- Upload vers S3 (eu-west-3)
- Rétention 15 jours glissants

Cron recommandé (toutes les 12h) — crontab -e sur le Mac :
  0 2,14 * * * /usr/bin/python3 /Users/fscan/Documents/odoo/scripts/backup_odoo_db.py >> /Users/fscan/Documents/odoo/scripts/backup.log 2>&1
"""

import subprocess
import datetime
import os
import sys
from pathlib import Path

# Load .env file from scripts/ directory if present (never committed)
_env_file = Path(__file__).parent / '.env'
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith('#') and '=' in _line:
            _k, _v = _line.split('=', 1)
            os.environ.setdefault(_k.strip(), _v.strip())

# =============================================================================
# CONFIGURATION
# =============================================================================

VPS_HOST        = '207.180.202.230'
VPS_USER        = 'root'
SSH_KEY         = '/Users/fscan/.ssh/contabo_key'

PG_CONTAINER    = 'postgresql-gm7iq81galclkuzhm0bnwbxu'
PG_USER         = 'fscan'
PG_DB           = 'odoo'
PG_PASSWORD     = os.environ.get('PG_PASSWORD', '')

S3_BUCKET       = 'wa-odoo'
S3_PREFIX       = 'data/coolify/odoo/db_backup'
S3_REGION       = 'eu-west-3'
AWS_KEY         = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET      = os.environ.get('AWS_SECRET_ACCESS_KEY', '')

RETENTION_DAYS  = 15
LOCAL_TMP       = '/tmp'

# =============================================================================

def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f'✗ Erreur : {result.stderr}')
        sys.exit(1)
    return result.stdout.strip()

def ssh(cmd):
    return run(f'ssh -i {SSH_KEY} -o StrictHostKeyChecking=no {VPS_USER}@{VPS_HOST} "{cmd}"')

def main():
    now = datetime.datetime.now()
    date_str = now.strftime('%Y%m%d_%H%M%S')
    filename = f'odoo_db_{date_str}.dump'
    remote_tmp = f'/tmp/{filename}'
    local_tmp = f'{LOCAL_TMP}/{filename}'

    print(f'=== Backup Odoo DB — {now.strftime("%Y-%m-%d %H:%M:%S")} ===')

    # 1. pg_dump dans le container PostgreSQL sur le VPS
    print('[1/4] pg_dump sur le VPS...')
    ssh(f'docker exec -e PGPASSWORD={PG_PASSWORD!r} {PG_CONTAINER} '
        f'pg_dump -U {PG_USER} -Fc {PG_DB} -f /var/lib/postgresql/data/{filename}')
    ssh(f'docker cp {PG_CONTAINER}:/var/lib/postgresql/data/{filename} {remote_tmp}')
    size = ssh(f'du -sh {remote_tmp} | cut -f1')
    print(f'     Taille : {size}')

    # 2. Récupérer le dump en local
    print('[2/4] Téléchargement en local...')
    run(f'scp -i {SSH_KEY} -o StrictHostKeyChecking=no {VPS_USER}@{VPS_HOST}:{remote_tmp} {local_tmp}')
    ssh(f'rm -f {remote_tmp}')
    # Nettoyer aussi dans le container
    ssh(f'docker exec {PG_CONTAINER} rm -f /var/lib/postgresql/data/{filename}')

    # 3. Upload S3
    print('[3/4] Upload S3...')
    env = os.environ.copy()
    env['AWS_ACCESS_KEY_ID'] = AWS_KEY
    env['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET
    env['AWS_DEFAULT_REGION'] = S3_REGION
    result = subprocess.run(
        f'aws s3 cp {local_tmp} s3://{S3_BUCKET}/{S3_PREFIX}/{filename}',
        shell=True, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f'✗ Upload S3 échoué : {result.stderr}')
        sys.exit(1)
    os.remove(local_tmp)
    print(f'     s3://{S3_BUCKET}/{S3_PREFIX}/{filename}')

    # 4. Rétention : supprimer les fichiers > RETENTION_DAYS jours
    print(f'[4/4] Nettoyage S3 (rétention {RETENTION_DAYS} jours)...')
    cutoff = now - datetime.timedelta(days=RETENTION_DAYS)
    listing = subprocess.run(
        f'aws s3 ls s3://{S3_BUCKET}/{S3_PREFIX}/',
        shell=True, capture_output=True, text=True, env=env).stdout
    deleted = 0
    for line in listing.splitlines():
        parts = line.split()
        if len(parts) < 4:
            continue
        fname = parts[3]
        if not fname.startswith('odoo_db_') or not fname.endswith('.dump'):
            continue
        try:
            fdate = datetime.datetime.strptime(f'{parts[0]} {parts[1]}', '%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue
        if fdate < cutoff:
            subprocess.run(
                f'aws s3 rm s3://{S3_BUCKET}/{S3_PREFIX}/{fname}',
                shell=True, env=env)
            print(f'     Supprimé : {fname}')
            deleted += 1
    if deleted == 0:
        print('     Rien à supprimer')

    print(f'=== Backup terminé : {filename} ===')

if __name__ == '__main__':
    main()
