import os
import json
import re
import httpx
from typing import Any, Dict, List

# Helper to extract JSON from LLM response (handles markdown code blocks)
def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()

_async_client: httpx.AsyncClient | None = None

def _get_client() -> httpx.AsyncClient:
    global _async_client
    if _async_client is None:
        _async_client = httpx.AsyncClient(timeout=90.0)
    return _async_client

async def _call_inference(messages: List[Dict[str, str]], max_tokens: int = 512) -> Dict[str, Any]:
    endpoint = "https://inference.do-ai.run/v1/chat/completions"
    api_key = os.getenv("DIGITALOCEAN_INFERENCE_KEY")
    model = os.getenv("DO_INFERENCE_MODEL", "openai-gpt-oss-120b")

    headers = {
        "Authorization": f"Bearer {api_key}" if api_key else "",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": max_tokens,
    }
    try:
        client = _get_client()
        response = await client.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        json_text = _extract_json(content)
        return json.loads(json_text)
    except Exception as exc:
        # Fallback response – never raise to caller
        return {"note": f"AI service temporarily unavailable: {str(exc)}"}

# Public API --------------------------------------------------------------
async def generate_summary(content: str) -> Dict[str, Any]:
    messages = [
        {"role": "system", "content": "You are a helpful assistant that extracts a one‑sentence summary, a list of relevant tags, and a numeric embedding vector for the given content. Return a JSON object with keys: summary (string), tags (array of strings), embedding (array of numbers)."},
        {"role": "user", "content": content},
    ]
    return await _call_inference(messages, max_tokens=512)

async def get_semantic_embedding(text: str) -> Dict[str, Any]:
    messages = [
        {"role": "system", "content": "Return a JSON object containing a single key \"embedding\" whose value is an array of floating‑point numbers representing the semantic embedding of the provided text."},
        {"role": "user", "content": text},
    ]
    return await _call_inference(messages, max_tokens=512)
