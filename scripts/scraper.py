import sys
import os
import asyncio
from datetime import date, datetime, timezone, timedelta
from bs4 import BeautifulSoup
import requests
from typing import List
from dateutil import parser as date_parser

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

gmt_plus_2 = timezone(timedelta(hours=2))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from llm import llm_service



# Import settings, models, and Base from the backend
from backend.config import settings
from backend.models.db_models import ScrapedArticle, Summary
from backend.database import Base # Needed if creating tables directly (optional here)

#function which cleans up the scraped article table
async def cleanup_scraped_articles():
    """Cleans up the scraped articles table."""
    # Consider creating the engine and session factory once outside the function
    # if you call this and other DB functions frequently in the same script run.
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    AsyncSessionFactory = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with AsyncSessionFactory() as session:
        async with session.begin():
            # Wrap the raw SQL string in text()
            await session.execute(text("DELETE FROM scraped_articles"))
            # No need for explicit commit() within session.begin() context manager
            print("Scraped articles cleaned up successfully.")
        # No need for explicit close() when using 'async with session:'
    await engine.dispose()

async def insert_articles_to_db(article_objects: List[ScrapedArticle]):
    """Inserts a list of pre-created ScrapedArticle objects into the database."""
    if not article_objects:
        print("No articles provided to insert.")
        return

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionFactory = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with AsyncSessionFactory() as session:
        async with session.begin():
            print(f"Adding {len(article_objects)} articles to session...")
            session.add_all(article_objects)
        print("Article insertion transaction committed.")
    await engine.dispose()

