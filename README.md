# Resume Extractor

Drop a resume PDF in a folder, get back structured JSON with skills, companies, total years of experience, and LinkedIn URL — powered by the Claude API.

## Why

Manually parsing resumes is slow, and traditional regex/rule-based parsers break on every new layout. An LLM handles weird formatting, multi-column layouts, and inconsistent date conventions out of the box.

## What it extracts

| Field | Type | Description |
|---|---|---|
| `linkedin_url` | string \| null | Normalized full LinkedIn URL |
| `skills` | string[] | Deduplicated technical & professional skills |
| `companies` | string[] | Employers, most recent first |
| `total_years_experience` | number \| null | Sum of professional experience in years |

See [`examples/sample_output.json`](examples/sample_output.json) for a full example.

## Setup

```bash
# 1. Clone and enter the repo
git clone https://github.com/<your-username>/resume-extractor.git
cd resume-extractor

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env
# then edit .env and paste your key from https://console.anthropic.com/
```

## Usage

```bash
# Process every PDF in resumes/
python -m src.main

# Or process one specific file
python -m src.main resumes/jane_doe.pdf
```

Each PDF in `resumes/` will produce a matching `<name>.json` in `output/`.

## How it works

```
PDF  →  pypdf (text extraction)  →  Claude API (structured extraction)  →  JSON
```

1. **`src/pdf_reader.py`** — uses `pypdf` to pull raw text from the PDF
2. **`src/extractor.py`** — sends that text to Claude with a system prompt that locks the output to a specific JSON schema
3. **`src/main.py`** — orchestrates the pipeline and writes results to disk

The model is pinned to `claude-sonnet-4-5-20250929` for reproducible behavior. Edit `MODEL` in `src/extractor.py` to switch.

## Limitations

- **Scanned PDFs won't work** — `pypdf` only reads embedded text. For image-only PDFs you'd need OCR (Tesseract). The script raises a clear error in this case.
- **Years of experience is an estimate** — calculated from date ranges in the resume; gaps and overlaps are not specially handled.
- **Costs API credits** — every PDF is one API call. With Sonnet 4.5 a typical resume costs well under a cent.

## Roadmap

- [ ] OCR fallback for scanned PDFs
- [ ] Batch CSV export across multiple resumes
- [ ] Web UI (Streamlit / Gradio)
- [ ] Confidence scores per field

## License

MIT
