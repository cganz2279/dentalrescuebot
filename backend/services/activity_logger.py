import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import uuid
from typing import Optional

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

class ActivityLogger:
    """
    Service for logging patient activity (PDF print, email, SMS)
    """
    
    @staticmethod
    async def log_activity(
        practice_id: str,
        patient_id: str,
        patient_name: str,
        patient_email: str,
        procedure_id: str,
        procedure_name: str,
        dentist_name: str,
        activity_type: str,  # 'print', 'email', 'sms'
        user_id: str,
        additional_data: Optional[dict] = None
    ):
        """
        Log patient activity to database
        
        Args:
            practice_id: Practice ID
            patient_id: Patient ID
            patient_name: Patient full name
            patient_email: Patient email
            procedure_id: Procedure assignment ID
            procedure_name: Name of the procedure
            dentist_name: Name of the dentist
            activity_type: Type of activity ('print', 'email', 'sms')
            user_id: ID of the user who performed the action
            additional_data: Additional data (e.g., email address, phone number)
        
        Returns:
            str: Activity log ID
        """
        try:
            activity_id = str(uuid.uuid4())
            
            activity_doc = {
                "id": activity_id,
                "practiceId": practice_id,
                "patientId": patient_id,
                "patientName": patient_name,
                "patientEmail": patient_email,
                "procedureId": procedure_id,
                "procedureName": procedure_name,
                "dentistName": dentist_name,
                "activityType": activity_type,
                "performedBy": user_id,
                "performedAt": datetime.now(timezone.utc),
                "additionalData": additional_data or {}
            }
            
            await db.activity_logs.insert_one(activity_doc)
            
            print(f"✅ Activity logged: {activity_type} - {procedure_name} for {patient_name}")
            return activity_id
            
        except Exception as e:
            print(f"❌ Error logging activity: {e}")
            raise Exception(f"Failed to log activity: {str(e)}")
    
    @staticmethod
    async def get_activities_by_date_range(
        practice_id: str,
        start_date: datetime,
        end_date: datetime,
        activity_types: Optional[list] = None
    ):
        """
        Get activities within a date range
        
        Args:
            practice_id: Practice ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            activity_types: List of activity types to filter by
        
        Returns:
            list: List of activity documents
        """
        try:
            # Build query
            query = {
                "practiceId": practice_id,
                "performedAt": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            if activity_types:
                query["activityType"] = {"$in": activity_types}
            
            # Get activities
            activities = await db.activity_logs.find(
                query,
                {"_id": 0}
            ).sort("performedAt", -1).to_list(length=None)
            
            return activities
            
        except Exception as e:
            print(f"❌ Error getting activities: {e}")
            raise Exception(f"Failed to get activities: {str(e)}")
    
    @staticmethod
    async def get_activity_stats(practice_id: str, days: int = 30):
        """
        Get activity statistics for the past N days
        
        Args:
            practice_id: Practice ID
            days: Number of days to look back
        
        Returns:
            dict: Activity statistics
        """
        try:
            from datetime import timedelta
            
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Get all activities in the date range
            activities = await db.activity_logs.find(
                {
                    "practiceId": practice_id,
                    "performedAt": {"$gte": start_date}
                }
            ).to_list(length=None)
            
            # Calculate stats
            stats = {
                "total": len(activities),
                "print": len([a for a in activities if a["activityType"] == "print"]),
                "email": len([a for a in activities if a["activityType"] == "email"]),
                "sms": len([a for a in activities if a["activityType"] == "sms"]),
                "unique_patients": len(set([a["patientId"] for a in activities])),
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": datetime.now(timezone.utc).isoformat()
                }
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting activity stats: {e}")
            raise Exception(f"Failed to get activity stats: {str(e)}")

# Global activity logger instance
activity_logger = ActivityLogger()