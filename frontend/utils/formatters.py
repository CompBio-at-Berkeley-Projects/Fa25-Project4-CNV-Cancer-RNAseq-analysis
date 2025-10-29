"""
Data Formatting Functions

Format data for display in UI.

Author: Baovi Nguyen
"""

from datetime import datetime
from typing import Union


def format_file_size(size_bytes: int) -> str:
    """
    Convert bytes to human-readable size.
    
    Args:
        size_bytes: File size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_timestamp(timestamp: Union[str, datetime]) -> str:
    """
    Format timestamp to readable string.
    
    Args:
        timestamp: Timestamp string or datetime object
    
    Returns:
        Formatted string (e.g., "Oct 29, 2024 12:00 PM")
    """
    if isinstance(timestamp, str):
        try:
            dt = datetime.fromisoformat(timestamp)
        except ValueError:
            return timestamp
    else:
        dt = timestamp
    
    return dt.strftime("%b %d, %Y %I:%M %p")


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format float as percentage.
    
    Args:
        value: Float value (0-1)
        decimals: Number of decimal places
    
    Returns:
        Formatted string (e.g., "75.5%")
    """
    return f"{value * 100:.{decimals}f}%"


def format_number(value: Union[int, float], decimals: int = 0) -> str:
    """
    Format number with thousands separator.
    
    Args:
        value: Numeric value
        decimals: Number of decimal places
    
    Returns:
        Formatted string (e.g., "1,234" or "1,234.56")
    """
    if decimals == 0:
        return f"{int(value):,}"
    return f"{value:,.{decimals}f}"


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate long text with ellipsis.
    
    Args:
        text: Input text
        max_length: Maximum length
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

