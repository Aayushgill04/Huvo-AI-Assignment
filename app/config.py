import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings and configuration parameters."""
    
    def __init__(self):
        # LLM Settings
        self.LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock").lower()  # openai, groq, openrouter, mock
        self.OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
        self.OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.OPENAI_BASE_URL: Optional[str] = os.getenv("OPENAI_BASE_URL", None)
        
        # Server Settings
        self.HOST: str = os.getenv("HOST", "0.0.0.0")
        self.PORT: int = int(os.getenv("PORT", "8000"))
        self.DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
        
        # Real-Estate Project Details
        self.PROJECT_NAME: str = "Northstar One"
        self.DEVELOPER_NAME: str = "Northstar Homes"
        self.PROJECT_LOCATION: str = "Sector 79, Gurugram"
        self.STARTING_PRICE_2BHK: str = "₹1.35 Crore"
        self.STARTING_PRICE_3BHK: str = "₹1.75 Crore"
        
        # Simulation Defaults
        self.SIMULATE_BOOKING_FAILURE: bool = os.getenv("SIMULATE_BOOKING_FAILURE", "false").lower() in ("true", "1", "yes")

settings = Settings()
