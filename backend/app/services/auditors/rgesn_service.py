from bs4 import BeautifulSoup
from playwright.sync_api import Page


class RGESNService:

    KWH_PER_GB = 0.81
    GLOBAL_GRID_CARBON_INTENSITY = 442

    @staticmethod
    def audit(page: Page, soup: BeautifulSoup) -> dict:
        poids_par_type = {
            "image": 0, "script": 0, "stylesheet": 0,
            "font": 0, "document": 0, "media": 0, "other": 0,
        }
        requetes_totales = 0
        poids_total_octets = 0

        # Évaluation JS synchrone pour la Performance API
        resources = page.evaluate("""
            () => performance.getEntriesByType('resource').map(r => ({
                name: r.name,
                type: r.initiatorType,
                size: r.transferSize || r.encodedBodySize || 0
            }))
        """)

        for res in resources:
            requetes_totales += 1
            size = res.get("size", 0)
            poids_total_octets += size
            res_type = res.get("type", "other")

            if res_type in ["img", "image"]:
                poids_par_type["image"] += size
            elif res_type in ["script"]:
                poids_par_type["script"] += size
            elif res_type in ["css", "link", "stylesheet"]:
                poids_par_type["stylesheet"] += size
            elif res_type in ["font"]:
                poids_par_type["font"] += size
            elif res_type in ["navigation", "document"]:
                poids_par_type["document"] += size
            elif res_type in ["media", "video", "audio"]:
                poids_par_type["media"] += size
            else:
                poids_par_type["other"] += size

        poids_total_mo = poids_total_octets / (1024 * 1024)
        poids_total_ko = poids_total_octets / 1024

        # Comptage synchrone des éléments DOM
        nombre_elements_dom = page.evaluate("() => document.querySelectorAll('*').length")

        # Empreinte carbone
        poids_go = poids_total_mo / 1024
        kwh_consommes = poids_go * RGESNService.KWH_PER_GB
        co2_grammes = kwh_consommes * RGESNService.GLOBAL_GRID_CARBON_INTENSITY

        # Calcul du score
        score_poids = max(0, 100 - (poids_total_mo * 25))
        score_requetes = max(0, 100 - (requetes_totales * 1.5))
        score_dom = max(0, 100 - (nombre_elements_dom / 30))

        score_rgesn = round((score_poids * 0.5) + (score_requetes * 0.3) + (score_dom * 0.2), 1)

        return {
            "score": score_rgesn,
            "empreinte_ecologique": {
                "co2_g_par_visite": round(co2_grammes, 3),
                "energie_kwh_par_visite": round(kwh_consommes, 5),
                "note_eco": (
                    "A" if co2_grammes < 0.2 else
                    "B" if co2_grammes < 0.5 else
                    "C" if co2_grammes < 1.0 else
                    "D" if co2_grammes < 1.5 else "E"
                ),
            },
            "poids": {
                "total_mo": round(poids_total_mo, 2),
                "total_ko": round(poids_total_ko, 2),
                "repartition_ko": {k: round(v / 1024, 2) for k, v in poids_par_type.items()},
            },
            "reseau": {"requetes_totales": requetes_totales},
            "dom": {"elements_totaux": nombre_elements_dom},
        }