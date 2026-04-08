#!/usr/bin/env bash
# ============================================================================
# Claude Memory Machine — Uninstaller
# ============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

CLAUDE_DIR="$HOME/.claude"

echo ""
echo -e "${YELLOW}${BOLD}Claude Memory Machine — Uninstaller${NC}"
echo ""

# Remove global CLAUDE.md
if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
    echo -e "${BLUE}Removing global CLAUDE.md...${NC}"
    rm "$CLAUDE_DIR/CLAUDE.md"
    echo -e "  ${GREEN}Removed.${NC}"
else
    echo -e "  ${YELLOW}No global CLAUDE.md found.${NC}"
fi

# Remove hook scripts (if installed by us)
if [ -f "$CLAUDE_DIR/hooks/mem0_hook.sh" ]; then
    echo -e "${BLUE}Removing Mem0 hook...${NC}"
    rm "$CLAUDE_DIR/hooks/mem0_hook.sh"
    rmdir "$CLAUDE_DIR/hooks" 2>/dev/null || true
    echo -e "  ${GREEN}Removed.${NC}"
fi

# Ask about memory files
echo ""
echo -e "${YELLOW}Your memory files are preserved at:${NC}"

HOME_ESCAPED=$(echo "$HOME" | sed 's|/|-|g')
MEMORY_DIR="$CLAUDE_DIR/projects/${HOME_ESCAPED}/memory"

if [ -d "$MEMORY_DIR" ]; then
    echo -e "  ${MEMORY_DIR}"
    echo ""
    FILE_COUNT=$(find "$MEMORY_DIR" -name "*.md" | wc -l | tr -d ' ')
    echo -e "  Found ${FILE_COUNT} memory files."
    echo ""
    read -p "  Delete memory files too? This cannot be undone. (y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$MEMORY_DIR"
        echo -e "  ${RED}Memory files deleted.${NC}"
    else
        echo -e "  ${GREEN}Memory files preserved.${NC}"
    fi
else
    echo -e "  ${YELLOW}No memory directory found.${NC}"
fi

# Restore backup if available
LATEST_BACKUP=$(ls -td "$CLAUDE_DIR/backups"/*/ 2>/dev/null | head -1 || true)
if [ -n "$LATEST_BACKUP" ] && [ -d "$LATEST_BACKUP" ]; then
    echo ""
    read -p "  Restore pre-install backup from ${LATEST_BACKUP}? (y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        [ -f "${LATEST_BACKUP}CLAUDE.md" ] && cp "${LATEST_BACKUP}CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
        [ -f "${LATEST_BACKUP}settings.json" ] && cp "${LATEST_BACKUP}settings.json" "$CLAUDE_DIR/settings.json"
        echo -e "  ${GREEN}Backup restored.${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Uninstall complete. Claude Code is back to default behavior.${NC}"
echo ""
