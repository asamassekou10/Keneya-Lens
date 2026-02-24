"""
Input validation and sanitization utilities
"""
import re
from typing import Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def sanitize_text(text: str, max_length: int = 5000) -> Tuple[str, Optional[str]]:
    """
    Sanitize user input text.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Tuple of (sanitized_text, error_message)
    """
    if not text or not isinstance(text, str):
        return "", "Input must be a non-empty string"
    
    # Check length
    if len(text) > max_length:
        return text[:max_length], f"Text truncated from {len(text)} to {max_length} characters"
    
    # Remove potentially dangerous characters (keep medical terminology safe)
    # Allow letters, numbers, spaces, and common medical punctuation
    sanitized = re.sub(r'[^\w\s\.,;:!?()\-/°]', '', text)
    
    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    if len(sanitized) < 10:
        return sanitized, "Input is too short (minimum 10 characters)"
    
    return sanitized, None


def validate_pdf_path(pdf_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate PDF file path.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        path = Path(pdf_path)
        
        # Check if file exists
        if not path.exists():
            return False, f"File not found: {pdf_path}"
        
        # Check if it's a file (not directory)
        if not path.is_file():
            return False, f"Path is not a file: {pdf_path}"
        
        # Check extension
        if path.suffix.lower() != '.pdf':
            return False, f"File must be a PDF (.pdf), got: {path.suffix}"
        
        # Check file size (max 50MB)
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 50:
            return False, f"PDF file too large ({size_mb:.2f}MB). Maximum: 50MB"
        
        return True, None
        
    except Exception as e:
        logger.error(f"PDF validation failed: {e}")
        return False, f"Invalid path: {str(e)}"


def validate_query_params(max_tokens: Optional[int] = None, 
                         temperature: Optional[float] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate query parameters.
    
    Args:
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if max_tokens is not None:
        if not isinstance(max_tokens, int):
            return False, "max_tokens must be an integer"
        if max_tokens < 1 or max_tokens > 2048:
            return False, "max_tokens must be between 1 and 2048"
    
    if temperature is not None:
        if not isinstance(temperature, (int, float)):
            return False, "temperature must be a number"
        if temperature < 0.0 or temperature > 2.0:
            return False, "temperature must be between 0.0 and 2.0"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = Path(filename).name
    
    # Remove dangerous characters
    filename = re.sub(r'[^\w\s\-_\.]', '', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename
