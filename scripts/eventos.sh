#!/usr/bin/env bash
# Eventos del entorno desde una hora dada, en orden cronológico, y duración del despliegue.
# Uso: INICIO=$(date -u +%Y-%m-%dT%H:%M:%SZ)   # justo antes de desplegar
#      ./scripts/eventos.sh blacklist-env "$INICIO" rolling
set -eu
ENV="${1:?Uso: $0 nombre-entorno inicio-ISO8601 etiqueta}"
DESDE="${2:?Falta la hora de inicio, p. ej. 2026-10-17T19:00:00Z}"
ETQ="${3:-despliegue}"
aws elasticbeanstalk describe-events --environment-name "$ENV" --start-time "$DESDE" \
  --query 'reverse(Events)[].[EventDate,Severity,Message]' --output text | tee "eventos-$ETQ.txt"
ini=$(grep -m1 'Environment update is starting' "eventos-$ETQ.txt" | cut -f1 || true)
fin=$(grep 'Environment update completed successfully' "eventos-$ETQ.txt" | tail -1 | cut -f1 || true)
if [ -n "$ini" ] && [ -n "$fin" ]; then
  d=$(( $(date -d "$fin" +%s) - $(date -d "$ini" +%s) ))   # GNU date (Linux/WSL); en macOS usa gdate
  printf '\nDuración (Events): %d min %02d s  (%s → %s)\n' $((d / 60)) $((d % 60)) "$ini" "$fin" | tee -a "eventos-$ETQ.txt"
else
  echo; echo "Aún no aparecen el evento de inicio y el de fin. ¿Terminó el despliegue?"
fi
