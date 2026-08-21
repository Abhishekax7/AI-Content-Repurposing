"""
prompts.py
----------
Builds the single prompt sent to the LLM. We ask for ONE structured JSON
object back (rather than 7 separate calls) — cheaper, faster, and keeps
all the generated assets consistent with each other since the model sees
the full context at once.
"""

# The exact JSON shape we require. Repeating this schema explicitly in the
# prompt (not just describing it) is what makes Groq return well-formed,
# predictable JSON instead of freeform text.
JSON_SCHEMA_EXAMPLE = """{
  "summary": "string",
  "linkedin_post": "string",
  "short_video_script": {
    "hook": "string",
    "body": "string",
    "cta": "string"
  },
  "campaign_ideas": ["string", "string", "string"],
  "hooks": ["string", "string", "string", "string", "string"],
  "cta_options": ["string", "string", "string"],
  "email_subject_lines": ["string", "string"]
}"""

SYSTEM_PROMPT = """You are an expert content repurposing strategist and
marketing copywriter. You take one piece of long-form content and turn it
into multiple ready-to-use marketing assets. You always respond with
STRICT, VALID JSON and nothing else — no markdown code fences, no
explanation text before or after, no comments inside the JSON. Every
string value must be complete, ready-to-publish content — never a
placeholder like [insert here]."""


def build_repurposing_prompt(content: str, source_type: str, brand: str,
                              audience: str, tone: str, extra: str) -> tuple:
    """Returns (system_prompt, user_prompt) ready to send to ai_engine."""

    user_prompt = f"""Repurpose the following {source_type} into marketing
assets for the brand "{brand}".

Target audience: {audience}
Tone: {tone}
Extra instructions: {extra or "none"}

SOURCE CONTENT:
\"\"\"
{content}
\"\"\"

Return ONLY a JSON object matching exactly this structure (fill in real
content, keep the same keys):

{JSON_SCHEMA_EXAMPLE}

Requirements for the content:
- summary: 2-3 sentences capturing the core idea
- linkedin_post: a complete, ready-to-post LinkedIn post (with line breaks using \\n)
- short_video_script: a hook (first 3 seconds), body, and CTA for a Reel/Shorts script
- campaign_ideas: exactly 3 distinct campaign concepts, one sentence each
- hooks: exactly 5 scroll-stopping opening lines, usable across platforms
- cta_options: exactly 3 different call-to-action phrasings
- email_subject_lines: 2 subject line options

Respond with ONLY the JSON object. No markdown fences, no extra text."""

    return SYSTEM_PROMPT, user_prompt
