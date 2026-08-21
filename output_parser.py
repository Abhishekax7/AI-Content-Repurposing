"""
output_parser.py
-----------------
Safely parses and validates the JSON text returned by the LLM. LLMs
occasionally wrap JSON in markdown fences or omit a key even when asked
not to — this module cleans that up and fails loudly with a useful
message rather than letting a KeyError crash the app later.
"""

import json

REQUIRED_KEYS = [
    "summary", "linkedin_post", "short_video_script",
    "campaign_ideas", "hooks", "cta_options", "email_subject_lines",
]

REQUIRED_SCRIPT_KEYS = ["hook", "body", "cta"]


class OutputParsingError(Exception):
    """Raised when the LLM's response can't be parsed into the expected shape."""
    pass


def _strip_markdown_fences(text: str) -> str:
    """Some models wrap JSON in ```json ... ``` even when told not to — strip it."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.split("\n")
        lines = lines[1:]  # drop opening fence (with or without 'json')
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]  # drop closing fence
        stripped = "\n".join(lines)
    return stripped.strip()


def parse_and_validate(raw_text: str) -> dict:
    """
    Parses raw_text as JSON and checks all required keys are present.
    Raises OutputParsingError with a clear message on any failure.
    Returns the parsed dict on success.
    """
    cleaned = _strip_markdown_fences(raw_text)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise OutputParsingError(
            f"The AI's response wasn't valid JSON (parse error: {e}). "
            f"This can happen occasionally — try generating again."
        )

    if not isinstance(data, dict):
        raise OutputParsingError("Expected a JSON object from the AI but got something else.")

    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        raise OutputParsingError(
            f"The AI's response was missing expected fields: {', '.join(missing)}. "
            f"Try generating again."
        )

    script = data.get("short_video_script", {})
    if not isinstance(script, dict) or any(k not in script for k in REQUIRED_SCRIPT_KEYS):
        raise OutputParsingError(
            "The video script section was malformed in the AI's response. Try generating again."
        )

    return data
