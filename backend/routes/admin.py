from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr, Field
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
from typing import Optional, List, Dict
import os
import bcrypt
import jwt
from datetime import datetime, timedelta
import uuid
from typing import Any
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

router = APIRouter(prefix="/api/admin", tags=["admin"])
security = HTTPBearer()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

JWT_SECRET = os.environ.get('JWT_SECRET', 'your-super-secret-jwt-key-change-in-production')

# Super admin credentials
SUPER_ADMIN_EMAIL = "cganz@admin.com"
SUPER_ADMIN_PASSWORD = "Dentist1#"

# Pydantic models
class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

class PracticeManagementRequest(BaseModel):
    practice_id: str
    action: str  # 'activate', 'deactivate', 'cancel_subscription', 'extend_trial'
    reason: Optional[str] = None

class CreatePracticeRequest(BaseModel):
    practiceName: str = Field(..., min_length=1, description="Practice name is required")
    adminEmail: EmailStr = Field(..., description="Admin email is required")
    adminFirstName: str = Field(..., min_length=1, description="Admin first name is required")
    adminLastName: str = Field(..., min_length=1, description="Admin last name is required")
    phone: Optional[str] = None
    address: Optional[str] = None
    tempPassword: str = Field(..., min_length=8, description="Temporary password is required (min 8 chars)")
    subscriptionType: str = Field(default="trial", description="trial, active, or inactive")
    trialDays: int = Field(default=30, description="Trial period in days")

class PasswordResetRequest(BaseModel):
    user_id: str
    new_password: str

# Global Procedure Management Models
class GlobalProcedureCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Procedure name cannot be empty")
    specialty: str = Field(..., min_length=1, description="Specialty cannot be empty")
    specialtyName: str = Field(..., min_length=1, description="Specialty name cannot be empty")
    duration: str = Field(..., min_length=1, description="Duration cannot be empty")
    overview: str = Field(..., min_length=1, description="Overview cannot be empty")
    immediateAftercare: List[str]
    dietRestrictions: List[str]
    warningSignsToCallDoctor: List[str]
    recoveryTimeline: Optional[str] = None  # Made optional and changed to string
    medications: List[str]

class GlobalProcedureUpdate(BaseModel):
    name: Optional[str] = None
    specialty: Optional[str] = None
    specialtyName: Optional[str] = None
    duration: Optional[str] = None
    overview: Optional[str] = None
    immediateAftercare: Optional[List[str]] = None
    dietRestrictions: Optional[List[str]] = None
    warningSignsToCallDoctor: Optional[List[str]] = None
    recoveryTimeline: Optional[List[Dict[str, str]]] = None
    medications: Optional[List[str]] = None

class ProcedureDeploymentRequest(BaseModel):
    procedure_ids: List[str]
    deployment_type: str  # 'all_practices', 'specific_practices', 'trial_only', 'active_only'
    practice_ids: Optional[List[str]] = None

class PracticeStats(BaseModel):
    total_practices: int
    active_practices: int
    trial_practices: int
    cancelled_practices: int
    total_revenue: float
    monthly_revenue: float

# Helper functions
def verify_super_admin(email: str, password: str) -> bool:
    """Verify super admin credentials"""
    return (email.lower() == SUPER_ADMIN_EMAIL.lower() and 
            password == SUPER_ADMIN_PASSWORD)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def generate_admin_token(admin_email: str) -> str:
    payload = {
        'adminEmail': admin_email,
        'role': 'super_admin',
        'exp': datetime.utcnow() + timedelta(hours=8),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        
        if payload.get('role') != 'super_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token"
        )

# Admin routes
@router.post("/login")
async def admin_login(request: AdminLoginRequest):
    """Super admin login"""
    try:
        print(f"Admin login attempt: email={request.email}")
        print(f"Expected email: {SUPER_ADMIN_EMAIL}")
        print(f"Expected password: {SUPER_ADMIN_PASSWORD}")
        print(f"Received password: {request.password}")
        
        if not verify_super_admin(request.email, request.password):
            print("Admin credentials verification failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin credentials"
            )
        
        print("Admin credentials verified, generating token...")
        token = generate_admin_token(request.email)
        print(f"Token generated successfully: {token[:20]}...")
        
        return {
            "success": True,
            "token": token,
            "message": "Admin login successful"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Admin login error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin login failed"
        )

