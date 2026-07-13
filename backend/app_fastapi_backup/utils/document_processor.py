import io
import re
from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from pypdf import PdfReader


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_from_pdf(content: bytes) -> tuple[str, int]:
    text_parts = []
    page_count = 0
    try:
        reader = PdfReader(io.BytesIO(content))
        page_count = len(reader.pages)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text)
    except Exception:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_parts.append(page_text)
    return clean_text("\n\n".join(text_parts)), page_count


def extract_from_docx(content: bytes) -> tuple[str, int]:
    doc = DocxDocument(io.BytesIO(content))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return clean_text("\n".join(paragraphs)), 1


def extract_from_text(content: bytes) -> tuple[str, int]:
    text = content.decode("utf-8", errors="ignore")
    return clean_text(text), 1


def extract_from_html(content: bytes) -> tuple[str, int]:
    soup = BeautifulSoup(content, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    return clean_text(text), 1


def extract_document(content: bytes, filename: str) -> tuple[str, int]:
    ext = Path(filename).suffix.lower()
    extractors = {
        ".pdf": extract_from_pdf,
        ".docx": extract_from_docx,
        ".doc": extract_from_docx,
        ".txt": extract_from_text,
        ".md": extract_from_text,
        ".csv": extract_from_text,
        ".html": extract_from_html,
        ".htm": extract_from_html,
    }
    extractor = extractors.get(ext, extract_from_text)
    return extractor(content)
