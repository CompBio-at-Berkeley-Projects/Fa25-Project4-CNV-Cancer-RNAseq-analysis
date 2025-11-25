from fastapi import APIRouter, HTTPException, UploadFile, File
from backend.api.models import AnalysisRequest
from backend.api.services import execute_analysis
import os
from pathlib import Path
from typing import List

router = APIRouter()

# Use absolute paths relative to this file
BACKEND_DIR = Path(__file__).parent.parent
DATA_DIR = BACKEND_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
RAW_DATA_DIR = DATA_DIR / "raw"

@router.post("/run")
async def run_analysis(request: AnalysisRequest):
    try:
        result = execute_analysis(request)
        if not result['success']:
            error_msg = result.get('error', 'Analysis failed')
            if 'R script not found' in error_msg:
                raise HTTPException(status_code=404, detail=f"Configuration error: {error_msg}")
            elif 'pandas' in error_msg.lower():
                raise HTTPException(status_code=500, detail=f"Missing dependency: {error_msg}")
            elif 'conda' in error_msg.lower():
                raise HTTPException(status_code=500, detail=f"Environment error: {error_msg}")
            else:
                raise HTTPException(status_code=500, detail=f"Analysis error: {error_msg}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        return {"filename": file.filename, "path": str(file_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.get("/files")
async def list_files():
    data_dir = RAW_DATA_DIR
    uploads_dir = UPLOAD_DIR
    
    files = []
    
    # List raw data
    if data_dir.exists():
        for f in data_dir.glob("**/*.gz"):
            files.append({"name": f.name, "path": str(f), "type": "raw"})
            
    # List uploads
    if uploads_dir.exists():
        for f in uploads_dir.glob("*"):
            files.append({"name": f.name, "path": str(f), "type": "uploaded"})
            
    return files
