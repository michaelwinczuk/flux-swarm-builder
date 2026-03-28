# FLUX Swarm Builder

**Build a complete multi-agent AI team from plain markdown files. Runs locally on your GPU in under 20 seconds. Zero cloud cost. No API keys required.**

Your agents are `.md` files. Your knowledge is a folder of documents. Drop them in, ask a question, get a synthesized report from 6 specialist agents. Everything runs on a local 3.8B model — the cloud API is never touched for core operations.

```
$ python swarm.py "What is the best go-to-market strategy for an AI startup?"

📚  Knowledge: 6 local files, 527 from research/ (533 total)
🔍  ClusterScout: 50 keyword hits → LLM refined to 16 sources (1.0s)
🔎  QueryExpander: 9 expanded search terms (1.4s)
🔍  Second pass: 34 total knowledge sources

🧠  Running 6 specialist agents...
   ✓ causes:      Root cause analysis (789ms)
   ✓ requires:    Dependency mapping (2130ms)
   ✓ solves:      Solution identification (1435ms)
   ✓ contradicts: Risk & failure modes (796ms)
   ✓ tradeoff:    Cost-benefit analysis (1396ms)
   ✓ systems:     Architecture review (795ms)

🎯  Synthesis complete (6.2s)
✅  Mission complete in 16.1s → output/report.md
```

## Why This Exists

Every multi-agent framework in 2026 requires cloud APIs, Python code, and complex setup. FLUX takes a different approach:

- **Agents are markdown.** Create `agents/researcher/cartridge.md`, define a role and expertise, done. No code.
- **Knowledge is drag-and-drop.** Move `.md` files into `knowledge/` and they're instantly searchable.
- **Everything runs locally.** A 3.8B model handles routing and analysis. Your data never leaves your machine.
- **The mesh self-organizes.** Agents declare capabilities in JSON tokens. The coordinator matches needs to abilities.

Built while competing in [OpenAI Parameter Golf](https://github.com/openai/parameter-golf) — where we beat SOTA (PR #977: 1.1185 BPB) using this swarm to research optimization techniques across 8 sequential missions.

## Quick Start (60 seconds)

```bash
# 1. Clone
git clone https://github.com/michaelwinczuk/flux-swarm-builder.git
cd flux-swarm-builder

# 2. Install Ollama + model (one time)
bash setup.sh

# 3. Start Ollama (in a separate terminal)
ollama serve

# 4. Run your first mission
python3 swarm.py "How should a small AI startup price its product?"
```

## Load Your Own Knowledge

Drop any `.md` or `.txt` files into `knowledge/` and the swarm searches them automatically.

For large knowledge bases (hundreds or thousands of files):
```bash
SWARM_KNOWLEDGE_PATH=/path/to/your/research python3 swarm.py "Your question"
```

The swarm uses a two-stage search: fast keyword matching across ALL files, then the local LLM refines to the most relevant sources. 533 files searched in under 1 second.

## Create an Agent

Create a folder in `agents/` with a `cartridge.md`:

```markdown
# Researcher — Deep Analysis Agent

## Role
Investigates complex topics by searching knowledge files,
identifying patterns, and producing evidence-based analysis.

## Expertise
- Literature review and synthesis
- Cross-domain pattern matching
- Evidence grading

## Constraints
- Must cite at least 2 sources per claim
- Flags uncertainty explicitly
```

That's it. The agent is live. No code, no config, no deployment.

## Folder Structure

```
my-swarm/
├── swarm.py                 # Mission runner (single file, no dependencies)
├── constitution.md          # Swarm-wide rules all agents follow
├── swarm.json               # Agent registry + mesh config
├── knowledge/               # Drop files here — auto-searched
│   ├── company/             # Business docs
│   ├── research/            # Technical papers
│   └── any-topic/           # Anything you want the swarm to know
├── agents/                  # One folder per agent
│   └── alpha/
│       ├── cartridge.md     # Agent identity (the only required file)
│       ├── scorecard.json   # Performance tracking
│       └── audit.json       # Action trail
├── mesh/                    # Capability discovery
│   ├── llm/                 # LLM connector tokens
│   ├── tools/               # Tool capability tokens
│   └── viewers/             # Data oracle tokens
└── output/                  # Mission reports land here
```

## How the Pipeline Works

1. **ClusterScout** searches all knowledge files using keyword matching, then asks the local LLM to pick the most relevant
2. **QueryExpander** generates synonyms and related terms to catch knowledge the keywords missed
3. **Second Pass** re-searches with expanded terms for deeper coverage
4. **6 Specialists** each analyze the knowledge from their unique angle (causes, requirements, solutions, risks, costs, architecture)
5. **Synthesis** combines all specialist findings into a coherent report with contradictions, gaps, and next steps

All powered by a local 3.8B model. Zero API calls. Under 20 seconds.

## Technical Details

- **Runtime:** Python 3.10+, single file (`swarm.py`), no framework dependencies
- **Local Model:** Phi-3 3.8B via [Ollama](https://ollama.ai) (2.4 GB, runs on 4GB+ VRAM)
- **Knowledge Search:** Two-stage — keyword TF-IDF scoring → LLM refinement
- **Capability Mesh:** JSON-based capability tokens in typed subdirectories
- **Governance:** Constitution rules injected into every synthesis call

## Background

This project was built during an intensive research sprint competing in [OpenAI's Parameter Golf](https://github.com/openai/parameter-golf) challenge. The swarm was used to research optimization techniques — running 8 sequential missions that identified Multi-Token Prediction as a key improvement, ultimately beating the competition SOTA.

The swarm that researches is also the product being built. Meta, but it works.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.ai) with any model (default: Phi-3 3.8B, 2.4 GB)
- Any GPU with 4GB+ VRAM (tested on RTX 4070, works on Apple Silicon)

## License

MIT
