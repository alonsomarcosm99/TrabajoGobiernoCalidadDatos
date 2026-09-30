"""Script de borrado del caso EnergiTech en OpenMetadata.

Elimina UNICAMENTE las entidades creadas por insertar_energitech.py:

- Database Service     : energitech-demo (cascada a database, schemas, tablas, lineage)
- Classifications      : EnergiTechSensibilidad, EnergiTechCapa, EnergiTechCriticidad
- Glossary             : EnergiTechNegocio (cascada a sus terminos)
- Custom Properties    : no se borran del tipo 'table' (la API de OpenMetadata
                         no soporta borrado parcial sin recrear el tipo). Quedan
                         registradas pero sin valor.

NO toca ninguna entidad fuera de esos prefijos. El TFM del autor convive sin colisiones.

Uso:
    python scripts/borrar_energitech.py --token <JWT_OPENMETADATA>

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
GLOSSARY_NAME = "EnergiTechNegocio"
CLASSIFICATION_NAMES = ["EnergiTechSensibilidad", "EnergiTechCapa", "EnergiTechCriticidad"]


class OmApi:
    def __init__(self, *, base_url: str, token: str, timeout_s: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json"})

    def _request(self, method: str, path: str, *, params: dict | None = None) -> Any:
        if not path.startswith("/"):
            path = "/" + path
        url = f"{self.base_url}{path}"
        r = self.session.request(method, url, params=params, timeout=self.timeout_s)
        if r.status_code == 404:
            return None
        if r.status_code >= 400:
            raise RuntimeError(f"{method} {path} -> {r.status_code}\n{r.text[:2000]}")
        if not r.content:
            return {}
        return r.json()

    def get(self, path: str, params: dict | None = None) -> Any:
        return self._request("GET", path, params=params)

    def delete(self, path: str, params: dict | None = None) -> Any:
        return self._request("DELETE", path, params=params)


def _delete_database_service(api: OmApi) -> bool:
    entity = api.get(f"/services/databaseServices/name/{SERVICE_NAME}")
    if not entity:
        print(f"  [skip] DatabaseService '{SERVICE_NAME}' no existe.")
        return False
    api.delete(f"/services/databaseServices/{entity['id']}", {"recursive": "true", "hardDelete": "true"})
    print(f"  [ok]   DatabaseService '{SERVICE_NAME}' eliminado (cascada).")
    return True


def _delete_glossary(api: OmApi) -> bool:
    entity = api.get(f"/glossaries/name/{GLOSSARY_NAME}")
    if not entity:
        print(f"  [skip] Glossary '{GLOSSARY_NAME}' no existe.")
        return False
    api.delete(f"/glossaries/{entity['id']}", {"recursive": "true", "hardDelete": "true"})
    print(f"  [ok]   Glossary '{GLOSSARY_NAME}' eliminado (cascada).")
    return True


def _delete_classifications(api: OmApi) -> list[str]:
    deleted: list[str] = []
    for name in CLASSIFICATION_NAMES:
        entity = api.get(f"/classifications/name/{name}")
        if not entity:
            print(f"  [skip] Classification '{name}' no existe.")
            continue
        api.delete(f"/classifications/{entity['id']}", {"recursive": "true", "hardDelete": "true"})
        print(f"  [ok]   Classification '{name}' eliminada (cascada).")
        deleted.append(name)
    return deleted


def delete_all(api: OmApi) -> dict[str, Any]:
    print("[1/3] Database Service (energitech-demo)...")
    service_deleted = _delete_database_service(api)

    print("[2/3] Glossary (EnergiTechNegocio)...")
    glossary_deleted = _delete_glossary(api)

    print("[3/3] Classifications (EnergiTech*)...")
    classifications_deleted = _delete_classifications(api)

    return {
        "service_deleted": service_deleted,
        "glossary_deleted": glossary_deleted,
        "classifications_deleted": classifications_deleted,
        "custom_properties_note": "Las custom properties UNE0078proceso, UNE0081caracteristica, stewardEnergiTech y capaMedallion permanecen registradas en el tipo 'table' sin valor para EnergiTech. La API de OpenMetadata no permite eliminarlas sin recrear el tipo.",
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    p.add_argument("--base-url", default=os.environ.get("OM_BASE_URL", OM_DEFAULT_BASE_URL))
    p.add_argument("--token", default=os.environ.get("OM_TOKEN"))
    p.add_argument("--yes", action="store_true", help="No pedir confirmacion interactiva.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.token:
        print("ERROR: falta token de OpenMetadata. Pasa --token o exporta OM_TOKEN.", file=sys.stderr)
        return 2
    if not args.yes:
        print(f"Vas a borrar de {args.base_url}:")
        print(f"  - DatabaseService: {SERVICE_NAME} (cascada)")
        print(f"  - Glossary       : {GLOSSARY_NAME} (cascada)")
        print(f"  - Classifications: {', '.join(CLASSIFICATION_NAMES)}")
        confirm = input("Confirmas? (escribe 'si' para continuar): ").strip().lower()
        if confirm != "si":
            print("Cancelado.")
            return 1
    api = OmApi(base_url=args.base_url, token=args.token)
    summary = delete_all(api)
    print("\n--- RESUMEN ---")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
