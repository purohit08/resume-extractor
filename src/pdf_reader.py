"""PDF text extraction using pypdf."""
from pathlib import Path
from pypdf import PdfReader


def extract_text(pdf_path: str | Path) -> str:
    """
    Extract all text from a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Concatenated text from all pages.

    Raises:
        FileNotFoundError: If the PDF doesn't exist.
        ValueError: If no text could be extracted (likely a scanned/image PDF).
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_parts.append(page_text)

    full_text = "\n".join(text_parts).strip()

    if not full_text:
        raise ValueError(
            f"No text extracted from {pdf_path.name}. "
            "It may be a scanned/image PDF — OCR would be needed."
        )

    return full_text
