#!/usr/bin/env bash
# Foto de las instancias del entorno: guárdala antes y después de cada despliegue.
# Uso: ./scripts/ids.sh blacklist-env antes-rolling
set -eu
ENV="${1:?Uso: $0 nombre-entorno etiqueta}"
ETQ="${2:?Uso: $0 nombre-entorno etiqueta}"
aws elasticbeanstalk describe-environment-resources --environment-name "$ENV" \
  --query 'EnvironmentResources.Instances[].Id' --output text | tr '\t' '\n' | sort > "ids-$ETQ.txt"
echo "$(wc -l < "ids-$ETQ.txt") instancias → ids-$ETQ.txt"
# Requiere enhanced health (viene activado por defecto al crear desde la consola).
aws elasticbeanstalk describe-instances-health --environment-name "$ENV" \
  --attribute-names HealthStatus LaunchedAt Deployment \
  --query 'InstanceHealthList[].[InstanceId,HealthStatus,LaunchedAt,Deployment.VersionLabel]' \
  --output table | tee "salud-$ETQ.txt"
# Para comparar:  comm -3 ids-antes-rolling.txt ids-despues-rolling.txt
#   columna 1 = solo antes (terminadas), columna 2 = solo después (nuevas)
