#!/bin/bash
# ============================================================================
# Claude Memory Machine — Mem0 Cloud Hook
# Pushes raw session actions to Mem0 for ground truth preservation (Tier 2)
# Called by Claude Code hooks after PostToolUse events
# ============================================================================

set -euo pipefail

MEM0_API_KEY="{{MEM0_API_KEY}}"
MEM0_URL="https://api.mem0.ai/v1/memories/"
USER_ID="{{MEM0_USER_ID}}"

# Read the hook input (JSON with tool_name, tool_input, tool_output)
INPUT=$(cat)

# Extract meaningful content from tool actions
TOOL_INPUT=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    tool = data.get('tool_name', '')
    if tool in ('Write', 'Edit', 'Bash'):
        file_path = data.get('tool_input', {}).get('file_path', data.get('tool_input', {}).get('command', ''))
        out = str(data.get('tool_output', ''))[:500]
        print(f'Claude Code action: {tool} on {file_path}. Output preview: {out[:200]}')
    else:
        print('')
except:
    print('')
" 2>/dev/null)

# Skip if empty or trivial
if [ -z "$TOOL_INPUT" ] || [ ${#TOOL_INPUT} -lt 20 ]; then
    exit 0
fi

# Push to Mem0 in background (non-blocking, preserves ground truth)
CONTENT_ESCAPED=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip())[1:-1])")

curl -s --request POST \
  --url "$MEM0_URL" \
  --header "Authorization: Token $MEM0_API_KEY" \
  --header "Content-Type: application/json" \
  --data "{
    \"messages\": [{\"role\": \"user\", \"content\": \"$CONTENT_ESCAPED\"}],
    \"user_id\": \"$USER_ID\",
    \"metadata\": {
      \"source\": \"claude-memory-machine\",
      \"category\": \"episodic-ground-truth\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }
  }" > /dev/null 2>&1 &

exit 0