async def insert_summary_to_db(summary_obj: Summary):
    """Inserts a pre-created Summary object into the database."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionFactory = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with AsyncSessionFactory() as session:
        async with session.begin():
            session.add(summary_obj)
            print(f"Adding summary for domain '{summary_obj.domain}' date '{summary_obj.date}' to session.")
        print("Summary insertion transaction committed.")
    await engine.dispose()

def scrape_telex():
    url = "https://www.telex.hu"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.find_all(class_='item__title')

    hrefs = []
    for element in elements:
        href = element.get('href')
        if href and not href.startswith('https')and href not in hrefs:
            hrefs.append(href)
    
    articles = []

    for href in hrefs:
        parts = href.strip('/').split('/')
        publication_date = None
        # Extracting the date from the url
        if len(parts) >= 4 and parts[1].isdigit() and parts[2].isdigit() and parts[3].isdigit():
            date_str = f"{parts[1]}/{parts[2]}/{parts[3]}" # Reconstruct YYYY/MM/DD
            try:
                publication_date = datetime.strptime(date_str, "%Y/%m/%d").date()
            except ValueError:
                print(f"Invalid date format in URL: {href}")
                continue
        else:
            print(f"Warning: Could not find expected date format in href: {href}")
            continue

        
        response = requests.get(url + href)
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find('h1').text.strip().replace('\n', '')

        # if the publication date is not from today, skip the article
        if publication_date != date.today():
            print(f"Skipping article: {title} with publication date: {publication_date}")
            continue

        # Find the content element
        content_element = soup.find(class_='article-html-content')

        # Remove elements with class 'ad'
        for ad in content_element.find_all(class_='ad'):
            ad.decompose()
        
        content = content_element.text.strip().replace('\n', '')


        print(f"URL: {url + href}")
        print(f"Title: {title}")
        print(f"Publication Date: {publication_date}") # Print the parsed date object
        print("-" * 20)

        article_obj = ScrapedArticle(
            url=url + href,
            domain="telex",
            title=title,
            content=content,
            scraped_at=datetime.now(timezone.utc),
            publication_date=publication_date
        )
    
        articles.append(article_obj)

    response = llm_service.summarize_multiple_articles(articles)
    print(f"telex response generated")
    summary_obj = Summary(
        domain="telex",
        language="hu",
        date=datetime.now(tz=gmt_plus_2),
        content=response
    )
    asyncio.run(insert_summary_to_db(summary_obj))
    print(f"telex summary inserted into db")


def scrape_origo(): 
    url = "https://www.origo.hu"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.find_all(class_='article-card-link')

    hrefs = []
    for element in elements:
        href = element.get('href')
        if href and not href.startswith('https') and href not in hrefs:
            hrefs.append(href)
            print(href)
    
    articles: List[ScrapedArticle] = []
    
    for href in hrefs:
        response = requests.get(url + href)
        soup = BeautifulSoup(response.text, "html.parser")

        #extracting time tag

        published_time_tag = soup.find('meta', attrs={'name': 'article:published_time'})
        publication_date = None
        if published_time_tag and published_time_tag.get('content'):
            date_str = published_time_tag['content']
            try:
                # Parse the ISO 8601 format string
                publication_datetime = datetime.fromisoformat(date_str)
                # Extract just the date part
                publication_date = publication_datetime.date()
            except ValueError:
                print(f"Warning: Could not parse date string '{date_str}' from meta tag in {href}")
        else:
            print(f"Warning: Could not find publication time meta tag in {href}")
        
        if publication_date != date.today():
            print(f"Skipping article (not target date): {href} with publication date: {publication_date}")
            continue

        title_element = soup.find('h1', class_='article-title')

        if title_element is None:
            print(f"No title found for {href}")
            continue

        title = title_element.text.strip().replace('\n', '')

        header_element = soup.find(class_='article-lead')
        if header_element is None:
            print(f"No header found for {href}")
            continue

        header = header_element.text.strip().replace('\n', '')

        content_element = soup.find(class_='block-content')
        if content_element is None:
            print(f"No content found for {href}")
            continue

        content = content_element.text.strip().replace('\n', '')

        content = header + " " + content

        print(f"  Title: {title}")
        print(f"  Date: {publication_date}")

        article_obj = ScrapedArticle(
            url=url + href,
            domain="origo",
            title=title,
            content=content,
            scraped_at=datetime.now(tz=gmt_plus_2),
            publication_date=publication_date,
        )
        articles.append(article_obj)
    
    response = llm_service.summarize_multiple_articles(articles)
    print(f"origo response generated")
    summary_obj = Summary(
        domain="origo",
        language="hu",
        date=datetime.now(tz=gmt_plus_2),
        content=response
    )
    asyncio.run(insert_summary_to_db(summary_obj))
    print(f"origo summary inserted into db")

def scrape_mandiner():    
    url = "https://www.mandiner.hu"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.find_all(class_='article-card-link')

    hrefs = []
    for element in elements:
        href = element.get('href')
        if href and not href.startswith('https') and href not in hrefs:
            hrefs.append(href)
            print(href)
    
    articles = []
    
    for href in hrefs:
        response = requests.get(url + href)
        soup = BeautifulSoup(response.text, "html.parser")
        title_element = soup.find('h1', class_='article-page-title')

        if title_element is None:
            print(f"No title found for {href}")
            continue

        title = title_element.text.strip().replace('\n', '')

        published_time_tag = soup.find('meta', attrs={'name': 'article:published_time'})
        publication_date = None
        if published_time_tag and published_time_tag.get('content'):
            date_str = published_time_tag['content']
            try:
                # Parse the ISO 8601 format string
                publication_datetime = datetime.fromisoformat(date_str)
                # Extract just the date part
                publication_date = publication_datetime.date()
            except ValueError:
                print(f"Warning: Could not parse date string '{date_str}' from meta tag in {href}")
        else:
            print(f"Warning: Could not find publication time meta tag in {href}")
        
        if publication_date != date.today():
            print(f"Skipping article (not target date): {href} with publication date: {publication_date}")
            continue

        header_element = soup.find(class_='article-page-lead').text.strip().replace('\n', '')
        content_element = soup.find_all(class_='block-content')

        for content in content_element:
            for i_tag in content.find_all('i'):
                if i_tag.text.startswith('Nyitókép'):
                    i_tag.decompose()

        content_element = ' '.join([content.text.strip().replace('\n', '') for content in content_element])

        content = header_element + " " + content_element

        print(f"  Title: {title}")
        print(f"  Date: {publication_date}")

        article_obj = ScrapedArticle(
            url=url + href,
            domain="mandiner",
            title=title,
            content=content,
            scraped_at=datetime.now(tz=gmt_plus_2),
            publication_date=publication_date,
        )
        articles.append(article_obj)

    response = llm_service.summarize_multiple_articles(articles)
    print(f"mandiner response generated")
    summary_obj = Summary(
        domain="mandiner",
        language="hu",
        date=datetime.now(tz=gmt_plus_2),
        content=response
    )
    asyncio.run(insert_summary_to_db(summary_obj))
    print(f"mandiner summary inserted into db")

def scrape_hvg():
    url = "https://www.hvg.hu"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    h1_elements = soup.find_all('h1')

    hrefs = []

    for h1 in h1_elements:
        a_elements = h1.find_all('a', href=True)
        for a in a_elements:
            href = a['href']
            if href and not href.startswith('https') and href not in hrefs:
                hrefs.append(href)
    
    articles = []

    for href in hrefs:
        if(href.startswith('/360')):
            print("-----------------360 articles are locked behind a paywall, cannot be parsed-----------------")
            continue

        response = requests.get(url + href)
        soup = BeautifulSoup(response.text, "html.parser")
        title_element = soup.find('h1')
        title = title_element.text.strip().replace('\n', '')

        published_time_tag = soup.find('meta', attrs={'property': 'article:published_time'})

        publication_date = None
        if published_time_tag and published_time_tag.get('content'):
            date_str = published_time_tag['content']
            try:
                # Parse the ISO 8601 format string
                publication_datetime = date_parser.parse(date_str)
                # Extract just the date part
                publication_date = publication_datetime.date()
            except ValueError:
                print(f"Warning: Could not parse date string '{date_str}' from meta tag in {href}")
        else:
            print(f"Warning: Could not find publication time meta tag in {href}")
        
        if publication_date != date.today():
            print(f"Skipping article (not target date): {href} with publication date: {publication_date}")
            continue

        content_header = soup.find('p', class_='article-lead').text.strip().replace('\n', '')
        content_divs= soup.find_all("div", class_="article-content")
        content = content_divs[1].text.strip().replace('\n', ' ')
        merged_content = content_header + " " + content

        print(f"  Title: {title}")
        print(f"  Date: {publication_date}")

        article_obj = ScrapedArticle(
            url=url + href,
            domain="hvg",
            title=title,
            content=content,
            scraped_at=datetime.now(tz=gmt_plus_2),
            publication_date=publication_date,
        )
        articles.append(article_obj)

    response = llm_service.summarize_multiple_articles(articles)
    print(f"hvg response generated")
    summary_obj = Summary(
        domain="hvg",
        language="hu",
        date=datetime.now(tz=gmt_plus_2),
        content=response
    )
    asyncio.run(insert_summary_to_db(summary_obj))
    print(f"hvg summary inserted into db")

def scrape_negynegynegy():
    url = "https://www.444.hu"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    a_elements = soup.find_all('a', href=True)

    hrefs = []
    for a in a_elements:
        href = a['href']
        if href and href.startswith('https://444.hu/') and href not in hrefs:
            hrefs.append(href)
            print(href)
    
    hrefs.remove('https://444.hu/kor')
    hrefs.remove('https://444.hu/szerzoi-jogok')
    hrefs.remove('https://444.hu/adatvedelmi-nyilatkozat')
    hrefs.remove('https://444.hu/mediaajanlat')
    hrefs.remove('https://444.hu/tamogatas-altalanos-szerzodesi-feltetelek')

    articles = []

    for href in hrefs:

        response = requests.get(href)
        soup = BeautifulSoup(response.text, "html.parser")
        title_element = soup.find('h1', class_='_18v5wa35')
        if title_element is None:
            print(f"No title found for {href}")
            continue
        title = title_element.text.strip().replace('\n', '')

        published_time_tag = soup.find('meta', attrs={'property': 'article:published_time'})

        publication_date = None
        if published_time_tag and published_time_tag.get('content'):
            date_str = published_time_tag['content']
            try:
                # Parse the ISO 8601 format string
                publication_datetime = date_parser.parse(date_str)
                # Extract just the date part
                publication_date = publication_datetime.date()
            except ValueError:
                print(f"Warning: Could not parse date string '{date_str}' from meta tag in {href}")
        else:
            print(f"Warning: Could not find publication time meta tag in {href}")
        
        if publication_date != date.today():
            print(f"Skipping article (not target date): {href} with publication date: {publication_date}")
            continue

        #  if there is a html element where the href is #livestream__icon-live, then the article should be skipped, cause its live and has a different format
        if soup.find(href='#livestream__icon-live') is not None:
            print(f"Article is a live stream, skipping {href}")
            continue

        content_element = soup.find('div', class_='jogfs53')
        for tag in content_element.find_all(True):
            if tag.name != 'p':
                tag.decompose()
        content = content_element.text.strip().replace('\n', '')

        print(f"  Title: {title}")
        print(f"  Date: {publication_date}")

        article_obj = ScrapedArticle(
            url=url + href,
            domain="444",
            title=title,
            content=content,
            scraped_at=datetime.now(tz=gmt_plus_2),
            publication_date=publication_date,
        )
        articles.append(article_obj)

    response = llm_service.summarize_multiple_articles(articles)
    print(f"444 response generated")
    summary_obj = Summary(
        domain="444",
        language="hu",
        date=datetime.now(tz=gmt_plus_2),
        content=response
    )
    asyncio.run(insert_summary_to_db(summary_obj))
    print(f"444 summary inserted into db")


if __name__ == "__main__":
    print("Running scraper script...")
    scrape_telex()
    scrape_origo()
    scrape_mandiner()
    scrape_hvg()
    scrape_negynegynegy()
    print("Script finished.")