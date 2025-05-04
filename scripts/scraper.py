import sys
import os
import asyncio
import asyncpg
from datetime import date, datetime, timezone, timedelta
from bs4 import BeautifulSoup
import requests
from typing import List
from dateutil import parser as date_parser
from dotenv import load_dotenv
import re

load_dotenv()

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

gmt_plus_2 = timezone(timedelta(hours=2))

db_url = os.getenv("DATABASE_URL")

from llm import llm_service



# Import settings, models, and Base from the backend
from backend.config import settings
from backend.models.db_models import ScrapedArticle, Summary, DomainAnalysis

async def get_connection():
    """Returns a database connection from the pool."""
    return await asyncpg.connect(db_url)

#function which cleans up the scraped article table
async def cleanup_scraped_articles():
    """Cleans up the scraped articles table using asyncpg directly."""
    conn = await get_connection()
    try:
        await conn.execute("DELETE FROM scraped_articles")
        print("Scraped articles cleaned up successfully.")
    except Exception as e:
        print(f"Error cleaning up scraped articles: {e}")
    finally:
        await conn.close()

async def insert_article_to_db(article: ScrapedArticle):
    """Inserts an article into the database using asyncpg directly."""
    conn = await get_connection()
    try:
        await conn.execute('''
        INSERT INTO scraped_articles (url, domain, title, content, publication_date, scraped_at)
        VALUES ($1, $2, $3, $4, $5, $6)
        ''', article.url, article.domain, article.title, article.content, 
            article.publication_date, article.scraped_at)
        print(f"Article '{article.title}' inserted into DB")
    except Exception as e:
        print(f"Error inserting article: {e}")
    finally:
        await conn.close()

async def insert_summary_to_db(summary: Summary):
    """Inserts a summary into the database using asyncpg directly."""
    conn = await get_connection()
    try:
        await conn.execute('''
        INSERT INTO summaries (domain, language, date, content)
        VALUES ($1, $2, $3, $4)
        ''', summary.domain, summary.language, summary.date, summary.content)
        print(f"Summary for {summary.domain} inserted into DB")
    except Exception as e:
        print(f"Error inserting summary: {e}")
    finally:
        await conn.close()

async def store_domain_analysis(analysis: DomainAnalysis):
    """
    Store domain analysis in the database.
    
    Args:
        analysis: A DomainAnalysis object containing the analysis data
    """
    if not analysis or not analysis.topics:
        print("No analysis data to store")
        return
        
    conn = await get_connection()
    try:
        # Insert domain analysis
        domain_analysis_id = await conn.fetchval('''
        INSERT INTO domain_analyses (domain, date)
        VALUES ($1, $2)
        RETURNING id
        ''', analysis.domain, analysis.date)
        
        # Insert each topic
        for topic in analysis.topics:
            topic_analysis_id = await conn.fetchval('''
            INSERT INTO topic_analyses 
            (domain_analysis_id, topic_name, political_leaning, sentiment, framing, article_urls)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
            ''', domain_analysis_id, topic.topic, topic.political_leaning, 
                topic.sentiment, topic.framing, topic.article_urls)
                
            # Insert key phrases for this topic
            for phrase in topic.key_phrases:
                await conn.execute('''
                INSERT INTO key_phrases (topic_analysis_id, phrase)
                VALUES ($1, $2)
                ''', topic_analysis_id, phrase)
                
        print(f"Analysis for {analysis.domain} stored successfully")
    except Exception as e:
        print(f"Error storing analysis: {e}")
    finally:
        await conn.close()

