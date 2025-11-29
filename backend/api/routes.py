from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from backend.api.models import AnalysisRequest
from backend.api.services import execute_analysis, start_analysis_task, get_task_status, list_analyses, get_results
import os
from pathlib import Path
from typing import List

router = APIRouter()

# Use absolute paths relative to this file
BACKEND_DIR = Path(__file__).parent.parent
DATA_DIR = BACKEND_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
RAW_DATA_DIR = DATA_DIR / "raw"
RESULTS_DIR = BACKEND_DIR / "results"

@router.post("/run")
async def run_analysis(request: AnalysisRequest):
    """
    Start analysis asynchronously. Returns a task_id.
    """
    try:
        task_id = start_analysis_task(request)
        return {"task_id": task_id, "status": "running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")

@router.get("/status/{task_id}")
async def check_status(task_id: str):
    """
    Check the status of a running analysis task.
    """
    status = get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status

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

@router.get("/analyses")
async def get_analyses_history():
    """
    List all completed analyses.
    """
    try:
        return list_analyses(str(RESULTS_DIR))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list analyses: {str(e)}")

@router.get("/results/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    """
    Get result details for a specific analysis ID (directory name).
    """
    analysis_dir = RESULTS_DIR / analysis_id
    if not analysis_dir.exists():
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        # Reconstruct the result object structure
        # We need to use locate_output_files logic but adapted for this context
        # Ideally, we should have stored the full result JSON, but we can reconstruct it
        # from the file system + summary stats
        
        # Extract sample name from directory (assuming {sample_name}_{timestamp})
        # This is a bit fragile if sample name has underscores, but let's try
        # Actually, locate_output_files needs sample_name.
        # Let's try to infer it from the filenames in the directory
        
        files = list(analysis_dir.glob("*_copykat_prediction.txt"))
        if not files:
             raise HTTPException(status_code=404, detail="Analysis result files not found")
        
        # sample_name is prefix of filename
        sample_name = files[0].name.replace("_copykat_prediction.txt", "")
        
        from backend.api.services import get_results
        result = get_results(str(analysis_dir))
        
        # Add success flag and other metadata needed by frontend
        # The parser returns {files: ..., summary: ...} but we need the full envelope
        
        full_result = {
            'success': True,
            'output_dir': str(analysis_dir),
            'files': result['files'],
            'summary': result['summary'],
            'runtime_minutes': 0, # Not preserved in fs, could read log if critical
            'error': None,
            'timestamp': analysis_id.split('_')[-1] if '_' in analysis_id else '' 
        }
        return full_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")
