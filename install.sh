#!/usr/bin/env bash
# ============================================================================
# Claude Memory Machine — Installer
# Gives Claude Code a real memory using MemMachine's 3-tier architecture
# ============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Config
CLAUDE_DIR="$HOME/.claude"
MEMORY_DIR=""
WITH_MEM0=false
MEM0_API_KEY=""
MEM0_USER_ID=""
BACKUP_EXISTING=true

# ============================================================================
# Parse arguments
# ============================================================================
while [[ $# -gt 0 ]]; do
    case $1 in
        --with-mem0)
            WITH_MEM0=true
            shift
            ;;
        --mem0-key)
            MEM0_API_KEY="$2"
            shift 2
            ;;
        --mem0-user-id)
            MEM0_USER_ID="$2"
            shift 2
            ;;
        --memory-dir)
            MEMORY_DIR="$2"
            shift 2
            ;;
        --no-backup)
            BACKUP_EXISTING=false
            shift
            ;;
        -h|--help)
            echo "Usage: ./install.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --with-mem0          Enable Mem0 cloud integration for ground truth storage"
            echo "  --mem0-key KEY       Mem0 API key (or set MEM0_API_KEY env var)"
            echo "  --mem0-user-id ID    Mem0 user ID (default: \$(whoami)-claude-memory)"
            echo "  --memory-dir PATH    Custom memory directory (default: auto-detected)"
            echo "  --no-backup          Don't backup existing config files"
            echo "  -h, --help           Show this help"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# ============================================================================
# Banner
# ============================================================================
echo ""
echo -e "${CYAN}${BOLD}"
echo "  ╔══════════════════════════════════════════════════════════════╗"
echo "  ║                                                            ║"
echo "  ║          CLAUDE MEMORY MACHINE                             ║"
echo "  ║          ━━━━━━━━━━━━━━━━━━━━━                             ║"
echo "  ║          Give Claude Code a real memory.                   ║"
echo "  ║          Every session. Every directory. Forever.          ║"
echo "  ║                                                            ║"
echo "  ║          Inspired by MemMachine (Wang et al., 2026)        ║"
echo "  ║          Ground-truth-preserving 3-tier architecture       ║"
echo "  ║                                                            ║"
echo "  ╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================================
# Detect environment
# ============================================================================
echo -e "${BLUE}[1/6]${NC} Detecting environment..."

# Check Claude Code is installed
if ! command -v claude &> /dev/null; then
    echo -e "${YELLOW}  Warning: 'claude' CLI not found in PATH.${NC}"
    echo -e "  Claude Memory Machine requires Claude Code CLI."
    echo -e "  Install it from: https://claude.ai/download"
    echo ""
    read -p "  Continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "unknown")
    echo -e "  ${GREEN}Claude Code found: ${CLAUDE_VERSION}${NC}"
fi

# Ensure .claude directory exists
if [ ! -d "$CLAUDE_DIR" ]; then
    echo -e "  ${YELLOW}Creating ~/.claude directory...${NC}"
    mkdir -p "$CLAUDE_DIR"
fi

# Detect project-specific memory directory
if [ -z "$MEMORY_DIR" ]; then
    # Convert home path to Claude's project directory format
    HOME_ESCAPED=$(echo "$HOME" | sed 's|/|-|g')
    MEMORY_DIR="$CLAUDE_DIR/projects/${HOME_ESCAPED}/memory"
fi

echo -e "  ${GREEN}Memory directory: ${MEMORY_DIR}${NC}"
echo -e "  ${GREEN}Claude config: ${CLAUDE_DIR}${NC}"

# ============================================================================
# Backup existing config
# ============================================================================
echo -e "${BLUE}[2/6]${NC} Checking existing configuration..."

if [ "$BACKUP_EXISTING" = true ]; then
    BACKUP_DIR="$CLAUDE_DIR/backups/$(date +%Y%m%d_%H%M%S)"
    NEEDS_BACKUP=false

    if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
        NEEDS_BACKUP=true
    fi
    if [ -f "$CLAUDE_DIR/settings.json" ]; then
        NEEDS_BACKUP=true
    fi

    if [ "$NEEDS_BACKUP" = true ]; then
        echo -e "  ${YELLOW}Backing up existing config to ${BACKUP_DIR}${NC}"
        mkdir -p "$BACKUP_DIR"
        [ -f "$CLAUDE_DIR/CLAUDE.md" ] && cp "$CLAUDE_DIR/CLAUDE.md" "$BACKUP_DIR/"
        [ -f "$CLAUDE_DIR/settings.json" ] && cp "$CLAUDE_DIR/settings.json" "$BACKUP_DIR/"
        echo -e "  ${GREEN}Backup complete.${NC}"
    else
        echo -e "  ${GREEN}No existing config to backup.${NC}"
    fi
