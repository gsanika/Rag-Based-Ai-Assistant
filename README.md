# 🧠 AI Document Assistant
### RAG-Powered Intelligent Document Q&A System

---

## What is This?

An AI assistant that reads your company's internal documents (PDFs, Word files, text files) and answers employee questions instantly — using **RAG (Retrieval-Augmented Generation)**.

No more manual searching through 500-page manuals.

---

## Features

| Feature | Description |
|---------|-------------|
| 📄 **Multi-format Upload** | PDF, DOCX, TXT support |
| 💬 **AI Chat** | Ask questions in plain English |
| 📋 **Summarizer** | Condense long documents to key points |
| 🔍 **Smart Search** | Semantic search across all documents |
| 🧠 **Conversation Memory** | Remembers previous questions in session |
| 📍 **Source Citations** | Every answer shows document + page number |

---

## Quick Start

### Windows
```bash
# Double-click start.bat
# OR run in terminal:
start.bat
```

### Mac / Linux
```bash
chmod +x start.sh
./start.sh
```

### Manual
```bash
pip install -r requirements.txt
streamlit run app/main.py
```

Open browser: **http://localhost:8501**

---

## Setup for Best AI Answers

### Option 1: Groq (Free Cloud API, Recommended) ⚡
Groq is FREE and incredibly fast for RAG workloads. No GPU needed!

```bash
# 1. Get free Groq API key
# Visit: https://console.groq.com/keys
# Sign up and generate an API key

# 2. Set environment variable
export GROQ_API_KEY=gsk_your_key_here    # Linux/Mac
set GROQ_API_KEY=gsk_your_key_here        # Windows (Command Prompt)
$env:GROQ_API_KEY="gsk_your_key_here"     # Windows (PowerShell)

# 3. Run the app
streamlit run app/main.py
```

**Available Models:**
- `mixtral-8x7b-32768` - Fast & powerful (default)
- `llama2-70b-4096` - Very accurate

### Option 2: Ollama (Free, Local, No Internet Required)
```bash
# 1. Install Ollama
# Windows/Mac: https://ollama.ai/download
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull a model
ollama pull llama3         # Best quality (4.7GB)
ollama pull mistral        # Faster (4.1GB)
ollama pull phi3           # Lightweight (2.3GB)

# 3. Start Ollama
ollama serve
```

### Option 3: OpenAI (Paid)
```bash
# Set environment variable
export OPENAI_API_KEY=sk-your-key-here   # Linux/Mac
set OPENAI_API_KEY=sk-your-key-here       # Windows
```

### Option 4: Fallback (No Setup Required)
Without Groq/Ollama/OpenAI, the system uses **keyword extraction** from the documents. Answers will be less polished but still functional.

---

## Architecture

```
User Uploads Document
        ↓
   Document Loader
   (PDF/DOCX/TXT)
        ↓
   Text Extraction
        ↓
   Text Chunking
   (800 chars, 150 overlap)
        ↓
   Sentence Embeddings
   (all-MiniLM-L6-v2)
        ↓
   FAISS Vector Index
        ↓
   User Asks Question
        ↓
   Similarity Search
   (Top-K chunks)
        ↓
   LLM (Groq/Ollama/OpenAI)
        ↓
   Answer + Sources
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | Python 3.9+ |
| AI Framework | LangChain |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector DB | FAISS |
| LLM | Groq API / Ollama / OpenAI |
| PDF | PyMuPDF |
| Word | python-docx |

---

## Project Structure

```
rag-assistant/
├── app/
│   └── main.py              # Streamlit UI
├── utils/
│   ├── document_processor.py # PDF/DOCX/TXT loader + chunker
│   ├── vector_store.py       # FAISS embeddings + search
│   ├── llm_handler.py        # Groq / Ollama / OpenAI / fallback
│   └── summarizer.py         # Document summarization
├── data/
│   ├── uploads/              # Uploaded files (auto-created)
│   ├── vectorstore/          # FAISS index (auto-created)
│   └── sample_Smart3D_Manual.txt  # Test document
├── .streamlit/
│   └── config.toml           # Theme configuration
├── requirements.txt
├── start.bat                 # Windows launcher
├── start.sh                  # Mac/Linux launcher
└── README.md
```

---

## Usage Guide

### 1. Upload Documents
- Click sidebar → "Upload Documents"
- Select PDF/DOCX/TXT files
- Click **"⚡ Process Documents"**
- Wait for indexing to complete

### 2. Ask Questions
- Go to **Chat Assistant** tab
- Type your question naturally
- Example: *"How do I create a piping route?"*
- See answer with page references

### 3. Summarize
- Go to **Summarizer** tab
- Select a document
- Choose summary style
- Get instant summary

### 4. Search
- Go to **Smart Search** tab
- Enter search terms
- Find all related passages

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | *(empty)* | Groq API key (optional, recommended) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3` | Ollama model name |
| `OPENAI_API_KEY` | *(empty)* | OpenAI API key (optional) |

---

## Troubleshooting

**Q: "Groq error" when running**
→ Make sure `GROQ_API_KEY` environment variable is set
→ Get API key at: https://console.groq.com/keys

**Q: Answers aren't accurate**
→ Make sure you have uploaded and processed documents
→ Try Groq API for faster, better responses

**Q: PDF text not extracting**
→ Run: `pip install pymupdf`

**Q: DOCX not loading**
→ Run: `pip install python-docx docx2txt`

**Q: Slow performance**
→ Groq is much faster than local Ollama
→ Reduce chunk size in `document_processor.py`

---

## Concepts Demonstrated

- ✅ **RAG** (Retrieval-Augmented Generation)
- ✅ **Vector Embeddings** (Semantic meaning → numbers)
- ✅ **FAISS** (Facebook AI Similarity Search)
- ✅ **LangChain** (AI orchestration)
- ✅ **Prompt Engineering** (System prompts, context injection)
- ✅ **NLP** (Text chunking, similarity search)
- ✅ **Conversation Memory** (Multi-turn context)
- ✅ **Document Processing** (PDF/DOCX/TXT pipelines)

---

## ✅ Why Groq?

| Feature | Groq | Ollama | OpenAI |
|---------|------|--------|--------|
| Speed | ⚡⚡⚡ Fast | ⚡ Slow | ⚡⚡ Medium |
| Cost | Free | Free | Paid |
| GPU Required | No | Yes | No |
| Setup | Easy | Hard | Easy |
| Quality | Excellent | Good | Excellent |
| Internet | Required | No | Required |

---
