# Oportunext (demo DDD)

Demo académica (UNMSM FISI, Taller de Aplicaciones Sociales): una web que centraliza **voluntariados** y **becas** para peruanos. Consume **2 microservicios** (DDD + SOLID) a través de **Huawei Cloud APIG**. Los backends corren con Docker en una **ECS de Huawei Cloud** y el frontend se despliega en **Vercel**.

> ⚠️ **Aviso:** el frontend incluye el AppCode de APIG en `frontend/config.js`, así que cualquiera que abra la página puede verlo. Esto es aceptable solo para la demo.

## Stack

- **Backend:** Python 3.12, FastAPI y Uvicorn. Datos en memoria.
- **Tests:** pytest y httpx.
- **Frontend:** HTML, CSS y JavaScript vanilla, sin build ni dependencias.
- **Infraestructura:** Docker y docker compose (ECS), Huawei Cloud APIG y Vercel.

## Estructura

```
oportunext-ddd-demo/
├─ frontend/                 # index.html, styles.css, app.js, config.js
├─ backend/
│  ├─ volunteering-service/  # app/{domain,application,infrastructure,api}, tests/, Dockerfile
│  └─ scholarship-service/   # misma estructura
├─ docker/docker-compose.yml
└─ docs/                     # sdd.md (spec), apig-setup.md, solid-ddd.md
```

Detalle de capas y principios en [`docs/solid-ddd.md`](docs/solid-ddd.md).

## Correr los backends

### Con venv y uvicorn

Desde `backend/volunteering-service/` (para `scholarship-service` es igual, con el puerto `8002`):

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8001
```

### Con Docker

Desde la raíz del repositorio:

```bash
docker compose -f docker/docker-compose.yml up -d --build
curl localhost:8001/volunteering
curl localhost:8002/scholarships
```

## Correr los tests

Desde la carpeta de cada servicio, con el venv activo:

```bash
pip install -r requirements-dev.txt
pytest
```

## Probar el frontend en localhost

1. Edita `frontend/config.js` con el dominio del API Group (`API_BASE_URL`) y el `APP_CODE`.
2. Sirve la carpeta:

   ```bash
   python -m http.server 5500 --directory frontend
   ```

3. Abre `http://localhost:5500`.

El frontend llama siempre a APIG, no a los backends directamente: los backends no envían cabeceras CORS (de eso se encarga APIG). Si `config.js` conserva los placeholders, la página muestra un aviso y no hace llamadas.

## Despliegue

1. **ECS:** instalar Docker, copiar el repositorio y ejecutar `docker compose -f docker/docker-compose.yml up -d --build`. Abrir los puertos 8001 y 8002 en el Security Group.
2. **APIG:** crear el API Group, las 4 APIs, el AppCode, el throttling y el CORS siguiendo [`docs/apig-setup.md`](docs/apig-setup.md).
3. **Vercel:** crear un proyecto con **Root Directory = `frontend`**, framework preset **Other**, sin comando de build y sin directorio de salida. Antes, completa `frontend/config.js`.

## Endpoints

| Servicio | Método | Ruta | Respuesta |
|---|---|---|---|
| volunteering-service (`:8001`) | GET | `/volunteering` | `200` lista de voluntariados |
| volunteering-service (`:8001`) | GET | `/volunteering/{id}` | `200` voluntariado · `404` no existe · `422` id no entero |
| volunteering-service (`:8001`) | GET | `/health` | `200` `{"status": "ok"}` |
| scholarship-service (`:8002`) | GET | `/scholarships` | `200` lista de becas |
| scholarship-service (`:8002`) | GET | `/scholarships/{id}` | `200` beca · `404` no existe · `422` id no entero |
| scholarship-service (`:8002`) | GET | `/health` | `200` `{"status": "ok"}` |

Las organizaciones de voluntariado son ficticias. Los datos de becas son ilustrativos: verifícalos en fuentes oficiales antes de usarlos fuera de la demo.

## Decisiones

Supuestos tomados por simplicidad (KISS) donde el spec no era explícito:

- **Ubicación del spec:** se mantiene en `docs/sdd.md` (el spec indicaba la raíz como `SPEC.md`; se decidió no moverlo).
- **`pytest.ini` por servicio:** contiene solo `pythonpath = .` para que `pytest` encuentre el paquete `app` al ejecutarse desde la carpeta del servicio.
- **`requirements-dev.txt`** incluye `-r requirements.txt`, así una sola instalación basta para correr los tests.
- **Test extra:** se agregó un test de `422` para id no entero, porque el contrato HTTP lo especifica.
- **Validación de `id`:** la entidad exige un `int` positivo (no solo `> 0`).
- **Detalle en el frontend:** el título del ítem va como encabezado del `<dialog>` y debajo se listan los demás campos; el `id` no se muestra porque no aporta al usuario.
- **Lista vacía:** si una lista llega vacía, el panel muestra "No hay elementos para mostrar.".
- **Config sin completar:** además del aviso, el botón Recargar queda deshabilitado.
- **Python local:** los tests se corrieron con Python 3.14 en un venv; la imagen Docker usa Python 3.12, como indica el spec.
- **Aviso de httpx:** Starlette advierte que el uso de `httpx` en `TestClient` está deprecado. Se mantuvo `httpx` porque el spec lo exige; el aviso no afecta los tests.
