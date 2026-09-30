# Anexo — Glosario de Negocio (EnergiTech · Dominio Demanda Energética)

> Producto de trabajo de UNE 0078 3.7.1.4 — *Repositorio del metadato de negocio (glosario de términos) poblado*.
> **Versión:** 1.0 · **Fecha:** 2026-04-09 · **Steward principal:** Dirección de Operaciones.

## Convenciones

- **Estado**: `Aprobado` / `Borrador` / `En revisión`.
- Cada término se enlaza con activos del [`catalogo-datos.md`](catalogo-datos.md) y campos del [`diccionario-datos.md`](diccionario-datos.md).

## Términos

| # | Término | Definición | Sinónimos | Dueño | Estado |
|---:|---|---|---|---|---|
| 1 | Apetito de riesgo | Nivel máximo de riesgo asumible por la organización al usar productos de datos en la toma de decisiones. | — | CDO | Aprobado |
| 2 | Cliente | Persona física o jurídica titular de uno o más contratos de suministro con EnergiTech. | Titular | Comercializadora | Aprobado |
| 3 | Cliente residencial | Cliente persona física con un contrato doméstico de potencia contratada < 15 kW. | Cliente doméstico | Comercializadora | Aprobado |
| 4 | Cliente crítico | Cliente cuyo corte de suministro implica riesgo para personas, salud o continuidad de servicio esencial (hospitales, industria 24x7). | Cliente esencial | Comercializadora | Aprobado |
| 5 | Consumo | Energía activa demandada por un punto de suministro en un periodo dado, expresada en kWh. | Demanda | Operaciones | Aprobado |
| 6 | Consumo mensual | Suma del consumo de un punto de suministro durante un mes natural. | — | Operaciones | Aprobado |
| 7 | Curva de carga | Serie temporal de consumo asociado a un punto de suministro o agregado de puntos. | Perfil de consumo | Operaciones | Aprobado |
| 8 | CUPS | *Código Unificado de Punto de Suministro*: identificador legal del punto de suministro (RD 1110/2007). | — | Operaciones | Aprobado |
| 9 | Punto de suministro | Lugar físico identificado por CUPS donde se entrega energía bajo un contrato. | PS | Operaciones | Aprobado |
| 10 | Smart-meter | Contador inteligente que registra lecturas de consumo a granularidad ≤ 15 min. | Contador inteligente | Operaciones | Aprobado |
| 11 | Lectura | Medida individual de consumo registrada por un smart-meter en un instante. | — | Operaciones | Aprobado |
| 12 | Telemetría | Conjunto de lecturas remitidas por los smart-meters al sistema central. | — | CTO | Aprobado |
| 13 | Previsión de demanda | Estimación de la energía a demandar por una zona y franja horaria, generada por un modelo predictivo. | Forecast de demanda | Operaciones | Aprobado |
| 14 | Horizonte de previsión | Distancia temporal entre el instante de cálculo y el instante previsto. | — | Operaciones | Aprobado |
| 15 | MAPE | *Mean Absolute Percentage Error*. Medida de error usada para validar la previsión. | Error porcentual medio absoluto | Resp. Calidad | Aprobado |
| 16 | Zona de red | Área geográfica con suministro gestionado de forma agregada (subestación o conjunto de éstas). | Área de red | Operaciones | Aprobado |
| 17 | Tarifa | Conjunto de condiciones económicas aplicables a un contrato. | — | Comercializadora | Aprobado |
| 18 | Contrato | Vínculo formal entre un cliente y EnergiTech para el suministro en un punto. | — | Comercializadora | Aprobado |
| 19 | PII | Información de identificación personal (DNI, dirección, email…). | Datos personales | DPO | Aprobado |
| 20 | Pseudonimización | Técnica de protección que sustituye PII por identificadores no reversibles sin información adicional (RGPD art. 4.5). | — | DPO | Aprobado |
| 21 | Producto de datos | Conjunto de datos publicado y consumido por procesos de negocio (p.ej. la curva prevista). | Data product | CDO | Aprobado |
| 22 | Cuadro de mandos | Visualización agregada de KPIs de negocio o de calidad. | Dashboard | Operaciones | Aprobado |
| 23 | Dato maestro | Dato de entidad clave para el negocio (Cliente, Producto, Zona…) compartido entre sistemas. | MDM record | Arquitecto del Dato | Aprobado |
| 24 | Dato de referencia | Conjunto cerrado de valores de uso transversal (códigos postales, tipos de tarifa…). | Reference data | Arquitecto del Dato | Aprobado |
| 25 | Steward del dato | Persona responsable de la calidad y definición de un activo de datos. | Custodio del dato | CDO | Aprobado |
| 26 | Linaje | Trazabilidad del dato desde la fuente hasta su uso final. | Data lineage | Arquitecto del Dato | Aprobado |
| 27 | Apetito de calidad | Mínimos aceptables de calidad para que el producto de datos sea publicable. | Umbral de DQ | Resp. Calidad | Aprobado |

## Control de cambios

| Versión | Fecha | Cambio | Autor |
|---|---|---|---|
| 1.0 | 2026-04-09 | Línea base con 27 términos del dominio Demanda. | Steward Operaciones |
