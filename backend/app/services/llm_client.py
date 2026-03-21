"""
Unified LLM client with automatic fallback:
  1. Groq (configurable model via GROQ_MODEL env var) - primary, fastest
  2. Google Gemini Flash - fallback
  3. Raises AllProvidersExhaustedError if both fail

Available Groq models (free tier):
  - llama-3.3-70b-versatile (default)
  - openai/gpt-oss-120b
  - openai/gpt-oss-20b
  - openai/gpt-oss-safeguard-20b
  - qwen/qwen3-32b
"""

import json
import logging
import httpx
import asyncio
import random

from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    pass


class LLMParsingError(Exception):
    pass


class AllProvidersExhaustedError(Exception):
    pass


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 4000,
    json_mode: bool = True,
) -> dict | list:
    """
    Call LLM with automatic provider fallback.
    Returns parsed JSON (dict or list).
    """
    providers = _build_provider_chain()

    last_error = None
    for provider_name, call_fn in providers:
        try:
            raw_text = await call_fn(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode,
            )
            return _parse_json_response(raw_text)
        except RateLimitError as e:
            logger.warning(f"{provider_name} rate limited: {e}")
            last_error = e
            continue
        except LLMParsingError:
            # Retry same provider with stricter prompt once
            try:
                strict_system = system_prompt + "\n\nCRITICAL: Return ONLY valid JSON. No markdown, no explanation, no code fences."
                raw_text = await call_fn(
                    system_prompt=strict_system,
                    user_prompt=user_prompt,
                    temperature=max(0.1, temperature - 0.2),
                    max_tokens=max_tokens,
                    json_mode=json_mode,
                )
                return _parse_json_response(raw_text)
            except Exception as e2:
                logger.warning(f"{provider_name} retry failed: {e2}")
                last_error = e2
                continue
        except Exception as e:
            logger.error(f"{provider_name} error: {e}")
            last_error = e
            continue

    raise AllProvidersExhaustedError(f"All LLM providers failed. Last error: {last_error}")


def _build_provider_chain() -> list[tuple[str, callable]]:
    """Build ordered list of available providers."""
    chain = []
    if settings.GROQ_API_KEY:
        chain.append(("groq", _call_groq))
    if settings.GEMINI_API_KEY:
        chain.append(("gemini", _call_gemini))
    if settings.OPENROUTER_API_KEY:
        chain.append(("openrouter", _call_openrouter))
    if settings.HF_API_TOKEN:
        chain.append(("huggingface", _call_hf))
    if not chain:
        raise AllProvidersExhaustedError("No LLM API keys configured")
    return chain


async def _call_groq(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    json_mode: bool,
) -> str:
    """Call Groq API (OpenAI-compatible endpoint)."""
    model = settings.GROQ_MODEL
    logger.info(f"Using Groq model: {model}")

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    # Note: Groq doesn't support response_format like OpenAI does
    # JSON parsing happens in _parse_json_response()

    return await _post_with_retry(
        url="https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json=body,
        parse=lambda resp: resp.json()["choices"][0]["message"]["content"],
    )


async def _call_openrouter(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    json_mode: bool,
) -> str:
    model = "meta-llama/llama-3.2-3b-instruct:free"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}

    return await _post_with_retry(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://openrouter.ai",
            "X-Title": "LaunchLens",
            "Content-Type": "application/json",
        },
        json=body,
        parse=lambda resp: resp.json()["choices"][0]["message"]["content"],
    )


async def _call_gemini(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    json_mode: bool,
) -> str:
    """Call Google Gemini API."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"
        )

        body = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\n---\n\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if json_mode:
            body["generationConfig"]["responseMimeType"] = "application/json"

        resp = await client.post(url, json=body)

        if resp.status_code == 429:
            raise RateLimitError("Gemini rate limit hit")
        resp.raise_for_status()

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise Exception("Gemini returned no candidates")
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise Exception("Gemini returned no content parts")
        return parts[0]["text"]


async def _call_hf(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    json_mode: bool,
) -> str:
    """
    Call Hugging Face Inference API for Llama 3 70B instruct (via free token).
    """
    model = "meta-llama/Llama-3.2-3B-Instruct"
    payload = {
        "inputs": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "parameters": {
            "temperature": temperature,
            "max_new_tokens": max_tokens,
        },
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"https://api-inference.huggingface.co/v1/chat/completions?model={model}",
            headers={"Authorization": f"Bearer {settings.HF_API_TOKEN}"},
            json=payload,
        )
        if resp.status_code == 429:
            raise RateLimitError("HF rate limit hit")
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def _post_with_retry(url: str, headers: dict, json: dict, parse) -> str:
    backoffs = [0.4, 0.8, 1.2]
    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, delay in enumerate([0] + backoffs):
            if delay:
                await asyncio.sleep(delay + random.random() * 0.15)
            resp = await client.post(url, headers=headers, json=json)
            if resp.status_code == 429:
                if i == len(backoffs):
                    raise RateLimitError("Groq rate limit hit")
                continue
            resp.raise_for_status()
            return parse(resp)
    raise RateLimitError("Rate limit after retries")


def _parse_json_response(raw: str) -> dict | list:
    """Parse LLM response text into JSON, handling code fences."""
    text = raw.strip()

    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Try to find JSON within the text
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start = text.find(start_char)
            end = text.rfind(end_char)
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    continue
        raise LLMParsingError(f"Could not parse LLM response as JSON: {e}")
