# SPEC — oportunext-ddd-demo

> Demo académica (UNMSM FISI · Taller de Aplicaciones Sociales): plataforma para centralizar **voluntariados** y **becas** para peruanos, con **2 microservicios (DDD + SOLID)** detrás de **Huawei Cloud APIG**, desplegados con Docker en una **ECS de Huawei Cloud**, y un frontend **vanilla JS** desplegado en **Vercel**.
>
> Metodología: Spec Driven Development. Este documento es la fuente de verdad. El código se deriva de él.

---

## 0. Instrucciones para Claude Code

1. Lee este documento completo antes de escribir código.
2. Implementa siguiendo el orden de la **sección 9 (Tareas)**. Al terminar cada tarea, marca su casilla `[x]` en este archivo (es lo único que puedes editar de este archivo).
3. **No uses comandos git** (`git init`, `add`, `commit`, `push`, etc.). El control de versiones lo hace el humano. Sí puedes crear un archivo `.gitignore`.
4. No inventes requisitos. Si algo es ambiguo, elige la opción **más simple** (KISS) y anótala en la sección "Decisiones" del `README.md`.
5. No escribas secretos ni valores reales de despliegue. Usa los placeholders de la sección 11.
6. Ejecuta los tests de cada servicio (`pytest`) cuando existan. Si Docker está disponible en tu entorno, valida también el `docker compose`. Si no lo está, indícalo en tu resumen final.

---

## 1. Contexto y alcance

**Problema:** las oportunidades de voluntariado y becas para peruanos están dispersas.
**Objetivo de la demo:** mostrar una web que consume **2 APIs** (una por microservicio) a través de un **API Gateway**, con una implementación limpia (SOLID/DDD) y simple.

### Dentro del alcance
- 2 microservicios de **solo lectura**: listar y detalle por id.
- Datos **en memoria** con datos semilla.
- Frontend con **pestañas** `Voluntariados | Becas`, desktop first, adaptable a mobile.
- Docker + docker-compose para los backends.
- Documentación: `README.md`, `docs/apig-setup.md`, `docs/solid-ddd.md`.

### Fuera del alcance (NO implementar)
- CRUD, filtros, búsqueda, paginación, login/registro, perfiles, matching/LLM, notificaciones.
- Base de datos, ORM, migraciones, broker de eventos.
- Diagrama de arquitectura (lo hace el humano por separado).
- Autenticación o CORS dentro de los backends (los resuelve APIG).
- Frameworks de frontend, bundlers, npm, TypeScript.
- Contenedor del frontend (se despliega en Vercel).

---

## 2. Principios y restricciones

| # | Regla |
|---|---|
| P1 | **KISS**: lo mínimo que cumple el requisito. Sin abstracciones "por si acaso". |
| P2 | **SOLID** y **DDD** visibles en el backend (ver sección 5). Es parte de lo que se evalúa. |
| P3 | Backend: **Python 3.12 + FastAPI**. Dependencias de runtime: solo `fastapi` y `uvicorn`. |
| P4 | Frontend: **HTML + CSS + JS vanilla**, sin build, sin dependencias. |
| P5 | Identificadores y comentarios de código en **inglés**. Textos de UI y documentación en **español**. |
| P6 | **No** agregar `CORSMiddleware` ni ninguna política de auth en los backends. CORS lo aplica APIG (evita cabeceras duplicadas). |
| P7 | Sin comandos git. |

---

## 3. Estructura del repositorio

```
oportunext-ddd-demo/
├─ frontend/
│  ├─ index.html
│  ├─ styles.css
│  ├─ app.js
│  └─ config.js
├─ backend/
│  ├─ volunteering-service/
│  │  ├─ app/
│  │  │  ├─ __init__.py
│  │  │  ├─ main.py                      # composition root
│  │  │  ├─ domain/
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ entities.py               # Volunteering, Modality
│  │  │  │  ├─ repositories.py           # VolunteeringRepository (port)
│  │  │  │  └─ errors.py                 # DomainError, InvalidVolunteeringError, VolunteeringNotFoundError
│  │  │  ├─ application/
│  │  │  │  ├─ __init__.py
│  │  │  │  └─ use_cases.py              # ListVolunteering, GetVolunteering
│  │  │  ├─ infrastructure/
│  │  │  │  ├─ __init__.py
│  │  │  │  └─ in_memory_repository.py   # adapter + seed data
│  │  │  └─ api/
│  │  │     ├─ __init__.py
│  │  │     ├─ routes.py                 # build_router(use cases)
│  │  │     └─ schemas.py                # Pydantic response model
│  │  ├─ tests/
│  │  │  ├─ test_entities.py
│  │  │  ├─ test_use_cases.py
│  │  │  └─ test_api.py
│  │  ├─ Dockerfile
│  │  ├─ requirements.txt
│  │  └─ requirements-dev.txt
│  └─ scholarship-service/               # misma estructura (Scholarship, Level, ScholarshipRepository, ...)
├─ docker/
│  └─ docker-compose.yml
├─ docs/
│  ├─ apig-setup.md
│  └─ solid-ddd.md
├─ .gitignore
└─ README.md
```

