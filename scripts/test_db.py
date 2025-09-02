from scripts.database import init_db, get_session, RawArticle, ProcessedArticle

engine = init_db()
session = get_session(engine)

print("=== LATEST RAW ARTICLES (PROCESSED STATUS) ===")
raw_articles = session.query(RawArticle).order_by(RawArticle.id.desc()).limit(3).all()
for article in raw_articles:
    print(f"ID: {article.id} | Title: {article.title[:50]}... | Processed: {article.processed}")

print("\n=== LATEST PROCESSED ARTICLES (ANALYSIS) ===")
processed_articles = session.query(ProcessedArticle).order_by(ProcessedArticle.id.desc()).limit(3).all()
for article in processed_articles:
    print(f"ID: {article.id} | Sentiment: {article.sentiment_label} ({article.sentiment_score:.2f}) | Category: {article.category}")
    print(f"Title: {article.title[:60]}...\n")

session.close()