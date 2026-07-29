#!/usr/bin/env bash
# Installation du coordinateur Lenyay sur un VPS Debian/Ubuntu vierge.
# Usage : sudo bash install-vps.sh <domaine> <jeton-admin>
# Idempotent : relançable sans casser l'existant.
set -euo pipefail

DOMAIN="${1:?Usage: install-vps.sh <domaine> <jeton-admin>}"
ADMIN_TOKEN="${2:?Il faut un jeton d'administration (long et aléatoire)}"
REPO="https://github.com/k1tz03/lenyay.git"
APP_DIR=/opt/lenyay
DATA_DIR=/var/lib/lenyay

echo "== Paquets =="
apt-get update -qq
apt-get install -y -qq git python3 python3-venv caddy

echo "== Utilisateur de service (sans droits, sans shell) =="
id -u lenyay &>/dev/null || useradd --system --home "$DATA_DIR" --shell /usr/sbin/nologin lenyay

echo "== Code =="
if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" pull --ff-only
else
  git clone "$REPO" "$APP_DIR"
fi
python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install -q --upgrade pip
"$APP_DIR/.venv/bin/pip" install -q fastapi "uvicorn[standard]" pydantic httpx

echo "== Données (hors du dossier de code, sauvegardables d'un bloc) =="
mkdir -p "$DATA_DIR"/{data,backups}
[ -f "$DATA_DIR/data/tasks.jsonl" ] || cp "$APP_DIR/data/tasks.jsonl" "$DATA_DIR/data/"
[ -f "$DATA_DIR/data/code_tasks.jsonl" ] || cp "$APP_DIR/data/code_tasks.jsonl" "$DATA_DIR/data/"
chown -R lenyay:lenyay "$DATA_DIR"

echo "== Service systemd =="
sed -e "s|__ADMIN_TOKEN__|$ADMIN_TOKEN|" \
    "$APP_DIR/deploy/lenyay.service" > /etc/systemd/system/lenyay.service
chmod 600 /etc/systemd/system/lenyay.service   # le jeton admin est dedans
systemctl daemon-reload
systemctl enable --now lenyay

echo "== Caddy (HTTPS automatique) =="
sed -e "s|__DOMAIN__|$DOMAIN|" "$APP_DIR/deploy/Caddyfile" > /etc/caddy/Caddyfile
systemctl reload caddy

echo "== Sauvegarde quotidienne (4 h du matin) =="
install -m 755 "$APP_DIR/deploy/backup.sh" /usr/local/bin/lenyay-backup
( crontab -l 2>/dev/null | grep -v lenyay-backup ; echo "0 4 * * * /usr/local/bin/lenyay-backup" ) | crontab -

echo
echo "Terminé. Vérifie :  curl -s https://$DOMAIN/stats"
echo "Console admin    :  https://$DOMAIN/admin  (avec ton jeton)"
