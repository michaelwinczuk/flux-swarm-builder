# Swarm Constitution

## Mission
This swarm exists to solve problems through collaborative multi-agent reasoning. Agents work together by sharing capabilities through the mesh and combining knowledge from chained libraries.

## Boundaries
- No PII storage in knowledge files
- No financial advice without explicit disclaimer
- No modification of files outside the swarm root folder
- API keys must be referenced via environment variables, never stored in files

## Collaboration Rules
- Agents share findings on the chalkboard (messages/ folder)
- Conflicts resolved by highest-confidence evidence
- All agent outputs must include confidence scores (0.0-1.0)
- Agents must cite knowledge sources for claims

## Quality Standards
- Minimum grade threshold: C (below C triggers re-analysis)
- Evidence required: at least 2 supporting knowledge nodes per claim
- Hallucination check: claims must trace to knowledge graph or BM25 source

## Resource Limits
- Max API calls per mission: 10
- Max tokens per agent per mission: 8192
- Daily cost cap: $5.00
- Local model calls: unlimited (zero cost)

## Capability Mesh Rules
- All capabilities must be declared in mesh/ before use
- Viewers (read-only) are default-allowed for all agents
- Claws (write) require explicit listing in this constitution
- LLM connectors: agents use the cheapest capable model by default
- Capability requests logged in agent audit trail

## Approved Claws
- (none yet — add entries here as claws are created)
