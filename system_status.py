"""
System status checking module.
Verifies MongoDB and Gemini API connections.
"""

import os
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class SystemStatus:
    """System health check results."""
    
    def __init__(self):
        self.mongodb_connected = False
        self.mongodb_error = None
        self.gemini_connected = False
        self.gemini_error = None
        self.laws_count = 0


def check_system_status() -> SystemStatus:
    """
    Check if all required systems are connected and working.
    
    Returns:
        SystemStatus with connection information
    """
    status = SystemStatus()
    
    # Check Gemini
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            status.gemini_error = "API key not configured"
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            # Quick test
            response = model.generate_content("Say OK", generation_config=genai.GenerationConfig(max_output_tokens=10))
            if response:
                status.gemini_connected = True
    except Exception as e:
        error_str = str(e).lower()
        if "429" in str(e) or "quota" in error_str or "rate" in error_str:
            status.gemini_error = "Temporarily rate limited"
        elif "401" in str(e) or "authentication" in error_str or "api key" in error_str:
            status.gemini_error = "API key issue"
        else:
            status.gemini_error = "Connection error"
    
    # Check MongoDB
    try:
        from mongodb import get_database
        db = get_database()
        # Try to count laws
        count = db.laws.estimated_document_count()
        status.mongodb_connected = True
        status.laws_count = count
    except Exception as e:
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
            status.mongodb_error = "Cannot connect to database"
        elif "authentication" in error_str:
            status.mongodb_error = "Authentication failed"
        else:
            status.mongodb_error = "Database error"
    
    return status


def get_status_display() -> str:
    """Get a formatted status display string."""
    status = check_system_status()
    
    lines = []
    
    if status.gemini_connected:
        lines.append("✅ Gemini 2.5 Flash API Connected")
    else:
        lines.append(f"❌ Gemini API: {status.gemini_error or 'Not connected'}")
    
    if status.mongodb_connected:
        lines.append(f"✅ MongoDB Connected ({status.laws_count} laws in database)")
    else:
        lines.append(f"❌ MongoDB: {status.mongodb_error or 'Not connected'}")
    
    return "\n".join(lines)
