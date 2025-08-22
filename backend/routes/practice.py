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
import bcrypt

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

router = APIRouter(prefix="/api/practice", tags=["practice"])
security = HTTPBearer()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

JWT_SECRET = os.environ.get('JWT_SECRET', 'your-super-secret-jwt-key-change-in-production')

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def generate_temp_password() -> str:
    return str(uuid.uuid4()).replace('-', '')[:12]

# Pydantic models
class BrandingUpdate(BaseModel):
    logo: Optional[str] = None
    primaryColor: Optional[str] = None
    secondaryColor: Optional[str] = None
    welcomeMessage: Optional[str] = None

class PracticeUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[dict] = None
    branding: Optional[BrandingUpdate] = None
    newPassword: Optional[str] = None

class PatientCreate(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str
    phone: Optional[str] = None

class ProcedureAssignment(BaseModel):
    patientId: str
    procedureId: str
    procedureName: str
    performedDate: str  # ISO date string
    dentistName: str
    practiceNotes: Optional[str] = None
    customInstructions: Optional[List[str]] = None
    followUpDate: Optional[str] = None

# Helper function to verify token and get user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['userId']
        role = payload['role']
        practice_id = payload['practiceId']
        
        # Get user from database
        user = await db.users.find_one({"id": user_id})
        if not user or not user.get('isActive'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return {
            "userId": user_id,
            "user": user,
            "role": role,
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
async def get_practice_dashboard(current_user: dict = Depends(get_current_user)):
    """Get practice dashboard data"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        
        if role not in ['practice_admin', 'practice_staff']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get practice info
        practice = await db.practices.find_one(
            {"id": practice_id},
            {"_id": 0}
        )
        
        if not practice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found"
            )
        
        # Get patient count
        patient_count = await db.users.count_documents({
            "practiceId": practice_id,
            "role": "patient",
            "isActive": True
        })
        
        # Get active procedures count
        active_procedures = await db.patientprocedures.count_documents({
            "practiceId": practice_id,
            "status": "active"
        })
        
        # Get recent patients (last 10)
        recent_patients = await db.users.find(
            {
                "practiceId": practice_id,
                "role": "patient",
                "isActive": True
            },
            {
                "_id": 0,
                "id": 1,
                "firstName": 1,
                "lastName": 1,
                "email": 1,
                "createdAt": 1,
                "lastLoginAt": 1
            }
        ).sort("createdAt", -1).limit(10).to_list(length=None)
        
        # Get recent procedures (last 10)
        recent_procedures = await db.patientprocedures.find(
            {"practiceId": practice_id},
            {"_id": 0}
        ).sort("performedDate", -1).limit(10).to_list(length=None)
        
        return {
            "success": True,
            "data": {
                "practice": practice,
                "stats": {
                    "patientCount": patient_count,
                    "activeProcedures": active_procedures,
                    "subscriptionStatus": practice.get("subscription", {}).get("status", "unknown")
                },
                "recentPatients": recent_patients,
                "recentProcedures": recent_procedures
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load dashboard"
        )

@router.get("/patients")
async def get_practice_patients(current_user: dict = Depends(get_current_user)):
    """Get all patients for the practice"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        
        if role not in ['practice_admin', 'practice_staff']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get all patients for this practice
        patients = await db.users.find(
            {
                "practiceId": practice_id,
                "role": "patient"
            },
            {
                "_id": 0,
                "password": 0
            }
        ).sort("lastName", 1).to_list(length=None)
        
        # Get procedure count for each patient
        for patient in patients:
            procedure_count = await db.patientprocedures.count_documents({
                "practiceId": practice_id,
                "patientId": patient["id"]
            })
            patient["procedureCount"] = procedure_count
        
        return {
            "success": True,
            "data": patients
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get patients error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get patients"
        )

@router.post("/patients")
async def create_patient(
    patient_data: PatientCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new patient"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        user_id = current_user["user"]["id"]
        
        if role not in ['practice_admin', 'practice_staff']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check if email already exists
        existing_user = await db.users.find_one({"email": patient_data.email.lower()})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Generate patient ID
        patient_id = str(uuid.uuid4())
        
        # Create patient document
        patient_doc = {
            "id": patient_id,
            "email": patient_data.email.lower(),
            "password": "$2b$12$" + str(uuid.uuid4()).replace("-", ""),  # Temporary password
            "firstName": patient_data.firstName,
            "lastName": patient_data.lastName,
            "role": "patient",
            "practiceId": practice_id,
            "isActive": True,
            "isEmailVerified": False,
            "invitedBy": user_id,
            "invitedAt": datetime.utcnow(),
            "loginCount": 0,
            "patientInfo": {
                "phone": patient_data.phone
            },
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        await db.users.insert_one(patient_doc)
        
        # Remove password from response
        del patient_doc["password"]
        
        return {
            "success": True,
            "message": "Patient created successfully",
            "data": patient_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Create patient error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create patient"
        )

@router.post("/assign-procedure")
async def assign_procedure_to_patient(
    assignment: ProcedureAssignment,
    current_user: dict = Depends(get_current_user)
):
    """Assign a procedure to a patient"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        
        if role not in ['practice_admin', 'practice_staff']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Verify patient belongs to this practice
        patient = await db.users.find_one({
            "id": assignment.patientId,
            "practiceId": practice_id,
            "role": "patient"
        })
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Verify procedure exists
        procedure = await db.procedures.find_one({"id": assignment.procedureId})
        if not procedure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Procedure not found"
            )
        
        # Create patient procedure assignment
        assignment_id = str(uuid.uuid4())
        
        assignment_doc = {
            "id": assignment_id,
            "patientId": assignment.patientId,
            "practiceId": practice_id,
            "procedureId": assignment.procedureId,
            "procedureName": assignment.procedureName,
            "performedDate": datetime.fromisoformat(assignment.performedDate.replace('Z', '+00:00')),
            "dentistName": assignment.dentistName,
            "practiceNotes": assignment.practiceNotes,
            "customInstructions": assignment.customInstructions or [],
            "followUpDate": datetime.fromisoformat(assignment.followUpDate.replace('Z', '+00:00')) if assignment.followUpDate else None,
            "status": "active",
            "pdfDownloadCount": 0,
            "viewCount": 0,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        await db.patientprocedures.insert_one(assignment_doc)
        
        return {
            "success": True,
            "message": "Procedure assigned successfully",
            "data": {
                "assignmentId": assignment_id,
                "patientName": f"{patient['firstName']} {patient['lastName']}",
                "procedureName": assignment.procedureName
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Assign procedure error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign procedure"
        )

@router.put("/branding")
async def update_practice_branding(
    branding: BrandingUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update practice branding"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        
        if role != 'practice_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only practice admins can update branding"
            )
        
        # Build update document
        update_doc = {"updatedAt": datetime.utcnow()}
        
        if branding.logo is not None:
            update_doc["branding.logo"] = branding.logo
        if branding.primaryColor is not None:
            update_doc["branding.primaryColor"] = branding.primaryColor
        if branding.secondaryColor is not None:
            update_doc["branding.secondaryColor"] = branding.secondaryColor
        if branding.welcomeMessage is not None:
            update_doc["branding.welcomeMessage"] = branding.welcomeMessage
        
        # Update practice
        result = await db.practices.update_one(
            {"id": practice_id},
            {"$set": update_doc}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found"
            )
        
        # Get updated practice
        updated_practice = await db.practices.find_one(
            {"id": practice_id},
            {"_id": 0}
        )
        
        return {
            "success": True,
            "message": "Branding updated successfully",
            "data": updated_practice
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update branding error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update branding"
        )

@router.put("/update")
async def update_practice(
    update_data: PracticeUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update practice information, branding, or password"""
    try:
        practice_id = current_user["practiceId"]
        user_id = current_user["userId"]
        role = current_user["role"]
        
        if role != 'practice_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only practice admins can update practice settings"
            )
        
        # Build practice update document
        practice_update = {"updatedAt": datetime.utcnow()}
        
        # Update basic practice info
        if update_data.name is not None:
            practice_update["name"] = update_data.name
        if update_data.phone is not None:
            practice_update["phone"] = update_data.phone
        if update_data.website is not None:
            practice_update["website"] = update_data.website
            
        # Update address if provided
        if hasattr(update_data, 'address') and update_data.address:
            practice_update["address"] = update_data.address
            
        # Update branding if provided
        if update_data.branding is not None:
            if update_data.branding.logo is not None:
                practice_update["branding.logo"] = update_data.branding.logo
            if update_data.branding.primaryColor is not None:
                practice_update["branding.primaryColor"] = update_data.branding.primaryColor
            if update_data.branding.secondaryColor is not None:
                practice_update["branding.secondaryColor"] = update_data.branding.secondaryColor
            if update_data.branding.welcomeMessage is not None:
                practice_update["branding.welcomeMessage"] = update_data.branding.welcomeMessage
        
        # Update practice if there are changes
        if len(practice_update) > 1:  # More than just updatedAt
            await db.practices.update_one(
                {"id": practice_id},
                {"$set": practice_update}
            )
        
        # Handle password update separately
        if hasattr(update_data, 'newPassword') and update_data.newPassword:
            import bcrypt
            hashed_password = bcrypt.hashpw(update_data.newPassword.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            await db.users.update_one(
                {"id": user_id},
                {"$set": {
                    "password": hashed_password,
                    "updatedAt": datetime.utcnow()
                }}
            )
        
        return {
            "success": True,
            "message": "Practice settings updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update practice error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update practice settings"
        )

@router.post("/add-staff")
async def add_practice_staff(
    firstName: str,
    lastName: str, 
    email: EmailStr,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Add a staff member to the practice (practice_admin only)"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['userId']
        role = payload['role']
        practice_id = payload['practiceId']
        
        # Only practice admins can add staff
        if role != 'practice_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only practice administrators can add staff members"
            )
        
        # Check if email already exists
        existing_user = await db.users.find_one({"email": email.lower()})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )
        
        # Generate temporary password
        temp_password = generate_temp_password()
        staff_id = str(uuid.uuid4())
        
        # Create staff user
        staff_doc = {
            "id": staff_id,
            "email": email.lower(),
            "password": hash_password(temp_password),
            "firstName": firstName,
            "lastName": lastName,
            "role": "practice_staff",
            "practiceId": practice_id,
            "isActive": True,
            "isEmailVerified": False,
            "requiresPasswordChange": True,
            "loginCount": 0,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        await db.users.insert_one(staff_doc)
        
        return {
            "success": True,
            "message": f"Staff member {firstName} {lastName} added successfully",
            "staffMember": {
                "id": staff_id,
                "email": email,
                "firstName": firstName,
                "lastName": lastName,
                "role": "practice_staff"
            },
            "temporaryPassword": temp_password
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
    except Exception as e:
        print(f"Add staff error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add staff member"
        )