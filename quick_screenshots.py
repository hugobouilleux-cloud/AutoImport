"""
Script rapide pour prendre des captures d'écran de l'application
Sans nécessiter de vraies credentials
"""

import asyncio
from playwright.async_api import async_playwright

APP_URL = "https://data-import-tools.preview.emergentagent.com"

async def take_screenshots():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        import os
        os.makedirs("screenshots", exist_ok=True)
        
        print("📸 Prise de captures d'écran...")
        
        # Page d'accueil
        print("\n1️⃣ Page d'accueil...")
        await page.goto(APP_URL)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)
        await page.screenshot(path="screenshots/01_homepage.png", full_page=True)
        
        # Vue mobile (optionnel)
        print("\n2️⃣ Vue mobile...")
        await page.set_viewport_size({"width": 375, "height": 812})
        await asyncio.sleep(1)
        await page.screenshot(path="screenshots/02_mobile.png", full_page=True)
        
        # Retour à la vue desktop
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Zoom sur le formulaire
        print("\n3️⃣ Formulaire de connexion...")
        await page.evaluate("window.scrollTo(0, 200)")
        await asyncio.sleep(1)
        await page.screenshot(path="screenshots/03_login_form.png")
        
        print("\n✅ Captures d'écran sauvegardées dans : screenshots/")
        print("\n💡 Pour des captures avec données réelles :")
        print("   - Naviguez manuellement dans l'application")
        print("   - Utilisez l'outil de capture d'écran de votre système")
        
        await asyncio.sleep(2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(take_screenshots())