Este `SPEC.md` va en la raíz del repo.

---

## 4. Requisitos

### 4.1 Funcionales

| ID | Requisito | Criterio de aceptación |
|---|---|---|
| RF-01 | `volunteering-service` lista voluntariados. | `GET /volunteering` → `200` con arreglo JSON de 4 elementos (ver 5.4). |
| RF-02 | `volunteering-service` devuelve el detalle por id. | `GET /volunteering/1` → `200` con el objeto. `GET /volunteering/999` → `404` con `{"detail": "..."}`. |
| RF-03 | `scholarship-service` lista becas. | `GET /scholarships` → `200` con arreglo JSON de 4 elementos. |
| RF-04 | `scholarship-service` devuelve el detalle por id. | `GET /scholarships/1` → `200`. `GET /scholarships/999` → `404`. |
| RF-05 | Cada servicio expone salud. | `GET /health` → `200` `{"status": "ok"}`. |
| RF-06 | La web muestra ambas listas en pestañas separadas. | Al abrir la página se hacen **ambas** llamadas en paralelo; cada pestaña muestra solo su lista. |
| RF-07 | La web muestra el detalle de un ítem. | Clic en una tarjeta → llamada `GET /{recurso}/{id}` → detalle en un `<dialog>`. |
| RF-08 | La web muestra errores simples. | Ante 401/403/404/429/red/otro, se muestra un mensaje de texto claro en la pestaña (o en el diálogo de detalle). |
| RF-09 | La web es responsive. | Correcta en 1280 px y en 375 px (ver 6.5). |

### 4.2 No funcionales

| ID | Requisito |
|---|---|
| RNF-01 | Cada servicio levanta con `docker compose up` sin configuración adicional. |
| RNF-02 | Mapeo único de puertos: contenedor `8000`; host `8001` (volunteering) y `8002` (scholarship). |
| RNF-03 | El frontend no usa `innerHTML` con datos de la API (evitar XSS): construir nodos con `createElement` y `textContent`. |
| RNF-04 | Cobertura de tests mínima: invariantes de entidad, casos de uso con repositorio falso y endpoints (200 y 404). |

---

## 5. Diseño del backend

### 5.1 Capas y dependencias (regla de dependencia)

```
api ──▶ application ──▶ domain ◀── infrastructure
```

- `domain`: sin imports de FastAPI, Pydantic ni de otras capas. Python puro.
- `application`: solo depende de `domain`.
- `infrastructure`: implementa los puertos de `domain`.
- `api`: traduce HTTP ↔ casos de uso. Es la única capa que conoce FastAPI/Pydantic.
- `main.py` es el **composition root**: crea el repositorio, los casos de uso y el router, y los conecta. No usar `Depends` para esto.

### 5.2 Domain (`volunteering-service`)

```python
# entities.py
class Modality(str, Enum):
    IN_PERSON = "in_person"
    REMOTE = "remote"

@dataclass(frozen=True)
class Volunteering:
    id: int
    title: str
    organization: str
    modality: Modality
    location: str
    description: str
    # __post_init__: id > 0; title, organization, location no vacíos (tras strip);
    # modality es instancia de Modality. Si no, raise InvalidVolunteeringError.
```

```python
# repositories.py
class VolunteeringRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[Volunteering]: ...
    @abstractmethod
    def get_by_id(self, volunteering_id: int) -> Volunteering | None: ...
```

```python
# errors.py
class DomainError(Exception): ...
class InvalidVolunteeringError(DomainError): ...
class VolunteeringNotFoundError(DomainError): ...
```

### 5.3 Application

