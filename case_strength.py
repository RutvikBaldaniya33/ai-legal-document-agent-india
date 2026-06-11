"""
Tool 4 — Case Strength Calculator
Input: Extracted facts + Laws + Dispute details
Output: CaseStrength { score, breakdown }

Calculates an explainable case strength score 0-100 based on evidence quality.
"""

import os
import json
import time
from pathlib import Path
from typing import Optional

import google.generativeai as genai
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv

from gemini_errors import handle_gemini_error

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")


# ─────────────────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────────────────

class CaseStrengthBreakdown(BaseModel):
    """Score breakdown by evidence type."""
    agreement_present: int = 0  # 0-25
    payment_proof: int = 0  # 0-20
    communication_evidence: int = 0  # 0-15
    law_match: int = 0  # 0-10
    timeline_consistency: int = 0  # 0-8
    witnesses: int = 0  # 0-7
    documentation_completeness: int = 0  # 0-15
    
    def total(self) -> int:
        """Calculate total score."""
        return (
            self.agreement_present +
            self.payment_proof +
            self.communication_evidence +
            self.law_match +
            self.timeline_consistency +
            self.witnesses +
            self.documentation_completeness
        )


class CaseStrength(BaseModel):
    """Case strength evaluation."""
    score: int  # 0-100
    breakdown: CaseStrengthBreakdown
    reasoning: str
    risk_factors: list[str] = []
    strengths: list[str] = []
    
    @field_validator("score")
    @classmethod
    def validate_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Score must be between 0 and 100")
        return v


# ─────────────────────────────────────────────────────────
# Gemini setup
# ─────────────────────────────────────────────────────────

def _get_model():
    """Get Gemini model for analysis."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


# ─────────────────────────────────────────────────────────
# Prompt loading
# ─────────────────────────────────────────────────────────

def _load_prompt() -> str:
    """Load the case strength prompt."""
    prompt_path = BASE_DIR / "prompts" / "case_strength.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


# ─────────────────────────────────────────────────────────
# JSON extraction
# ─────────────────────────────────────────────────────────

def _extract_json(raw: str) -> dict:
    """Extract JSON from response, handling markdown fences."""
    raw = raw.strip()
    
    if raw.startswith("```"):
        raw = raw.replace("```json", "")
        raw = raw.replace("```", "")
        raw = raw.strip()
    
    return json.loads(raw)


# ─────────────────────────────────────────────────────────
# Case strength calculation
# ─────────────────────────────────────────────────────────

def calculate_case_strength(
    dispute_description: str,
    dispute_type: str,
    extracted_facts: dict,
    relevant_laws: list[dict],
) -> CaseStrength:
    """
    Calculate case strength based on evidence and laws.
    
    Args:
        dispute_description: Description of the dispute
        dispute_type: Type of dispute (tenant, consumer)
        extracted_facts: Extracted facts from documents
        relevant_laws: List of relevant laws/acts
        
    Returns:
        CaseStrength with score, breakdown, and reasoning
        
    Raises:
        ValueError: If analysis fails
    """
    model = _get_model()
    prompt = _load_prompt()
    
    # Format context
    facts_text = json.dumps(extracted_facts, indent=2, ensure_ascii=False)
    laws_text = "\n".join([
        f"- {law.get('title', 'Unknown')} ({law.get('state', 'National')}): {law.get('content', '')[:200]}..."
        for law in relevant_laws[:5]
    ])
    
    full_prompt = f"""
{prompt}

CASE DETAILS:
Dispute Type: {dispute_type}
Description: {dispute_description}

EXTRACTED FACTS:
{facts_text}

RELEVANT LAWS:
{laws_text}

Return ONLY valid JSON.

Example:
{{
  "score": 75,
  "breakdown": {{
    "agreement_present": 20,
    "payment_proof": 15,
    "communication_evidence": 12,
    "law_match": 10,
    "timeline_consistency": 8,
    "witnesses": 5,
    "documentation_completeness": 5
  }},
  "reasoning": "Strong evidence with clear paper trail...",
  "risk_factors": ["Delayed response", "Missing witness statement"],
  "strengths": ["Clear communication trail", "Payment proof present", "Law matches well"]
}}
"""
    
    last_error = None
    last_retry_needed = False
    
    for attempt in range(2):
        try:
            response = model.generate_content(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2000,
                ),
            )
            
            raw_response = response.text.strip()
            
            # Extract JSON
            data = _extract_json(raw_response)
            return CaseStrength(**data)
            
        except Exception as e:
            last_error = e
            should_retry, message = handle_gemini_error(e)
            last_retry_needed = should_retry
            
            if not should_retry:
                raise ValueError(f"Case Strength Error: {message}") from e
            
            if attempt < 1:
                time.sleep(2)
    
    # Final fallback: return a moderate score instead of crashing
    if last_retry_needed:
        raise ValueError("⏱️ Gemini rate limited. Unable to calculate case strength now.")
    
    # Fallback default score
    return CaseStrength(
        score=50,
        breakdown=CaseStrengthBreakdown(
            agreement_present=10,
            payment_proof=10,
            communication_evidence=10,
            law_match=10,
            timeline_consistency=10,
        ),
        reasoning="Score calculation temporarily unavailable. Please retry.",
        risk_factors=["Analysis unavailable"],
        strengths=["Please retry for detailed analysis"],
    )


def get_strength_label(score: int) -> str:
    """Get human-readable label for strength score."""
    if score >= 80:
        return "Very Strong"
    elif score >= 60:
        return "Strong"
    elif score >= 40:
        return "Moderate"
    elif score >= 20:
        return "Weak"
    else:
        return "Very Weak"


# ─────────────────────────────────────────────────────────
# Test runner
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Case Strength Calculator module ready.")
    print("Usage: calculate_case_strength(description, type, facts, laws)")
