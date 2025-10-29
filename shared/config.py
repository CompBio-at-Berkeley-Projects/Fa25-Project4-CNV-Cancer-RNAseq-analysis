"""
Configuration Management

Centralized configuration loading and validation.

This module provides utilities for loading and managing configuration
from YAML files and command-line arguments.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Tuple, List


def load_config(config_file: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_file: Path to YAML configuration file
    
    Returns:
        Dictionary with configuration
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is malformed
    """
    config_path = Path(config_file)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration: {str(e)}")


def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate configuration structure and values.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    
    # Check required top-level keys
    required_keys = ['input', 'output', 'copykat']
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required section: {key}")
    
    # Validate input section
    if 'input' in config:
        if 'file' not in config['input']:
            errors.append("Missing required field: input.file")
    
    # Validate output section
    if 'output' in config:
        if 'directory' not in config['output']:
            errors.append("Missing required field: output.directory")
        if 'sample_name' not in config['output']:
            errors.append("Missing required field: output.sample_name")
    
    # Validate copykat section
    if 'copykat' in config:
        copykat = config['copykat']
        
        # Validate genome
        if 'genome' in copykat:
            if copykat['genome'] not in ['hg20', 'mm10']:
                errors.append(f"Invalid genome: {copykat['genome']}")
        
        # Validate numeric ranges
        if 'LOW_DR' in copykat:
            if not (0.0 < copykat['LOW_DR'] <= 0.5):
                errors.append("LOW_DR must be between 0.0 and 0.5")
        
        if 'UP_DR' in copykat:
            if not (0.0 < copykat['UP_DR'] <= 0.5):
                errors.append("UP_DR must be between 0.0 and 0.5")
        
        if 'LOW_DR' in copykat and 'UP_DR' in copykat:
            if copykat['UP_DR'] < copykat['LOW_DR']:
                errors.append("UP_DR must be >= LOW_DR")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def merge_configs(base_config: Dict, override_config: Dict) -> Dict:
    """
    Merge two configuration dictionaries.
    
    Override config takes precedence.
    
    Args:
        base_config: Base configuration
        override_config: Configuration to override with
    
    Returns:
        Merged configuration
    """
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            # Recursively merge nested dicts
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged


def save_config(config: Dict[str, Any], output_file: str) -> None:
    """
    Save configuration to YAML file.
    
    Args:
        config: Configuration dictionary
        output_file: Path to output YAML file
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration.
    
    Returns:
        Default configuration dictionary
    """
    return {
        'input': {
            'file': '',
            'separator': 'tab',
            'header': True,
            'row_names': True
        },
        'output': {
            'directory': 'backend/results',
            'sample_name': 'sample',
            'timestamp': True
        },
        'copykat': {
            'genome': 'hg20',
            'cell_line': 'no',
            'ngene_chr': 5,
            'LOW_DR': 0.05,
            'UP_DR': 0.10,
            'win_size': 25,
            'KS_cut': 0.1,
            'distance': 'euclidean',
            'n_cores': 4,
            'plot_genes': True
        },
        'quality_control': {
            'auto_filter': False,
            'min_genes_per_cell': 200,
            'min_umi_per_cell': 500,
            'max_mt_percent': 20,
            'min_cells_per_gene': 3
        },
        'preprocessing': {
            'detect_log_transform': True,
            'convert_to_counts': True,
            'log_base': 2
        }
    }

