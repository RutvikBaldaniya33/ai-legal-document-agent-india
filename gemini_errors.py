"""
Error handling and retry logic for Gemini API.
Gracefully handles rate limits, quota errors, and network issues.
"""

import time
from typing import Optional, Callable, Any, TypeVar
import google.generativeai as genai

T = TypeVar('T')

class GeminiRateLimitError(Exception):
    """Raised when Gemini API hits rate limit (429)."""
    pass

class GeminiError(Exception):
    """Base exception for Gemini API errors."""
    pass


def handle_gemini_error(error: Exception) -> tuple[bool, str]:
    """
    Analyze Gemini error and return (should_retry, user_message).
    
    Returns:
        (should_retry: bool, user_message: str)
    """
    error_str = str(error).lower()
    
    # Rate limit errors
    if "429" in str(error) or "rate" in error_str or "quota" in error_str:
        return (True, "🔄 Gemini API temporarily rate limited. Please wait 30 seconds and retry.")
    
    # Authentication errors
    if "401" in str(error) or "authentication" in error_str or "api key" in error_str.lower():
        return (False, "❌ API Key Issue: Please check your GEMINI_API_KEY in .env file.")
    
    # Resource exhausted
    if "resource" in error_str and "exhaust" in error_str:
        return (True, "🔄 API Resources temporarily exhausted. Please retry in 1 minute.")
    
    # Timeout/connection errors
    if "timeout" in error_str or "connection" in error_str or "network" in error_str:
        return (True, "🌐 Network issue. Please check your connection and retry.")
    
    # Generic fallback
    return (False, f"❌ Processing Error: {str(error)[:100]}")


def call_gemini_with_retry(
    func: Callable[..., T],
    *args,
    max_retries: int = 2,
    retry_delay: int = 5,
    **kwargs
) -> Optional[T]:
    """
    Call Gemini function with automatic retry logic for rate limits.
    
    Args:
        func: Function to call
        max_retries: Maximum retry attempts
        retry_delay: Delay between retries in seconds
        *args, **kwargs: Arguments to pass to func
        
    Returns:
        Result from func, or None if all retries exhausted
        
    Raises:
        GeminiError: If error is not retryable
    """
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
            
        except Exception as e:
            last_error = e
            should_retry, message = handle_gemini_error(e)
            
            if not should_retry:
                raise GeminiError(message) from e
            
            if attempt < max_retries:
                # Only sleep on actual retries, not on last failure
                time.sleep(retry_delay)
            else:
                # Last attempt failed
                raise GeminiError(
                    f"Failed after {max_retries + 1} attempts: {message}"
                ) from e
    
    return None


def get_safe_gemini_response(
    model,
    prompt: str,
    config: Optional[dict] = None,
) -> Optional[str]:
    """
    Call Gemini safely with error handling.
    
    Returns:
        Response text or None on fatal error
        
    Raises:
        GeminiError: On fatal errors
    """
    try:
        gen_config = {}
        if config:
            gen_config.update(config)
        else:
            gen_config = genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=2000,
            )
        
        response = model.generate_content(prompt, generation_config=gen_config)
        return response.text if response else None
        
    except Exception as e:
        should_retry, message = handle_gemini_error(e)
        if should_retry:
            raise GeminiError(f"{message}\n\nTechnical: {str(e)[:50]}") from e
        else:
            raise GeminiError(message) from e


def extract_json_safely(raw_text: str) -> dict:
    """
    Extract JSON from response, handling markdown code blocks.
    
    Returns:
        Parsed JSON dict or empty dict on failure
    """
    import json
    
    if not raw_text:
        return {}
    
    raw = raw_text.strip()
    
    # Remove markdown code blocks if present
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}
