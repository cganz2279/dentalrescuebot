from fastapi import APIRouter, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timedelta
from emergentintegrations.payments.stripe.checkout import StripeCheckout
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

router = APIRouter(prefix="/webhook", tags=["webhooks"])

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

# Stripe setup
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

@router.post("/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        # Get the raw body and signature
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        
        # Setup Stripe
        host_url = str(request.base_url)
        webhook_url = f"{host_url}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        # Handle webhook
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Process the webhook event
        if webhook_response.event_type == "checkout.session.completed":
            session_id = webhook_response.session_id
            
            # Find transaction
            transaction = await db.payment_transactions.find_one({"session_id": session_id})
            
            if transaction and transaction["payment_status"] != "paid":
                # Update transaction status
                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {
                        "$set": {
                            "payment_status": "paid",
                            "stripe_status": "complete",
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                # Activate practice subscription
                practice_id = transaction.get("practice_id")
                if practice_id and practice_id != "new_practice":
                    await db.practices.update_one(
                        {"id": practice_id},
                        {
                            "$set": {
                                "subscription.status": "active",
                                "subscription.stripeSessionId": session_id,
                                "subscription.currentPeriodEnd": datetime.utcnow() + timedelta(days=30),
                                "updatedAt": datetime.utcnow()
                            }
                        }
                    )
                
                print(f"Successfully processed payment for session: {session_id}")
        
        elif webhook_response.event_type == "checkout.session.expired":
            session_id = webhook_response.session_id
            
            # Update transaction status
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "payment_status": "expired",
                        "stripe_status": "expired",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            print(f"Payment session expired: {session_id}")
        
        return {"received": True}
        
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )