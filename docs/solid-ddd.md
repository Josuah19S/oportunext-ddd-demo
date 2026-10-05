# SOLID y DDD en oportunext-ddd-demo

Este documento muestra dónde se aplican los principios SOLID y los patrones de DDD en el código. Los ejemplos citan `volunteering-service`; `scholarship-service` tiene la misma estructura con `Scholarship`, `Level`, `ScholarshipRepository`, `ListScholarships` y `GetScholarship`.

Regla de dependencia entre capas:

```
api ──▶ application ──▶ domain ◀── infrastructure
```

## SOLID

**S: Single Responsibility.** Cada clase tiene un solo motivo de cambio. `ListVolunteering` y `GetVolunteering` (`app/application/use_cases.py`) son un caso de uso cada uno. `InMemoryVolunteeringRepository` (`app/infrastructure/in_memory_repository.py`) solo guarda datos, y `schemas.py` solo traduce entidades a respuestas HTTP.

**O: Open/Closed.** Para cambiar la fuente de datos se agrega una clase nueva que implemente `VolunteeringRepository` (`app/domain/repositories.py`). Los casos de uso y el dominio no se modifican.

**L: Liskov Substitution.** `InMemoryVolunteeringRepository` y `FakeVolunteeringRepository` (`tests/test_use_cases.py`) son intercambiables: los casos de uso funcionan igual con cualquiera, como prueban los tests.

**I: Interface Segregation.** El puerto `VolunteeringRepository` expone solo lo que los casos de uso necesitan: `list_all` y `get_by_id`. No hay métodos de escritura que nadie usa.

**D: Dependency Inversion.** Los casos de uso reciben la abstracción `VolunteeringRepository` en su constructor, no la implementación concreta. `app/main.py` decide qué implementación inyectar.

## DDD

- **Bounded contexts:** un microservicio por contexto. *Voluntariados* (`volunteering-service`) y *Becas* (`scholarship-service`) no comparten código ni datos.
- **Entidades con invariantes:** `Volunteering` (`app/domain/entities.py`) es un `dataclass(frozen=True)` que valida en `__post_init__` que `id > 0`, que los textos obligatorios no estén vacíos y que `modality` sea un `Modality`. Si no, lanza `InvalidVolunteeringError`. No puede existir una entidad inválida.
- **Repositorio como puerto/adaptador:** el puerto `VolunteeringRepository` vive en `domain`; el adaptador `InMemoryVolunteeringRepository` vive en `infrastructure`.
- **Casos de uso en `application`:** `ListVolunteering` y `GetVolunteering` coordinan el dominio. `GetVolunteering` convierte un `None` del repositorio en `VolunteeringNotFoundError`.
- **Errores de dominio mapeados a HTTP en `api`:** el dominio lanza `VolunteeringNotFoundError` (`app/domain/errors.py`) sin saber nada de HTTP. `app/main.py` registra un `exception_handler` que lo traduce a `404 {"detail": "..."}`.
- **Dominio puro:** `app/domain/` no importa FastAPI, Pydantic ni otras capas. Las respuestas HTTP usan `VolunteeringResponse` (`app/api/schemas.py`), así la entidad no se expone directamente.
- **Composition root:** `app/main.py` crea el repositorio, los casos de uso y el router (`build_router` en `app/api/routes.py`) y los conecta a mano, sin `Depends`.

## Cómo cambiar a PostgreSQL sin tocar dominio ni casos de uso

1. Crear `app/infrastructure/postgres_repository.py` con una clase `PostgresVolunteeringRepository(VolunteeringRepository)` que implemente `list_all` y `get_by_id` con consultas SQL y devuelva entidades `Volunteering`.
2. Agregar el driver (por ejemplo `psycopg`) a `requirements.txt`.
3. En `app/main.py`, cambiar una línea: `repository = PostgresVolunteeringRepository(...)` en lugar de `InMemoryVolunteeringRepository()`.

`domain/`, `application/`, `api/` y los tests de casos de uso no cambian.