```python
class ListVolunteering:
    def __init__(self, repository: VolunteeringRepository): ...
    def execute(self) -> list[Volunteering]: ...

class GetVolunteering:
    def __init__(self, repository: VolunteeringRepository): ...
    def execute(self, volunteering_id: int) -> Volunteering:
        # si el repositorio devuelve None -> raise VolunteeringNotFoundError
```

Un caso de uso = una clase = una responsabilidad.

### 5.4 Contratos HTTP

**volunteering-service**

| Método | Ruta | Respuesta |
|---|---|---|
| GET | `/volunteering` | `200` `[Volunteering, ...]` |
| GET | `/volunteering/{id}` | `200` `Volunteering` · `404` `{"detail": "Volunteering 999 not found"}` · `422` si `id` no es entero |
| GET | `/health` | `200` `{"status": "ok"}` |

Objeto `Volunteering` (claves en inglés, `snake_case`; `modality` serializa su valor del enum):

```json
{
  "id": 1,
  "title": "Reforestación en Lurín",
  "organization": "Eco Perú",
  "modality": "in_person",
  "location": "Lima",
  "description": "..."
}
```

**scholarship-service**

| Método | Ruta | Respuesta |
|---|---|---|
| GET | `/scholarships` | `200` `[Scholarship, ...]` |
| GET | `/scholarships/{id}` | `200` · `404` `{"detail": "Scholarship 999 not found"}` |
| GET | `/health` | `200` `{"status": "ok"}` |

```json
{
  "id": 1,
  "name": "Beca 18",
  "institution": "PRONABEC",
  "level": "undergraduate",
  "country": "Perú",
  "description": "..."
}
```

Entidad `Scholarship`: `id`, `name`, `institution`, `level: Level`, `country`, `description`. `Level`: `UNDERGRADUATE = "undergraduate"`, `POSTGRADUATE = "postgraduate"`. Mismas invariantes que Volunteering (id > 0, textos no vacíos, `level` válido). Errores: `InvalidScholarshipError`, `ScholarshipNotFoundError`.

### 5.5 Capa API

- `schemas.py`: modelo Pydantic de respuesta (`VolunteeringResponse` / `ScholarshipResponse`) y una función `to_response(entity)`. Las entidades de dominio **no** se exponen directamente.
- `routes.py`: `build_router(list_uc, get_uc) -> APIRouter`. Usa `response_model`.
- `main.py`: crea `FastAPI(title="Volunteering Service")`, registra el router, `/health`, y un `exception_handler` que convierte `VolunteeringNotFoundError` en `404` con `{"detail": str(error)}`.

### 5.6 Infrastructure y datos semilla

`InMemoryVolunteeringRepository` guarda los datos en un `dict[int, Volunteering]` cargado en el constructor con la semilla. Devuelve la lista ordenada por `id`.

> Las organizaciones de voluntariado son ficticias. Los datos de becas son ilustrativos; verificar en fuentes oficiales antes de usarlos fuera de la demo.

**Voluntariados**

| id | title | organization | modality | location | description |
|---|---|---|---|---|---|
| 1 | Reforestación en Lurín | Eco Perú | in_person | Lima | Jornada de siembra de árboles nativos en la zona de lomas. Incluye una charla de capacitación al inicio. |
| 2 | Mentoría escolar en línea | Educa Más | remote | Remoto | Acompañamiento semanal a estudiantes de secundaria en matemática y comprensión lectora. |
| 3 | Apoyo en comedor popular | Manos Unidas | in_person | Cusco | Preparación y reparto de raciones en un comedor popular del distrito. |
| 4 | Limpieza de playas | Mar Limpio | in_person | Lima | Campaña de recolección de residuos y educación ambiental para vecinos. |

**Becas**

| id | name | institution | level | country | description |
|---|---|---|---|---|---|
| 1 | Beca 18 | PRONABEC | undergraduate | Perú | Beca integral para estudios de pregrado dirigida a jóvenes con alto rendimiento y bajos recursos económicos. |
| 2 | Beca Generación del Bicentenario | PRONABEC | postgraduate | Extranjero | Beca para estudios de posgrado en universidades del extranjero. |
| 3 | Chevening | Gobierno del Reino Unido | postgraduate | Reino Unido | Beca para estudios de maestría de un año en universidades del Reino Unido. |
| 4 | Fulbright | Comisión Fulbright | postgraduate | Estados Unidos | Beca para estudios de posgrado en universidades de Estados Unidos. |

