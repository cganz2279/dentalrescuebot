from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
import os
import jwt
from datetime import datetime
import uuid
from typing import Optional, List
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

router = APIRouter(prefix="/api/patients", tags=["patients"])
security = HTTPBearer()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

JWT_SECRET = os.environ.get('JWT_SECRET', 'your-super-secret-jwt-key-change-in-production')

# Helper function to verify patient token and get patient info
async def get_current_patient(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['userId']
        role = payload['role']
        practice_id = payload['practiceId']
        
        # Verify it's a patient
        if role != 'patient':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patient access required"
            )
        
        # Get patient from database
        patient = await db.users.find_one({"id": user_id, "role": "patient"})
        if not patient or not patient.get('isActive'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Patient not found or inactive"
            )
        
        return {
            "patientId": user_id,
            "patient": patient,
            "practiceId": practice_id
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.get("/dashboard")
async def get_patient_dashboard(current_patient: dict = Depends(get_current_patient)):
    """Get patient dashboard with assigned procedures"""
    try:
        patient_id = current_patient["patientId"]
        practice_id = current_patient["practiceId"]
        patient = current_patient["patient"]
        
        # Get practice info for branding
        practice = await db.practices.find_one(
            {"id": practice_id},
            {"_id": 0, "name": 1, "branding": 1, "phone": 1, "address": 1}
        )
        
        # Get assigned procedures for this patient
        assigned_procedures = await db.patientprocedures.find(
            {"patientId": patient_id, "practiceId": practice_id},
            {"_id": 0}
        ).sort("performedDate", -1).to_list(length=None)
        
        # Get full procedure details for each assignment
        for assignment in assigned_procedures:
            procedure_details = await db.procedures.find_one(
                {"id": assignment["procedureId"]},
                {"_id": 0}
            )
            if procedure_details:
                assignment["procedureDetails"] = procedure_details
        
        return {
            "success": True,
            "data": {
                "patient": {
                    "id": patient["id"],
                    "firstName": patient["firstName"],
                    "lastName": patient["lastName"],
                    "email": patient["email"]
                },
                "practice": practice,
                "assignedProcedures": assigned_procedures,
                "stats": {
                    "totalProcedures": len(assigned_procedures),
                    "activeProcedures": len([p for p in assigned_procedures if p.get("status") == "active"]),
                    "completedProcedures": len([p for p in assigned_procedures if p.get("status") == "completed"])
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Patient dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load dashboard"
        )

@router.get("/procedures/{assignment_id}")
async def get_patient_procedure(
    assignment_id: str,
    current_patient: dict = Depends(get_current_patient)
):
    """Get detailed procedure information for a patient"""
    try:
        patient_id = current_patient["patientId"]
        practice_id = current_patient["practiceId"]
        
        # Get procedure assignment - verify it belongs to this patient
        assignment = await db.patientprocedures.find_one(
            {
                "id": assignment_id,
                "patientId": patient_id,
                "practiceId": practice_id
            },
            {"_id": 0}
        )
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Procedure assignment not found"
            )
        
        # Get full procedure details
        procedure = await db.procedures.find_one(
            {"id": assignment["procedureId"]},
            {"_id": 0}
        )
        
        if not procedure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Procedure details not found"
            )
        
        # Get practice info for branding
        practice = await db.practices.find_one(
            {"id": practice_id},
            {"_id": 0, "name": 1, "branding": 1, "phone": 1, "address": 1}
        )
        
        # Increment view count
        await db.patientprocedures.update_one(
            {"id": assignment_id},
            {"$inc": {"viewCount": 1}, "$set": {"updatedAt": datetime.utcnow()}}
        )
        
        return {
            "success": True,
            "data": {
                "assignment": assignment,
                "procedure": procedure,
                "practice": practice
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get patient procedure error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get procedure details"
        )

@router.post("/procedures/{assignment_id}/download")
async def track_pdf_download(
    assignment_id: str,
    current_patient: dict = Depends(get_current_patient)
):
    """Track PDF download for analytics"""
    try:
        patient_id = current_patient["patientId"]
        
        # Verify assignment belongs to this patient
        assignment = await db.patientprocedures.find_one(
            {
                "id": assignment_id,
                "patientId": patient_id
            }
        )
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Procedure assignment not found"
            )
        
        # Increment download count
        await db.patientprocedures.update_one(
            {"id": assignment_id},
            {"$inc": {"pdfDownloadCount": 1}, "$set": {"updatedAt": datetime.utcnow()}}
        )
        
        return {
            "success": True,
            "message": "Download tracked"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Track download error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track download"
        )