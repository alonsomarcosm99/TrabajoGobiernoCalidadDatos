# Scripts auxiliares — Práctica 2 EnergiTech

Automatizan dos tareas principales:

1. **Cargar el caso EnergiTech en OpenMetadata** (`insertar_energitech.py`).
2. **Borrar el caso EnergiTech de OpenMetadata** (`borrar_energitech.py`).

> El OpenMetadata utilizado es el del TFM del autor (`F:\DISCO DURO PORTABLE\INGENIERIA\MASTER\TFM\TFM_Alonso_Marcos_Mu-oz\`). Todas las entidades de EnergiTech viven bajo nombres exclusivos (`energitech-demo`, `EnergiTech*`, `EnergiTechNegocio`) y se borran de forma quirúrgica — el TFM no se ve afectado.

---

## Requisitos

- OpenMetadata corriendo en el cluster Kind del TFM (`tfm-om`).
- `kubectl`, `python` ≥ 3.10, `requests`, `PyJWT`, `cryptography` (ya en `requirements-dev.txt` del TFM).

---

## Flujo recomendado

### 1. Abrir túnel a OpenMetadata

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\port_forward_openmetadata.ps1
```

Deja la ventana abierta. OpenMetadata queda disponible en `http://localhost:8585`.

### 2. Generar el token JWT y exportarlo a la sesión

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\obtener_token_openmetadata.ps1 -SetEnv
```

Esto deja `$env:OM_TOKEN` listo para los dos scripts Python (TTL 8 h por defecto).

> Si se prefiere no propagar el token a `$env`, omitir `-SetEnv` y pasarlo con `--token <jwt>`.

### 3. Cargar el caso EnergiTech

```powershell
python .\scripts\insertar_energitech.py
```

Resultado: en OpenMetadata aparece un **Database Service** llamado `energitech-demo` con:

- Base de datos `energitech`.
- 4 schemas (`crm`, `red`, `silver`, `gold`).
- 6 tablas con columnas, descripciones, restricciones, tags y términos de glosario.
- 3 classifications (`EnergiTechSensibilidad`, `EnergiTechCapa`, `EnergiTechCriticidad`) con sus tags.
- 1 glosario de negocio (`EnergiTechNegocio`) con 19 términos.
- 4 custom properties añadidas al tipo `table` (`UNE0078proceso`, `UNE0081caracteristica`, `stewardEnergiTech`, `capaMedallion`).
- 5 aristas de lineage entre las tablas del flujo.

### 4. Hacer las capturas de pantalla

Guardar las evidencias de OpenMetadata en `entregable/imágenes/openmetadata/`. Las capturas usadas por la memoria ya están incrustadas en los proyectos y anexos correspondientes.

### 5. (Opcional) Limpiar OpenMetadata

```powershell
python .\scripts\borrar_energitech.py
```

Pedirá confirmación interactiva (responder `si`). Pasar `--yes` para automatizarlo.

---

## Aislamiento del TFM

| Recurso | Nombre en EnergiTech | Riesgo de colisión con TFM |
|---|---|---|
| DatabaseService | `energitech-demo` | Ninguno (TFM usa `opendata_postgres_a/b`). |
| Database | `energitech` | Ninguno (TFM usa `opendata_demo`). |
| Glossary | `EnergiTechNegocio` | Ninguno. |
| Classifications | `EnergiTech*` | Ninguno (TFM usa `dcat_theme`). |
| Custom properties | `UNE0078*`, `UNE0081*`, `stewardEnergiTech`, `capaMedallion` | Compartirían el tipo `table`, pero no chocan en nombre con las del TFM (`dcat_publisher_name`, `dcat_hvd_category`, `dcat_access_url`). |

El script de borrado solo elimina por nombre exacto; nunca toca clasificaciones, glosarios ni servicios fuera del prefijo `EnergiTech*` / `energitech-demo`.

---

## Variables de entorno

| Variable | Default | Uso |
|---|---|---|
| `OM_BASE_URL` | `http://localhost:8585/api/v1` | Base de la API REST de OpenMetadata. |
| `OM_TOKEN` | — | JWT con TTL 8 h generado por `obtener_token_openmetadata.ps1`. |
