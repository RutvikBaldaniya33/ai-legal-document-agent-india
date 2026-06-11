"""
System validation and startup test.
Verifies all dependencies and configurations before running the app.

Usage: python verify_setup.py
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check Python version."""
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.9+)")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    print("\n✓ Checking dependencies...")
    
    required = {
        "streamlit": "streamlit",
        "pydantic": "pydantic",
        "google.generativeai": "google-generativeai",
        "pymongo": "pymongo",
        "dotenv": "python-dotenv",
        "fitz": "PyMuPDF",
        "PIL": "Pillow",
    }
    
    missing = []
    
    for module, package in required.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (MISSING)")
            missing.append(package)
    
    return len(missing) == 0, missing


def check_environment():
    """Check environment variables."""
    print("\n✓ Checking environment variables...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("  ✗ .env file not found")
        print("  → Copy from env.example: cp env.example .env")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["GEMINI_API_KEY", "MONGODB_URI"]
    all_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = value[:20] + "..." if len(value) > 20 else value
            print(f"  ✓ {var} = {masked}")
        else:
            print(f"  ✗ {var} (MISSING)")
            all_present = False
    
    return all_present


def check_files():
    """Check if all necessary files exist."""
    print("\n✓ Checking project structure...")
    
    required_files = [
        "app.py",
        "classifier.py",
        "law_retriever.py",
        "mongodb.py",
        "evidence_extractor.py",
        "case_strength.py",
        "legal_notice.py",
        "utils.py",
        "requirements.txt",
        "prompts/classifier.txt",
        "prompts/evidence_extractor.txt",
        "prompts/case_strength.txt",
        "prompts/legal_notice.txt",
    ]
    
    missing = []
    
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (MISSING)")
            missing.append(file)
    
    return len(missing) == 0, missing


def test_gemini_connection():
    """Test Gemini API connection."""
    print("\n✓ Testing Gemini API connection...")
    
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            print("  ✗ GEMINI_API_KEY not set")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        response = model.generate_content("Respond with 'API OK' in one word.")
        if response.text:
            print(f"  ✓ Gemini API responding: {response.text.strip()}")
            return True
        else:
            print("  ✗ Gemini API not responding")
            return False
            
    except Exception as e:
        print(f"  ✗ Gemini API error: {str(e)}")
        return False


def test_mongodb_connection():
    """Test MongoDB connection."""
    print("\n✓ Testing MongoDB connection...")
    
    try:
        from mongodb import get_database
        
        db = get_database()
        # Try a ping
        db.client.admin.command("ping")
        print("  ✓ MongoDB connected")
        return True
        
    except Exception as e:
        print(f"  ✗ MongoDB connection error: {str(e)}")
        print("  → Check MONGODB_URI in .env")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("AI LEGAL DOCUMENT AGENT - SYSTEM VERIFICATION")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version()),
        ("Dependencies", check_dependencies()),
        ("Environment", check_environment()),
        ("Project Files", check_files()),
    ]
    
    all_passed = True
    
    for name, result in checks:
        if isinstance(result, tuple):
            passed = result[0]
        else:
            passed = result
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\n{status}: {name}")
        
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    # Optional: Test API connections
    if all_passed:
        print("\nOptional: Testing API connections...")
        
        gemini_ok = test_gemini_connection()
        mongo_ok = test_mongodb_connection()
        
        if gemini_ok and mongo_ok:
            print("\n" + "=" * 60)
            print("✓ ALL SYSTEMS READY FOR LAUNCH")
            print("=" * 60)
            print("\nStart the app with:")
            print("  streamlit run app.py")
            print("\nThe app will open at: http://localhost:8501")
            print("=" * 60)
            return 0
        else:
            print("\n⚠️  API connections have issues. Check configuration.")
            return 1
    else:
        print("\n✗ SETUP INCOMPLETE")
        print("\nFix the above issues and run again:")
        print("  python verify_setup.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
