from bs4 import BeautifulSoup
from playwright.sync_api import Page

# URL du script axe-core (version stable)
AXE_CORE_CDN = (
    "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.3/axe.min.js"
)


class RGAAService:

    @staticmethod
    def audit(page: Page, soup: BeautifulSoup) -> dict:
        """Effectue un audit d'accessibilité approfondi basé sur le RGAA 4.1.

        Combine l'analyse de structure BeautifulSoup et le moteur de règles
        axe-core.
        """
        # -------------------------------------------------------------
        # 1. Analyse structurale via BeautifulSoup (Titres & Images)
        # -------------------------------------------------------------
        images = soup.find_all("img")
        images_sans_alt = []
        images_decoratives = []
        images_valides = []

        for img in images:
            alt = img.get("alt")
            src = img.get("src", "sans-src")
            if alt is None:
                images_sans_alt.append(src)
            elif alt.strip() == "":
                images_decoratives.append(src)
            else:
                images_valides.append({"src": src, "alt": alt})

        total_images = len(images)

        # Structure de la hiérarchie des titres (h1 - h6)
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        structure_titres = [
            {"niveau": h.name, "texte": h.get_text(strip=True)[:60]}
            for h in headings
        ]

        has_h1 = any(h.name == "h1" for h in headings)

        # -------------------------------------------------------------
        # 2. Audit automatisé via Axe-Core injecté dans Playwright
        # -------------------------------------------------------------
        axe_violations = []
        axe_passes_count = 0

        try:
            # Injection de axe-core dans la page
            page.add_script_tag(url=AXE_CORE_CDN)

            # Exécution de l'analyse d'accessibilité
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
                    "impact": v.get("impact"),  # 'minor', 'moderate', 'serious', 'critical'
                    "description": v.get("help"),
                    "regle": v.get("helpUrl"),
                    "elements_touches": len(v.get("nodes", [])),
                    "exemples": [
                        node.get("html") for node in v.get("nodes", [])[:3]
                    ],
                })
        except Exception as e:
            # Si le CDN échoue ou que le JS est bloqué
            axe_violations.append({
                "id": "axe-error",
                "impact": "unknown",
                "description": f"Erreur lors de l'exécution d'axe-core : {str(e)}",
                "elements_touches": 0,
                "exemples": [],
            })

        # -------------------------------------------------------------
        # 3. Calcul du Score Global RGAA (Sur 100)
        # -------------------------------------------------------------
        # Déductions basées sur la sévérité des violations d'axe-core
        penalites = 0
        for v in axe_violations:
            impact = v.get("impact")
            count = v.get("elements_touches", 1)
            if impact == "critical":
                penalites += 10 * min(count, 3)
            elif impact == "serious":
                penalites += 5 * min(count, 3)
            elif impact == "moderate":
                penalites += 2 * min(count, 3)
            elif impact == "minor":
                penalites += 1 * min(count, 3)

        # Pénalité si le h1 est absent
        if not has_h1:
            penalites += 10

        score_rgaa = max(0.0, round(100.0 - penalites, 1))

        return {
            "score": score_rgaa,
            "synthese": {
                "critique": sum(
                    1
                    for v in axe_violations
                    if v.get("impact") == "critical"
                ),
                "grave": sum(
                    1 for v in axe_violations if v.get("impact") == "serious"
                ),
                "moyen": sum(
                    1 for v in axe_violations if v.get("impact") == "moderate"
                ),
                "mineur": sum(
                    1 for v in axe_violations if v.get("impact") == "minor"
                ),
                "regles_validees": axe_passes_count,
            },
            "images": {
                "total": total_images,
                "sans_alt": len(images_sans_alt),
                "decoratives": len(images_decoratives),
                "valides": len(images_valides),
                "liste_sans_alt": images_sans_alt[:5],  # 5 premières max
            },
            "structure": {
                "presence_h1": has_h1,
                "nombre_titres": len(headings),
                "arborescence": structure_titres[
                    :10
                ],  # 10 premiers titres max
            },
            "violations_detaillees": axe_violations,
        }