async def generate_cross_source_analysis(target_date=None):
    """
    Use LLM to analyze how different news sources cover the same topics.
    
    Args:
        target_date: Optional date to analyze. Defaults to today.
        
    Returns:
        LLM-generated analysis comparing coverage across sources.
    """
    if target_date is None:
        target_date = date.today()
    
    conn = await get_connection()
    try:
        # Get raw topic data from all sources on the target date
        source_data_by_domain = {}
        
        rows = await conn.fetch('''
        WITH topic_data AS (
            SELECT 
                da.domain,
                da.date,
                ta.topic_name,
                ta.political_leaning,
                ta.sentiment,
                ta.framing,
                ta.article_urls,
                array_agg(kp.phrase) as key_phrases
            FROM 
                domain_analyses da
            JOIN 
                topic_analyses ta ON da.id = ta.domain_analysis_id
            LEFT JOIN 
                key_phrases kp ON ta.id = kp.topic_analysis_id
            WHERE 
                da.date = $1
            GROUP BY
                da.domain, da.date, ta.id, ta.topic_name, ta.political_leaning, ta.sentiment, ta.framing, ta.article_urls
        )
        SELECT * FROM topic_data
        ''', target_date)
        
        if not rows:
            return {"error": f"No analysis data found for {target_date}"}
            
        # Organize data by domain for LLM input
        for row in rows:
            domain = row['domain']
            if domain not in source_data_by_domain:
                source_data_by_domain[domain] = []
                
            source_data_by_domain[domain].append({
                "topic": row['topic_name'],
                "sentiment": row['sentiment'],
                "political_leaning": row['political_leaning'],
                "key_phrases": row['key_phrases'],
                "framing": row['framing'],
                "article_urls": row['article_urls'] or []
            })
        
        # Format the data for the LLM prompt
        llm_input = f"Date: {target_date.isoformat()}\n\n"
        for domain, topics in source_data_by_domain.items():
            llm_input += f"Source: {domain}\n"
            for i, topic in enumerate(topics, 1):
                llm_input += f"  Topic {i}: {topic['topic']}\n"
                llm_input += f"    Sentiment: {topic['sentiment']}\n"
                llm_input += f"    Political Leaning: {topic['political_leaning']}\n"
                llm_input += f"    Key Phrases: {', '.join(topic['key_phrases'])}\n"
                llm_input += f"    Framing: {topic['framing']}\n"
                if topic['article_urls']:
                    llm_input += f"    Article URLs: {', '.join(topic['article_urls'])}\n"
            llm_input += "\n"
        
        response = llm_service.cross_source_analysis(target_date, llm_input)
            
        return response
        
    except Exception as e:
        print(f"Error generating cross-source analysis: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    finally:
        await conn.close()

async def store_cross_source_analysis(analysis_data):
    """Store the cross-source analysis in the database."""
    if "error" in analysis_data or not analysis_data.get("unified_topics"):
        print(f"No valid analysis data to store: {analysis_data}")
        return
        
    conn = await get_connection()
    try:
        # Convert to JSON string for storage
        import json
        from datetime import datetime
        
        analysis_json = json.dumps(analysis_data, ensure_ascii=False)
        
        # Convert string date to date object
        date_str = analysis_data.get("date")
        if isinstance(date_str, str):
            try:
                # Parse the date string to a date object
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                # Fallback to today's date if parsing fails
                date_obj = date.today()
                print(f"Warning: Could not parse date '{date_str}', using today's date instead")
        else:
            # Use today's date if no date is provided
            date_obj = date.today()
            
        # Store in a new cross_source_analyses table
        await conn.execute('''
        INSERT INTO cross_source_analyses (date, analysis_json)
        VALUES ($1, $2)
        ''', date_obj, analysis_json)
            
        print(f"Cross-source analysis stored successfully for {date_obj}")
    except Exception as e:
        print(f"Error storing cross-source analysis: {e}")
    finally:
        await conn.close()

async def scrape_telex():
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
        title_element = soup.find('h1')
        if title_element is None:
            print(f"No h1 tag found for {url + href}")
            # Try alternative selectors
            title_element = soup.find(class_='article-title')
            if title_element is None:
                print(f"No title element found, skipping {href}")
                continue
                
        title = title_element.text.strip().replace('\n', '')

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
    await insert_summary_to_db(summary_obj)

    analysis_data = llm_service.extract_domain_topics(articles)
    
    await store_domain_analysis(analysis_data)

    print(f"telex summary inserted into db")


async def scrape_origo(): 
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
    await insert_summary_to_db(summary_obj)

    analysis_data = llm_service.extract_domain_topics(articles)
    
    await store_domain_analysis(analysis_data)

    print(f"origo summary inserted into db")

async def scrape_mandiner():    
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
    await insert_summary_to_db(summary_obj)

    analysis_data = llm_service.extract_domain_topics(articles)
    
    await store_domain_analysis(analysis_data)

    print(f"mandiner summary inserted into db")

async def scrape_hvg():
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
    await insert_summary_to_db(summary_obj)

    analysis_data = llm_service.extract_domain_topics(articles)
    
    await  store_domain_analysis(analysis_data)

    print(f"hvg summary inserted into db")

async def scrape_negynegynegy():
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
            url=href,
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
    await insert_summary_to_db(summary_obj)

    analysis_data = llm_service.extract_domain_topics(articles)
    
    await store_domain_analysis(analysis_data)

    print(f"444 summary inserted into db")

async def scrape_24ponthu():
    url = "https://www.24.hu"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    a_elements = soup.find_all('a', href=True)

    # Regular expression to match URLs with date pattern YYYY/MM/DD
    date_pattern = r'https://24\.hu/[^/]+/(\d{4})/(\d{2})/(\d{2})/'

    hrefs = []
    for a in a_elements:
        href = a['href']
        if href and re.match(date_pattern, href) and href not in hrefs:
            hrefs.append(href)

    articles = []

    for href in hrefs:

        response = requests.get(href)
        soup = BeautifulSoup(response.text, "html.parser")
        title_element = soup.find('h1', class_='o-post__title')
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

        content_element = soup.find('div', class_='u-onlyArticlePages')
        for tag in content_element.find_all(True):
            if tag.name != 'p':
                tag.decompose()
        content = content_element.text.strip().replace('\n', '')

        print(f"  Title: {title}")
        print(f"  Date: {publication_date}")

        article_obj = ScrapedArticle(
            url=href,
            domain="24.hu",
            title=title,
            content=content,
            scraped_at=datetime.now(tz=gmt_plus_2),
            publication_date=publication_date,
        )
        articles.append(article_obj)

    response = llm_service.summarize_multiple_articles(articles)
    print(f"24ponthu response generated")
    summary_obj = Summary(
        domain="24.hu",
        language="hu",
        date=datetime.now(tz=gmt_plus_2),
        content=response
    )
    await insert_summary_to_db(summary_obj)

    analysis_data = llm_service.extract_domain_topics(articles)
    
    await store_domain_analysis(analysis_data)


    print(f"24ponthu summary inserted into db")

async def scrape_vadhajtasok():
    url = "https://www.vadhajtasok.hu"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    a_elements = soup.find_all('a', href=True)

    hrefs = []
    for a in a_elements:
        href = a['href']
        if href and href.startswith('https://www.vadhajtasok.hu/') and href not in hrefs:
            hrefs.append(href)

    hrefs.remove('https://www.vadhajtasok.hu/')
    hrefs.remove('https://www.vadhajtasok.hu/impresszum')
    hrefs.remove('https://www.vadhajtasok.hu/szerzoi-jogok')
    hrefs.remove('https://www.vadhajtasok.hu/adatvedelmi-szabalyzat')

    articles = []

    for href in hrefs:
        response = requests.get(href)
        soup = BeautifulSoup(response.text, "html.parser")
        title_element = soup.find('meta', attrs={'property': 'og:title'})
        if title_element is None:
            print(f"No title found for {href}")
            continue
        title = title_element.text.strip().replace('\n', '')

        parts = href.strip('/').split('/')
        publication_date = None

        # Extracting the date from the url
        if len(parts) >= 6 and parts[3].isdigit() and parts[4].isdigit() and parts[5].isdigit():
            date_str = f"{parts[3]}/{parts[4]}/{parts[5]}" # Reconstruct YYYY/MM/DD
            try:
                publication_date = datetime.strptime(date_str, "%Y/%m/%d").date()
            except ValueError:
                print(f"Invalid date format in URL: {href}")
                continue
        else:
            print(f"Could not find expected date format in href: {href}")
            continue
        
        if publication_date != date.today():
            print(f"Skipping article (not target date): {href} with publication date: {publication_date}")
            continue

        content_element = soup.find('div', class_='post-content')
        for tag in content_element.find_all(True):
            if tag.name != 'p':
                tag.decompose()
        content = content_element.text.strip().replace('\n', '')

        print(f"  Title: {title}")
        print(f"  Date: {publication_date}")
        print(f"\n {content} \n")

        article_obj = ScrapedArticle(
            url=href,
            domain="vadhajtasok",
            title=title,
            content=content,
            scraped_at=datetime.now(tz=gmt_plus_2),
            publication_date=publication_date,
        )
        articles.append(article_obj)
    
    response = llm_service.summarize_multiple_articles(articles)
    print(f"vadhajtasok response generated")
    summary_obj = Summary(
        domain="vadhajtasok",
        language="hu",
        date=datetime.now(tz=gmt_plus_2),
        content=response
    )
    await insert_summary_to_db(summary_obj)

    analysis_data = llm_service.extract_domain_topics(articles)
    
    await store_domain_analysis(analysis_data)

    print(f"vadhajtasok summary inserted into db")


async def run_full_analysis_pipeline():
    """Run the complete analysis pipeline for all sources."""
    current_date = date.today()
    
    await scrape_telex()
    await scrape_origo()
    await scrape_hvg()
    await scrape_mandiner()
    await scrape_negynegynegy()
    await scrape_24ponthu()
    await scrape_vadhajtasok()

    try:
        print("Generating cross-source analysis...")
        cross_analysis = await generate_cross_source_analysis(current_date)

        #save the analysis in a separate file for debugging

        with open("cross_source_analysis.json", "w", encoding="utf-8") as f:
            import json
            json.dump(cross_analysis, f, ensure_ascii=False, indent=4)
        
        # Store the cross-source analysis in a new table
        print("Storing cross-source analysis in database...")
        await store_cross_source_analysis(cross_analysis)
        
        print("Analysis pipeline completed successfully")
    except Exception as e:
        print(f"Error in cross-source analysis: {e}")

if __name__ == "__main__":
    print("Running scraper script...")
    asyncio.run(run_full_analysis_pipeline())
    print("Script finished.")