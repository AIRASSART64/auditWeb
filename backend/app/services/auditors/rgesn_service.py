from bs4 import BeautifulSoup
from playwright.sync_api import Page


class RGESNService:

    # Constantes pour l'estimation d'empreinte carbone (SWD v3 Model)
    KWH_PER_GB = 0.81  # Consommation moyenne par Go transféré
    GLOBAL_GRID_CARBON_INTENSITY = (
        442  # gCO2e par kWh (Moyenne mondiale de l'électricité)
    )

    @staticmethod
    def audit(page: Page, soup: BeautifulSoup) -> dict:
        """Effectue un audit RGESN : Analyse des requêtes réseau, poids global

        des ressources et calcul d'empreinte carbone.
        """
        # -------------------------------------------------------------
        # 1. Écoute et mesure du trafic réseau (Network Interception)
        # -------------------------------------------------------------
        poids_par_type = {
            "image": 0,
            "script": 0,
            "stylesheet": 0,
            "font": 0,
            "document": 0,
            "media": 0,
            "other": 0,
        }
        requetes_totales = 0
        poids_total_octets = 0

        # Récupération des ressources chargées via l'API Performance du navigateur
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

        # Convertir les octets en Mo et Ko
        poids_total_mo = poids_total_octets / (1024 * 1024)
        poids_total_ko = poids_total_octets / 1024

        poids_details_ko = {
            k: round(v / 1024, 2) for k, v in poids_par_type.items()
        }

        # -------------------------------------------------------------
        # 2. Analyse de la sobriété du DOM
        # -------------------------------------------------------------
        nombre_elements_dom = page.evaluate(
            "() => document.querySelectorAll('*').length"
        )

        # -------------------------------------------------------------
        # 3. Calcul de l'Empreinte Carbone (gCO2e) & Énergie (kWh)
        # -------------------------------------------------------------
        # Conversion Mo en Go pour la formule
        poids_go = poids_total_mo / 1024
        kwh_consommes = poids_go * RGESNService.KWH_PER_GB
        co2_grammes = kwh_consommes * RGESNService.GLOBAL_GRID_CARBON_INTENSITY

        # -------------------------------------------------------------
        # 4. Calcul du Score RGESN (Sur 100)
        # -------------------------------------------------------------
        # Recommandations RGESN : Page < 2 Mo, < 50 requêtes HTTP, < 1500 éléments DOM
        score_poids = max(0, 100 - (poids_total_mo * 25))  # Malus dès > 1 Mo
        score_requetes = max(0, 100 - (requetes_totales * 1.5))
        score_dom = max(0, 100 - (nombre_elements_dom / 30))

        score_rgesn = round(
            (score_poids * 0.5) + (score_requetes * 0.3) + (score_dom * 0.2), 1
        )

        return {
            "score": score_rgesn,
            "empreinte_ecologique": {
                "co2_g_par_visite": round(co2_grammes, 3),
                "energie_kwh_par_visite": round(kwh_consommes, 5),
                "note_eco": (
                    "A"
                    if co2_grammes < 0.2
                    else (
                        "B"
                        if co2_grammes < 0.5
                        else (
                            "C"
                            if co2_grammes < 1.0
                            else "D" if co2_grammes < 1.5 else "E"
                        )
                    )
                ),
            },
            "poids": {
                "total_mo": round(poids_total_mo, 2),
                "total_ko": round(poids_total_ko, 2),
                "repartition_ko": poids_details_ko,
            },
            "reseau": {
                "requetes_totales": requetes_totales,
            },
            "dom": {
                "elements_totaux": nombre_elements_dom,
            },
        }