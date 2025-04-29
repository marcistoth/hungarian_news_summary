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