### 5.7 Tests (pytest)

`requirements-dev.txt`: `pytest`, `httpx` (requerido por `fastapi.testclient`).

- `test_entities.py`: entidad válida se crea; `id <= 0`, texto vacío y enum inválido lanzan `Invalid*Error`.
- `test_use_cases.py`: usando un **repositorio falso** (clase que implementa el puerto): lista devuelve lo del repo; `get` devuelve la entidad; `get` de id inexistente lanza `*NotFoundError`. Esto demuestra Liskov y Dependency Inversion.
- `test_api.py`: con `TestClient(app)`: `GET` lista → 200 y 4 elementos; detalle → 200; detalle inexistente → 404; `/health` → 200.

Ejecución desde `backend/<service>/`: `pip install -r requirements-dev.txt && pytest`.

---

## 6. Diseño del frontend

### 6.1 Configuración (`frontend/config.js`)

```js
// Demo only: the AppCode is visible to anyone who opens the page.
window.APP_CONFIG = {
  API_BASE_URL: "https://<APIG-GROUP-DOMAIN>", // sin "/" final
  APP_CODE: "<APPCODE>"
};
```

Si `API_BASE_URL` o `APP_CODE` conservan el valor placeholder (contienen `<`), la UI muestra: *"Configura frontend/config.js con el dominio de APIG y el AppCode."* y no hace llamadas.

### 6.2 Llamadas a la API

- Todas las llamadas van a `API_BASE_URL + ruta` con la cabecera `X-Apig-AppCode: <APP_CODE>`.
- Rutas: `/volunteering`, `/volunteering/{id}`, `/scholarships`, `/scholarships/{id}`.
- `apiGet(path)` lanza un `ApiError` con `status` si `!response.ok`; los fallos de red se tratan como `status = 0`.

### 6.3 Comportamiento

1. **Carga inicial:** al cargar, se disparan **las dos listas en paralelo** (`Promise.allSettled`). Cada pestaña tiene su propio estado independiente: *cargando → ok / error*.
2. **Pestañas:** `Voluntariados` (activa por defecto) y `Becas`. Solo se muestra el panel activo. Accesibilidad: `role="tablist"`, `role="tab"`, `role="tabpanel"`, `aria-selected`, `aria-controls`; navegación con clic y con flechas izquierda/derecha.
3. **Tarjetas:** cada ítem es un `<button class="card">` con título, entidad (organización / institución) y una etiqueta (modalidad / nivel). Mapeo de etiquetas: `in_person` → *Presencial*, `remote` → *Virtual*, `undergraduate` → *Pregrado*, `postgraduate` → *Posgrado*.
4. **Detalle:** clic en tarjeta → `GET /{recurso}/{id}` → se abre un `<dialog>` (`showModal()`) con todos los campos y un botón *Cerrar*. Mientras carga: *"Cargando…"*. Si falla: mensaje de error dentro del diálogo.
5. **Recargar:** un botón *Recargar* en el encabezado vuelve a pedir ambas listas.
6. **Errores (texto simple, en un `<p role="alert">` por panel):**

| Situación | Mensaje |
|---|---|
| `401` / `403` | `No autorizado. Revisa el AppCode.` |
| `404` | `No se encontró el recurso.` |
| `429` | `Demasiadas solicitudes. Intenta de nuevo en un minuto.` |
| `0` (red/CORS) | `No se pudo conectar con el servidor.` |
| otro | `Error inesperado (HTTP <status>).` |

### 6.4 Archivos

- `index.html`: `<meta name="viewport" content="width=device-width, initial-scale=1">`, encabezado (título "Oportunext", subtítulo "Voluntariados y becas para peruanos", botón Recargar), tablist, dos tabpanels, un `<dialog>`. Carga `config.js` y luego `app.js` con `defer`.
- `styles.css`: sin librerías ni fuentes externas (fuente del sistema).
- `app.js`: un solo archivo, script clásico (sin módulos), funciones pequeñas: `apiGet`, `errorMessage`, `renderCards`, `loadList`, `openDetail`, `setupTabs`. Todo el DOM con `createElement` y `textContent`.

### 6.5 Responsive (desktop first)

