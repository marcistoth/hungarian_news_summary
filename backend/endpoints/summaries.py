from fastapi import APIRouter, HTTPException, Depends, Query
from backend.models import response as response_models
from typing import List, Optional
from datetime import date as dt_date
import asyncpg

router = APIRouter(tags=["summaries"])

from backend.database import get_connection
from backend.utils.textutils import normalize_domain


@router.get("/summaries", response_model=response_models.SummaryResponseModel)
async def get_summaries(
    language: str = Query(default="hu"),
    date: Optional[dt_date] = Query(default=None),
    conn: asyncpg.Connection = Depends(get_connection)
):
    """
    Retrieves news summaries from the database for a specific language and date.
    If no summaries are found for the requested date, returns the most recent from the previous day.
    """
    current_date = date if date is not None else dt_date.today()
    
    try:
        rows = await conn.fetch('''
            WITH LatestSummaries AS (
                SELECT 
                    id,
                    domain,
                    language,
                    date,
                    content,
                    created_at,
                    ROW_NUMBER() OVER (PARTITION BY domain ORDER BY created_at DESC) as row_num
                FROM 
                    summaries
                WHERE 
                    language = $1 
                    AND date = $2
            )
            SELECT id, domain, language, date, content
            FROM LatestSummaries
            WHERE row_num = 1
            ORDER BY domain
        ''', language, current_date)
        
        # If no results, try previous day
        if not rows:
            previous_date = current_date - dt_date.resolution
            rows = await conn.fetch('''
                WITH LatestSummaries AS (
                    SELECT 
                        id,
                        domain,
                        language,
                        date,
                        content,
                        created_at,
                        ROW_NUMBER() OVER (PARTITION BY domain ORDER BY created_at DESC) as row_num
                    FROM 
                        summaries
                    WHERE 
                        language = $1 
                        AND date = $2
                )
                SELECT id, domain, language, date, content
                FROM LatestSummaries
                WHERE row_num = 1
                ORDER BY domain
            ''', language, previous_date)
        
        # Convert rows to response models
        response_summaries: List[response_models.Summary] = []
        for row in rows:
            response_summaries.append(
                response_models.Summary(
                    domain=normalize_domain(row['domain']),
                    language=row['language'],
                    date=row['date'],
                    content=row['content']
                )
            )
            
        return response_models.SummaryResponseModel(summaries=response_summaries, success=True)
    except Exception as e:
        # Log the error
        raise HTTPException(status_code=500, detail=f"Failed to fetch summaries: {str(e)}")