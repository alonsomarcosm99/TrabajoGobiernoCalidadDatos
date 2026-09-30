# Anexo — Procedimientos de Medición de Calidad del Dato

> Producto de trabajo de UNE 0079 3.2 — *Control y monitorización de calidad del dato*.
> **Versión:** 1.0 · **Fecha:** 2026-04-30 · **Aprobador:** Responsable de Calidad del Dato.

Cada procedimiento contiene los **10 campos** exigidos por el enunciado del Proyecto 5.

---

## PM-EX-01 — Exactitud sintáctica de lecturas

| # | Campo | Valor |
|---|---|---|
| 1 | Característica de calidad | **Exactitud** (sintáctica) |
| 2 | Dato evaluado | `bronze.lectura_smart_meter` (todos los registros del día anterior) |
| 3 | Regla de medición | Una lectura es sintácticamente exacta si su `kwh ≥ 0` y está dentro del rango `[0, P99,99 histórico]`. |
| 4 | Fórmula | `M-EX-01 = 1 − (filas con kwh fuera de rango / total filas)` |
| 5 | Frecuencia | Diaria (06:00 UTC sobre datos del día previo) |
| 6 | Herramienta | dbt-tests (`accepted_range`) + perfilador OpenMetadata |
| 7 | Responsable (RACI) | R: *Steward* Operaciones · A: Resp. Calidad · C: CTO · I: CDO |
| 8 | Umbral aceptable | ≥ 0,995 |
| 9 | Acción correctiva | Aislar lote afectado; relanzar extracción del *gateway*; abrir ticket si recurrente. |
| 10 | Evidencias generadas | Informe diario en OpenMetadata; logs de dbt; ticket DQ en ServiceNow si no conforme. |

## PM-EX-02 — Exactitud semántica de lecturas (calibración)

| # | Campo | Valor |
|---|---|---|
| 1 | Característica | **Exactitud** (semántica) |
| 2 | Dato evaluado | `silver.lectura_smart_meter`, muestra de 1.000 puntos de suministro mensuales |
| 3 | Regla | Comparar lectura con patrón calibrado in-situ. |
| 4 | Fórmula | `M-EX-02 = 1 − media(\|lectura − patrón\| / patrón)` |
| 5 | Frecuencia | Mensual |
| 6 | Herramienta | Notebook auditoría + plataforma SCADA + OpenMetadata |
| 7 | Responsable | R: Resp. Calibración Operaciones · A: Resp. Calidad · C: Reguladores externos |
| 8 | Umbral | ≥ 0,98 (≤ 2 % desviación, conforme a RD 1110/2007 y RQ-02) |
| 9 | Acción correctiva | Recalibrar smart-meters fuera de umbral; comunicar al regulador si > 5 %. |
| 10 | Evidencias | Informe mensual de calibración; certificado del laboratorio; ticket DQ. |

## PM-CO-01 — Completitud de la serie de consumo

| # | Campo | Valor |
|---|---|---|
| 1 | Característica | **Completitud** (registros) |
| 2 | Dato evaluado | `silver.lectura_smart_meter`, ventana móvil 30 días |
| 3 | Regla | Comparar lecturas recibidas con esperadas (96 lecturas/día/PS). |
| 4 | Fórmula | `M-CO-01 = lecturas_recibidas / lecturas_esperadas` |
| 5 | Frecuencia | Diaria, granularidad zona/día |
| 6 | Herramienta | OpenMetadata profiler + query SQL programada en Airflow |
| 7 | Responsable | R: *Steward* Operaciones · A: Resp. Calidad · C: CTO |
| 8 | Umbral | ≥ 99 % por zona/día (RQ-01) |
| 9 | Acción correctiva | Re-extracción del *gateway*; imputación marcada para gaps < 2 h; escalado a operación de campo si > 4 h. |
| 10 | Evidencias | Informe diario por zona; histograma de gaps; ticket DQ; logs de imputación. |

## PM-CO-02 — Completitud de atributos *Must* en MDM

| # | Campo | Valor |
|---|---|---|
| 1 | Característica | **Completitud** (atributos) |
| 2 | Dato evaluado | `mdm.cliente_maestro` (atributos `dni_pseudo`, `tipo_cliente`, `criticidad`) |
| 3 | Regla | Ningún campo *Must* puede ser NULL en filas con `estado_maestro=activo`. |
| 4 | Fórmula | `M-CO-02 = 1 − filas_con_NULL / total_filas` |
| 5 | Frecuencia | Diaria |
| 6 | Herramienta | dbt-tests (`not_null`) + OpenMetadata |
| 7 | Responsable | R: *Steward* Comercial · A: Resp. Calidad · C: Comercializadora |
| 8 | Umbral | ≥ 99,5 % |
| 9 | Acción correctiva | Re-disparo del pipeline MDM; cola de revisión por *data steward* si > 100 filas. |
| 10 | Evidencias | Informe diario; cola de revisión; ticket DQ. |

## PM-CS-01 — Consistencia referencial Contrato → Punto de Suministro

