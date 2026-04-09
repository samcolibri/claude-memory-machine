"""
Level 3: Pattern Detector
- Analyzes recent memories for recurring themes
- Detects repeated topics, ongoing threads, recurring blockers
- Uses Claude API for deep pattern analysis when available
- Falls back to keyword frequency analysis
- Writes pattern insights to memorymesh
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from collections import Counter, defaultdict

import config
import mem0_client
import memorymesh_client


def extract_keywords(text):
    """Extract meaningful keywords from memory text."""
    stop_words = {
        "the", "a", "an", "is", "was", "are", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above", "below",
        "between", "out", "off", "over", "under", "again", "further", "then",
        "once", "here", "there", "when", "where", "why", "how", "all", "each",
        "every", "both", "few", "more", "most", "other", "some", "such", "no",
        "not", "only", "own", "same", "so", "than", "too", "very", "just",
        "that", "this", "these", "those", "and", "but", "or", "if", "while",
        "user", "file", "command", "ran", "executed", "wrote", "edited", "bash",
    }
    words = text.lower().split()
    # Clean words
    words = [w.strip(".,;:!?()[]{}\"'`") for w in words]
    # Filter
    words = [w for w in words if len(w) > 2 and w not in stop_words and not w.startswith("/")]
    return words


def detect_topic_clusters(memories):
    """Group memories by topic using keyword co-occurrence."""
    # Build keyword frequency
    keyword_counter = Counter()
    keyword_to_memories = defaultdict(list)

    for m in memories:
        text = m.get("memory", "")
        keywords = extract_keywords(text)
        keyword_counter.update(set(keywords))  # Count each keyword once per memory
        for kw in set(keywords):
            keyword_to_memories[kw].append(m)

    # Find recurring topics (appear in N+ memories)
    recurring = {
        kw: count for kw, count in keyword_counter.items()
        if count >= config.PATTERN_MIN_OCCURRENCES
    }

    return recurring, keyword_to_memories


def detect_temporal_patterns(memories):
    """Detect patterns in when work happens."""
    day_counts = Counter()
    hour_counts = Counter()

    for m in memories:
        created = m.get("created_at", "")
        if created:
            try:
                dt = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
                day_counts[dt.strftime("%A")] += 1
                hour_counts[dt.hour] += 1
            except (ValueError, TypeError):
                pass

    return day_counts, hour_counts


def detect_project_threads(memories):
    """Detect ongoing project threads across sessions."""
    project_keywords = {
        "colibri-qa": ["colibri", "qa-platform", "playwright", "jira"],
        "workday": ["workday", "raas", "prism"],
        "netsuite": ["netsuite", "suiteql", "tba"],
        "aonxi": ["aonxi", "outreach", "aria"],
        "nova-gtm": ["nova", "gtm", "simplenursing"],
        "agi-research": ["agi", "frontier", "paper", "neurips"],
        "memory-system": ["memorymesh", "mem0", "memory", "claude.md"],
        "llm-council": ["llm-council", "council", "openrouter"],
    }

    project_activity = defaultdict(lambda: {"count": 0, "latest": "", "memories": []})

    for m in memories:
        text = m.get("memory", "").lower()
        created = str(m.get("created_at", ""))[:10]
        for project, keywords in project_keywords.items():
            if any(kw in text for kw in keywords):
                project_activity[project]["count"] += 1
                if created > project_activity[project]["latest"]:
                    project_activity[project]["latest"] = created
                project_activity[project]["memories"].append(m)

    return dict(project_activity)


def detect_blockers(memories):
    """Detect recurring blockers or pain points."""
    blocker_keywords = [
        "blocked", "blocker", "failed", "error", "bug", "broken",
        "missing", "pending", "waiting", "stuck", "issue", "problem",
        "403", "401", "timeout", "crash",
    ]
    blockers = []
    for m in memories:
        text = m.get("memory", "").lower()
        if any(kw in text for kw in blocker_keywords):
            blockers.append(m)
    return blockers


def try_claude_analysis(memories, patterns):
    """Use Claude API for deep pattern analysis if available."""
    if not config.ANTHROPIC_API_KEY:
        return None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        # Prepare memory summary for analysis
        memory_texts = [m.get("memory", "")[:200] for m in memories[:50]]
        memory_block = "\n".join(f"- {t}" for t in memory_texts)

        response = client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""Analyze these recent memories from a developer's AI assistant and identify:
1. Top 3 active projects and their current status
2. Any recurring blockers or pain points
3. Patterns in work style or focus areas
4. Predictions: what will they likely work on next?
5. One actionable suggestion based on the patterns

Recent memories:
{memory_block}

Recurring keywords: {', '.join(list(patterns.keys())[:20])}

Be concise. Each point should be 1-2 sentences max."""
            }],
        )
        return response.content[0].text
    except Exception as e:
        print(f"  Claude analysis failed: {e}")
        return None


