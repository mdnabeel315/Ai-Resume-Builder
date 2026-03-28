"""
LLM Service — Clean abstraction over Google Gemini 2.0 Flash.
Features:
  - Streamlit secrets + env var fallback for API key
  - Tenacity retry (3x, exponential backoff) on every Gemini call
  - JSON mode with auto-strip of markdown fences
  - TTL cache (5 min) — identical prompts never re-hit the API
  - Clean LLMError / LLMParseError exception hierarchy
"""

import json
import hashlib
import time
import logging
import os
from typing import Any

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

import structlog
logger = structlog.get_logger(__name__)

_MODEL_NAME = "gemini-2.0-flash"


# ── API Key ────────────────────────────────────────────────────────────────────
def _get_api_key() -> str:
    """Load Gemini key: Streamlit secrets first, then env var."""
    try:
        import streamlit as st
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        key = os.environ.get("GEMINI_API_KEY", "")
        if not key:
            raise EnvironmentError(
                "GEMINI_API_KEY not found. "
                "Set it in .streamlit/secrets.toml or as an environment variable."
            )
        return key


genai.configure(api_key=_get_api_key())


# ── TTL Cache ──────────────────────────────────────────────────────────────────
_CACHE: dict[str, tuple[Any, float]] = {}
_CACHE_TTL = 300  # seconds


def _cache_key(system: str, user: str) -> str:
    return hashlib.sha256(f"{system}||{user}".encode()).hexdigest()


def _get_cached(key: str) -> Any | None:
    if key in _CACHE:
        value, ts = _CACHE[key]
        if time.time() - ts < _CACHE_TTL:
            return value
        del _CACHE[key]
    return None


def _set_cached(key: str, value: Any) -> None:
    _CACHE[key] = (value, time.time())


# ── Custom Exceptions ──────────────────────────────────────────────────────────
class LLMError(Exception):
    """Raised when the LLM call fails after all retries."""


class LLMParseError(LLMError):
    """Raised when JSON parsing of the LLM response fails."""


# ── Raw Gemini Call (with retry) ───────────────────────────────────────────────
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _call_gemini(
    system: str,
    user: str,
    temperature: float,
    max_tokens: int,
    json_mode: bool,
) -> str:
    generation_config = genai.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
        response_mime_type="application/json" if json_mode else "text/plain",
    )
    model = genai.GenerativeModel(
        model_name=_MODEL_NAME,
        generation_config=generation_config,
        system_instruction=system,
    )
    response = model.generate_content(user)
    return response.text.strip()


# ── Public API ─────────────────────────────────────────────────────────────────
def complete(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    json_mode: bool = False,
    use_cache: bool = True,
) -> Any:
    """
    Call Gemini and return either a plain string or a parsed dict/list.

    Args:
        system_prompt: System instruction for the model.
        user_prompt:   User turn content.
        temperature:   Sampling temperature (0.0-1.0).
        max_tokens:    Max output tokens.
        json_mode:     If True, forces JSON output and auto-parses to dict/list.
        use_cache:     Set False for non-deterministic creative calls.

    Returns:
        str   when json_mode=False
        dict  when json_mode=True
    """
    key = _cache_key(system_prompt, user_prompt)

    if use_cache:
        cached = _get_cached(key)
        if cached is not None:
            logger.debug("LLM cache hit", cache_key=key[:8])
            return cached
            return cached

    try:
        raw = _call_gemini(system_prompt, user_prompt, temperature, max_tokens, json_mode)
    except Exception as e:
        raise LLMError(f"Gemini call failed after retries: {e}") from e

    if not json_mode:
        if use_cache:
            _set_cached(key, raw)
        return raw

    # Strip markdown fences if the model wrapped the output
    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("```", 2)[1]
        if clean.startswith("json"):
            clean = clean[4:]
        clean = clean.rsplit("```", 1)[0].strip()

    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError as e:
        raise LLMParseError(
            f"Could not parse LLM JSON: {e}\nRaw output (first 300 chars): {raw[:300]}"
        ) from e

    if use_cache:
        _set_cached(key, parsed)
    return parsed
