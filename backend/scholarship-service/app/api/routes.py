from fastapi import APIRouter

from app.api.schemas import ScholarshipResponse, to_response
from app.application.use_cases import GetScholarship, ListScholarships


def build_router(list_uc: ListScholarships, get_uc: GetScholarship) -> APIRouter:
    router = APIRouter()

    @router.get("/scholarships", response_model=list[ScholarshipResponse])
    def list_scholarships() -> list[ScholarshipResponse]:
        return [to_response(item) for item in list_uc.execute()]

    @router.get("/scholarships/{scholarship_id}", response_model=ScholarshipResponse)
    def get_scholarship(scholarship_id: int) -> ScholarshipResponse:
        return to_response(get_uc.execute(scholarship_id))

    return router
