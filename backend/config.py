import os
from dotenv import load_dotenv


backend_dir = os.path.dirname(os.path.abspath(__file__))
default_db_path = os.path.join(backend_dir, "app.db")
default_database_url = f"sqlite+aiosqlite:///{default_db_path.replace(os.sep, '/')}"


# Load environment variables from .env file
load_dotenv()

class Settings:
    API_TITLE = "Hungarian News Summary API"
    API_VERSION = "1.0.0"

    CORS_ORIGINS = ["http://localhost:5173"]  # Vite's default port

    DATABASE_URL: str = os.getenv("DATABASE_URL", default_database_url)

settings = Settings()