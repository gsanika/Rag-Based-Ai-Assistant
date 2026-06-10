#!/bin/bash
echo ""
echo "=========================================="
echo "   iPundit AI Document Assistant"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python3 not found. Install from https://python.org"
    exit 1
fi

# Install dependencies
echo "[1/3] Installing dependencies..."
pip3 install -r requirements.txt --quiet

# Start Ollama if installed
if command -v ollama &>/dev/null; then
    echo "[2/3] Starting Ollama in background..."
    ollama serve &>/dev/null &
    sleep 2
else
    echo "[2/3] Ollama not found — fallback mode active."
    echo "      For AI answers: https://ollama.ai | then: ollama pull llama3"
fi

# Launch app
echo "[3/3] Starting iPundit AI Assistant..."
echo ""
echo "  Open: http://localhost:8501"
echo "  Stop: Ctrl+C"
echo ""
streamlit run app/main.py --server.port=8501
