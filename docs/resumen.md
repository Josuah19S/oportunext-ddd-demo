# Oportunext: resumen para la presentación

Demo académica (UNMSM FISI, Taller de Aplicaciones Sociales).

## 1. Problema y propuesta

Las oportunidades de **voluntariado** y **becas** para peruanos están dispersas en muchas fuentes. Oportunext las reúne en una sola web con dos pestañas: *Voluntariados* y *Becas*.

La demo muestra tres cosas:

1. Una web que consume **2 APIs**, una por microservicio.
2. Un **API Gateway** (Huawei Cloud APIG) que protege y controla esas APIs.
3. Un backend con **DDD y SOLID**, simple y fácil de extender.

## 2. Arquitectura

### Componentes

| Componente | Tecnología | Dónde corre | Responsabilidad |
|---|---|---|---|
| Frontend | HTML, CSS y JavaScript vanilla (sin dependencias) | Vercel | Muestra las pestañas, las tarjetas y el detalle; llama a APIG con el AppCode |
| API Gateway | Huawei Cloud APIG (gateway dedicado) | Huawei Cloud, en la misma VPC que la ECS | Punto único de entrada: autenticación, throttling y CORS |
| volunteering-service | Python 3.12 + FastAPI | Contenedor Docker en la ECS, puerto 8001 | API de voluntariados |
| scholarship-service | Python 3.12 + FastAPI | Contenedor Docker en la ECS, puerto 8002 | API de becas |
| ECS | Ubuntu + Docker Compose | Huawei Cloud | Hospeda los dos contenedores |

### Recorrido de una petición

1. El usuario abre la web en Vercel. El navegador descarga los archivos estáticos.
2. `app.js` pide **en paralelo** `GET /volunteering` y `GET /scholarships` al dominio del API Group, con la cabecera `X-Apig-AppCode`.
3. APIG responde el *preflight* CORS, valida el AppCode y aplica el límite de tráfico.
4. Si todo es válido, APIG reenvía la petición por la red privada de la VPC a la IP privada de la ECS, al puerto 8001 u 8002.
5. FastAPI ejecuta el caso de uso, que lee del repositorio en memoria, y devuelve JSON.
6. APIG agrega las cabeceras CORS y devuelve la respuesta al navegador, que dibuja las tarjetas.
7. Al hacer clic en una tarjeta se repite el ciclo con `GET /{recurso}/{id}` y el detalle se muestra en un `<dialog>`.

### Decisiones de arquitectura

- **Un microservicio por contexto de negocio.** Voluntariados y becas evolucionan por separado y no comparten código ni datos.
- **El gateway concentra las políticas transversales.** Los backends no implementan autenticación ni CORS: así no hay lógica duplicada ni cabeceras CORS repetidas.
- **Backend solo accesible dentro de la VPC.** Como el gateway dedicado y la ECS están en la misma VPC, APIG llega por IP privada. Los puertos 8001/8002 solo aceptan tráfico desde la subred del gateway y no quedan expuestos a internet.
- **Frontend estático en Vercel.** No necesita servidor ni contenedor: son tres archivos y una configuración.
- **Configuración por variables de entorno.** El dominio de APIG y el AppCode se definen como variables de entorno en Vercel. En cada despliegue, `build-config.sh` genera `config.js` con esos valores, y `config.js` está excluido de git. Así los valores reales no quedan en el repositorio.
- **Datos en memoria.** Es suficiente para la demo; la sección 4 explica cómo cambiar a una base de datos sin tocar el dominio.

## 3. Características de APIG

| Característica | Configuración | Qué demuestra |
|---|---|---|
| Autenticación | Las 4 APIs requieren una App con AppCode (cabecera `X-Apig-AppCode`) | Sin AppCode válido responde `401`, y la web muestra "No autorizado. Revisa el AppCode." |
| Throttling | Política de 5 llamadas por minuto por API | Al superar el límite responde `429`, y la web muestra "Demasiadas solicitudes. Intenta de nuevo en un minuto." |
| CORS | Plugin CORS con el dominio de Vercel y `http://localhost:5500` como orígenes permitidos | El navegador puede llamar al gateway desde otro dominio |

APIs publicadas en el entorno **RELEASE**:

| API pública | Servicio |
|---|---|
| `GET /volunteering` | volunteering-service |
| `GET /volunteering/{id}` | volunteering-service |
| `GET /scholarships` | scholarship-service |
| `GET /scholarships/{id}` | scholarship-service |

## 4. Backend: cómo se aplicaron DDD y SOLID

Los ejemplos usan `volunteering-service`. `scholarship-service` es idéntico en estructura, con `Scholarship`, `Level`, `ScholarshipRepository`, `ListScholarships` y `GetScholarship`.

### 4.1 Estructura en capas

Cada microservicio se organiza en cuatro capas, y las dependencias siempre apuntan hacia el dominio:

`api → application → domain ← infrastructure`

