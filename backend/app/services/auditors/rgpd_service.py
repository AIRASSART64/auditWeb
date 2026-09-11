import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import Page

# Domaines/mots-clés de traqueurs connus
TRACKER_PATTERNS = [
    r"google-analytics\.com",
    r"googletagmanager\.com",
    r"facebook\.net",
    r"doubleclick\.net",
    r"hotjar\.com",
    r"clarity\.ms",
    r"criteo\.com",
    r"tiktok\.com",
    r"linkedin\.com",
    r"datadoghq\.com",
    r"segment\.io",
    r"mixpanel\.com",
    r"amplitude\.com",
]

# Signatures de bannières de consentement (CMP) courantes
CMP_PATTERNS = [
    "axeptio",
    "didomi",
    "onetrust",
    "tarteaucitron",
    "cookiebot",
    "trustarc",
    "quantcast",
    "usercentrics",
]


class RGPDService:

    @staticmethod
    def audit(page: Page, soup: BeautifulSoup, base_url: str) -> dict:
        """Effectue un audit RGPD/Vie privée : traqueurs, cookies et bannières de

        consentement.
        """
        domain_base = urlparse(base_url).netloc.lower()

        # -------------------------------------------------------------
        # 1. Analyse des Cookies déposés
        # -------------------------------------------------------------
        cookies_context = page.context.cookies()
        cookies_presents = []
        cookies_non_securises = 0

        for c in cookies_context:
            is_secure = c.get("secure", False)
            same_site = c.get("sameSite", "None")

            if not is_secure:
                cookies_non_securises += 1

            cookies_presents.append({
                "nom": c.get("name"),
                "domaine": c.get("domain"),
                "securise": is_secure,
                "http_only": c.get("httpOnly", False),
                "same_site": same_site,
            })

        # -------------------------------------------------------------
        # 2. Détection des scripts & traqueurs tiers
        # -------------------------------------------------------------
        scripts = soup.find_all("script", src=True)
        trackers_detectes = set()
        domaines_tiers = set()

        for s in scripts:
            src = s.get("src", "")
            src_domain = urlparse(src).netloc.lower()

            # Vérification si le domaine du script est tiers
            if src_domain and domain_base not in src_domain:
                domaines_tiers.add(src_domain)

            # Vérification des patterns de traqueurs
            for pattern in TRACKER_PATTERNS:
                if re.search(pattern, src, re.IGNORECASE):
                    trackers_detectes.add(src_domain or src[:50])

        # -------------------------------------------------------------
        # 3. Détection de la bannière de consentement (CMP)
        # -------------------------------------------------------------
        html_content = str(soup).lower()
        cmp_trouvee = None

        for cmp in CMP_PATTERNS:
            if cmp in html_content:
                cmp_trouvee = cmp.capitalize()
                break

        # -------------------------------------------------------------
        # 4. Calcul du Score RGPD (Sur 100)
        # -------------------------------------------------------------
        penalites = 0

        # Pénalité par traqueur tiers détecté
        penalites += len(trackers_detectes) * 15

        # Pénalité si des cookies sont déposés sans HTTPS/Secure
        penalites += cookies_non_securises * 10

        # Pénalité si traqueurs présents sans bannière de consentement détectée
        if len(trackers_detectes) > 0 and not cmp_trouvee:
            penalites += 25

        score_rgpd = max(0.0, round(100.0 - penalites, 1))

        return {
            "score": score_rgpd,
            "banniere_consentement": {
                "detectee": cmp_trouvee is not None,
                "nom_cmp": cmp_trouvee or "Aucune CMP détectée",
            },
            "cookies": {
                "total": len(cookies_presents),
                "non_securises": cookies_non_securises,
                "liste": cookies_presents,
            },
            "traqueurs": {
                "total_detectes": len(trackers_detectes),
                "liste": list(trackers_detectes),
                "domaines_tiers_appeles": list(domaines_tiers),
            },
        }