- **Base (desktop ≥ 769 px):** contenedor de `max-width: 1000px` centrado; tarjetas en grilla de 2–3 columnas (`repeat(auto-fill, minmax(280px, 1fr))`); `<dialog>` de ancho máx. 560 px centrado.
- **Mobile (`@media (max-width: 768px)`):** tarjetas en 1 columna; pestañas ocupan 50 % cada una; padding reducido; botón Recargar a ancho completo; `<dialog>` casi a pantalla completa.
- Objetivos táctiles ≥ 44 px de alto; contraste legible; sin scroll horizontal a 375 px.

---

## 7. Docker y despliegue

### 7.1 Dockerfile (idéntico por servicio, ajustando solo el nombre de la carpeta)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`requirements.txt`: `fastapi` y `uvicorn` (sin versiones fijas innecesarias; si fijas, que sean compatibles con Python 3.12).

### 7.2 `docker/docker-compose.yml`

```yaml
services:
  volunteering-service:
    build: ../backend/volunteering-service
    container_name: volunteering-service
    ports: ["8001:8000"]
    restart: unless-stopped
  scholarship-service:
    build: ../backend/scholarship-service
    container_name: scholarship-service
    ports: ["8002:8000"]
    restart: unless-stopped
```

Ejecución desde la raíz: `docker compose -f docker/docker-compose.yml up -d --build`.

### 7.3 Frontend en Vercel

- Proyecto de Vercel con **Root Directory = `frontend`**, framework preset **Other**, sin comando de build, sin directorio de salida. No crear `vercel.json`.
- Pruebas locales: `python -m http.server 5500 --directory frontend` y abrir `http://localhost:5500`.

---

## 8. Documentación a generar

### 8.1 `README.md`
Secciones: descripción breve · stack · estructura · cómo correr los backends (venv + uvicorn, y Docker) · cómo correr los tests · cómo probar el frontend en localhost · despliegue (ECS con Docker, APIG según `docs/apig-setup.md`, Vercel) · tabla de endpoints · **Decisiones** (supuestos tomados por KISS) · aviso de que la demo expone el AppCode en el frontend.

### 8.2 `docs/apig-setup.md`
Guía para el humano (Claude Code **no** puede ejecutarla; solo la documenta):

1. **ECS:** instalar Docker, copiar el repo, `docker compose -f docker/docker-compose.yml up -d --build`. Abrir en el Security Group los puertos TCP 8001 y 8002 (demo: `0.0.0.0/0`; ideal: solo las IPs del gateway). Probar `curl http://<ECS_EIP>:8001/volunteering` y `:8002/scholarships`.
2. **APIG:** crear un API Group y registrar **4 APIs** (método GET, tipo de backend HTTP, sin canal VPC):

| API pública | Backend |
|---|---|
| `/volunteering` | `http://<ECS_EIP>:8001/volunteering` |
| `/volunteering/{id}` | `http://<ECS_EIP>:8001/volunteering/{id}` |
| `/scholarships` | `http://<ECS_EIP>:8002/scholarships` |
| `/scholarships/{id}` | `http://<ECS_EIP>:8002/scholarships/{id}` |

Publicarlas en el entorno **RELEASE**.

3. **Característica 1 — Autenticación:** seguridad de las APIs = App con AppCode; crear la App, generar el AppCode y asociarlo a las 4 APIs. Cabecera: `X-Apig-AppCode`.
4. **Característica 2 — Throttling:** política de límite de tráfico (valor de demo: 5 llamadas/min por API) vinculada a las 4 APIs. Cada "Recargar" consume 1 llamada por lista.
5. **Característica 3 — CORS:** plugin CORS vinculado a las APIs, con orígenes permitidos = dominio de Vercel y `http://localhost:5500` (o `*` solo en la demo) y cabeceras permitidas `X-Apig-AppCode, Content-Type`. Para el preflight, crear las APIs `OPTIONS` necesarias con autenticación `None` y vincular el plugin. **Verificar en la documentación de Huawei APIG** según el tipo de gateway/versión.
6. **Pruebas con curl:** sin AppCode → `401`; con AppCode → `200`; superar el límite → `429`.
7. **Notas:** el gateway compartido tiene límite diario en su dominio de depuración; APIG→ECS va por HTTP sin cifrar (aceptable en demo; en producción usar canal VPC y HTTPS); el AppCode en el frontend es solo para demo.

