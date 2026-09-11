from fastapi import APIRouter, HTTPException
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/audit", tags=["Audit"])

@router.get("/")
def executer_audit(url: str):
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="L'URL doit commencer par http:// ou https://")
    
    resultats = AuditService.analyser_url(url)
    
    if "error" in resultats:
        raise HTTPException(status_code=400, detail=resultats["error"])
        
    return resultats