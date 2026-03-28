#!/bin/bash
# FLUX Swarm Builder — Quick Setup
# Installs Ollama and pulls the default model

set -e

echo "=== FLUX Swarm Builder Setup ==="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3.10+ required. Install from https://python.org"
    exit 1
fi
echo "Python: $(python3 --version)"

# Check/Install Ollama
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ollama
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        echo "Download Ollama from https://ollama.ai"
        exit 1
    fi
fi
echo "Ollama: $(ollama --version 2>/dev/null || echo 'installed')"

# Pull model
echo "Pulling Phi-3 3.8B (2.4 GB)..."
ollama pull phi3:3.8b-mini-128k-instruct-q4_K_M

echo ""
echo "=== Setup Complete ==="
echo "Start Ollama:  ollama serve"
echo "Run a mission: python3 swarm.py \"Your question here\""
