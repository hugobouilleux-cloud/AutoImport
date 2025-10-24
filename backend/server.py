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