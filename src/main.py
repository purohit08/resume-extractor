"""
Resume Extractor — main entry point.

Drops every PDF in the `resumes/` folder through the pipeline and saves
extracted JSON for each to `output/`.

Usage:
    python -m src.main
    python -m src.main resumes/some_specific_file.pdf
"""
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.pdf_reader import extract_text
from src.extractor import extract_fields

# Load .env so ANTHROPIC_API_KEY is available
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESUMES_DIR = PROJECT_ROOT / "resumes"
OUTPUT_DIR = PROJECT_ROOT / "output"


def process_pdf(pdf_path: Path) -> dict:
    """Run the full pipeline on a single PDF and write its JSON output."""
    print(f"\n→ Processing {pdf_path.name}")

    text = extract_text(pdf_path)
    print(f"  • Extracted {len(text):,} characters of text")

    fields = extract_fields(text)
    print(f"  • Skills found: {len(fields.get('skills', []))}")
    print(f"  • Companies found: {len(fields.get('companies', []))}")
    print(f"  • Years of experience: {fields.get('total_years_experience')}")
    print(f"  • LinkedIn: {fields.get('linkedin_url') or '—'}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / f"{pdf_path.stem}.json"
    out_path.write_text(json.dumps(fields, indent=2))
    print(f"  ✓ Saved → {out_path.relative_to(PROJECT_ROOT)}")

    return fields


def main() -> None:
    # Specific file given on the command line
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        if not target.exists():
            print(f"Error: {target} not found")
            sys.exit(1)
        process_pdf(target)
        return

    # Otherwise process every PDF in resumes/
    if not RESUMES_DIR.exists():
        print(f"Error: {RESUMES_DIR} doesn't exist. Create it and add PDFs.")
        sys.exit(1)

    pdfs = sorted(RESUMES_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {RESUMES_DIR}. Drop some in and re-run.")
        sys.exit(0)

    print(f"Found {len(pdfs)} PDF(s) to process.")
    for pdf in pdfs:
        try:
            process_pdf(pdf)
        except Exception as e:
            print(f"  ✗ Failed: {e}")


if __name__ == "__main__":
    main()