def run():
    """Run full pattern detection pipeline."""
    print("=" * 60)
    print("PATTERN DETECTOR — Level 3 Agent")
    print(f"Run time: {datetime.now().isoformat()}")
    print("=" * 60)

    # Fetch recent memories from both systems
    print("\n[1/5] Fetching memories...")
    mem0_memories = mem0_client.get_all_memories(max_pages=5)  # Last ~500
    mesh_memories = memorymesh_client.get_all_memories()
    all_memories = mem0_memories + [{"memory": m["content"], **m} for m in mesh_memories]
    print(f"  Loaded {len(mem0_memories)} from Mem0 + {len(mesh_memories)} from memorymesh")

    # Detect topic clusters
    print("\n[2/5] Detecting topic clusters...")
    recurring, kw_to_mem = detect_topic_clusters(all_memories)
    top_topics = sorted(recurring.items(), key=lambda x: -x[1])[:15]
    print(f"  Top recurring topics:")
    for topic, count in top_topics:
        print(f"    {topic}: {count} occurrences")

    # Detect project threads
    print("\n[3/5] Detecting project threads...")
    projects = detect_project_threads(all_memories)
    print(f"  Active projects:")
    for proj, data in sorted(projects.items(), key=lambda x: -x[1]["count"]):
        print(f"    {proj}: {data['count']} memories, latest {data['latest']}")

    # Detect blockers
    print("\n[4/5] Detecting blockers...")
    blockers = detect_blockers(all_memories)
    print(f"  Found {len(blockers)} blocker-related memories")
    for b in blockers[:5]:
        print(f"    - {b.get('memory', '')[:100]}...")

    # Claude deep analysis
    print("\n[5/5] Deep pattern analysis...")
    claude_insights = try_claude_analysis(all_memories, recurring)
    if claude_insights:
        print(f"  Claude analysis:\n")
        for line in claude_insights.strip().split("\n"):
            print(f"    {line}")
    else:
        print("  (Claude API not available — using keyword analysis only)")

    # Build pattern report
    report_lines = [
        f"PATTERN REPORT — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "TOP TOPICS: " + ", ".join(f"{t[0]}({t[1]})" for t in top_topics[:10]),
        "",
        "ACTIVE PROJECTS:",
    ]
    for proj, data in sorted(projects.items(), key=lambda x: -x[1]["count"]):
        report_lines.append(f"  {proj}: {data['count']} memories, latest {data['latest']}")
    report_lines.append("")
    report_lines.append(f"BLOCKERS: {len(blockers)} detected")
    for b in blockers[:3]:
        report_lines.append(f"  - {b.get('memory', '')[:100]}")

    if claude_insights:
        report_lines.append("")
        report_lines.append("CLAUDE ANALYSIS:")
        report_lines.append(claude_insights)

    report = "\n".join(report_lines)

    # Save pattern report to memorymesh
    memorymesh_client.store_memory(
        content=report,
        importance=0.8,
        tags=["pattern-report", "auto-generated", datetime.now().strftime("%Y-%m-%d")],
        source="pattern-detector",
    )
    print(f"\n  Pattern report saved to memorymesh")

    # Save to log file
    log_file = config.LOG_DIR / f"patterns_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(log_file, "w") as f:
        f.write(report)
    print(f"  Log saved to {log_file}")

    print("\n" + "=" * 60)
    print("PATTERN DETECTION COMPLETE")
    print("=" * 60)

    return report


if __name__ == "__main__":
    run()
