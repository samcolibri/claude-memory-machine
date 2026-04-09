"""
Memory Agent Configuration
Auto-detects paths and loads API keys from standard locations.
Works on any machine — no hardcoded paths.
"""

import os
from pathlib import Path

# ============================================================================
# Load environment variables from common .env locations
# ============================================================================
ENV_FILES = [
    Path.home() / ".env",
    Path.home() / ".claude" / ".env",
    Path.cwd() / ".env",
]


def load_env():
    """Load .env files into os.environ (first found wins per key)."""
    for env_file in ENV_FILES:
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip("'\"")
                        if key and value:
                            os.environ.setdefault(key, value)


load_env()

# ============================================================================
# API Keys (all optional — agents fall back to heuristics without them)
# ============================================================================
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MEM0_API_KEY = os.environ.get("MEM0_API_KEY", "")
MEM0_USER_ID = os.environ.get("MEM0_USER_ID", f"{os.environ.get('USER', 'default')}-claude-memory")

# ============================================================================
# Paths (auto-detected from home directory, no hardcoding)
# ============================================================================
CLAUDE_DIR = Path.home() / ".claude"

# Claude Code uses this format for project dirs: /Users/foo → -Users-foo
HOME_ESCAPED = str(Path.home()).replace("/", "-")
MEMORY_DIR = CLAUDE_DIR / "projects" / HOME_ESCAPED / "memory"

# memorymesh database (optional — used if installed)
MEMORYMESH_DB = Path.home() / ".memorymesh" / "memory.db"
MEMORYMESH_AVAILABLE = MEMORYMESH_DB.exists()

# Agent logs
AGENTS_DIR = Path(__file__).parent
LOG_DIR = AGENTS_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ============================================================================
# Mem0 API config
# ============================================================================
MEM0_BASE_URL = "https://api.mem0.ai/v1"
MEM0_AVAILABLE = bool(MEM0_API_KEY)

# ============================================================================
# Claude model for agent analysis
# ============================================================================
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# ============================================================================
# Consolidation thresholds
# ============================================================================
NOISE_KEYWORDS = [
    "user ran git status", "user executed a bash command",
    "user ran ls", "user ran cd", "git diff", "git log",
    "user checked", "user viewed", "user listed",
]
MIN_MEMORY_LENGTH = 30
DEDUP_SIMILARITY_THRESHOLD = 0.85
PATTERN_MIN_OCCURRENCES = 3

# ============================================================================
# Status check (run this file directly to verify config)
# ============================================================================
if __name__ == "__main__":
    print("Claude Memory Machine — Agent Configuration")
    print(f"  Home:            {Path.home()}")
    print(f"  Claude dir:      {CLAUDE_DIR}")
    print(f"  Memory dir:      {MEMORY_DIR} ({'exists' if MEMORY_DIR.exists() else 'not found — run install.sh first'})")
    print(f"  memorymesh:      {'found' if MEMORYMESH_AVAILABLE else 'not installed (optional)'}")
    print(f"  Mem0 API:        {'configured' if MEM0_AVAILABLE else 'not configured (optional)'}")
    print(f"  Anthropic API:   {'configured' if ANTHROPIC_API_KEY else 'not configured (optional)'}")
    print(f"  Log dir:         {LOG_DIR}")
    print()
    if not MEM0_AVAILABLE and not MEMORYMESH_AVAILABLE:
        print("  NOTE: No memory backends configured.")
        print("  The system works with just local markdown files.")
        print("  For more power, install memorymesh or configure Mem0.")
