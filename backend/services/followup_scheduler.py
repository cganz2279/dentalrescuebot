"""
Follow-up Email Scheduler Service
Handles automated follow-up emails 24 hours after procedures are marked as delivered
"""

import asyncio
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from database import db
from services.email_service import send_email, EmailData
import uuid

class FollowUpScheduler:
    def __init__(self):
        self.scheduler_running = False
        
    async def start_scheduler(self):
        """Start the background follow-up email scheduler"""
        if self.scheduler_running:
            return
            
        self.scheduler_running = True
        print("🕒 Follow-up email scheduler started")
        
        # Run scheduler check every 10 minutes
        while self.scheduler_running:
            try:
                await self.process_pending_followups()
                await asyncio.sleep(600)  # 10 minutes
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                await asyncio.sleep(600)
                
    async def stop_scheduler(self):
        """Stop the background scheduler"""
        self.scheduler_running = False
        print("🛑 Follow-up email scheduler stopped")
        
    async def schedule_followup_email(self, assignment_id: str, practice_id: str):
        """Schedule a follow-up email for a delivered procedure"""
        try:
            # Get procedure assignment details
            assignment = await db.patientprocedures.find_one({
                "id": assignment_id,
                "practiceId": practice_id
            })
            
            if not assignment:
                print(f"❌ Assignment not found: {assignment_id}")
                return False
            
            # Calculate follow-up time (24 hours from now)
            followup_time = datetime.now(timezone.utc) + timedelta(hours=24)
            
            # Create follow-up schedule record
            followup_record = {
                "id": str(uuid.uuid4()),
                "assignmentId": assignment_id,
                "practiceId": practice_id,
                "patientId": assignment.get("patientId"),
                "patientName": assignment.get("patientName"),
                "patientEmail": assignment.get("patientEmail"),
                "procedureName": assignment.get("procedureName"),
                "deliveredAt": datetime.now(timezone.utc),
                "scheduledFor": followup_time,
                "status": "scheduled",  # scheduled, sent, failed, cancelled
                "emailSent": False,
                "createdAt": datetime.now(timezone.utc),
                "updatedAt": datetime.now(timezone.utc)
            }
            
            # Insert follow-up record
            await db.followup_emails.insert_one(followup_record)
            
            # Update assignment with follow-up info
            await db.patientprocedures.update_one(
                {"id": assignment_id},
                {
                    "$set": {
                        "followUpScheduled": True,
                        "followUpScheduledAt": followup_time,
                        "followUpStatus": "scheduled",
                        "updatedAt": datetime.now(timezone.utc)
                    }
                }
            )
            
            print(f"✅ Follow-up email scheduled for {assignment.get('patientName')} - {assignment.get('procedureName')} at {followup_time}")
            return True
            
        except Exception as e:
            print(f"❌ Error scheduling follow-up email: {e}")
            return False
            
    async def process_pending_followups(self):
        """Process all pending follow-up emails that are due"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # Find follow-ups that are due
            pending_followups = await db.followup_emails.find({
                "status": "scheduled",
                "scheduledFor": {"$lte": current_time},
                "emailSent": False
            }).to_list(length=None)
            
            print(f"🔍 Found {len(pending_followups)} pending follow-up emails")
            
            for followup in pending_followups:
                success = await self.send_followup_email(followup)
                if success:
                    # Update status to sent
                    await db.followup_emails.update_one(
                        {"id": followup["id"]},
                        {
                            "$set": {
                                "status": "sent",
                                "emailSent": True,
                                "sentAt": datetime.now(timezone.utc),
                                "updatedAt": datetime.now(timezone.utc)
                            }
                        }
                    )
                    
                    # Update original assignment - change status from "delivered" to "second"
                    await db.patientprocedures.update_one(
                        {"id": followup["assignmentId"]},
                        {
                            "$set": {
                                "status": "second",  # Change from delivered to second
                                "followUpStatus": "sent",
                                "followUpSentAt": datetime.now(timezone.utc),
                                "updatedAt": datetime.now(timezone.utc)
                            }
                        }
                    )
                else:
                    # Mark as failed
                    await db.followup_emails.update_one(
                        {"id": followup["id"]},
                        {
                            "$set": {
                                "status": "failed",
                                "failedAt": datetime.now(timezone.utc),
                                "updatedAt": datetime.now(timezone.utc)
                            }
                        }
                    )
                    
        except Exception as e:
            print(f"❌ Error processing pending follow-ups: {e}")
            
    async def send_followup_email(self, followup: Dict[str, Any]) -> bool:
        """Send the actual follow-up email"""
        try:
            # Get practice information for email template (including branding for logo)
            practice = await db.practices.find_one({
                "id": followup["practiceId"]
            }, {
                "_id": 0,
                "name": 1,
                "phone": 1,
                "ownerName": 1,
                "email": 1,
                "branding": 1
            })
            
            if not practice:
                print(f"❌ Practice not found: {followup['practiceId']}")
                return False
            
            # Extract practice details
            practice_name = practice.get("name", "Our Dental Practice")
            practice_phone = practice.get("phone", "")
            dentist_name = practice.get("ownerName", "Dr. Smith")
            practice_email = practice.get("email", "office@dentalpractice.com")
            
            # Get practice logo for email header
            logo_html = ""
            if practice.get("branding", {}).get("logo"):
                logo_data = practice["branding"]["logo"]
                # Ensure logo is in proper data URL format
                if not logo_data.startswith('data:image'):
                    logo_data = f"data:image/png;base64,{logo_data}"
                
                logo_html = f"""
                <div style="text-align: center; margin-bottom: 25px;">
                    <img src="{logo_data}" alt="{practice_name} Logo" style="max-width: 200px; max-height: 100px; object-fit: contain;" />
                </div>
                """
            
            # Create follow-up email content
            email_subject = "Just Checking In – How Are You Feeling After Your Visit?"
            
            email_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9fafb;">
                <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    {logo_html}
                    <h2 style="color: #2563eb; margin-bottom: 20px; text-align: center;">Just Checking In</h2>
                    
                    <p style="font-size: 16px; color: #374151; margin-bottom: 20px;">
                        Dear {followup.get('patientName', 'Patient')},
                    </p>
                    
                    <p style="font-size: 16px; color: #374151; margin-bottom: 20px; line-height: 1.6;">
                        I hope this message finds you well. I wanted to follow up regarding the <strong>{followup.get('procedureName', 'procedure')}</strong> you had in our office yesterday. My main concern is your comfort and recovery.
                    </p>
                    
                    <p style="font-size: 16px; color: #374151; margin-bottom: 20px; line-height: 1.6;">
                        Have you been doing alright since your visit? If you have any questions, concerns, or if you feel you need additional instructions beyond what we provided, please don't hesitate to reach out. Your health and peace of mind are very important to us.
                    </p>
                    
                    <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #2563eb;">
                        <h3 style="color: #1f2937; margin-top: 0;">📞 How to Reach Us:</h3>
                        <p style="margin: 5px 0; color: #374151;"><strong>Reply to this email</strong> for non-urgent questions</p>
                        <p style="margin: 5px 0; color: #374151;"><strong>Call our office:</strong> {practice_phone}</p>
                        <p style="margin: 5px 0; color: #374151; font-size: 14px;">We'll be happy to assist you with any concerns.</p>
                    </div>
                    
                    <p style="font-size: 16px; color: #374151; margin-bottom: 30px; line-height: 1.6;">
                        Thank you for allowing us to care for you. Wishing you a smooth and comfortable recovery.
                    </p>
                    
                    <div style="border-top: 1px solid #e5e7eb; padding-top: 20px; margin-top: 30px;">
                        <p style="margin: 5px 0; color: #374151;"><strong>Warm regards,</strong></p>
                        <p style="margin: 5px 0; color: #2563eb; font-weight: bold;">{dentist_name}</p>
                        <p style="margin: 5px 0; color: #6b7280;">{practice_name}</p>
                        <p style="margin: 5px 0; color: #6b7280;">{practice_phone}</p>
                    </div>
                    
                    <div style="background-color: #f9fafb; padding: 15px; border-radius: 6px; margin-top: 25px;">
                        <p style="font-size: 12px; color: #6b7280; text-align: center; margin: 0;">
                            This is an automated follow-up message from {practice_name}.<br>
                            If you have urgent concerns, please call our office directly.
                        </p>
                    </div>
                </div>
            </div>
            """
            
            # Send email using existing email service
            email_data = EmailData(
                to=[followup.get('patientEmail')],
                subject=email_subject,
                html_content=email_content,
                from_email=practice_email
            )
            
            success = await send_email(email_data)
            
            if success:
                print(f"✅ Follow-up email sent to {followup.get('patientName')} ({followup.get('patientEmail')})")
                print(f"📈 Status progression: delivered → second for {followup.get('procedureName')}")
                
                # Log the email activity
                await self.log_followup_activity(followup, "email_sent", {
                    "subject": email_subject,
                    "recipient": followup.get('patientEmail'),
                    "practice": practice_name,
                    "dentist": dentist_name,
                    "status_change": "delivered → second"
                })
            else:
                print(f"❌ Failed to send follow-up email to {followup.get('patientName')} ({followup.get('patientEmail')})")
                
                # Log the failure
                await self.log_followup_activity(followup, "email_failed", {
                    "recipient": followup.get('patientEmail'),
                    "error": "Email delivery failed"
                })
            
            return success
            
        except Exception as e:
            print(f"❌ Error sending follow-up email: {e}")
            await self.log_followup_activity(followup, "email_error", {
                "error": str(e)
            })
            return False
            
    async def log_followup_activity(self, followup: Dict[str, Any], activity_type: str, details: Dict[str, Any]):
        """Log follow-up email activity for audit trail"""
        try:
            log_record = {
                "id": str(uuid.uuid4()),
                "followupId": followup.get("id"),
                "assignmentId": followup.get("assignmentId"),
                "practiceId": followup.get("practiceId"),
                "patientId": followup.get("patientId"),
                "activityType": activity_type,  # email_sent, email_failed, email_error
                "details": details,
                "timestamp": datetime.now(timezone.utc),
                "createdAt": datetime.now(timezone.utc)
            }
            
            await db.followup_activity_log.insert_one(log_record)
            print(f"📝 Logged follow-up activity: {activity_type} for {followup.get('patientName')}")
            
        except Exception as e:
            print(f"❌ Error logging follow-up activity: {e}")
            
    async def get_followup_stats(self, practice_id: str) -> Dict[str, Any]:
        """Get follow-up email statistics for a practice"""
        try:
            # Count follow-ups by status
            scheduled = await db.followup_emails.count_documents({
                "practiceId": practice_id,
                "status": "scheduled"
            })
            
            sent = await db.followup_emails.count_documents({
                "practiceId": practice_id,
                "status": "sent"
            })
            
            failed = await db.followup_emails.count_documents({
                "practiceId": practice_id,
                "status": "failed"
            })
            
            # Count procedures by sequence status
            active_procedures = await db.patientprocedures.count_documents({
                "practiceId": practice_id,
                "status": "active"
            })
            
            delivered_procedures = await db.patientprocedures.count_documents({
                "practiceId": practice_id,
                "status": "delivered"
            })
            
            second_procedures = await db.patientprocedures.count_documents({
                "practiceId": practice_id,
                "status": "second"
            })
            
            # Get recent follow-up activity
            recent_activity = await db.followup_activity_log.find({
                "practiceId": practice_id
            }).sort("timestamp", -1).limit(10).to_list(length=10)
            
            return {
                "scheduled": scheduled,
                "sent": sent,
                "failed": failed,
                "total": scheduled + sent + failed,
                "success_rate": (sent / (sent + failed) * 100) if (sent + failed) > 0 else 0,
                "procedure_stats": {
                    "active": active_procedures,
                    "delivered": delivered_procedures,
                    "second": second_procedures,
                    "total": active_procedures + delivered_procedures + second_procedures
                },
                "recent_activity": recent_activity
            }
            
        except Exception as e:
            print(f"❌ Error getting follow-up stats: {e}")
            return {
                "scheduled": 0,
                "sent": 0,
                "failed": 0,
                "total": 0,
                "success_rate": 0,
                "recent_activity": []
            }

# Global scheduler instance
followup_scheduler = FollowUpScheduler()

async def start_followup_scheduler():
    """Start the global follow-up scheduler"""
    await followup_scheduler.start_scheduler()

async def stop_followup_scheduler():
    """Stop the global follow-up scheduler"""
    await followup_scheduler.stop_scheduler()