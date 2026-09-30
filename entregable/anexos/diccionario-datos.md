# Anexo — Diccionario de Datos (EnergiTech)

> Producto de trabajo de UNE 0078 3.7.1.4 — *Repositorio del metadato operativo (diccionario de datos) poblado*.
> **Versión:** 1.0 · **Fecha:** 2026-04-09 · **Steward principal:** Arquitecto del Dato.

## Convenciones

- **Tipo SQL** corresponde a Snowflake/PostgreSQL (consistente con el Lakehouse propuesto en P3).
- **PII**: `Sí` · `Pseudo` (pseudonimizada) · `No`.
- **Origen** apunta al activo del [`catalogo-datos.md`](catalogo-datos.md).

---

## Tabla `bronze.lectura_smart_meter`

| Campo | Tipo | Nullable | PK/FK | Restricciones | PII | Descripción |
|---|---|:---:|:---:|---|:---:|---|
| `id_lectura` | BIGINT | No | PK | — | No | Identificador secuencial. |
| `id_punto_suministro` | VARCHAR(22) | No | FK → `red.punto_suministro.cups` | Regex CUPS válido (`ES\d{16}[A-Z]{2}\d?[A-Z]?`) | No | CUPS del punto de suministro. |
| `timestamp_utc` | TIMESTAMP_NTZ | No | — | UTC, no futuro | No | Instante de la lectura. |
| `kwh` | NUMERIC(10,4) | No | — | ≥ 0 | No | Energía activa registrada en el periodo. |
| `flag_anomalia` | BOOLEAN | No | — | default `false` | No | Marcado por reglas de calidad. |
| `firma_gateway` | VARCHAR(128) | No | — | HMAC-SHA256 | No | Firma del concentrador para integridad. |
| `fecha_ingesta` | TIMESTAMP_NTZ | No | — | default `now()` | No | Auditoría de ingesta. |

## Tabla `silver.lectura_smart_meter`

Hereda los campos anteriores y añade:

| Campo | Tipo | Nullable | Restricciones | Descripción |
|---|---|:---:|---|---|
| `kwh_imputado` | BOOLEAN | No | default `false` | `true` si el valor procede de imputación por gap. |
| `id_zona_red` | VARCHAR(8) | No | FK → `red.zona_red.id_zona` | Zona derivada del punto. |

## Tabla `crm.cliente`

| Campo | Tipo | Nullable | PK/FK | Restricciones | PII | Descripción |
|---|---|:---:|:---:|---|:---:|---|
| `id_cliente` | VARCHAR(18) | No | PK | Salesforce ID | No | Identificador interno CRM. |
| `dni` | VARCHAR(20) | Sí | UQ | Validación NIF/NIE | Sí | Documento legal. |
| `nombre` | VARCHAR(120) | No | — | — | Sí | Nombre completo. |
| `email` | VARCHAR(160) | Sí | — | RFC 5322 | Sí | Correo de contacto. |
| `telefono` | VARCHAR(20) | Sí | — | E.164 | Sí | Teléfono de contacto. |
| `direccion` | VARCHAR(255) | Sí | — | — | Sí | Dirección postal. |
| `cp` | VARCHAR(5) | Sí | FK → `ref.codigo_postal` | 5 dígitos | No | Código postal. |
| `tipo_cliente` | VARCHAR(20) | No | — | `residencial` / `empresa` / `crítico` | No | Segmentación. |
| `criticidad` | VARCHAR(10) | No | — | `alta` / `media` / `baja` | No | Atributo de cliente crítico. |
| `fecha_alta` | DATE | No | — | — | No | Alta de la ficha CRM. |

## Tabla `silver.cliente` (capa pseudonimizada)

| Campo | Tipo | Nullable | PK | Restricciones | PII | Descripción |
|---|---|:---:|:---:|---|:---:|---|
| `dni_pseudo` | CHAR(64) | No | PK | SHA-256(DNI + sal organizativa) | Pseudo | Identificador estable sin reidentificación directa. |
| `id_cliente` | VARCHAR(18) | No | UQ | — | No | Identificador CRM (no PII). |
| `tipo_cliente` | VARCHAR(20) | No | — | enum | No | Mantiene segmentación. |
| `criticidad` | VARCHAR(10) | No | — | enum | No | — |
| `cp` | VARCHAR(5) | Sí | FK | — | No | — |
| `fecha_alta` | DATE | No | — | — | No | — |

