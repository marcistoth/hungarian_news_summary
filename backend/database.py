import os
import asyncpg
import logging
from contextlib import asynccontextmanager
from backend.config import settings

logger = logging.getLogger(__name__)

# Global connection pool
db_pool = None

async def init_db():
    """Initialize the database connection pool."""
    global db_pool
    try:
        logger.info("Creating database connection pool...")
        db_pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=5,
            max_size=20
        )
        logger.info("Database connection pool created successfully")
    except Exception as e:
        logger.error(f"Failed to create database connection pool: {e}")
        raise

async def close_db():
    """Close the database connection pool."""
    global db_pool
    if db_pool:
        logger.info("Closing database connection pool...")
        await db_pool.close()
        logger.info("Database connection pool closed")

@asynccontextmanager
async def lifespan_context(app):
    """Context manager for FastAPI lifespan."""
    await init_db()
    yield
    await close_db()

async def get_connection():
    """Dependency for getting a database connection."""
    if not db_pool:
        raise RuntimeError("Database connection pool not initialized")
    async with db_pool.acquire() as conn:
        yield conn