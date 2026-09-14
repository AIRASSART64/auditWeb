from bs4 import BeautifulSoup
from playwright.sync_api import Page

AXE_CORE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.3/axe.min.js"


class RGAAService:

    @staticmethod
    def audit(page: Page, soup: BeautifulSoup) -> dict:
        # 1. Analyse BeautifulSoup
        images = soup.find_all("img")
        images_sans_alt = [img.get("src", "sans-src") for img in images if img.get("alt") is None]
        images_decoratives = [img.get("src", "sans-src") for img in images if img.get("alt", "").strip() == ""]
        images_valides = [
            {"src": img.get("src", "sans-src"), "alt": img.get("alt")} 
            for img in images if img.get("alt") and img.get("alt").strip() != ""
        ]

        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        has_h1 = any(h.name == "h1" for h in headings)

        # 2. Injection axe-core et exécution synchrone
        axe_violations = []
        axe_passes_count = 0

        try:
            page.add_script_tag(url=AXE_CORE_CDN)

            results = page.evaluate("""
                async () => {
                    return await axe.run({
                        runOnly: {
                            type: 'tag',
                            values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice']
                        }
                    });
                }
            """)

            axe_passes_count = len(results.get("passes", []))

            for v in results.get("violations", []):
                axe_violations.append({
                    "id": v.get("id"),
                    "impact": v.get("impact"),
                    "description": v.get("help"),
                    "regle": v.get("helpUrl"),
                    "elements_touches": len(v.get("nodes", [])),
                    "exemples": [node.get("html") for node in v.get("nodes", [])[:3]],
                })
        except Exception as e:
            axe_violations.append({
                "id": "axe-error",
                "impact": "unknown",
                "description": f"Erreur axe-core : {str(e)}",
                "elements_touches": 0,
                "exemples": [],
            })

        # 3. Calcul du score RGAA
        penalites = sum(
            (10 if v.get("impact") == "critical" else
             5 if v.get("impact") == "serious" else
             2 if v.get("impact") == "moderate" else 1) * min(v.get("elements_touches", 1), 3)
            for v in axe_violations
        )

        if not has_h1:
            penalites += 10

        return {
            "score": max(0.0, round(100.0 - penalites, 1)),
            "synthese": {
                "critique": sum(1 for v in axe_violations if v.get("impact") == "critical"),
                "grave": sum(1 for v in axe_violations if v.get("impact") == "serious"),
                "moyen": sum(1 for v in axe_violations if v.get("impact") == "moderate"),
                "mineur": sum(1 for v in axe_violations if v.get("impact") == "minor"),
                "regles_validees": axe_passes_count,
            },
            "images": {
                "total": len(images),
                "sans_alt": len(images_sans_alt),
                "decoratives": len(images_decoratives),
                "valides": len(images_valides),
                "liste_sans_alt": images_sans_alt[:5],
            },
            "structure": {
                "presence_h1": has_h1,
                "nombre_titres": len(headings),
                "arborescence": [{"niveau": h.name, "texte": h.get_text(strip=True)[:60]} for h in headings[:10]],
            },
            "violations_detaillees": axe_violations,
        }