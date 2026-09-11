from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from app.services.auditors.rgaa_service import RGAAService
from app.services.auditors.rgesn_service import RGESNService
from app.services.auditors.rgpd_service import RGPDService


class AuditService:

    @staticmethod
    def analyser_url(url: str):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1280, "height": 800},
                )
                page = context.new_page()

                response = page.goto(
                    url, timeout=20000, wait_until="networkidle"
                )

                if not response:
                    browser.close()
                    return {"error": "Aucune réponse reçue du serveur."}

                html_content = page.content()
                soup = BeautifulSoup(html_content, "html.parser")

                # --- Execution des 3 audits spécialisés ---
                resultats_rgaa = RGAAService.audit(page, soup)
                resultats_rgpd = RGPDService.audit(page, soup, url)
                resultats_rgesn = RGESNService.audit(page, soup)

                browser.close()

                return {
                    "url": url,
                    "rgaa": resultats_rgaa,
                    "rgpd": resultats_rgpd,
                    "rgesn": resultats_rgesn,
                }

        except Exception as e:
            return {"error": f"Erreur lors de l'analyse Playwright : {str(e)}"}