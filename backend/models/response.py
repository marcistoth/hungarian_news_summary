from pydantic import BaseModel
from typing import List, Optional
from datetime import date as dt_date

class Summary(BaseModel):
    domain: str
    language: str
    date: dt_date
    content: str

class SummaryResponseModel(BaseModel):
    summaries: List[Summary]
    success: bool = True
    error: Optional[str] = None