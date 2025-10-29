"""
Data Validation Functions

Validate user inputs and uploaded data.

Author: Baovi Nguyen
"""

import pandas as pd
from typing import Tuple, List, Dict


def validate_expression_matrix(df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
    """
    Validate expression matrix structure and content.
    
    Args:
        df: Expression matrix DataFrame (genes x cells)
    
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    errors = []
    warnings = []
    
    # Check dimensions
    n_genes, n_cells = df.shape
    
    if n_cells < 50:
        errors.append(f"Too few cells ({n_cells}). Minimum: 50 cells")
    elif n_cells < 100:
        warnings.append(f"Low cell count ({n_cells}). Recommended: 100+ cells")
    
    if n_genes < 1000:
        warnings.append(f"Low gene count ({n_genes}). Recommended: 5000+ genes")
    
    # Check for missing values
    if df.isnull().any().any():
        n_missing = df.isnull().sum().sum()
        warnings.append(f"Found {n_missing} missing values")
    
    # Check for negative values
    if (df < 0).any().any():
        errors.append("Found negative values. Expression data should be non-negative")
    
    # Check for infinite values
    if df.isin([float('inf'), float('-inf')]).any().any():
        errors.append("Found infinite values")
    
    # Check row/column names
    if df.index.empty:
        errors.append("Missing gene names (row names)")
    
    if df.columns.empty:
        errors.append("Missing cell names (column names)")
    
    # Check for duplicates
    if df.index.duplicated().any():
        n_dup = df.index.duplicated().sum()
        warnings.append(f"Found {n_dup} duplicate gene names")
    
    if df.columns.duplicated().any():
        n_dup = df.columns.duplicated().sum()
        errors.append(f"Found {n_dup} duplicate cell names")
    
    is_valid = len(errors) == 0
    
    return is_valid, errors, warnings


def validate_parameters(params: Dict) -> Tuple[bool, List[str]]:
    """
    Validate analysis parameters.
    
    Args:
        params: Dictionary of analysis parameters
    
    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    
    # Validate sample name
    sample_name = params.get('sample_name', '')
    if not sample_name:
        errors.append("Sample name is required")
    elif not sample_name.replace('_', '').isalnum():
        errors.append("Sample name must be alphanumeric (underscores allowed)")
    
    # Validate genome
    genome = params.get('genome', '')
    if genome not in ['hg20', 'mm10']:
        errors.append(f"Invalid genome: {genome}. Must be 'hg20' or 'mm10'")
    
    # Validate numeric parameters
    n_cores = params.get('n_cores', 0)
    if n_cores < 1 or n_cores > 64:
        errors.append("n_cores must be between 1 and 64")
    
    # Validate detection rates
    low_dr = params.get('low_dr', 0)
    up_dr = params.get('up_dr', 0)
    
    if low_dr < 0.01 or low_dr > 0.5:
        errors.append("LOW.DR must be between 0.01 and 0.5")
    
    if up_dr < 0.01 or up_dr > 0.5:
        errors.append("UP.DR must be between 0.01 and 0.5")
    
    if up_dr < low_dr:
        errors.append("UP.DR must be >= LOW.DR")
    
    # Validate window size
    win_size = params.get('win_size', 0)
    if win_size < 10 or win_size > 200:
        errors.append("Window size must be between 10 and 200")
    
    is_valid = len(errors) == 0
    
    return is_valid, errors


def validate_file_path(file_path: str) -> Tuple[bool, str]:
    """
    Validate file path exists and is readable.
    
    Args:
        file_path: Path to file
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    import os
    
    if not file_path:
        return False, "File path is empty"
    
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    if not os.access(file_path, os.R_OK):
        return False, f"File not readable: {file_path}"
    
    return True, ""

