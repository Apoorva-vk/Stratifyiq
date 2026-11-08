"""AI answers for the assistant.

Supports a free local model through Ollama and the Claude API. Returns None when the
provider is off or the call fails, so the caller falls back to rule-based answers.
API keys are only read from the environment and never returned to the browser.
"""
import json

import httpx

from app.config import settings

SYSTEM_PROMPT = (
    "You are the StratifyIQ assistant, inside a project management and decision "
    "intelligence app. Answer the user's question using only the company data provided. "
    "Be concise (2 to 4 sentences), give numbers with their units, and say so plainly "
    "when the data does not contain the answer. Risk and overrun figures are model "
    "predictions, so describe them as estimates."
)


def _user_message(question: str, context: dict) -> str:
    return f"Company data (JSON):\n{json.dumps(context)}\n\nQuestion: {question}"


def _ask_ollama(question: str, context: dict) -> str | None:
    response = httpx.post(
        f"{settings.OLLAMA_URL}/api/chat",
        json={
            "model": settings.OLLAMA_MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _user_message(question, context)},
            ],
        },
        timeout=120,  # local models can take a while on a laptop CPU
    )
    response.raise_for_status()
    text = response.json().get("message", {}).get("content", "").strip()
    return text or None


def _ask_anthropic(question: str, context: dict) -> str | None:
    response = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": settings.ANTHROPIC_MODEL,
            "max_tokens": 400,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": _user_message(question, context)}],
        },
        timeout=20,
    )
    response.raise_for_status()
    blocks = response.json().get("content", [])
    text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
    return text or None


def ask_llm(question: str, context: dict) -> str | None:
    try:
        if settings.AI_PROVIDER == "ollama":
            return _ask_ollama(question, context)
        if settings.AI_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
            return _ask_anthropic(question, context)
    except Exception:
        return None
    return None
