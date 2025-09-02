from transformers import pipeline
#from vaderSentiment import SentimentIntensityAnalyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from scripts.database import init_db, get_session, RawArticle, ProcessedArticle
from typing import Optional, Dict

import sys
print("Python executable:", sys.executable)


analyzer = SentimentIntensityAnalyzer()
_classifier = None


def get_classifier():
    """Lazily load the zero-shot classifier on first use."""
    global _classifier
    if _classifier is None:
        try:
            print("Loading Zero-Shot Classification model... (This may take a moment on first run)")
            _classifier = pipeline("zero-shot-classification",
                                   model="typeform/distilbert-base-uncased-mnli",
                                   device=-1)
        except Exception as e:
            print(f"Error loading the model: {e}")
            print("Falling back to rule-based categorization.")
    return _classifier


def analyze_sentiment(text: Optional[str]) -> Dict[str, object]:
    """Analyze sentiment of text using VADER."""
    if not text or not text.strip():
        return {'score': 0.0, 'label': 'Neutral'}

    score = analyzer.polarity_scores(text)['compound']
    label = 'Positive' if score >= 0.05 else 'Negative' if score <= -0.05 else 'Neutral'
    return {'score': score, 'label': label}


def categorize_article(title: Optional[str], description: Optional[str]) -> str:
    """Categorize article using zero-shot classifier or fallback rules."""
    classifier = get_classifier()
    full_text = (title or '') + ' ' + (description or '')
    if not full_text.strip():
        return 'General'

    if classifier is None:
        # Simple fallback categorization rules
        text_lower = full_text.lower()
        if any(keyword in text_lower for keyword in ['python', 'ai', 'tech']):
            return 'Technology'
        if any(keyword in text_lower for keyword in ['stock', 'finance']):
            return 'Business'
        if any(keyword in text_lower for keyword in ['election', 'trump', 'biden']):
            return 'Politics'
        return 'General'

    sequence_to_classify = full_text[:1000]  # Limit length for model

    candidate_labels = [
        "technology",
        "politics",
        "business",
        "science",
        "entertainment",
        "health",
        "sports",
        "art"
    ]

    result = classifier(sequence_to_classify, candidate_labels, multi_label=False)
    predicted_label = result['labels'][0]
    confidence = result['scores'][0]
    return predicted_label.title() if confidence >= 0.3 else 'General'


def process_articles():
    """Process all unprocessed articles: sentiment, categorization, save results."""
    print("Starting article processing...")

    engine = init_db()
    session = get_session(engine)

    unprocessed = session.query(RawArticle).filter(RawArticle.processed==0).all()
    if not unprocessed:
        print("No unprocessed articles found.")
        session.close()
        return

    print(f"Found {len(unprocessed)} articles to process.")
    processed_count = 0

    for raw_article in unprocessed:
        sentiment = analyze_sentiment(raw_article.title)
        category = categorize_article(raw_article.title, raw_article.description)

        processed_article = ProcessedArticle(
            raw_article_id=raw_article.id,
            title=raw_article.title,
            sentiment_score=sentiment['score'],
            sentiment_label=sentiment['label'],
            category=category
        )

        session.add(processed_article)
        raw_article.processed = 1
        processed_count += 1

    try:
        session.commit()
        print(f"Successfully processed {processed_count} articles.")
    except Exception as err:
        session.rollback()
        print(f"Error during processing: {err}")
    finally:
        session.close()

    print("Processing complete.")


if __name__ == "__main__":
    process_articles()


