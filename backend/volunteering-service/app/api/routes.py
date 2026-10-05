from fastapi import APIRouter

from app.api.schemas import VolunteeringResponse, to_response
from app.application.use_cases import GetVolunteering, ListVolunteering


def build_router(list_uc: ListVolunteering, get_uc: GetVolunteering) -> APIRouter:
    router = APIRouter()

    @router.get("/volunteering", response_model=list[VolunteeringResponse])
    def list_volunteering() -> list[VolunteeringResponse]:
        return [to_response(item) for item in list_uc.execute()]

    @router.get("/volunteering/{volunteering_id}", response_model=VolunteeringResponse)
    def get_volunteering(volunteering_id: int) -> VolunteeringResponse:
        return to_response(get_uc.execute(volunteering_id))

    return router
