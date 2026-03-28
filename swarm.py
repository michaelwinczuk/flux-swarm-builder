#!/usr/bin/env python3
"""
FLUX Swarm Builder — Run a multi-agent swarm from a folder.

Usage:
    python swarm.py "Your question here"
    python swarm.py --mission mission.json

The swarm reads its configuration from the current directory:
    constitution.md  — governance rules
    swarm.json       — agent registry + mesh config
    agents/          — agent cartridges, scorecards, audits
    knowledge/       — shared knowledge (md, jsonld)
    mesh/            — capability tokens
    tools/           — shared tools

Requires: Ollama running locally with a model loaded.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

# ─── Configuration ────────────────────────────────────────────────────────

OLLAMA_HOST = os.environ.get("SWARM_OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("SWARM_MODEL", "phi3:3.8b-mini-128k-instruct-q4_K_M")
SWARM_DIR = Path(os.environ.get("SWARM_DIR", "."))


def log(icon: str, msg: str):
    try:
        print(f"\n{icon}  {msg}")
    except UnicodeEncodeError:
        print(f"\n[*] {msg}")


def log_detail(msg: str):
    try:
        print(f"   -> {msg}")
    except UnicodeEncodeError:
        print(f"   -> {msg}")


# ─── Ollama Client ────────────────────────────────────────────────────────

import urllib.request
import urllib.error


def ollama_generate(prompt: str, max_tokens: int = 1024) -> str | None:
    """Call local Ollama. Returns response text or None on failure."""
    body = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1, "num_predict": max_tokens},
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("response", "")
    except (urllib.error.URLError, TimeoutError) as e:
        return None


def ollama_available() -> bool:
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags")
        with urllib.request.urlopen(req, timeout=5):
            return True
    except Exception:
        return False


# ─── Swarm Loader ─────────────────────────────────────────────────────────

def load_swarm(swarm_dir: Path) -> dict:
    """Load swarm configuration from directory."""
    swarm_json = swarm_dir / "swarm.json"
    if not swarm_json.exists():
        print(f"Error: {swarm_json} not found. Are you in a swarm directory?")
        sys.exit(1)
    return json.loads(swarm_json.read_text())


def load_constitution(swarm_dir: Path) -> str:
    """Load swarm constitution."""
    path = swarm_dir / "constitution.md"
    return path.read_text() if path.exists() else ""


def load_agent_cartridges(swarm_dir: Path) -> dict[str, str]:
    """Load all agent cartridge.md files."""
    agents = {}
    agents_dir = swarm_dir / "agents"
    if agents_dir.exists():
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                cartridge = agent_dir / "cartridge.md"
                if cartridge.exists():
                    agents[agent_dir.name] = cartridge.read_text()
    return agents


def load_knowledge(swarm_dir: Path) -> list[str]:
    """Load all knowledge files from knowledge/ + any external library paths.

    Set SWARM_KNOWLEDGE_PATH to load additional .md files from external directories.
    This lets you plug in massive knowledge bases (e.g., 40+ cluster cartridges,
    330K+ node research libraries) while keeping the swarm folder clean.

    Example: SWARM_KNOWLEDGE_PATH=C:/Users/micha/swarm-core/cartridges/clusters
    """
    knowledge = []
    sources = []

    # 1. Local knowledge/ directory (user's files — always loaded)
    knowledge_dir = swarm_dir / "knowledge"
    if knowledge_dir.exists():
        local_files = list(knowledge_dir.rglob("*.md")) + list(knowledge_dir.rglob("*.txt"))
        for f in local_files:
            try:
                knowledge.append(f.read_text(errors="ignore")[:2000])
            except Exception:
                pass
        if local_files:
            sources.append(f"{len(local_files)} local files")

    # 2. External knowledge libraries
    ext_path = os.environ.get("SWARM_KNOWLEDGE_PATH")
    if ext_path:
        for p in ext_path.split(os.pathsep):
            ext_dir = Path(p.strip())
            if ext_dir.exists():
                ext_files = list(ext_dir.rglob("*.md"))
                for f in ext_files:
                    try:
                        knowledge.append(f.read_text(errors="ignore")[:2000])
                    except Exception:
                        pass
                if ext_files:
                    sources.append(f"{len(ext_files)} from {ext_dir.name}/")

    if sources:
        log("📚", f"Knowledge: {', '.join(sources)} ({len(knowledge)} total)")

    return knowledge


def scan_mesh(swarm_dir: Path) -> list[dict]:
    """Scan all capability tokens in the mesh."""
    capabilities = []
    mesh_dir = swarm_dir / "mesh"
    if mesh_dir.exists():
        for f in mesh_dir.rglob("*.capabilities.json"):
            try:
                data = json.loads(f.read_text())
                for cap in data.get("capabilities", []):
                    cap["_agent"] = data.get("agent_id", "unknown")
                    capabilities.append(cap)
            except Exception:
                pass
    return capabilities


# ─── BM25-Style Keyword Search ────────────────────────────────────────────

def keyword_search(query: str, documents: list[str], top_k: int = 30) -> list[tuple[int, float]]:
    """Simple TF-IDF-ish keyword search. Returns (index, score) pairs."""
    import re
    from collections import Counter

    query_terms = set(re.findall(r'[a-z]{3,}', query.lower()))
    if not query_terms:
        return [(i, 1.0) for i in range(min(top_k, len(documents)))]

    scored = []
    for i, doc in enumerate(documents):
        doc_lower = doc.lower()
        doc_terms = Counter(re.findall(r'[a-z]{3,}', doc_lower))
        if not doc_terms:
            continue
        # Score: sum of TF for matching query terms, normalized by doc length
        score = sum(doc_terms.get(t, 0) for t in query_terms)
        if score > 0:
            score = score / (len(doc_terms) ** 0.5)  # length normalization
            scored.append((i, score))

    scored.sort(key=lambda x: -x[1])
    return scored[:top_k]


# ─── Micro-Agents ─────────────────────────────────────────────────────────

def agent_cluster_scout(mission: str, available_knowledge: list[str]) -> list[str]:
    """Two-stage knowledge selection: keyword search (fast) → LLM refinement (smart)."""
    log("🔍", "ClusterScout selecting relevant knowledge...")
    start = time.time()

    if not available_knowledge:
        log_detail("No knowledge files found")
        return []

    # Stage 1: Fast keyword search over ALL files (no LLM needed)
    keyword_hits = keyword_search(mission, available_knowledge, top_k=50)
    if not keyword_hits:
        log_detail("No keyword matches — using first 20 files")
        return available_knowledge[:20]

    log_detail(f"Keyword search: {len(keyword_hits)} hits from {len(available_knowledge)} files")

    # Stage 2: LLM refines the top keyword hits
    top_docs = [(available_knowledge[i], score) for i, score in keyword_hits[:30]]
    summaries = []
    for j, (doc, score) in enumerate(top_docs):
        first_lines = doc.strip().split("\n")[:3]
        preview = " | ".join(line.strip() for line in first_lines if line.strip())[:120]
        summaries.append(f"{j+1}. [{score:.2f}] {preview}")

    prompt = (
        "You are a knowledge selector. From these keyword-matched sources, "
        "pick the 10-15 MOST relevant for this mission.\n\n"
        f"Mission: {mission[:500]}\n\n"
        f"Sources:\n" + "\n".join(summaries) + "\n\n"
        "Return JSON: {\"selected\": [1, 3, 5, ...]}"
    )

    resp = ollama_generate(prompt, 256)
    elapsed = time.time() - start

    if resp:
        try:
            parsed = json.loads(resp)
            indices = [i - 1 for i in parsed.get("selected", []) if 0 < i <= len(top_docs)]
            selected = [top_docs[i][0] for i in indices]
            log_detail(f"LLM refined to {len(selected)} sources ({elapsed:.1f}s)")
            return selected
        except Exception:
            pass

    # Fallback: use top keyword matches directly
    log_detail(f"Using top {min(15, len(top_docs))} keyword matches ({elapsed:.1f}s)")
    return [doc for doc, _ in top_docs[:15]]


def agent_query_expander(mission: str) -> list[str]:
    """Generate expanded search terms for deeper knowledge retrieval."""
    log("🔎", "QueryExpander generating search terms...")
    start = time.time()

    prompt = (
        "You are a search term expander. Generate 5-10 additional search terms "
        "for finding knowledge relevant to this mission. Think: synonyms, related concepts, "
        "technical terms.\n\n"
        f"Mission: {mission[:300]}\n\n"
        "Return JSON: {\"terms\": [\"term1\", \"term2\", ...]}"
    )

    resp = ollama_generate(prompt, 256)
    elapsed = time.time() - start

    if resp:
        try:
            parsed = json.loads(resp)
            terms = parsed.get("terms", [])
            log_detail(f"{len(terms)} terms: {', '.join(terms[:5])}... ({elapsed:.1f}s)")
            return terms
        except Exception:
            pass

    log_detail(f"No expansion ({elapsed:.1f}s)")
    return []


def agent_specialist(name: str, question: str, knowledge_context: str) -> dict:
    """Run a specialist agent — one question, one focused answer."""
    start = time.time()

    prompt = (
        f"You are a specialist analyst. Your focus: {question}\n\n"
        f"Available knowledge:\n{knowledge_context[:4000]}\n\n"
        "Based ONLY on the knowledge provided, answer the question. "
        "Be specific and cite sources. If the knowledge doesn't cover this, say so.\n\n"
        "Return JSON: {{\"findings\": \"your analysis\", \"confidence\": 0.0-1.0, "
        "\"sources_used\": 0}}"
    )

    resp = ollama_generate(prompt, 512)
    elapsed = time.time() - start

    if resp:
        try:
            parsed = json.loads(resp)
            findings = parsed.get("findings", "No findings")
            confidence = parsed.get("confidence", 0.0)
            return {
                "agent": name,
                "question": question,
                "findings": findings,
                "confidence": confidence,
                "elapsed_ms": int(elapsed * 1000),
            }
        except Exception:
            pass

    return {
        "agent": name,
        "question": question,
        "findings": "Agent failed to produce results",
        "confidence": 0.0,
        "elapsed_ms": int(elapsed * 1000),
    }


def agent_synthesis(mission: str, specialist_results: list[dict], constitution: str) -> str:
    """Synthesize all specialist findings into a coherent report."""
    log("🎯", "Synthesis agent building final report...")
    start = time.time()

    findings_text = ""
    for r in specialist_results:
        findings_text += f"\n## {r['agent']} (confidence: {r['confidence']})\n"
        findings_text += f"**Question:** {r['question']}\n"
        findings_text += f"**Findings:** {r['findings']}\n"

    prompt = (
        f"You are a synthesis agent. Combine these specialist findings into a coherent report.\n\n"
        f"Constitution rules:\n{constitution[:500]}\n\n"
        f"Mission: {mission}\n\n"
        f"Specialist findings:\n{findings_text[:4000]}\n\n"
        "Produce a clear, actionable synthesis. Identify: (1) key findings, "
        "(2) contradictions between specialists, (3) gaps in knowledge, "
        "(4) recommended next steps.\n\n"
        "Return JSON: {{\"synthesis\": \"...\", \"contradictions\": [...], "
        "\"gaps\": [...], \"next_steps\": [...]}}"
    )

    resp = ollama_generate(prompt, 1024)
    elapsed = time.time() - start
    log_detail(f"Synthesis complete ({elapsed:.1f}s)")

    if resp:
        try:
            parsed = json.loads(resp)
            return parsed
        except Exception:
            return {"synthesis": resp, "contradictions": [], "gaps": [], "next_steps": []}

    return {"synthesis": "Synthesis failed", "contradictions": [], "gaps": [], "next_steps": []}


# ─── Mission Runner ───────────────────────────────────────────────────────

SPECIALISTS = [
    ("causes", "Why does this problem exist? What are the root causes?"),
    ("requires", "What do we need to solve this? What are the dependencies?"),
    ("solves", "What solutions exist? What has been tried?"),
    ("contradicts", "What breaks the proposed solutions? What are the risks?"),
    ("tradeoff", "What does each solution cost? What are the tradeoffs?"),
    ("systems", "How do the pieces connect? What is the system architecture?"),
]


def run_mission(mission: str, swarm_dir: Path):
    """Execute a full swarm mission."""
    mission_start = time.time()
    mission_id = f"mission-{int(time.time())}"

    print("=" * 60)
    print(f"  FLUX SWARM — Mission: {mission_id}")
    print(f"  {mission[:80]}...")
    print("=" * 60)

    # Load swarm
    swarm_config = load_swarm(swarm_dir)
    constitution = load_constitution(swarm_dir)
    cartridges = load_agent_cartridges(swarm_dir)
    knowledge = load_knowledge(swarm_dir)
    capabilities = scan_mesh(swarm_dir)

    log("📋", f"Swarm: {swarm_config.get('name', 'unnamed')}")
    log_detail(f"{len(cartridges)} agents, {len(knowledge)} knowledge files, {len(capabilities)} capabilities")

    # Check Ollama
    if not ollama_available():
        print("\n❌  Ollama not running. Start it with: ollama serve")
        sys.exit(1)
    log("🤖", f"Local model: {OLLAMA_MODEL} @ {OLLAMA_HOST}")

    # Step 1: ClusterScout — first pass keyword + LLM selection
    relevant_knowledge = agent_cluster_scout(mission, knowledge)

    # Step 2: QueryExpander — generate search terms
    expanded_terms = agent_query_expander(mission)
    enriched_mission = mission + " " + " ".join(expanded_terms)

    # Step 2b: Second search pass with expanded terms (catches what first pass missed)
    if expanded_terms and knowledge:
        log("🔍", "Second pass with expanded terms...")
        expanded_query = " ".join(expanded_terms)
        second_hits = keyword_search(expanded_query, knowledge, top_k=20)
        for idx, score in second_hits:
            doc = knowledge[idx]
            if doc not in relevant_knowledge:
                relevant_knowledge.append(doc)
        log_detail(f"Total knowledge sources: {len(relevant_knowledge)}")

    # Build context for specialists — truncate each source to keep total manageable
    # Phi-3 3.8B handles ~4000 chars of context well, more causes timeouts
    trimmed = [doc[:800] for doc in relevant_knowledge[:20]]
    knowledge_context = "\n---\n".join(trimmed)

    # Step 3: Run specialists
    log("🧠", f"Running {len(SPECIALISTS)} specialist agents...")
    specialist_results = []
    for name, question in SPECIALISTS:
        focused_q = question.replace("this problem", f"the problem of: {mission[:100]}")
        result = agent_specialist(name, focused_q, knowledge_context)
        specialist_results.append(result)
        status = "✓" if result["confidence"] > 0.3 else "○"
        print(f"   {status} {name}: {result['findings'][:80]}... ({result['elapsed_ms']}ms)")

    # Step 4: Synthesis
    synthesis = agent_synthesis(mission, specialist_results, constitution)

    # Save output
    output_dir = swarm_dir / "output" / mission_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write report
    report = f"# Mission Report: {mission_id}\n\n"
    report += f"**Mission:** {mission}\n\n"
    report += f"**Date:** {datetime.now(timezone.utc).isoformat()}\n\n"
    report += f"**Swarm:** {swarm_config.get('name', 'unnamed')}\n\n"
    report += "---\n\n"
    report += f"## Synthesis\n\n{synthesis.get('synthesis', 'N/A')}\n\n"

    if synthesis.get("contradictions"):
        report += "## Contradictions\n\n"
        for c in synthesis["contradictions"]:
            report += f"- {c}\n"
        report += "\n"

    if synthesis.get("gaps"):
        report += "## Knowledge Gaps\n\n"
        for g in synthesis["gaps"]:
            report += f"- {g}\n"
        report += "\n"

    if synthesis.get("next_steps"):
        report += "## Recommended Next Steps\n\n"
        for s in synthesis["next_steps"]:
            report += f"- {s}\n"
        report += "\n"

    report += "---\n\n## Specialist Reports\n\n"
    for r in specialist_results:
        report += f"### {r['agent']} (confidence: {r['confidence']})\n\n"
        report += f"**Question:** {r['question']}\n\n"
        report += f"**Findings:** {r['findings']}\n\n"

    (output_dir / "report.md").write_text(report)
    (output_dir / "raw.json").write_text(json.dumps({
        "mission_id": mission_id,
        "mission": mission,
        "specialists": specialist_results,
        "synthesis": synthesis,
        "expanded_terms": expanded_terms,
        "knowledge_sources": len(relevant_knowledge),
    }, indent=2))

    # Update agent scorecards
    for r in specialist_results:
        agent_dir = swarm_dir / "agents"
        # Update audit for any matching agent
        for a in agent_dir.iterdir() if agent_dir.exists() else []:
            audit_path = a / "audit.json"
            if audit_path.exists():
                try:
                    audit = json.loads(audit_path.read_text())
                    audit.append({
                        "mission_id": mission_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "action": "specialist_analysis",
                    })
                    audit_path.write_text(json.dumps(audit, indent=2))
                except Exception:
                    pass

    elapsed = time.time() - mission_start

    print("\n" + "=" * 60)
    log("✅", f"Mission complete in {elapsed:.1f}s")
    log_detail(f"Report: {output_dir / 'report.md'}")
    log_detail(f"Raw data: {output_dir / 'raw.json'}")
    print("=" * 60)


# ─── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="FLUX Swarm Builder — Run a multi-agent swarm")
    parser.add_argument("mission", nargs="?", help="Mission statement (question to investigate)")
    parser.add_argument("--dir", default=".", help="Swarm directory (default: current)")
    args = parser.parse_args()

    swarm_dir = Path(args.dir).resolve()

    if not args.mission:
        print("FLUX Swarm Builder")
        print(f"Swarm directory: {swarm_dir}")
        config = load_swarm(swarm_dir)
        print(f"Swarm: {config.get('name', 'unnamed')}")
        agents = load_agent_cartridges(swarm_dir)
        print(f"Agents: {', '.join(agents.keys()) if agents else 'none'}")
        caps = scan_mesh(swarm_dir)
        print(f"Capabilities: {len(caps)}")
        print(f"\nUsage: python swarm.py \"Your question here\"")
        return

    run_mission(args.mission, swarm_dir)


if __name__ == "__main__":
    main()
