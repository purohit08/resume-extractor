markdown# Resume Extractor

Drop a resume PDF in a folder, get back structured JSON with skills, companies, total years of experience, and LinkedIn URL — powered by the Claude API. Then chat with the resume to ask follow-up questions.

## Why

Manually parsing resumes is slow, and traditional regex/rule-based parsers break on every new layout. An LLM handles weird formatting, multi-column layouts, and inconsistent date conventions out of the box.

## What it does

**Extract** — Pulls structured fields from a resume PDF:

| Field | Type | Description |
|---|---|---|
| `linkedin_url` | string \| null | Normalized full LinkedIn URL |
| `skills` | string[] | Deduplicated technical & professional skills |
| `companies` | string[] | Employers, most recent first |
| `total_years_experience` | number \| null | Sum of professional experience in years |

**Chat** — Opens an interactive Q&A loop where you can ask anything about the candidate, with the resume as context.

See [`examples/sample_output.json`](examples/sample_output.json) for a full example output.

## Setup

```bash
# 1. Clone and enter the repo
git clone https://github.com/purohit08/resume-extractor.git
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

### Extract structured data

```bash
# Process every PDF in resumes/
python -m src.main

# Or process one specific file
python -m src.main resumes/jane_doe.pdf
```

Each PDF in `resumes/` produces a matching `<name>.json` file in `output/`.

### Chat with a resume

Ask follow-up questions about a candidate, with the resume as context:

```bash
python -m src.chat resumes/jane_doe.pdf
```

Example session:
You: What's the most recent role?
Claude: The candidate's most recent role is at Adobe.
You: Do they have cloud experience?
Claude: Yes — they list Azure AI Foundry, Azure Function App, and Azure AI Search.
You: Are they a good fit for a Senior AI Engineer role?
Claude: Based on the resume, yes — they have 8.5 years of experience...
You: exit
Bye!

Type `exit`, `quit`, or press `Ctrl+C` to leave the loop.

## How it works
PDF  →  pypdf (text extraction)  →  Claude API  →  JSON / chat answer

- **`src/pdf_reader.py`** — uses `pypdf` to pull raw text from the PDF
- **`src/extractor.py`** — sends that text to Claude with a system prompt that locks the output to a strict JSON schema
- **`src/chat.py`** — loads the resume into context and runs an interactive Q&A loop with conversation history
- **`src/main.py`** — orchestrates the extraction pipeline

The model is pinned to `claude-sonnet-4-5-20250929` for reproducible behavior. Edit `MODEL` in `src/extractor.py` or `src/chat.py` to switch.

## Why no RAG?

Resumes are short — usually under 5,000 characters. They fit comfortably inside Claude's 200,000-token context window, so there's no need to chunk, embed, or retrieve. Sending the full text every time is simpler, more accurate, and cheaper than running a vector database for a single document.

RAG becomes worthwhile when scaling to **many** resumes (e.g., a searchable database of thousands of candidates) — see roadmap below.

## Limitations

- **Scanned PDFs won't work.** `pypdf` only reads embedded text. Image-only PDFs need OCR (Tesseract). The script raises a clear error in this case.
- **Years of experience is an estimate.** Calculated from date ranges in the resume; gaps and overlaps are not specially handled.
- **Costs API credits.** Every PDF or chat question is one API call. With Sonnet 4.5, a typical resume costs well under a cent.

## Roadmap

- [ ] OCR fallback for scanned PDFs
- [ ] Batch CSV export across multiple resumes
- [ ] Web UI (Streamlit / Gradio)
- [ ] Confidence scores per field
- [ ] Resume database with RAG (search across thousands of candidates by skill, company, experience)

## License

MIT
