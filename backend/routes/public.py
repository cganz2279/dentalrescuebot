from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

# Create PUBLIC router - NO AUTHENTICATION
router = APIRouter(prefix="/api/public", tags=["public"])

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

@router.get("/procedures/{procedure_id}")
async def get_procedure_public(procedure_id: str):
    """PUBLIC endpoint to get procedure details - NO authentication required"""
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

@router.get("/procedures")
async def get_all_procedures_public():
    """PUBLIC endpoint to get all procedures - NO authentication required"""
    try:
        procedures = await db.procedures.find(
            {}, 
            {"_id": 0, "createdAt": 0, "updatedAt": 0}
        ).to_list(1000)
        
        return {"success": True, "data": procedures}
    except Exception as e:
        logging.error(f"Error fetching procedures: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")