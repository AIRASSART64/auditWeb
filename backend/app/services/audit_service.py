import requests
from bs4 import BeautifulSoup

class AuditService:
    @staticmethod
    def analyser_url(url: str):
        try:
            # Envoi de la requête à l'URL cible
            response = requests.get(url, timeout=10, headers={"User-Agent": "AuditFlow/1.0"})
            response.raise_for_status()
        except Exception as e:
            return {"error": f"Impossible d'analyser l'URL : {str(e)}"}

        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Analyse RGESN (Poids HTML en Ko et estimation CO2 basique)
        poids_ko = len(response.content) / 1024
        score_rgesn = max(0, round(100 - (poids_ko / 5), 1))

        # 2. Analyse RGAA (Accessibilité des images)
        images = soup.find_all("img")
        images_sans_alt = [img for img in images if not img.get("alt")]
        total_images = len(images)
        score_rgaa = (
            100.0 if total_images == 0 
            else round(((total_images - len(images_sans_alt)) / total_images) * 100, 1)
        )

        # 3. Analyse RGPD (Traqueurs et scripts tiers)
        scripts = soup.find_all("script", src=True)
        trackers = [s["src"] for s in scripts if any(keyword in s["src"].lower() for keyword in ["analytics", "pixel", "gtm", "facebook"])]
        score_rgpd = 100.0 if len(trackers) == 0 else max(20.0, 100 - (len(trackers) * 25))

        return {
            "url": url,
            "rgesn": {
                "score": score_rgesn,
                "poids_ko": round(poids_ko, 2)
            },
            "rgaa": {
                "score": score_rgaa,
                "total_images": total_images,
                "images_sans_alt": len(images_sans_alt)
            },
            "rgpd": {
                "score": score_rgpd,
                "trackers_detectes": len(trackers),
                "liste_trackers": trackers
            }
        }