from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
import os
import jwt
from datetime import datetime, timezone
import uuid
from typing import Optional, List, Dict
from dotenv import load_dotenv
from pathlib import Path
import bcrypt
import traceback
from ..utils.pdf_generator import generate_pdf_content
from ..services.email_service import email_service

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
    officeHours: Optional[str] = None
    emergencyContact: Optional[str] = None
    address: Optional[dict] = None
    branding: Optional[BrandingUpdate] = None
    newPassword: Optional[str] = None

class PatientCreate(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str
    phone: Optional[str] = None

class PatientUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    dateOfBirth: Optional[str] = None
    address: Optional[dict] = None
    emergencyContact: Optional[dict] = None
    # Delete action fields
    action: Optional[str] = None  # "deactivate" or "remove" for delete operations
    confirmDelete: Optional[bool] = None  # Confirmation flag for delete operations
    
    class Config:
        extra = "allow"  # Allow extra fields to pass through

class ProcedureAssignment(BaseModel):
    patientId: str
    procedureId: str
    procedureName: str
    performedDate: str  # ISO date string
    dentistName: str
    practiceNotes: Optional[str] = None
    customInstructions: Optional[List[str]] = None
    followUpDate: Optional[str] = None

class DentistCreate(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    phone: Optional[str] = None
    licenseNumber: Optional[str] = None
    specialties: Optional[List[str]] = []

class DentistUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    licenseNumber: Optional[str] = None
    specialties: Optional[List[str]] = None

class EmailPDFRequest(BaseModel):
    patientEmail: EmailStr
    procedureId: str
    procedureName: str
    assignmentId: Optional[str] = None

# Practice-Specific Procedure Override Models  
class ProcedureCustomization(BaseModel):
    name: Optional[str] = None
    overview: Optional[str] = None
    immediateAftercare: Optional[List[str]] = None
    dietRestrictions: Optional[List[str]] = None
    warningSignsToCallDoctor: Optional[List[str]] = None
    recoveryTimeline: Optional[List[Dict[str, str]]] = None
    medications: Optional[List[str]] = None

class PracticeProcedureOverride(BaseModel):
    practiceId: str
    procedureId: str  # References the global procedure ID
    name: str
    overview: str
    immediateAftercare: List[str]
    dietRestrictions: List[str]
    warningSignsToCallDoctor: List[str]
    recoveryTimeline: List[Dict[str, str]]
    medications: List[str]
    customizedAt: datetime
    customizedBy: str

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

@router.get("/debug-gmail-patients")
async def debug_gmail_patients(current_user: dict = Depends(get_current_user)):
    """Debug endpoint to check Gmail patients"""
    try:
        practice_id = current_user["practiceId"]
        
        # Get Gmail patients
        gmail_patients = await db.users.find(
            {
                "practiceId": practice_id,
                "role": "patient", 
                "email": {"$regex": "@gmail\\.com$"}
            }
        ).to_list(length=None)
        
        return {
            "success": True,
            "gmail_patients_count": len(gmail_patients),
            "gmail_patients": [
                {
                    "firstName": p["firstName"],
                    "lastName": p["lastName"], 
                    "email": p["email"]
                } for p in gmail_patients
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

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
        
        # Get only real patients (Gmail addresses only) - no test patients
        print("DEBUG: Looking for Gmail patients only")
        recent_patients = await db.users.find(
            {
                "practiceId": practice_id,
                "role": "patient",
                "email": {"$regex": "@gmail\\.com$"}  # Only Gmail addresses (real patients)
            },
            {
                "_id": 0,
                "id": 1,
                "firstName": 1,
                "lastName": 1,
                "email": 1,
                "createdAt": 1,
                "lastLoginAt": 1,
                "isActive": 1,
                "deactivatedAt": 1
            }
        ).sort("lastName", 1).to_list(length=None)  # Sort by last name
        
        print(f"DEBUG: Found {len(recent_patients)} Gmail patients")
        for patient in recent_patients:
            print(f"DEBUG: Patient {patient['firstName']} {patient['lastName']} ({patient['email']})")
        
        # Add status information to recent patients
        for patient in recent_patients:
            # Default to active if isActive field is not set
            is_active = patient.get("isActive")
            if is_active is None:
                is_active = True  # Default to active for existing patients without the field
            patient["status"] = "Active" if is_active else "Inactive"
        
        # Get recent procedures (last 10) with patient names
        recent_procedures = await db.patientprocedures.find(
            {"practiceId": practice_id},
            {"_id": 0}
        ).sort("performedDate", -1).limit(10).to_list(length=None)
        
        # Add patient names to recent procedures
        for procedure in recent_procedures:
            patient = await db.users.find_one(
                {
                    "id": procedure.get("patientId"),
                    "practiceId": practice_id,
                    "role": "patient"
                },
                {"firstName": 1, "lastName": 1, "isActive": 1, "_id": 0}
            )
            if patient:
                procedure["patientName"] = f"{patient['firstName']} {patient['lastName']}"
                procedure["patientStatus"] = "Active" if patient.get("isActive", True) else "Inactive"
            else:
                # Patient was permanently deleted
                procedure["patientName"] = "[Deleted Patient]"
                procedure["patientStatus"] = "Deleted"
        
        return {
            "success": True,
            "data": {
                "practice": practice,
                "stats": {
                    "patientCount": patient_count,
                    "activeProcedures": active_procedures,
                    "subscriptionStatus": practice.get("subscription", {}).get("status", "")
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
        
        # Get all active patients for this practice
        patients = await db.users.find(
            {
                "practiceId": practice_id,
                "role": "patient",
                "isActive": True
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
        
        # Remove password and _id from response (if present)
        response_doc = patient_doc.copy()
        response_doc.pop("password", None)
        response_doc.pop("_id", None)
        
        return {
            "success": True,
            "message": "Patient created successfully",
            "data": response_doc
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

@router.post("/request-procedure")
async def request_new_procedure(
    request_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Submit a request for a new procedure to be added"""
    try:
        practice_id = current_user["practiceId"]
        user_id = current_user["userId"]
        role = current_user["role"]
        
        if role not in ['practice_admin', 'practice_staff']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Create procedure request
        procedure_request = {
            "id": str(uuid.uuid4()),
            "practiceId": practice_id,
            "requestedBy": user_id,
            "requestedByName": f"{current_user.get('firstName', '')} {current_user.get('lastName', '')}".strip(),
            "practiceName": current_user.get('practiceName', ''),
            "procedureName": request_data.get("procedureName"),
            "specialty": request_data.get("specialty"),
            "description": request_data.get("description"),
            "reasonForRequest": request_data.get("reasonForRequest"),
            "urgencyLevel": request_data.get("urgencyLevel", "normal"),
            "status": "pending",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        # Store in database
        await db.procedure_requests.insert_one(procedure_request)
        
        return {
            "success": True,
            "message": "Procedure request submitted successfully",
            "requestId": procedure_request["id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Request procedure error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit procedure request"
        )

@router.get("/doctors")
async def get_practice_doctors(current_user: dict = Depends(get_current_user)):
    """Get all doctors/staff in the practice"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        
        if role not in ['practice_admin', 'practice_staff']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get all practice staff and admins
        doctors = await db.users.find(
            {
                "practiceId": practice_id,
                "role": {"$in": ["practice_admin", "practice_staff"]},
                "isActive": True
            },
            {
                "_id": 0,
                "id": 1,
                "firstName": 1,
                "lastName": 1,
                "role": 1
            }
        ).to_list(length=None)
        
        # Format doctor names
        doctor_list = []
        for doctor in doctors:
            # Remove existing Dr. prefix if present to avoid duplication
            first_name = doctor['firstName'].replace('Dr. ', '').replace('Dr.', '').strip()
            last_name = doctor['lastName']
            doctor_name = f"Dr. {first_name} {last_name}"
            doctor_list.append({
                "id": doctor["id"],
                "name": doctor_name,
                "role": doctor["role"]
            })
        
        return {
            "success": True,
            "data": doctor_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get doctors error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get practice doctors"
        )

@router.get("/assignment/{assignment_id}")
async def get_procedure_assignment(
    assignment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed procedure assignment with full procedure content"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        
        if role not in ['practice_admin', 'practice_staff']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get procedure assignment
        assignment = await db.patientprocedures.find_one(
            {
                "id": assignment_id,
                "practiceId": practice_id
            },
            {"_id": 0}
        )
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Procedure assignment not found"
            )
        
        # Get patient details
        patient = await db.users.find_one(
            {
                "id": assignment["patientId"],
                "practiceId": practice_id,
                "role": "patient"
            },
            {"_id": 0, "password": 0}
        )
        
        # Get full procedure details from procedures collection
        procedure = await db.procedures.find_one(
            {"name": assignment["procedureName"]},
            {"_id": 0}
        )
        
        if not procedure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Procedure details not found"
            )
        
        # Check for practice-specific customizations
        customization = await db.practice_procedure_customizations.find_one(
            {
                "practiceId": practice_id,
                "procedureId": procedure["id"],
                "isActive": True
            },
            {"_id": 0}
        )
        
        # Apply practice customizations if they exist
        if customization:
            print(f"🏥 Applying practice-specific customizations for {procedure['id']}")
            # Override global content with practice-specific content
            if customization.get("overview"):
                procedure["overview"] = customization["overview"]
            if customization.get("name"):
                procedure["name"] = customization["name"]
            if customization.get("immediateAftercare"):
                procedure["immediateAftercare"] = customization["immediateAftercare"]
            if customization.get("dietRestrictions"):
                procedure["dietRestrictions"] = customization["dietRestrictions"]
            if customization.get("warningSignsToCallDoctor"):
                procedure["warningSignsToCallDoctor"] = customization["warningSignsToCallDoctor"]
            if customization.get("recoveryTimeline"):
                procedure["recoveryTimeline"] = customization["recoveryTimeline"]
            if customization.get("medications"):
                procedure["medications"] = customization["medications"]
            
            # Add customization metadata
            procedure["isCustomized"] = True
            procedure["customizedAt"] = customization.get("customizedAt")
            procedure["customizedBy"] = customization.get("customizedBy")
        else:
            procedure["isCustomized"] = False
        
        # Combine assignment with full procedure details
        result = {
            "assignment": assignment,
            "patient": {
                "id": patient["id"],
                "firstName": patient["firstName"],
                "lastName": patient["lastName"],
                "email": patient["email"]
            } if patient else None,
            "procedure": procedure
        }
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get procedure assignment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get procedure assignment"
        )

@router.put("/assignment/{assignment_id}")
async def update_procedure_assignment(
    assignment_id: str,
    update_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update procedure assignment details"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        
        if role not in ['practice_admin', 'practice_staff']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Verify assignment belongs to this practice
        assignment = await db.patientprocedures.find_one({
            "id": assignment_id,
            "practiceId": practice_id
        })
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Procedure assignment not found"
            )
        
        # Build update document
        update_doc = {"updatedAt": datetime.utcnow()}
        
        # Update allowed fields
        allowed_fields = ['performedDate', 'followUpDate', 'dentistName', 'practiceNotes', 'customInstructions', 'status']
        for field in allowed_fields:
            if field in update_data:
                if field in ['performedDate', 'followUpDate'] and update_data[field]:
                    # Parse date strings
                    update_doc[field] = datetime.fromisoformat(update_data[field].replace('Z', '+00:00'))
                else:
                    update_doc[field] = update_data[field]
        
        # Update the assignment
        result = await db.patientprocedures.update_one(
            {"id": assignment_id},
            {"$set": update_doc}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Procedure assignment not found"
            )
        
        return {
            "success": True,
            "message": "Procedure assignment updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update procedure assignment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update procedure assignment"
        )

@router.get("/export-data")
async def get_export_data(current_user: dict = Depends(get_current_user)):
    """Get data for exporting (patients with their assigned procedures)"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        
        if role not in ['practice_admin', 'practice_staff']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get all patients with their assigned procedures
        patients_with_procedures = []
        
        # Get all patients for this practice
        patients = await db.users.find(
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
                "createdAt": 1
            }
        ).to_list(length=None)
        
        # For each patient, get their procedures
        for patient in patients:
            procedures = await db.patientprocedures.find(
                {
                    "practiceId": practice_id,
                    "patientId": patient["id"]
                },
                {"_id": 0}
            ).sort("performedDate", -1).to_list(length=None)
            
            # Get full procedure details for each assignment
            for proc_assignment in procedures:
                procedure_details = await db.procedures.find_one(
                    {"id": proc_assignment["procedureId"]},
                    {"_id": 0, "name": 1, "specialty": 1, "specialtyName": 1}
                )
                if procedure_details:
                    proc_assignment["procedureDetails"] = procedure_details
            
            patient["assignedProcedures"] = procedures
            patients_with_procedures.append(patient)
        
        return {
            "success": True,
            "data": {
                "patients": patients_with_procedures,
                "exportedAt": datetime.utcnow().isoformat(),
                "practiceId": practice_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Export data error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get export data"
        )

@router.put("/patients/{patient_id}")
async def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update patient information or handle delete operations"""
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
            "id": patient_id,
            "practiceId": practice_id,
            "role": "patient"
        })
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Handle delete operations FIRST
        print(f"DEBUG: Raw patient_data attributes: {dir(patient_data)}")
        print(f"DEBUG: patient_data dict: {patient_data.dict()}")
        if hasattr(patient_data, 'action') and patient_data.action in ["deactivate", "remove"] and hasattr(patient_data, 'confirmDelete') and patient_data.confirmDelete:
            # Check if patient has active procedure assignments
            active_procedures = await db.patientprocedures.count_documents({
                "patientId": patient_id,
                "practiceId": practice_id,
                "status": "active"
            })
            
            if patient_data.action == "remove":
                # Permanent removal
                if active_procedures > 0:
                    # For permanent removal, delete all procedure assignments
                    await db.patientprocedures.delete_many({
                        "patientId": patient_id,
                        "practiceId": practice_id
                    })
                
                # Completely remove patient from database
                result = await db.users.delete_one({
                    "id": patient_id,
                    "practiceId": practice_id,
                    "role": "patient"
                })
                
                if result.deleted_count == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Patient not found for removal"
                    )
                
                return {
                    "success": True,
                    "message": f"Patient {patient['firstName']} {patient['lastName']} has been permanently removed",
                    "deletedProcedures": active_procedures
                }
            else:
                # Deactivation (soft delete)
                result = await db.users.update_one(
                    {
                        "id": patient_id,
                        "practiceId": practice_id,
                        "role": "patient"
                    },
                    {"$set": {
                        "isActive": False,
                        "deactivatedAt": datetime.utcnow(),
                        "updatedAt": datetime.utcnow()
                    }}
                )
                
                if result.modified_count == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Patient not found for deactivation"
                    )
                
                return {
                    "success": True,
                    "message": f"Patient {patient['firstName']} {patient['lastName']} has been deactivated",
                    "activeProcedures": active_procedures,
                    "note": "Procedure assignments have been preserved"
                }
        
        # Regular patient update logic (only if no delete action)
        if hasattr(patient_data, 'action') and patient_data.action is not None and patient_data.action not in ["deactivate", "remove"]:
            # If action is provided but not a valid delete action, reject it
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action. Use 'deactivate' or 'remove' with confirmDelete=true for delete operations."
            )
        
        # Check if email is being updated and ensure it's unique
        if patient_data.email and patient_data.email != patient.get('email'):
            existing_email = await db.users.find_one({
                "email": patient_data.email,
                "id": {"$ne": patient_id}
            })
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email address already in use"
                )
        
        # Build update document with only provided fields (excluding delete action fields)
        update_data = {"updatedAt": datetime.utcnow()}
        
        if patient_data.firstName is not None:
            update_data["firstName"] = patient_data.firstName
        if patient_data.lastName is not None:
            update_data["lastName"] = patient_data.lastName
        if patient_data.email is not None:
            update_data["email"] = patient_data.email
        if patient_data.phone is not None:
            update_data["phone"] = patient_data.phone
        if patient_data.dateOfBirth is not None:
            update_data["dateOfBirth"] = patient_data.dateOfBirth
        if patient_data.address is not None:
            update_data["address"] = patient_data.address
        if patient_data.emergencyContact is not None:
            update_data["emergencyContact"] = patient_data.emergencyContact
        
        # Update patient in database
        result = await db.users.update_one(
            {
                "id": patient_id,
                "practiceId": practice_id,
                "role": "patient"
            },
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No changes made to patient record"
            )
        
        # Get updated patient data
        updated_patient = await db.users.find_one(
            {
                "id": patient_id,
                "practiceId": practice_id,
                "role": "patient"
            },
            {
                "_id": 0,
                "password": 0
            }
        )
        
        return {
            "success": True,
            "message": "Patient updated successfully",
            "data": updated_patient
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update patient error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update patient"
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
        if update_data.officeHours is not None:
            practice_update["officeHours"] = update_data.officeHours
        if update_data.emergencyContact is not None:
            practice_update["emergencyContact"] = update_data.emergencyContact
            
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

# Dentist Management Routes
@router.get("/dentists")
async def get_dentists(current_user: dict = Depends(get_current_user)):
    """Get all dentists for the practice"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        
        if role not in ['practice_admin', 'practice_staff']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get dentists for this practice
        dentists = await db.dentists.find(
            {
                "practiceId": practice_id,
                "isActive": True
            },
            {"_id": 0}
        ).to_list(length=None)
        
        return {
            "success": True,
            "data": dentists
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get dentists error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dentists"
        )

@router.post("/dentists")
async def add_dentist(
    dentist_data: DentistCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a new dentist to the practice"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        
        if role != 'practice_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only practice admins can add dentists"
            )
        
        # Check if email already exists for this practice
        existing_dentist = await db.dentists.find_one({
            "practiceId": practice_id,
            "email": dentist_data.email,
            "isActive": True
        })
        
        if existing_dentist:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A dentist with this email already exists in your practice"
            )
        
        # Create new dentist
        dentist_id = str(uuid.uuid4())
        new_dentist = {
            "id": dentist_id,
            "practiceId": practice_id,
            "firstName": dentist_data.firstName,
            "lastName": dentist_data.lastName,
            "email": dentist_data.email,
            "phone": dentist_data.phone,
            "licenseNumber": dentist_data.licenseNumber,
            "specialties": dentist_data.specialties or [],
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        await db.dentists.insert_one(new_dentist)
        
        # Return the created dentist (without _id)
        new_dentist.pop("_id", None)
        
        return {
            "success": True,
            "message": "Dentist added successfully",
            "data": new_dentist
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Add dentist error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add dentist"
        )

@router.put("/dentists/{dentist_id}")
async def update_dentist(
    dentist_id: str,
    dentist_data: DentistUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update dentist information"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        
        if role != 'practice_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only practice admins can update dentists"
            )
        
        # Verify dentist belongs to this practice
        dentist = await db.dentists.find_one({
            "id": dentist_id,
            "practiceId": practice_id,
            "isActive": True
        })
        
        if not dentist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dentist not found"
            )
        
        # Check if email is being updated and ensure it's unique
        if dentist_data.email and dentist_data.email != dentist.get('email'):
            existing_email = await db.dentists.find_one({
                "practiceId": practice_id,
                "email": dentist_data.email,
                "id": {"$ne": dentist_id},
                "isActive": True
            })
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A dentist with this email already exists in your practice"
                )
        
        # Build update document with only provided fields
        update_data = {"updatedAt": datetime.utcnow()}
        
        if dentist_data.firstName is not None:
            update_data["firstName"] = dentist_data.firstName
        if dentist_data.lastName is not None:
            update_data["lastName"] = dentist_data.lastName
        if dentist_data.email is not None:
            update_data["email"] = dentist_data.email
        if dentist_data.phone is not None:
            update_data["phone"] = dentist_data.phone
        if dentist_data.licenseNumber is not None:
            update_data["licenseNumber"] = dentist_data.licenseNumber
        if dentist_data.specialties is not None:
            update_data["specialties"] = dentist_data.specialties
        
        # Update dentist in database
        result = await db.dentists.update_one(
            {
                "id": dentist_id,
                "practiceId": practice_id,
                "isActive": True
            },
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No changes made to dentist record"
            )
        
        # Get updated dentist data
        updated_dentist = await db.dentists.find_one(
            {
                "id": dentist_id,
                "practiceId": practice_id,
                "isActive": True
            },
            {"_id": 0}
        )
        
        return {
            "success": True,
            "message": "Dentist updated successfully",
            "data": updated_dentist
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update dentist error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update dentist"
        )

@router.delete("/dentists/{dentist_id}")
async def remove_dentist(
    dentist_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove (deactivate) a dentist from the practice"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        
        if role != 'practice_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only practice admins can remove dentists"
            )
        
        # Verify dentist belongs to this practice
        dentist = await db.dentists.find_one({
            "id": dentist_id,
            "practiceId": practice_id,
            "isActive": True
        })
        
        if not dentist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dentist not found"
            )
        
        # Soft delete - set isActive to False
        await db.dentists.update_one(
            {
                "id": dentist_id,
                "practiceId": practice_id
            },
            {"$set": {
                "isActive": False,
                "updatedAt": datetime.utcnow()
            }}
        )
        
        return {
            "success": True,
            "message": "Dentist removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Remove dentist error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove dentist"
        )

@router.delete("/patients/{patient_id}")
async def delete_patient(
    patient_id: str,
    hard_delete: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Delete or deactivate a patient"""
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
            "id": patient_id,
            "practiceId": practice_id,
            "role": "patient"
        })
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Check if patient has active procedure assignments
        active_procedures = await db.patientprocedures.count_documents({
            "patientId": patient_id,
            "practiceId": practice_id,
            "status": "active"
        })
        
        if hard_delete:
            if active_procedures > 0:
                # For hard delete, we warn but allow deletion of assignments
                await db.patientprocedures.delete_many({
                    "patientId": patient_id,
                    "practiceId": practice_id
                })
            
            # Completely remove patient from database
            result = await db.users.delete_one({
                "id": patient_id,
                "practiceId": practice_id,
                "role": "patient"
            })
            
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found"
                )
            
            return {
                "success": True,
                "message": f"Patient {patient['firstName']} {patient['lastName']} has been permanently deleted",
                "deletedProcedures": active_procedures
            }
        else:
            # Soft delete - mark as inactive
            result = await db.users.update_one(
                {
                    "id": patient_id,
                    "practiceId": practice_id,
                    "role": "patient"
                },
                {"$set": {
                    "isActive": False,
                    "deactivatedAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found"
                )
            
            return {
                "success": True,
                "message": f"Patient {patient['firstName']} {patient['lastName']} has been deactivated",
                "activeProcedures": active_procedures,
                "note": "Procedure assignments have been preserved"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete patient error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete patient"
        )

@router.put("/patient-status/{patient_id}")
async def update_patient_status(
    patient_id: str,
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update patient status - supports deactivation and permanent removal"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        action = request.get("action", "deactivate")  # "deactivate" or "remove"
        
        if role not in ['practice_admin', 'practice_staff']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Verify patient belongs to this practice
        patient = await db.users.find_one({
            "id": patient_id,
            "practiceId": practice_id,
            "role": "patient"
        })
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Check if patient has active procedure assignments
        active_procedures = await db.patientprocedures.count_documents({
            "patientId": patient_id,
            "practiceId": practice_id,
            "status": "active"
        })
        
        if action == "remove":
            # Permanent removal
            if active_procedures > 0:
                # For permanent removal, delete all procedure assignments
                await db.patientprocedures.delete_many({
                    "patientId": patient_id,
                    "practiceId": practice_id
                })
            
            # Completely remove patient from database
            result = await db.users.delete_one({
                "id": patient_id,
                "practiceId": practice_id,
                "role": "patient"
            })
            
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found"
                )
            
            return {
                "success": True,
                "message": f"Patient {patient['firstName']} {patient['lastName']} has been permanently removed",
                "deletedProcedures": active_procedures
            }
        else:
            # Deactivation (soft delete)
            result = await db.users.update_one(
                {
                    "id": patient_id,
                    "practiceId": practice_id,
                    "role": "patient"
                },
                {"$set": {
                    "isActive": False,
                    "deactivatedAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found"
                )
            
            return {
                "success": True,
                "message": f"Patient {patient['firstName']} {patient['lastName']} has been deactivated",
                "activeProcedures": active_procedures,
                "note": "Procedure assignments have been preserved"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update patient status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update patient status"
        )

# ======= PRACTICE-SPECIFIC PROCEDURE OVERRIDE ENDPOINTS =======

@router.get("/procedures")
async def get_practice_procedures(current_user: dict = Depends(get_current_user)):
    """Get all procedures for this practice (global + practice-specific overrides)"""
    try:
        practice_id = current_user["practiceId"]
        
        # Get all global procedures
        global_procedures = await db.procedures.find({}, {"_id": 0}).to_list(length=None)
        
        # Get practice-specific overrides
        overrides = await db.practice_procedure_overrides.find(
            {"practiceId": practice_id}, 
            {"_id": 0}
        ).to_list(length=None)
        
        # Create a map of procedure overrides
        override_map = {override["procedureId"]: override for override in overrides}
        
        # Build final procedures list (overrides take precedence)
        final_procedures = []
        for global_proc in global_procedures:
            if global_proc["id"] in override_map:
                # Use practice-specific override
                override = override_map[global_proc["id"]]
                procedure = {
                    **global_proc,  # Start with global template
                    **{k: v for k, v in override.items() if k not in ["practiceId", "procedureId", "customizedAt", "customizedBy"]},
                    "isCustomized": True,
                    "customizedAt": override.get("customizedAt"),
                    "customizedBy": override.get("customizedBy")
                }
            else:
                # Use global procedure
                procedure = {
                    **global_proc,
                    "isCustomized": False
                }
            
            final_procedures.append(procedure)
        
        return {
            "success": True,
            "procedures": final_procedures,
            "global_count": len(global_procedures),
            "customized_count": len(overrides)
        }
        
    except Exception as e:
        print(f"Get practice procedures error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get practice procedures"
        )

@router.get("/procedures/{procedure_id}")
async def get_practice_procedure(
    procedure_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific procedure for this practice (with override if exists)"""
    try:
        practice_id = current_user["practiceId"]
        
        # Check for practice-specific override first
        override = await db.practice_procedure_overrides.find_one({
            "practiceId": practice_id,
            "procedureId": procedure_id
        }, {"_id": 0})
        
        if override:
            # Get global procedure for metadata
            global_proc = await db.procedures.find_one({"id": procedure_id}, {"_id": 0})
            if not global_proc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Global procedure not found"
                )
            
            # Merge override with global metadata
            procedure = {
                **global_proc,
                **{k: v for k, v in override.items() if k not in ["practiceId", "procedureId", "customizedAt", "customizedBy"]},
                "isCustomized": True,
                "customizedAt": override.get("customizedAt"),
                "customizedBy": override.get("customizedBy")
            }
        else:
            # Use global procedure
            procedure = await db.procedures.find_one({"id": procedure_id}, {"_id": 0})
            if not procedure:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Procedure not found"
                )
            procedure["isCustomized"] = False
        
        return {
            "success": True,
            "data": procedure
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get practice procedure error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get practice procedure"
        )

@router.post("/procedures/{procedure_id}/customize")
async def customize_procedure(
    procedure_id: str,
    customization: ProcedureCustomization,
    current_user: dict = Depends(get_current_user)
):
    """Create or update practice-specific customization of a global procedure"""
    try:
        print(f"🔧 DEBUG: Starting customization for procedure_id: {procedure_id}")
        print(f"🔧 DEBUG: Current user: {current_user}")
        print(f"🔧 DEBUG: Customization data: {customization}")
        
        practice_id = current_user["practiceId"]
        user_email = current_user["user"]["email"]
        role = current_user["role"]
        
        print(f"🔧 DEBUG: Extracted - practice_id: {practice_id}, role: {role}")
        
    except Exception as e:
        print(f"❌ DEBUG: Error in user extraction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User extraction error: {str(e)}"
        )
    
    try:
        
        if role != 'practice_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only practice admins can customize procedures"
            )
        
        # Verify global procedure exists
        global_proc = await db.procedures.find_one({"id": procedure_id}, {"_id": 0})
        if not global_proc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Global procedure not found"
            )
        
        # Check if customization already exists
        existing_customization = await db.practice_procedure_customizations.find_one({
            "practiceId": practice_id,
            "procedureId": procedure_id
        })
        
        if existing_customization:
            # Update existing customization
            update_data = {"customizedAt": datetime.now(timezone.utc), "customizedBy": user_email, "isActive": True}
            
            # Only update provided fields
            if hasattr(customization, 'name') and customization.name is not None:
                update_data["name"] = customization.name
            if hasattr(customization, 'overview') and customization.overview is not None:
                update_data["overview"] = customization.overview
            if hasattr(customization, 'immediateAftercare') and customization.immediateAftercare is not None:
                update_data["immediateAftercare"] = customization.immediateAftercare
            if hasattr(customization, 'dietRestrictions') and customization.dietRestrictions is not None:
                update_data["dietRestrictions"] = customization.dietRestrictions
            if hasattr(customization, 'warningSignsToCallDoctor') and customization.warningSignsToCallDoctor is not None:
                update_data["warningSignsToCallDoctor"] = customization.warningSignsToCallDoctor
            if hasattr(customization, 'recoveryTimeline') and customization.recoveryTimeline is not None:
                update_data["recoveryTimeline"] = customization.recoveryTimeline
            if hasattr(customization, 'medications') and customization.medications is not None:
                update_data["medications"] = customization.medications
            
            await db.practice_procedure_customizations.update_one(
                {"practiceId": practice_id, "procedureId": procedure_id},
                {"$set": update_data}
            )
            
            action = "updated"
        else:
            # Create new customization based on global procedure
            customization_data = {
                "practiceId": practice_id,
                "procedureId": procedure_id,
                "name": getattr(customization, 'name', None) or global_proc["name"],
                "overview": getattr(customization, 'overview', None) or global_proc["overview"],
                "immediateAftercare": getattr(customization, 'immediateAftercare', None) or global_proc.get("immediateAftercare", []),
                "dietRestrictions": getattr(customization, 'dietRestrictions', None) or global_proc.get("dietRestrictions", []),
                "warningSignsToCallDoctor": getattr(customization, 'warningSignsToCallDoctor', None) or global_proc.get("warningSignsToCallDoctor", []),
                "recoveryTimeline": getattr(customization, 'recoveryTimeline', None) or global_proc.get("recoveryTimeline", []),
                "medications": getattr(customization, 'medications', None) or global_proc.get("medications", []),
                "customizedAt": datetime.now(timezone.utc),
                "customizedBy": user_email,
                "isActive": True,
                "originalOverview": global_proc["overview"]  # Backup of original
            }
            
            await db.practice_procedure_customizations.insert_one(customization_data)
            action = "created"
        
        return {
            "success": True,
            "message": f"Procedure customization {action} successfully",
            "procedure_id": procedure_id,
            "practice_id": practice_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Customize procedure error: {e}")
        print(f"❌ Error type: {type(e)}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to customize procedure: {str(e)}"
        )

@router.delete("/procedures/{procedure_id}/customize")
async def remove_procedure_customization(
    procedure_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove practice-specific customization and revert to global procedure"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        
        if role != 'practice_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only practice admins can remove customizations"
            )
        
        # Verify customization exists
        customization = await db.practice_procedure_customizations.find_one({
            "practiceId": practice_id,
            "procedureId": procedure_id
        })
        
        if not customization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No customization found for this procedure"
            )
        
        # Remove the customization
        await db.practice_procedure_customizations.delete_one({
            "practiceId": practice_id,
            "procedureId": procedure_id
        })
        
        return {
            "success": True,
            "message": "Procedure customization removed - reverted to global template",
            "procedure_id": procedure_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Remove customization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove procedure customization"
        )

@router.post("/email-pdf")
async def email_pdf_to_patient(
    email_request: EmailPDFRequest,
    current_user: dict = Depends(get_current_user)
):
    """Email PDF of procedure instructions to patient"""
    try:
        practice_id = current_user["practiceId"]
        role = current_user["role"]
        
        if role not in ['practice_admin', 'practice_staff']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get practice information for email template
        practice = await db.practices.find_one(
            {"id": practice_id},
            {"_id": 0, "name": 1, "phone": 1, "emergencyContact": 1, "officeHours": 1}
        )
        
        if not practice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found"
            )
        
        # Get procedure details
        procedure = await db.procedures.find_one(
            {"id": email_request.procedureId},
            {"_id": 0}
        )
        
        if not procedure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Procedure not found"
            )
        
        # Generate PDF content (using the same logic as frontend PDF generation)
        from ..utils.pdf_generator import generate_pdf_content
        
        pdf_content = generate_pdf_content(
            procedure_name=email_request.procedureName,
            procedure_data=procedure,
            practice_info=practice
        )
        
        # Send email with PDF attachment
        from ..services.email_service import email_service
        
        success = email_service.send_pdf_email(
            patient_email=email_request.patientEmail,
            pdf_content=pdf_content,
            procedure_name=email_request.procedureName,
            practice_info=practice
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email"
            )
        
        return {
            "success": True,
            "message": f"PDF instructions for {email_request.procedureName} sent successfully to {email_request.patientEmail}",
            "patientEmail": email_request.patientEmail,
            "procedureName": email_request.procedureName
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Email PDF error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send PDF email"
        )