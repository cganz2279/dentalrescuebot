from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
import json
import uuid
import bcrypt
from datetime import datetime, timedelta, timezone
import os
import asyncio

# Import existing services
from database import db
from services.email_service import EmailService

# Initialize email service
email_service = EmailService()

router = APIRouter(prefix="/api/webhook", tags=["samcart"])

# Configuration - Get from environment
TRIAL_PERIOD_DAYS = 30
MONTHLY_PRICE = 49.95
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://app.dentalaftercarenotes.com')
# Note: Admin notifications disabled for privacy

# Models
class SamCartWebhook(BaseModel):
    webhook_id: str
    event_type: str
    customer_email: str
    order_id: str
    status: str
    created_at: datetime
    error_message: Optional[str] = None

class PracticeAccount(BaseModel):
    id: str
    name: str
    email: str
    owner_name: str
    password_hash: str
    subscription_status: str
    trial_end_date: datetime
    created_at: datetime

def generate_secure_password() -> str:
    """Generate a secure password for new practice accounts"""
    import secrets
    import string
    
    # Create a strong password with mix of characters
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(12))
    
    # Ensure it has required character types
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%&*" for c in password)
    
    if not all([has_upper, has_lower, has_digit, has_special]):
        return generate_secure_password()  # Regenerate if requirements not met
    
    return password

