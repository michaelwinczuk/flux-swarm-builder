# Graph Query Tool

## Description
Queries the swarm's knowledge graph using typed edge traversal and BM25 gap-fill. Returns relevant nodes and their relationships.

## Input
```json
{
  "query": "search terms",
  "max_results": 20,
  "edge_types": ["Causes", "Enables", "Requires"],
  "depth": 2
}
```

## Output
```json
{
  "results": [
    {
      "node": "node_name",
      "description": "...",
      "confidence": 0.95,
      "path": "query -> Causes -> node_name",
      "source": "cluster_name"
    }
  ],
  "total_found": 42
}
```

## Access
All agents (shared tool)
