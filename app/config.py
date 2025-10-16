"""
Configuration module for Code Review Assistant
Supports universal API key management for multiple AI providers
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Settings:
    """Application settings with universal AI provider support"""
    
    # Application
    APP_NAME: str = os.getenv("APP_NAME", "Code Review Assistant")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./reviews.db")
    
    # AI Provider Configuration
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "anthropic").lower()
    
    # API Keys (Universal placeholders)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    CUSTOM_API_KEY: str = os.getenv("CUSTOM_API_KEY", "")
    
    # Local LLM Settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Model Configuration
    AI_MODEL: str = os.getenv("AI_MODEL", "claude-sonnet-4-20250514")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "60"))
    
    # File Upload
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "5242880"))  # 5MB
    ALLOWED_EXTENSIONS: list = os.getenv(
        "ALLOWED_EXTENSIONS", 
        ".py,.js,.java,.ts,.jsx,.tsx,.go,.rb,.php,.cpp,.c,.cs,.swift"
    ).split(",")
    
    # Upload Directory
    UPLOAD_DIR: Path = Path("./uploads")
    
    @classmethod
    def get_api_key(cls) -> str:
        """Get the API key based on selected provider"""
        if cls.AI_PROVIDER == "anthropic":
            return cls.ANTHROPIC_API_KEY
        elif cls.AI_PROVIDER == "openai":
            return cls.OPENAI_API_KEY
        elif cls.AI_PROVIDER == "gemini":
            return cls.GEMINI_API_KEY or cls.CUSTOM_API_KEY
        elif cls.AI_PROVIDER == "ollama":
            return "local"  # No API key needed for local
        else:
            return cls.CUSTOM_API_KEY
    
    @classmethod
    def validate_api_key(cls) -> bool:
        """Validate that an API key is configured"""
        if cls.AI_PROVIDER == "ollama":
            return True  # Local LLM doesn't need API key
        
        api_key = cls.get_api_key()
        if not api_key or api_key == "your_anthropic_api_key_here" or api_key == "your_openai_api_key_here":
            return False
        return True
    
    @classmethod
    def initialize(cls):
        """Initialize application directories"""
        cls.UPLOAD_DIR.mkdir(exist_ok=True)

# Create settings instance
settings = Settings()
