from playwright.sync_api import sync_playwright
import json
import time
import re
import os

# Lien optimisé
SEARCH_URL = "https://www.bing.com/search?q=ram+ddr5+32gb+6000mhz+cl30+price"

def executer_releve():
    print(f"[{time.strftime('%H:%M:%S')}] Lancement du releve...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            
            page = context.new_page()
            # On simule un vrai comportement
            page.goto(SEARCH_URL, wait_until="domcontentloaded")
            time.sleep(5)
            
            # Gestion cookies
            try:
                page.locator("#bnp_btn_accept, button:has-text('Accepter'), .bnp_btn_accept").first.click(timeout=3000)
            except: pass

            # Extraction plus large : on prend les chiffres suivis de € ou EUR
            content = page.content()
            # Regex qui accepte 120, 120.50 ou 120,50
            regex_prix = r"(\d{2,3}(?:[,\.]\d{2})?)\s*(?:€|EUR)"
            trouvailles = re.findall(regex_prix, content)
            
            prix_valides = []
            for p_str in trouvailles:
                val = float(p_str.replace(',', '.'))
                # FILTRE MIS A JOUR : 80€ a 400€ (plus realiste pour de la RAM)
                if 80 <= val <= 700:
                    prix_valides.append(val)

            prix_uniques = list(dict.fromkeys(prix_valides))[:8]

            if prix_uniques:
                moyenne = round(sum(prix_uniques) / len(prix_uniques), 2)
                timestamp = int((time.time() + 7200) * 1000)
                
                if os.path.exists('data.json'):
                    with open('data.json', 'r') as f:
                        try: data = json.load(f)
                        except: data = []
                else: data = []
                
                data.append([timestamp, moyenne])
                
                # On ne garde que les 100 derniers points pour pas que le fichier soit trop lourd
                if len(data) > 100: data = data[-100:]
                
                with open('data.json', 'w') as f:
                    json.dump(data, f)
                
                print(f"SUCCES : Moyenne de {moyenne}€ enregistree ({len(prix_uniques)} prix trouves).")
            else:
                print("ECHEC : Aucun prix detecte dans la zone 80€-400€.")
                page.screenshot(path="debug_screenshot.png")
            
            browser.close()
    except Exception as e:
        print(f"ERREUR CRITIQUE : {e}")

if __name__ == "__main__":
    executer_releve()
