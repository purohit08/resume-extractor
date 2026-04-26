"""
Chat with a resume.

Loads a PDF (or .txt), then opens an interactive Q&A loop where you can
ask any question about the candidate. Each question is answered using
the full resume text as context.

Usage:
    python -m src.chat resumes/some_resume.pdf
"""
import os
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

from src.pdf_reader import extract_text

load_dotenv()

MODEL = "claude-sonnet-4-5-20250929"

SYSTEM_PROMPT = """You are a helpful assistant answering questions about a candidate based on their resume.

Rules:
- Answer ONLY using information from the resume below.
- If the resume does not contain the answer, say "The resume doesn't mention that."
- Be concise. Use bullet points only if listing 3+ items.
- Do not invent companies, dates, skills, or accomplishments.
- When asked about experience or duration, calculate from the dates given. If a role says "Present", treat it as today.

--- RESUME ---
{resume_text}
--- END RESUME ---"""


def chat_loop(resume_text: str) -> None:
    """Open an interactive chat about the given resume."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY not set in .env")

    client = Anthropic(api_key=api_key)
    system = SYSTEM_PROMPT.format(resume_text=resume_text)

    # Keep conversation history so follow-ups work ("what about her education?")
    history: list[dict] = []

    print("\n" + "=" * 60)
    print("Chat with the resume. Type 'exit' or Ctrl+C to quit.")
    print("=" * 60 + "\n")

    while True:
        try:
            question = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            return

        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            print("Bye!")
            return

        history.append({"role": "user", "content": question})

        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=system,
                messages=history,
            )
        except Exception as e:
            print(f"  ✗ API error: {e}\n")
            history.pop()  # don't keep the failed turn
            continue

        answer = response.content[0].text.strip()
        history.append({"role": "assistant", "content": answer})

        print(f"\nClaude: {answer}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m src.chat <path_to_resume.pdf>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: {path} not found")
        sys.exit(1)

    if path.suffix.lower() == ".pdf":
        print(f"Reading {path.name}...")
        text = extract_text(path)
    else:
        text = path.read_text(encoding="utf-8")

    print(f"Loaded {len(text):,} characters.")
    chat_loop(text)


if __name__ == "__main__":
    main()