async def create_practice_account(customer_email: str, customer_name: str, order_id: str) -> Dict[str, Any]:
    """Create a new practice account from SamCart payment data"""
    try:
        # Check if we've already processed this specific order to prevent duplicate emails
        existing_webhook = await db.samcart_webhook_logs.find_one({
            "customer_email": customer_email,
            "order_id": order_id,
            "status": "success"
        })
        
        if existing_webhook:
            print(f"⚠️ Order {order_id} already processed for {customer_email} - preventing duplicate email")
            existing_practice = await db.practices.find_one({"email": customer_email})
            return {
                "status": "already_processed",
                "message": f"Order {order_id} already processed - no duplicate email sent",
                "practice_id": existing_practice.get("id") if existing_practice else None
            }
        
        # Check if practice already exists (for different orders)
        existing_practice = await db.practices.find_one({"email": customer_email})
        if existing_practice:
            print(f"⚠️ Practice exists for {customer_email} but this is a new order {order_id} - sending welcome email")
            
            # For new orders from existing customers, send welcome email with existing credentials
            # Don't change password, just use existing account
            return {
                "status": "existing_customer_new_order",
                "message": f"Existing customer new order - sending welcome email",
                "practice_id": existing_practice.get("id"),
                "email": customer_email,
                "password": "Please use password reset",  # Don't expose existing password
                "practice_name": existing_practice.get("name", f"Dr. {customer_name} Dental Practice"),
                "owner_name": existing_practice.get("ownerName", customer_name),
                "trial_end": existing_practice.get("subscription", {}).get("trialEndDate", datetime.now(timezone.utc).isoformat())
            }
        
        # Generate secure credentials
        practice_id = str(uuid.uuid4())
        password = generate_secure_password()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Calculate trial period
        trial_end = datetime.now(timezone.utc) + timedelta(days=TRIAL_PERIOD_DAYS)
        
        # Create practice name from customer name
        if " " in customer_name:
            first_name, last_name = customer_name.split(" ", 1)
            practice_name = f"Dr. {last_name} Dental Practice"
        else:
            practice_name = f"{customer_name} Dental Practice"
        
        # Create practice document
        practice_data = {
            "id": practice_id,
            "name": practice_name,
            "email": customer_email,
            "password": password_hash,
            "ownerName": customer_name,
            "ownerEmail": customer_email,
            
            # Contact info - blank since not provided in SamCart payment
            "phone": None,
            "address": "",
            "city": "",
            "state": "",
            "zipCode": "",
            "country": "",
            "ownerPhone": None,
            
            # Subscription details
            "subscription": {
                "status": "trial",  # Start as trial
                "type": "monthly",
                "price": MONTHLY_PRICE,
                "trialEndDate": trial_end.isoformat(),
                "samcartOrderId": order_id,
                "currentPeriodEnd": trial_end.isoformat()
            },
            
            # Account status
            "isActive": True,
            "emailVerified": True,
            "setupCompleted": False,
            
            # Default branding
            "branding": {
                "logo": None,
                "primaryColor": "#2563eb",
                "secondaryColor": "#1e40af",
                "welcomeMessage": "Welcome to our practice!"
            },
            
            # Metadata
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "source": "samcart",
            "samcartOrderId": order_id
        }
        
        # Insert into database
        result = await db.practices.insert_one(practice_data)
        
        print(f"✅ Created practice account: {customer_email} (ID: {practice_id})")
        
        return {
            "status": "success",
            "practice_id": practice_id,
            "email": customer_email,
            "password": password,  # Return plain password for welcome email
            "practice_name": practice_name,
            "owner_name": customer_name,
            "trial_end": trial_end.isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error creating practice account: {e}")
        raise e

async def send_welcome_email(practice_info: Dict[str, Any]) -> bool:
    """Send welcome email to new practice owner"""
    try:
        # Extract practice information
        practice_name = practice_info.get('practice_name', 'Your Practice')
        owner_name = practice_info.get('owner_name', 'Practice Owner')
        admin_email = practice_info.get('email')
        temp_password = practice_info.get('password')
        
        if not admin_email or not temp_password:
            print(f"❌ Missing email or password for welcome email")
            return False
        
        # Create admin credentials dictionary for email template
        admin_credentials = {
            'adminEmail': admin_email,
            'tempPassword': temp_password,
            'adminFirstName': owner_name.split()[0] if owner_name else 'Doctor',
            'adminLastName': owner_name.split()[-1] if ' ' in owner_name else 'Practice'
        }
        
        # Create practice data dictionary for email template
        practice_data = {
            'practiceName': practice_name
        }
        
        # Use the existing welcome email method from email service
        success = email_service.send_welcome_email(
            practice_data=practice_data,
            admin_credentials=admin_credentials,
            app_url=FRONTEND_URL
        )
        
        if success:
            print(f"✅ Welcome email sent successfully to {admin_email}")
        else:
            print(f"❌ Failed to send welcome email to {admin_email}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error sending welcome email: {e}")
        return False

async def log_webhook_event(webhook_data: Dict[str, Any]) -> bool:
    """Log webhook event to database"""
    try:
        webhook_log = {
            "webhook_id": webhook_data.get("webhook_id"),
            "event_type": webhook_data.get("event_type"),
            "customer_email": webhook_data.get("customer_email"),
            "order_id": webhook_data.get("order_id"),
            "status": webhook_data.get("status"),
            "created_at": datetime.now(timezone.utc),
            "error_message": webhook_data.get("error_message")
        }
        
        await db.samcart_webhook_logs.insert_one(webhook_log)
        return True
        
    except Exception as e:
        print(f"❌ Error logging webhook event: {e}")
        return False

# Admin notifications removed for privacy - practice creation is logged in admin dashboard

# Note: log_webhook_event function is now inline in the webhook handlers

@router.post("/samcart")
async def handle_samcart_webhook(request: Request):
    """Handle SamCart webhook for practice account creation - REBUILT FOR RELIABILITY"""
    webhook_id = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc)
    
    print(f"🚀 NEW SamCart webhook received: {webhook_id}")
    
    try:
        # Get request body
        body = await request.body()
        print(f"📦 Received payload ({len(body)} bytes)")
        
        # Parse JSON payload
        try:
            payload = json.loads(body.decode('utf-8'))
            event_type = payload.get("type", "unknown")
            print(f"📋 Event type: {event_type}")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Process ALL payment events (SamCart sends different event types than expected)
        print(f"💰 Processing SamCart event: {event_type} (accepting all events)")
        
        # Extract customer data - handle real SamCart payload structure
        customer = payload.get("customer", {})
        order = payload.get("order", {})
        products = payload.get("products", [])
        
        # Real SamCart structure: payload.customer.email
        customer_email = customer.get("email", "").strip().lower()
        customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
        
        # Try multiple order ID sources from real SamCart webhooks
        order_id = str(order.get("id", webhook_id))
        if not order_id or order_id == webhook_id:
            # Try product transaction_id if order_id not available
            if products and isinstance(products, list) and len(products) > 0:
                order_id = products[0].get("transaction_id", webhook_id)
        
        print(f"📧 Customer email extracted: '{customer_email}'")
        print(f"👤 Customer name extracted: '{customer_name}'")
            
        if not customer_email:
            print(f"❌ No customer email in webhook payload")
            print(f"🔍 Full payload structure: {json.dumps(payload, indent=2)}")
            raise HTTPException(status_code=400, detail="Customer email required")
            
        if not customer_name or customer_name == " ":
            customer_name = customer_email.split("@")[0]  # Use email prefix as fallback
        
        print(f"👤 Customer: {customer_name} ({customer_email})")
        print(f"🔖 Order ID: {order_id}")
        
        # Create practice account
        account_result = await create_practice_account(
            customer_email=customer_email,
            customer_name=customer_name,
            order_id=order_id
        )
            
        # Log the webhook event
        await log_webhook_event({
            "webhook_id": webhook_id,
            "event_type": event_type,
            "customer_email": customer_email,
            "order_id": order_id,
            "status": account_result["status"]
        })
        
        if account_result["status"] == "success":
            # Send welcome email immediately (not in background)
            print(f"📧 Sending welcome email to {customer_email}...")
            email_success = await send_welcome_email(account_result)
            
            if email_success:
                print(f"✅ Welcome email sent successfully to {customer_email}")
            else:
                print(f"⚠️ Welcome email failed for {customer_email} - but account was created")
            
            return JSONResponse(
                status_code=200,
                content={
                    "webhook_id": webhook_id,
                    "status": "success", 
                    "message": "Practice account created and welcome email sent",
                    "practice_id": account_result["practice_id"],
                    "email": customer_email,
                    "email_sent": email_success
                }
            )
        
        elif account_result["status"] == "duplicate_with_email":
            print(f"📧 Sending welcome email for duplicate payment: {customer_email}")
            email_success = await send_welcome_email(account_result)
            
            if email_success:
                print(f"✅ Welcome email sent for duplicate payment to {customer_email}")
            else:
                print(f"❌ Welcome email failed for duplicate payment to {customer_email}")
            
            return JSONResponse(
                status_code=200,
                content={
                    "webhook_id": webhook_id,
                    "status": "duplicate_with_email",
                    "message": f"Account exists - welcome email sent with new credentials",
                    "practice_id": account_result.get("practice_id"),
                    "email": customer_email,
                    "email_sent": email_success
                }
            )
        
        elif account_result["status"] == "duplicate":
            print(f"⚠️ Duplicate account for {customer_email} - no email sent")
            return JSONResponse(
                status_code=200,
                content={
                    "webhook_id": webhook_id,
                    "status": "duplicate", 
                    "message": f"Account already exists for {customer_email}",
                    "practice_id": account_result.get("practice_id")
                }
            )
        
        else:
            print(f"❌ Account creation failed: {account_result}")
            raise HTTPException(status_code=500, detail="Account creation failed")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Webhook processing error: {e}")
        
        # Log failed webhook
        try:
            await log_webhook_event({
                "webhook_id": webhook_id,
                "event_type": "unknown",
                "customer_email": "unknown",
                "order_id": "unknown", 
                "status": "failed",
                "error_message": str(e)
            })
        except:
            pass  # Don't fail webhook if logging fails
        
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

