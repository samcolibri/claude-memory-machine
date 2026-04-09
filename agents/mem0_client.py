"""
Mem0 Cloud API Client
Wraps the REST API for memory operations.
"""

import json
import urllib.request
from config import MEM0_API_KEY, MEM0_USER_ID, MEM0_BASE_URL


def _request(method, path, data=None):
    """Make an authenticated request to Mem0 API."""
    url = f"{MEM0_BASE_URL}{path}"
    headers = {
        "Authorization": f"Token {MEM0_API_KEY}",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  Mem0 API error: {e}")
        return None


def search(query, top_k=10):
    """Semantic search across Mem0 memories."""
    return _request("POST", "/memories/search/", {
        "query": query,
        "user_id": MEM0_USER_ID,
        "top_k": top_k,
    }) or []


def get_all(page=1, page_size=100):
    """Get paginated list of all memories."""
    return _request("GET", f"/memories/?user_id={MEM0_USER_ID}&page={page}&page_size={page_size}")


def get_total_count():
    """Get total memory count."""
    result = get_all(page=1, page_size=1)
    if isinstance(result, dict):
        return result.get("count", 0)
    return len(result) if result else 0


def delete(memory_id):
    """Delete a memory by ID."""
    return _request("DELETE", f"/memories/{memory_id}/")


def get_all_memories(max_pages=20):
    """Fetch all memories (paginated). Returns flat list."""
    all_memories = []
    page = 1
    while page <= max_pages:
        result = get_all(page=page, page_size=100)
        if not result:
            break
        if isinstance(result, dict):
            items = result.get("results", [])
            all_memories.extend(items)
            if not result.get("next"):
                break
        elif isinstance(result, list):
            all_memories.extend(result)
            if len(result) < 100:
                break
        else:
            break
        page += 1
    return all_memories
