from fastapi import APIRouter, HTTPException, status
from app.schemas.audit import AuditResponse, AuditErrorResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.post(
    "/analyser",
    response_model=AuditResponse,
    responses={400: {"model": AuditErrorResponse}},
    summary="Effectuer un audit complet (RGAA, RGPD, RGESN)",
)
def effectuer_audit(url: str):
    resultat = AuditService.analyser_url(url)

    if "error" in resultat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultat["error"]
        )

    return resultat