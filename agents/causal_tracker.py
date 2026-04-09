"""
Level 4: Causal Tracker
- Tracks decision → outcome chains across sessions
- Builds a causal graph: what decisions led to what results
- Detects what approaches work and what doesn't for this user
- Enables "what worked last time we tried X" queries
- Self-evolving: adjusts memory importance based on outcome data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
from collections import defaultdict

import config
import mem0_client
import memorymesh_client


# Decision and outcome markers
DECISION_MARKERS = [
    "decided", "decision", "chose", "selected", "went with",
    "approved", "agreed", "plan is", "approach:", "strategy:",
    "will use", "switching to", "migrating to",
]

OUTCOME_MARKERS = {
    "positive": [
        "live", "shipped", "deployed", "passing", "working", "success",
        "merged", "approved", "completed", "fixed", "resolved",
        "15/15", "all tests", "great work", "good job",
    ],
    "negative": [
        "failed", "broken", "blocked", "error", "bug", "crash",
        "rejected", "reverted", "rollback", "timeout", "403", "401",
        "missing", "stuck", "incident",
    ],
    "pending": [
        "pending", "waiting", "in progress", "todo", "wip",
        "needs", "requires", "blocked on",
    ],
}


def extract_decisions(memories):
    """Find memories that represent decisions."""
    decisions = []
    for m in memories:
        text = m.get("memory", m.get("content", "")).lower()
        if any(marker in text for marker in DECISION_MARKERS):
            decisions.append({
                "memory": m,
                "text": m.get("memory", m.get("content", "")),
                "date": str(m.get("created_at", ""))[:10],
                "type": "decision",
            })
    return decisions


def extract_outcomes(memories):
    """Classify memories as positive, negative, or pending outcomes."""
    outcomes = []
    for m in memories:
        text = m.get("memory", m.get("content", "")).lower()
        for outcome_type, markers in OUTCOME_MARKERS.items():
            if any(marker in text for marker in markers):
                outcomes.append({
                    "memory": m,
                    "text": m.get("memory", m.get("content", "")),
                    "date": str(m.get("created_at", ""))[:10],
                    "type": outcome_type,
                })
                break
    return outcomes


def link_decisions_to_outcomes(decisions, outcomes):
    """Link decisions to their outcomes using keyword overlap."""
    links = []
    for d in decisions:
        d_words = set(d["text"].lower().split())
        best_match = None
        best_overlap = 0

        for o in outcomes:
            o_words = set(o["text"].lower().split())
            overlap = len(d_words & o_words)
            # Must share meaningful keywords and outcome must be after decision
            if overlap > best_overlap and overlap >= 3:
                if o["date"] >= d["date"]:
                    best_match = o
                    best_overlap = overlap

        if best_match:
            links.append({
                "decision": d["text"][:150],
                "decision_date": d["date"],
                "outcome": best_match["text"][:150],
                "outcome_date": best_match["date"],
                "outcome_type": best_match["type"],
                "confidence": min(best_overlap / 10, 1.0),
            })

    return links


def build_causal_graph(links):
    """Build a summary causal graph from decision-outcome links."""
    project_outcomes = defaultdict(lambda: {"positive": 0, "negative": 0, "pending": 0})

    # Detect project from link content
    project_keywords = {
        "colibri-qa": ["colibri", "qa-platform", "playwright"],
        "workday": ["workday", "raas", "prism"],
        "netsuite": ["netsuite", "suiteql"],
        "aonxi": ["aonxi", "outreach"],
        "memory": ["memorymesh", "mem0", "memory"],
    }

    for link in links:
        text = (link["decision"] + " " + link["outcome"]).lower()
        matched_project = "other"
        for proj, keywords in project_keywords.items():
            if any(kw in text for kw in keywords):
                matched_project = proj
                break
        project_outcomes[matched_project][link["outcome_type"]] += 1

    return dict(project_outcomes)


def try_claude_causal_analysis(links):
    """Use Claude for deep causal analysis."""
    if not config.ANTHROPIC_API_KEY or not links:
        return None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        link_text = "\n".join(
            f"- Decision [{l['decision_date']}]: {l['decision']}\n"
            f"  Outcome [{l['outcome_date']}] ({l['outcome_type']}): {l['outcome']}"
            for l in links[:20]
        )

        response = client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=800,
            messages=[{
                "role": "user",
                "content": f"""Analyze these decision→outcome chains from a developer's work history:

{link_text}

Identify:
1. What types of decisions consistently lead to positive outcomes?
2. What patterns appear before negative outcomes?
3. Any recurring decision anti-patterns to avoid?
4. One specific recommendation based on the causal patterns.

