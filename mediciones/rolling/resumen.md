# Rolling: v3 → rolling-v1

- Entorno: claudistas-rolling-env, us-east-2.
- Fecha: 2026-10-17, horas de Colombia (UTC-5).
- Commit nuevo: ea439819f94ad282e6880ea13f08019706528158.
- Etiqueta anterior: blacklist-base-01; etiqueta final: rolling-v1.
- Política: Rolling, Fixed, lote de 1; Auto Scaling mínimo 3 y máximo 6.
- Inicio Events: 2026-10-17T22:34:35.730000-05:00.
- Fin Events: 2026-10-17T22:43:52.816000-05:00.
- Duración Events: 9 min 17.086 s.
- Instancias antes/después: 3/3; máximo observado en sondeos: 3.
- Las tres instancias originales se actualizaron en sitio; mismos IDs antes y después.

## HTTP durante la ventana de Events

- Peticiones: 768.
- Códigos: {'200': 767, '000': 1}.
- Errores 5xx: 0.
- Código 000: 1 (curl no obtuvo respuesta HTTP con límite de 2 s; no permite atribuir la causa al servidor).
- Latencia de respuestas 200: media 0.196 s; máxima 0.363 s.
- Primera respuesta nueva: 22:35:41.787000.
- Última respuesta anterior: 22:40:21.353000.
- Convivencia observada: 279.566 s.

## Alcance y evidencias

El CSV completo incluye tiempo antes y después del despliegue: 1152 solicitudes, 2 sin respuesta HTTP. Las métricas anteriores se filtran a la ventana de Events para evitar mezclar la preparación con el despliegue.
El monitor agrega una pausa de 0,5 s después de cada solicitud; no equivale a dos solicitudes exactas por segundo. Es un muestreo de /version, no una prueba de carga ni una garantía de ausencia de interrupciones.
Los sondeos de instancias fueron periódicos, no un seguimiento continuo del número de instancias ni de su capacidad efectiva en el balanceador.

Archivos: eventos.json, instancias-antes.json, instancias-despues.json, recursos-antes.json, recursos-despues.json, configuracion-antes.json, seguimiento.jsonl y CSV/TXT de HTTP. No contienen las variables secretas del entorno.

## Para Word

- 7.2.1: configuración, commit y versiones.
- 7.2.2: instancias 3 antes, 3 de máximo observado y 3 después.
- 7.2.3: Events y seguimiento por lotes; añadir capturas de consola.
- 7.2.4: duración según Events (no duración total del monitor).
- 7.2.5: mismos IDs antes/después.
- 7.2.6: métricas HTTP filtradas al despliegue.
- 7.2.7: actualización en sitio, convivencia de versiones y una solicitud sin respuesta HTTP si corresponde al conteo anterior.
