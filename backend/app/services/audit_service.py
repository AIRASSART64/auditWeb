import asyncio
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from app.services.auditors.rgaa_service import RGAAService
from app.services.auditors.rgesn_service import RGESNService
from app.services.auditors.rgpd_service import RGPDService


class AuditService:

    @staticmethod
    def _analyser_sync(url: str) -> dict:
        """Méthode synchrone exécutée dans un thread séparé (contourne les limites d'Event Loop Windows)."""
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )

            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 800},
                locale="fr-FR"
            )

            context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            page = context.new_page()

            try:
                page.goto(url, timeout=25000, wait_until="domcontentloaded")
            except Exception as goto_err:
                html_content = page.content()
                if len(html_content) < 500:
                    browser.close()
                    return {"error": f"Impossible d'accéder à la page : {str(goto_err)}"}

            page.wait_for_timeout(2000)
            html_content = page.content()
            soup = BeautifulSoup(html_content, "html.parser")

            # Exécution des audits
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

    @staticmethod
    async def analyser_url(url: str) -> dict:
        """Point d'entrée asynchrone appelé par le routeur FastAPI."""
        try:
            return await asyncio.to_thread(AuditService._analyser_sync, url)
        except Exception as e:
            return {"error": f"Erreur lors de l'analyse Playwright : {str(e)}"}