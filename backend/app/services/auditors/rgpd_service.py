import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import Page

TRACKER_PATTERNS = [
    r"google-analytics\.com", r"googletagmanager\.com", r"facebook\.net",
    r"doubleclick\.net", r"hotjar\.com", r"clarity\.ms", r"criteo\.com",
    r"tiktok\.com", r"linkedin\.com", r"datadoghq\.com", r"segment\.io",
    r"mixpanel\.com", r"amplitude\.com",
]

CMP_PATTERNS = [
    "axeptio", "didomi", "onetrust", "tarteaucitron",
    "cookiebot", "trustarc", "quantcast", "usercentrics",
]


class RGPDService:

    @staticmethod
    def audit(page: Page, soup: BeautifulSoup, base_url: str) -> dict:
        domain_base = urlparse(base_url).netloc.lower()

        # 1. Récupération synchrone des cookies
        cookies_context = page.context.cookies()
        cookies_presents = []
        cookies_non_securises = 0

        for c in cookies_context:
            is_secure = c.get("secure", False)
            if not is_secure:
                cookies_non_securises += 1

            cookies_presents.append({
                "nom": c.get("name"),
                "domaine": c.get("domain"),
                "securise": is_secure,
                "http_only": c.get("httpOnly", False),
                "same_site": c.get("sameSite", "None"),
            })

        # 2. Analyse BeautifulSoup
        scripts = soup.find_all("script", src=True)
        trackers_detectes = set()
        domaines_tiers = set()

        for s in scripts:
            src = s.get("src", "")
            src_domain = urlparse(src).netloc.lower()

            if src_domain and domain_base not in src_domain:
                domaines_tiers.add(src_domain)

            for pattern in TRACKER_PATTERNS:
                if re.search(pattern, src, re.IGNORECASE):
                    trackers_detectes.add(src_domain or src[:50])

        # 3. Recherche CMP dans le DOM
        html_content = str(soup).lower()
        cmp_trouvee = next((cmp.capitalize() for cmp in CMP_PATTERNS if cmp in html_content), None)

        # 4. Calcul du score
        penalites = (len(trackers_detectes) * 15) + (cookies_non_securises * 10)
        if len(trackers_detectes) > 0 and not cmp_trouvee:
            penalites += 25

        return {
            "score": max(0.0, round(100.0 - penalites, 1)),
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