"""Secure OpenAI client helpers. API keys stay server-side in session state."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional, Type, TypeVar

from openai import APIError, AuthenticationError, OpenAI, RateLimitError
from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL = "gpt-4o-mini"


def _redact(text: str) -> str:
    """Never log secrets that look like OpenAI keys."""
    return re.sub(r"sk-[A-Za-z0-9_\-]{10,}", "sk-***REDACTED***", text or "")


def create_client(api_key: str) -> OpenAI:
    if not api_key or not api_key.strip():
        raise ValueError("API key is required.")
    key = api_key.strip()
    if not key.startswith("sk-"):
        raise ValueError("Invalid API key format. OpenAI keys typically start with 'sk-'.")
    return OpenAI(api_key=key)


def validate_api_key(api_key: str) -> tuple[bool, str]:
    """Validate key with a lightweight models.list call. Never logs the key."""
    try:
        client = create_client(api_key)
        client.models.list()
        return True, "API key validated successfully."
    except AuthenticationError:
        return False, "Authentication failed. Please check your OpenAI API key."
    except RateLimitError:
        return False, "Rate limit reached while validating. Try again shortly."
    except APIError as exc:
        return False, f"OpenAI API error: {_redact(str(exc))}"
    except Exception as exc:  # noqa: BLE001
        return False, f"Validation failed: {_redact(str(exc))}"


def _extract_json(text: str) -> Any:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}|\[[\s\S]*\]", text)
        if match:
            return json.loads(match.group(0))
        raise


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
def chat_json(
    api_key: str,
    *,
    system: str,
    user: str,
    schema: Type[T],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.4,
) -> T:
    """Call OpenAI and validate the response against a Pydantic schema."""
    client = create_client(api_key)
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    content = response.choices[0].message.content or "{}"
    try:
        data = _extract_json(content)
        return schema.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        logger.warning("Schema validation failed: %s", _redact(str(exc)))
        raise ValueError(f"AI response failed schema validation: {exc}") from exc


def chat_text(
    api_key: str,
    *,
    system: str,
    user: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.5,
) -> str:
    client = create_client(api_key)
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return (response.choices[0].message.content or "").strip()


def safe_error_message(exc: Exception) -> str:
    if isinstance(exc, AuthenticationError):
        return "OpenAI authentication failed. Re-enter a valid API key."
    if isinstance(exc, RateLimitError):
        return "OpenAI rate limit exceeded. Please wait and try again."
    if isinstance(exc, APIError):
        return f"OpenAI API error: {_redact(str(exc))}"
    return f"Unexpected error: {_redact(str(exc))}"
