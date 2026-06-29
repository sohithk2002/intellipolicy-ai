"""Database setup and connection management for PostgreSQL + PGVector."""
import os
from sqlalchemy import create_engine, text, Column, String, Integer, Float, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/intellipolicy")

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DocumentRecord(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    document_type = Column(String, default="policy")
    page_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    status = Column(String, default="processing")
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class ChunkRecord(Base):
    __tablename__ = "chunks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, nullable=False)
    document_name = Column(String, nullable=False)
    page_number = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    chunk_index = Column(Integer, default=0)
    embedding = Column(JSONB, nullable=True)  # stored as list; PGVector adds its own column type


class AuditRecordDB(Base):
    __tablename__ = "audit_records"
    session_id = Column(String, primary_key=True)
    question = Column(Text, nullable=False)
    retrieved_pages = Column(JSONB, default=[])
    reasoning_summary = Column(Text, default="")
    final_answer = Column(Text, default="")
    source_citations = Column(JSONB, default=[])
    steps = Column(JSONB, default=[])
    avg_confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create tables and enable pgvector extension."""
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        except Exception:
            pass
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
