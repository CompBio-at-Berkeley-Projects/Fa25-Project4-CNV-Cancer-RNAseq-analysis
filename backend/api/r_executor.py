"""
R Script Executor

Execute R scripts via subprocess and handle results.

This module provides the main interface for running CopyKAT analysis
from the Python frontend.

Author: Backend Team Integration
"""

import subprocess
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


def run_copykat_analysis(params: Dict) -> Dict:
    """
    Execute CopyKAT analysis by calling R script.
    
    This is the main function called by the frontend to run analysis.
    It constructs the R command, executes it, and returns structured results.
    
    Args:
        params: Dictionary with analysis parameters
            Required keys:
                - input_file: Path to expression matrix
                - sample_name: Sample identifier
                - output_dir: Output directory path
                - genome: 'hg20' or 'mm10'
            Optional keys:
                - ngene_chr: Min genes per chromosome (default: 5)
                - LOW_DR: Detection rate for smoothing (default: 0.05)
                - UP_DR: Detection rate for segmentation (default: 0.10)
                - win_size: Window size (default: 25)
                - KS_cut: Segmentation sensitivity (default: 0.1)
                - distance: Distance metric (default: 'euclidean')
                - n_cores: CPU cores (default: 4)
                - cell_line: 'yes' or 'no' (default: 'no')
                - plot_genes: Show gene names (default: True)
    
    Returns:
        Dictionary with results:
            - success: Boolean indicating if analysis succeeded
            - output_dir: Path to results directory
            - files: Dict of output file paths
            - summary: Dict of summary statistics
            - runtime_minutes: Analysis duration
            - error: Error message if failed (None otherwise)
    
    Example:
        >>> params = {
        ...     'input_file': 'backend/data/raw/sample.txt.gz',
        ...     'sample_name': 'sample_001',
        ...     'output_dir': 'backend/results',
        ...     'genome': 'hg20',
        ...     'n_cores': 4
        ... }
        >>> result = run_copykat_analysis(params)
        >>> if result['success']:
        ...     print(f"Results in: {result['output_dir']}")
    """
    # TODO: Implement actual R script execution
    # This is a skeleton showing the expected structure
    
    # Validate required parameters
    required_params = ['input_file', 'sample_name', 'output_dir', 'genome']
    for param in required_params:
        if param not in params:
            return {
                'success': False,
                'error': f"Missing required parameter: {param}",
                'output_dir': None,
                'files': {},
                'summary': {},
                'runtime_minutes': 0
            }
    
    # Build R command
    r_script_path = "backend/r_scripts/copykat_analysis.R"
    command = build_r_command(r_script_path, params)
    
    # Execute R script
    try:
        start_time = datetime.now()
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=get_project_root()
        )
        
        end_time = datetime.now()
        runtime = (end_time - start_time).total_seconds() / 60
        
        # Parse outputs
        output_dir = find_output_directory(params['output_dir'], params['sample_name'])
        
        if output_dir:
            files = locate_output_files(output_dir, params['sample_name'])
            summary = extract_summary_statistics(files)
            
            return {
                'success': True,
                'output_dir': output_dir,
                'files': files,
                'summary': summary,
                'runtime_minutes': runtime,
                'error': None,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'success': False,
                'error': "Output directory not found",
                'output_dir': None,
                'files': {},
                'summary': {},
                'runtime_minutes': runtime
            }
    
    except subprocess.CalledProcessError as e:
        return {
            'success': False,
            'error': f"R script failed: {e.stderr}",
            'output_dir': None,
            'files': {},
            'summary': {},
            'runtime_minutes': 0
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'output_dir': None,
            'files': {},
            'summary': {},
            'runtime_minutes': 0
        }


