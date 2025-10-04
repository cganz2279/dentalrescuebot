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
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@theoncallbot.com')

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
        # Check if practice already exists
        existing_practice = await db.practices.find_one({"email": customer_email})
        if existing_practice:
            print(f"⚠️ Practice already exists for {customer_email}")
            return {
                "status": "duplicate",
                "message": f"Account already exists for {customer_email}",
                "practice_id": existing_practice.get("id")
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

async def send_admin_notification(practice_info: Dict[str, Any]) -> bool:
    """Send admin notification about new practice"""
    try:
        # Create admin notification content
        admin_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #dc2626;">🚀 New Practice Account Created</h2>
            
            <div style="background-color: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Practice Details:</h3>
                <p><strong>Practice Name:</strong> {practice_info['practice_name']}</p>
                <p><strong>Owner:</strong> {practice_info['owner_name']}</p>
                <p><strong>Email:</strong> {practice_info['email']}</p>
                <p><strong>Created:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                <p><strong>Trial Ends:</strong> {practice_info['trial_end'].strftime('%Y-%m-%d')}</p>
                <p><strong>Source:</strong> SamCart Integration</p>
            </div>
            
            <p style="color: #374151;">
                A welcome email with login credentials has been sent to the practice owner.
                Please monitor the account setup progress in the admin dashboard.
            </p>
        </div>
        """
        
        admin_email_data = EmailData(
            to=[ADMIN_EMAIL],
            subject=f"New Practice: {practice_info['practice_name']}",
            html_content=admin_content
        )
        
        success = await send_email(admin_email_data)
        
        if success:
            print(f"✅ Admin notification sent for {practice_info['practice_name']}")
        else:
            print(f"❌ Failed to send admin notification for {practice_info['practice_name']}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error sending admin notification: {e}")
        return False

async def log_webhook_event(webhook_log: SamCartWebhookLog):
    """Log webhook processing event"""
    try:
        log_doc = webhook_log.dict()
        await db.samcart_webhook_logs.insert_one(log_doc)
    except Exception as e:
        print(f"❌ Error logging webhook event: {e}")

@router.post("/samcart")
async def handle_samcart_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle SamCart webhook for practice account creation"""
    webhook_id = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc)
    
    print(f"🔔 SamCart webhook received: {webhook_id}")
    
    try:
        # Get request body and headers
        body = await request.body()
        signature_header = (
            request.headers.get("X-Webhook-Signature") or 
            request.headers.get("X-Hub-Signature-256") or
            request.headers.get("Signature")
        )
        
        print(f"📝 Body length: {len(body)} bytes")
        print(f"🔑 Signature header: {signature_header[:20] if signature_header else 'None'}...")
        
        # For development/testing, allow webhooks without signature verification
        # In production, uncomment the signature verification
        """
        if not verify_samcart_signature(body, signature_header):
            await log_webhook_event(SamCartWebhookLog(
                webhook_id=webhook_id,
                event_type="signature_verification_failed",
                payload={"error": "Invalid signature"},
                processing_status="failed",
                error_message="Webhook signature verification failed",
                created_at=datetime.now(timezone.utc)
            ))
            raise HTTPException(status_code=403, detail="Invalid webhook signature")
        """
        
        # Parse JSON payload
        try:
            payload = json.loads(body.decode('utf-8'))
            print(f"📦 Parsed payload type: {payload.get('type', 'unknown')}")
        except json.JSONDecodeError as e:
            await log_webhook_event(SamCartWebhookLog(
                webhook_id=webhook_id,
                event_type="json_parse_error",
                payload={"error": str(e)},
                processing_status="failed",
                error_message="Failed to parse JSON payload",
                created_at=datetime.now(timezone.utc)
            ))
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        event_type = payload.get("type", "unknown")
        
        # Process webhook based on event type
        result = None
        
        if event_type in ["ProductPurchased", "OrderCompleted", "Order.Completed", "Order"]:
            print(f"🎯 Processing {event_type} event...")
            
            # Create practice account
            practice_result = await create_practice_from_samcart(payload)
            
            if practice_result["status"] == "success":
                # Send welcome email and admin notification in background
                background_tasks.add_task(send_welcome_email, practice_result)
                background_tasks.add_task(send_admin_notification, practice_result)
                
                result = {
                    "status": "success",
                    "message": "Practice account created and welcome email queued",
                    "practice_id": practice_result["practice_id"],
                    "email": practice_result["email"]
                }
            else:
                result = practice_result
                
        else:
            result = {
                "status": "ignored",
                "message": f"Event type '{event_type}' not processed"
            }
            print(f"ℹ️ Ignoring event type: {event_type}")
        
        # Log successful webhook processing
        processing_duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        background_tasks.add_task(
            log_webhook_event,
            SamCartWebhookLog(
                webhook_id=webhook_id,
                event_type=event_type,
                payload=payload,
                processing_status="success",
                created_at=start_time,
                processing_duration=processing_duration
            )
        )
        
        print(f"✅ Webhook {webhook_id} processed successfully in {processing_duration:.2f}s")
        
        return JSONResponse(
            status_code=200,
            content={
                "webhook_id": webhook_id,
                "status": "success",
                "result": result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Webhook processing error: {e}")
        
        # Log failed webhook processing
        processing_duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        background_tasks.add_task(
            log_webhook_event,
            SamCartWebhookLog(
                webhook_id=webhook_id,
                event_type=payload.get("type", "unknown") if 'payload' in locals() else "unknown",
                payload=payload if 'payload' in locals() else {},
                processing_status="failed",
                error_message=str(e),
                created_at=start_time,
                processing_duration=processing_duration
            )
        )
        
        raise HTTPException(status_code=500, detail="Internal server error")

# Test endpoint for webhook simulation
@router.post("/samcart/test")
async def test_samcart_webhook(test_email: str = "test@example.com"):
    """Test endpoint to simulate SamCart webhook (for development)"""
    
    # Create test payload
    test_payload = {
        "type": "ProductPurchased",
        "api_key": None,
        "product": {
            "id": 999999,
            "sku": "DENTAL-TEST-001",
            "name": "Dental Practice Management - Test",
            "price": "49.95",
            "tax": "0.00",
            "shipping": "0.00",
            "sub_total": "49.95",
            "product_price": "49.95"
        },
        "customer": {
            "first_name": "Dr. Test",
            "last_name": "Practice",
            "email": test_email,
            "phone_number": "555-123-4567",
            "customer_id": 999999,
            "billing_address_line1": "123 Test Medical Plaza",
            "billing_address_line2": "Suite 100",
            "billing_city": "Test City",
            "billing_state": "TX",
            "billing_zip": "78759",
            "billing_country": "United States"
        },
        "order": {
            "id": 999999,
            "total": "49.95",
            "ip_address": "127.0.0.1",
            "custom_fields": []
        }
    }
    
    try:
        # Process the test webhook
        result = await create_practice_from_samcart(test_payload)
        
        if result["status"] == "success":
            # Send emails
            email_success = await send_welcome_email(result)
            admin_success = await send_admin_notification(result)
            
            return {
                "status": "success",
                "message": "Test practice account created successfully",
                "practice_info": {
                    "practice_id": result["practice_id"],
                    "email": result["email"],
                    "practice_name": result["practice_name"],
                    "password": result["password"],  # Include password for testing
                    "owner_name": result["owner_name"]
                },
                "emails_sent": {
                    "welcome_email": email_success,
                    "admin_notification": admin_success
                }
            }
        else:
            return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@router.get("/samcart/logs")
async def get_webhook_logs(limit: int = 50):
    """Get recent webhook processing logs"""
    try:
        logs = await db.samcart_webhook_logs.find().sort("created_at", -1).limit(limit).to_list(length=limit)
        
        # Convert ObjectIds to strings
        for log in logs:
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
        successful_webhooks = await db.samcart_webhook_logs.count_documents({"processing_status": "success"})
        failed_webhooks = await db.samcart_webhook_logs.count_documents({"processing_status": "failed"})
        
        # Get recent practice creations from SamCart
        recent_practices = await db.practices.count_documents({
            "source": "samcart",
            "createdAt": {"$gte": datetime.now(timezone.utc) - timedelta(days=30)}
        })
        
        return {
            "total_webhooks": total_webhooks,
            "successful_webhooks": successful_webhooks,
            "failed_webhooks": failed_webhooks,
            "success_rate": (successful_webhooks / total_webhooks * 100) if total_webhooks > 0 else 0,
            "recent_practice_signups": recent_practices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")