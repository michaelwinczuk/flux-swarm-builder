#!/bin/bash
# mesh_query.sh — Query the capability mesh using local Ollama
# Usage: ./mesh_query.sh "I need a fast LLM for classification"
# Usage: ./mesh_query.sh "I need a price feed for ETH"
#
# Scans all capability files in mesh/ subdirs, builds a capability list,
# sends to local Phi-3 for semantic matching, returns best match.

MESH_DIR="$(cd "$(dirname "$0")" && pwd)"
SWARM_DIR="$(dirname "$MESH_DIR")"
OLLAMA_ENDPOINT="${OLLAMA_HOST:-http://127.0.0.1:11434}"
NEED="$1"

if [ -z "$NEED" ]; then
    echo "Usage: mesh_query.sh \"what capability do you need?\""
    exit 1
fi

# Collect all capabilities from mesh subdirs
CAPABILITIES=""
for f in "$MESH_DIR"/llm/*.capabilities.json "$MESH_DIR"/tools/*.capabilities.json "$MESH_DIR"/viewers/*.capabilities.json "$MESH_DIR"/claws/*.capabilities.json; do
    [ -f "$f" ] || continue
    # Extract each capability entry with agent context
    AGENT_ID=$(python -c "import json,sys; d=json.load(open(sys.argv[1])); print(d['agent_id'])" "$f" 2>/dev/null)
    CAPS=$(python -c "
import json, sys
d = json.load(open(sys.argv[1]))
for c in d.get('capabilities', []):
    cost = c.get('config', {}).get('cost_per_call', 0)
    tags = ', '.join(c.get('tags', []))
    print(f\"- [{c['id']}] agent={d['agent_id']} type={c['type']} status={c['status']} cost=\${cost} tags=[{tags}] — {c['provides']}\")
" "$f" 2>/dev/null)
    if [ -n "$CAPS" ]; then
        CAPABILITIES="${CAPABILITIES}${CAPS}\n"
    fi
done

if [ -z "$CAPABILITIES" ]; then
    echo '{"match": null, "reason": "No capabilities registered in mesh"}'
    exit 0
fi

# Check constitution for blocked types
CONSTITUTION="$SWARM_DIR/constitution.md"

# Build the prompt
PROMPT="You are a capability matcher for a multi-agent swarm. Given a NEED and AVAILABLE capabilities, return the best match as JSON.

Rules:
- Match by semantic similarity of tags and descriptions
- Prefer cheapest capable option (free > paid, local > cloud)
- If no match, return {\"match\": null, \"reason\": \"...\"}
- Claws require constitutional approval — check if the claw type is approved

NEED: $NEED

AVAILABLE CAPABILITIES:
$(echo -e "$CAPABILITIES")

Respond with ONLY valid JSON:
{\"match\": \"capability_id\", \"agent\": \"agent_id\", \"confidence\": 0.0-1.0, \"reason\": \"why this is the best match\"}"

# Query Ollama
RESPONSE=$(curl -s "$OLLAMA_ENDPOINT/api/generate" \
    -d "$(python -c "import json; print(json.dumps({'model': 'phi3:3.8b-mini-128k-instruct-q4_K_M', 'prompt': '''$PROMPT''', 'stream': False, 'format': 'json'}))")" \
    2>/dev/null)

# Extract the response text
echo "$RESPONSE" | python -c "import json,sys; r=json.load(sys.stdin); print(r.get('response', '{\"error\": \"no response\"}'))" 2>/dev/null

