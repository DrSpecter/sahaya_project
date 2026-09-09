from sqlalchemy import create_engine, Column, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import uuid
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/sahaya.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(String, primary_key=True, index=True)
    query = Column(Text)
    language = Column(String)
    intent = Column(String)
    confidence = Column(Float)
    reason = Column(String)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
