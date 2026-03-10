from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from routes import router

app = FastAPI()

@app.get("/health", response_model=dict)
async def health() -> dict:
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    return """
<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"UTF-8\">
<title>BookmarkBrain API</title>
<style>
  body { background:#121212; color:#e0e0e0; font-family:Arial,Helvetica,sans-serif; padding:2rem; }
  a { color:#90caf9; text-decoration:none; }
  a:hover { text-decoration:underline; }
  pre { background:#1e1e1e; padding:1rem; overflow:auto; }
</style>
</head>
<body>
<h1>BookmarkBrain API</h1>
<p>Where every saved link becomes a searchable idea.</p>
<h2>Available Endpoints</h2>
<pre>
GET  /health                – health check
POST /api/bookmarks          – create bookmark with AI summary & tags
GET  /api/bookmarks/search   – semantic search of bookmarks (query param \"query\")
GET  /docs                   – Swagger UI
GET  /redoc                  – ReDoc UI
</pre>
<p>Tech Stack: FastAPI 0.115.0, PostgreSQL, DigitalOcean Serverless Inference (openai‑gpt‑oss‑120b), Pydantic 2.9.0, SQLAlchemy 2.0.35.</p>
<p><a href=\"/docs\">/docs</a> | <a href=\"/redoc\">/redoc</a></p>
</body>
</html>
"""

app.include_router(router, prefix="/api")
