"""
Memory Agent Configuration
Loads API keys from all known .env locations on this machine.
"""

import os
from pathlib import Path

# Load .env files (order matters — later overrides earlier)
ENV_FILES = [
    Path.home() / ".env",
    Path.home() / "super-brain" / "config" / ".env",
    Path.home() / "colibri-qa-platform" / ".env",
]

def load_env():
    """Load all .env files into os.environ."""
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

# API Keys
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MEM0_API_KEY = os.environ.get("MEM0_API_KEY", "")
MEM0_USER_ID = os.environ.get("MEM0_USER_ID", "anmol-super-brain")

# Paths
MEMORY_DIR = Path.home() / ".claude" / "projects" / "-Users-anmolsam" / "memory"
MEMORYMESH_DB = Path.home() / ".memorymesh" / "memory.db"
AGENTS_DIR = Path(__file__).parent
LOG_DIR = AGENTS_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Mem0 API
MEM0_BASE_URL = "https://api.mem0.ai/v1"

# Claude model for analysis
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # Cost-efficient for background analysis

# Thresholds
NOISE_KEYWORDS = [
    "user ran git status", "user executed a bash command",
    "user ran ls", "user ran cd", "git diff", "git log",
    "user checked", "user viewed", "user listed",
]
MIN_MEMORY_LENGTH = 30  # Characters — shorter is likely noise
DEDUP_SIMILARITY_THRESHOLD = 0.85  # Fuzzy match threshold
PATTERN_MIN_OCCURRENCES = 3  # Minimum times a topic must appear to be a "pattern"
