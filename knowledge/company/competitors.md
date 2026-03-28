# SwarmForge AI — Competitive Analysis

## Direct Competitors

### CrewAI
- Python framework, 25k+ GitHub stars
- Agent roles defined in Python code (not markdown)
- Cloud-dependent for LLM calls
- No local model support
- No knowledge graph engine
- Weakness: requires coding, no visual builder, cloud-only

### AutoGen (Microsoft)
- Multi-agent conversation framework
- Strong enterprise backing
- Heavy, complex setup
- No local-first story
- Weakness: enterprise complexity, no visual canvas

### LangGraph
- Graph-based agent workflows
- Part of LangChain ecosystem
- Code-heavy, steep learning curve
- Weakness: complexity, no file-based simplicity

### Swarms (swarms.ai)
- Multi-agent orchestration
- Good API but cloud-focused
- Weakness: not local-first, no knowledge graph

## Our Differentiation
1. **File-based simplicity**: agents are .md files, not code
2. **Local-first**: runs on a 4070, no cloud required
3. **Knowledge graph**: JSON-LD + BM25 + algebraic reasoner (nobody else has this)
4. **Proven at scale**: built while competing in and beating Parameter Golf SOTA
5. **Visual canvas**: coming v0.2, drag-and-drop agent creation
6. **Zero cost**: local model handles routing, only synthesis needs API

## Key Insight
Every competitor requires cloud API calls for basic operations. We use a 3.8B local model for routing, scoring, and expansion — the expensive API is only called for deep synthesis. This makes us 10-100x cheaper per mission.
