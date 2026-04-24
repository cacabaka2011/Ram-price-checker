from playwright.sync_api import sync_playwright
import json
import time
import re
import os

# Ton lien Bing
SEARCH_URL = "https://www.bing.com/search?q=ram%20ddr5%2032gb&qs=n&form=QBRE&sp=-1&lq=0&pq=ram%20ddr5%2032gb&sc=12-13&sk=&cvid=09914EBAAAA2421498C78DA6C802E7D5"

def executer_releve():
    heure_actuelle = time.strftime('%H:%M:%S')
    print(f"[{heure_actuelle}] Lancement du releve sur les serveurs GitHub...")

    try:
        with sync_playwright() as p:
            # HEADLESS=TRUE EST OBLIGATOIRE SUR GITHUB (pas d'écran sur les serveurs)
            browser = p.chromium.launch(headless=True)
            
            # LE DÉGUISEMENT
            context = browser.new_context(
                locale="fr-BE",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            )
            
            page = context.new_page()
            page.goto(SEARCH_URL, wait_until="networkidle")
            
            # Clic Cookies
            try:
                btn = page.locator("#bnp_btn_accept, button:has-text('Accepter')").first
                btn.click(timeout=5000)
            except:
                pass

            time.sleep(6) 
            content = page.content()
            
            # Extraction des prix
            regex_prix = r"(\d{2,3}[,\.]\d{2})\s*€"
            trouvailles = re.findall(regex_prix, content)
            
            prix_valides = []
            for p_str in trouvailles:
                val = float(p_str.replace(',', '.'))
                # Filtre de securite 200€ - 750€
                if 200 <= val <= 750:
                    prix_valides.append(val)

            prix_uniques = list(dict.fromkeys(prix_valides))[:5]

            if prix_uniques:
                moyenne = round(sum(prix_uniques) / len(prix_uniques), 2)
                
                # Fix Heure UTC+2 (Bruxelles/Paris)
                timestamp_local = int((time.time() + 7200) * 1000)
                
                if os.path.exists('data.json'):
                    with open('data.json', 'r') as f:
                        try:
                            data = json.load(f)
                        except:
                            data = []
                else:
                    data = []
                
                data.append([timestamp_local, moyenne])
                
                with open('data.json', 'w') as f:
                    json.dump(data, f)
                
                print(f"Succès ! Moyenne de {moyenne}€ ajoutée à data.json")
            else:
                print("Problème technique, aucun prix trouvé.")
                print("Prise de la photo en cours pour voir ce que Bing affiche...")
                
                # --- LA PARTIE PHOTO EST ICI ---
                page.screenshot(path="debug_screenshot.png")
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(content)
                    
                print("Voici un aperçu de ce que le robot a vu :")
                print(content[:600]) 
            
            browser.close()
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    executer_releve()
