import re
from typing import Union, Any, List, Dict

def validate_inputs(height: float, width: float, depth: float, letters: str) -> bool:
    """
    Validate input dimensions and letter text.
    
    Args:
        height: Letter height in inches
        width: Letter width in inches
        depth: Letter depth in inches
        letters: The letters/text for the quotation
        
    Returns:
        True if inputs are valid, False otherwise
    """
    # Check if dimensions are within acceptable ranges
    dimension_valid = all([
        height > 0,
        width > 0,
        depth > 0,
        height <= 120,  # Max 10 feet
        width <= 120,
        depth <= 24
    ])
    
    # Check if letters field is not empty
    letters_valid = letters.strip() != ""
    
    return dimension_valid and letters_valid

def sanitize_text_input(text: str) -> str:
    """
    Sanitize text inputs to prevent injection attacks.
    
    Args:
        text: Raw text input
        
    Returns:
        Sanitized text
    """
    # Remove any HTML/script tags
    sanitized = re.sub(r'<[^>]*>', '', text)
    
    # Limit to printable characters
    sanitized = re.sub(r'[^\w\s.,!?@#$%^&*()-]', '', sanitized)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    return sanitized

def validate_file_upload(file_content: bytes, file_type: str) -> bool:
    """
    Validate uploaded files for security.
    
    Args:
        file_content: Content of the uploaded file
        file_type: Expected file type (extension)
        
    Returns:
        True if file is valid, False otherwise
    """
    # Check file size (limit to 5MB)
    if len(file_content) > 5 * 1024 * 1024:
        return False
    
    # Additional validation based on file type
    if file_type.lower() == 'json':
        # Basic check for JSON structure
        try:
            import json
            json.loads(file_content)
            return True
        except:
            return False
    
    elif file_type.lower() in ['ttf', 'otf']:
        # Basic check for font files (check magic numbers)
        if file_content.startswith(b'\x00\x01\x00\x00') or file_content.startswith(b'OTTO'):
            return True
        return False
    
    # Default to true for other file types
    return True