@router.get("/dashboard")
async def get_admin_dashboard(admin_data = Depends(verify_admin_token)):
    """Get admin dashboard overview"""
    try:
        # Get practice statistics
        total_practices = await db.practices.count_documents({})
        active_practices = await db.practices.count_documents({"subscription.status": "active"})
        trial_practices = await db.practices.count_documents({"subscription.status": "trial"})
        cancelled_practices = await db.practices.count_documents({"subscription.status": "cancelled"})
        
        # Calculate revenue from paid transactions
        pipeline = [
            {"$match": {"payment_status": "paid"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        revenue_result = await db.payment_transactions.aggregate(pipeline).to_list(1)
        total_revenue = revenue_result[0]["total"] if revenue_result else 0.0
        
        # Monthly revenue (current month)
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_pipeline = [
            {"$match": {
                "payment_status": "paid",
                "created_at": {"$gte": start_of_month}
            }},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        monthly_result = await db.payment_transactions.aggregate(monthly_pipeline).to_list(1)
        monthly_revenue = monthly_result[0]["total"] if monthly_result else 0.0
        
        # Get recent practices
        recent_practices = await db.practices.find(
            {},
            {"_id": 0, "password": 0}
        ).sort("createdAt", -1).limit(10).to_list(10)
        
        # Get trial expiring soon
        expiring_soon = datetime.utcnow() + timedelta(days=3)
        expiring_trials = await db.practices.find(
            {
                "subscription.status": "trial",
                "subscription.trialEndsAt": {"$lte": expiring_soon}
            },
            {"_id": 0}
        ).to_list(20)
        
        return {
            "success": True,
            "stats": {
                "total_practices": total_practices,
                "active_practices": active_practices,
                "trial_practices": trial_practices,
                "cancelled_practices": cancelled_practices,
                "total_revenue": total_revenue,
                "monthly_revenue": monthly_revenue
            },
            "recent_practices": recent_practices,
            "expiring_trials": expiring_trials
        }
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load dashboard"
        )

@router.get("/practices")
async def get_all_practices(
    admin_data = Depends(verify_admin_token),
    status_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get all practices with filtering and pagination"""
    try:
        # Build query
        query = {}
        if status_filter:
            query["subscription.status"] = status_filter
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
        
        # Get total count
        total = await db.practices.count_documents(query)
        
        # Get practices with pagination
        skip = (page - 1) * limit
        practices = await db.practices.find(
            query,
            {"_id": 0}
        ).sort("createdAt", -1).skip(skip).limit(limit).to_list(limit)
        
        # Add user info for each practice
        for practice in practices:
            admin_user = await db.users.find_one(
                {"practiceId": practice["id"], "role": "practice_admin"},
                {"_id": 0, "password": 0}
            )
            practice["admin_user"] = admin_user
            
            # Get payment transactions
            transactions = await db.payment_transactions.find(
                {"practice_id": practice["id"]},
                {"_id": 0}
            ).sort("created_at", -1).limit(5).to_list(5)
            practice["recent_transactions"] = transactions
        
        return {
            "success": True,
            "practices": practices,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        print(f"Get practices error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get practices"
        )

@router.post("/manage-practice")
async def manage_practice(
    request: PracticeManagementRequest,
    admin_data = Depends(verify_admin_token)
):
    """Manage practice subscription and status"""
    try:
        practice = await db.practices.find_one({"id": request.practice_id})
        if not practice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found"
            )
        
        updates = {"updatedAt": datetime.utcnow()}
        
        if request.action == "activate":
            updates["subscription.status"] = "active"
            updates["isActive"] = True
            
        elif request.action == "deactivate":
            updates["subscription.status"] = "inactive"
            updates["isActive"] = False
            
        elif request.action == "cancel_subscription":
            updates["subscription.status"] = "cancelled"
            updates["isActive"] = False
            
        elif request.action == "extend_trial":
            new_end_date = datetime.utcnow() + timedelta(days=15)
            updates["subscription.trialEndsAt"] = new_end_date
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action"
            )
        
        # Update practice
        await db.practices.update_one(
            {"id": request.practice_id},
            {"$set": updates}
        )
        
        # Log admin action (create admin_actions collection)
        admin_action = {
            "id": str(uuid.uuid4()),
            "admin_email": admin_data["adminEmail"],
            "practice_id": request.practice_id,
            "action": request.action,
            "reason": request.reason,
            "timestamp": datetime.utcnow()
        }
        await db.admin_actions.insert_one(admin_action)
        
        return {
            "success": True,
            "message": f"Practice {request.action} completed",
            "practice_id": request.practice_id
        }
        
    except Exception as e:
        print(f"Manage practice error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to manage practice"
        )

@router.post("/create-practice")
async def create_practice(
    request: CreatePracticeRequest,
    admin_data = Depends(verify_admin_token)
):
    """Create a new dental practice with admin user"""
    try:
        # Check if email already exists
        existing_user = await db.users.find_one({"email": request.adminEmail})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists"
            )
        
        # Check if practice name already exists
        existing_practice = await db.practices.find_one({"name": request.practiceName})
        if existing_practice:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A practice with this name already exists"
            )
        
        # Generate unique IDs
        practice_id = str(uuid.uuid4())
        admin_user_id = str(uuid.uuid4())
        
        # Hash password
        hashed_password = hash_password(request.tempPassword)
        
        # Set trial/subscription details
        created_at = datetime.utcnow()
        subscription_data = {
            "plan": request.subscriptionType,
            "status": request.subscriptionType,
            "createdAt": created_at,
            "updatedAt": created_at
        }
        
        if request.subscriptionType == "trial":
            subscription_data["trialStartedAt"] = created_at
            subscription_data["trialEndsAt"] = created_at + timedelta(days=request.trialDays)
        
        # Create practice document
        practice_doc = {
            "id": practice_id,
            "name": request.practiceName,
            "email": request.adminEmail,
            "phone": request.phone or "",
            "address": request.address or "",
            "isActive": request.subscriptionType in ["trial", "active"],
            "subscription": subscription_data,
            "branding": {
                "logo": None,
                "colors": {
                    "primary": "#2563eb",
                    "secondary": "#64748b"
                }
            },
            "createdAt": created_at,
            "updatedAt": created_at,
            "createdBy": admin_data["adminEmail"]
        }
        
        # Create admin user document
        admin_user_doc = {
            "id": admin_user_id,
            "email": request.adminEmail,
            "password": hashed_password,
            "firstName": request.adminFirstName,
            "lastName": request.adminLastName,
            "role": "practice_admin",
            "practiceId": practice_id,
            "specialties": [],
            "isActive": True,
            "createdAt": created_at,
            "updatedAt": created_at,
            "createdBy": admin_data["adminEmail"]
        }
        
        # Insert both documents
        await db.practices.insert_one(practice_doc)
        await db.users.insert_one(admin_user_doc)
        
        # Log admin action
        admin_action = {
            "id": str(uuid.uuid4()),
            "admin_email": admin_data["adminEmail"],
            "action": "create_practice",
            "practice_id": practice_id,
            "practice_name": request.practiceName,
            "admin_user_id": admin_user_id,
            "admin_user_email": request.adminEmail,
            "subscription_type": request.subscriptionType,
            "timestamp": datetime.utcnow()
        }
        await db.admin_actions.insert_one(admin_action)
        
        return {
            "success": True,
            "message": f"Practice '{request.practiceName}' created successfully",
            "practice": {
                "id": practice_id,
                "name": request.practiceName,
                "email": request.adminEmail,
                "subscription_type": request.subscriptionType,
                "admin_user": {
                    "id": admin_user_id,
                    "name": f"{request.adminFirstName} {request.adminLastName}",
                    "email": request.adminEmail
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Create practice error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create practice"
        )

# Debug endpoint removed for production

@router.post("/send-welcome-email")
async def send_welcome_email(
    request: dict,
    admin_data = Depends(verify_admin_token)
):
    """Send welcome email to a practice with login credentials"""
    try:
        from ..services.email_service import email_service
        
        # Validate required fields
        if not request.get('practiceData') or not request.get('adminCredentials'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Practice data and admin credentials are required"
            )
        
        practice_data = request['practiceData']
        admin_credentials = request['adminCredentials']
        app_url = request.get('appUrl', 'https://dental-admin-3.preview.emergentagent.com')
        
        # Send welcome email
        success = email_service.send_welcome_email(
            practice_data=practice_data,
            admin_credentials=admin_credentials,
            app_url=app_url
        )
        
        if success:
            # Log admin action
            admin_action = {
                "id": str(uuid.uuid4()),
                "admin_email": admin_data["adminEmail"],
                "action": "send_welcome_email",
                "practice_name": practice_data.get('practiceName'),
                "recipient_email": admin_credentials.get('adminEmail'),
                "timestamp": datetime.utcnow()
            }
            await db.admin_actions.insert_one(admin_action)
            
            return {
                "success": True,
                "message": f"Welcome email sent successfully to {admin_credentials.get('adminEmail')}"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send welcome email"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Send welcome email error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug: Failed to send welcome email: {str(e)}"
        )

@router.post("/reset-password")
async def reset_user_password(
    request: PasswordResetRequest,
    admin_data = Depends(verify_admin_token)
):
    """Reset a user's password"""
    try:
        # Find user
        user = await db.users.find_one({"id": request.user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        hashed_password = hash_password(request.new_password)
        await db.users.update_one(
            {"id": request.user_id},
            {
                "$set": {
                    "password": hashed_password,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        # Log admin action
        admin_action = {
            "id": str(uuid.uuid4()),
            "admin_email": admin_data["adminEmail"],
            "user_id": request.user_id,
            "action": "password_reset",
            "timestamp": datetime.utcnow()
        }
        await db.admin_actions.insert_one(admin_action)
        
        return {
            "success": True,
            "message": "Password reset successfully"
        }
        
    except Exception as e:
        print(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )

@router.get("/users/{practice_id}")
async def get_practice_users(
    practice_id: str,
    admin_data = Depends(verify_admin_token)
):
    """Get all users for a specific practice"""
    try:
        users = await db.users.find(
            {"practiceId": practice_id},
            {"_id": 0, "password": 0}
        ).to_list(100)
        
        return {
            "success": True,
            "users": users
        }
        
    except Exception as e:
        print(f"Get practice users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get practice users"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_data = Depends(verify_admin_token)
):
    """Delete a user from the system"""
    try:
        # Check if user exists
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user has any active procedure assignments as a dentist
        active_assignments = await db.patientprocedures.count_documents({
            "dentistId": user_id,
            "status": "active"
        })
        
        if active_assignments > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete user. They have {active_assignments} active procedure assignments."
            )
        
        # Delete the user
        result = await db.users.delete_one({"id": user_id})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Log admin action
        admin_action = {
            "id": str(uuid.uuid4()),
            "admin_email": admin_data["adminEmail"],
            "action": "delete_user",
            "user_id": user_id,
            "user_name": f"{user.get('firstName', '')} {user.get('lastName', '')}",
            "user_email": user.get('email', ''),
            "practice_id": user.get('practiceId', ''),
            "timestamp": datetime.utcnow()
        }
        await db.admin_actions.insert_one(admin_action)
        
        return {
            "success": True,
            "message": "User deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

@router.delete("/practices/{practice_id}")
async def delete_practice(
    practice_id: str,
    admin_data = Depends(verify_admin_token)
):
    """Permanently delete a practice and all associated data"""
    try:
        # Check if practice exists
        practice = await db.practices.find_one({"id": practice_id})
        if not practice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found"
            )
        
        practice_name = practice.get("name", "Unknown Practice")
        
        # Get counts for logging
        user_count = await db.users.count_documents({"practiceId": practice_id})
        patient_count = await db.patients.count_documents({"practiceId": practice_id})
        procedure_count = await db.patientprocedures.count_documents({"practiceId": practice_id})
        
        # Delete all associated data
        # 1. Delete all users for this practice
        await db.users.delete_many({"practiceId": practice_id})
        
        # 2. Delete all patients for this practice
        await db.patients.delete_many({"practiceId": practice_id})
        
        # 3. Delete all patient procedures for this practice
        await db.patientprocedures.delete_many({"practiceId": practice_id})
        
        # 4. Delete any procedure requests for this practice
        await db.procedure_requests.delete_many({"practiceId": practice_id})
        
        # 5. Delete any payment transactions for this practice
        await db.payment_transactions.delete_many({"practice_id": practice_id})
        
        # 6. Finally, delete the practice itself
        result = await db.practices.delete_one({"id": practice_id})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Practice not found"
            )
        
        # Log admin action with detailed information
        admin_action = {
            "id": str(uuid.uuid4()),
            "admin_email": admin_data["adminEmail"],
            "action": "delete_practice",
            "practice_id": practice_id,
            "practice_name": practice_name,
            "practice_email": practice.get("email", ""),
            "deleted_data": {
                "users": user_count,
                "patients": patient_count,
                "procedures": procedure_count
            },
            "timestamp": datetime.utcnow()
        }
        await db.admin_actions.insert_one(admin_action)
        
        return {
            "success": True,
            "message": f"Practice '{practice_name}' and all associated data has been permanently deleted",
            "deleted_data": {
                "practice": 1,
                "users": user_count,
                "patients": patient_count,
                "procedures": procedure_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete practice error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete practice"
        )

@router.get("/monitoring")
async def get_monitoring_data(admin_data = Depends(verify_admin_token)):
    """Get system monitoring data with actual statistics"""
    try:
        # Get practice statistics
        total_practices = await db.practices.count_documents({})
        active_practices = await db.practices.count_documents({"subscription.status": "active"})
        
        # Get user statistics
        total_users = await db.users.count_documents({})
        practice_admins = await db.users.count_documents({"role": "practice_admin"})
        patients = await db.patients.count_documents({})
        
        # Get procedure statistics
        total_procedures_assigned = await db.patient_procedures.count_documents({})
        completed_procedures = await db.patient_procedures.count_documents({"status": "completed"})
        active_procedures = await db.patient_procedures.count_documents({"status": "active"})
        
        # Get procedure requests statistics
        total_requests = await db.procedure_requests.count_documents({})
        pending_requests = await db.procedure_requests.count_documents({"status": "pending"})
        approved_requests = await db.procedure_requests.count_documents({"status": "approved"})
        
        # Get recent activity (last 7 days)
        from datetime import datetime, timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        recent_practices = await db.practices.count_documents({
            "createdAt": {"$gte": seven_days_ago}
        })
        
        recent_procedures = await db.patient_procedures.count_documents({
            "createdAt": {"$gte": seven_days_ago}
        })
        
        # Get most active practice
        pipeline = [
            {"$group": {
                "_id": "$practiceId",
                "procedure_count": {"$sum": 1}
            }},
            {"$sort": {"procedure_count": -1}},
            {"$limit": 1}
        ]
        most_active_result = await db.patient_procedures.aggregate(pipeline).to_list(1)
        most_active_practice = None
        
        if most_active_result:
            practice_id = most_active_result[0]["_id"]
            practice = await db.practices.find_one({"id": practice_id})
            if practice:
                most_active_practice = {
                    "name": practice["name"],
                    "procedure_count": most_active_result[0]["procedure_count"]
                }
        
        # Get practices with recent activity
        practices_with_activity = await db.practices.find(
            {},
            {"_id": 0, "id": 1, "name": 1, "email": 1, "createdAt": 1, "updatedAt": 1}
        ).sort("updatedAt", -1).limit(20).to_list(20)
        
        # Add patient and procedure counts for each practice
        for practice in practices_with_activity:
            # Get patient count
            patient_count = await db.patients.count_documents({"practiceId": practice["id"]})
            practice["patient_count"] = patient_count
            
            # Get procedure count
            procedure_count = await db.patient_procedures.count_documents({"practiceId": practice["id"]})
            practice["procedure_count"] = procedure_count
            
            # Get user count
            user_count = await db.users.count_documents({"practiceId": practice["id"]})
            practice["user_count"] = user_count
        
        return {
            "success": True,
            "system_stats": {
                "total_practices": total_practices,
                "active_practices": active_practices,
                "total_users": total_users,
                "practice_admins": practice_admins,
                "total_patients": patients,
                "total_procedures_assigned": total_procedures_assigned,
                "completed_procedures": completed_procedures,
                "active_procedures": active_procedures,
                "total_requests": total_requests,
                "pending_requests": pending_requests,
                "approved_requests": approved_requests,
                "recent_practices_7days": recent_practices,
                "recent_procedures_7days": recent_procedures,
                "most_active_practice": most_active_practice
            },
            "practices_activity": practices_with_activity
        }
        
    except Exception as e:
        print(f"Monitoring data error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load monitoring data"
        )

@router.get("/payments")
async def get_all_payments(
    admin_data = Depends(verify_admin_token),
    practice_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    """Get all payment transactions"""
    try:
        # Build query
        query = {}
        if practice_id:
            query["practice_id"] = practice_id
        if status_filter:
            query["payment_status"] = status_filter
        
        # Get total count
        total = await db.payment_transactions.count_documents(query)
        
        # Get transactions with pagination
        skip = (page - 1) * limit
        transactions = await db.payment_transactions.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        # Add practice info for each transaction
        for transaction in transactions:
            if transaction.get("practice_id"):
                practice = await db.practices.find_one(
                    {"id": transaction["practice_id"]},
                    {"_id": 0, "name": 1, "email": 1}
                )
                transaction["practice"] = practice
        
        return {
            "success": True,
            "transactions": transactions,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        print(f"Get payments error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payments"
        )

@router.get("/dashboard-html", response_class=HTMLResponse)
async def get_admin_dashboard_html():
    """Serve the complete HTML admin dashboard"""
    try:
        admin_html_path = Path(__file__).parent.parent.parent / "admin-dashboard.html"
        if admin_html_path.exists():
            return admin_html_path.read_text()
        else:
            raise HTTPException(status_code=404, detail="Admin dashboard HTML not found")
    except Exception as e:
        print(f"Admin dashboard HTML error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load admin dashboard HTML")

@router.get("/guide-pdf")
async def get_admin_guide_pdf():
    """Serve the admin guide PDF"""
    try:
        from fastapi.responses import FileResponse
        pdf_path = Path(__file__).parent.parent.parent / "Practice_Notes_Admin_Guide.pdf"
        if pdf_path.exists():
            return FileResponse(
                path=str(pdf_path),
                media_type='application/pdf',
                filename="Practice_Notes_Admin_Guide.pdf"
            )
        else:
            raise HTTPException(status_code=404, detail="Admin guide PDF not found")
    except Exception as e:
        print(f"Admin guide PDF error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load admin guide PDF")

@router.get("/registration-attempts")
async def get_registration_attempts(
    admin_data = Depends(verify_admin_token),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    """Get all registration attempts for admin review"""
    try:
        # Get total count
        total = await db.registration_attempts.count_documents({})
        
        # Get registration attempts with pagination
        skip = (page - 1) * limit
        attempts = await db.registration_attempts.find(
            {},
            {"_id": 0}
        ).sort("attempted_at", -1).skip(skip).limit(limit).to_list(limit)
        
        return {
            "success": True,
            "data": attempts,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        print(f"Get registration attempts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get registration attempts"
        )

@router.get("/procedure-requests")
async def get_procedure_requests(admin_data = Depends(verify_admin_token)):
    """Get all procedure requests for admin review"""
    try:
        # Get all procedure requests, newest first
        requests = await db.procedure_requests.find(
            {},
            {"_id": 0}
        ).sort("createdAt", -1).to_list(length=None)
        
        return {
            "success": True,
            "data": requests
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get procedure requests error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get procedure requests"
        )

@router.put("/procedure-requests/{request_id}")
async def update_procedure_request_status(
    request_id: str,
    update_data: dict,
    admin_data = Depends(verify_admin_token)
):
    """Update procedure request status (approve, reject, in-progress)"""
    try:
        # Update the request
        result = await db.procedure_requests.update_one(
            {"id": request_id},
            {
                "$set": {
                    "status": update_data.get("status"),
                    "adminNotes": update_data.get("adminNotes"),
                    "reviewedBy": admin_data.get("adminEmail", ""),
                    "reviewedAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Procedure request not found"
            )
        
        return {
            "success": True,
            "message": "Procedure request updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update procedure request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update procedure request"
        )

# ======= GLOBAL PROCEDURE MANAGEMENT ENDPOINTS =======

@router.get("/procedures")
async def get_all_procedures(admin_data = Depends(verify_admin_token)):
    """Get all procedures in the system for admin management"""
    try:
        procedures = await db.procedures.find(
            {},
            {"_id": 0}
        ).sort("specialtyName", 1).to_list(length=None)
        
        # Get specialties for organization
        specialties = await db.specialties.find(
            {},
            {"_id": 0}
        ).sort("name", 1).to_list(length=None)
        
        return {
            "success": True,
            "procedures": procedures,
            "specialties": specialties,
            "total_count": len(procedures)
        }
        
    except Exception as e:
        print(f"Get procedures error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get procedures"
        )

@router.post("/procedures")
async def create_global_procedure(
    procedure: GlobalProcedureCreate,
    admin_data = Depends(verify_admin_token)
):
    """Create a new global procedure"""
    try:
        # Generate unique ID from name
        procedure_id = procedure.name.lower().replace(' ', '-').replace('--', '-')
        procedure_id = ''.join(c for c in procedure_id if c.isalnum() or c == '-')
        
        # Check if procedure already exists
        existing = await db.procedures.find_one({"id": procedure_id})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Procedure with name '{procedure.name}' already exists"
            )
        
        # Create procedure document
        procedure_doc = {
            "id": procedure_id,
            "name": procedure.name,
            "specialty": procedure.specialty,
            "specialtyName": procedure.specialtyName,
            "duration": procedure.duration,
            "overview": procedure.overview,
            "immediateAftercare": procedure.immediateAftercare,
            "dietRestrictions": procedure.dietRestrictions,
            "warningSignsToCallDoctor": procedure.warningSignsToCallDoctor,
            "recoveryTimeline": procedure.recoveryTimeline,
            "medications": procedure.medications,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "createdBy": admin_data["adminEmail"]
        }
        
        # Insert procedure
        await db.procedures.insert_one(procedure_doc)
        
        # Update specialty count if it exists
        await db.specialties.update_one(
            {"id": procedure.specialty},
            {"$inc": {"procedureCount": 1}},
            upsert=False
        )
        
        # Log admin action
        admin_action = {
            "id": str(uuid.uuid4()),
            "admin_email": admin_data["adminEmail"],
            "action": "create_procedure",
            "procedure_id": procedure_id,
            "procedure_name": procedure.name,
            "timestamp": datetime.utcnow()
        }
        await db.admin_actions.insert_one(admin_action)
        
        # Create a clean response without datetime objects and MongoDB _id
        clean_procedure = {
            "id": procedure_id,
            "name": procedure.name,
            "specialty": procedure.specialty,
            "specialtyName": procedure.specialtyName,
            "duration": procedure.duration,
            "overview": procedure.overview,
            "immediateAftercare": procedure.immediateAftercare,
            "dietRestrictions": procedure.dietRestrictions,
            "warningSignsToCallDoctor": procedure.warningSignsToCallDoctor,
            "recoveryTimeline": procedure.recoveryTimeline,
            "medications": procedure.medications,
            "createdBy": admin_data["adminEmail"]
        }
        
        return {
            "success": True,
            "message": "Procedure created successfully",
            "procedure_id": procedure_id,
            "procedure": clean_procedure
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Create procedure error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create procedure"
        )

@router.put("/procedures/{procedure_id}")
async def update_global_procedure(
    procedure_id: str,
    procedure: GlobalProcedureUpdate,
    admin_data = Depends(verify_admin_token)
):
    """Update an existing global procedure"""
    try:
        # Check if procedure exists
        existing = await db.procedures.find_one({"id": procedure_id})
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Procedure not found"
            )
        
        # Build update document with only provided fields
        update_doc = {"updatedAt": datetime.utcnow(), "updatedBy": admin_data["adminEmail"]}
        
        if procedure.name is not None:
            update_doc["name"] = procedure.name
        if procedure.specialty is not None:
            update_doc["specialty"] = procedure.specialty
        if procedure.specialtyName is not None:
            update_doc["specialtyName"] = procedure.specialtyName
        if procedure.duration is not None:
            update_doc["duration"] = procedure.duration
        if procedure.overview is not None:
            update_doc["overview"] = procedure.overview
        if procedure.immediateAftercare is not None:
            update_doc["immediateAftercare"] = procedure.immediateAftercare
        if procedure.dietRestrictions is not None:
            update_doc["dietRestrictions"] = procedure.dietRestrictions
        if procedure.warningSignsToCallDoctor is not None:
            update_doc["warningSignsToCallDoctor"] = procedure.warningSignsToCallDoctor
        if procedure.recoveryTimeline is not None:
            update_doc["recoveryTimeline"] = procedure.recoveryTimeline
        if procedure.medications is not None:
            update_doc["medications"] = procedure.medications
        
        # Update procedure
        await db.procedures.update_one(
            {"id": procedure_id},
            {"$set": update_doc}
        )
        
        # Log admin action
        admin_action = {
            "id": str(uuid.uuid4()),
            "admin_email": admin_data["adminEmail"],
            "action": "update_procedure",
            "procedure_id": procedure_id,
            "procedure_name": existing["name"],
            "changes": list(update_doc.keys()),
            "timestamp": datetime.utcnow()
        }
        await db.admin_actions.insert_one(admin_action)
        
        return {
            "success": True,
            "message": "Procedure updated successfully",
            "procedure_id": procedure_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update procedure error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update procedure"
        )

@router.delete("/procedures/{procedure_id}")
async def delete_global_procedure(
    procedure_id: str,
    admin_data = Depends(verify_admin_token)
):
    """Delete a global procedure"""
    try:
        # Check if procedure exists
        existing = await db.procedures.find_one({"id": procedure_id})
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Procedure not found"
            )
        
        # Check if procedure is used in any assignments
        assignments_count = await db.patientprocedures.count_documents({"procedureId": procedure_id})
        if assignments_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete procedure. It is currently assigned to {assignments_count} patients."
            )
        
        # Delete procedure
        await db.procedures.delete_one({"id": procedure_id})
        
        # Update specialty count
        await db.specialties.update_one(
            {"id": existing["specialty"]},
            {"$inc": {"procedureCount": -1}},
            upsert=False
        )
        
        # Log admin action
        admin_action = {
            "id": str(uuid.uuid4()),
            "admin_email": admin_data["adminEmail"],
            "action": "delete_procedure",
            "procedure_id": procedure_id,
            "procedure_name": existing["name"],
            "timestamp": datetime.utcnow()
        }
        await db.admin_actions.insert_one(admin_action)
        
        return {
            "success": True,
            "message": "Procedure deleted successfully",
            "procedure_id": procedure_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete procedure error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete procedure"
        )

@router.post("/procedures/deploy")
async def deploy_procedures_to_practices(
    deployment: ProcedureDeploymentRequest,
    admin_data = Depends(verify_admin_token)
):
    """Deploy procedure updates to specified practices"""
    try:
        # Get target practices based on deployment type
        practices_query = {}
        
        if deployment.deployment_type == "all_practices":
            # Deploy to all practices
            pass
        elif deployment.deployment_type == "active_only":
            practices_query = {"subscription.status": "active"}
        elif deployment.deployment_type == "trial_only":
            practices_query = {"subscription.status": "trial"}
        elif deployment.deployment_type == "specific_practices":
            if not deployment.practice_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="practice_ids required for specific_practices deployment"
                )
            practices_query = {"id": {"$in": deployment.practice_ids}}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid deployment_type"
            )
        
        # Get target practices
        practices = await db.practices.find(practices_query, {"_id": 0, "id": 1, "name": 1}).to_list(length=None)
        
        if not practices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No practices found matching deployment criteria"
            )
        
        # For now, procedures are global so deployment is immediate
        # In a more complex system, you might have practice-specific procedure copies
        
        deployment_result = {
            "deployed_to_practices": len(practices),
            "procedures_deployed": len(deployment.procedure_ids),
            "practice_list": [p["name"] for p in practices[:10]]  # First 10 for display
        }
        
        # Log admin action
        admin_action = {
            "id": str(uuid.uuid4()),
            "admin_email": admin_data["adminEmail"],
            "action": "deploy_procedures",
            "deployment_type": deployment.deployment_type,
            "procedure_ids": deployment.procedure_ids,
            "practices_affected": len(practices),
            "timestamp": datetime.utcnow()
        }
        await db.admin_actions.insert_one(admin_action)
        
        return {
            "success": True,
            "message": f"Procedures deployed to {len(practices)} practices",
            "deployment_result": deployment_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Deploy procedures error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deploy procedures"
        )

@router.get("/procedures/{procedure_id}/usage")
async def get_procedure_usage_stats(
    procedure_id: str,
    admin_data = Depends(verify_admin_token)
):
    """Get usage statistics for a specific procedure"""
    try:
        # Check if procedure exists
        procedure = await db.procedures.find_one({"id": procedure_id})
        if not procedure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Procedure not found"
            )
        
        # Get usage statistics
        total_assignments = await db.patientprocedures.count_documents({"procedureId": procedure_id})
        active_assignments = await db.patientprocedures.count_documents({"procedureId": procedure_id, "status": "active"})
        completed_assignments = await db.patientprocedures.count_documents({"procedureId": procedure_id, "status": "completed"})
        
        # Get practices using this procedure
        practices_pipeline = [
            {"$match": {"procedureId": procedure_id}},
            {"$group": {"_id": "$practiceId", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        practices_using = await db.patientprocedures.aggregate(practices_pipeline).to_list(length=None)
        
        # Get practice names
        practice_usage = []
        for p in practices_using[:10]:  # Top 10 practices
            practice = await db.practices.find_one({"id": p["_id"]}, {"_id": 0, "name": 1})
            if practice:
                practice_usage.append({
                    "practice_name": practice["name"],
                    "usage_count": p["count"]
                })
        
        return {
            "success": True,
            "procedure": {
                "id": procedure["id"],
                "name": procedure["name"],
                "specialty": procedure["specialtyName"]
            },
            "usage_stats": {
                "total_assignments": total_assignments,
                "active_assignments": active_assignments,
                "completed_assignments": completed_assignments,
                "practices_using": len(practices_using),
                "top_practices": practice_usage
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get procedure usage error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get procedure usage statistics"
        )