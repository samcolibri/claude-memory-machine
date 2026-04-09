#!/bin/bash
# ============================================================================
# Install memory agent cron jobs
# Usage: bash agents/install_cron.sh
# ============================================================================

AGENTS_DIR="${1:-$HOME/.claude/memory-agents}"

if [ ! -f "$AGENTS_DIR/memory_agent.py" ]; then
    echo "Error: memory_agent.py not found at $AGENTS_DIR"
    echo "Run install.sh first, or pass the agents directory:"
    echo "  bash install_cron.sh /path/to/agents"
    exit 1
fi

# Get existing crontab
EXISTING=$(crontab -l 2>/dev/null || echo "")

if echo "$EXISTING" | grep -q "Memory Agents"; then
    echo "Memory agent crons already installed."
    echo "To remove: crontab -l | grep -v 'memory-agents\|Memory Agents' | crontab -"
    exit 0
fi

NEW_CRONS="
# === Memory Agents (Level 3 + Level 4) ===
# Daily Briefing — 5:30 AM local (before your first session)
30 5 * * * cd $AGENTS_DIR && /usr/bin/python3 daily_briefing.py >> $AGENTS_DIR/logs/briefing.log 2>&1
# Memory Consolidator — 1:00 AM local (cleanup overnight)
0 1 * * * cd $AGENTS_DIR && /usr/bin/python3 consolidator.py >> $AGENTS_DIR/logs/consolidator.log 2>&1
# Pattern Detector — 11:00 PM local (end of day analysis)
0 23 * * * cd $AGENTS_DIR && /usr/bin/python3 pattern_detector.py >> $AGENTS_DIR/logs/patterns.log 2>&1
# Digital Twin — Sundays 2:00 AM local (weekly model rebuild)
0 2 * * 0 cd $AGENTS_DIR && /usr/bin/python3 digital_twin.py >> $AGENTS_DIR/logs/twin.log 2>&1
# Causal Tracker — Fridays 11:00 PM local (weekly decision analysis)
0 23 * * 5 cd $AGENTS_DIR && /usr/bin/python3 causal_tracker.py >> $AGENTS_DIR/logs/causal.log 2>&1"

echo "${EXISTING}${NEW_CRONS}" | crontab -

echo "Memory agent crons installed:"
echo "  Daily Briefing:      5:30 AM daily"
echo "  Consolidator:        1:00 AM daily"
echo "  Pattern Detector:   11:00 PM daily"
echo "  Digital Twin:        2:00 AM Sundays"
echo "  Causal Tracker:     11:00 PM Fridays"
echo ""
echo "Logs at: $AGENTS_DIR/logs/"
echo ""
echo "To verify: crontab -l | grep memory-agents"
