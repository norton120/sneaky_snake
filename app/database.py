from sqlalchemy import create_engine, Column, String, Text, Boolean, DateTime
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

    request_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    processed_at = Column(DateTime, nullable=True)
    url = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    processed = Column(Boolean, nullable=False, default=False)
    errors = Column(String, nullable=True)
    selector = Column(String, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()