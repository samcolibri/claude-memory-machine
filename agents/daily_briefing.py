"""
Level 3: Daily Briefing Generator
- Runs every morning before work
- Generates a contextual briefing from all memory sources
- Writes to episodic_last_session.md so Claude greets with it
- Proactive: predicts what you'll work on based on patterns
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
from pathlib import Path

import config
import mem0_client
import memorymesh_client


def get_recent_activity():
    """Get yesterday's and recent activity from both memory sources."""
    # Recent Mem0 memories
    recent_mem0 = mem0_client.search("recent work activity projects", top_k=15)

    # All memorymesh memories (sorted by recency in the client)
    mesh = memorymesh_client.get_all_memories()

    return recent_mem0, mesh


def build_briefing_with_claude(mem0_recent, mesh_memories):
    """Generate a contextual morning briefing using Claude."""
    if not config.ANTHROPIC_API_KEY:
        return None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        mem0_text = "\n".join(
            f"- [{m.get('created_at', '')[:10]}] {m.get('memory', '')[:150]}"
            for m in mem0_recent[:15]
        )
        mesh_text = "\n".join(
            f"- [imp:{m.get('importance', 0.5):.1f}] {m.get('content', '')[:150]}"
            for m in mesh_memories[:15]
        )

        today = datetime.now().strftime("%A, %B %d, %Y")

        response = client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=600,
            messages=[{
                "role": "user",
                "content": f"""Generate a morning briefing for a developer based on their memory context.
Today is {today}.

RECENT ACTIVITY (Mem0 cloud):
{mem0_text}

STRUCTURED CONTEXT (memorymesh):
{mesh_text}

Write a concise morning briefing with:
1. **Status**: 1-2 sentence summary of where things stand
2. **Priority**: The most important thing to focus on today (based on patterns)
3. **Open threads**: 2-3 items that need attention
4. **Watch out**: Any blockers or risks detected

Keep it under 200 words. Be specific, not generic. This will be read by an AI assistant to greet the user."""
            }],
        )
        return response.content[0].text
    except Exception as e:
        print(f"  Claude briefing generation failed: {e}")
        return None


def build_briefing_heuristic(mem0_recent, mesh_memories):
    """Fallback briefing without Claude API."""
    today = datetime.now().strftime("%A, %B %d, %Y")
    lines = [
        f"Daily Briefing — {today}",
        "",
        "RECENT ACTIVITY:",
    ]
    for m in mem0_recent[:5]:
        lines.append(f"  - {m.get('memory', '')[:120]}")

    lines.extend(["", "KEY CONTEXT:"])
    for m in mesh_memories[:5]:
        imp = m.get("importance", 0.5)
        if imp >= 0.7:
            lines.append(f"  - [!] {m.get('content', '')[:120]}")

    return "\n".join(lines)


def run():
    """Generate the daily briefing."""
    print("=" * 60)
    print("DAILY BRIEFING — Level 3 Agent")
    print(f"Run time: {datetime.now().isoformat()}")
    print("=" * 60)

    # Gather recent activity
    print("\n[1/3] Gathering recent activity...")
    mem0_recent, mesh_memories = get_recent_activity()
    print(f"  Mem0 recent: {len(mem0_recent)} memories")
    print(f"  memorymesh: {len(mesh_memories)} memories")

    # Generate briefing
    print("\n[2/3] Generating briefing...")
    briefing = build_briefing_with_claude(mem0_recent, mesh_memories)
    if not briefing:
        briefing = build_briefing_heuristic(mem0_recent, mesh_memories)
        print("  Generated heuristic briefing (no Claude API)")
    else:
        print("  Generated Claude-powered briefing")

    print(f"\n--- BRIEFING ---\n{briefing}\n--- END ---\n")

    # Write to episodic_last_session.md (this is what Claude reads on startup)
    print("[3/3] Writing to session bridge...")
    session_file = config.MEMORY_DIR / "episodic_last_session.md"

    # Preserve existing content, add briefing on top
    existing = ""
    if session_file.exists():
        existing = session_file.read_text()
        # Extract the part after the frontmatter
        if "---" in existing:
            parts = existing.split("---", 2)
            if len(parts) >= 3:
                existing_content = parts[2].strip()
            else:
                existing_content = existing
        else:
            existing_content = existing

    session_file.write_text(f"""---
name: Last Session Summary
description: Most recent session + daily briefing — loaded at startup
type: project
---

## Daily Briefing — {datetime.now().strftime('%Y-%m-%d')}

{briefing}

---

{existing_content if 'existing_content' in dir() else ''}
""")
    print(f"  Written to {session_file}")

    # Also save to memorymesh
    memorymesh_client.store_memory(
        content=f"Daily Briefing {datetime.now().strftime('%Y-%m-%d')}: {briefing[:500]}",
        importance=0.6,
        tags=["daily-briefing", "auto-generated", datetime.now().strftime("%Y-%m-%d")],
        source="daily-briefing",
    )

    # Log
    log_file = config.LOG_DIR / f"briefing_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(log_file, "w") as f:
        f.write(briefing)

    print("\n" + "=" * 60)
    print("DAILY BRIEFING COMPLETE")
    print("=" * 60)

    return briefing


if __name__ == "__main__":
    run()
