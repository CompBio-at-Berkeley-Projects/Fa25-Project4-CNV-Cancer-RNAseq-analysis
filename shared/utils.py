"""
Shared Utility Functions

Common utilities used by both frontend and backend.
"""

import os
from pathlib import Path
from typing import Tuple, List, Optional
from datetime import datetime


def get_absolute_path(relative_path: str) -> str:
    """
    Convert relative path to absolute path from project root.
    
    Args:
        relative_path: Path relative to project root
    
    Returns:
        Absolute path
    """
    project_root = get_project_root()
    return str(Path(project_root) / relative_path)


def ensure_dir_exists(dir_path: str) -> None:
    """
    Create directory if it doesn't exist.
    
    Args:
        dir_path: Directory path to create
    """
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def get_project_root() -> str:
    """
    Get project root directory.
    
    Returns:
        Absolute path to project root
    """
    # Assume this file is in shared/ directory
    return str(Path(__file__).parent.parent)


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to file
    
    Returns:
        File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0


def is_compressed(file_path: str) -> bool:
    """
    Check if file is gzip compressed.
    
    Args:
        file_path: Path to file
    
    Returns:
        True if compressed, False otherwise
    """
    return file_path.endswith('.gz')


def list_result_directories(results_dir: str = "backend/results") -> List[str]:
    """
    List all analysis result directories.
    
    Args:
        results_dir: Base results directory
    
    Returns:
        List of result directory paths
    """
    results_path = Path(get_absolute_path(results_dir))
    
    if not results_path.exists():
        return []
    
    # Find directories (not files)
    dirs = [str(d) for d in results_path.iterdir() if d.is_dir()]
    
    # Sort by modification time (most recent first)
    dirs.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)
    
    return dirs


def validate_file_path(file_path: str) -> Tuple[bool, str]:
    """
    Validate file exists and is readable.
    
    Args:
        file_path: Path to file
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path:
        return False, "File path is empty"
    
    path = Path(file_path)
    
    if not path.exists():
        return False, f"File not found: {file_path}"
    
    if not path.is_file():
        return False, f"Path is not a file: {file_path}"
    
    if not os.access(file_path, os.R_OK):
        return False, f"File not readable: {file_path}"
    
    return True, ""


def validate_genome(genome: str) -> bool:
    """
    Validate genome parameter.
    
    Args:
        genome: Genome string ('hg20' or 'mm10')
    
    Returns:
        True if valid, False otherwise
    """
    return genome in ['hg20', 'mm10']


def validate_sample_name(name: str) -> Tuple[bool, str]:
    """
    Validate sample name format.
    
    Args:
        name: Sample name
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Sample name cannot be empty"
    
    if not name.replace('_', '').isalnum():
        return False, "Sample name must be alphanumeric (underscores allowed)"
    
    if len(name) > 50:
        return False, "Sample name too long (max 50 characters)"
    
    return True, ""


def timestamp_to_readable(timestamp: str) -> str:
    """
    Convert timestamp to human-readable format.
    
    Args:
        timestamp: ISO format timestamp string
    
    Returns:
        Readable timestamp string
    """
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except (ValueError, AttributeError):
        return timestamp


def bytes_to_human_readable(size_bytes: int) -> str:
    """
    Convert bytes to human-readable size.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def find_latest_result(sample_name: str, results_dir: str = "backend/results") -> Optional[str]:
    """
    Find the most recent result directory for a sample.
    
    Args:
        sample_name: Sample name to search for
        results_dir: Base results directory
    
    Returns:
        Path to most recent result directory or None
    """
    results_path = Path(get_absolute_path(results_dir))
    
    if not results_path.exists():
        return None
    
    # Find directories starting with sample name
    pattern = f"{sample_name}_*"
    matches = list(results_path.glob(pattern))
    
    if not matches:
        return None
    
    # Return most recent
    latest = max(matches, key=lambda p: p.stat().st_mtime)
    return str(latest)


def get_file_extension(file_path: str) -> str:
    """
    Get file extension (including compound extensions like .txt.gz).
    
    Args:
        file_path: Path to file
    
    Returns:
        File extension (e.g., ".txt.gz")
    """
    path = Path(file_path)
    
    # Handle compound extensions
    if path.suffix == '.gz' and len(path.suffixes) > 1:
        return ''.join(path.suffixes[-2:])
    
    return path.suffix


def cleanup_temp_files(temp_dir: str) -> int:
    """
    Remove temporary files from directory.
    
    Args:
        temp_dir: Temporary directory path
    
    Returns:
        Number of files removed
    """
    temp_path = Path(temp_dir)
    
    if not temp_path.exists():
        return 0
    
    count = 0
    for file in temp_path.glob("*"):
        if file.is_file():
            try:
                file.unlink()
                count += 1
            except OSError:
                pass
    
    return count

