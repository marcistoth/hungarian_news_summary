from fastapi import APIRouter, HTTPException, Depends, Query
# Import Pydantic response models
from backend.models import response as response_models
# Import DB models
from backend.models import db_models
from typing import List, Optional
from datetime import date as dt_date
# Import SQLAlchemy components
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select # Use select for queries
from backend.database import get_db

router = APIRouter(tags=["summaries"])

@router.get("/summaries", response_model=response_models.SummaryResponseModel)
async def get_summaries(
    language: str = Query(
        default="hu",
        description="The language code for the summaries (e.g., 'hu' for Hungarian)."
    ),
    date: Optional[dt_date] = Query(
        default=None,
        description="The date for which to retrieve summaries (format: YYYY-MM-DD). Defaults to the current date if not provided."
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves news summaries from the database for a specific language and date.

    Args:
        language (str): Language code. Defaults to "hu".
        date (Optional[dt_date]): Date for summaries. Defaults to today.
        db (AsyncSession): Database session dependency.

    Returns:
        SummaryResponseModel: Contains a list of summaries matching the criteria.
    """
    domain: str = "general"
    current_date = date if date is not None else dt_date.today()

    try:
        # Construct the query to select summaries matching language and date
        stmt = select(db_models.Summary).where(
            db_models.Summary.language == language,
            db_models.Summary.date == current_date
        )

        # Execute the query
        result = await db.execute(stmt)
        db_summaries = result.scalars().all()

        # Convert SQLAlchemy models to Pydantic models for the response
        response_summaries: List[response_models.Summary] = []
        for db_summary in db_summaries:
            response_summaries.append(
                response_models.Summary(
                    domain=db_summary.domain,
                    language=db_summary.language,
                    date=db_summary.date,
                    content=db_summary.content
                )
            )

        return response_models.SummaryResponseModel(summaries=response_summaries, success=True)

    except Exception as e:
        # Log the error e
        raise HTTPException(status_code=500, detail=f"Failed to fetch summaries: {str(e)}")