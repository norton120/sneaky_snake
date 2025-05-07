from sqlalchemy import create_engine, Column, String, Text, Boolean, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

SQLALCHEMY_DATABASE_URL = "sqlite:///./scrape_results.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ScrapeResult(Base):
    __tablename__ = "scrape_results"

    request_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), doc="The unique identifier for the scrape request")
    processed_at = Column(DateTime, nullable=True, doc="The date and time the scrape was processed")
    url = Column(String, nullable=False, doc="The URL that was scraped")
    content = Column(Text, nullable=True, doc="The content of the page that was scraped")
    processed = Column(Boolean, nullable=False, default=False, doc="Whether the scrape was processed")
    errors = Column(String, nullable=True, doc="Any errors that occurred during the scrape")
    selector = Column(String, nullable=True, doc="The CSS selector used to scrape the page, if any")
    timeout = Column(Integer, default=10000, doc="The timeout for the scrape in milliseconds")
# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()