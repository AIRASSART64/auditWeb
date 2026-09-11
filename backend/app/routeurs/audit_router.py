from fastapi import APIRouter, HTTPException
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Audits"])


@router.get("/")
def executer_audit(url: str):  # Retrait de 'async'
    if not url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=400,
            detail="L'URL doit commencer par http:// ou https://",
        )

    # Retrait de 'await' ici car analyser_url renvoie directement un dictionnaire
    resultats = AuditService.analyser_url(url)

    if "error" in resultats:
        raise HTTPException(status_code=400, detail=resultats["error"])

    return resultats