"""
Script de démo automatisé pour AutoImport by VPWhite
À enregistrer avec OBS Studio ou Loom pour créer un teaser vidéo

Instructions :
1. Lancez OBS Studio ou Loom en mode enregistrement d'écran
2. Exécutez ce script : python demo_script.py
3. Le script va automatiquement naviguer dans l'application avec des pauses
4. Arrêtez l'enregistrement à la fin
"""

import asyncio
from playwright.async_api import async_playwright
import time

# Configuration
APP_URL = "https://data-import-tools.preview.emergentagent.com"
DEMO_SPEED = "slow"  # "slow", "medium", "fast"

# Timing pour chaque vitesse
SPEEDS = {
    "slow": {"pause": 3, "action": 1.5, "typing": 100},
    "medium": {"pause": 2, "action": 1, "typing": 50},
    "fast": {"pause": 1, "action": 0.5, "typing": 30}
}

async def demo_workflow():
    """
    Workflow de démo complet
    """
    speed = SPEEDS[DEMO_SPEED]
    
    async with async_playwright() as p:
        # Lancer le navigateur en mode visible
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            record_video_dir="./demo_videos",
            record_video_size={"width": 1920, "height": 1080}
        )
        
        page = await context.new_page()
        
        try:
            print("🎬 Démarrage de la démo AutoImport by VPWhite...")
            
            # ========================================
            # ÉTAPE 1 : Page d'accueil
            # ========================================
            print("\n📍 ÉTAPE 1 : Chargement de l'application...")
            await page.goto(APP_URL)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(speed["pause"] * 2)  # Pause plus longue pour l'intro
            
            # Prendre une capture d'écran
            await page.screenshot(path="demo_screenshots/01_homepage.png", full_page=True)
            
            # ========================================
            # ÉTAPE 2 : Formulaire de connexion
            # ========================================
            print("\n📍 ÉTAPE 2 : Affichage du formulaire de connexion...")
            await asyncio.sleep(speed["pause"])
            
            # Simuler le remplissage (sans vraies credentials)
            # Scroll vers le formulaire si nécessaire
            await page.evaluate("window.scrollTo(0, 200)")
            await asyncio.sleep(speed["action"])
            
            await page.screenshot(path="demo_screenshots/02_login_form.png")
            
            print("\n💡 NOTE : Pour la vraie démo, remplacez par vos credentials Legisway")
            print("   Pour l'instant, le script s'arrête ici.")
            print("\n📸 Captures d'écran sauvegardées dans : demo_screenshots/")
            
            # ========================================
            # Si vous avez des credentials de démo, décommentez ci-dessous
            # ========================================
            """
            # Remplir le formulaire
            await page.fill('input[name="site_url"]', 'https://votre-legisway.com', delay=speed["typing"])
            await asyncio.sleep(speed["action"])
            
            await page.fill('input[name="login"]', 'demo@user.com', delay=speed["typing"])
            await asyncio.sleep(speed["action"])
            
            await page.fill('input[name="password"]', '********', delay=speed["typing"])
            await asyncio.sleep(speed["action"])
            
            await page.fill('input[name="system_password"]', '********', delay=speed["typing"])
            await asyncio.sleep(speed["action"])
            
            await page.screenshot(path="demo_screenshots/03_form_filled.png")
            
            # Cliquer sur le bouton de connexion
            await page.click('button:has-text("Se connecter")')
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(speed["pause"])
            
            # ========================================
            # ÉTAPE 3 : Liste des formats d'import
            # ========================================
            print("\n📍 ÉTAPE 3 : Affichage des formats d'import...")
            await page.screenshot(path="demo_screenshots/04_import_formats.png")
            await asyncio.sleep(speed["pause"])
            
            # Scroller dans la liste
            await page.evaluate("window.scrollTo(0, 400)")
            await asyncio.sleep(speed["action"])
            
            # Sélectionner un format (simulé)
            # await page.click('button:has-text("Personne physique")')
            # await asyncio.sleep(speed["pause"])
            
            # ========================================
            # ÉTAPE 4 : Listes de référence
            # ========================================
            print("\n📍 ÉTAPE 4 : Affichage des listes de référence...")
            await page.screenshot(path="demo_screenshots/05_reference_lists.png", full_page=True)
            await asyncio.sleep(speed["pause"])
            
            # Ouvrir les détails d'une liste
            details = await page.query_selector('details')
            if details:
                await details.click()
                await asyncio.sleep(speed["action"])
                await page.screenshot(path="demo_screenshots/06_list_details.png")
            
            # ========================================
            # ÉTAPE 5 : Upload de fichier
            # ========================================
            print("\n📍 ÉTAPE 5 : Upload du fichier Excel...")
            await asyncio.sleep(speed["pause"])
            
            # Simuler le hover sur la zone d'upload
            upload_zone = await page.query_selector('#file-upload')
            if upload_zone:
                await upload_zone.hover()
                await asyncio.sleep(speed["action"])
                await page.screenshot(path="demo_screenshots/07_file_upload.png")
            
            # ========================================
            # ÉTAPE 6 : Validation avec erreurs
            # ========================================
            print("\n📍 ÉTAPE 6 : Affichage des erreurs de validation...")
            await asyncio.sleep(speed["pause"])
            
            # Scroller vers les erreurs (si présentes)
            await page.evaluate("window.scrollTo(0, 800)")
            await asyncio.sleep(speed["action"])
            await page.screenshot(path="demo_screenshots/08_validation_errors.png")
            
            # ========================================
            # ÉTAPE 7 : Import réussi
            # ========================================
            print("\n📍 ÉTAPE 7 : Import réussi avec fichier de résultat...")
            await asyncio.sleep(speed["pause"])
            
            await page.screenshot(path="demo_screenshots/09_import_success.png", full_page=True)
            """
            
            # Pause finale
            await asyncio.sleep(speed["pause"] * 2)
            
        except Exception as e:
            print(f"\n❌ Erreur pendant la démo : {str(e)}")
            await page.screenshot(path="demo_screenshots/error.png")
        
        finally:
            print("\n✅ Démo terminée !")
            print("📁 Vidéo sauvegardée dans : demo_videos/")
            print("📸 Screenshots sauvegardés dans : demo_screenshots/")
            
            await asyncio.sleep(2)
            await browser.close()


