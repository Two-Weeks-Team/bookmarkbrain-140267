import os
from uuid import uuid4
from datetime import datetime
from sqlalchemy import (Column, String, Text, DateTime, Float, JSON,
                        ForeignKey, Table, create_engine, event)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

# Resolve database URL with required transformations
_raw_url = os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))
if _raw_url.startswith("postgresql+asyncpg://"):
    _raw_url = _raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
elif _raw_url.startswith("postgres://"):
    _raw_url = _raw_url.replace("postgres://", "postgresql+psycopg://")

# Determine if we need SSL args (non‑localhost and not SQLite)
_use_ssl = not (_raw_url.startswith("sqlite")) and "localhost" not in _raw_url and "127.0.0.1" not in _raw_url
engine_kwargs = {}
if _use_ssl:
    engine_kwargs["connect_args"] = {"sslmode": "require"}

engine = create_engine(_raw_url, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Association table for many‑to‑many Bookmark <-> Tag
bb_bookmark_tags = Table(
    "bb_bookmark_tags",
    Base.metadata,
    Column("bookmark_id", String, ForeignKey("bb_bookmarks.id"), primary_key=True),
    Column("tag_id", String, ForeignKey("bb_tags.id"), primary_key=True),
    Column("confidence_score", Float, nullable=False, default=0.0),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
)

class Bookmark(Base):
    __tablename__ = "bb_bookmarks"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    url = Column(Text, nullable=False, unique=True)
    title = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    # Store AI generated embedding as JSON array of floats for simplicity
    embedding = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)

    # Relationships
    tags = relationship("Tag", secondary=bb_bookmark_tags, back_populates="bookmarks")
    ai_summary = relationship("AISummary", uselist=False, back_populates="bookmark")

class Tag(Base):
    __tablename__ = "bb_tags"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    bookmarks = relationship("Bookmark", secondary=bb_bookmark_tags, back_populates="tags")

class AISummary(Base):
    __tablename__ = "bb_ai_summaries"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    bookmark_id = Column(String, ForeignKey("bb_bookmarks.id"), nullable=False, unique=True)
    summary_text = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False, default=0.0)
    model_version = Column(String, nullable=False, default="unknown")
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    bookmark = relationship("Bookmark", back_populates="ai_summary")

# Ensure tables are created (useful for the lightweight example)
@event.listens_for(Base.metadata, "before_create")
def receive_before_create(target, connection, **kw):
    pass