### 8.3 `docs/solid-ddd.md`
Sustentación (la tarea la exige). Para cada principio SOLID, 1–2 líneas con el archivo y clase concretos del repo donde se evidencia; para DDD: bounded contexts (un servicio por contexto), entidades con invariantes, repositorio como puerto/adaptador, casos de uso en `application`, errores de dominio mapeados a HTTP en `api`, composition root en `main.py`. Incluir una sección corta "Cómo cambiar a PostgreSQL sin tocar dominio ni casos de uso". **No incluir diagramas.**

---

## 9. Tareas (ejecutar en orden)

- [x] **T01 — Scaffolding:** crear la estructura de carpetas de la sección 3, `__init__.py` en cada paquete Python y `.gitignore` (`__pycache__/`, `.venv/`, `.pytest_cache/`, `.env`, `.vercel/`, `.DS_Store`).
- [x] **T02 — volunteering-service / domain:** `entities.py`, `repositories.py`, `errors.py` según 5.2. Python puro.
- [x] **T03 — volunteering-service / application + infrastructure:** `use_cases.py` (5.3) e `in_memory_repository.py` con la semilla (5.6).
- [x] **T04 — volunteering-service / api + main:** `schemas.py`, `routes.py`, `main.py` (5.5), `requirements.txt`, `requirements-dev.txt`.
- [x] **T05 — volunteering-service / tests:** los 3 archivos de 5.7; `pytest` en verde.
- [x] **T06 — scholarship-service:** repetir T02–T05 con `Scholarship`, `Level`, `ScholarshipRepository`, `ListScholarships`, `GetScholarship` y la semilla de becas. Rutas `/scholarships` y `/scholarships/{id}`.
- [x] **T07 — Docker:** `Dockerfile` por servicio y `docker/docker-compose.yml` (7.1, 7.2).
- [x] **T08 — frontend / base:** `index.html`, `styles.css` (desktop first + media query mobile) y `config.js` con placeholders.
- [x] **T09 — frontend / lógica:** `app.js` según 6.2–6.3 (carga paralela, pestañas, tarjetas, detalle en `<dialog>`, errores, Recargar).
- [x] **T10 — docs:** `docs/apig-setup.md` y `docs/solid-ddd.md` según 8.2 y 8.3.
- [x] **T11 — README:** `README.md` según 8.1.
- [x] **T12 — Verificación:** recorrer la sección 10 y reportar el resultado.

---

## 10. Verificación y Definition of Done

### 10.1 Backend
- [ ] `pytest` en verde en ambos servicios.
- [ ] `uvicorn app.main:app --port 8001` (y 8002) responde a los `curl` de RF-01 a RF-05.
- [ ] Ningún archivo de `domain/` importa `fastapi`, `pydantic` ni otras capas (revisar con búsqueda de texto).
- [ ] No existe `CORSMiddleware` en ningún backend.

### 10.2 Docker (si Docker está disponible)
- [ ] `docker compose -f docker/docker-compose.yml up -d --build` levanta ambos contenedores.
- [ ] `curl localhost:8001/volunteering` y `curl localhost:8002/scholarships` devuelven 4 elementos.

### 10.3 Frontend (con `config.js` apuntando a APIG real, lo prueba el humano)
- [ ] Al abrir la página se ven ambas llamadas en la pestaña Network.
- [ ] Las pestañas alternan sin recargar; cada una muestra solo su lista.
- [ ] Clic en tarjeta abre el detalle (llamada por id).
- [ ] Sin AppCode correcto se ve "No autorizado. Revisa el AppCode."; tras superar el throttling se ve el mensaje de 429.
- [ ] A 1280 px: grilla de varias columnas. A 375 px: 1 columna, sin scroll horizontal.
- [ ] Con placeholders en `config.js` se ve el aviso de configuración y no se hacen llamadas.

### 10.4 Entregable
- [ ] Todas las casillas de la sección 9 marcadas.
- [ ] El resumen final de Claude Code lista: qué hizo, qué verificó, qué **no** pudo verificar (p. ej. Docker o APIG) y las decisiones tomadas.

---

## 11. Valores pendientes (los completa el humano, no Claude Code)

| Placeholder | Dónde se usa |
|---|---|
| `<APIG-GROUP-DOMAIN>` | `frontend/config.js` |
| `<APPCODE>` | `frontend/config.js` |
| `<ECS_EIP>` | Backend de las APIs en APIG (consola), pruebas con curl |
| Dominio de Vercel | Orígenes permitidos en el plugin CORS de APIG |