| # | Campo | Valor |
|---|---|---|
| 1 | Característica | **Consistencia** (referencial) |
| 2 | Dato evaluado | `crm.contrato.cups → red.punto_suministro.cups` |
| 3 | Regla | Cada `cups` referenciado debe existir en la tabla maestra. |
| 4 | Fórmula | `M-CS-01 = filas_con_FK_válida / total_filas` |
| 5 | Frecuencia | Diaria |
| 6 | Herramienta | dbt-tests (`relationships`) + OpenMetadata |
| 7 | Responsable | R: Arquitecto del Dato · A: Resp. Calidad · C: Comercial, Operaciones |
| 8 | Umbral | 100 % |
| 9 | Acción correctiva | Bloquear merge de la rama dbt; abrir incidencia para sincronizar GIS-CRM. |
| 10 | Evidencias | Logs de dbt; informe en OpenMetadata; tabla `dq.violations_cs01`. |

## PM-CS-02 — Consistencia inter-sistema (matching MDM)

| # | Campo | Valor |
|---|---|---|
| 1 | Característica | **Consistencia** (inter-sistema) |
| 2 | Dato evaluado | `mdm.cliente_maestro` ↔ `crm.cliente`, `erp.cliente`, `mnt.cliente` |
| 3 | Regla | Cada cliente debe tener un único `cliente_id_maestro` con `confianza_match ≥ 0,75`. |
| 4 | Fórmula | `M-CS-02 = 1 − filas_con_match_inferior / total_filas` |
| 5 | Frecuencia | Semanal (lunes 03:00 UTC) |
| 6 | Herramienta | Splink (Spark) + OpenMetadata + ServiceNow |
| 7 | Responsable | R: Arquitecto del Dato · A: Resp. Calidad · C: DPO, Comercializadora |
| 8 | Umbral | ≥ 0,98 (RQ-03) |
| 9 | Acción correctiva | Cola de *stewardship* para registros 0,75–0,91; revisión manual; ajustar reglas si > 1 % se queda sin match. |
| 10 | Evidencias | Informe semanal; cola de stewardship con tiempo de resolución; tabla `dq.history_matching`. |

## PM-AC-01 — Frescura de datos meteorológicos

| # | Campo | Valor |
|---|---|---|
| 1 | Característica | **Actualidad** (frescura ingesta) |
| 2 | Dato evaluado | `bronze.meteo_zona` |
| 3 | Regla | Mediana del lag entre `timestamp_evento` y `now()`. |
| 4 | Fórmula | `M-AC-01 = mediana(now − fecha_evento)` (en minutos) |
| 5 | Frecuencia | Cada hora |
| 6 | Herramienta | Airflow `FreshnessSensor` + OpenMetadata |
| 7 | Responsable | R: *Steward* Operaciones · A: Resp. Calidad · C: CTO |
| 8 | Umbral | ≤ 60 min (RQ-04) |
| 9 | Acción correctiva | Conmutar a proveedor de meteo secundario; reintentos automatizados. |
| 10 | Evidencias | Métricas en Prometheus/Grafana; alertas Slack; ticket DQ si > 90 min. |

## PM-AC-02 — Frescura de telemetría

| # | Campo | Valor |
|---|---|---|
| 1 | Característica | **Actualidad** (frescura telemetría) |
| 2 | Dato evaluado | `bronze.lectura_smart_meter` |
| 3 | Regla | Mediana del lag entre `timestamp_utc` y `now()`. |
| 4 | Fórmula | `M-AC-02 = mediana(now − timestamp_utc)` (en minutos) |
| 5 | Frecuencia | Cada hora |
| 6 | Herramienta | Airflow `FreshnessSensor` + OpenMetadata |
| 7 | Responsable | R: *Steward* Operaciones · A: Resp. Calidad · C: Operación de campo |
| 8 | Umbral | ≤ 30 min |
| 9 | Acción correctiva | Diagnóstico de comunicaciones por zona; despacho de equipos a *gateways* sin reportar > 1 h. |
| 10 | Evidencias | Métricas en Prometheus; alertas; ticket DQ; informe a operación de red. |

---

## Matriz RACI consolidada

| Procedimiento | R | A | C | I |
|---|---|---|---|---|
| PM-EX-01 | *Steward* Operaciones | Resp. Calidad | CTO | CDO |
| PM-EX-02 | Resp. Calibración | Resp. Calidad | Reguladores | CDO |
| PM-CO-01 | *Steward* Operaciones | Resp. Calidad | CTO | CDO |
| PM-CO-02 | *Steward* Comercial | Resp. Calidad | Comercializadora | CDO |
| PM-CS-01 | Arquitecto del Dato | Resp. Calidad | Comercial, Operaciones | CDO |
| PM-CS-02 | Arquitecto del Dato | Resp. Calidad | DPO, Comercializadora | CDO |
| PM-AC-01 | *Steward* Operaciones | Resp. Calidad | CTO | CDO |
| PM-AC-02 | *Steward* Operaciones | Resp. Calidad | Operación de campo | CDO |

## Control de cambios

| Versión | Fecha | Cambio | Autor |
|---|---|---|---|
| 1.0 | 2026-04-30 | Línea base con 8 procedimientos. | Resp. Calidad |
