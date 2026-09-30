#!/usr/bin/env bash
# Ricostruisce il sito e lo pubblica. Le call con la scadenza passata
# escono da sole dalle open call ed entrano in archivio, nell ordine giusto.
set -uo pipefail
cd "$(dirname "$0")"
SITE_ID=b62e6fd3-d064-4e4d-8447-79c9f01ccb96
LOG="$(dirname "$0")/data/aggiorna.log"
mkdir -p "$(dirname "$LOG")"
ts(){ date "+%Y-%m-%d %H:%M"; }

PY=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
[ -x "$PY" ] || PY=$(command -v python3)

uscita=$("$PY" build.py 2>&1)
echo "[$(ts)] $uscita" >> "$LOG"

# si pubblica solo se qualcosa e cambiato davvero
if echo "$uscita" | grep -q "call scadute"; then
  echo "[$(ts)] cambiate le call: pubblico" >> "$LOG"
  npx -y netlify-cli@latest deploy --dir=site --site="$SITE_ID" --prod \
      --message "aggiornamento automatico call scadute" >> "$LOG" 2>&1
  echo "[$(ts)] deploy concluso" >> "$LOG"
else
  echo "[$(ts)] nessuna call scaduta, niente da pubblicare" >> "$LOG"
fi
