from fastapi import APIRouter, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
import hmac
import hashlib
import json
import uuid
import secrets
import bcrypt
from datetime import datetime, timedelta, timezone
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Import existing services
from database import db
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import email service with proper error handling
try:
    from services.email_service import send_email, EmailData
except ImportError:
    print("Warning: Email service not available")
    def send_email(email_data):
        print(f"Mock email send to: {email_data.to}")
        return True
    
    class EmailData:
        def __init__(self, to, subject, html_content):
            self.to = to
            self.subject = subject
            self.html_content = html_content

router = APIRouter(prefix="/api/webhook", tags=["samcart"])

# Configuration
SAMCART_WEBHOOK_SECRET = os.environ.get('SAMCART_WEBHOOK_SECRET', 'default_secret')
TRIAL_PERIOD_DAYS = int(os.environ.get('TRIAL_PERIOD_DAYS', '30'))
MONTHLY_PRICE = float(os.environ.get('MONTHLY_SUBSCRIPTION_PRICE', '49.95'))
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://app.dentalaftercarenotes.com')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@theoncallbot.com')

# Models
class SamCartWebhookLog(BaseModel):
    webhook_id: str
    event_type: str
    payload: Dict[str, Any]
    processing_status: str
    error_message: Optional[str] = None
    created_at: datetime
    processing_duration: Optional[float] = None

class PracticeAccountData(BaseModel):
    practice_name: str
    owner_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Dict[str, str]
    subscription_info: Dict[str, Any]
    login_credentials: Dict[str, str]
    trial_end_date: datetime
    account_status: str = "active"
    created_at: datetime

def verify_samcart_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify SamCart webhook signature"""
    if not signature_header or not SAMCART_WEBHOOK_SECRET:
        print(f"⚠️ Missing signature or secret: sig={bool(signature_header)}, secret={bool(SAMCART_WEBHOOK_SECRET)}")
        return False
    
    try:
        # SamCart typically uses HMAC-SHA256 with different header formats
        # Try multiple signature formats
        expected_signatures = []
        
        # Format 1: sha256=hash
        mac1 = hmac.new(
            SAMCART_WEBHOOK_SECRET.encode('utf-8'),
            payload_body,
            hashlib.sha256
        )
        expected_signatures.append(f"sha256={mac1.hexdigest()}")
        
        # Format 2: just the hash
        expected_signatures.append(mac1.hexdigest())
        
        # Format 3: SHA1 format (some webhooks use this)
        mac2 = hmac.new(
            SAMCART_WEBHOOK_SECRET.encode('utf-8'),
            payload_body,
            hashlib.sha1
        )
        expected_signatures.append(f"sha1={mac2.hexdigest()}")
        expected_signatures.append(mac2.hexdigest())
        
        # Use constant-time comparison
        for expected in expected_signatures:
            if hmac.compare_digest(expected, signature_header):
                print(f"✅ Signature verified with format: {expected[:10]}...")
                return True
        
        print(f"❌ Signature verification failed. Received: {signature_header[:20]}...")
        return False
        
    except Exception as e:
        print(f"❌ Signature verification error: {e}")
        return False

def generate_secure_password(length: int = 12) -> str:
    """Generate a secure, user-friendly password"""
    # Use a mix that's secure but user-friendly (avoid confusing characters)
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    # Ensure password has variety
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in "!@#$%&*" for c in password)
    
    if not all([has_lower, has_upper, has_digit, has_symbol]):
        return generate_secure_password(length)
    
    return password

async def create_practice_from_samcart(samcart_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create practice account from SamCart webhook data"""
    try:
        customer = samcart_data.get("customer", {})
        product = samcart_data.get("product", {})
        order = samcart_data.get("order", {})
        
        # Extract customer information
        first_name = customer.get("first_name", "")
        last_name = customer.get("last_name", "")
        email = customer.get("email", "").lower().strip()
        phone = customer.get("phone_number", "")
        
        if not email:
            raise ValueError("Customer email is required")
        
        # Check if practice already exists
        existing_practice = await db.practices.find_one({"email": email})
        if existing_practice:
            return {
                "status": "duplicate",
                "message": "Practice account already exists",
                "practice_id": str(existing_practice["_id"]),
                "email": email
            }
        
        # Generate secure password
        password = generate_secure_password()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create practice name
        if last_name:
            practice_name = f"Dr. {last_name} Dental Practice"
        else:
            practice_name = f"{first_name} Dental Practice"
        
        # Calculate trial end date
        trial_end = datetime.now(timezone.utc) + timedelta(days=TRIAL_PERIOD_DAYS)
        
        # Create practice document
        practice_data = {
            "id": str(uuid.uuid4()),
            "name": practice_name,
            "email": email,
            "phone": phone,
            "address": customer.get("billing_address_line1", ""),
            "city": customer.get("billing_city", ""),
            "state": customer.get("billing_state", ""),
            "zipCode": customer.get("billing_zip", ""),
            "country": customer.get("billing_country", "United States"),
            
            # Owner information
            "ownerName": f"{first_name} {last_name}".strip(),
            "ownerEmail": email,
            "ownerPhone": phone,
            
            # Subscription information
            "subscription": {
                "status": "trial",
                "type": "monthly",
                "price": MONTHLY_PRICE,
                "trialEndDate": trial_end,
                "currentPeriodEnd": trial_end,
                "samcartOrderId": order.get("id"),
                "samcartCustomerId": customer.get("customer_id"),
                "productName": product.get("name", "Dental Practice Management"),
                "productPrice": product.get("price", "0.00")
            },
            
            # Login credentials
            "password": password_hash,  # Hashed password for login
            
            # Account settings
            "isActive": True,
            "emailVerified": True,  # SamCart email is considered verified
            "setupCompleted": False,  # User needs to complete setup
            
            # Branding (will be set up by user)
            "branding": {
                "logo": None,
                "primaryColor": "#2563eb",
                "secondaryColor": "#1e40af",
                "welcomeMessage": "Welcome to our practice!"
            },
            
            # Metadata
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
            "source": "samcart",
            "samcartData": {
                "orderId": order.get("id"),
                "customerId": customer.get("customer_id"),
                "productId": product.get("id"),
                "originalPayload": samcart_data
            }
        }
        
        # Insert practice into database
        result = await db.practices.insert_one(practice_data)
        practice_id = str(result.inserted_id)
        
        return {
            "status": "success",
            "message": "Practice account created successfully",
            "practice_id": practice_id,
            "email": email,
            "password": password,  # Plain password for email
            "practice_name": practice_name,
            "owner_name": f"{first_name} {last_name}".strip(),
            "trial_end": trial_end
        }
        
    except Exception as e:
        print(f"❌ Error creating practice account: {e}")
        raise e