def build_r_command(script_path: str, params: Dict) -> List[str]:
    """
    Build command line arguments for R script.
    
    Args:
        script_path: Path to R script
        params: Analysis parameters
    
    Returns:
        List of command arguments
    """
    command = ["Rscript", script_path]
    
    # Add required arguments
    command.extend(["--input", params['input_file']])
    command.extend(["--output", params['output_dir']])
    command.extend(["--name", params['sample_name']])
    command.extend(["--genome", params['genome']])
    
    # Add optional arguments
    if 'ngene_chr' in params:
        command.extend(["--ngene_chr", str(params['ngene_chr'])])
    
    if 'win_size' in params:
        command.extend(["--win_size", str(params['win_size'])])
    
    if 'n_cores' in params:
        command.extend(["--cores", str(params['n_cores'])])
    
    if 'LOW_DR' in params:
        command.extend(["--low_dr", str(params['LOW_DR'])])
    
    if 'UP_DR' in params:
        command.extend(["--up_dr", str(params['UP_DR'])])
    
    if 'KS_cut' in params:
        command.extend(["--ks_cut", str(params['KS_cut'])])
    
    if 'distance' in params:
        command.extend(["--distance", params['distance']])
    
    if 'cell_line' in params:
        command.extend(["--cell_line", params['cell_line']])
    
    return command


def find_output_directory(base_dir: str, sample_name: str) -> Optional[str]:
    """
    Find the output directory created by R script.
    
    R script creates directory with timestamp, so we need to find it.
    
    Args:
        base_dir: Base output directory
        sample_name: Sample name
    
    Returns:
        Full path to output directory or None
    """
    # TODO: Implement directory search
    # Look for directories matching pattern: {sample_name}_*
    # Return the most recent one
    
    base_path = Path(base_dir)
    if not base_path.exists():
        return None
    
    # Find directories starting with sample name
    matching_dirs = list(base_path.glob(f"{sample_name}_*"))
    
    if matching_dirs:
        # Return most recent
        return str(max(matching_dirs, key=lambda p: p.stat().st_mtime))
    
    return None


def locate_output_files(output_dir: str, sample_name: str) -> Dict[str, str]:
    """
    Locate all output files generated by CopyKAT.
    
    Args:
        output_dir: Output directory path
        sample_name: Sample name
    
    Returns:
        Dictionary mapping file types to paths
    """
    output_path = Path(output_dir)
    
    files = {
        'predictions': str(output_path / f"{sample_name}_copykat_prediction.txt"),
        'cna_results': str(output_path / f"{sample_name}_copykat_CNA_results.txt"),
        'heatmap': str(output_path / f"{sample_name}_copykat_heatmap.jpeg"),
        'log': str(output_path / "logs" / "analysis.log"),
        'report': str(output_path / f"{sample_name}_report.html")
    }
    
    # Verify files exist
    existing_files = {k: v for k, v in files.items() if Path(v).exists()}
    
    return existing_files


def extract_summary_statistics(files: Dict[str, str]) -> Dict:
    """
    Extract summary statistics from output files.
    
    Args:
        files: Dictionary of file paths
    
    Returns:
        Dictionary of summary statistics
    """
    summary = {
        'n_cells': 0,
        'n_aneuploid': 0,
        'n_diploid': 0,
        'n_not_defined': 0,
        'aneuploid_fraction': 0.0
    }
    
    # TODO: Implement actual parsing
    # Read predictions file and count cell types
    predictions_file = files.get('predictions')
    
    if predictions_file and Path(predictions_file).exists():
        try:
            import pandas as pd
            df = pd.read_csv(predictions_file, sep='\t')
            
            summary['n_cells'] = len(df)
            
            if 'copykat.pred' in df.columns:
                counts = df['copykat.pred'].value_counts()
                summary['n_aneuploid'] = counts.get('aneuploid', 0)
                summary['n_diploid'] = counts.get('diploid', 0)
                summary['n_not_defined'] = counts.get('not.defined', 0)
                
                if summary['n_cells'] > 0:
                    summary['aneuploid_fraction'] = summary['n_aneuploid'] / summary['n_cells']
        
        except Exception:
            pass
    
    return summary


def get_project_root() -> str:
    """
    Get absolute path to project root.
    
    Returns:
        Project root directory path
    """
    # TODO: Make this more robust
    # For now, assume we're in backend/api/
    return str(Path(__file__).parent.parent.parent)

