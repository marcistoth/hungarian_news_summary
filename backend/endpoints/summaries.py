from fastapi import APIRouter, HTTPException, Depends, Query
from backend.models import response as response_models
from typing import List, Optional
from datetime import date as dt_date
import asyncpg

router = APIRouter(tags=["summaries"])

# Database connection pool
from backend.main import db_pool

# Dependency to get a database connection
async def get_connection():
    async with db_pool.acquire() as conn:
        yield conn

@router.get("/summaries", response_model=response_models.SummaryResponseModel)
async def get_summaries(
    language: str = Query(default="hu"),
    date: Optional[dt_date] = Query(default=None),
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Retrieves news summaries from the database for a specific language and date.
    """
    current_date = date if date is not None else dt_date.today()

    try:
        # Use raw SQL query with asyncpg instead of SQLAlchemy
        rows = await conn.fetch('''
            SELECT id, domain, language, date, content 
            FROM summaries 
            WHERE language = $1 AND date = $2
        ''', language, current_date)
        
        # Convert rows to response models
        response_summaries: List[response_models.Summary] = []
        for row in rows:
            response_summaries.append(
                response_models.Summary(
                    domain=row['domain'],
                    language=row['language'],
                    date=row['date'],
                    content=row['content']
                )
            )
            
        return response_models.SummaryResponseModel(summaries=response_summaries, success=True)
    except Exception as e:
        # Log the error
        raise HTTPException(status_code=500, detail=f"Failed to fetch summaries: {str(e)}")