| Capa | Carpeta | Contenido | Puede depender de |
|---|---|---|---|
| Dominio | `app/domain/` | Entidad, enum, puerto del repositorio y errores de dominio | Nada (Python puro) |
| Aplicación | `app/application/` | Casos de uso | Solo `domain` |
| Infraestructura | `app/infrastructure/` | Repositorio en memoria con los datos semilla | `domain` (implementa su puerto) |
| API | `app/api/` | Esquemas Pydantic y rutas FastAPI | `application` y `domain` |
| Composition root | `app/main.py` | Crea y conecta todas las piezas | Todas |

La consecuencia práctica es que el dominio, el corazón del negocio, no sabe que existen FastAPI, Pydantic, HTTP ni el lugar donde se guardan los datos. Se puede probar y cambiar sin tocar nada de eso. Se comprobó con una búsqueda de texto: ningún archivo de `domain/` importa esas librerías.

### 4.2 DDD: cómo se plasmó

**1. Bounded contexts → un microservicio por contexto.**
"Voluntariado" y "Beca" son conceptos de negocio distintos, con reglas, datos y ritmo de cambio propios. Cada uno vive en su propio servicio (`volunteering-service`, `scholarship-service`), con su propio modelo, y no comparten código ni datos. Un cambio en becas no puede romper voluntariados.

**2. Lenguaje ubicuo.**
Las clases y métodos usan los términos del negocio: `Volunteering`, `Scholarship`, `Modality.IN_PERSON`, `Level.POSTGRADUATE`, `ListVolunteering`, `GetScholarship`. Leer el código es leer el dominio.

**3. Entidades con invariantes (modelo rico, no anémico).**
La entidad es inmutable (`frozen=True`) y se valida a sí misma al crearse. Si una regla no se cumple, lanza un error de dominio, así que **no puede existir una entidad inválida** en el sistema:

```python
# app/domain/entities.py
@dataclass(frozen=True)
class Volunteering:
    id: int
    title: str
    organization: str
    modality: Modality
    location: str
    description: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, int) or self.id <= 0:
            raise InvalidVolunteeringError("id must be a positive integer")
        # title, organization y location no vacíos; modality debe ser un Modality
```

**4. Valores acotados del dominio.**
`Modality` (`in_person`, `remote`) y `Level` (`undergraduate`, `postgraduate`) son enums: el dominio declara explícitamente cuáles son los valores válidos, en vez de aceptar cualquier texto.

**5. Repositorio como puerto (dominio) y adaptador (infraestructura).**
El dominio define *qué* necesita, sin decir *cómo* se obtiene:

```python
# app/domain/repositories.py  (puerto)
class VolunteeringRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[Volunteering]: ...
    @abstractmethod
    def get_by_id(self, volunteering_id: int) -> Volunteering | None: ...
```

`InMemoryVolunteeringRepository` (`app/infrastructure/in_memory_repository.py`) es el adaptador que lo implementa con un diccionario en memoria. Es el patrón de **puertos y adaptadores** (arquitectura hexagonal).

**6. Casos de uso en la capa de aplicación.**
Cada acción del sistema es una clase con un método `execute`. El caso de uso coordina el dominio y aplica la regla "si no existe, es un error de negocio":

```python
# app/application/use_cases.py
class GetVolunteering:
    def __init__(self, repository: VolunteeringRepository):
        self._repository = repository

    def execute(self, volunteering_id: int) -> Volunteering:
        volunteering = self._repository.get_by_id(volunteering_id)
        if volunteering is None:
            raise VolunteeringNotFoundError(f"Volunteering {volunteering_id} not found")
        return volunteering
```

**7. Errores de dominio traducidos a HTTP en el borde.**
El dominio lanza `VolunteeringNotFoundError` sin saber nada de HTTP. Solo `main.py` lo traduce a un `404`:

```python
# app/main.py
@app.exception_handler(VolunteeringNotFoundError)
def handle_not_found(request, error):
    return JSONResponse(status_code=404, content={"detail": str(error)})
```

**8. El dominio no se expone directamente.**
La API responde con `VolunteeringResponse` (`app/api/schemas.py`), un modelo Pydantic que se construye con `to_response(entity)`. Si mañana cambia la entidad, el contrato HTTP puede mantenerse.

**9. Composition root.**
`main.py` es el único lugar donde se eligen las implementaciones concretas y se conectan a mano, sin magia:

```python
# app/main.py
repository = InMemoryVolunteeringRepository()
list_volunteering = ListVolunteering(repository)
get_volunteering = GetVolunteering(repository)
app.include_router(build_router(list_volunteering, get_volunteering))
```

### 4.3 SOLID: cómo se plasmó

