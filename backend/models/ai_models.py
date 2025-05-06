from pydantic import BaseModel, Field, validator
from typing import List, Optional
from .enums import PoliticalLeaning, Sentiment

class TopicAnalysisLLM(BaseModel):
    """Topic analysis structure for LLM responses"""
    
    topic: str = Field(..., description="Topic name")
    sentiment: Sentiment = Field(..., description="Sentiment analysis of the coverage")
    political_leaning: PoliticalLeaning = Field(..., description="Political leaning")
    framing: str = Field(..., description="Analysis of how the topic was framed")
    key_phrases: List[str] = Field(..., description="Key phrases from the coverage")
    article_urls: List[str] = Field(default_factory=list, description="URLs of articles covering this topic")

class DomainAnalysisLLM(BaseModel):
    """Domain analysis structure for LLM responses"""
    
    domain: str = Field(..., description="Domain name (e.g., telex, origo)")
    topics: List[TopicAnalysisLLM] = Field(..., description="Topics analyzed for this domain")

class SourceCoverage(BaseModel):
    """Information about how a specific source covers a topic."""
    
    domain: str = Field(..., description="The news source domain name (e.g., telex, origo)")
    original_topic_name: str = Field(..., description="The original topic name used by this source")
    sentiment: str = Field(..., description="The sentiment in the coverage (pozitív, negatív, semleges)")
    political_leaning: str = Field(..., description="The political leaning (bal, közép-bal, közép, közép-jobb, jobb)")
    key_phrases: List[str] = Field(..., description="Key phrases or quotes demonstrating the framing")
    framing: str = Field(..., description="Analysis of how the topic was framed by this source")
    article_urls: List[str] = Field(default_factory=list, description="URLs of articles covering this topic")

class UnifiedTopic(BaseModel):
    """A topic that is covered by multiple sources."""
    
    name: str = Field(..., description="Unified topic name that encompasses related topics across sources")
    source_coverage: List[SourceCoverage] = Field(..., description="How different sources cover this topic")
    comparative_analysis: str = Field(..., description="Comparative analysis of how sources differ in covering this topic")

class CrossSourceAnalysis(BaseModel):
    """Cross-source analysis comparing how different sources cover the same topics."""
    
    date: str = Field(..., description="The date of analysis in YYYY-MM-DD format")
    unified_topics: List[UnifiedTopic] = Field(..., description="List of unified topics covered by multiple sources")