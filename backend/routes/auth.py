from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
import os
import bcrypt
import jwt
from datetime import datetime, timedelta
import uuid
from typing import Optional
import re
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

JWT_SECRET = os.environ.get('JWT_SECRET', 'your-super-secret-jwt-key-change-in-production')

# Pydantic models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    firstName: str
    lastName: str
    role: str = "patient"
    practiceId: Optional[str] = None

class PracticeRegisterRequest(BaseModel):
    # Practice info
    practiceName: str
    email: EmailStr
    phone: Optional[str] = None
    website: Optional[str] = None
    # Admin user info
    adminFirstName: str
    adminLastName: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str

class ForgotUsernameRequest(BaseModel):
    practice_name: str
    phone: Optional[str] = None
    adminPassword: str
    # Address
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    firstName: str
    lastName: str
    role: str
    practiceId: Optional[str] = None
    isActive: bool

class LoginResponse(BaseModel):
    success: bool
    user: UserResponse
    token: str
    practice: Optional[dict] = None

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_token(user_id: str, role: str, practice_id: str = None) -> str:
    payload = {
        'userId': user_id,
        'role': role,
        'practiceId': practice_id,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def validate_password(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 6:
        return False
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True

# Auth routes
@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    try:
        # Find user by email
        user = await db.users.find_one({"email": request.email.lower()})
        
        if not user or not user.get('isActive', True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not verify_password(request.password, user['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Update last login
        await db.users.update_one(
            {"id": user['id']},
            {
                "$set": {"lastLoginAt": datetime.utcnow()},
                "$inc": {"loginCount": 1}
            }
        )
        
        # Get practice info if user has practice
        practice = None
        if user.get('practiceId'):
            practice = await db.practices.find_one(
                {"id": user['practiceId']},
                {"_id": 0, "password": 0}
            )
        
        # Generate token
        token = generate_token(user['id'], user['role'], user.get('practiceId'))
        
        # Create user response
        user_response = UserResponse(
            id=user['id'],
            email=user['email'],
            firstName=user['firstName'],
            lastName=user['lastName'],
            role=user['role'],
            practiceId=user.get('practiceId'),
            isActive=user.get('isActive', True)
        )
        
        return LoginResponse(
            success=True,
            user=user_response,
            token=token,
            practice=practice
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/register-practice")
async def register_practice(request: PracticeRegisterRequest):
    try:
        # Validate password
        if not validate_password(request.adminPassword):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters with letters and numbers"
            )
        
        # Check if email already exists
        existing_user = await db.users.find_one({"email": request.email.lower()})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Generate IDs
        practice_id = str(uuid.uuid4())
        admin_user_id = str(uuid.uuid4())
        
        # Create practice document with trial that requires payment setup
        practice_doc = {
            "id": practice_id,
            "name": request.practiceName,
            "email": request.email.lower(),
            "phone": request.phone,
            "website": request.website,
            "address": {
                "street": request.street,
                "city": request.city,
                "state": request.state,
                "zipCode": request.zipCode
            },
            "branding": {
                "primaryColor": "#2563eb",
                "secondaryColor": "#1e40af",
                "welcomeMessage": f"Welcome to {request.practiceName}'s post-operative care portal"
            },
            "subscription": {
                "plan": "basic",
                "status": "trial_pending_payment",  # Requires payment method setup
                "trialEndsAt": datetime.utcnow() + timedelta(days=15),
                "requiresPayment": True,
                "monthlyAmount": 49.0,
                "paymentMethodRequired": True,
                "chargeDate": datetime.utcnow() + timedelta(days=15)  # When to charge
            },
            "settings": {
                "allowPatientRegistration": False,
                "requirePatientApproval": True,
                "customProcedures": []
            },
            "isActive": False,  # Will be activated after payment method setup
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        # Create admin user document
        admin_user_doc = {
            "id": admin_user_id,
            "email": request.email.lower(),
            "password": hash_password(request.adminPassword),
            "firstName": request.adminFirstName,
            "lastName": request.adminLastName,
            "role": "practice_admin",
            "practiceId": practice_id,
            "isActive": False,  # Will be activated after payment setup
            "isEmailVerified": True,
            "loginCount": 0,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        # Insert both documents
        await db.practices.insert_one(practice_doc)
        await db.users.insert_one(admin_user_doc)
        
        # Return practice info and flag for payment setup requirement
        return {
            "success": True,
            "message": "Practice registered successfully - payment method required to activate trial",
            "practice": {
                "id": practice_id,
                "name": request.practiceName,
                "email": request.email,
                "trialEndsAt": practice_doc["subscription"]["trialEndsAt"],
                "chargeDate": practice_doc["subscription"]["chargeDate"]
            },
            "requiresPaymentSetup": True,
            "nextStep": "setup_payment_method"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Practice registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/register-practice-samcart")
async def register_practice_samcart(request: PracticeRegisterRequest):
    """Register practice after SamCart payment verification"""
    try:
        # Validate password
        if not validate_password(request.adminPassword):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters with letters and numbers"
            )
        
        # Check if email already exists
        existing_user = await db.users.find_one({"email": request.email.lower()})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Generate IDs
        practice_id = str(uuid.uuid4())
        admin_user_id = str(uuid.uuid4())
        
        # Create practice document - ACTIVE since payment already processed
        practice_doc = {
            "id": practice_id,
            "name": request.practiceName,
            "email": request.email.lower(),
            "phone": request.phone,
            "website": request.website,
            "address": {
                "street": request.street,
                "city": request.city,
                "state": request.state,
                "zipCode": request.zipCode
            },
            "branding": {
                "primaryColor": "#2563eb",
                "secondaryColor": "#1e40af",
                "welcomeMessage": f"Welcome to {request.practiceName}'s post-operative care portal"
            },
            "subscription": {
                "plan": "basic",
                "status": "active",  # Already paid via SamCart
                "paymentSource": "samcart",
                "monthlyAmount": 49.0,
                "activatedAt": datetime.utcnow(),
                "nextBillingDate": datetime.utcnow() + timedelta(days=30)
            },
            "settings": {
                "allowPatientRegistration": False,
                "requirePatientApproval": True,
                "customProcedures": []
            },
            "isActive": True,  # Immediately active
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        # Create admin user document
        admin_user_doc = {
            "id": admin_user_id,
            "email": request.email.lower(),
            "password": hash_password(request.adminPassword),
            "firstName": request.adminFirstName,
            "lastName": request.adminLastName,
            "role": "practice_admin",
            "practiceId": practice_id,
            "isActive": True,  # Immediately active
            "isEmailVerified": True,
            "loginCount": 0,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        # Insert both documents
        await db.practices.insert_one(practice_doc)
        await db.users.insert_one(admin_user_doc)
        
        return {
            "success": True,
            "message": "Registration completed successfully - account is active",
            "practice": {
                "id": practice_id,
                "name": request.practiceName,
                "email": request.email,
                "status": "active"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"SamCart registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/invite-patient")
async def invite_patient(
    email: EmailStr,
    firstName: str,
    lastName: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Practice admin can invite patients"""
    try:
        # Verify token and get user
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['userId']
        role = payload['role']
        practice_id = payload['practiceId']
        
        # Check if user is practice admin or staff
        if role not in ['practice_admin', 'practice_staff']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only practice admins can invite patients"
            )
        
        # Check if email already exists
        existing_user = await db.users.find_one({"email": email.lower()})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Generate patient ID
        patient_id = str(uuid.uuid4())
        
        # Create patient user (they'll set password on first login)
        patient_doc = {
            "id": patient_id,
            "email": email.lower(),
            "password": hash_password(str(uuid.uuid4())),  # Temporary password
            "firstName": firstName,
            "lastName": lastName,
            "role": "patient",
            "practiceId": practice_id,
            "isActive": True,
            "isEmailVerified": False,
            "invitedBy": user_id,
            "invitedAt": datetime.utcnow(),
            "loginCount": 0,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        await db.users.insert_one(patient_doc)
        
        return {
            "success": True,
            "message": "Patient invited successfully",
            "patientId": patient_id
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
    except HTTPException:
        raise
    except Exception as e:
        print(f"Patient invitation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invitation failed"
        )

@router.post("/patient-setup")
async def patient_setup_password(request: dict):
    """Patient sets up their password for first-time login"""
    try:
        email = request.get("email")
        new_password = request.get("password")
        invitation_code = request.get("invitationCode", "")  # Optional for validation
        
        if not email or not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        # Validate password
        if not validate_password(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters with letters and numbers"
            )
        
        # Find patient
        patient = await db.users.find_one({"email": email.lower(), "role": "patient"})
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Update password and activate account
        hashed_password = hash_password(new_password)
        await db.users.update_one(
            {"id": patient["id"]},
            {
                "$set": {
                    "password": hashed_password,
                    "isActive": True,
                    "isEmailVerified": True,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Password setup successful. You can now login."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Patient setup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password setup failed"
        )

@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user info"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['userId']
        
        # Get user from database
        user = await db.users.find_one(
            {"id": user_id},
            {"_id": 0, "password": 0}
        )
        
        if not user or not user.get('isActive'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Get practice info if applicable
        practice = None
        if user.get('practiceId'):
            practice = await db.practices.find_one(
                {"id": user['practiceId']},
                {"_id": 0}
            )
        
        return {
            "success": True,
            "user": user,
            "practice": practice
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
        print(f"Get user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user info"
        )

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Initiate password reset process"""
    try:
        email = request.email.lower()
        
        # Find user by email
        user = await db.users.find_one({"email": email})
        
        # Always return success to prevent email enumeration attacks
        if not user:
            return {
                "success": True,
                "message": "If an account with this email exists, password reset instructions have been sent."
            }
        
        # Generate reset token
        reset_token = str(uuid.uuid4())
        reset_expires = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
        
        # Store reset token in database
        await db.password_resets.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": user["id"],
            "email": email,
            "reset_token": reset_token,
            "expires_at": reset_expires,
            "used": False,
            "created_at": datetime.utcnow()
        })
        
        # In a real application, you would send an email here
        # For now, we'll return the token for testing purposes
        # TODO: Implement email sending service
        
        return {
            "success": True,
            "message": "If an account with this email exists, password reset instructions have been sent.",
            "reset_token": reset_token,  # Remove this in production
            "reset_link": f"https://www.theoncallbot.com/practice-notes/reset-password?token={reset_token}"  # Remove in production
        }
        
    except Exception as e:
        print(f"Forgot password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password using reset token"""
    try:
        reset_token = request.reset_token
        new_password = request.new_password
        
        # Validate password
        if not validate_password(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters with letters and numbers"
            )
        
        # Find valid reset token
        reset_record = await db.password_resets.find_one({
            "reset_token": reset_token,
            "used": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not reset_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Find user
        user = await db.users.find_one({"id": reset_record["user_id"]})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        hashed_password = hash_password(new_password)
        await db.users.update_one(
            {"id": user["id"]},
            {
                "$set": {
                    "password": hashed_password,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        # Mark reset token as used
        await db.password_resets.update_one(
            {"id": reset_record["id"]},
            {
                "$set": {
                    "used": True,
                    "used_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Password reset successful. You can now login with your new password."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reset password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )

@router.post("/forgot-username")
async def forgot_username(request: ForgotUsernameRequest):
    """Help user recover their username/email"""
    try:
        practice_name = request.practice_name.strip()
        phone = request.phone.strip() if request.phone else None
        
        if not practice_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Practice name is required"
            )
        
        # Build search query
        query = {"name": {"$regex": practice_name, "$options": "i"}}
        if phone:
            # Remove any non-digit characters for phone comparison
            clean_phone = re.sub(r'\D', '', phone)
            if clean_phone:
                query["phone"] = {"$regex": clean_phone}
        
        # Find practice
        practice = await db.practices.find_one(query)
        
        # Always return success to prevent information disclosure
        if not practice:
            return {
                "success": True,
                "message": "If a practice with these details exists, username recovery information has been sent."
            }
        
        # Find admin user for this practice
        admin_user = await db.users.find_one({
            "practiceId": practice["id"],
            "role": "practice_admin"
        })
        
        if not admin_user:
            return {
                "success": True,
                "message": "If a practice with these details exists, username recovery information has been sent."
            }
        
        # In a real application, you would send an email here
        # For now, we'll return the information for testing
        # TODO: Implement email sending with username recovery
        
        return {
            "success": True,
            "message": "If a practice with these details exists, username recovery information has been sent.",
            "practice_name": practice["name"],  # Remove in production
            "email": admin_user["email"],  # Remove in production
            "login_url": "https://www.theoncallbot.com/practice-notes"  # Remove in production
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Forgot username error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Username recovery request failed"
        )

@router.get("/validate-reset-token/{token}")
async def validate_reset_token(token: str):
    """Validate if a reset token is valid and not expired"""
    try:
        reset_record = await db.password_resets.find_one({
            "reset_token": token,
            "used": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not reset_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Get user info (without sensitive data)
        user = await db.users.find_one(
            {"id": reset_record["user_id"]},
            {"_id": 0, "email": 1, "firstName": 1, "lastName": 1}
        )
        
        return {
            "success": True,
            "valid": True,
            "user": user,
            "expires_at": reset_record["expires_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Validate token error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token validation failed"
        )