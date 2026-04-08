#!/bin/bash
# ============================================================================
# mem0_recall.sh — Pull relevant memories from Mem0 cloud
# Usage: mem0_recall.sh "query string" [top_k]
# Place at: ~/.claude/scripts/mem0_recall.sh
# ============================================================================

set -euo pipefail

# Source your env file with MEM0_API_KEY and MEM0_USER_ID
# Customize this path to where your .env lives:
source "${MEM0_ENV_FILE:-$HOME/.env}" 2>/dev/null || true

MEM0_API_KEY="${MEM0_API_KEY:?Error: MEM0_API_KEY not set. Set it in your env file or export it.}"
MEM0_USER_ID="${MEM0_USER_ID:-$(whoami)-claude-memory}"
MEM0_URL="https://api.mem0.ai/v1/memories/search/"

QUERY="${1:-what is the user currently working on}"
TOP_K="${2:-10}"

RESPONSE=$(curl -s --max-time 10 --request POST \
  --url "$MEM0_URL" \
  --header "Authorization: Token $MEM0_API_KEY" \
  --header "Content-Type: application/json" \
  --data "{\"query\": \"$QUERY\", \"user_id\": \"$MEM0_USER_ID\", \"top_k\": $TOP_K}" 2>/dev/null)

if [ -z "$RESPONSE" ]; then
    echo "Mem0: No response (network issue or timeout)"
    exit 0
fi

python3 -c "
import json, sys
try:
    memories = json.loads(sys.stdin.read())
    if not memories:
        print('Mem0: No memories found')
        sys.exit(0)
    print('=== Mem0 Cloud Memories ===')
    print()
    for i, m in enumerate(memories, 1):
        memory = m.get('memory', 'N/A')
        created = m.get('created_at', 'N/A')[:10]
        score = m.get('score', 0)
        cats = m.get('categories', [])
        cat_str = ', '.join(cats) if isinstance(cats, list) else ''
        print(f'{i}. [{created}] (relevance: {score:.0%}) {memory}')
    print()
    print(f'Retrieved {len(memories)} memories from Mem0 cloud')
except Exception as e:
    print(f'Mem0 parse error: {e}')
" <<< "$RESPONSE" 2>/dev/null || echo "Mem0: Failed to parse response"
