"""
Quick Start Script for Code Review Assistant
Run this to verify everything is set up correctly
"""
import sys
import os

def check_environment():
    """Check if environment is configured"""
    print("=" * 60)
    print("Code Review Assistant - Environment Check")
    print("=" * 60)
    
    errors = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        errors.append("❌ Python 3.8+ required")
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check .env file
    if not os.path.exists('.env'):
        errors.append("❌ .env file not found. Copy .env.example to .env")
    else:
        print("✅ .env file exists")
    
    # Check dependencies
    try:
        import fastapi
        print(f"✅ FastAPI installed")
    except ImportError:
        errors.append("❌ FastAPI not installed. Run: pip install -r requirements.txt")
    
    try:
        import anthropic
        print(f"✅ Anthropic SDK installed")
    except ImportError:
        print("⚠️  Anthropic SDK not installed (optional)")
    
    try:
        import openai
        print(f"✅ OpenAI SDK installed")
    except ImportError:
        print("⚠️  OpenAI SDK not installed (optional)")
    
    try:
        from radon.complexity import cc_visit
        print(f"✅ Radon installed")
    except ImportError:
        errors.append("❌ Radon not installed. Run: pip install -r requirements.txt")
    
    # Check API key configuration
    from dotenv import load_dotenv
    load_dotenv()
    
    anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
    openai_key = os.getenv('OPENAI_API_KEY', '')
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    if not anthropic_key and not openai_key and not GEMINI_API_KEY:
        errors.append("❌ No AI API key configured in .env file")
    elif anthropic_key and anthropic_key != "your_anthropic_api_key_here":
        print("✅ Anthropic API key configured")
    elif openai_key and openai_key != "your_openai_api_key_here":
        print("✅ OpenAI API key configured")
    elif GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        print("✅ Gemini API key configured")
    else:
        errors.append("❌ API key placeholder not replaced in .env file")
    
    print("=" * 60)
    
    if errors:
        print("\n❌ ERRORS FOUND:\n")
        for error in errors:
            print(f"  {error}")
        print("\nPlease fix the above errors before running the application.\n")
        return False
    else:
        print("\n✅ All checks passed! Ready to start.\n")
        print("To start the application, run:")
        print("  python -m app.main")
        print("\nOr:")
        print("  uvicorn app.main:app --reload")
        print("\nThen open: http://localhost:8000\n")
        return True

if __name__ == "__main__":
    check_environment()
