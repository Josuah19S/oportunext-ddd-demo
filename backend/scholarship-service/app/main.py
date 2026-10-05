from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import build_router
from app.application.use_cases import GetScholarship, ListScholarships
from app.domain.errors import ScholarshipNotFoundError
from app.infrastructure.in_memory_repository import InMemoryScholarshipRepository

# Composition root: wires the adapter, the use cases and the router by hand.
repository = InMemoryScholarshipRepository()
list_scholarships = ListScholarships(repository)
get_scholarship = GetScholarship(repository)

app = FastAPI(title="Scholarship Service")
app.include_router(build_router(list_scholarships, get_scholarship))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(ScholarshipNotFoundError)
def handle_not_found(request: Request, error: ScholarshipNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(error)})
