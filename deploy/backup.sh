#!/usr/bin/env bash
# Sauvegarde quotidienne : base SQLite (copie cohérente) + traces acceptées.
# 14 jours de rétention. Restaurer = décompresser dans /var/lib/lenyay/data.
set -euo pipefail
DATA=/var/lib/lenyay/data
OUT=/var/lib/lenyay/backups
STAMP=$(date +%Y-%m-%d)

mkdir -p "$OUT"
# .backup fait une copie cohérente même pendant les écritures.
sqlite3 "$DATA/lenyay.db" ".backup '$OUT/lenyay-$STAMP.db'" 2>/dev/null \
  || cp "$DATA/lenyay.db" "$OUT/lenyay-$STAMP.db"
tar -czf "$OUT/accepted-$STAMP.tar.gz" -C "$DATA" accepted 2>/dev/null || true
find "$OUT" -mtime +14 -delete
