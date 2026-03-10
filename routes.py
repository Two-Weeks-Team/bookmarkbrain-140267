from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import SessionLocal, Bookmark, Tag, AISummary, bb_bookmark_tags, Base, engine
from ai_service import generate_summary, get_semantic_embedding
from pydantic import BaseModel, Field, HttpUrl
import json
import math

router = APIRouter()

# Dependency to provide a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic request models
class BookmarkCreateRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL of the page to bookmark")
    title: str = Field(..., description="Human readable title")

class BookmarkResponse(BaseModel):
    id: str
    url: str
    title: str
    summary: str | None = None
    tags: list[str] = []
    embedding: list[float] | None = None
    created_at: str

@router.post("/bookmarks", response_model=BookmarkResponse)
async def create_bookmark(payload: BookmarkCreateRequest, db: Session = Depends(get_db)):
    # Check for existing bookmark
    existing = db.query(Bookmark).filter(Bookmark.url == str(payload.url)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bookmark already exists")

    # Call AI to get summary, tags and embedding
    ai_result = await generate_summary(str(payload.url))
    summary_text = ai_result.get("summary") or ""
    tags_list = ai_result.get("tags") or []
    embedding = ai_result.get("embedding") or []
    model_version = ai_result.get("model", "openai-gpt-oss-120b")

    # Create DB objects
    bookmark = Bookmark(url=str(payload.url), title=payload.title, summary=summary_text, embedding=embedding)
    db.add(bookmark)
    db.flush()  # get bookmark.id

    # Tags – create if not exist
    tag_objs = []
    for tag_name in tags_list:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.flush()
        tag_objs.append(tag)
        # association row confidence placeholder
        stmt = bb_bookmark_tags.insert().values(
            bookmark_id=bookmark.id,
            tag_id=tag.id,
            confidence_score=1.0,
            created_at=bookmark.created_at,
        )
        db.execute(stmt)

    # AI summary record
    ai_summary = AISummary(
        bookmark_id=bookmark.id,
        summary_text=summary_text,
        confidence_score=1.0,
        model_version=model_version,
    )
    db.add(ai_summary)
    db.commit()
    db.refresh(bookmark)

    return BookmarkResponse(
        id=bookmark.id,
        url=bookmark.url,
        title=bookmark.title,
        summary=bookmark.summary,
        tags=tags_list,
        embedding=embedding,
        created_at=bookmark.created_at.isoformat(),
    )

class SearchResult(BaseModel):
    id: str
    title: str
    similarity: float

class SearchResponse(BaseModel):
    results: list[SearchResult]

@router.get("/bookmarks/search", response_model=SearchResponse)
async def search_bookmarks(query: str = Query(..., description="Search phrase"), db: Session = Depends(get_db)):
    # Get embedding for query via AI
    embed_resp = await get_semantic_embedding(query)
    query_vec = embed_resp.get("embedding")
    if not query_vec:
        raise HTTPException(status_code=500, detail="Failed to obtain embedding from AI")

    # Load all bookmarks with embeddings
    bookmarks = db.query(Bookmark).filter(Bookmark.embedding.is_not(None)).all()
    if not bookmarks:
        return SearchResponse(results=[])

    def cosine(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

    scored = []
    for bm in bookmarks:
        try:
            sim = cosine(query_vec, bm.embedding)
        except Exception:
            sim = 0.0
        scored.append((sim, bm))

    # Sort by similarity descending and take top 10
    top = sorted(scored, key=lambda x: x[0], reverse=True)[:10]
    results = [SearchResult(id=b.id, title=b.title, similarity=round(sim, 4)) for sim, b in top]
    return SearchResponse(results=results)
