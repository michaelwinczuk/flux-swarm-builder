# FLUX Swarm Builder

Build a multi-agent AI team from markdown files. Runs locally on your GPU. Zero cloud dependency.

## What It Does

Drop files into a folder. The swarm reads them, searches them, and answers your questions using 6 specialist agents — all running locally on your GPU in under 20 seconds.

```
$ python swarm.py "What is the best go-to-market strategy for an AI startup?"

📚  Knowledge: 6 local files, 527 from research/ (533 total)
🔍  ClusterScout: keyword search → 50 hits → LLM refined to 16 sources (1.0s)
🔎  QueryExpander: 9 expanded search terms (1.4s)
🧠  6 specialists analyzing...
   ✓ causes:      Root cause analysis (789ms)
   ✓ requires:    Dependency mapping (2130ms)
   ✓ solves:      Solution finding (1435ms)
   ✓ contradicts: Risk identification (796ms)
   ✓ tradeoff:    Cost analysis (1396ms)
   ✓ systems:     Architecture review (795ms)
🎯  Synthesis complete (6.2s)
✅  Mission complete in 16.1s → output/report.md
```

## Quick Start

```bash
# 1. Install Ollama (https://ollama.ai)
ollama pull phi3:3.8b-mini-128k-instruct-q4_K_M

# 2. Start Ollama
ollama serve

# 3. Run a mission
cd swarm-builder
python swarm.py "Your question here"
```

## Load Your Own Knowledge

Drop `.md` or `.txt` files into `knowledge/` and the swarm searches them automatically.

For massive knowledge bases, set the environment variable:
```bash
SWARM_KNOWLEDGE_PATH=/path/to/your/research python swarm.py "Your question"
```

## How It Works

**Agents are markdown files.** Each agent has a `cartridge.md` that defines its role, expertise, and personality. No code required to create a new agent — just create a folder and write a `.md` file.

**Knowledge is drop-in.** Move files into `knowledge/` and they're instantly searchable. The swarm uses keyword matching + a local LLM to find the most relevant sources for each mission.

**The mesh discovers capabilities.** Agents declare what they can do in `mesh/` capability tokens. The swarm coordinator matches needs to capabilities automatically.

**Everything runs locally.** A 3.8B model (Phi-3) handles all routing, scoring, and expansion at zero cost. Only deep synthesis optionally uses cloud APIs.

## Folder Structure

```
my-swarm/
├── constitution.md          # Swarm-wide rules
├── swarm.json               # Agent registry
├── swarm.py                 # Mission runner
├── knowledge/               # Drop files here — auto-searched
│   ├── company/
│   ├── research/
│   └── any-topic/
├── agents/                  # One folder per agent
│   ├── alpha/
│   │   ├── cartridge.md     # Agent personality + role
│   │   ├── scorecard.json   # Performance tracking
│   │   └── audit.json       # Action trail
│   └── sentinel/
├── mesh/                    # Capability discovery
│   ├── llm/                 # LLM connectors
│   ├── tools/               # Tool capabilities
│   └── viewers/             # Data oracles
├── tools/                   # Shared tools
└── viewers/                 # Read-only data feeds
```

## Built With

- **Phi-3 3.8B** via Ollama — local inference, zero API cost
- **Python** — single-file runtime, no framework dependencies
- Built while competing in [Parameter Golf](https://github.com/openai/parameter-golf) (beat SOTA with PR #977, PR #1031 pending)

## Requirements

- Python 3.10+
- [Ollama](https://ollama.ai) with any model (default: phi3:3.8b-mini-128k-instruct-q4_K_M)
- Any GPU with 4GB+ VRAM (runs on RTX 4070, Apple Silicon, etc.)

## License

MIT
