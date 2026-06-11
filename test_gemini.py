"""
Quick test: Gemini API connected and responding.
Run: python scripts/test_gemini.py
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in .env")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Basic response test
    response = model.generate_content("Say hello in one sentence.")
    print(f"Gemini response: {response.text.strip()}")

    # Embedding test (needed for Law Retriever)
    response = model.generate_content("Say hello in one sentence.")
    print(response.text)

if __name__ == "__main__":
    test_gemini()
