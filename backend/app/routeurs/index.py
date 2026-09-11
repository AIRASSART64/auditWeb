from app.routeurs.audit_router import router as audit_router
from fastapi import APIRouter

# Routeur principal de l'API
api_router = APIRouter(prefix="/api")

# On attache chaque sous-routeur
api_router.include_router(audit_router)
# Quand tu ajouteras d'autres fonctionnalités :
# api_router.include_router(user_router)