# Ram-price-checker
this project is meant to make a robot that checks the ram prices and put them on a graphic

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
            # headless=True est OBLIGATOIRE sur GitHub
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(locale="fr-BE")
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
                
                # Lecture du fichier data.json existant sur GitHub
                if os.path.exists('data.json'):
                    with open('data.json', 'r') as f:
                        try:
                            data = json.load(f)
                        except:
                            data = []
                else:
                    data = []
                
                # Ajout de la nouvelle donnée
                data.append([timestamp_local, moyenne])
                
                # Sauvegarde locale (GitHub Actions l'enverra ensuite sur ton dépôt)
                with open('data.json', 'w') as f:
                    json.dump(data, f)
                
                print(f"Succès ! Moyenne de {moyenne}€ ajoutée à data.json")
            else:
                print("Problème technique, aucun prix trouvé.")
            
            browser.close()
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    # On l'execute une seule fois (GitHub s'occupe de le relancer)
    executer_releve()


    OPEN SOURCE CODE (this is for python script)
