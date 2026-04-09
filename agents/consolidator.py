"""
Level 3: Memory Consolidator
- Pulls all Mem0 memories
- Identifies and removes noise (git status, ls, trivial commands)
- Deduplicates similar memories using fuzzy matching
- Promotes high-value memories to memorymesh (structured + tagged)
- Generates consolidation report
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
from difflib import SequenceMatcher
from collections import defaultdict

import config
import mem0_client
import memorymesh_client


def is_noise(memory_text):
    """Check if a memory is noise (trivial tool output)."""
    text = memory_text.lower()
    # Too short
    if len(text) < config.MIN_MEMORY_LENGTH:
        return True
    # Known noise patterns
    for keyword in config.NOISE_KEYWORDS:
        if keyword.lower() in text:
            return True
    # Pure command output with no insight
    noise_starts = [
        "user executed a bash command",
        "user ran a command",
        "user wrote the file",
        "user edited the file",
        "user read the file",
    ]
    for start in noise_starts:
        if text.startswith(start) and len(text) < 120:
            return True
    return False


def similarity(a, b):
    """Fuzzy similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_duplicates(memories):
    """Find groups of duplicate/near-duplicate memories."""
    groups = []
    used = set()
    for i, m1 in enumerate(memories):
        if i in used:
            continue
        group = [m1]
        for j, m2 in enumerate(memories[i + 1:], i + 1):
            if j in used:
                continue
            if similarity(m1["memory"], m2["memory"]) > config.DEDUP_SIMILARITY_THRESHOLD:
                group.append(m2)
                used.add(j)
        if len(group) > 1:
            groups.append(group)
            used.add(i)
    return groups


def categorize_memory(memory_text):
    """Simple keyword-based categorization."""
    text = memory_text.lower()
    categories = {
        "colibri-qa": ["colibri", "qa-platform", "playwright", "jira", "qmetry"],
        "workday": ["workday", "raas", "prism", "wd108"],
        "netsuite": ["netsuite", "suiteql", "restlet", "3520739"],
        "aonxi": ["aonxi", "outreach", "aria"],
        "nova-gtm": ["nova", "gtm", "simplenursing"],
        "memory-system": ["memorymesh", "mem0", "memory", "claude.md"],
        "agi-research": ["agi", "frontier", "neurips", "paper", "research"],
        "infrastructure": ["github", "git", "deploy", "aws", "docker", "cron"],
        "personal": ["sam", "anmol", "cto", "meta", "apple"],
    }
    matched = []
    for cat, keywords in categories.items():
        if any(kw in text for kw in keywords):
            matched.append(cat)
    return matched or ["uncategorized"]


def assess_importance(memory_text, categories):
    """Heuristic importance scoring."""
    score = 0.5
    text = memory_text.lower()
    # Boost for decisions and outcomes
    if any(w in text for w in ["decided", "decision", "approved", "live", "shipped", "merged"]):
        score += 0.2
    # Boost for credentials and architecture
    if any(w in text for w in ["password", "api_key", "credential", "auth", "architecture"]):
        score += 0.15
    # Boost for people/feedback
    if any(w in text for w in ["prabhu", "smita", "aashima", "shipra", "feedback"]):
        score += 0.15
    # Boost for longer, more detailed memories
    if len(memory_text) > 200:
        score += 0.1
    # Lower for generic tool actions
    if any(w in text for w in ["git status", "npm install", "pip install"]):
        score -= 0.2
    return min(max(score, 0.1), 1.0)