async def send_welcome_email(practice_info: Dict[str, Any]) -> bool:
    """Send welcome email to new practice owner"""
    try:
        login_url = f"{FRONTEND_URL}/practice/login"
        
        # Create welcome email content
        email_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9fafb;">
            <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #2563eb; margin-bottom: 20px;">Welcome to Dental AfterCare Notes!</h1>
                
                <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
                    Dear {practice_info['owner_name']},
                </p>
                
                <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
                    Congratulations! Your dental practice management account has been successfully created. 
                    You now have access to our comprehensive aftercare notes system.
                </p>
                
                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="color: #1f2937; margin-top: 0;">Your Account Details:</h3>
                    <p style="margin: 5px 0;"><strong>Practice:</strong> {practice_info['practice_name']}</p>
                    <p style="margin: 5px 0;"><strong>Email/Username:</strong> {practice_info['email']}</p>
                    <p style="margin: 5px 0;"><strong>Password:</strong> <code style="background-color: #e5e7eb; padding: 2px 4px; border-radius: 3px;">{practice_info['password']}</code></p>
                    <p style="margin: 5px 0;"><strong>Trial Period:</strong> 30 days (until {practice_info['trial_end'].strftime('%B %d, %Y')})</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{login_url}" style="background-color: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                        Login to Your Account
                    </a>
                </div>
                
                <div style="background-color: #fef3c7; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #f59e0b;">
                    <h3 style="color: #92400e; margin-top: 0;">🔧 Important Next Steps:</h3>
                    <ol style="color: #92400e; margin-left: 20px;">
                        <li style="margin-bottom: 8px;"><strong>Change Your Password:</strong> Go to Practice Settings → Change Password</li>
                        <li style="margin-bottom: 8px;"><strong>Brand Your Practice:</strong> Upload your logo and customize colors in Practice Settings</li>
                        <li style="margin-bottom: 8px;"><strong>Complete Your Profile:</strong> Add practice details, contact information, and emergency contacts</li>
                        <li style="margin-bottom: 8px;"><strong>Watch Tutorials:</strong> Click the "Tutorials" button to learn about all features</li>
                    </ol>
                </div>
                
                <h3 style="color: #1f2937;">📋 What You Get:</h3>
                <ul style="color: #374151; line-height: 1.6;">
                    <li><strong>Professional Aftercare Instructions:</strong> Pre-written, customizable post-op care notes</li>
                    <li><strong>Email & SMS Delivery:</strong> Send instructions directly to patients</li>
                    <li><strong>Print Ready PDFs:</strong> Professional branded documents</li>
                    <li><strong>Patient Management:</strong> Track and manage patient communications</li>
                    <li><strong>Custom Branding:</strong> Your logo and colors on all materials</li>
                </ul>
                
                <h3 style="color: #1f2937;">💰 Pricing Information:</h3>
                <ul style="color: #374151; line-height: 1.6;">
                    <li><strong>Setup:</strong> Free</li>
                    <li><strong>Trial Period:</strong> 30 days free</li>
                    <li><strong>Monthly Subscription:</strong> $49.95/month after trial</li>
                    <li><strong>Upgrades:</strong> Free</li>
                    <li><strong>Cancellation:</strong> Cancel anytime</li>
                </ul>
                
                <div style="background-color: #ecfdf5; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #10b981;">
                    <h3 style="color: #047857; margin-top: 0;">📞 Need Help?</h3>
                    <p style="color: #047857; margin-bottom: 10px;">Our support team is here to help you get started:</p>
                    <ul style="color: #047857; margin-left: 20px;">
                        <li>Email: <a href="mailto:support@dentalaftercarenotes.com" style="color: #047857;">support@dentalaftercarenotes.com</a></li>
                        <li>Watch our tutorial videos in your dashboard</li>
                        <li>Check our help documentation</li>
                    </ul>
                </div>
                
                <p style="font-size: 14px; color: #6b7280; text-align: center; margin-top: 30px;">
                    Thank you for choosing Dental AfterCare Notes!<br>
                    We're excited to help you provide excellent patient care.
                </p>
            </div>
        </div>
        """
        
        # Send email using existing email service
        email_data = EmailData(
            to=[practice_info['email']],
            subject=f"Welcome to Dental AfterCare Notes - {practice_info['practice_name']}",
            html_content=email_content
        )
        
        success = await send_email(email_data)
        
        if success:
            print(f"✅ Welcome email sent to {practice_info['email']}")
        else:
            print(f"❌ Failed to send welcome email to {practice_info['email']}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error sending welcome email: {e}")
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
                    "practice_name": result["practice_name"]
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