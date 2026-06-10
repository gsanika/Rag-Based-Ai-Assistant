"""
Document Summarizer
Condenses document chunks into readable summaries.
"""

from typing import List, Dict, Any


class Summarizer:
    def __init__(self):
        from utils.llm_handler import LLMHandler
        self.llm = LLMHandler()

    def summarize(self, chunks: List[Dict[str, Any]], style: str = "Concise (5 lines)") -> str:
        if not chunks:
            return "No content found for this document."

        # Take first 8 chunks (most representative) and last 2 (conclusion)
        sample = chunks[:3]
    
        combined = "\n\n".join(c["content"] for c in sample)
        # Trim to ~4000 chars to fit LLM context
        combined = combined[:1000]

        style_instruction = {
            "Concise (5 lines)":     "Provide a concise 5-line summary covering the main topics.",
            "Detailed (bullet points)": "Provide a detailed bullet-point summary with key sections and findings.",
            "Executive Brief":        "Provide an executive brief: Purpose, Key Points, Conclusions, and Action Items.",
        }.get(style, "Summarize the document.")

        prompt_chunks = [{
            "content": combined,
            "metadata": {"source": "document", "page": "1-N"},
        }]

        answer, _ = self.llm.answer(
            f"Summarize this document. {style_instruction}",
            prompt_chunks,
        )
        return answer