def run(dry_run=False):
    """Run the full consolidation pipeline."""
    print("=" * 60)
    print("MEMORY CONSOLIDATOR — Level 3 Agent")
    print(f"Run time: {datetime.now().isoformat()}")
    print("=" * 60)

    # Step 1: Fetch all Mem0 memories
    print("\n[1/5] Fetching all Mem0 memories...")
    all_memories = mem0_client.get_all_memories(max_pages=20)
    print(f"  Fetched {len(all_memories)} memories from Mem0 cloud")

    # Step 2: Identify noise
    print("\n[2/5] Identifying noise...")
    noise = [m for m in all_memories if is_noise(m.get("memory", ""))]
    signal = [m for m in all_memories if not is_noise(m.get("memory", ""))]
    print(f"  Signal: {len(signal)} memories")
    print(f"  Noise:  {len(noise)} memories ({len(noise)/max(len(all_memories),1)*100:.0f}%)")

    if noise and not dry_run:
        print(f"  Removing {len(noise)} noise memories from Mem0...")
        removed = 0
        for m in noise:
            result = mem0_client.delete(m["id"])
            if result is not None:
                removed += 1
        print(f"  Removed {removed}/{len(noise)} noise memories")
    elif noise:
        print(f"  [DRY RUN] Would remove {len(noise)} noise memories")
        for m in noise[:5]:
            print(f"    - {m.get('memory', '')[:80]}...")

    # Step 3: Find duplicates
    print("\n[3/5] Finding duplicates...")
    dup_groups = find_duplicates(signal)
    total_dups = sum(len(g) - 1 for g in dup_groups)
    print(f"  Found {len(dup_groups)} duplicate groups ({total_dups} redundant memories)")

    if dup_groups and not dry_run:
        print(f"  Deduplicating (keeping longest in each group)...")
        deduped = 0
        for group in dup_groups:
            # Keep the longest (most detailed) memory
            group.sort(key=lambda m: len(m.get("memory", "")), reverse=True)
            for m in group[1:]:  # Delete all but the longest
                mem0_client.delete(m["id"])
                deduped += 1
        print(f"  Removed {deduped} duplicate memories")
    elif dup_groups:
        print(f"  [DRY RUN] Would remove {total_dups} duplicate memories")

    # Step 4: Categorize and score remaining
    print("\n[4/5] Categorizing and scoring...")
    category_counts = defaultdict(int)
    high_value = []
    for m in signal:
        text = m.get("memory", "")
        cats = categorize_memory(text)
        importance = assess_importance(text, cats)
        m["_categories"] = cats
        m["_importance"] = importance
        for c in cats:
            category_counts[c] += 1
        if importance >= 0.7:
            high_value.append(m)

    print(f"  Categories:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {count}")
    print(f"  High-value memories (importance >= 0.7): {len(high_value)}")

    # Step 5: Promote high-value to memorymesh
    print("\n[5/5] Promoting high-value memories to memorymesh...")
    existing = memorymesh_client.get_all_memories()
    existing_texts = {m["content"][:100].lower() for m in existing}
    promoted = 0

    for m in high_value:
        text = m.get("memory", "")
        # Skip if already in memorymesh
        if text[:100].lower() in existing_texts:
            continue
        if not dry_run:
            memorymesh_client.store_memory(
                content=text,
                importance=m["_importance"],
                tags=m["_categories"],
                source="consolidator",
            )
            promoted += 1
        else:
            print(f"  [DRY RUN] Would promote: {text[:80]}...")
            promoted += 1

    print(f"  Promoted {promoted} memories to memorymesh")

    # Summary
    final_stats = memorymesh_client.get_stats()
    final_mem0_count = mem0_client.get_total_count()

    print("\n" + "=" * 60)
    print("CONSOLIDATION COMPLETE")
    print(f"  Mem0 Cloud:     {final_mem0_count} memories (was {len(all_memories)})")
    print(f"  memorymesh:     {final_stats['total']} memories")
    print(f"  Noise removed:  {len(noise)}")
    print(f"  Duplicates removed: {total_dups}")
    print(f"  Promoted to memorymesh: {promoted}")
    print("=" * 60)

    return {
        "total_processed": len(all_memories),
        "noise_removed": len(noise),
        "duplicates_removed": total_dups,
        "promoted": promoted,
        "final_mem0": final_mem0_count,
        "final_memorymesh": final_stats["total"],
    }


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    if dry:
        print("*** DRY RUN MODE — no changes will be made ***\n")
    run(dry_run=dry)
