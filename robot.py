from playwright.sync_api import sync_playwright
import json
import time
import re
import os

# CIBLE : eBay France (Objets Neufs)
SEARCH_URL = "https://www.befr.ebay.be/sch/i.html?_nkw=ram+ddr5+cl30+6000mhz+32+gb&_sacat=0&_from=R40&_trksid=p4624852.m570.l1313"

def executer_releve():
    print(f"[{time.strftime('%H:%M:%S')}] Lancement du releve sur eBay...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            # 1. LE REGLAGE FRANÇAIS (Mieux qu'un clic)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                locale="fr-FR", # Force le site en Français
                extra_http_headers={"Accept-Language": "fr-FR,fr;q=0.9"} # Sécurité anti-anglais
            )
            
            page = context.new_page()
            page.goto(SEARCH_URL, wait_until="domcontentloaded")
            time.sleep(3)
            
            # Gestion cookies eBay
            try:
                page.locator("#gdpr-banner-accept").click(timeout=3000)
                print("Cookies acceptes.")
            except: pass

            # 2. LE SCROLL (Pour simuler un humain et charger les images/prix)
            print("Simulation de l'humain : defilement de la page...")
            for _ in range(4): # Appuie 4 fois sur "Page Suivante"
                page.keyboard.press("PageDown")
                time.sleep(1.5) # Pause entre chaque scroll

            content = page.content()
            
            # Extraction des prix
            regex_prix = r"(\d{2,3}[,\.]\d{2})\s*(?:€|EUR)"
            trouvailles = re.findall(regex_prix, content)
            
            prix_valides = []
            for p_str in trouvailles:
                val = float(p_str.replace(',', '.'))
                if 80 <= val <= 400:
                    prix_valides.append(val)

            # 3. ON PREND LES 10 PREMIERS OFFRES (au lieu de 5)
            prix_uniques = list(dict.fromkeys(prix_valides))[:10]

            if prix_uniques:
                moyenne = round(sum(prix_uniques) / len(prix_uniques), 2)
                timestamp = int((time.time() + 7200) * 1000)
                
                if os.path.exists('data.json'):
                    with open('data.json', 'r') as f:
                        try: data = json.load(f)
                        except: data = []
                else: data = []
                
                data.append([timestamp, moyenne])
                
                if len(data) > 100: data = data[-100:]
                
                with open('data.json', 'w') as f:
                    json.dump(data, f)
                
                print(f"SUCCES : Moyenne de {moyenne}€ calculee sur les {len(prix_uniques)} premiers prix eBay.")
            else:
                print("ECHEC : Aucun prix detecte sur eBay.")
                page.screenshot(path="debug_screenshot.png")
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(content)
            
            browser.close()
    except Exception as e:
        print(f"ERREUR : {e}")

if __name__ == "__main__":
    executer_releve()
