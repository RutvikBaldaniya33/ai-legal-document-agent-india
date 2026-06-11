"""
Tool 1 — Case Classifier
Input : raw dispute text (str)
Output: ClassifierResult { dispute_type, state }
"""

import os
import json
import time
from pathlib import Path
from typing import Literal

import google.generativeai as genai
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv
from typing import Optional

from gemini_errors import handle_gemini_error
# Load .env from current project folder
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")


# ─────────────────────────────────────────────────────────
# Pydantic model
# ─────────────────────────────────────────────────────────

class ClassifierResult(BaseModel):
    dispute_type: Literal["tenant", "consumer"]
    

    state: Optional[str] = None

    @field_validator("state")
    @classmethod
    def clean_state(cls, v):
        if v is None:
            return None
        return v.strip()


# ─────────────────────────────────────────────────────────
# Gemini setup
# ─────────────────────────────────────────────────────────

def _get_model():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            f"GEMINI_API_KEY not found. Check: {BASE_DIR / '.env'}"
        )

    genai.configure(api_key=api_key)

    return genai.GenerativeModel("gemini-2.5-flash")


# ─────────────────────────────────────────────────────────
# Prompt loader
# ─────────────────────────────────────────────────────────

def _load_prompt() -> str:
    prompt_path = BASE_DIR / "prompts" / "classifier.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_path}"
        )

    return prompt_path.read_text(encoding="utf-8")


# ─────────────────────────────────────────────────────────
# JSON extractor
# ─────────────────────────────────────────────────────────

def _extract_json(raw: str) -> dict:
    raw = raw.strip()

    # Remove markdown fences if Gemini adds them
    if raw.startswith("```"):
        raw = raw.replace("```json", "")
        raw = raw.replace("```", "")
        raw = raw.strip()

    return json.loads(raw)


# ─────────────────────────────────────────────────────────
# Main classifier
# ─────────────────────────────────────────────────────────

def classify_case(text: str) -> ClassifierResult:
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty.")

    model = _get_model()

    prompt = f"""
{_load_prompt()}

User Input:
{text.strip()}

Return ONLY valid JSON.

Example:

{{
  "dispute_type": "tenant",
  "state": "Gujarat"
}}
"""

    last_error = None
    last_retry_needed = False

    for attempt in range(3):

        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0,
                    max_output_tokens=256,
                ),
            )

            raw = response.text.strip()

            data = _extract_json(raw)

            return ClassifierResult(**data)

        except Exception as e:
            last_error = e
            should_retry, message = handle_gemini_error(e)
            last_retry_needed = should_retry
            
            if not should_retry:
                # Fatal error, raise immediately
                raise ValueError(f"Classification Error: {message}") from e
            
            # Retryable error - wait and try again
            if attempt < 2:  # Don't sleep after last attempt
                time.sleep(2)

    # All retries exhausted
    if last_retry_needed:
        raise ValueError(
            "⏱️ Gemini API rate limited. Please wait 30 seconds and retry."
        )
    else:
        raise ValueError(
            f"Failed to classify dispute after retries.\nError: {last_error}"
        )


# ─────────────────────────────────────────────────────────
# Test runner
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":

    test_cases = [
        "Landlord not returning ₹50,000 deposit after 3 months in Gujarat",
        "Amazon delivered a damaged laptop in Maharashtra",
        "Owner locked my room without notice",
        "Zomato charged me but order never arrived",
        "Mera makaan maalik deposit wapas nahi de raha, Surat Gujarat mein",
    ]

    print("Testing classifier...\n")

    for text in test_cases:

        result = classify_case(text)

        print(f"\nInput : {text}")
        print(
            f"Output: dispute_type='{result.dispute_type}', state='{result.state}'"
        )

    print("\nAll tests passed.")