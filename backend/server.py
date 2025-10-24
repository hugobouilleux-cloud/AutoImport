from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import httpx
from playwright.async_api import async_playwright
import asyncio


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class ConnectionConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    site_url: str
    login: str
    password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_connected: Optional[datetime] = None
    status: str = "pending"  # pending, success, failed

class ConnectionConfigCreate(BaseModel):
    site_url: str
    login: str
    password: str

class ConnectionTest(BaseModel):
    site_url: str
    login: str
    password: str

class ConnectionResult(BaseModel):
    success: bool
    message: str
    status_code: Optional[int] = None

class ImportFormat(BaseModel):
    name: str
    href: str

class ImportFormatsList(BaseModel):
    success: bool
    message: str
    formats: List[ImportFormat]
    total_count: int

class SelectFormatRequest(BaseModel):
    site_url: str
    login: str
    password: str
    selected_format: ImportFormat

class SelectFormatResult(BaseModel):
    success: bool
    message: str
    format_url: Optional[str] = None

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Automation Import App API"}

@api_router.post("/connection/test", response_model=ConnectionResult)
async def test_connection(connection_data: ConnectionTest):
    """
    Test the connection to the external site
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0, verify=False) as client:
            # Préparer les données de connexion
            login_data = {
                "username": connection_data.login,
                "password": connection_data.password
            }
            
            # Tenter la connexion
            response = await client.post(
                connection_data.site_url,
                data=login_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            
            # Vérifier la réponse
            if response.status_code == 200:
                # Vérifier si la connexion a réussi (peut nécessiter une adaptation selon le site)
                if "error" not in response.text.lower() and "invalid" not in response.text.lower():
                    return ConnectionResult(
                        success=True,
                        message="Connexion réussie au site cible",
                        status_code=response.status_code
                    )
                else:
                    return ConnectionResult(
                        success=False,
                        message="Identifiants invalides",
                        status_code=response.status_code
                    )
            else:
                return ConnectionResult(
                    success=False,
                    message=f"Échec de la connexion: HTTP {response.status_code}",
                    status_code=response.status_code
                )
                
    except httpx.TimeoutException:
        return ConnectionResult(
            success=False,
            message="Timeout: le site ne répond pas",
            status_code=None
        )
    except httpx.RequestError as e:
        return ConnectionResult(
            success=False,
            message=f"Erreur de connexion: {str(e)}",
            status_code=None
        )
    except Exception as e:
        return ConnectionResult(
            success=False,
            message=f"Erreur inattendue: {str(e)}",
            status_code=None
        )

@api_router.post("/connection/save", response_model=ConnectionConfig)
async def save_connection(connection_data: ConnectionConfigCreate):
    """
    Save connection configuration
    """
    config = ConnectionConfig(**connection_data.model_dump())
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = config.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc['last_connected']:
        doc['last_connected'] = doc['last_connected'].isoformat()
    
    await db.connections.insert_one(doc)
    return config

@api_router.get("/connection/list", response_model=List[ConnectionConfig])
async def list_connections():
    """
    Get all saved connections
    """
    connections = await db.connections.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for conn in connections:
        if isinstance(conn['created_at'], str):
            conn['created_at'] = datetime.fromisoformat(conn['created_at'])
        if conn.get('last_connected') and isinstance(conn['last_connected'], str):
            conn['last_connected'] = datetime.fromisoformat(conn['last_connected'])
    
    return connections

@api_router.delete("/connection/{connection_id}")
async def delete_connection(connection_id: str):
    """
    Delete a saved connection
    """
    result = await db.connections.delete_one({"id": connection_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Connection not found")
    return {"message": "Connection deleted successfully"}

@api_router.post("/connection/navigate-admin")
async def navigate_to_admin(connection_data: ConnectionTest):
    """
    Navigate to administration page using Playwright
    """
    try:
        async with async_playwright() as p:
            # Lancer le navigateur en mode headless
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
            context = await browser.new_context(
                ignore_https_errors=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            
            try:
                # Étape 1: Aller sur la page de login
                await page.goto(connection_data.site_url, timeout=30000, wait_until="networkidle")
                await asyncio.sleep(1)
                
                # Étape 2: Remplir le formulaire de connexion
                # Remplir le champ username (j_username)
                await page.fill('input[name="j_username"]', connection_data.login, timeout=5000)
                await asyncio.sleep(0.5)
                
                # Remplir le champ password (j_password)
                await page.fill('input[name="j_password"]', connection_data.password, timeout=5000)
                await asyncio.sleep(1)
                
                # Étape 3: Attendre que le bouton soit activé et cliquer
                # Le bouton est désactivé tant que le formulaire n'est pas valide
                await page.wait_for_selector('button[type="submit"]:not([disabled])', timeout=10000)
                await asyncio.sleep(0.5)
                await page.click('button[type="submit"]', timeout=5000)
                
                # Attendre la navigation
                await page.wait_for_load_state("networkidle", timeout=15000)
                await asyncio.sleep(2)
                
                # Étape 4: Cliquer sur l'icône utilisateur
                try:
                    # Chercher l'élément avec la classe icon-user
                    await page.click('.icon-user', timeout=5000)
                    await asyncio.sleep(1)
                except Exception as e:
                    # Essayer d'autres sélecteurs
                    user_selectors = [
                        'span.icon-user-without-picture',
                        'span.icon-user',
                        '[class*="icon-user"]',
                        'button:has(.icon-user)'
                    ]
                    clicked = False
                    for selector in user_selectors:
                        try:
                            await page.click(selector, timeout=2000)
                            clicked = True
                            await asyncio.sleep(1)
                            break
                        except:
                            continue
                    
                    if not clicked:
                        raise Exception(f"Impossible de cliquer sur l'icône utilisateur: {str(e)}")
                
                # Étape 5: Cliquer sur "Administration" dans le menu
                try:
                    # Attendre que le menu apparaisse
                    await page.wait_for_selector('button[mat-menu-item]', timeout=5000)
                    
                    # Cliquer sur Administration
                    admin_selectors = [
                        'button.user-menu-item:has-text("Administration")',
                        'button[mat-menu-item]:has-text("Administration")',
                        'span.user-menu-item-label:has-text("Administration")',
                        '[class*="menu-item"]:has-text("Administration")'
                    ]
                    
                    clicked_admin = False
                    for selector in admin_selectors:
                        try:
                            await page.click(selector, timeout=2000)
                            clicked_admin = True
                            break
                        except:
                            continue
                    
                    if not clicked_admin:
                        raise Exception("Impossible de cliquer sur Administration")
                    
                    # Attendre le chargement de la page d'administration
                    await page.wait_for_load_state("networkidle", timeout=15000)
                    await asyncio.sleep(2)
                    
                    # Récupérer l'URL actuelle
                    current_url = page.url
                    
                    # Prendre un screenshot pour vérification
                    screenshot = await page.screenshot(full_page=False)
                    
                    await browser.close()
                    
                    return {
                        "success": True,
                        "message": "Navigation vers l'administration réussie",
                        "admin_url": current_url
                    }
                    
                except Exception as e:
                    await browser.close()
                    raise Exception(f"Erreur lors de la navigation vers l'administration: {str(e)}")
                
            except Exception as e:
                await browser.close()
                raise e
                
    except Exception as e:
        logger.error(f"Navigation error: {str(e)}")
        return {
            "success": False,
            "message": f"Erreur: {str(e)}",
            "admin_url": None
        }

@api_router.post("/connection/extract-formats", response_model=ImportFormatsList)
async def extract_import_formats(connection_data: ConnectionTest):
    """
    Extract all import formats from the admin page with pagination
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
            context = await browser.new_context(
                ignore_https_errors=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            
            try:
                # Étape 1: Connexion (même processus que navigate-admin)
                await page.goto(connection_data.site_url, timeout=30000, wait_until="networkidle")
                await asyncio.sleep(1)
                
                await page.fill('input[name="j_username"]', connection_data.login, timeout=5000)
                await asyncio.sleep(0.5)
                await page.fill('input[name="j_password"]', connection_data.password, timeout=5000)
                await asyncio.sleep(1)
                
                await page.wait_for_selector('button[type="submit"]:not([disabled])', timeout=10000)
                await asyncio.sleep(0.5)
                await page.click('button[type="submit"]', timeout=5000)
                
                await page.wait_for_load_state("networkidle", timeout=15000)
                await asyncio.sleep(2)
                
                # Cliquer sur l'icône utilisateur
                await page.click('.icon-user', timeout=5000)
                await asyncio.sleep(1)
                
                # Cliquer sur Administration
                await page.wait_for_selector('button[mat-menu-item]', timeout=5000)
                await page.click('button.user-menu-item:has-text("Administration")', timeout=5000)
                await page.wait_for_load_state("networkidle", timeout=15000)
                await asyncio.sleep(2)
                
                # Étape 2: Cliquer sur "Import de données"
                await page.click('a:has-text("Import de données")', timeout=10000)
                await page.wait_for_load_state("networkidle", timeout=15000)
                await asyncio.sleep(2)
                
                # Étape 3: Extraire tous les formats avec pagination
                all_formats = []
                page_number = 1
                
                while True:
                    # Attendre que le tableau soit chargé
                    await page.wait_for_selector('app-link a.a', timeout=10000)
                    await asyncio.sleep(1.5)
                    
                    # Extraire les éléments de la page actuelle
                    formats = await page.evaluate('''() => {
                        const links = document.querySelectorAll('app-link a.a');
                        return Array.from(links).map(link => ({
                            name: link.textContent.trim(),
                            href: link.getAttribute('href')
                        }));
                    }''')
                    
                    all_formats.extend(formats)
                    logger.info(f"Page {page_number}: {len(formats)} formats extraits, total: {len(all_formats)}")
                    
                    # Vérifier s'il y a une page suivante (bouton non désactivé)
                    try:
                        # Chercher le bouton "Page suivante" qui n'est pas disabled
                        next_button_exists = await page.evaluate('''() => {
                            const buttons = document.querySelectorAll('button.k-pager-nav');
                            for (let btn of buttons) {
                                const title = btn.getAttribute('title');
                                const ariaLabel = btn.getAttribute('aria-label');
                                if ((title === 'Page suivante' || ariaLabel === 'Page suivante') && 
                                    !btn.disabled && !btn.classList.contains('k-disabled')) {
                                    return true;
                                }
                            }
                            return false;
                        }''')
                        
                        if next_button_exists:
                            # Cliquer sur le bouton suivant
                            await page.evaluate('''() => {
                                const buttons = document.querySelectorAll('button.k-pager-nav');
                                for (let btn of buttons) {
                                    const title = btn.getAttribute('title');
                                    const ariaLabel = btn.getAttribute('aria-label');
                                    if ((title === 'Page suivante' || ariaLabel === 'Page suivante') && 
                                        !btn.disabled && !btn.classList.contains('k-disabled')) {
                                        btn.click();
                                        return;
                                    }
                                }
                            }''')
                            await asyncio.sleep(2)
                            await page.wait_for_load_state("networkidle", timeout=10000)
                            await asyncio.sleep(1)
                            page_number += 1
                        else:
                            logger.info(f"Fin de la pagination - Total: {len(all_formats)} formats")
                            break
                    except Exception as e:
                        logger.info(f"Erreur pagination ou fin atteinte: {str(e)}")
                        break
                
                await browser.close()
                
                return ImportFormatsList(
                    success=True,
                    message=f"{len(all_formats)} formats d'import extraits avec succès",
                    formats=all_formats,
                    total_count=len(all_formats)
                )
                
            except Exception as e:
                await browser.close()
                raise e
                
    except Exception as e:
        logger.error(f"Extract formats error: {str(e)}")
        return ImportFormatsList(
            success=False,
            message=f"Erreur: {str(e)}",
            formats=[],
            total_count=0
        )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()