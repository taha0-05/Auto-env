"""
Auto-ENV — Gemini API Client
Calls gemini-2.5-flash with a strict JSON-only system prompt.
Validates the response against a JSON schema. Retries up to 2 times on failure.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
    _HAS_JSONSCHEMA = True
except ImportError:
    _HAS_JSONSCHEMA = False

try:
    import google.generativeai as genai
    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False


# ---------------------------------------------------------------------------
# JSON Blueprint Schema
# ---------------------------------------------------------------------------

BLUEPRINT_SCHEMA = {
    "type": "object",
    "required": ["project_name", "stack", "dependencies", "env_vars", "structure"],
    "properties": {
        "project_name": {"type": "string"},
        "stack": {
            "type": "object",
            "required": ["language", "framework"],
            "properties": {
                "language": {"type": "string"},
                "framework": {"type": "string"},
                "runtime_version": {"type": "string"},
            },
        },
        "dependencies": {
            "type": "array",
            "items": {"type": "string"},
        },
        "env_vars": {
            "type": "object",
            "additionalProperties": {"type": "string"},
        },
        "structure": {
            "type": "array",
            "items": {"type": "string"},
        },
        "start_command": {"type": "string"},
        "notes": {"type": "string"},
    },
    "additionalProperties": True,
}


# ---------------------------------------------------------------------------
# Key Management
# ---------------------------------------------------------------------------

_CONFIG_FILE = Path.home() / ".autoenv" / "gemini_key.txt"


def _load_api_key() -> str | None:
    # 1. Environment variable
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key
    # 2. Config file
    if _CONFIG_FILE.exists():
        key = _CONFIG_FILE.read_text(encoding="utf-8").strip()
        if key:
            return key
    return None


def save_api_key(key: str) -> None:
    """Persist the API key to the config file."""
    _CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CONFIG_FILE.write_text(key.strip(), encoding="utf-8")


def has_api_key() -> bool:
    return bool(_load_api_key())


# ---------------------------------------------------------------------------
# JSON Extraction & Validation
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> dict:
    """Extract and parse a JSON object from a (possibly markdown-wrapped) string."""
    # Strip markdown code fences
    cleaned = re.sub(r"```(?:json)?\s*", "", text, flags=re.IGNORECASE).strip()
    cleaned = cleaned.replace("```", "").strip()

    # Try direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to find the first { ... } block
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No valid JSON found in Gemini response. Raw: {text[:300]}")


def _validate(blueprint: dict) -> None:
    """Validate blueprint against schema. Raises ValueError on mismatch."""
    if not _HAS_JSONSCHEMA:
        return  # Skip validation if jsonschema not installed
    try:
        jsonschema.validate(instance=blueprint, schema=BLUEPRINT_SCHEMA)
    except jsonschema.ValidationError as exc:
        raise ValueError(f"Blueprint schema validation failed: {exc.message}")


# ---------------------------------------------------------------------------
# System Prompt Builder
# ---------------------------------------------------------------------------

def _build_system_prompt(system_info: dict) -> str:
    os_info = system_info.get("os", {})
    runtimes = system_info.get("runtimes", {})
    ports = system_info.get("ports", {})

    runtime_lines = []
    for name, info in runtimes.items():
        if isinstance(info, dict):
            runtime_lines.append(f"  - {name}: {info.get('version','?')} ({info.get('manager','global')})")
        else:
            runtime_lines.append(f"  - {name}: {info}")
    runtimes_str = "\n".join(runtime_lines) or "  - none detected"

    return f"""You are Auto-ENV, an intelligent developer environment configuration assistant.
The user's system profile:
  OS: {os_info.get('system','?')} {os_info.get('release','?')} ({os_info.get('arch','?')})
  Available runtimes:
{runtimes_str}
  Suggested free port: {ports.get('suggested_port', 3000)}

STRICT RULES:
1. Respond with ONLY a single raw JSON object — no markdown, no prose, no code fences.
2. The JSON must conform to this exact schema:
   {{
     "project_name": "snake_case_name",
     "stack": {{
       "language": "python|node|rust|go|java",
       "framework": "framework name or 'none'",
       "runtime_version": "exact version string"
     }},
     "dependencies": ["pkg==version", ...],
     "env_vars": {{
       "PORT": "{ports.get('suggested_port', 3000)}",
       "KEY": "VALUE"
     }},
     "structure": ["src/", "src/main.py", ".env", "README.md"],
     "start_command": "python src/main.py",
     "notes": "brief setup notes"
   }}
3. Use the suggested free port {ports.get('suggested_port', 3000)} for the PORT env var.
4. Pin exact dependency versions (e.g. flask==3.0.3, not just flask).
5. Never include explanatory text outside the JSON object.
"""


# ---------------------------------------------------------------------------
# Main API Call
# ---------------------------------------------------------------------------

class GeminiError(Exception):
    pass


def generate_blueprint(
    prompt: str,
    system_info: dict,
    api_key: str | None = None,
    *,
    log_fn=None,
) -> dict:
    """
    Call Gemini and return a validated blueprint dict.
    Retries up to 2 times on malformed JSON.
    Raises GeminiError if all attempts fail or library is missing.
    """
    def _log(msg: str):
        if log_fn:
            log_fn(msg)

    key = api_key or _load_api_key()
    if not key:
        raise GeminiError(
            "No Gemini API key found.\n"
            "Set the GEMINI_API_KEY environment variable, or enter your key in the app settings."
        )

    if not _HAS_GENAI:
        raise GeminiError(
            "The 'google-generativeai' package is not installed.\n"
            "Run: pip install google-generativeai"
        )

    genai.configure(api_key=key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=_build_system_prompt(system_info),
    )

    full_prompt = (
        f"Generate a complete development environment blueprint for this project:\n\n{prompt}\n\n"
        "Remember: respond with ONLY the JSON object."
    )

    last_error: Exception | None = None
    for attempt in range(1, 4):
        _log(f"[→] Calling Gemini API (attempt {attempt}/3)...")
        try:
            response = model.generate_content(full_prompt)
            raw = response.text
            _log("[→] Response received. Parsing JSON...")
            blueprint = _extract_json(raw)
            _validate(blueprint)
            _log("[✓] Blueprint validated successfully.")
            return blueprint
        except (ValueError, Exception) as exc:
            last_error = exc
            _log(f"[✗] Attempt {attempt} failed: {exc}")

    raise GeminiError(f"Gemini failed after 3 attempts. Last error: {last_error}")