@router.post("/samcart/test")
async def test_samcart_webhook(test_email: str = "test@example.com"):
    """Test endpoint to simulate SamCart payment - REBUILT VERSION"""
    
    try:
        # Generate test data
        test_name = "Dr. Test Practice"
        test_order_id = f"TEST_{int(datetime.now().timestamp())}"
        
        print(f"🧪 Testing SamCart integration for {test_email}")
        
        # Create practice account
        account_result = await create_practice_account(
            customer_email=test_email,
            customer_name=test_name,
            order_id=test_order_id
        )
        
        if account_result["status"] == "success":
            # Send welcome email
            email_success = await send_welcome_email(account_result)
            
            return {
                "status": "success",
                "message": "Test practice account created and email sent",
                "practice_info": {
                    "practice_id": account_result["practice_id"],
                    "email": account_result["email"],
                    "practice_name": account_result["practice_name"],
                    "password": account_result["password"],  # Include for testing
                    "owner_name": account_result["owner_name"],
                    "trial_end": account_result["trial_end"]
                },
                "email_sent": email_success
            }
        else:
            return account_result
            
    except Exception as e:
        print(f"❌ Test webhook error: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@router.get("/samcart/logs")
async def get_webhook_logs(limit: int = 50):
    """Get recent webhook processing logs"""
    try:
        logs = await db.samcart_webhook_logs.find().sort("created_at", -1).limit(limit).to_list(length=limit)
        
        # Convert ObjectIds to strings and format response
        for log in logs:
            if "_id" in log:
                log["_id"] = str(log["_id"])
        
        return {
            "status": "success",
            "logs": logs,
            "count": len(logs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch logs: {str(e)}")

@router.get("/samcart/stats") 
async def get_webhook_stats():
    """Get webhook processing statistics"""
    try:
        total_webhooks = await db.samcart_webhook_logs.count_documents({})
        successful_webhooks = await db.samcart_webhook_logs.count_documents({"status": "success"})
        failed_webhooks = await db.samcart_webhook_logs.count_documents({"status": "failed"})
        
        # Get recent practice creations from SamCart
        recent_practices = await db.practices.count_documents({
            "source": "samcart"
        })
        
        return {
            "total_webhooks": total_webhooks,
            "successful_webhooks": successful_webhooks,
            "failed_webhooks": failed_webhooks,
            "success_rate": round((successful_webhooks / total_webhooks * 100), 1) if total_webhooks > 0 else 0,
            "recent_practice_signups": recent_practices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")