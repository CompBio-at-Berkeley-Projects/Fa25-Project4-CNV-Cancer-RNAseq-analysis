"""
Status Monitor

Monitor R process execution and provide progress updates.

Author: Backend Team Integration
"""

import time
import subprocess
from pathlib import Path
from typing import Dict, Generator, Optional
from datetime import datetime


def monitor_analysis_progress(
    process: subprocess.Popen,
    log_file: Optional[str] = None
) -> Generator[Dict, None, None]:
    """
    Monitor R process and yield progress updates.
    
    This generator yields status dictionaries that can be used to update
    progress bars and status messages in the frontend.
    
    Args:
        process: Running subprocess.Popen object
        log_file: Optional path to log file to parse for progress
    
    Yields:
        Dictionary with:
            - progress: Float 0-1 indicating completion
            - message: Status message string
            - stage: Current stage name
            - complete: Boolean if process finished
    
    Example:
        >>> process = subprocess.Popen(command)
        >>> for status in monitor_analysis_progress(process):
        ...     progress_bar.progress(status['progress'])
        ...     status_text.text(status['message'])
        ...     if status['complete']:
        ...         break
    """
    stages = [
        (0.1, "Loading and validating data..."),
        (0.2, "Quality control assessment..."),
        (0.3, "Preprocessing data..."),
        (0.4, "Running CopyKAT analysis..."),
        (0.9, "Processing results..."),
        (1.0, "Complete!")
    ]
    
    current_stage = 0
    
    while process.poll() is None:
        # Process still running
        if current_stage < len(stages):
            progress, message = stages[current_stage]
            
            # Check log file for more detailed progress
            if log_file and Path(log_file).exists():
                detailed_message = parse_log_for_progress(log_file)
                if detailed_message:
                    message = detailed_message
            
            yield {
                'progress': progress,
                'message': message,
                'stage': f"Stage {current_stage + 1}/{len(stages)}",
                'complete': False,
                'timestamp': datetime.now().isoformat()
            }
            
            current_stage += 1
        
        time.sleep(2)  # Check every 2 seconds
    
    # Process finished
    return_code = process.returncode
    
    if return_code == 0:
        yield {
            'progress': 1.0,
            'message': "Analysis completed successfully!",
            'stage': "Complete",
            'complete': True,
            'success': True,
            'timestamp': datetime.now().isoformat()
        }
    else:
        yield {
            'progress': 0.0,
            'message': f"Analysis failed with code {return_code}",
            'stage': "Error",
            'complete': True,
            'success': False,
            'error_code': return_code,
            'timestamp': datetime.now().isoformat()
        }


def parse_log_for_progress(log_file: str) -> Optional[str]:
    """
    Parse log file to extract current progress message.
    
    Args:
        log_file: Path to log file
    
    Returns:
        Latest progress message or None
    """
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Look for lines with "STEP" or "INFO"
        for line in reversed(lines[-10:]):  # Check last 10 lines
            if "STEP" in line or "INFO" in line:
                # Extract message
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    return parts[2].strip()
        
        return None
    
    except Exception:
        return None


def estimate_runtime(n_cells: int, n_cores: int = 4) -> float:
    """
    Estimate analysis runtime based on cell count and cores.
    
    This is a rough estimate based on empirical observations.
    
    Args:
        n_cells: Number of cells in dataset
        n_cores: Number of CPU cores to use
    
    Returns:
        Estimated runtime in minutes
    """
    # Rough formula: base time + time per cell / cores
    base_time = 2.0  # minutes
    time_per_cell = 0.015  # minutes per cell
    
    estimated = base_time + (n_cells * time_per_cell) / n_cores
    
    return round(estimated, 1)


def check_resource_usage() -> Dict:
    """
    Check system resource usage (CPU, memory).
    
    Returns:
        Dictionary with resource metrics
    """
    try:
        import psutil
        
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'available_memory_gb': psutil.virtual_memory().available / (1024**3)
        }
    except ImportError:
        return {
            'cpu_percent': None,
            'memory_percent': None,
            'available_memory_gb': None
        }


def is_process_running(process: subprocess.Popen) -> bool:
    """
    Check if subprocess is still running.
    
    Args:
        process: Subprocess object
    
    Returns:
        True if running, False otherwise
    """
    return process.poll() is None