async def create_title_screen():
    """
    Créer un écran titre pour la vidéo
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Créer un écran titre avec HTML/CSS
        await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    margin: 0;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    color: white;
                }
                h1 {
                    font-size: 72px;
                    margin: 0;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                h2 {
                    font-size: 36px;
                    margin: 20px 0;
                    font-weight: 300;
                }
                p {
                    font-size: 24px;
                    opacity: 0.9;
                }
            </style>
        </head>
        <body>
            <h1>AutoImport by VPWhite</h1>
            <h2>Automatisez vos imports dans Legisway</h2>
            <p>✨ Validation intelligente • 🚀 Import automatique • 📊 Rapports détaillés</p>
        </body>
        </html>
        """)
        
        await page.screenshot(path="demo_screenshots/00_title.png", full_page=True)
        await browser.close()
        print("✅ Écran titre créé : demo_screenshots/00_title.png")


async def main():
    """
    Point d'entrée principal
    """
    import os
    
    # Créer les dossiers nécessaires
    os.makedirs("demo_screenshots", exist_ok=True)
    os.makedirs("demo_videos", exist_ok=True)
    
    print("=" * 60)
    print("  AutoImport by VPWhite - Script de Démo")
    print("=" * 60)
    print("\n⚡ Configuration :")
    print(f"   Vitesse : {DEMO_SPEED}")
    print(f"   URL : {APP_URL}")
    print("\n💡 Conseil : Lancez OBS Studio ou Loom AVANT d'exécuter ce script")
    print("\n⏰ La démo démarre dans 3 secondes...")
    
    await asyncio.sleep(3)
    
    # Créer l'écran titre
    await create_title_screen()
    
    # Lancer la démo
    await demo_workflow()
    
    print("\n" + "=" * 60)
    print("  🎉 Démo terminée avec succès !")
    print("=" * 60)
    print("\n📝 Prochaines étapes :")
    print("   1. Montez les captures d'écran avec votre outil préféré")
    print("   2. Ajoutez de la musique et des transitions")
    print("   3. Ajoutez des annotations pour expliquer les fonctionnalités")
    print("\n💡 Pour une vraie démo vidéo complète :")
    print("   - Décommentez le code avec les credentials")
    print("   - Enregistrez avec OBS pendant l'exécution")


if __name__ == "__main__":
    asyncio.run(main())
