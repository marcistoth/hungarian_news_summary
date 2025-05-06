from datetime import datetime, date as dateee
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from .enums import PoliticalLeaning, Sentiment

class ScrapedArticle(BaseModel):
    url: str = Field(..., description="URL of the article")
    domain: str = Field(..., description="Domain the article belongs to")
    title: str = Field(..., description="Title of the article")
    content: str = Field(..., description="Full article content")
    scraped_at: datetime = Field(..., description="When the article was scraped")
    publication_date: dateee = Field(..., description="When the article was published")
    
    class Config:
        arbitrary_types_allowed = True

class Summary(BaseModel):
    domain: str = Field(..., description="Domain the summary is for")
    language: str = Field(..., description="Language of the summary")
    date: datetime = Field(..., description="Date and time the summary was created")
    content: str = Field(..., description="Summary content")
    
    class Config:
        arbitrary_types_allowed = True

class KeyPhrase(BaseModel):
    phrase: str = Field(..., description="A key phrase extracted from articles")

class TopicAnalysis(BaseModel):
    topic: str = Field(..., description="Topic name")
    political_leaning: PoliticalLeaning = Field(..., description="Political leaning of the coverage")
    sentiment: Sentiment = Field(..., description="Sentiment analysis of the coverage")
    framing: str = Field("", description="Analysis of how the topic was framed")
    key_phrases: List[str] = Field(default_factory=list, description="Key phrases from the coverage")
    article_urls: List[str] = Field(default_factory=list, description="URLs of articles covering this topic")
    
    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        return f"Topic: {self.topic}\nSentiment: {self.sentiment}\nPolitical: {self.political_leaning}\nPhrases: {self.key_phrases} \nArticles: {self.article_urls}"

class DomainAnalysis(BaseModel):
    domain: str = Field(..., description="Domain name")
    date: dateee = Field(..., description="Analysis date")
    topics: List[TopicAnalysis] = Field(..., description="Topics analyzed for this domain")
    
    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        topics_str = "\n".join([str(t) for t in self.topics])
        return f"Domain: {self.domain}, Date: {self.date}, Topics:\n{topics_str}"