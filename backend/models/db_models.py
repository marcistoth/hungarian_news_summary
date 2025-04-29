from datetime import datetime, date
from typing import List, Optional

class ScrapedArticle():
    def __init__(self, url, domain, title, content, scraped_at, publication_date):
        self.url = url
        self.domain = domain
        self.title = title
        self.content = content
        self.scraped_at = scraped_at
        self.publication_date = publication_date

class Summary():
    def __init__(self, domain, language, date, content):
        self.domain = domain
        self.language = language
        self.date = date
        self.content = content

# New classes for domain analysis
class KeyPhrase():
    def __init__(self, phrase: str):
        self.phrase = phrase

class TopicAnalysis():
    def __init__(
        self, 
        topic: str,
        political_leaning: str,
        sentiment: str,
        framing: Optional[str] = None,
        key_phrases: Optional[List[str]] = None
    ):
        self.topic = topic
        self.political_leaning = political_leaning
        self.sentiment = sentiment
        self.framing = framing or ""
        self.key_phrases = key_phrases or []

    def __str__(self):
        return f"Topic: {self.topic}\nSentiment: {self.sentiment}\nPolitical: {self.political_leaning}\nPhrases: {self.key_phrases}"    

class DomainAnalysis():
    def __init__(
        self,
        domain: str,
        date: date,
        topics: List[TopicAnalysis]
    ):
        self.domain = domain
        self.date = date
        self.topics = topics

    def __str__(self):
        topics_str = "\n".join([str(t) for t in self.topics])
        return f"Domain: {self.domain}, Date: {self.date}, Topics:\n{topics_str}"