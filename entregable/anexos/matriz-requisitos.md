# Anexo — Matriz de Requisitos del Dato (EnergiTech · Previsión de Demanda)

> Producto de trabajo de UNE 0078 3.3.1.4 — *Catálogo actualizado y validado de requisitos del dato con su prioridad establecida*.
> **Versión:** 1.0 · **Fecha:** 2026-03-26 · **Aprobador:** Director del Dato (CDO).

## Leyenda

- **Tipo**: `B` Negocio · `D` Dato · `S` Seguridad · `Q` Calidad · `I` Infraestructura.
- **Prioridad MoSCoW**: `M` Must · `S` Should · `C` Could · `W` Won't (esta iteración).
- **Estado**: `Id` Identificado · `Ap` Aprobado · `Im` Implantado · `Re` Retirado.

## Catálogo

| ID | Título | Descripción | Tipo | Fuente | Prio. | Propietario | Criterio de aceptación | Datos asociados | Estado |
|---|---|---|:---:|---|:---:|---|---|---|:---:|
| RB-01 | Disponibilidad de previsión 24 h | El sistema debe entregar la curva prevista con horizonte ≥ 24 h y granularidad horaria. | B | F-NEG-01 | M | Operaciones | Curva publicada en cuadro de mandos antes de las 06:00 cada día. | producto_datos.prevision | Ap |
| RB-02 | Cobertura geográfica | La previsión debe cubrir todas las zonas de red activas. | B | F-NEG-01 | M | Operaciones | 100 % de zonas con `estado=activo`. | zona_red | Ap |
| RB-03 | Re-ejecución bajo demanda | El planificador debe poder relanzar la previsión cuando rechace los resultados (T10). | B | F-NEG-01 | S | Operaciones | Ciclo completo < 30 min. | — | Id |
| RB-04 | Atención a clientes críticos | La previsión debe distinguir clientes críticos (hospitales, industria 24x7). | B | F-NEG-02 | M | Comercializadora | Atributo `criticidad` consultable y filtrable. | cliente, contrato | Ap |
| RD-01 | Identificador único de punto de suministro | Cada lectura debe llevar `id_punto_suministro` no nulo. | D | F-LEG-02 | M | Arquitecto del Dato | NULLs = 0 en producción. | lectura_smart_meter | Im |
| RD-02 | Marca temporal en UTC | Toda lectura registra `timestamp` en UTC. | D | F-INT-01 | M | Arquitecto del Dato | 100 % registros en UTC. | lectura_smart_meter | Im |
| RD-03 | Granularidad mínima | Granularidad de lectura ≤ 15 min. | D | F-LEG-02 | M | Operaciones | Δt(modo) ≤ 900 s. | lectura_smart_meter | Im |
| RD-04 | Series meteorológicas horarias | Datos meteo accesibles a granularidad horaria por zona. | D | F-NEG-01 | M | Arquitecto del Dato | Cobertura ≥ 99 %. | meteo_zona | Ap |
| RD-05 | Catálogo de zonas de red | Existe un catálogo único `zona_red` referenciado por todas las extracciones. | D | F-NEG-01 | S | Arquitecto del Dato | Una sola tabla maestra. | zona_red | Ap |
| RS-01 | Pseudonimización de PII | La PII debe pseudonimizarse antes de cualquier explotación analítica. | S | F-LEG-01 | M | DPO | DNI, email y dirección no presentes en capa analítica. | cliente | Ap |
| RS-02 | Trazabilidad de accesos | Toda consulta a datos sensibles queda registrada con usuario, propósito y timestamp. | S | F-LEG-01, F-INT-02 | M | CISO | Logs auditables ≥ 12 meses. | log_accesos | Id |
| RS-03 | Cifrado en tránsito y reposo | Datos PII cifrados con TLS 1.2+ y AES-256. | S | F-INT-02 | M | CISO | Auditoría ENS sin no-conformidades. | infraestructura | Im |
| RQ-01 | Completitud de la serie de consumo | Completitud de lectura ≥ 99 % en ventana de 30 días. | Q | F-INT-01 | M | Resp. Calidad | (lecturas_recibidas / lecturas_esperadas) ≥ 0,99. | lectura_smart_meter | Ap |
| RQ-02 | Exactitud de lectura | Desviación lectura vs. patrón ≤ 2 %. | Q | F-LEG-02 | M | Resp. Calidad | Validación cruzada mensual. | lectura_smart_meter | Ap |
| RQ-03 | Consistencia inter-sistema cliente | Mismo cliente con mismos atributos identificativos en todos los silos. | Q | F-INT-01 | M | Resp. Calidad | Tasa coincidencia ≥ 98 % tras matching. | cliente | Id |
| RQ-04 | Frescura de meteo | Datos meteo publicados en plataforma con retardo ≤ 1 h respecto al evento. | Q | F-NEG-01 | S | Resp. Calidad | Mediana(latencia) ≤ 60 min. | meteo_zona | Id |
| RI-01 | Capacidad de ingesta | Soportar ingesta de ≥ 10⁹ lecturas/día con latencia ≤ 5 min. | I | F-TEC-01 | M | CTO | Pruebas de carga superadas en pre-producción. | infraestructura | Id |
| RI-02 | Disponibilidad analítica | Plataforma analítica con SLA 99,5 % horario laboral. | I | F-TEC-01 | S | CTO | Informes mensuales de SLA. | infraestructura | Id |

## Matriz de trazabilidad fuente → requisito

| Fuente | Requisitos cubiertos |
|---|---|
| F-NEG-01 (Dir. Operaciones) | RB-01, RB-02, RB-03, RD-04, RD-05, RQ-04 |
| F-NEG-02 (Comercializadora) | RB-04 |
| F-LEG-01 (RGPD/LOPDGDD) | RS-01, RS-02 |
| F-LEG-02 (RD 1110/2007) | RD-01, RD-03, RQ-02 |
| F-INT-01 (Pol. interna calidad) | RD-02, RQ-01, RQ-03 |
| F-INT-02 (ENS) | RS-02, RS-03 |
| F-TEC-01 (Inventario TI) | RI-01, RI-02 |

## Matriz de trazabilidad requisito → dato afectado

| Dato | Requisitos asociados |
|---|---|
| `lectura_smart_meter` | RD-01, RD-02, RD-03, RQ-01, RQ-02 |
| `cliente` | RB-04, RS-01, RQ-03 |
| `contrato` | RB-04 |
| `meteo_zona` | RD-04, RQ-04 |
| `zona_red` | RB-02, RD-05 |
| `producto_datos.prevision` | RB-01 |
| `log_accesos` | RS-02 |
| `infraestructura` | RS-03, RI-01, RI-02 |

## Control de cambios

| Versión | Fecha | Cambio | Autor |
|---|---|---|---|
| 1.0 | 2026-03-26 | Línea base inicial al cierre de la sesión 09. | CDO |
