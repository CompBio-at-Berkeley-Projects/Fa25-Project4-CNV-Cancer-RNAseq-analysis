"""
Backend Services Layer with Live Logging Support
"""

from backend.api.r_executor import run_copykat_analysis, build_r_command, get_project_root, find_output_directory, locate_output_files, extract_summary_statistics
from backend.api.models import AnalysisRequest
from backend.api.result_parser import parse_copykat_results
from pathlib import Path
import threading
import uuid
import subprocess
from datetime import datetime
from typing import Dict, Optional

# In-memory store for active tasks (in production use Redis/DB)
_active_tasks = {}

def start_analysis_task(request: AnalysisRequest) -> str:
    """
    Start analysis in a background thread and capture output in real-time.
    """
    task_id = str(uuid.uuid4())
    params = request.dict()
    
    # Initialize task state
    _active_tasks[task_id] = {
        'status': 'running',
        'start_time': datetime.now().isoformat(),
        'logs': [],  # List of log strings
        'result': None,
        'params': params
    }
    
    def _run_task():
        try:
            # 1. Validation steps from run_copykat_analysis
            project_root = Path(get_project_root())
            r_script_path = project_root / "backend" / "r_scripts" / "copykat_simple.R"
            
            if not r_script_path.exists():
                raise Exception(f"R script not found: {r_script_path}")
                
            command = build_r_command(str(r_script_path), params)
            
            _active_tasks[task_id]['logs'].append(f"Starting analysis for {params['sample_name']}...")
            _active_tasks[task_id]['logs'].append(f"Executing command: {' '.join(command)}")
            
            # 2. Execute with live output capturing
            start_time = datetime.now()
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Merge stderr into stdout
                text=True,
                cwd=get_project_root(),
                bufsize=1 # Line buffered
            )
            
            # Stream logs
            for line in process.stdout:
                line = line.strip()
                if line:
                    _active_tasks[task_id]['logs'].append(line)
            
            process.wait()
            
            end_time = datetime.now()
            runtime = (end_time - start_time).total_seconds() / 60
            
            if process.returncode != 0:
                raise Exception(f"Analysis failed with exit code {process.returncode}")
            
            _active_tasks[task_id]['logs'].append("Analysis process finished. Parsing results...")
            
            # 3. Parse results
            output_dir = find_output_directory(params['output_dir'], params['sample_name'])
            
            if output_dir:
                files = locate_output_files(output_dir, params['sample_name'])
                summary = extract_summary_statistics(files)
                
                result = {
                    'success': True,
                    'output_dir': output_dir,
                    'files': files,
                    'summary': summary,
                    'runtime_minutes': runtime,
                    'error': None,
                    'timestamp': datetime.now().isoformat(),
                    'stdout': "\n".join(_active_tasks[task_id]['logs']),
                    'stderr': ""
                }
                _active_tasks[task_id]['status'] = 'completed'
                _active_tasks[task_id]['result'] = result
            else:
                raise Exception("Output directory not found")
                
        except Exception as e:
            _active_tasks[task_id]['status'] = 'failed'
            _active_tasks[task_id]['error'] = str(e)
            _active_tasks[task_id]['logs'].append(f"ERROR: {str(e)}")

    # Start thread
    thread = threading.Thread(target=_run_task)
    thread.daemon = True
    thread.start()
    
    return task_id

def get_task_status(task_id: str) -> Optional[Dict]:
    """
    Get current status of a task.
    """
    return _active_tasks.get(task_id)

def execute_analysis(request: AnalysisRequest) -> Dict:
    """Legacy synchronous execution"""
    params = request.dict()
    return run_copykat_analysis(params)

def get_results(output_dir: str) -> Dict:
    return parse_copykat_results(output_dir)

def list_analyses(results_dir: str) -> list:
    path = Path(results_dir)
    if not path.exists():
        return []
    analyses = []
    for p in path.iterdir():
        if p.is_dir():
            if any(p.glob("*_copykat_*.txt")) or any(p.glob("*_copykat_*.jpeg")):
                analyses.append(p.name)
    return analyses
