from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from sqlalchemy.sql import func
from backend.database import Base # Import Base from database.py

class ScrapedArticle(Base):
    __tablename__ = "scraped_articles"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    domain = Column(String, index=True) # e.g., 'index', 'telex'
    title = Column(String)
    content = Column(Text)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    publication_date = Column(Date)

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, index=True) # e.g., 'index', 'telex'
    language = Column(String, index=True) # e.g., 'hu', 'en'
    date = Column(Date, index=True)
    content = Column(Text)