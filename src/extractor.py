"""LLM-powered resume field extraction using the Claude API."""
import json
import os
from anthropic import Anthropic

# Pinned model snapshot — change this if you want a different model.
# See https://docs.claude.com/en/docs/about-claude/models
MODEL = "claude-sonnet-4-5-20250929"

SYSTEM_PROMPT = """You are a precise resume parser. Extract the requested fields from the resume text the user provides.

Return ONLY valid JSON matching this exact schema — no markdown, no commentary, no code fences:

{
  "linkedin_url": string or null,
  "skills": [string, ...],
  "companies": [string, ...],
  "total_years_experience": number or null
}

Rules:
- linkedin_url: Full URL if present (e.g. "https://linkedin.com/in/jane-doe"). If only a handle is shown, normalize to a full URL. Use null if absent.
- skills: A flat list of distinct technical and professional skills. Deduplicate. Keep original casing where reasonable (e.g. "Python", "AWS", "React"). Do NOT include soft-skill filler like "team player" unless the resume explicitly emphasizes it.
- companies: Distinct employer names in the order they appear, most recent first. Exclude universities and certification issuers.
- total_years_experience: Sum of full-time professional work experience in years (number, can be decimal like 5.5). Calculate from the date ranges in the work history. If a role lists "Present" or "Current", treat it as today. If dates are missing entirely, return null. Do NOT include internships unless they are the only experience listed.

If a field cannot be determined, use null (or [] for lists). Never invent data."""


def extract_fields(resume_text: str, client: Anthropic | None = None) -> dict:
    """
    Extract structured fields from resume text using Claude.

    Args:
        resume_text: Raw text content of a resume.
        client: Optional pre-configured Anthropic client. If None, one is created
                using the ANTHROPIC_API_KEY environment variable.

    Returns:
        Dict with keys: linkedin_url, skills, companies, total_years_experience.

    Raises:
        ValueError: If the model response is not valid JSON.
    """
    if client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY not set. Add it to your .env file."
            )
        client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": resume_text}
        ],
    )

    raw = response.content[0].text.strip()

    # Strip code fences if the model wrapped them despite instructions
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON.\nResponse:\n{raw}") from e
