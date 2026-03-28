#!/bin/bash
# mesh_scan.sh — Scan and display all capabilities in the mesh
# Shows what's available without needing the LLM coordinator

MESH_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== SWARM CAPABILITY MESH ==="
echo ""

for TYPE_DIR in llm tools viewers claws; do
    DIR="$MESH_DIR/$TYPE_DIR"
    [ -d "$DIR" ] || continue

    COUNT=$(ls "$DIR"/*.capabilities.json 2>/dev/null | wc -l)
    [ "$COUNT" -eq 0 ] && continue

    echo "--- ${TYPE_DIR^^} ($COUNT providers) ---"
    for f in "$DIR"/*.capabilities.json; do
        [ -f "$f" ] || continue
        # Simple parse with grep/sed for no-python environments
        AGENT=$(grep -o '"agent_id"[[:space:]]*:[[:space:]]*"[^"]*"' "$f" | head -1 | sed 's/.*"agent_id"[[:space:]]*:[[:space:]]*"\([^"]*\)"/\1/')
        # Count capabilities in file
        CAP_COUNT=$(grep -c '"id"' "$f")
        echo "  $AGENT: $CAP_COUNT capabilities"
        # Show each capability id and status
        grep -o '"id"[[:space:]]*:[[:space:]]*"[^"]*"' "$f" | while read -r line; do
            CAP_ID=$(echo "$line" | sed 's/.*"\([^"]*\)"$/\1/')
            echo "    - $CAP_ID"
        done
    done
    echo ""
done

echo "=== END MESH SCAN ==="