| Principio | Qué dice | Dónde se ve en el código |
|---|---|---|
| **S**: Single Responsibility | Cada clase tiene un solo motivo para cambiar | `ListVolunteering` solo lista y `GetVolunteering` solo obtiene uno (dos clases, no una con dos métodos). `InMemoryVolunteeringRepository` solo guarda datos, `schemas.py` solo convierte a JSON y `routes.py` solo define rutas. |
| **O**: Open/Closed | Abierto a extensión, cerrado a modificación | Para usar otra fuente de datos se **agrega** una clase que implemente `VolunteeringRepository`. No se modifican la entidad, los casos de uso ni las rutas. |
| **L**: Liskov Substitution | Una implementación puede reemplazar a otra sin romper nada | `InMemoryVolunteeringRepository` y `FakeVolunteeringRepository` (`tests/test_use_cases.py`) son intercambiables: los casos de uso funcionan igual con cualquiera, y los tests lo prueban. |
| **I**: Interface Segregation | Interfaces pequeñas, solo con lo que se usa | El puerto tiene únicamente `list_all` y `get_by_id`. No incluye métodos de escritura que ningún caso de uso necesita. |
| **D**: Dependency Inversion | Depender de abstracciones, no de implementaciones | Los casos de uso reciben un `VolunteeringRepository` (abstracto) en el constructor y nunca importan la clase concreta. La implementación la decide `main.py`. |

**Demostración con los tests:** `test_use_cases.py` crea un repositorio falso que implementa el puerto y se lo pasa a los casos de uso. Prueba a la vez la **L** (el falso sustituye al real) y la **D** (el caso de uso depende solo de la abstracción). Además, esos tests no necesitan levantar FastAPI.

### 4.4 Ejemplo de extensión: cambiar a PostgreSQL

1. Crear `app/infrastructure/postgres_repository.py` con `PostgresVolunteeringRepository(VolunteeringRepository)`, que implemente `list_all` y `get_by_id` con SQL.
2. Agregar el driver a `requirements.txt`.
3. Cambiar **una línea** en `main.py`: `repository = PostgresVolunteeringRepository(...)`.

`domain/`, `application/`, `api/` y los tests de casos de uso **no cambian**. Ahí se ven juntos OCP, DIP y la separación de capas de DDD.

Más detalle en [`solid-ddd.md`](solid-ddd.md).

## 5. Calidad y verificación

- **Tests:** 15 por servicio con pytest, en verde. Cubren las invariantes de la entidad, los casos de uso con un repositorio falso y los endpoints (`200`, `404`, `422` y `/health`).
- **Reglas comprobadas con búsqueda de texto:** `domain/` no importa FastAPI, Pydantic ni otras capas; los backends no usan `CORSMiddleware`, y el frontend no usa `innerHTML` (evita XSS).
- **Despliegue:** los contenedores corren en la ECS con `docker compose` y el frontend funciona en localhost a través de APIG.

## 6. Guion sugerido para la demo

1. **Problema** (30 s): oportunidades dispersas, una sola web que las centraliza.
2. **Web funcionando:**
   - Abre la página con DevTools → Network: se ven **2 llamadas en paralelo**.
   - Alterna las pestañas sin recargar.
   - Haz clic en una tarjeta: llamada por id y detalle en el diálogo.
   - Muestra la versión móvil (375 px): una sola columna.
3. **Características de APIG:**
   - **Autenticación:** con un AppCode incorrecto en tu `config.js` local, sirviendo la web en localhost (o con `curl` sin la cabecera), aparece "No autorizado".
   - **Throttling:** pulsa *Recargar* varias veces seguidas hasta ver el mensaje de `429`.
   - **CORS:** en Network, las cabeceras `Access-Control-Allow-Origin` de la respuesta.
4. **Arquitectura:** el recorrido de la sección 2, apoyado en el diagrama.
5. **Código:** la estructura de capas, una entidad con invariantes, un caso de uso, el composition root y un test con el repositorio falso.
6. **Cierre:** qué se dejó fuera (sección 7) y cómo se extendería.

Comandos `curl` útiles en vivo:

```bash
curl -i https://<APIG-GROUP-DOMAIN>/volunteering                                   # 401
curl -i -H "X-Apig-AppCode: <APPCODE>" https://<APIG-GROUP-DOMAIN>/volunteering     # 200
curl -i -H "X-Apig-AppCode: <APPCODE>" https://<APIG-GROUP-DOMAIN>/scholarships/999 # 404
```

## 7. Alcance y limitaciones

- **Fuera del alcance:** CRUD, búsqueda, filtros, paginación, usuarios y login, y base de datos.
- **AppCode visible en el navegador:** aunque ya no está en el repositorio, el navegador necesita el dominio y el AppCode para llamar a APIG, así que se ven en DevTools. Las variables de entorno no pueden ocultar valores que usa el propio navegador. En producción se usaría un proxy del lado del servidor (patrón BFF, por ejemplo con Vercel Functions) que agregue el AppCode sin enviarlo al cliente, o autenticación por usuario.
- **Tráfico sin cifrar dentro de la VPC:** el tramo APIG → ECS va por HTTP sin TLS, pero no sale de la red privada.
- **Datos ilustrativos:** las organizaciones de voluntariado son ficticias y los datos de becas deben verificarse en fuentes oficiales.
