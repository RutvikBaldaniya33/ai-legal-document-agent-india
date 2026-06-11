"""
Tool 3 — Evidence Extractor
Input: Uploaded documents (PDF, Images, Screenshots)
Output: ExtractedFacts { names, dates, amounts, addresses, facts }

Uses Gemini Vision to extract structured information from documents.
"""

import os
import json
import base64
import mimetypes
from pathlib import Path
from typing import Optional

import google.generativeai as genai
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")


# ─────────────────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────────────────

class ExtractedFacts(BaseModel):
    """Structured facts extracted from documents."""
    names: list[str] = []
    dates: list[str] = []
    amounts: list[str] = []
    addresses: list[str] = []
    important_facts: list[str] = []
    raw_text: str = ""


# ─────────────────────────────────────────────────────────
# Gemini setup
# ─────────────────────────────────────────────────────────

def _get_vision_model():
    """Get Gemini Vision model for image/PDF analysis."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


# ─────────────────────────────────────────────────────────
# Document processing
# ─────────────────────────────────────────────────────────

def _load_prompt() -> str:
    """Load the evidence extraction prompt."""
    prompt_path = BASE_DIR / "prompts" / "evidence_extractor.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def _encode_file_to_base64(file_path: str) -> tuple[str, str]:
    """Read file and encode to base64. Returns (base64_data, mime_type)."""
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        # Default to octet-stream if mime type can't be determined
        mime_type = "application/octet-stream"
    
    base64_data = base64.b64encode(file_data).decode("utf-8")
    return base64_data, mime_type


def _extract_json(raw: str) -> dict:
    """Extract JSON from response, handling markdown fences."""
    raw = raw.strip()
    
    if raw.startswith("```"):
        raw = raw.replace("```json", "")
        raw = raw.replace("```", "")
        raw = raw.strip()
    
    return json.loads(raw)


def extract_evidence_from_document(file_path: str) -> ExtractedFacts:
    """
    Extract structured facts from a document (PDF, Image, or Screenshot).
    
    Supported formats:
    - PDF files
    - Images (PNG, JPEG, GIF, WebP)
    - Screenshots (any image format)
    
    Args:
        file_path: Absolute path to the document
        
    Returns:
        ExtractedFacts with names, dates, amounts, addresses, and facts
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format not supported or Gemini extraction fails
    """
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Get file extension
    file_ext = file_path_obj.suffix.lower()
    
    # Supported formats
    supported_formats = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp"}
    if file_ext not in supported_formats:
        raise ValueError(
            f"Unsupported file format: {file_ext}. "
            f"Supported: {', '.join(supported_formats)}"
        )
    
    model = _get_vision_model()
    prompt = _load_prompt()
    
    # Encode file
    try:
        base64_data, mime_type = _encode_file_to_base64(file_path)
    except Exception as e:
        raise ValueError(f"Failed to read file: {e}")
    
    # Prepare content for Gemini
    content_parts = [
        {
            "type": "image",
            "data": base64_data,
        },
        {
            "type": "text",
            "text": prompt,
        }
    ]
    
    # Call Gemini Vision
    try:
        response = model.generate_content(
            content_parts,
            generation_config=genai.GenerationConfig(
                temperature=0,
                max_output_tokens=2000,
            ),
        )
        
        raw_response = response.text.strip()
        print("\n[DEBUG] Evidence Extraction Raw Response:")
        print(repr(raw_response[:500]))
        
        # Extract JSON
        data = _extract_json(raw_response)
        
        return ExtractedFacts(**data)
        
    except Exception as e:
        raise ValueError(f"Failed to extract evidence: {e}")


def extract_evidence_from_base64(
    base64_data: str,
    mime_type: str = "image/png",
) -> ExtractedFacts:
    """
    Extract facts from a base64-encoded image.
    
    Args:
        base64_data: Base64-encoded image data
        mime_type: MIME type (e.g., "image/png", "image/jpeg")
        
    Returns:
        ExtractedFacts with extracted information
    """
    model = _get_vision_model()
    prompt = _load_prompt()
    
    content_parts = [
        {
            "type": "image",
            "data": base64_data,
        },
        {
            "type": "text",
            "text": prompt,
        }
    ]
    
    try:
        response = model.generate_content(
            content_parts,
            generation_config=genai.GenerationConfig(
                temperature=0,
                max_output_tokens=2000,
            ),
        )
        
        raw_response = response.text.strip()
        data = _extract_json(raw_response)
        return ExtractedFacts(**data)
        
    except Exception as e:
        raise ValueError(f"Failed to extract evidence from base64: {e}")


# ─────────────────────────────────────────────────────────
# Test runner
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Evidence Extractor module ready for testing.")
    print("Usage: extract_evidence_from_document('/path/to/file.pdf')")