fi

# ============================================================================
# Create memory directory structure
# ============================================================================
echo -e "${BLUE}[3/6]${NC} Creating memory architecture..."

mkdir -p "$MEMORY_DIR"

# Create MEMORY.md index if it doesn't exist
if [ ! -f "$MEMORY_DIR/MEMORY.md" ]; then
    cp "$(dirname "$0")/memory/templates/MEMORY.md" "$MEMORY_DIR/MEMORY.md"
    echo -e "  ${GREEN}Created MEMORY.md index${NC}"
else
    echo -e "  ${YELLOW}MEMORY.md already exists — preserving${NC}"
fi

# Create episodic memory files
if [ ! -f "$MEMORY_DIR/episodic_last_session.md" ]; then
    cp "$(dirname "$0")/memory/templates/episodic_last_session.md" "$MEMORY_DIR/episodic_last_session.md"
    echo -e "  ${GREEN}Created episodic_last_session.md${NC}"
fi

if [ ! -f "$MEMORY_DIR/episodic_sessions.md" ]; then
    cp "$(dirname "$0")/memory/templates/episodic_sessions.md" "$MEMORY_DIR/episodic_sessions.md"
    echo -e "  ${GREEN}Created episodic_sessions.md${NC}"
fi

# Create starter user profile
if [ ! -f "$MEMORY_DIR/user_profile.md" ]; then
    USERNAME=$(whoami)
    cat > "$MEMORY_DIR/user_profile.md" << USEREOF
---
name: User Profile
description: Basic profile for ${USERNAME} — Claude will learn more over time
type: user
---

User: ${USERNAME}
Setup date: $(date +%Y-%m-%d)
Memory system: Claude Memory Machine (MemMachine-inspired)

Claude will automatically learn and update this profile as you interact.
USEREOF
    echo -e "  ${GREEN}Created starter user profile${NC}"

    # Add to index if not already there
    if ! grep -q "user_profile.md" "$MEMORY_DIR/MEMORY.md" 2>/dev/null; then
        echo "- [User Profile](user_profile.md) — Basic profile, will be enriched over time" >> "$MEMORY_DIR/MEMORY.md"
    fi
fi

echo -e "  ${GREEN}Memory architecture ready.${NC}"

# ============================================================================
# Install global CLAUDE.md
# ============================================================================
echo -e "${BLUE}[4/6]${NC} Installing global CLAUDE.md (the brain)..."

# Generate the CLAUDE.md with the correct memory path
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
sed "s|{{MEMORY_DIR}}|${MEMORY_DIR}|g" "$SCRIPT_DIR/setup/CLAUDE.md.template" > "$CLAUDE_DIR/CLAUDE.md"

echo -e "  ${GREEN}Global CLAUDE.md installed at ~/.claude/CLAUDE.md${NC}"
echo -e "  ${GREEN}This will load in EVERY Claude Code session, in any directory.${NC}"

# ============================================================================
# Configure hooks (optional Mem0)
# ============================================================================
echo -e "${BLUE}[5/6]${NC} Configuring hooks..."

