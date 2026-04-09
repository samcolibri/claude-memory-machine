"""
Level 4: Digital Twin
- Builds a comprehensive user model from ALL memory sources
- Uses Claude API to synthesize a "mental model" of the user
- Tracks working patterns, decision styles, expertise areas
- Updates automatically — the model evolves as the user does
- Outputs to memorymesh (high importance) and local markdown
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
from collections import Counter, defaultdict
from pathlib import Path

import config
import mem0_client
import memorymesh_client


def analyze_expertise(memories):
    """Detect expertise areas from memory content."""
    tech_keywords = {
        "languages": ["python", "typescript", "javascript", "sql", "bash", "go", "rust"],
        "frameworks": ["playwright", "react", "fastapi", "express", "nextjs", "vue"],
        "databases": ["postgresql", "sqlite", "neo4j", "redis", "mongodb", "netsuite"],
        "cloud": ["aws", "gcp", "azure", "docker", "kubernetes", "terraform"],
        "ai_ml": ["claude", "gpt", "llm", "embedding", "vector", "anthropic", "openai"],
        "tools": ["git", "github", "jira", "confluence", "qmetry", "figma", "slack"],
        "domains": ["qa", "testing", "gtm", "outreach", "sales", "marketing", "compliance"],
    }

    expertise = defaultdict(Counter)
    for m in memories:
        text = m.get("memory", m.get("content", "")).lower()
        for category, keywords in tech_keywords.items():
            for kw in keywords:
                if kw in text:
                    expertise[category][kw] += 1

    return {
        cat: dict(counter.most_common(5))
        for cat, counter in expertise.items()
        if counter
    }


def analyze_work_patterns(memories):
    """Analyze when and how the user works."""
    hours = Counter()
    days = Counter()
    session_lengths = []

    for m in memories:
        created = m.get("created_at", "")
        if created:
            try:
                dt = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
                hours[dt.hour] += 1
                days[dt.strftime("%A")] += 1
            except (ValueError, TypeError):
                pass

    peak_hours = sorted(hours.items(), key=lambda x: -x[1])[:3]
    peak_days = sorted(days.items(), key=lambda x: -x[1])[:3]

    return {
        "peak_hours": [f"{h}:00" for h, _ in peak_hours],
        "peak_days": [d for d, _ in peak_days],
        "total_memories": len(memories),
    }


def analyze_decision_style(memories):
    """Infer decision-making patterns."""
    patterns = {
        "moves_fast": 0,
        "thorough_researcher": 0,
        "collaborative": 0,
        "autonomous": 0,
        "detail_oriented": 0,
    }

    for m in memories:
        text = m.get("memory", m.get("content", "")).lower()
        if any(w in text for w in ["shipped", "pushed", "deployed", "live", "done"]):
            patterns["moves_fast"] += 1
        if any(w in text for w in ["research", "paper", "benchmark", "compare", "analyze"]):
            patterns["thorough_researcher"] += 1
        if any(w in text for w in ["smita", "prabhu", "aashima", "team", "demo", "presented"]):
            patterns["collaborative"] += 1
        if any(w in text for w in ["built", "created", "automated", "self-", "autonomous"]):
            patterns["autonomous"] += 1
        if any(w in text for w in ["test", "verify", "check", "audit", "15/15", "37 tests"]):
            patterns["detail_oriented"] += 1

    # Normalize
    total = max(sum(patterns.values()), 1)
    return {k: round(v / total, 2) for k, v in patterns.items()}


def build_twin_with_claude(memories, expertise, work_patterns, decision_style):
    """Use Claude to synthesize the digital twin."""
    if not config.ANTHROPIC_API_KEY:
        return None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        # Sample memories for analysis
        sample = [m.get("memory", m.get("content", ""))[:200] for m in memories[:60]]
        memory_block = "\n".join(f"- {t}" for t in sample)

        response = client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": f"""Build a comprehensive "digital twin" profile of this user based on their AI assistant memories.

MEMORIES (sample of {len(memories)} total):
{memory_block}

DETECTED EXPERTISE:
{expertise}

WORK PATTERNS:
{work_patterns}

DECISION STYLE:
{decision_style}

Create a structured profile with:
1. **Identity**: Who they are (role, companies, ambitions)
2. **Expertise Map**: What they're strong at, what they're learning
3. **Work Style**: How they approach problems, pace, preferences
4. **Active Threads**: What they're currently focused on
5. **Growth Trajectory**: Where they're heading based on patterns
6. **How to Help Them Best**: Specific guidance for an AI assistant

