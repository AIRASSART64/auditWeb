from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


# ==========================================
# 1. SCHÉMAS RGAA (Accessibilité)
# ==========================================
class SyntheseGravite(BaseModel):
    critique: int = 0
    grave: int = 0
    moyen: int = 0
    mineur: int = 0
    regles_validees: int = 0


class ViolationDetail(BaseModel):
    id: str
    impact: Optional[str] = "unknown"
    description: Optional[str] = None
    regle: Optional[str] = None
    elements_touches: int = 0
    exemples: List[str] = Field(default_factory=list)


class ImagesAudit(BaseModel):
    total: int = 0
    sans_alt: int = 0
    decoratives: int = 0
    valides: int = 0
    liste_sans_alt: List[str] = Field(default_factory=list)


class StructureAudit(BaseModel):
    presence_h1: bool = False
    nombre_titres: int = 0
    arborescence: List[Dict[str, Any]] = Field(default_factory=list)


class RGAAAuditResult(BaseModel):
    score: float = Field(..., ge=0, le=100)
    synthese: SyntheseGravite
    images: ImagesAudit
    structure: StructureAudit
    violations_detaillees: List[ViolationDetail] = Field(default_factory=list)


# ==========================================
# 2. SCHÉMAS RGPD (Vie Privée)
# ==========================================
class CookieDetail(BaseModel):
    nom: str
    domaine: Optional[str] = None
    securise: bool = False
    http_only: bool = False
    same_site: Optional[str] = "None"


class CookiesAudit(BaseModel):
    total: int = 0
    non_securises: int = 0
    liste: List[CookieDetail] = Field(default_factory=list)


class BanniereConsentement(BaseModel):
    detectee: bool = False
    nom_cmp: str = "Aucune CMP détectée"


class TraqueursAudit(BaseModel):
    total_detectes: int = 0
    liste: List[str] = Field(default_factory=list)
    domaines_tiers_appeles: List[str] = Field(default_factory=list)


class RGPDAuditResult(BaseModel):
    score: float = Field(..., ge=0, le=100)
    banniere_consentement: BanniereConsentement
    cookies: CookiesAudit
    traqueurs: TraqueursAudit


# ==========================================
# 3. SCHÉMAS RGESN (Éco-conception)
# ==========================================
class EmpreinteEcologique(BaseModel):
    co2_g_par_visite: float = 0.0
    energie_kwh_par_visite: float = 0.0
    note_eco: str = "E"


class PoidsAudit(BaseModel):
    total_mo: float = 0.0
    total_ko: float = 0.0
    repartition_ko: Dict[str, float] = Field(default_factory=dict)


class ReseauAudit(BaseModel):
    requetes_totales: int = 0


class DOMAudit(BaseModel):
    elements_totaux: int = 0


class RGESNAuditResult(BaseModel):
    score: float = Field(..., ge=0, le=100)
    empreinte_ecologique: EmpreinteEcologique
    poids: PoidsAudit
    reseau: ReseauAudit
    dom: DOMAudit


# ==========================================
# 4. SCHÉMA GLOBAL & RÉSOLUTION DYNAMIQUE
# ==========================================
class AuditResponse(BaseModel):
    url: HttpUrl
    rgaa: RGAAAuditResult
    rgpd: RGPDAuditResult
    rgesn: RGESNAuditResult


class AuditErrorResponse(BaseModel):
    error: str


# Forcer la reconstruction et la résolution explicite des types Pydantic v2
AuditResponse.model_rebuild()
AuditErrorResponse.model_rebuild()