from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


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
                    url, timeout=15000, wait_until="domcontentloaded"
                )

                if not response:
                    browser.close()
                    return {"error": "Aucune réponse reçue du serveur."}

                html_content = page.content()
                soup = BeautifulSoup(html_content, "html.parser")

                # 1. RGESN
                poids_ko = len(html_content.encode("utf-8")) / 1024
                score_rgesn = max(0, round(100 - (poids_ko / 5), 1))

                # 2. RGAA
                images = soup.find_all("img")
                images_sans_alt = [img for img in images if not img.get("alt")]
                total_images = len(images)
                score_rgaa = (
                    100.0
                    if total_images == 0
                    else round(
                        ((total_images - len(images_sans_alt)) / total_images)
                        * 100,
                        1,
                    )
                )

                # 3. RGPD
                scripts = soup.find_all("script", src=True)
                trackers = [
                    s["src"]
                    for s in scripts
                    if any(
                        k in s["src"].lower()
                        for k in [
                            "analytics",
                            "pixel",
                            "gtm",
                            "facebook",
                            "datadome",
                            "akamai",
                        ]
                    )
                ]
                score_rgpd = (
                    100.0
                    if len(trackers) == 0
                    else max(20.0, 100 - (len(trackers) * 25))
                )

                browser.close()

                return {
                    "url": url,
                    "rgesn": {
                        "score": score_rgesn,
                        "poids_ko": round(poids_ko, 2),
                    },
                    "rgaa": {
                        "score": score_rgaa,
                        "total_images": total_images,
                        "images_sans_alt": len(images_sans_alt),
                    },
                    "rgpd": {
                        "score": score_rgpd,
                        "trackers_detectes": len(trackers),
                        "liste_trackers": trackers,
                    },
                }

        except Exception as e:
            return {"error": f"Erreur lors de l'analyse Playwright : {str(e)}"}