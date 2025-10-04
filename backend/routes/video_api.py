"""
Video API for serving tutorial videos
Workaround for reverse proxy routing issues with /uploads/* paths
"""

from fastapi import APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import StreamingResponse, FileResponse
import os
import stat
from pathlib import Path
import mimetypes
from typing import Optional
from .admin import verify_admin_token

router = APIRouter(prefix="/api/video", tags=["video"])

UPLOADS_DIR = "/app/uploads/tutorials"

@router.get("/tutorial/{filename}")
@router.head("/tutorial/{filename}")
async def serve_tutorial_video(
    filename: str, 
    request: Request,
    admin_data: dict = Depends(verify_admin_token)
):
    """
    Serve tutorial video files with proper streaming support
    Workaround for reverse proxy routing /uploads/* to frontend
    """
    try:
        # Validate filename (security)
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Ensure only video files
        if not filename.lower().endswith(('.mp4', '.webm', '.mov', '.avi')):
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Build file path
        file_path = Path(UPLOADS_DIR) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        # Get file info
        file_size = file_path.stat().st_size
        
        # Get MIME type
        content_type, _ = mimetypes.guess_type(str(file_path))
        if not content_type:
            content_type = "video/mp4"  # Default for video
        
        print(f"🎬 Serving video: {filename} ({file_size} bytes, {content_type})")
        
        # Check for Range header (video streaming support)
        range_header = request.headers.get("range")
        
        if range_header:
            # Handle range requests for video streaming
            return handle_range_request(file_path, file_size, range_header, content_type)
        else:
            # Return full file
            return FileResponse(
                path=str(file_path),
                media_type=content_type,
                filename=filename,
                headers={
                    "Accept-Ranges": "bytes",
                    "Cache-Control": "public, max-age=3600",
                    "Content-Length": str(file_size)
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error serving video {filename}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def handle_range_request(file_path: Path, file_size: int, range_header: str, content_type: str):
    """Handle HTTP Range requests for video streaming"""
    try:
        # Parse range header (e.g., "bytes=0-1023")
        if not range_header.startswith("bytes="):
            raise HTTPException(status_code=400, detail="Invalid range header")
        
        range_value = range_header[6:]  # Remove "bytes="
        
        if "-" not in range_value:
            raise HTTPException(status_code=400, detail="Invalid range format")
        
        range_start, range_end = range_value.split("-", 1)
        
        # Parse start and end
        start = int(range_start) if range_start else 0
        end = int(range_end) if range_end else file_size - 1
        
        # Validate range
        if start >= file_size or end >= file_size or start > end:
            raise HTTPException(status_code=416, detail="Range not satisfiable")
        
        chunk_size = end - start + 1
        
        print(f"🎬 Range request: {start}-{end}/{file_size} ({chunk_size} bytes)")
        
        def generate_chunk():
            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = chunk_size
                while remaining > 0:
                    chunk = f.read(min(8192, remaining))  # 8KB chunks
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk
        
        return StreamingResponse(
            generate_chunk(),
            status_code=206,  # Partial Content
            media_type=content_type,
            headers={
                "Accept-Ranges": "bytes",
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Content-Length": str(chunk_size),
                "Cache-Control": "public, max-age=3600"
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid range values")
    except Exception as e:
        print(f"❌ Error handling range request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/list")
async def list_tutorial_videos(admin_data: dict = Depends(verify_admin_token)):
    """List available tutorial videos"""
    try:
        uploads_path = Path(UPLOADS_DIR)
        if not uploads_path.exists():
            return {"videos": []}
        
        video_files = []
        for file_path in uploads_path.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.mp4', '.webm', '.mov', '.avi']:
                video_files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "url": f"/api/video/tutorial/{file_path.name}"
                })
        
        return {"videos": video_files}
        
    except Exception as e:
        print(f"❌ Error listing videos: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")