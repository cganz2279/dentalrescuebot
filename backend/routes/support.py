from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
import uuid
from datetime import datetime, timezone
import os
from database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/support", tags=["support"])

class SupportRequest(BaseModel):
    practice_name: str
    email: EmailStr
    phone: Optional[str] = None
    support: bool = False
    suggestions: bool = False
    description: str
    
    @validator('description')
    def validate_description(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Description must be at least 10 characters long')
        if len(v) > 2000:
            raise ValueError('Description cannot exceed 2000 characters')
        return v.strip()
    
    @validator('support', 'suggestions')
    def validate_checkboxes(cls, v, values):
        # This will be checked after both fields are validated
        return v
    
    @validator('suggestions')
    def validate_at_least_one_checkbox(cls, v, values):
        support = values.get('support', False)
        if not support and not v:
            raise ValueError('Please select at least one option: Support or Suggestions')
        return v

class SupportRequestResponse(BaseModel):
    id: str
    practice_id: str
    practice_name: str
    email: str
    phone: Optional[str]
    support: bool
    suggestions: bool
    description: str
    created_at: datetime
    status: str

@router.post("/request", response_model=dict)
async def create_support_request(
    request: SupportRequest,
    current_user = Depends(get_current_user)
):
    """Create a new support request"""
    try:
        # Create support request document
        support_doc = {
            "id": str(uuid.uuid4()),
            "practice_id": current_user["practice_id"],
            "practice_name": request.practice_name,
            "email": request.email,
            "phone": request.phone,
            "support": request.support,
            "suggestions": request.suggestions,
            "description": request.description,
            "created_at": datetime.now(timezone.utc),
            "status": "open"
        }
        
        # Insert into database
        await db.support_requests.insert_one(support_doc)
        
        # Send email notification
        await send_support_email(support_doc)
        
        return {
            "success": True,
            "message": "Support request submitted successfully",
            "id": support_doc["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit support request: {str(e)}")

@router.get("/requests", response_model=List[SupportRequestResponse])
async def get_support_requests(
    current_user = Depends(get_current_user)
):
    """Get support requests for the current practice"""
    try:
        # Get support requests for this practice
        cursor = db.support_requests.find(
            {"practice_id": current_user["practice_id"]}
        ).sort("created_at", -1)
        
        requests = await cursor.to_list(length=100)
        
        return [SupportRequestResponse(**req) for req in requests]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch support requests: {str(e)}")

@router.get("/admin/all-requests", response_model=List[SupportRequestResponse])
async def get_all_support_requests():
    """Get all support requests for admin panel (no auth required for admin)"""
    try:
        # Get all support requests
        cursor = db.support_requests.find({}).sort("created_at", -1)
        requests = await cursor.to_list(length=1000)
        
        return [SupportRequestResponse(**req) for req in requests]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch all support requests: {str(e)}")

async def send_support_email(support_doc: dict):
    """Send support request email using SendGrid"""
    try:
        from services.email_service import EmailService
        
        email_service = EmailService()
        
        # Determine request type
        request_types = []
        if support_doc["support"]:
            request_types.append("Support")
        if support_doc["suggestions"]:
            request_types.append("Suggestions")
        
        request_type_str = " & ".join(request_types)
        
        # Create email content
        subject = f"New {request_type_str} Request from {support_doc['practice_name']}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h2 style="color: #2563eb; margin-bottom: 20px;">New Support Request</h2>
                
                <div style="background-color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="margin-top: 0; color: #374151;">Request Details</h3>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; width: 150px;">Date & Time:</td>
                            <td style="padding: 8px 0;">{support_doc['created_at'].strftime('%B %d, %Y at %I:%M %p UTC')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Practice Name:</td>
                            <td style="padding: 8px 0;">{support_doc['practice_name']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Email:</td>
                            <td style="padding: 8px 0;"><a href="mailto:{support_doc['email']}">{support_doc['email']}</a></td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Phone:</td>
                            <td style="padding: 8px 0;">{support_doc['phone'] or 'Not provided'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold;">Request Type:</td>
                            <td style="padding: 8px 0;">{request_type_str}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: white; padding: 20px; border-radius: 8px;">
                    <h3 style="margin-top: 0; color: #374151;">Description</h3>
                    <div style="background-color: #f9fafb; padding: 15px; border-radius: 6px; border-left: 4px solid #2563eb;">
                        {support_doc['description'].replace(chr(10), '<br>')}
                    </div>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background-color: #dbeafe; border-radius: 8px;">
                    <p style="margin: 0; color: #1e40af; font-size: 14px;">
                        <strong>Practice ID:</strong> {support_doc['practice_id']}<br>
                        <strong>Request ID:</strong> {support_doc['id']}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email
        success = await email_service.send_custom_email(
            to_email="support@dentalaftercarenotes.com",
            subject=subject,
            html_content=html_content,
            from_email=support_doc['email'],
            from_name=support_doc['practice_name']
        )
        
        if success:
            print(f"✅ Support email sent successfully for request {support_doc['id']}")
        else:
            print(f"❌ Failed to send support email for request {support_doc['id']}")
            
    except Exception as e:
        print(f"❌ Error sending support email: {str(e)}")
        # Don't raise exception here - we don't want to fail the request if email fails