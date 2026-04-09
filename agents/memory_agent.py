#!/usr/bin/env python3
"""
Memory Agent — Master Orchestrator
Runs all Level 3 + Level 4 memory agents in sequence.

Usage:
    python3 memory_agent.py                  # Run all agents
    python3 memory_agent.py consolidate      # Just consolidator
    python3 memory_agent.py patterns         # Just pattern detector
    python3 memory_agent.py twin             # Just digital twin
    python3 memory_agent.py causal           # Just causal tracker
    python3 memory_agent.py briefing         # Just daily briefing
    python3 memory_agent.py --dry-run        # Consolidator in dry-run mode
"""

import sys
import os
import time
from datetime import datetime

# Ensure we can import sibling modules
sys.path.insert(0, os.path.dirname(__file__))

import config


def run_agent(name, func, *args, **kwargs):
    """Run an agent with timing and error handling."""
    print(f"\n{'#' * 60}")
    print(f"# RUNNING: {name}")
    print(f"{'#' * 60}\n")
    start = time.time()
    try:
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"\n  [{name}] Completed in {elapsed:.1f}s")
        return result
    except Exception as e:
        elapsed = time.time() - start
        print(f"\n  [{name}] FAILED after {elapsed:.1f}s: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_all(dry_run=False):
    """Run the full agent pipeline."""
    print("=" * 60)
    print("MEMORY AGENT — Master Orchestrator")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"Anthropic API: {'Available' if config.ANTHROPIC_API_KEY else 'Not configured'}")
    print(f"Mem0 API: {'Available' if config.MEM0_API_KEY else 'Not configured'}")
    print("=" * 60)

    results = {}

    # 1. Consolidate (clean up noise, dedup, promote)
    import consolidator
    results["consolidator"] = run_agent(
        "Memory Consolidator (Level 3)",
        consolidator.run,
        dry_run=dry_run,
    )

    # 2. Detect patterns
    import pattern_detector
    results["patterns"] = run_agent(
        "Pattern Detector (Level 3)",
        pattern_detector.run,
    )

    # 3. Build digital twin
    import digital_twin
    results["twin"] = run_agent(
        "Digital Twin (Level 4)",
        digital_twin.run,
    )

    # 4. Track causal chains
    import causal_tracker
    results["causal"] = run_agent(
        "Causal Tracker (Level 4)",
        causal_tracker.run,
    )

    # 5. Generate daily briefing (runs last — uses outputs from above)
    import daily_briefing
    results["briefing"] = run_agent(
        "Daily Briefing (Level 3)",
        daily_briefing.run,
    )

    # Summary
    print("\n" + "=" * 60)
    print("ALL AGENTS COMPLETE")
    print("=" * 60)
    for name, result in results.items():
        status = "OK" if result is not None else "FAILED"
        print(f"  {name}: {status}")
    print("=" * 60)

    return results


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    if not args:
        run_all(dry_run=dry_run)
    elif args[0] == "consolidate":
        import consolidator
        consolidator.run(dry_run=dry_run)
    elif args[0] == "patterns":
        import pattern_detector
        pattern_detector.run()
    elif args[0] == "twin":
        import digital_twin
        digital_twin.run()
    elif args[0] == "causal":
        import causal_tracker
        causal_tracker.run()
    elif args[0] == "briefing":
        import daily_briefing
        daily_briefing.run()
    else:
        print(f"Unknown agent: {args[0]}")
        print("Available: consolidate, patterns, twin, causal, briefing")
        sys.exit(1)


if __name__ == "__main__":
    main()
