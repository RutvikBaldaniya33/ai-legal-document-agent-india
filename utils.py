"""
Utility functions for the AI Legal Document Agent.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional
import mimetypes


def validate_env_variables() -> dict:
    """
    Validate that all required environment variables are set.
    
    Returns:
        dict with keys: gemini_api_key, mongodb_uri, db_name
        
    Raises:
        ValueError: If any required variable is missing
    """
    from dotenv import load_dotenv
    
    load_dotenv()
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    mongodb_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DB_NAME", "legal_agent")
    
    errors = []
    
    if not gemini_api_key:
        errors.append("GEMINI_API_KEY not set in .env")
    if not mongodb_uri:
        errors.append("MONGODB_URI not set in .env")
    
    if errors:
        raise ValueError("Missing environment variables:\n" + "\n".join(errors))
    
    return {
        "gemini_api_key": gemini_api_key,
        "mongodb_uri": mongodb_uri,
        "db_name": db_name,
    }


def validate_file_for_upload(file_path: str, max_size_mb: int = 50) -> bool:
    """
    Validate if a file is suitable for upload.
    
    Args:
        file_path: Path to the file
        max_size_mb: Maximum file size in MB
        
    Returns:
        True if file is valid
        
    Raises:
        ValueError: If file is invalid
    """
    path = Path(file_path)
    
    if not path.exists():
        raise ValueError(f"File not found: {file_path}")
    
    # Check file size
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > max_size_mb:
        raise ValueError(
            f"File too large: {file_size_mb:.1f}MB (max {max_size_mb}MB)"
        )
    
    # Check file type
    mime_type, _ = mimetypes.guess_type(file_path)
    allowed_types = {
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/webp",
    }
    
    if mime_type not in allowed_types:
        raise ValueError(
            f"Unsupported file type: {mime_type}. "
            f"Allowed: PDF, PNG, JPEG, GIF, WebP"
        )
    
    return True


def format_score_display(score: int) -> str:
    """Format score for display with emoji and label."""
    if score >= 80:
        return f"🟢 {score}/100 - Very Strong"
    elif score >= 60:
        return f"🟢 {score}/100 - Strong"
    elif score >= 40:
        return f"🟡 {score}/100 - Moderate"
    elif score >= 20:
        return f"🟠 {score}/100 - Weak"
    else:
        return f"🔴 {score}/100 - Very Weak"


def format_indian_rupees(amount: str) -> str:
    """Format amount as Indian Rupees."""
    try:
        # Try to extract numeric value
        numeric = ''.join(c for c in amount if c.isdigit() or c == '.')
        if numeric:
            return f"₹{numeric}"
    except:
        pass
    return amount


def clean_text(text: str, max_length: Optional[int] = None) -> str:
    """Clean and normalize text."""
    text = text.strip()
    if max_length and len(text) > max_length:
        text = text[:max_length] + "..."
    return text


def format_list_for_display(items: list, max_items: int = 10) -> str:
    """Format a list for nice display."""
    if not items:
        return "None"
    
    displayed = items[:max_items]
    result = "\n".join(f"• {item}" for item in displayed)
    
    if len(items) > max_items:
        result += f"\n... and {len(items) - max_items} more"
    
    return result


def get_file_extension_from_mime(mime_type: str) -> str:
    """Get file extension from MIME type."""
    mime_to_ext = {
        "application/pdf": ".pdf",
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/gif": ".gif",
        "image/webp": ".webp",
    }
    return mime_to_ext.get(mime_type, ".bin")


def get_state_abbreviation(state_name: str) -> str:
    """Get abbreviation for Indian state."""
    state_abbr = {
        "Gujarat": "GJ",
        "Maharashtra": "MH",
        "Karnataka": "KA",
        "Tamil Nadu": "TN",
        "Delhi": "DL",
        "Uttar Pradesh": "UP",
        "West Bengal": "WB",
        "Rajasthan": "RJ",
        "Punjab": "PB",
        "Haryana": "HR",
        "Madhya Pradesh": "MP",
        "Telangana": "TG",
        "Andhra Pradesh": "AP",
        "Kerala": "KL",
        "Goa": "GA",
    }
    return state_abbr.get(state_name, state_name[:2].upper())


# ─────────────────────────────────────────────────────────
# Test runner
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Utility module ready.")
    print(f"Score display test: {format_score_display(75)}")
    print(f"Rupees format test: {format_indian_rupees('50000')}")
