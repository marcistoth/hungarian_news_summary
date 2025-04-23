import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    API_TITLE = "Hungarian News Summary API"
    API_VERSION = "1.0.0"

    CORS_ORIGINS = ["http://localhost:5173"]  # Vite's default port

    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

settings = Settings()