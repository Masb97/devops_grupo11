#!/usr/bin/env bash
# Mide un despliegue desde el punto de vista del cliente.
# Uso:   ./scripts/medir.sh http://mi-entorno.us-east-1.elasticbeanstalk.com rolling [intervalo_s]
# Para:  Ctrl+C cuando Events diga "Environment update completed successfully".
# Deja:  rolling-AAAAMMDD-HHMMSS.csv y un resumen en pantalla (y en .txt).
set -u
URL="${1:?Uso: $0 URL etiqueta [intervalo_s]}"
ETQ="${2:-despliegue}"
INT="${3:-0.5}"
BASE="${ETQ}-$(date +%Y%m%d-%H%M%S)"
CSV="${BASE}.csv"
echo "hora,codigo,version,instancia,segundos" > "$CSV"

resumen() {
  trap - INT TERM
  echo
  awk -F, '
    function s(h,  p) { split(h, p, ":"); return p[1]*3600 + p[2]*60 + p[3] }
    function dur(x) { return sprintf("%d min %04.1f s", int(x/60), x - 60*int(x/60)) }
    NR == 1 { next }
    {
      n++; cod[$2]++
      if (n == 1) ini = $1
      fin = $1
      if ($2 ~ /^5/) e5++
      if ($2 == "000") to++
      if ($2 == "200" && $3 != "") {
        if (v1 == "") v1 = $3
        if ($3 == v1) { ult_v1 = $1 }
        else { if (v2 == "") { v2 = $3; pri_v2 = $1 }; ult_v2 = $1 }
        if (!(($3 SUBSEP $4) in vista)) { vista[$3 SUBSEP $4] = 1; inst[$3] = inst[$3] " " $4 }
      }
    }
    END {
      printf "Peticiones: %d  (de %s a %s, %s)\n", n, ini, fin, dur(s(fin) - s(ini))
      printf "Códigos:"; for (c in cod) printf "  %s=%d", c, cod[c]; print ""
      printf "Errores 5xx: %d   Timeouts/sin respuesta (000): %d\n", e5 + 0, to + 0
      printf "Versión inicial: %s   instancias:%s\n", v1, inst[v1]
      if (v2 != "") {
        printf "Versión nueva:   %s   instancias:%s\n", v2, inst[v2]
        printf "Primera respuesta %s: %s\n", v2, pri_v2
        printf "Última respuesta  %s: %s\n", v1, ult_v1
        c = s(ult_v1) - s(pri_v2)
        if (c > 0) printf "Ventana de convivencia v1+v2: %s\n", dur(c)
        else       printf "Sin convivencia: el corte fue limpio (o hubo un hueco de %s)\n", dur(-c)
      } else print "Nunca apareció una versión distinta: ¿terminó el despliegue?"
    }' "$CSV" | tee "${BASE}.txt"
  echo "Detalle: $CSV"
  exit 0
}
trap resumen INT TERM

echo "Midiendo $URL/version cada ${INT}s → $CSV  (Ctrl+C para terminar)"
while true; do
  hora=$(date +%H:%M:%S.%3N)
  salida=$(curl -s -m 2 -o - -w $'\n%{http_code} %{time_total}' "$URL/version")
  cuerpo=${salida%$'\n'*}
  read -r codigo seg <<< "${salida##*$'\n'}"
  version=$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' <<< "$cuerpo")
  instancia=$(sed -n 's/.*"instance": *"\([^"]*\)".*/\1/p' <<< "$cuerpo")
  echo "$hora,$codigo,$version,$instancia,$seg" | tee -a "$CSV"
  sleep "$INT"
done
