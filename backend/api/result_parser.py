"""
Result Parser

Parse CopyKAT output files and extract data for frontend.

Author: Backend Team Integration
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional, List


def parse_copykat_results(output_dir: str) -> Dict:
    """
    Parse all CopyKAT output files from a results directory.
    
    Args:
        output_dir: Path to results directory
    
    Returns:
        Dictionary with parsed results:
            - predictions: DataFrame of cell classifications
            - cna_segments: DataFrame of CNV segments
            - summary: Dict of summary statistics
            - file_paths: Dict of file locations
    """
    output_path = Path(output_dir)
    
    if not output_path.exists():
        raise ValueError(f"Output directory not found: {output_dir}")
    
    # Initialize result structure
    results = {
        'predictions': None,
        'cna_segments': None,
        'summary': {},
        'file_paths': {}
    }
    
    # Parse predictions
    predictions_file = find_file(output_path, "*_copykat_prediction.txt")
    if predictions_file:
        results['predictions'] = parse_predictions(predictions_file)
        results['file_paths']['predictions'] = str(predictions_file)
    
    # Parse CNV segments
    cna_file = find_file(output_path, "*_copykat_CNA_results.txt")
    if cna_file:
        results['cna_segments'] = parse_cna_segments(cna_file)
        results['file_paths']['cna_results'] = str(cna_file)
    
    # Find other files
    heatmap_file = find_file(output_path, "*_copykat_heatmap.jpeg")
    if heatmap_file:
        results['file_paths']['heatmap'] = str(heatmap_file)
    
    report_file = find_file(output_path, "*_report.html")
    if report_file:
        results['file_paths']['report'] = str(report_file)
    
    log_file = output_path / "logs" / "analysis.log"
    if log_file.exists():
        results['file_paths']['log'] = str(log_file)
    
    # Generate summary
    if results['predictions'] is not None:
        results['summary'] = generate_summary(results['predictions'])
    
    return results


def parse_predictions(file_path: Path) -> pd.DataFrame:
    """
    Parse CopyKAT predictions file.
    
    Args:
        file_path: Path to predictions file
    
    Returns:
        DataFrame with cell classifications
    """
    try:
        df = pd.read_csv(file_path, sep='\t')
        return df
    except Exception as e:
        raise ValueError(f"Error parsing predictions file: {str(e)}")


def parse_cna_segments(file_path: Path) -> pd.DataFrame:
    """
    Parse CopyKAT CNV segments file.
    
    Args:
        file_path: Path to CNA results file
    
    Returns:
        DataFrame with CNV segments
    """
    try:
        df = pd.read_csv(file_path, sep='\t')
        return df
    except Exception as e:
        raise ValueError(f"Error parsing CNA segments file: {str(e)}")


def generate_summary(predictions: pd.DataFrame) -> Dict:
    """
    Generate summary statistics from predictions.
    
    Args:
        predictions: Predictions DataFrame
    
    Returns:
        Dictionary of summary statistics
    """
    summary = {
        'n_cells': len(predictions),
        'n_aneuploid': 0,
        'n_diploid': 0,
        'n_not_defined': 0,
        'aneuploid_fraction': 0.0,
        'mean_confidence': 0.0
    }
    
    if 'copykat.pred' in predictions.columns:
        counts = predictions['copykat.pred'].value_counts()
        summary['n_aneuploid'] = int(counts.get('aneuploid', 0))
        summary['n_diploid'] = int(counts.get('diploid', 0))
        summary['n_not_defined'] = int(counts.get('not.defined', 0))
        
        if summary['n_cells'] > 0:
            summary['aneuploid_fraction'] = summary['n_aneuploid'] / summary['n_cells']
    
    if 'copykat.confidence' in predictions.columns:
        summary['mean_confidence'] = float(predictions['copykat.confidence'].mean())
    
    return summary


def find_file(directory: Path, pattern: str) -> Optional[Path]:
    """
    Find file matching pattern in directory.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern
    
    Returns:
        Path to file or None
    """
    matches = list(directory.glob(pattern))
    if matches:
        return matches[0]
    return None


def extract_chromosome_summary(cna_segments: pd.DataFrame) -> Dict:
    """
    Extract chromosome-level CNV summary.
    
    Args:
        cna_segments: CNV segments DataFrame
    
    Returns:
        Dictionary with chromosome summaries
    """
    summary = {}
    
    if 'chrom' not in cna_segments.columns:
        return summary
    
    # Group by chromosome
    for chrom in cna_segments['chrom'].unique():
        chrom_data = cna_segments[cna_segments['chrom'] == chrom]
        
        # Calculate mean copy number
        if 'copyNumber' in chrom_data.columns:
            mean_cn = chrom_data['copyNumber'].mean()
            
            # Classify chromosome
            if mean_cn > 2.3:
                status = "Amplified"
            elif mean_cn < 1.7:
                status = "Deleted"
            else:
                status = "Normal"
            
            summary[chrom] = {
                'mean_copy_number': mean_cn,
                'status': status,
                'n_segments': len(chrom_data)
            }
    
    return summary


def read_log_file(log_path: Path) -> List[str]:
    """
    Read analysis log file.
    
    Args:
        log_path: Path to log file
    
    Returns:
        List of log lines
    """
    try:
        with open(log_path, 'r') as f:
            return f.readlines()
    except Exception:
        return []

