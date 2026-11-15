"""
Text extraction utilities for document ingestion.

Phase 4 - Extract text from PDF, DOCX, TXT, Markdown, and CSV files.
"""

import logging
import os
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None

try:
    import markdown
except ImportError:
    markdown = None

try:
    import csv
except ImportError:
    csv = None


class ExtractionError(Exception):
    pass


def extract_pdf(file_path, max_pages=None):
    if PdfReader is None:
        raise ExtractionError("pypdf is not installed.")
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)
    extracted = []
    pages_processed = 0
    for i, page in enumerate(reader.pages):
        if max_pages and pages_processed >= max_pages:
            break
        try:
            text = page.extract_text()
            if text:
                extracted.append("--- Page " + str(i + 1) + " ---" + chr(10) + text)
                pages_processed += 1
        except Exception as e:
            logger.warning("Failed to extract text from page " + str(i + 1) + ": " + str(e))
            extracted.append("--- Page " + str(i + 1) + " ---" + chr(10) + "[Unable to extract text]")
    return chr(10).join(extracted), total_pages


def extract_docx(file_path):
    if docx is None:
        raise ExtractionError("python-docx is not installed.")
    doc = docx.Document(file_path)
    paragraphs = []
    for para in doc.paragraphs:
        if para.text.strip():
            if para.style.name.startswith("Heading"):
                paragraphs.append("[" + para.style.name + "] " + para.text)
            else:
                paragraphs.append(para.text)
    for table in doc.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            paragraphs.append(" | ".join(cells))
    return chr(10).join(paragraphs)


def extract_txt(file_path):
    for encoding in ["utf-8", "latin-1", "ascii"]:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except Exception:
            continue
    raise ExtractionError("Unable to decode text file.")


def extract_md(file_path):
    if markdown is None:
        raise ExtractionError("markdown is not installed.")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    html = markdown.markdown(content, extensions=["extra", "toc"])
    lines = []
    for line in html.split(chr(10)):
        if line.startswith("<h1"):
            lines.append(chr(10) + "# " + line.split(">", 1)[1].rsplit("<", 1)[0])
        elif line.startswith("<h2"):
            lines.append(chr(10) + "## " + line.split(">", 1)[1].rsplit("<", 1)[0])
        elif line.startswith("<h3"):
            lines.append(chr(10) + "### " + line.split(">", 1)[1].rsplit("<", 1)[0])
        elif line.startswith("<h4"):
            lines.append(chr(10) + "#### " + line.split(">", 1)[1].rsplit("<", 1)[0])
        elif line.startswith("<h5"):
            lines.append(chr(10) + "##### " + line.split(">", 1)[1].rsplit("<", 1)[0])
        elif line.startswith("<h6"):
            lines.append(chr(10) + "###### " + line.split(">", 1)[1].rsplit("<", 1)[0])
        elif line.startswith("<p"):
            content_start = line.find(">", 1) + 1
            content_end = line.rfind("</p")
            if content_start > 0 and content_end > content_start:
                lines.append(line[content_start:content_end])
            elif content_start > 0:
                lines.append(line[content_start:])
        elif line.startswith("<li"):
            content_start = line.find(">", 1) + 1
            content_end = line.rfind("</li")
            if content_start > 0 and content_end > content_start:
                lines.append("- " + line[content_start:content_end])
            elif content_start > 0:
                lines.append("- " + line[content_start:])
        elif line.startswith("<b>") or line.startswith("<strong"):
            content_start = line.find(">", 1) + 1
            content_end = line.rfind("</b>") if "</b>" in line else line.rfind("</strong>")
            if content_end > content_start:
                lines.append(line[content_start:content_end])
    return chr(10).join(lines)


def extract_csv(file_path, max_rows=1000):
    rows = []
    with open(file_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header:
            rows.append(" | ".join(header))
        count = 0
        for row in reader:
            if count >= max_rows:
                rows.append("... (truncated after " + str(max_rows) + " rows)")
                break
            rows.append(" | ".join(row))
            count += 1
    return chr(10).join(rows)


def extract_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        text, pages = extract_pdf(file_path)
        return text, "pdf (" + str(pages) + " pages)"
    elif ext == ".docx":
        return extract_docx(file_path), "docx"
    elif ext == ".txt":
        return extract_txt(file_path), "txt"
    elif ext == ".md":
        return extract_md(file_path), "md"
    elif ext == ".csv":
        return extract_csv(file_path), "csv"
    else:
        raise ExtractionError("Unsupported file type: " + ext + ". Supported: .pdf, .docx, .txt, .md, .csv")
