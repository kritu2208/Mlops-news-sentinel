import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class RawArticle(Base):
    __tablename__ = 'raw_articles'

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    url = Column(String(500), unique=True, nullable=False)
    source = Column(String(100))
    published_at = Column(DateTime)
    full_text = Column(Text)
    processed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProcessedArticle(Base):
    __tablename__ = 'processed_articles'

    id = Column(Integer, primary_key=True)
    raw_article_id = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    sentiment_score = Column(Float)
    sentiment_label = Column(String(20))
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


# Project root directory (adjust if your scripts folder is elsewhere)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'scripts', 'news_data.db')


def init_db():
    # Use absolute DB path to avoid multiple DB copies
    db_engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={'check_same_thread': False})
    Base.metadata.create_all(db_engine)
    return db_engine


def get_session(eng):
    sessionclass = sessionmaker(bind=eng)
    return sessionclass()


if __name__ == "__main__":
    print("Initializing DB at:", DB_PATH)
    engine = init_db()
    print("DB initialized.")
