# Rolling with additional batch · despliegue v1 → v2

Entorno `blacklist-env` (ALB, Auto Scaling 3–6 t3.micro), 16 oct 2026.
Política `RollingWithAdditionalBatch`, lote fijo de 1 instancia. Versión `v2` = commit `dac5bdf`.

## a. Instancias
- 3 instancias en servicio antes y después; pico de 4 durante el despliegue (lote adicional).

## b. Validación
- `scripts/medir.sh`: `GET /version` cada 0,5 s durante todo el despliegue → `rolling-lote-adicional-20261016-204604.csv`.
- `scripts/ids.sh` antes y después → `ids-*.txt`, `salud-*.txt`.
- `scripts/eventos.sh` → `eventos-rolling-lote-adicional.txt`.

| Resultado | Valor |
| --- | --- |
| Peticiones | 359, todas 200 |
| Errores 5xx / sin respuesta | 0 / 0 |
| Primera respuesta v2 | 20:47:47.7 (-05) |
| Última respuesta v1 | 20:49:28.6 (-05) |
| Convivencia v1 + v2 | 1 min 40,9 s |
| Latencia media / máx. | 0,165 s / 0,366 s |

## c. Tiempo total
- **3 min 25 s** según Events: `Environment update is starting` 01:46:10 UTC → `Environment update completed successfully` 01:49:35 UTC.
- La salud volvió a Ok a las 01:52:25 UTC (ver hallazgos).

## d. Instancias iniciales y nuevas
| Instancia | Antes | Después |
| --- | --- | --- |
| i-05dd0ae2af9d41bc8 | — | v2 (nueva, lote adicional) |
| i-08bd5749f9016d469 | v1 | v2 (actualizada en el lote 2) |
| i-07cb869f3e8a628aa | v1 | v2 (actualizada en el lote 3) |
| i-05746ab43c1ec7116 | v1 | terminada como excedente |

`salud-despues-*.txt` aún lista a i-05746ab43c1ec7116 porque se tomó mientras el balanceador la desregistraba.

## e. Secuencia (Events, hora -05)
1. 20:46:34 lanza 1 instancia adicional; 20:47:20 queda en servicio con v2 (lote 1).
2. 20:47:51 – 20:48:32 despliega v2 en i-08bd5749f9016d469 (lote 2).
3. 20:48:32 – 20:49:13 despliega v2 en i-07cb869f3e8a628aa (lote 3).
4. 20:49:30 termina i-05746ab43c1ec7116 como excedente; 20:49:35 fin del despliegue.

## f. Hallazgos
- Sin caída: la capacidad nunca bajó de 3 instancias y ninguna petición falló.
- La última instancia con v1 no se actualiza: se termina, porque las 3 en v2 ya cubren la capacidad.
- v1 y v2 respondieron a la vez durante 1 min 41 s; la API debe tolerar dos versiones simultáneas.
- Tras el fin, la salud pasó a Degraded unos 2 min mientras se desregistraba la instancia terminada; no afectó a los clientes.

## Segunda corrida · v2 → v3 (carpeta `v3/`)

Misma configuración, versión `v3` = commit `f5d96be`. Confirma que el resultado se repite.

| | v1 → v2 | v2 → v3 |
| --- | --- | --- |
| Duración (Events) | 3 min 25 s | 3 min 30 s |
| Peticiones / errores | 359 / 0 | 360 / 0 |
| Convivencia de versiones | 1 min 40,9 s | 1 min 39,2 s |
| Latencia media / máx. | 0,165 s / 0,366 s | 0,164 s / 0,364 s |
| Instancia adicional | i-05dd0ae2af9d41bc8 | i-01492cb02351b39cd |
| Actualizadas en sitio | i-08bd…, i-07cb… | i-05dd…, i-07cb… |
| Terminada como excedente | i-05746ab43c1ec7116 | i-08bd5749f9016d469 |

Secuencia v3 (UTC): 01:59:49 inicio · 02:00:14 lanza la adicional · 02:01:31 fin lote 1 ·
02:02:16 fin lote 2 · 02:02:57 fin lote 3 · 02:03:15 termina el excedente · 02:03:19 fin.

En las dos corridas la instancia terminada fue la única que seguía con la versión anterior, y la
adicional de una corrida se actualizó en sitio en la siguiente: el lote adicional no es temporal,
sino que reemplaza a una instancia vieja.
