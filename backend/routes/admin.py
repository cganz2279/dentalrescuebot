from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
import os
import bcrypt
import jwt
from datetime import datetime, timedelta
import uuid
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from pathlib import Path

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

class PasswordResetRequest(BaseModel):
    user_id: str
    new_password: str

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
        if not verify_super_admin(request.email, request.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin credentials"
            )
        
        token = generate_admin_token(request.email)
        
        return {
            "success": True,
            "token": token,
            "message": "Admin login successful"
        }
        
    except Exception as e:
        print(f"Admin login error: {e}")
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