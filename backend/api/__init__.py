"""
Backend API Layer

Python bridge between Streamlit frontend and R backend.

This module provides functions to:
- Execute R scripts via subprocess
- Parse R script outputs
- Monitor R process execution
- Handle errors and status updates
"""

# API imports
# from .r_executor import run_copykat_analysis
# from .result_parser import parse_copykat_results
# from .status_monitor import monitor_analysis_progress

__all__ = [
    'run_copykat_analysis',
    'parse_copykat_results',
    'monitor_analysis_progress'
]

