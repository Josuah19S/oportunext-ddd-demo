from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import build_router
from app.application.use_cases import GetVolunteering, ListVolunteering
from app.domain.errors import VolunteeringNotFoundError
from app.infrastructure.in_memory_repository import InMemoryVolunteeringRepository

# Composition root: wires the adapter, the use cases and the router by hand.
repository = InMemoryVolunteeringRepository()
list_volunteering = ListVolunteering(repository)
get_volunteering = GetVolunteering(repository)

app = FastAPI(title="Volunteering Service")
app.include_router(build_router(list_volunteering, get_volunteering))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(VolunteeringNotFoundError)
def handle_not_found(request: Request, error: VolunteeringNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(error)})
