"""
validators.py
--------------
All input validation lives here, separate from the UI and the AI logic.
Interview talking point: validating BEFORE calling the LLM saves API
calls/cost and gives the user instant, clear feedback instead of a
confusing downstream error.
"""

MIN_CONTENT_LENGTH = 200  # characters — roughly a short paragraph+


def validate_content(content: str) -> tuple[bool, str]:
    """
    Returns (is_valid, error_message).
    error_message is empty string when is_valid is True.
    """
    if content is None or content.strip() == "":
        return False, "Please paste some content — the input box is empty."

    stripped = content.strip()

    if len(stripped) < MIN_CONTENT_LENGTH:
        return False, (
            f"That's too short to repurpose meaningfully "
            f"({len(stripped)} characters). Please paste at least "
            f"{MIN_CONTENT_LENGTH} characters — a full paragraph or more."
        )

    return True, ""


def validate_required_fields(brand: str, audience: str) -> tuple[bool, str]:
    """Checks the other required form fields before generation."""
    if not brand or not brand.strip():
        return False, "Please enter a brand name."
    if not audience or not audience.strip():
        return False, "Please enter a target audience."
    return True, ""
