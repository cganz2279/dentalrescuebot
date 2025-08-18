from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

# Import the new auth, practice, payment, webhook, and admin routes
from routes.auth import router as auth_router
from routes.practice import router as practice_router
from routes.payments import router as payments_router
from routes.webhooks import router as webhooks_router
from routes.admin import router as admin_router


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

print(f"Connecting to MongoDB: {mongo_url}")
print(f"Using database: {os.environ.get('DB_NAME', 'test_database')}")

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class RecoveryTimeline(BaseModel):
    day: str
    activity: str

class Procedure(BaseModel):
    id: str
    name: str
    specialty: str
    specialtyName: str
    duration: str
    overview: str
    immediateAftercare: List[str]
    dietRestrictions: List[str]
    warningSignsToCallDoctor: List[str]
    recoveryTimeline: List[RecoveryTimeline]
    medications: List[str]

class ProcedureBasic(BaseModel):
    id: str
    name: str
    specialty: str
    specialtyName: str
    duration: str

class Specialty(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    color: str
    procedureCount: Optional[int] = 0

class APIResponse(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Dental API Routes
@api_router.get("/specialties")
async def get_specialties():
    try:
        # Get all specialties
        specialties_cursor = db.specialties.find({}, {"_id": 0, "createdAt": 0, "updatedAt": 0})
        specialties = await specialties_cursor.to_list(length=None)
        
        # Get procedure counts for each specialty
        for specialty in specialties:
            count = await db.procedures.count_documents({"specialty": specialty["id"]})
            specialty["procedureCount"] = count
        
        return {"success": True, "data": specialties}
    except Exception as e:
        logging.error(f"Error fetching specialties: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/specialties/{specialty_id}")
async def get_specialty(specialty_id: str):
    try:
        # Get specialty details
        specialty = await db.specialties.find_one(
            {"id": specialty_id}, 
            {"_id": 0, "createdAt": 0, "updatedAt": 0}
        )
        
        if not specialty:
            raise HTTPException(status_code=404, detail="Specialty not found")
        
        # Get procedures for this specialty
        procedures_cursor = db.procedures.find(
            {"specialty": specialty_id},
            {"_id": 0, "id": 1, "name": 1, "specialty": 1, "specialtyName": 1, "duration": 1}
        )
        procedures = await procedures_cursor.to_list(length=None)
        
        specialty["procedures"] = procedures
        
        return {"success": True, "data": specialty}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching specialty {specialty_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/procedures")
async def get_procedures(specialty: Optional[str] = Query(None)):
    try:
        query = {}
        if specialty:
            query["specialty"] = specialty
        
        procedures_cursor = db.procedures.find(
            query,
            {"_id": 0, "id": 1, "name": 1, "specialty": 1, "specialtyName": 1, "duration": 1}
        )
        procedures = await procedures_cursor.to_list(length=None)
        
        return {"success": True, "data": procedures}
    except Exception as e:
        logging.error(f"Error fetching procedures: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/procedures/search")
async def search_procedures(q: str = Query(..., min_length=1)):
    try:
        # Create text search query
        procedures_cursor = db.procedures.find(
            {
                "$or": [
                    {"name": {"$regex": q, "$options": "i"}},
                    {"specialtyName": {"$regex": q, "$options": "i"}},
                    {"overview": {"$regex": q, "$options": "i"}}
                ]
            },
            {"_id": 0, "id": 1, "name": 1, "specialty": 1, "specialtyName": 1, "duration": 1}
        )
        procedures = await procedures_cursor.to_list(length=None)
        
        return {"success": True, "data": procedures}
    except Exception as e:
        logging.error(f"Error searching procedures: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/procedures/{procedure_id}")
async def get_procedure(procedure_id: str):
    try:
        procedure = await db.procedures.find_one(
            {"id": procedure_id}, 
            {"_id": 0, "createdAt": 0, "updatedAt": 0}
        )
        
        if not procedure:
            raise HTTPException(status_code=404, detail="Procedure not found")
        
        return {"success": True, "data": procedure}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching procedure {procedure_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Include the router in the main app
app.include_router(api_router)

# Include auth, practice management, payment, and webhook routes
app.include_router(auth_router)
app.include_router(practice_router)
app.include_router(payments_router)
app.include_router(webhooks_router)

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
