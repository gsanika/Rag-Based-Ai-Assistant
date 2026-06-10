"""
LLM Handler
Primary: Ollama (local, free)
Fallback: OpenAI-compatible API
"""

import os
import re
from typing import List, Dict, Any, Tuple


SYSTEM_PROMPT = """You are an expert AI assistant for iPundit, specializing in technical documentation including Smart3D manuals, AutoCAD customization, SOPs, and engineering documents.

Your job is to answer questions ONLY based on the provided document excerpts.

Rules:
1. Answer using ONLY the context provided below.
2. Be precise, structured, and use numbered steps where appropriate.
3. If the answer is not in the context, say: "I couldn't find that information in the uploaded documents."
4. Always mention which document/page you found the answer on.
5. Format answers clearly with headings and bullet points when helpful.
"""


class LLMHandler:
    def __init__(self):
        self.ollama_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        self.openai_key   = os.getenv("OPENAI_API_KEY", "")
        self.backend      = self._detect_backend()

    def _detect_backend(self) -> str:
        """Auto-detect available LLM backend."""
        # Try Ollama first
        try:
            import requests
            r = requests.get(f"{self.ollama_base}/api/tags", timeout=3)
            if r.status_code == 200:
                models = [m["name"] for m in r.json().get("models", [])]
                if models:
                    self.ollama_model = models[0]
                return "ollama"
        except Exception:
            pass

        # Try OpenAI
        if self.openai_key:
            return "openai"

        # Fallback to rule-based extraction
        return "fallback"

    # ── Public ────────────────────────────────────────────────────────────────
    def answer(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]],
        history: List[Tuple[str, str]] = None,
    ) -> Tuple[str, List[str]]:
        """Returns (answer_text, source_list)."""
        if not context_chunks:
            return "No relevant documents found. Please upload documents first.", []

        context_text, sources = self._build_context(context_chunks)

        if self.backend == "ollama":
            answer = self._ask_ollama(question, context_text, history or [])
        elif self.backend == "openai":
            answer = self._ask_openai(question, context_text, history or [])
        else:
            answer = self._fallback_answer(question, context_chunks)

        return answer, sources

    # ── Context Builder ───────────────────────────────────────────────────────
    def _build_context(self, chunks: List[Dict]) -> Tuple[str, List[str]]:
        sources = []
        parts   = []
        for i, c in enumerate(chunks, 1):
            src  = c["metadata"].get("source", "Unknown")
            page = c["metadata"].get("page", "?")
            ref  = f"{src} (Page {page})"
            if ref not in sources:
                sources.append(ref)
            parts.append(f"[Excerpt {i} — {ref}]\n{c['content']}")
        return "\n\n---\n\n".join(parts), sources

    # ── Ollama ────────────────────────────────────────────────────────────────
    def _ask_ollama(self, question: str, context: str, history: List) -> str:
        import requests, json

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for user_msg, assistant_msg in history[-3:]:  # last 3 turns
            messages.append({"role": "user",      "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})

        messages.append({"role": "user", "content": f"""Context from documents:
{context}

Question: {question}

Please answer based only on the context above."""})

        try:
            r = requests.post(
                f"{self.ollama_base}/api/chat",
                json={"model": self.ollama_model, "messages": messages, "stream": False},
                timeout=300,
            )
            data = r.json()
            return data.get("message", {}).get("content", "No response from Ollama.")
        except Exception as e:
            return f"Ollama error: {e}. Make sure Ollama is running: `ollama serve`"

    # ── OpenAI ────────────────────────────────────────────────────────────────
    def _ask_openai(self, question: str, context: str, history: List) -> str:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for user_msg, assistant_msg in history[-3:]:
                messages.append({"role": "user",      "content": user_msg})
                messages.append({"role": "assistant", "content": assistant_msg})
            messages.append({"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"})

            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=800,
                temperature=0.2,
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"OpenAI error: {e}"

    # ── Fallback (no LLM) ─────────────────────────────────────────────────────
    def _fallback_answer(self, question: str, chunks: List[Dict]) -> str:
        """Simple keyword extraction when no LLM is available."""
        keywords = set(re.findall(r"\b\w{4,}\b", question.lower()))
        scored   = []
        for c in chunks:
            text  = c["content"].lower()
            score = sum(1 for kw in keywords if kw in text)
            scored.append((score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[:2]

        if not best or best[0][0] == 0:
            return "I couldn't find relevant information in the uploaded documents for that question."

        answer = "Based on the uploaded documents:\n\n"
        for _, c in best:
            src  = c["metadata"].get("source", "Unknown")
            page = c["metadata"].get("page", "?")
            answer += f"**From {src} (Page {page}):**\n{c['content'][:600]}\n\n"

        answer += "\n\n⚠️ *Note: For better AI answers, install and run Ollama locally: https://ollama.ai*"
        return answer
