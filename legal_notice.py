"""
Tool 5 — Legal Notice Generator
Input: Case details + Facts + Laws
Output: LegalNoticeOutput { notice, complaint, summary }

Generates professional legal documents.
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

import google.generativeai as genai
from pydantic import BaseModel
from dotenv import load_dotenv

from gemini_errors import handle_gemini_error

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")


# ─────────────────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────────────────

class LegalNoticeOutput(BaseModel):
    """Generated legal documents."""
    legal_notice: str
    consumer_complaint: Optional[str] = None
    summary: str
    date_generated: str


# ─────────────────────────────────────────────────────────
# Gemini setup
# ─────────────────────────────────────────────────────────

def _get_model():
    """Get Gemini model for content generation."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


# ─────────────────────────────────────────────────────────
# Prompt loading
# ─────────────────────────────────────────────────────────

def _load_prompt() -> str:
    """Load the legal notice prompt."""
    prompt_path = BASE_DIR / "prompts" / "legal_notice.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


# ─────────────────────────────────────────────────────────
# Legal notice generation
# ─────────────────────────────────────────────────────────

def generate_legal_notice(
    dispute_description: str,
    dispute_type: str,
    claimant_name: str,
    respondent_name: str,
    state: str,
    extracted_facts: dict,
    case_strength: dict,
    relevant_laws: list[dict],
) -> LegalNoticeOutput:
    """
    Generate professional legal notice and related documents.
    
    Args:
        dispute_description: Description of the dispute
        dispute_type: Type (tenant, consumer)
        claimant_name: Name of the party filing notice
        respondent_name: Name of the party being noticed
        state: Indian state
        extracted_facts: Extracted facts from documents
        case_strength: Case strength analysis
        relevant_laws: List of relevant laws
        
    Returns:
        LegalNoticeOutput with notice, complaint, and summary
        
    Raises:
        ValueError: If generation fails
    """
    model = _get_model()
    prompt = _load_prompt()
    
    # Format context
    facts_text = json.dumps(extracted_facts, indent=2, ensure_ascii=False)
    laws_text = "\n".join([
        f"- {law.get('title', 'Unknown')} ({law.get('state', 'National')})"
        for law in relevant_laws[:3]
    ])
    
    # Modify prompt based on dispute type
    type_guidance = ""
    if dispute_type == "tenant":
        type_guidance = "\nGenerate a Rent Determination Notice/Eviction Notice as applicable."
    elif dispute_type == "consumer":
        type_guidance = "\nGenerate a Consumer Complaint Notice under Consumer Protection Act, 2019."
    
    full_prompt = f"""
{prompt}

{type_guidance}

CASE DETAILS:
Claimant: {claimant_name}
Respondent: {respondent_name}
Dispute Type: {dispute_type}
State: {state}
Description: {dispute_description}

FACTS:
{facts_text}

APPLICABLE LAWS:
{laws_text}

CASE STRENGTH: {case_strength.get('score', 0)}/100

Generate THREE professional documents:
1. Formal Legal Notice
2. Consumer Complaint (if applicable, otherwise alternative formal document)
3. Executive Summary (2-3 paragraphs)

Return ONLY valid JSON with NO markdown formatting in the text content:
{{
  "legal_notice": "Full formal legal notice text here...",
  "consumer_complaint": "Consumer complaint or alternative notice here...",
  "summary": "Executive summary here...",
  "date_generated": "YYYY-MM-DD"
}}
"""
    
    last_error = None
    last_retry_needed = False
    
    for attempt in range(2):
        try:
            response = model.generate_content(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=5000,
                ),
            )
            
            raw_response = response.text.strip()
            
            # Handle markdown code blocks
            if raw_response.startswith("```"):
                raw_response = raw_response.replace("```json", "")
                raw_response = raw_response.replace("```", "")
                raw_response = raw_response.strip()
            
            data = json.loads(raw_response)
            
            # Ensure date is set
            if not data.get("date_generated"):
                data["date_generated"] = datetime.now().strftime("%Y-%m-%d")
            
            return LegalNoticeOutput(**data)
            
        except Exception as e:
            last_error = e
            should_retry, message = handle_gemini_error(e)
            last_retry_needed = should_retry
            
            if not should_retry:
                raise ValueError(f"Legal Notice Error: {message}") from e
            
            if attempt < 1:
                time.sleep(2)
    
    # Fallback: return a template notice
    if last_retry_needed:
        raise ValueError("⏱️ Gemini rate limited. Unable to generate legal notice now.")
    
    return LegalNoticeOutput(
        legal_notice=f"[Legal Notice for {claimant_name} vs {respondent_name}]\n\nTo whom it may concern:\n\nThis is a formal notice regarding the dispute described above. Please provide your response within 30 days.\n\n{dispute_description}",
        consumer_complaint="Please retry generation when API is available.",
        summary="Notice generation temporarily unavailable. Please retry in a few moments.",
        date_generated=datetime.now().strftime("%Y-%m-%d"),
    )


def format_legal_notice_for_display(notice_output: LegalNoticeOutput) -> str:
    """Format notice output for clean display."""
    text = f"""
{'='*80}
GENERATED LEGAL NOTICE
{'='*80}

DATE: {notice_output.date_generated}

{notice_output.legal_notice}

{'='*80}
"""
    if notice_output.consumer_complaint:
        text += f"""
CONSUMER COMPLAINT / FORMAL DOCUMENT:
{notice_output.consumer_complaint}

{'='*80}
"""
    
    text += f"""
SUMMARY:
{notice_output.summary}

{'='*80}
"""
    return text


# ─────────────────────────────────────────────────────────
# Test runner
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Legal Notice Generator module ready.")
    print("Usage: generate_legal_notice(...)")
