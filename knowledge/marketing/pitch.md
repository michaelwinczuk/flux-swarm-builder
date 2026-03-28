# SwarmForge AI — Pitch

## One Line
Build a multi-agent AI team from markdown files. Runs locally on your GPU. Zero cloud dependency.

## The Problem
Building multi-agent AI systems today requires:
- Complex Python frameworks (CrewAI, AutoGen, LangGraph)
- Cloud API dependencies ($$$, latency, privacy concerns)
- Code-heavy configuration (not accessible to non-developers)
- No visual tooling for designing agent workflows

## Our Solution
FLUX Swarm Builder: a folder-based multi-agent system where:
- Agents are .md files (human-readable, editable with any text editor)
- Knowledge is drop-in (move files into a folder, auto-indexed)
- A 3.8B local model handles all routing at zero cost
- Only deep synthesis touches the cloud API
- Full mission: question in → 6 specialists → synthesized report in 10 seconds

## Traction
- Beat OpenAI's Parameter Golf SOTA using our own swarm for research
- PR #977 (1.1185 BPB) and PR #1031 (MTP funnel, awaiting eval)
- 40+ knowledge clusters, 330K+ graph nodes, 80K+ edges in production swarm
- Running locally on an RTX 4070 with 64GB RAM

## Ask
Open sourcing Q2 2026. Looking for:
- Early adopters willing to test and give feedback
- Contributors interested in visual agent tooling
- Potential pilot customers for industry-specific swarm templates
