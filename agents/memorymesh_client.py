"""
memorymesh Local Client
Direct SQLite access to the memorymesh database for batch operations.
Returns empty results gracefully if memorymesh is not installed.
"""

import sqlite3
import json
from datetime import datetime
from config import MEMORYMESH_DB, MEMORYMESH_AVAILABLE


def get_connection():
    """Get SQLite connection to memorymesh DB."""
    if not MEMORYMESH_AVAILABLE:
        return None
    return sqlite3.connect(str(MEMORYMESH_DB))


def get_all_memories():
    """Fetch all memories from memorymesh."""
    conn = get_connection()
    if not conn:
        return []
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            "SELECT * FROM memories ORDER BY created_at DESC"
        )
    except sqlite3.OperationalError:
        conn.close()
        return []
    memories = [dict(row) for row in cursor.fetchall()]
    conn.close()
    for m in memories:
        if m.get("tags") and isinstance(m["tags"], str):
            try:
                m["tags"] = json.loads(m["tags"])
            except (json.JSONDecodeError, TypeError):
                m["tags"] = []
    return memories


def store_memory(content, importance=0.5, tags=None, source="agent"):
    """Store a new memory in memorymesh."""
    conn = get_connection()
    if not conn:
        return None
    now = datetime.utcnow().isoformat()
    tags_json = json.dumps(tags or [])
    conn.execute(
        "INSERT INTO memories (namespace, content, importance, tags, source, created_at, accessed_at, access_count) "
        "VALUES ('default', ?, ?, ?, ?, ?, ?, 0)",
        (content, importance, tags_json, source, now, now),
    )
    conn.commit()
    # Get the ID of the inserted row
    cursor = conn.execute("SELECT last_insert_rowid()")
    row_id = cursor.fetchone()[0]
    conn.close()
    return row_id


def update_importance(memory_id, new_importance):
    """Update importance score of a memory."""
    conn = get_connection()
    if not conn:
        return
    now = datetime.utcnow().isoformat()
    conn.execute(
        "UPDATE memories SET importance = ?, accessed_at = ? WHERE id = ?",
        (new_importance, now, memory_id),
    )
    conn.commit()
    conn.close()


def delete_memory(memory_id):
    """Delete a memory by ID."""
    conn = get_connection()
    if not conn:
        return
    conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    conn.commit()
    conn.close()


def search(query, limit=10):
    """FTS5 search across memories."""
    conn = get_connection()
    if not conn:
        return []
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            "SELECT id, content, importance, tags, source, created_at "
            "FROM memories WHERE content MATCH ? ORDER BY rank LIMIT ?",
            (query, limit),
        )
        results = [dict(row) for row in cursor.fetchall()]
    except sqlite3.OperationalError:
        # Fallback to LIKE search if FTS not available on this table
        cursor = conn.execute(
            "SELECT id, content, importance, tags, source, created_at "
            "FROM memories WHERE content LIKE ? ORDER BY importance DESC LIMIT ?",
            (f"%{query}%", limit),
        )
        results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_stats():
    """Get memory store statistics."""
    conn = get_connection()
    if not conn:
        return {"total": 0, "by_source": {}, "avg_importance": 0}
    cursor = conn.execute("SELECT COUNT(*) FROM memories")
    total = cursor.fetchone()[0]
    cursor = conn.execute("SELECT source, COUNT(*) FROM memories GROUP BY source")
    by_source = dict(cursor.fetchall())
    cursor = conn.execute("SELECT AVG(importance) FROM memories")
    avg_importance = cursor.fetchone()[0] or 0
    conn.close()
    return {"total": total, "by_source": by_source, "avg_importance": round(avg_importance, 2)}
