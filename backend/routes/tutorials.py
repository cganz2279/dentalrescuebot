from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
from datetime import datetime
import jwt
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from database import db

router = APIRouter()
security = HTTPBearer()

# Pydantic models
class Tutorial(BaseModel):
    id: str
    title: str
    description: str
    video_url: str
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None  # in seconds
    category: Optional[str] = "general"
    order: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class TutorialCreate(BaseModel):
    title: str
    description: str
    category: Optional[str] = "general"
    order: int = 0

class TutorialUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None

# Helper function to verify admin token
async def verify_admin_token(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, os.environ.get('JWT_SECRET', 'default_secret'), algorithms=["HS256"])
        admin_email = payload.get("adminEmail")
        if not admin_email:
            raise HTTPException(status_code=401, detail="Invalid token")
        return admin_email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Get all active tutorials (for practice users)
@router.get("/api/tutorials", response_model=List[Tutorial])
async def get_tutorials():
    """Get all active tutorials for practice users"""
    try:
        tutorials = await db.tutorials.find({"is_active": True}).sort("order", 1).to_list(length=None)
        
        result = []
        for tutorial in tutorials:
            tutorial_dict = {
                "id": str(tutorial["_id"]),
                "title": tutorial.get("title", ""),
                "description": tutorial.get("description", ""),
                "video_url": tutorial.get("video_url", ""),
                "thumbnail_url": tutorial.get("thumbnail_url"),
                "duration": tutorial.get("duration"),
                "category": tutorial.get("category", "general"),
                "order": tutorial.get("order", 0),
                "is_active": tutorial.get("is_active", True),
                "created_at": tutorial.get("created_at", datetime.utcnow()),
                "updated_at": tutorial.get("updated_at", datetime.utcnow())
            }
            result.append(Tutorial(**tutorial_dict))
        
        return result
    except Exception as e:
        print(f"Error fetching tutorials: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tutorials")

# Admin endpoints
@router.get("/api/admin/tutorials", response_model=List[Tutorial])
async def get_all_tutorials_admin(admin_email: str = Depends(verify_admin_token)):
    """Get all tutorials for admin management (including inactive)"""
    try:
        tutorials = await db.tutorials.find().sort("order", 1).to_list(length=None)
        
        result = []
        for tutorial in tutorials:
            tutorial_dict = {
                "id": str(tutorial["_id"]),
                "title": tutorial.get("title", ""),
                "description": tutorial.get("description", ""),
                "video_url": tutorial.get("video_url", ""),
                "thumbnail_url": tutorial.get("thumbnail_url"),
                "duration": tutorial.get("duration"),
                "category": tutorial.get("category", "general"),
                "order": tutorial.get("order", 0),
                "is_active": tutorial.get("is_active", True),
                "created_at": tutorial.get("created_at", datetime.utcnow()),
                "updated_at": tutorial.get("updated_at", datetime.utcnow())
            }
            result.append(Tutorial(**tutorial_dict))
        
        return result
    except Exception as e:
        print(f"Error fetching tutorials for admin: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tutorials")

@router.post("/api/admin/tutorials")
async def create_tutorial(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form("general"),
    order: int = Form(0),
    video: UploadFile = File(...),
    admin_email: str = Depends(verify_admin_token)
):
    """Create a new tutorial with video upload"""
    try:
        # Validate video file
        if not video.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Create uploads directory if it doesn't exist
        uploads_dir = "/app/uploads/tutorials"
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(video.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(uploads_dir, unique_filename)
        
        # Save video file
        with open(file_path, "wb") as buffer:
            content = await video.read()
            buffer.write(content)
        
        # Create video URL (relative to serve from static files)
        video_url = f"/uploads/tutorials/{unique_filename}"
        
        # Create tutorial document
        tutorial_doc = {
            "title": title,
            "description": description,
            "video_url": video_url,
            "category": category,
            "order": order,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.tutorials.insert_one(tutorial_doc)
        
        return {
            "success": True,
            "tutorial_id": str(result.inserted_id),
            "message": "Tutorial created successfully"
        }
        
    except Exception as e:
        print(f"Error creating tutorial: {e}")
        raise HTTPException(status_code=500, detail="Failed to create tutorial")

@router.put("/api/admin/tutorials/{tutorial_id}")
async def update_tutorial(
    tutorial_id: str,
    tutorial_update: TutorialUpdate,
    admin_email: str = Depends(verify_admin_token)
):
    """Update an existing tutorial"""
    try:
        # Validate tutorial ID
        if not ObjectId.is_valid(tutorial_id):
            raise HTTPException(status_code=400, detail="Invalid tutorial ID")
        
        # Build update document
        update_doc = {"updated_at": datetime.utcnow()}
        
        if tutorial_update.title is not None:
            update_doc["title"] = tutorial_update.title
        if tutorial_update.description is not None:
            update_doc["description"] = tutorial_update.description
        if tutorial_update.category is not None:
            update_doc["category"] = tutorial_update.category
        if tutorial_update.order is not None:
            update_doc["order"] = tutorial_update.order
        if tutorial_update.is_active is not None:
            update_doc["is_active"] = tutorial_update.is_active
        
        # Update tutorial
        result = await db.tutorials.update_one(
            {"_id": ObjectId(tutorial_id)},
            {"$set": update_doc}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Tutorial not found")
        
        return {"success": True, "message": "Tutorial updated successfully"}
        
    except Exception as e:
        print(f"Error updating tutorial: {e}")
        raise HTTPException(status_code=500, detail="Failed to update tutorial")

@router.delete("/api/admin/tutorials/{tutorial_id}")
async def delete_tutorial(
    tutorial_id: str,
    admin_email: str = Depends(verify_admin_token)
):
    """Delete a tutorial"""
    try:
        # Validate tutorial ID
        if not ObjectId.is_valid(tutorial_id):
            raise HTTPException(status_code=400, detail="Invalid tutorial ID")
        
        # Get tutorial to delete video file
        tutorial = await db.tutorials.find_one({"_id": ObjectId(tutorial_id)})
        if not tutorial:
            raise HTTPException(status_code=404, detail="Tutorial not found")
        
        # Delete video file if it exists
        video_url = tutorial.get("video_url", "")
        if video_url.startswith("/uploads/tutorials/"):
            file_path = f"/app{video_url}"
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Delete tutorial from database
        await db.tutorials.delete_one({"_id": ObjectId(tutorial_id)})
        
        return {"success": True, "message": "Tutorial deleted successfully"}
        
    except Exception as e:
        print(f"Error deleting tutorial: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete tutorial")