## Tabla `crm.contrato`

| Campo | Tipo | Nullable | PK/FK | Restricciones | PII | Descripción |
|---|---|:---:|:---:|---|:---:|---|
| `id_contrato` | VARCHAR(18) | No | PK | — | No | Identificador del contrato. |
| `id_cliente` | VARCHAR(18) | No | FK → `crm.cliente` | — | No | Titular. |
| `cups` | VARCHAR(22) | No | FK → `red.punto_suministro` | Regex CUPS | No | Punto asociado. |
| `id_tarifa` | VARCHAR(10) | No | FK → `erp.tarifa` | — | No | Tarifa contratada. |
| `potencia_contratada_kw` | NUMERIC(6,2) | No | — | > 0 | No | Potencia. |
| `estado` | VARCHAR(15) | No | — | `activo`/`baja`/`suspendido` | No | Estado contractual. |
| `fecha_inicio` | DATE | No | — | — | No | — |
| `fecha_fin` | DATE | Sí | — | ≥ `fecha_inicio` | No | — |

## Tabla `red.punto_suministro`

| Campo | Tipo | Nullable | PK/FK | Restricciones | PII | Descripción |
|---|---|:---:|:---:|---|:---:|---|
| `cups` | VARCHAR(22) | No | PK | Regex CUPS | No | Identificador legal del PS. |
| `id_zona_red` | VARCHAR(8) | No | FK → `red.zona_red` | — | No | Zona de red asignada. |
| `direccion_norm` | VARCHAR(255) | Sí | — | — | No | Dirección normalizada (sin titular). |
| `cp` | VARCHAR(5) | No | FK → `ref.codigo_postal` | — | No | — |
| `latitud` | NUMERIC(9,6) | Sí | — | [-90, 90] | No | Coordenada. |
| `longitud` | NUMERIC(9,6) | Sí | — | [-180, 180] | No | — |

## Tabla `bronze.meteo_zona`

| Campo | Tipo | Nullable | PK/FK | Restricciones | PII | Descripción |
|---|---|:---:|:---:|---|:---:|---|
| `id_zona_red` | VARCHAR(8) | No | PK (compuesta) | FK | No | Zona. |
| `timestamp_utc` | TIMESTAMP_NTZ | No | PK (compuesta) | UTC | No | Hora de la observación. |
| `temperatura_c` | NUMERIC(5,2) | Sí | — | [-50, 60] | No | °C. |
| `irradiancia_wm2` | NUMERIC(7,2) | Sí | — | ≥ 0 | No | W/m². |
| `viento_ms` | NUMERIC(5,2) | Sí | — | ≥ 0 | No | m/s. |
| `humedad_pct` | NUMERIC(5,2) | Sí | — | [0, 100] | No | %. |

## Tabla `gold.prevision_demanda`

| Campo | Tipo | Nullable | PK | Restricciones | PII | Descripción |
|---|---|:---:|:---:|---|:---:|---|
| `run_id` | VARCHAR(36) | No | PK (compuesta) | UUID | No | Ejecución del modelo. |
| `id_zona_red` | VARCHAR(8) | No | PK | FK | No | Zona prevista. |
| `timestamp_objetivo_utc` | TIMESTAMP_NTZ | No | PK | UTC | No | Hora prevista. |
| `kwh_previstos` | NUMERIC(12,2) | No | — | ≥ 0 | No | Energía prevista. |
| `mape_estimado` | NUMERIC(5,2) | Sí | — | [0, 100] | No | Error esperado. |
| `model_id` | VARCHAR(64) | No | — | — | No | Versión del modelo. |
| `fecha_publicacion` | TIMESTAMP_NTZ | No | — | default `now()` | No | Auditoría. |

## Control de cambios

| Versión | Fecha | Cambio | Autor |
|---|---|---|---|
| 1.0 | 2026-04-09 | Línea base con 7 tablas representativas del dominio Demanda. | Arquitecto del Dato |
