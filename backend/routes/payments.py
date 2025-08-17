from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
import os
import jwt
from datetime import datetime, timedelta
import uuid
from typing import Optional, Dict, Any
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

router = APIRouter(prefix="/api/payments/v1", tags=["payments"])
security = HTTPBearer()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

# Stripe setup
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-super-secret-jwt-key-change-in-production')

# Fixed pricing packages
PACKAGES = {
    "monthly_subscription": 49.0  # $49/month after trial
}

# Pydantic models
class CheckoutRequest(BaseModel):
    package_id: str = Field(..., description="Package ID (monthly_subscription)")
    origin_url: str = Field(..., description="Frontend origin URL")
    practice_id: Optional[str] = Field(None, description="Practice ID for authenticated users")

class PaymentTransaction(BaseModel):
    id: str
    session_id: str
    practice_id: Optional[str]
    amount: float
    currency: str
    package_id: str
    payment_status: str  # pending, paid, failed, expired
    stripe_status: str   # Stripe's checkout session status
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

# Helper function to get user from token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
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

@router.post("/checkout/session")
async def create_checkout_session(request: CheckoutRequest, http_request: Request):
    """Create a Stripe checkout session for practice subscription"""
    try:
        # Validate package
        if request.package_id not in PACKAGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid package selected"
            )
        
        # Get amount from server-side definition
        amount = PACKAGES[request.package_id]
        
        # Build URLs from frontend origin
        success_url = f"{request.origin_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{request.origin_url}/payment-cancelled"
        
        # Setup Stripe
        host_url = str(http_request.base_url)
        webhook_url = f"{host_url}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Create metadata
        metadata = {
            "source": "dental_practice_registration",
            "package_id": request.package_id,
            "practice_id": request.practice_id or "new_practice",
            "amount": str(amount),
            "currency": "usd"
        }
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=amount,
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record
        transaction_id = str(uuid.uuid4())
        transaction = {
            "id": transaction_id,
            "session_id": session.session_id,
            "practice_id": request.practice_id,
            "amount": amount,
            "currency": "usd",
            "package_id": request.package_id,
            "payment_status": "pending",
            "stripe_status": "open",
            "metadata": metadata,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.payment_transactions.insert_one(transaction)
        
        return {
            "success": True,
            "url": session.url,
            "session_id": session.session_id,
            "transaction_id": transaction_id
        }
        
    except Exception as e:
        print(f"Checkout session creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )

@router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str, http_request: Request):
    """Get payment status for a checkout session"""
    try:
        # Setup Stripe
        host_url = str(http_request.base_url)
        webhook_url = f"{host_url}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Get status from Stripe
        checkout_status = await stripe_checkout.get_checkout_status(session_id)
        
        # Find transaction in database
        transaction = await db.payment_transactions.find_one({"session_id": session_id})
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        # Update transaction status if changed and not already processed
        updated = False
        if (checkout_status.payment_status == "paid" and 
            transaction["payment_status"] != "paid"):
            
            # Activate practice subscription
            if transaction["practice_id"] and transaction["practice_id"] != "new_practice":
                await db.practices.update_one(
                    {"id": transaction["practice_id"]},
                    {
                        "$set": {
                            "subscription.status": "active",
                            "subscription.stripeSessionId": session_id,
                            "subscription.currentPeriodEnd": datetime.utcnow() + timedelta(days=30),
                            "updatedAt": datetime.utcnow()
                        }
                    }
                )
            
            # Update transaction
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "payment_status": "paid",
                        "stripe_status": checkout_status.status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            updated = True
            
        elif checkout_status.status == "expired" and transaction["payment_status"] != "expired":
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "payment_status": "expired",
                        "stripe_status": checkout_status.status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            updated = True
        
        return {
            "success": True,
            "session_id": session_id,
            "status": checkout_status.status,
            "payment_status": checkout_status.payment_status,
            "amount_total": checkout_status.amount_total,
            "currency": checkout_status.currency,
            "metadata": checkout_status.metadata,
            "updated": updated
        }
        
    except Exception as e:
        print(f"Checkout status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get checkout status"
        )

@router.get("/transactions")
async def get_user_transactions(user_data = Depends(get_current_user)):
    """Get payment transactions for authenticated user's practice"""
    try:
        practice_id = user_data.get('practiceId')
        if not practice_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No practice associated with user"
            )
        
        transactions = await db.payment_transactions.find(
            {"practice_id": practice_id},
            {"_id": 0}
        ).to_list(length=None)
        
        return {
            "success": True,
            "transactions": transactions
        }
        
    except Exception as e:
        print(f"Get transactions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transactions"
        )