Be specific and evidence-based — cite memory patterns, not assumptions. Keep each section to 2-3 sentences."""
            }],
        )
        return response.content[0].text
    except Exception as e:
        print(f"  Claude analysis failed: {e}")
        return None


def build_twin_heuristic(expertise, work_patterns, decision_style):
    """Build digital twin from heuristics when Claude API unavailable."""
    lines = [
        "DIGITAL TWIN — Heuristic Analysis",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "EXPERTISE:",
    ]
    for cat, skills in expertise.items():
        top = ", ".join(f"{k}({v})" for k, v in list(skills.items())[:3])
        lines.append(f"  {cat}: {top}")

    lines.extend([
        "",
        "WORK PATTERNS:",
        f"  Peak hours: {', '.join(work_patterns['peak_hours'])}",
        f"  Peak days: {', '.join(work_patterns['peak_days'])}",
        f"  Total memory footprint: {work_patterns['total_memories']} memories",
        "",
        "DECISION STYLE:",
    ])
    for trait, score in sorted(decision_style.items(), key=lambda x: -x[1]):
        bar = "#" * int(score * 20)
        lines.append(f"  {trait}: {bar} ({score:.0%})")

    return "\n".join(lines)


def run():
    """Build the digital twin."""
    print("=" * 60)
    print("DIGITAL TWIN — Level 4 Agent")
    print(f"Run time: {datetime.now().isoformat()}")
    print("=" * 60)

    # Gather all memories
    print("\n[1/4] Gathering memories from all sources...")
    mem0_memories = mem0_client.get_all_memories(max_pages=15)
    mesh_memories = memorymesh_client.get_all_memories()
    all_memories = mem0_memories + [{"memory": m["content"], **m} for m in mesh_memories]
    print(f"  Total: {len(all_memories)} memories ({len(mem0_memories)} Mem0 + {len(mesh_memories)} memorymesh)")

    # Analyze
    print("\n[2/4] Analyzing expertise...")
    expertise = analyze_expertise(all_memories)
    for cat, skills in expertise.items():
        top = ", ".join(f"{k}({v})" for k, v in list(skills.items())[:3])
        print(f"  {cat}: {top}")

    print("\n[3/4] Analyzing work patterns & decision style...")
    work_patterns = analyze_work_patterns(all_memories)
    decision_style = analyze_decision_style(all_memories)
    print(f"  Peak hours: {', '.join(work_patterns['peak_hours'])}")
    print(f"  Peak days: {', '.join(work_patterns['peak_days'])}")
    for trait, score in sorted(decision_style.items(), key=lambda x: -x[1]):
        print(f"  {trait}: {score:.0%}")

    # Build the twin
    print("\n[4/4] Building digital twin...")
    claude_twin = build_twin_with_claude(all_memories, expertise, work_patterns, decision_style)
    if claude_twin:
        twin_content = claude_twin
        print("  Built with Claude analysis")
    else:
        twin_content = build_twin_heuristic(expertise, work_patterns, decision_style)
        print("  Built with heuristic analysis (no Claude API)")

    print(f"\n--- DIGITAL TWIN ---\n")
    print(twin_content)
    print(f"\n--- END TWIN ---\n")

    # Save to memorymesh (high importance)
    # First, remove old twin if exists
    existing = memorymesh_client.search("digital twin")
    for m in existing:
        if "DIGITAL TWIN" in m.get("content", ""):
            memorymesh_client.delete_memory(m["id"])

    memorymesh_client.store_memory(
        content=f"DIGITAL TWIN — Updated {datetime.now().strftime('%Y-%m-%d')}\n\n{twin_content}",
        importance=1.0,
        tags=["digital-twin", "user-model", "auto-generated"],
        source="digital-twin-agent",
    )
    print("  Saved to memorymesh (importance: 1.0)")

    # Also save to local markdown
    twin_file = config.MEMORY_DIR / "digital_twin.md"
    with open(twin_file, "w") as f:
        f.write(f"""---
name: Digital Twin
description: AI-generated comprehensive user model — auto-updated by Level 4 agent
type: user
---

{twin_content}

---
*Auto-generated by Digital Twin Agent on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*Sources: {len(mem0_memories)} Mem0 + {len(mesh_memories)} memorymesh memories*
""")
    print(f"  Saved to {twin_file}")

    # Update MEMORY.md index
    memory_md = config.MEMORY_DIR / "MEMORY.md"
    content = memory_md.read_text()
    if "digital_twin.md" not in content:
        content += "\n- [Digital Twin](digital_twin.md) — AI-generated user model, auto-updated by Level 4 agent\n"
        memory_md.write_text(content)
        print("  Updated MEMORY.md index")

    # Save to log
    log_file = config.LOG_DIR / f"twin_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(log_file, "w") as f:
        f.write(twin_content)

    print("\n" + "=" * 60)
    print("DIGITAL TWIN BUILD COMPLETE")
    print("=" * 60)

    return twin_content


if __name__ == "__main__":
    run()