if [ "$WITH_MEM0" = true ]; then
    # Get Mem0 credentials
    if [ -z "$MEM0_API_KEY" ]; then
        MEM0_API_KEY="${MEM0_API_KEY:-}"
        if [ -z "$MEM0_API_KEY" ]; then
            echo -e "  ${YELLOW}Mem0 API key required.${NC}"
            echo -n "  Enter your Mem0 API key: "
            read -r MEM0_API_KEY
        fi
    fi

    if [ -z "$MEM0_USER_ID" ]; then
        MEM0_USER_ID="$(whoami)-claude-memory"
    fi

    # Create the hook script
    HOOK_DIR="$CLAUDE_DIR/hooks"
    mkdir -p "$HOOK_DIR"

    sed -e "s|{{MEM0_API_KEY}}|${MEM0_API_KEY}|g" \
        -e "s|{{MEM0_USER_ID}}|${MEM0_USER_ID}|g" \
        "$SCRIPT_DIR/setup/hooks/mem0_hook.sh" > "$HOOK_DIR/mem0_hook.sh"
    chmod +x "$HOOK_DIR/mem0_hook.sh"

    # Create or update settings.json
    if [ -f "$CLAUDE_DIR/settings.json" ]; then
        # Check if hooks already configured
        if grep -q "mem0_hook" "$CLAUDE_DIR/settings.json" 2>/dev/null; then
            echo -e "  ${YELLOW}Mem0 hook already configured in settings.json${NC}"
        else
            echo -e "  ${YELLOW}settings.json exists — please add the Mem0 hook manually:${NC}"
            echo ""
            echo "  Add to your settings.json hooks.PostToolUse:"
            echo "  {"
            echo "    \"matcher\": \"Write|Edit|Bash\","
            echo "    \"hooks\": [{"
            echo "      \"type\": \"command\","
            echo "      \"command\": \"$HOOK_DIR/mem0_hook.sh\""
            echo "    }]"
            echo "  }"
            echo ""
        fi
    else
        cat > "$CLAUDE_DIR/settings.json" << SETTINGSEOF
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "$HOOK_DIR/mem0_hook.sh"
          }
        ]
      }
    ]
  }
}
SETTINGSEOF
        echo -e "  ${GREEN}Mem0 hook configured in settings.json${NC}"
    fi

    echo -e "  ${GREEN}Mem0 integration enabled (ground truth preservation layer)${NC}"
else
    echo -e "  ${GREEN}Running in local-only mode (no cloud services).${NC}"
    echo -e "  ${CYAN}  Tip: Run with --with-mem0 to add ground truth cloud storage${NC}"
fi

# ============================================================================
# Verify installation
# ============================================================================
echo -e "${BLUE}[6/6]${NC} Verifying installation..."

ERRORS=0

if [ ! -f "$CLAUDE_DIR/CLAUDE.md" ]; then
    echo -e "  ${RED}FAIL: ~/.claude/CLAUDE.md not found${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "  ${GREEN}OK: Global CLAUDE.md installed${NC}"
fi

if [ ! -f "$MEMORY_DIR/MEMORY.md" ]; then
    echo -e "  ${RED}FAIL: MEMORY.md index not found${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "  ${GREEN}OK: Memory index exists${NC}"
fi

if [ ! -f "$MEMORY_DIR/episodic_last_session.md" ]; then
    echo -e "  ${RED}FAIL: episodic_last_session.md not found${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "  ${GREEN}OK: Episodic memory (STM bridge) exists${NC}"
fi

if [ ! -f "$MEMORY_DIR/episodic_sessions.md" ]; then
    echo -e "  ${RED}FAIL: episodic_sessions.md not found${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "  ${GREEN}OK: Episodic memory (rolling log) exists${NC}"
fi

# ============================================================================
# Done
# ============================================================================
echo ""
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}${BOLD}"
    echo "  ╔══════════════════════════════════════════════════════════════╗"
    echo "  ║                                                            ║"
    echo "  ║   INSTALLATION COMPLETE                                    ║"
    echo "  ║                                                            ║"
    echo "  ║   Claude now has a real memory.                            ║"
    echo "  ║   Open any new Claude Code session to experience it.       ║"
    echo "  ║                                                            ║"
    echo "  ║   Memory architecture:                                     ║"
    echo "  ║     Tier 1 (STM):      episodic_last_session.md           ║"
    echo "  ║     Tier 2 (Episodic): episodic_sessions.md               ║"
    echo "  ║     Tier 3 (Profile):  user_*.md, feedback_*.md, etc.     ║"
    echo "  ║                                                            ║"
    echo "  ║   Ground truth preservation: ACTIVE                       ║"
    echo "  ║   Contextualized retrieval:  ACTIVE                       ║"
    echo "  ║   Cross-directory memory:    ACTIVE                       ║"
    echo "  ║                                                            ║"
    echo "  ╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo -e "  ${CYAN}Your AI assistant just got a real memory.${NC}"
    echo ""
else
    echo -e "${RED}  Installation completed with ${ERRORS} error(s). Check output above.${NC}"
    exit 1
fi
