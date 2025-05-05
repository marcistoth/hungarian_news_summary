import os
from dotenv import load_dotenv

load_dotenv()

backend_dir = os.path.dirname(os.path.abspath(__file__))
default_db_path = os.path.join(backend_dir, "app.db")
database_url = os.getenv("DATABASE_URL")



# Check if using PostgreSQL and format correctly for async SQLAlchemy
if database_url and database_url.startswith("postgresql"):
    # For async operations, we need postgresql+asyncpg:// instead of postgresql://
    if not "postgresql+asyncpg" in database_url:
        database_url = database_url.replace("postgresql:", "postgresql+asyncpg:")

# Use the reformatted URL or the default SQLite URL
default_database_url = database_url or f"sqlite+aiosqlite:///{default_db_path.replace(os.sep, '/')}"

class Settings:
    API_TITLE = "Hungarian News Summary API"
    API_VERSION = "1.0.0"

    CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", 
    "https://marcistoth.github.io,"
    "http://localhost:5173"
).split(",")

    GEMINI_MODEL = "gemini-2.0-flash"
    GEMINI_TEMPERATURE = 1

    DATABASE_URL: str = os.getenv("DATABASE_URL", default_database_url)

settings = Settings()