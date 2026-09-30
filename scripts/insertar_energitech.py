"""Script de inserción del caso EnergiTech en OpenMetadata.

Carga un modelo simplificado del trabajo de la asignatura Gobierno y Calidad
del Dato (MUBDCN UCLM 2025/26) en una instancia local de OpenMetadata.
Está pensado para reutilizar el OpenMetadata desplegado por el TFM del autor,
sin tocar ninguna de sus entidades: todo lo de EnergiTech vive bajo el prefijo
EnergiTech-* / energitech-demo y puede borrarse con borrar_energitech.py.

Uso:
    python scripts/insertar_energitech.py --token <JWT_OPENMETADATA>

Variables de entorno admitidas:
    OM_BASE_URL  (por defecto http://localhost:8585/api/v1)
    OM_TOKEN     (alternativa a --token)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import requests


OM_DEFAULT_BASE_URL = "http://localhost:8585/api/v1"

SERVICE_NAME = "energitech-demo"
DATABASE_NAME = "energitech"
DOMAIN_NAME = "EnergiTechDemanda"

SCHEMAS: list[dict[str, str]] = [
    {"name": "crm", "description": "Sistema CRM (Salesforce) - datos de cliente."},
    {"name": "red", "description": "Maestros de red electrica (CUPS, zonas)."},
    {"name": "silver", "description": "Capa Silver - dato limpio y pseudonimizado."},
    {"name": "gold", "description": "Capa Gold - productos de dato listos para explotacion."},
]

CLASSIFICATIONS: list[dict[str, Any]] = [
    {
        "name": "EnergiTechSensibilidad",
        "description": "Sensibilidad del activo segun politica de EnergiTech (P2).",
        "tags": [
            ("PII", "Contiene datos personales identificables. RGPD aplica."),
            ("Confidencial", "Datos confidenciales (cliente, contrato) - acceso restringido."),
            ("Interna", "Datos internos no sensibles - acceso amplio en EnergiTech."),
            ("Publica", "Datos publicables (referencia, meteo)."),
        ],
    },
    {
        "name": "EnergiTechCapa",
        "description": "Capa medallion del dato (P2 / P3).",
        "tags": [
            ("Bronze", "Dato crudo tal como llega de la fuente."),
            ("Silver", "Dato limpio, validado, pseudonimizado."),
            ("Gold", "Producto de dato agregado y publicable."),
        ],
    },
    {
        "name": "EnergiTechCriticidad",
        "description": "Criticidad de negocio para el proceso de prevision de demanda.",
        "tags": [
            ("Alta", "Critico para la prevision - rompe el proceso si falla."),
            ("Media", "Necesario pero degradable."),
            ("Baja", "Auxiliar o de referencia."),
        ],
    },
]

GLOSSARY_NAME = "EnergiTechNegocio"
GLOSSARY_DESCRIPTION = (
    "Glosario de negocio del dominio Demanda Energetica de EnergiTech. "
    "Producto de trabajo UNE 0078 3.7.1.4 - repositorio de metadato de negocio."
)
GLOSSARY_TERMS: list[dict[str, str]] = [
    {"name": "Cliente", "description": "Persona fisica o juridica titular de uno o mas contratos de suministro con EnergiTech."},
    {"name": "ClienteResidencial", "description": "Cliente persona fisica con contrato domestico < 15 kW."},
    {"name": "ClienteCritico", "description": "Cliente cuyo corte de suministro implica riesgo para personas o continuidad de servicio esencial."},
    {"name": "Consumo", "description": "Energia activa demandada por un punto de suministro en un periodo dado (kWh)."},
    {"name": "CurvaDeCarga", "description": "Serie temporal de consumo asociado a un punto de suministro o agregado."},
    {"name": "CUPS", "description": "Codigo Unificado de Punto de Suministro - identificador legal (RD 1110/2007)."},
    {"name": "PuntoDeSuministro", "description": "Lugar fisico identificado por CUPS donde se entrega energia bajo un contrato."},
    {"name": "SmartMeter", "description": "Contador inteligente que registra lecturas de consumo a granularidad <= 15 min."},
    {"name": "Lectura", "description": "Medida individual de consumo registrada por un smart-meter en un instante."},
    {"name": "PrevisionDemanda", "description": "Estimacion de energia a demandar por zona y franja horaria, generada por modelo predictivo."},
    {"name": "MAPE", "description": "Mean Absolute Percentage Error. Medida del error de la prevision."},
    {"name": "ZonaDeRed", "description": "Area geografica con suministro gestionado de forma agregada."},
    {"name": "Tarifa", "description": "Conjunto de condiciones economicas aplicables a un contrato."},
    {"name": "Contrato", "description": "Vinculo formal entre un cliente y EnergiTech para el suministro en un punto."},
    {"name": "PII", "description": "Personally Identifiable Information - datos personales identificables (DNI, email...)."},
    {"name": "Pseudonimizacion", "description": "Sustitucion de PII por identificadores no reversibles (RGPD art. 4.5)."},
    {"name": "ProductoDeDatos", "description": "Conjunto de datos publicado para consumo de procesos de negocio."},
    {"name": "DatoMaestro", "description": "Dato de entidad clave (Cliente, Producto, Zona...) compartido entre sistemas."},
    {"name": "StewardDelDato", "description": "Persona responsable de la calidad y definicion de un activo de datos."},
]

CUSTOM_PROPERTIES: list[dict[str, str]] = [
    {"name": "UNE0078proceso", "description": "Proceso UNE 0078 al que da evidencia el activo (ej. 3.7, 3.10, 3.12)."},
    {"name": "UNE0081caracteristica", "description": "Caracteristica de calidad UNE 0081 medida sobre el activo."},
    {"name": "stewardEnergiTech", "description": "Steward de negocio responsable del activo en EnergiTech."},
    {"name": "capaMedallion", "description": "Capa medallion (Bronze/Silver/Gold) en la arquitectura de P3."},
]


def _col(name: str, dtype: str, *, nullable: bool = True, length: int | None = None,
         precision: int | None = None, scale: int | None = None,
         description: str = "", constraint: str | None = None,
         tags: list[str] | None = None) -> dict[str, Any]:
    col: dict[str, Any] = {
        "name": name,
        "dataType": dtype,
        "dataTypeDisplay": dtype.lower() + (f"({length})" if length else "")
        + (f"({precision},{scale})" if precision is not None and scale is not None else ""),
        "description": description or name,
    }
    if length is not None:
        col["dataLength"] = length
    if precision is not None:
        col["precision"] = precision
    if scale is not None:
        col["scale"] = scale
    if constraint:
        col["constraint"] = constraint
    if tags:
        col["tags"] = [{"tagFQN": t, "source": "Classification", "labelType": "Manual", "state": "Confirmed"} for t in tags]
    return col


TABLES: list[dict[str, Any]] = [
    {
        "schema": "crm",
        "name": "cliente",
        "description": "Maestro de cliente del CRM Salesforce. Contiene PII; aplican POL-PII-01 y POL-ACC-01.",
        "tags": ["EnergiTechSensibilidad.PII", "EnergiTechCriticidad.Alta"],
        "glossary_terms": ["EnergiTechNegocio.Cliente", "EnergiTechNegocio.ClienteResidencial", "EnergiTechNegocio.PII"],
        "extension": {"UNE0078proceso": "3.7 / 3.10", "UNE0081caracteristica": "Exactitud, Unicidad", "stewardEnergiTech": "Comercializadora", "capaMedallion": "Bronze"},
        "columns": [
            _col("id_cliente", "VARCHAR", nullable=False, length=18, constraint="PRIMARY_KEY", description="Identificador interno CRM."),
            _col("dni", "VARCHAR", length=20, constraint="UNIQUE", description="Documento legal del titular.", tags=["EnergiTechSensibilidad.PII"]),
            _col("nombre", "VARCHAR", length=120, description="Nombre completo del titular.", tags=["EnergiTechSensibilidad.PII"]),
            _col("email", "VARCHAR", length=160, description="Correo de contacto.", tags=["EnergiTechSensibilidad.PII"]),
            _col("telefono", "VARCHAR", length=20, description="Telefono de contacto (E.164).", tags=["EnergiTechSensibilidad.PII"]),
            _col("tipo_cliente", "VARCHAR", length=20, description="Segmentacion: residencial / empresa / critico."),
            _col("criticidad", "VARCHAR", length=10, description="Atributo de cliente critico: alta / media / baja."),
            _col("fecha_alta", "DATE", description="Fecha de alta de la ficha CRM."),
        ],
    },
    {
        "schema": "crm",
        "name": "contrato",
        "description": "Contratos de suministro - vinculo cliente / punto / tarifa.",
        "tags": ["EnergiTechSensibilidad.Confidencial", "EnergiTechCriticidad.Alta"],
        "glossary_terms": ["EnergiTechNegocio.Contrato", "EnergiTechNegocio.Tarifa"],
        "extension": {"UNE0078proceso": "3.7", "UNE0081caracteristica": "Consistencia", "stewardEnergiTech": "Comercializadora", "capaMedallion": "Bronze"},
        "columns": [
            _col("id_contrato", "VARCHAR", nullable=False, length=18, constraint="PRIMARY_KEY", description="Identificador del contrato."),
            _col("id_cliente", "VARCHAR", length=18, description="FK -> crm.cliente.id_cliente."),
            _col("cups", "VARCHAR", length=22, description="FK -> red.punto_suministro.cups."),
            _col("id_tarifa", "VARCHAR", length=10, description="Tarifa contratada."),
            _col("potencia_contratada_kw", "DECIMAL", precision=6, scale=2, description="Potencia contratada (kW)."),
            _col("estado", "VARCHAR", length=15, description="activo / baja / suspendido."),
            _col("fecha_inicio", "DATE", description="Inicio del contrato."),
            _col("fecha_fin", "DATE", description="Fin del contrato (opcional)."),
        ],
    },
    {
        "schema": "red",
        "name": "punto_suministro",
        "description": "Maestro de puntos de suministro (CUPS) y su zona de red.",
        "tags": ["EnergiTechSensibilidad.Interna", "EnergiTechCriticidad.Alta"],
        "glossary_terms": ["EnergiTechNegocio.PuntoDeSuministro", "EnergiTechNegocio.CUPS", "EnergiTechNegocio.ZonaDeRed"],
        "extension": {"UNE0078proceso": "3.7 / 3.10", "UNE0081caracteristica": "Consistencia, Exactitud", "stewardEnergiTech": "Operaciones", "capaMedallion": "Bronze"},
        "columns": [
            _col("cups", "VARCHAR", nullable=False, length=22, constraint="PRIMARY_KEY", description="Identificador legal del punto de suministro."),
            _col("id_zona_red", "VARCHAR", length=8, description="Zona de red a la que pertenece."),
            _col("cp", "VARCHAR", length=5, description="Codigo postal."),
            _col("latitud", "DECIMAL", precision=9, scale=6, description="Latitud."),
            _col("longitud", "DECIMAL", precision=9, scale=6, description="Longitud."),
        ],
    },
    {
        "schema": "silver",
        "name": "lectura_smart_meter",
        "description": "Lecturas de smart-meter depuradas y pseudonimizadas (capa silver).",
        "tags": ["EnergiTechSensibilidad.Interna", "EnergiTechCriticidad.Alta"],
        "glossary_terms": ["EnergiTechNegocio.Lectura", "EnergiTechNegocio.SmartMeter", "EnergiTechNegocio.Consumo"],
        "extension": {"UNE0078proceso": "3.12", "UNE0081caracteristica": "Completitud, Exactitud, Actualidad", "stewardEnergiTech": "Operaciones", "capaMedallion": "Silver"},
        "columns": [
            _col("id_lectura", "BIGINT", nullable=False, constraint="PRIMARY_KEY", description="Identificador secuencial."),
            _col("id_punto_suministro", "VARCHAR", length=22, description="FK -> red.punto_suministro.cups."),
            _col("timestamp_utc", "TIMESTAMP", description="Instante de la lectura (UTC)."),
            _col("kwh", "DECIMAL", precision=10, scale=4, description="Energia activa registrada (>= 0)."),
            _col("flag_anomalia", "BOOLEAN", description="Marcado por reglas de calidad."),
            _col("id_zona_red", "VARCHAR", length=8, description="Zona derivada del punto."),
        ],
    },
    {
        "schema": "gold",
        "name": "curva_carga_zona",
        "description": "Curva de carga horaria agregada por zona de red (capa gold).",
        "tags": ["EnergiTechSensibilidad.Interna", "EnergiTechCriticidad.Alta"],
        "glossary_terms": ["EnergiTechNegocio.CurvaDeCarga", "EnergiTechNegocio.ZonaDeRed"],
        "extension": {"UNE0078proceso": "3.12", "UNE0081caracteristica": "Completitud, Consistencia", "stewardEnergiTech": "Operaciones", "capaMedallion": "Gold"},
        "columns": [
            _col("id_zona_red", "VARCHAR", nullable=False, length=8, constraint="NOT_NULL", description="Zona agregada."),
            _col("timestamp_utc", "TIMESTAMP", nullable=False, constraint="NOT_NULL", description="Hora UTC del agregado."),
            _col("kwh_agregados", "DECIMAL", precision=12, scale=2, description="Suma de kWh de la zona en la hora."),
        ],
        "primary_key": ["id_zona_red", "timestamp_utc"],
    },
    {
        "schema": "gold",
        "name": "prevision_demanda",
        "description": "Producto de datos PD-01: prevision de demanda por zona y hora. Salida del modelo predictivo.",
        "tags": ["EnergiTechSensibilidad.Interna", "EnergiTechCriticidad.Alta"],
        "glossary_terms": ["EnergiTechNegocio.PrevisionDemanda", "EnergiTechNegocio.MAPE", "EnergiTechNegocio.ProductoDeDatos"],
        "extension": {"UNE0078proceso": "3.12", "UNE0081caracteristica": "Exactitud, Credibilidad, Actualidad", "stewardEnergiTech": "Operaciones", "capaMedallion": "Gold"},
        "columns": [
            _col("run_id", "VARCHAR", nullable=False, length=36, constraint="NOT_NULL", description="UUID de la ejecucion del modelo."),
            _col("id_zona_red", "VARCHAR", nullable=False, length=8, constraint="NOT_NULL", description="Zona prevista."),
            _col("timestamp_objetivo_utc", "TIMESTAMP", nullable=False, constraint="NOT_NULL", description="Hora prevista (UTC)."),
            _col("kwh_previstos", "DECIMAL", precision=12, scale=2, description="Energia prevista (>= 0)."),
            _col("mape_estimado", "DECIMAL", precision=5, scale=2, description="Error porcentual esperado."),
            _col("model_id", "VARCHAR", length=64, description="Version del modelo."),
            _col("fecha_publicacion", "TIMESTAMP", description="Auditoria de publicacion."),
        ],
        "primary_key": ["run_id", "id_zona_red", "timestamp_objetivo_utc"],
    },
]

LINEAGE_EDGES: list[tuple[str, str]] = [
    ("crm.cliente", "crm.contrato"),
    ("red.punto_suministro", "crm.contrato"),
    ("red.punto_suministro", "silver.lectura_smart_meter"),
    ("silver.lectura_smart_meter", "gold.curva_carga_zona"),
    ("gold.curva_carga_zona", "gold.prevision_demanda"),
]


class OmApi:
    def __init__(self, *, base_url: str, token: str, timeout_s: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        )

    def _request(self, method: str, path: str, *, json_body: Any = None, params: dict | None = None) -> Any:
        if not path.startswith("/"):
            path = "/" + path
        url = f"{self.base_url}{path}"
        r = self.session.request(method, url, json=json_body, params=params, timeout=self.timeout_s)
        if r.status_code >= 400:
            raise RuntimeError(f"{method} {path} -> {r.status_code}\n{r.text[:2000]}")
        if not r.content:
            return {}
        return r.json()

    def get(self, path: str, params: dict | None = None) -> Any:
        return self._request("GET", path, params=params)

    def put(self, path: str, body: Any) -> Any:
        return self._request("PUT", path, json_body=body)

    def post(self, path: str, body: Any) -> Any:
        return self._request("POST", path, json_body=body)


def _upsert_database_service(api: OmApi) -> str:
    body = {
        "name": SERVICE_NAME,
        "displayName": "EnergiTech Demo (Practica 2 - Gobierno y Calidad del Dato)",
        "description": "Servicio simulado de EnergiTech para evidenciar la Practica 2 del MUBDCN UCLM. Aislado del TFM.",
        "serviceType": "Postgres",
        "connection": {
            "config": {
                "type": "Postgres",
                "username": "energitech_ro",
                "authType": {"password": "no-real-password"},
                "hostPort": "energitech.invalid:5432",
                "database": DATABASE_NAME,
            }
        },
    }
    resp = api.put("/services/databaseServices", body)
    return resp["fullyQualifiedName"]


def _upsert_database(api: OmApi, service_fqn: str) -> str:
    body = {
        "name": DATABASE_NAME,
        "displayName": "energitech",
        "description": "Base de datos logica del caso EnergiTech (capas medallion + CRM).",
        "service": service_fqn,
    }
    resp = api.put("/databases", body)
    return resp["fullyQualifiedName"]


def _upsert_schemas(api: OmApi, db_fqn: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for s in SCHEMAS:
        body = {
            "name": s["name"],
            "description": s["description"],
            "database": db_fqn,
        }
        resp = api.put("/databaseSchemas", body)
        out[s["name"]] = resp["fullyQualifiedName"]
    return out


def _upsert_classifications_and_tags(api: OmApi) -> None:
    for cl in CLASSIFICATIONS:
        api.put("/classifications", {"name": cl["name"], "description": cl["description"]})
        for tag_name, tag_desc in cl["tags"]:
            api.put("/tags", {"classification": cl["name"], "name": tag_name, "description": tag_desc})


def _upsert_glossary(api: OmApi) -> None:
    api.put(
        "/glossaries",
        {
            "name": GLOSSARY_NAME,
            "displayName": "EnergiTech - Glosario de Negocio",
            "description": GLOSSARY_DESCRIPTION,
        },
    )
    for term in GLOSSARY_TERMS:
        api.put(
            "/glossaryTerms",
            {
                "name": term["name"],
                "displayName": term["name"],
                "description": term["description"],
                "glossary": GLOSSARY_NAME,
            },
        )


def _ensure_custom_properties(api: OmApi) -> None:
    table_type = api.get("/metadata/types/name/table", {"fields": "customProperties"})
    string_type = api.get("/metadata/types/name/string")
    table_type_id = str(table_type["id"])
    string_type_id = str(string_type["id"])
    string_type_name = str(string_type["name"])
    existing = {str(cp["name"]) for cp in (table_type.get("customProperties") or []) if isinstance(cp, dict) and cp.get("name")}
    for prop in CUSTOM_PROPERTIES:
        if prop["name"] in existing:
            continue
        body = {
            "name": prop["name"],
            "description": prop["description"],
            "propertyType": {"id": string_type_id, "type": "type", "name": string_type_name},
        }
        api.put(f"/metadata/types/{table_type_id}", body)
        existing.add(prop["name"])


def _upsert_tables(api: OmApi, schemas_fqn: dict[str, str]) -> list[str]:
    fqns: list[str] = []
    for t in TABLES:
        body: dict[str, Any] = {
            "name": t["name"],
            "displayName": t["name"],
            "description": t["description"],
            "databaseSchema": schemas_fqn[t["schema"]],
            "columns": t["columns"],
            "tableType": "Regular",
        }
        if t.get("primary_key"):
            body["tableConstraints"] = [
                {"constraintType": "PRIMARY_KEY", "columns": t["primary_key"]}
            ]
        tags_payload: list[dict[str, str]] = []
        if t.get("tags"):
            tags_payload.extend(
                {"tagFQN": tag, "source": "Classification", "labelType": "Manual", "state": "Confirmed"}
                for tag in t["tags"]
            )
        if t.get("glossary_terms"):
            tags_payload.extend(
                {"tagFQN": term, "source": "Glossary", "labelType": "Manual", "state": "Confirmed"}
                for term in t["glossary_terms"]
            )
        if tags_payload:
            body["tags"] = tags_payload
        if t.get("extension"):
            body["extension"] = t["extension"]
        resp = api.put("/tables", body)
        fqns.append(resp["fullyQualifiedName"])
    return fqns


def _fqn_table(short_name: str) -> str:
    schema, table = short_name.split(".", 1)
    return f"{SERVICE_NAME}.{DATABASE_NAME}.{schema}.{table}"


def _add_lineage(api: OmApi) -> None:
    for src, dst in LINEAGE_EDGES:
        src_fqn = _fqn_table(src)
        dst_fqn = _fqn_table(dst)
        try:
            src_entity = api.get(f"/tables/name/{src_fqn}")
            dst_entity = api.get(f"/tables/name/{dst_fqn}")
        except Exception as exc:
            print(f"  [WARN] no se localiza {src_fqn} o {dst_fqn}: {exc}")
            continue
        body = {
            "edge": {
                "fromEntity": {"id": src_entity["id"], "type": "table"},
                "toEntity": {"id": dst_entity["id"], "type": "table"},
                "lineageDetails": {
                    "description": f"Linaje EnergiTech: {src} -> {dst}",
                    "source": "Manual",
                },
            }
        }
        api.put("/lineage", body)


def insert_all(api: OmApi) -> dict[str, Any]:
    summary: dict[str, Any] = {}

    print("[1/7] Custom properties en tipo 'table'...")
    _ensure_custom_properties(api)

    print("[2/7] Classifications y tags...")
    _upsert_classifications_and_tags(api)

    print("[3/7] Glosario de negocio...")
    _upsert_glossary(api)

    print("[4/7] Database Service...")
    service_fqn = _upsert_database_service(api)
    summary["service"] = service_fqn

    print("[5/7] Database y schemas...")
    db_fqn = _upsert_database(api, service_fqn)
    schemas_fqn = _upsert_schemas(api, db_fqn)
    summary["database"] = db_fqn
    summary["schemas"] = list(schemas_fqn.values())

    print("[6/7] Tablas y columnas...")
    tables_fqn = _upsert_tables(api, schemas_fqn)
    summary["tables"] = tables_fqn

    print("[7/7] Linaje entre tablas...")
    _add_lineage(api)

    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    p.add_argument("--base-url", default=os.environ.get("OM_BASE_URL", OM_DEFAULT_BASE_URL))
    p.add_argument("--token", default=os.environ.get("OM_TOKEN"))
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.token:
        print("ERROR: falta token de OpenMetadata. Pasa --token o exporta OM_TOKEN.", file=sys.stderr)
        return 2
    api = OmApi(base_url=args.base_url, token=args.token)
    summary = insert_all(api)
    print("\n--- RESUMEN ---")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print("\nListo. Abre OpenMetadata y busca el servicio 'energitech-demo'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
