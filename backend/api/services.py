"""
Backend Services Layer

Business logic connecting API routes to R executor and result parser.
This layer provides a clean interface between HTTP handlers and core functionality.
"""

from backend.api.r_executor import run_copykat_analysis
from backend.api.models import AnalysisRequest
from backend.api.result_parser import parse_copykat_results
from pathlib import Path
import shutil
import os
from typing import Dict

def execute_analysis(request: AnalysisRequest) -> Dict:
    """
    Execute CopyKAT analysis with validated parameters.
    
    Args:
        request: Validated analysis request model
        
    Returns:
        Dictionary with analysis results (success, output_dir, files, summary, etc.)
    """
    # Convert Pydantic model to dict for r_executor
    params = request.dict()
    return run_copykat_analysis(params)

def get_results(output_dir: str) -> Dict:
    """
    Parse and return analysis results from output directory.
    
    Args:
        output_dir: Path to results directory
        
    Returns:
        Dictionary with parsed results (predictions, CNA segments, summary, file paths)
    """
    return parse_copykat_results(output_dir)

def list_analyses(results_dir: str) -> list:
    """
    List all completed analyses in results directory.
    
    Args:
        results_dir: Base results directory path
        
    Returns:
        List of analysis directory names
    """
    path = Path(results_dir)
    if not path.exists():
        return []
    
    analyses = []
    for p in path.iterdir():
        if p.is_dir():
            # Check for any CopyKAT output files as indicator of completed analysis
            if any(p.glob("*_copykat_*.txt")) or any(p.glob("*_copykat_*.jpeg")):
                analyses.append(p.name)
    return analyses
