import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.document_processor import DocumentProcessor
from utils.vector_store import VectorStore
from utils.llm_handler import LLMHandler
from utils.summarizer import Summarizer

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background: #0f1117; }

    /* Header */
    .header-bar {
        background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
        border: 1px solid #2d3748;
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .header-title { font-size: 28px; font-weight: 700; color: #e2e8f0; margin: 0; }
    .header-sub   { font-size: 14px; color: #718096; margin: 4px 0 0; }
    .badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Chat bubbles */
    .chat-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 14px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
        font-size: 14px;
        line-height: 1.6;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }
    .chat-assistant {
        background: #1a1f2e;
        border: 1px solid #2d3748;
        color: #e2e8f0;
        padding: 14px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 85%;
        font-size: 14px;
        line-height: 1.7;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .source-tag {
        display: inline-block;
        background: #2d3748;
        color: #68d391;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        margin: 4px 3px 0;
        font-weight: 500;
    }

    /* Upload zone */
    .upload-zone {
        border: 2px dashed #4a5568;
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        background: #1a1f2e;
        transition: border-color 0.3s;
    }

    /* Stats cards */
    .stat-card {
        background: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .stat-number { font-size: 28px; font-weight: 700; color: #667eea; }
    .stat-label  { font-size: 12px; color: #718096; margin-top: 4px; }

    /* Doc item */
    .doc-item {
        background: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 10px 14px;
        margin: 6px 0;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 13px;
        color: #a0aec0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #0d1117 !important; }
    [data-testid="stSidebar"] .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px;
        font-weight: 600;
        transition: opacity 0.2s;
    }
    [data-testid="stSidebar"] .stButton>button:hover { opacity: 0.85; }

    /* Input */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background: #1a1f2e !important;
        border: 1px solid #4a5568 !important;
        color: #e2e8f0 !important;
        border-radius: 10px !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background: #1a1f2e; border-radius: 12px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { color: #a0aec0 !important; border-radius: 8px; }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #1a1f2e; }
    ::-webkit-scrollbar-thumb { background: #4a5568; border-radius: 3px; }

    /* Thinking indicator */
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
    .thinking { animation: pulse 1.5s infinite; color: #667eea; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "messages"          not in st.session_state: st.session_state.messages = []
if "processed_docs"    not in st.session_state: st.session_state.processed_docs = []
if "vector_store_ready" not in st.session_state: st.session_state.vector_store_ready = False
if "total_chunks"      not in st.session_state: st.session_state.total_chunks = 0

# ── Cached Resources ──────────────────────────────────────────────────────────
@st.cache_resource
def get_vector_store():
    return VectorStore()

@st.cache_resource
def get_llm_handler():
    return LLMHandler()

@st.cache_resource
def get_summarizer():
    return Summarizer()

vs       = get_vector_store()
llm      = get_llm_handler()
summarizer = get_summarizer()
doc_proc = DocumentProcessor()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-bar">
    <div style="font-size:40px">🧠</div>
    <div>
        <div class="header-title">AI Assistant</div>
        <div class="header-sub">RAG-powered document intelligence — ask anything about your uploaded documents</div>
    </div>
    <div style="margin-left:auto"><span class="badge">RAG • LLM • Vector Search</span></div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Document Manager")
    st.markdown("---")

    uploaded_files = st.file_uploader(
        "Upload Documents",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="PDF, Word, or Text files",
    )

    if uploaded_files:
        if st.button("⚡ Process Documents", use_container_width=True):
            progress = st.progress(0)
            status   = st.empty()
            all_chunks = []

            for i, uf in enumerate(uploaded_files):
                status.markdown(f"<div class='thinking'>Processing {uf.name}…</div>", unsafe_allow_html=True)
                save_path = os.path.join("data/uploads", uf.name)
                os.makedirs("data/uploads", exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(uf.read())

                try:
                    chunks = doc_proc.process(save_path, uf.name)
                    all_chunks.extend(chunks)
                    if uf.name not in st.session_state.processed_docs:
                        st.session_state.processed_docs.append(uf.name)
                except Exception as e:
                    st.error(f"Error: {uf.name} — {e}")

                progress.progress((i + 1) / len(uploaded_files))

            if all_chunks:
                status.markdown("<div class='thinking'>Building vector index…</div>", unsafe_allow_html=True)
                vs.add_documents(all_chunks)
                st.session_state.vector_store_ready = True
                st.session_state.total_chunks += len(all_chunks)
                status.empty()
                progress.empty()
                st.success(f"✅ {len(uploaded_files)} doc(s) indexed — {len(all_chunks)} chunks")

    st.markdown("---")
    st.markdown("### 📊 Stats")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-number">{len(st.session_state.processed_docs)}</div>
            <div class="stat-label">Documents</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-number">{st.session_state.total_chunks}</div>
            <div class="stat-label">Chunks</div></div>""", unsafe_allow_html=True)

    if st.session_state.processed_docs:
        st.markdown("### 📄 Indexed Files")
        for doc in st.session_state.processed_docs:
            ext = doc.split(".")[-1].upper()
            icon = {"PDF":"📕","DOCX":"📘","TXT":"📄"}.get(ext,"📄")
            st.markdown(f"""<div class="doc-item">{icon} {doc}</div>""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🗑️ Clear All Data", use_container_width=True):
        vs.clear()
        st.session_state.messages = []
        st.session_state.processed_docs = []
        st.session_state.vector_store_ready = False
        st.session_state.total_chunks = 0
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px;color:#4a5568;text-align:center">
    Powered by LangChain · FAISS · Ollama<br>
    <b style="color:#667eea">RAG System v1.0</b>
    </div>""", unsafe_allow_html=True)

# ── Main Tabs ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["💬 Chat Assistant", "📋 Summarizer", "🔍 Smart Search"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CHAT
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    if not st.session_state.vector_store_ready:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#4a5568">
            <div style="font-size:64px;margin-bottom:16px">📂</div>
            <div style="font-size:20px;font-weight:600;color:#718096">No documents indexed yet</div>
            <div style="font-size:14px;margin-top:8px">Upload PDF, DOCX, or TXT files using the sidebar to get started.</div>
        </div>""", unsafe_allow_html=True)
    else:
        # Chat history
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    sources_html = ""
                    if msg.get("sources"):
                        sources_html = "<div style='margin-top:10px'>" + "".join(
                            f'<span class="source-tag">📄 {s}</span>'
                            for s in msg["sources"]
                        ) + "</div>"
                    st.markdown(
                        f'<div class="chat-assistant">🤖 {msg["content"]}{sources_html}</div>',
                        unsafe_allow_html=True,
                    )

        # Input
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_question = st.text_input(
                "Ask a question",
                placeholder="e.g. How do I create a piping route?",
                label_visibility="collapsed",
                key="chat_input",
            )
        with col_btn:
            send = st.button("Send ➤", use_container_width=True)

        if send and user_question.strip():
            st.session_state.messages.append({"role": "user", "content": user_question})

            with st.spinner("🔍 Searching documents…"):
                # Build conversation history for context
                history = [
                    (m["content"], st.session_state.messages[i+1]["content"])
                    for i, m in enumerate(st.session_state.messages[:-1])
                    if m["role"] == "user" and i+1 < len(st.session_state.messages)
                ]

                results = vs.search(user_question, k=4)
                answer, sources = llm.answer(user_question, results, history)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
            })
            st.rerun()

        if st.session_state.messages:
            if st.button("🗑️ Clear Chat", key="clear_chat"):
                st.session_state.messages = []
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SUMMARIZER
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 📋 Document Summarizer")
    st.markdown("Get a concise summary of any uploaded document instantly.")

    if not st.session_state.processed_docs:
        st.info("Upload and process documents first.")
    else:
        sel_doc = st.selectbox("Choose a document to summarize", st.session_state.processed_docs)
        style   = st.radio("Summary Style", ["Concise (5 lines)", "Detailed (bullet points)", "Executive Brief"], horizontal=True)

        if st.button("✨ Generate Summary", use_container_width=False):
            with st.spinner("Summarizing…"):
                doc_chunks = vs.get_doc_chunks(sel_doc)
                if doc_chunks:
                    summary = summarizer.summarize(doc_chunks, style)
                    st.markdown(f"""
                    <div class="chat-assistant">
                    <b>📄 Summary — {sel_doc}</b><br><br>{summary}
                    </div>""", unsafe_allow_html=True)
                else:
                    st.warning("No chunks found for this document. Please re-process it.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SMART SEARCH
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🔍 Smart Semantic Search")
    st.markdown("Find all relevant passages across your documents.")

    if not st.session_state.vector_store_ready:
        st.info("Upload and process documents first.")
    else:
        search_query = st.text_input("Search query", placeholder="e.g. Pipe Routing, Equipment Configuration…")
        top_k = st.slider("Number of results", 3, 15, 5)

        if st.button("🔍 Search", use_container_width=False) and search_query.strip():
            with st.spinner("Searching…"):
                results = vs.search(search_query, k=top_k)

            st.markdown(f"**Found {len(results)} relevant passages:**")
            for i, r in enumerate(results, 1):
                score_pct = round((1 - r.get("score", 0)) * 100, 1)
                score_pct = max(0, min(100, score_pct))
                src  = r["metadata"].get("source", "Unknown")
                page = r["metadata"].get("page", "?")
                st.markdown(f"""
                <div class="chat-assistant" style="margin:8px 0">
                    <div style="display:flex;justify-content:space-between;margin-bottom:8px">
                        <span style="color:#667eea;font-weight:600">Result {i}</span>
                        <span class="source-tag">📄 {src} · Page {page}</span>
                    </div>
                    {r["content"][:500]}{"…" if len(r["content"])>500 else ""}
                </div>""", unsafe_allow_html=True)
