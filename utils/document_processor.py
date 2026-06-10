"""
Document Processor
Handles PDF, DOCX, TXT loading + chunking.
"""

import os
import re
from typing import List, Dict, Any
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    # ── Public ────────────────────────────────────────────────────────────────
    def process(self, file_path: str, file_name: str) -> List[Dict[str, Any]]:
        """Load a file, extract text, split into chunks with metadata."""
        ext = os.path.splitext(file_name)[1].lower()

        if ext == ".pdf":
            pages = self._load_pdf(file_path)
        elif ext == ".docx":
            pages = self._load_docx(file_path)
        elif ext == ".txt":
            pages = self._load_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        chunks = []
        for page_num, text in pages:
            if not text.strip():
                continue
            splits = self.splitter.split_text(text)
            for i, chunk_text in enumerate(splits):
                if chunk_text.strip():
                    chunks.append({
                        "content": chunk_text.strip(),
                        "metadata": {
                            "source": file_name,
                            "page": page_num,
                            "chunk_index": i,
                        },
                    })
        return chunks

    # ── Loaders ───────────────────────────────────────────────────────────────
    def _load_pdf(self, path: str) -> List[tuple]:
        """Returns list of (page_number, text)."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(path)
            pages = []
            for i, page in enumerate(doc, start=1):
                pages.append((i, page.get_text()))
            doc.close()
            return pages
        except ImportError:
            pass

        # Fallback: PyPDF2
        try:
            import PyPDF2
            pages = []
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(reader.pages, start=1):
                    pages.append((i, page.extract_text() or ""))
            return pages
        except ImportError:
            pass

        # Last resort: pdfplumber
        try:
            import pdfplumber
            pages = []
            with pdfplumber.open(path) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    pages.append((i, page.extract_text() or ""))
            return pages
        except Exception as e:
            raise RuntimeError(f"PDF extraction failed. Install PyMuPDF: pip install pymupdf. Error: {e}")

    def _load_docx(self, path: str) -> List[tuple]:
        try:
            import docx2txt
            text = docx2txt.process(path)
            return [(1, text)]
        except ImportError:
            pass

        try:
            from docx import Document
            doc = Document(path)
            text = "\n".join(p.text for p in doc.paragraphs)
            return [(1, text)]
        except Exception as e:
            raise RuntimeError(f"DOCX extraction failed. Install python-docx: pip install python-docx. Error: {e}")

    def _load_txt(self, path: str) -> List[tuple]:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        # Split by natural page breaks if present
        if "\f" in text:
            pages = [(i + 1, p) for i, p in enumerate(text.split("\f"))]
        else:
            # Treat every ~3000 chars as a "page"
            chunk_size = 3000
            pages = []
            for i in range(0, len(text), chunk_size):
                pages.append((i // chunk_size + 1, text[i:i + chunk_size]))
        return pages
