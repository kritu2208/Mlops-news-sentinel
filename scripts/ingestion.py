import requests
from bs4 import BeautifulSoup
from datetime import datetime
from config.credentials import NEWSAPI_KEY
from scripts.database import get_session, RawArticle, init_db


def fetch_news_from_api():
    """
    Fetches top headlines from NewsAPI with time filtering.
    Returns a list of articles or an empty list on failure.
    """
    url = 'https://newsapi.org/v2/top-headlines'

    # Calculate date for recent articles (last 24 hours)
    from datetime import datetime, timedelta
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    params = {
        'apiKey': NEWSAPI_KEY,
        'category': 'technology',
        'pageSize': 30,  # Increased from 20 to 30
        'country': 'us',
        # 'from': yesterday,        # Uncomment if you have paid NewsAPI plan
        # 'sortBy': 'publishedAt'   # Sort by newest first
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        print(f"Fetched {len(data.get('articles', []))} articles from API")
        return data.get('articles', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from NewsAPI: {e}")
        return []


def extract_text_simple(url):
    """
    Simple text extraction using BeautifulSoup instead of newspaper3k
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Use BeautifulSoup to extract text
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        # Try to find the main content
        selectors = ['article', 'main', '[role="main"]', '.content', '.article-body', '.post-content']
        content = None

        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                break

        # If no specific content found, use body
        if not content:
            content = soup.body or soup

        # Get text and clean it
        text = content.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text[:1500]  # Return first 1500 characters

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""


def run_ingestion():
    print("Starting news ingestion...")

    # Fetch articles first
    articles = fetch_news_from_api()

    if not articles:
        print("No articles fetched from API. Stopping.")
        return
    engine = init_db()  # Initializes and connects using absolute path
    session = get_session(engine)

    new_article_count = 0
    for article_data in articles:
        # Check duplicates by URL
        if session.query(RawArticle).filter_by(url=article_data['url']).first():
            print(f"Skipping duplicate article: {article_data['url']}")
            continue
        try:
            published_time = datetime.fromisoformat(article_data['publishedAt'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            published_time = datetime.utcnow()

            # Your scraping and insertion logic:
        full_text = extract_text_simple(article_data['url'])
        if not full_text and article_data.get('description'):
            full_text = article_data['description']

        # Your existing scrape and insert logic
        # Mark processed=0 always for new inserts
        new_article = RawArticle(
            title=article_data['title'],
            description=article_data.get('description'),
            url=article_data['url'],
            source=article_data.get('source', {}).get('name', 'Unknown'),
            published_at=published_time,
            full_text=full_text,
            processed=0
        )
        session.add(new_article)
        new_article_count += 1

    try:
        session.commit()
        total_raw_articles = session.query(RawArticle).count()
        print(f"Successfully stored {new_article_count} new articles.")
        print(f"Total raw articles in DB now: {total_raw_articles}")
    except Exception as e:
        session.rollback()
        print(f"DB error during ingestion: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    run_ingestion()
