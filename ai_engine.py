"""
ai_engine.py
------------
The only module that talks to the Groq API. Isolating this means every
network/API failure mode is handled in exactly one place, and the model
name is a single constant you can change without touching any other file.
"""

import os
import requests
import streamlit as st

# Change the model here — nowhere else in the codebase references a model name.
GROQ_MODEL = "openai/gpt-oss-20b"

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class AIEngineError(Exception):
    """Raised for any failure calling the LLM — caught and shown cleanly in app.py."""
    pass


def get_api_key() -> str:
    """Check Streamlit secrets first (cloud), then environment variables (local)."""
    if "GROQ_API_KEY" in st.secrets:
        return st.secrets["GROQ_API_KEY"]
    return os.environ.get("GROQ_API_KEY", "")


def generate_json_content(system_prompt: str, user_prompt: str,
                           temperature: float = 0.7) -> str:
    """
    Calls Groq and returns the raw text response (expected to be JSON —
    parsing happens in output_parser.py, not here, so this function's
    only job is "talk to the network and return text or raise a clear error").
    """
    api_key = get_api_key()
    if not api_key:
        raise AIEngineError(
            "No Groq API key found. Add GROQ_API_KEY to your .env file "
            "(local) or to Streamlit Secrets (cloud deployment)."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
    except requests.exceptions.Timeout:
        raise AIEngineError("The request to Groq timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        raise AIEngineError("Could not connect to Groq — check your internet connection.")
    except requests.exceptions.RequestException as e:
        raise AIEngineError(f"Network error while calling Groq: {e}")

    if response.status_code == 401:
        raise AIEngineError("Groq rejected the API key (401 Unauthorized). Check your key is correct.")
    if response.status_code == 429:
        raise AIEngineError("Groq rate limit reached (429). Wait a moment and try again.")
    if response.status_code != 200:
        raise AIEngineError(f"Groq API error ({response.status_code}): {response.text[:300]}")

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError) as e:
        raise AIEngineError(f"Unexpected response shape from Groq: {e}")