Be concise — 1-2 sentences per point."""
            }],
        )
        return response.content[0].text
    except Exception as e:
        print(f"  Claude causal analysis failed: {e}")
        return None


def adjust_importance_scores(links):
    """Self-evolving: adjust memorymesh importance based on outcomes."""
    adjustments = 0
    mesh_memories = memorymesh_client.get_all_memories()

    for link in links:
        # Find matching memorymesh entries
        for m in mesh_memories:
            content = m.get("content", "").lower()
            decision_fragment = link["decision"][:50].lower()
            if decision_fragment in content:
                current = m.get("importance", 0.5)
                if link["outcome_type"] == "positive":
                    new = min(current + 0.1, 1.0)
                elif link["outcome_type"] == "negative":
                    new = min(current + 0.05, 1.0)  # Still valuable to remember failures
                else:
                    continue

                if abs(new - current) > 0.01:
                    memorymesh_client.update_importance(m["id"], new)
                    adjustments += 1

    return adjustments


def run():
    """Run the causal tracker."""
    print("=" * 60)
    print("CAUSAL TRACKER — Level 4 Agent")
    print(f"Run time: {datetime.now().isoformat()}")
    print("=" * 60)

    # Gather memories
    print("\n[1/5] Gathering memories...")
    mem0_memories = mem0_client.get_all_memories(max_pages=10)
    mesh_memories = memorymesh_client.get_all_memories()
    all_memories = mem0_memories + [{"memory": m["content"], **m} for m in mesh_memories]
    print(f"  Total: {len(all_memories)} memories")

    # Extract decisions and outcomes
    print("\n[2/5] Extracting decisions...")
    decisions = extract_decisions(all_memories)
    print(f"  Found {len(decisions)} decisions")

    print("\n[3/5] Extracting outcomes...")
    outcomes = extract_outcomes(all_memories)
    positive = len([o for o in outcomes if o["type"] == "positive"])
    negative = len([o for o in outcomes if o["type"] == "negative"])
    pending = len([o for o in outcomes if o["type"] == "pending"])
    print(f"  Found {len(outcomes)} outcomes: {positive} positive, {negative} negative, {pending} pending")

    # Link decisions to outcomes
    print("\n[4/5] Building causal links...")
    links = link_decisions_to_outcomes(decisions, outcomes)
    print(f"  Linked {len(links)} decision→outcome chains")
    for link in links[:5]:
        emoji = {"positive": "+", "negative": "-", "pending": "~"}[link["outcome_type"]]
        print(f"    [{emoji}] {link['decision'][:60]}... → {link['outcome'][:60]}...")

    # Build causal graph
    graph = build_causal_graph(links)
    print(f"\n  Project outcome summary:")
    for proj, counts in graph.items():
        print(f"    {proj}: +{counts['positive']} -{counts['negative']} ~{counts['pending']}")

    # Claude deep analysis
    print("\n[5/5] Deep causal analysis...")
    claude_analysis = try_claude_causal_analysis(links)
    if claude_analysis:
        print(f"\n  {claude_analysis}")

    # Self-evolving: adjust importance scores
    adjustments = adjust_importance_scores(links)
    print(f"\n  Self-evolution: adjusted {adjustments} memorymesh importance scores")

    # Save causal report to memorymesh
    report_lines = [
        f"CAUSAL REPORT — {datetime.now().strftime('%Y-%m-%d')}",
        f"Decisions tracked: {len(decisions)}",
        f"Outcomes: +{positive} -{negative} ~{pending}",
        f"Causal links: {len(links)}",
        "",
        "PROJECT OUTCOMES:",
    ]
    for proj, counts in graph.items():
        report_lines.append(f"  {proj}: +{counts['positive']} -{counts['negative']} ~{counts['pending']}")
    if claude_analysis:
        report_lines.extend(["", "ANALYSIS:", claude_analysis])

    # Remove old causal report
    existing = memorymesh_client.search("causal report")
    for m in existing:
        if "CAUSAL REPORT" in m.get("content", ""):
            memorymesh_client.delete_memory(m["id"])

    memorymesh_client.store_memory(
        content="\n".join(report_lines),
        importance=0.85,
        tags=["causal-report", "self-evolving", "auto-generated"],
        source="causal-tracker",
    )

    # Log
    log_file = config.LOG_DIR / f"causal_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(log_file, "w") as f:
        f.write("\n".join(report_lines))

    print("\n" + "=" * 60)
    print("CAUSAL TRACKING COMPLETE")
    print("=" * 60)

    return links


if __name__ == "__main__":
    run()
