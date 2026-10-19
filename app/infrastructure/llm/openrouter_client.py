# app/infrastructure/llm/openrouter_client.py
"""OpenRouter LLM client (OpenAI-compatible API)."""
from __future__ import annotations

import json
import logging
from typing import Sequence

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

from app.core.config import get_settings
from app.core.exceptions import LLMError
from app.domain.ports import LLMProvider

logger = logging.getLogger(__name__)

_RETRYABLE = (httpx.TimeoutException, httpx.ConnectError)


class OpenRouterClient(LLMProvider):
    def __init__(self) -> None:
        self._settings = get_settings()
        self._client = httpx.AsyncClient(
            base_url=self._settings.llm_base_url,
            timeout=httpx.Timeout(self._settings.llm_timeout_s),
            headers={
                "Authorization": f"Bearer {self._settings.llm_api_key}",
                "Content-Type": "application/json",
            },
        )

    async def complete(
            self,
            messages: Sequence[dict],
            *,
            json_mode: bool = False,
            temperature: float | None = None,
    ) -> str:
        last_exc = None
        # Fallback chain: Primary -> Fallback
        models = [self._settings.llm_model, self._settings.llm_fallback_model]

        for model in models:
            try:
                return await self._call_api(model, messages, json_mode, temperature)
            except Exception as exc:
                logger.warning("Model %s failed: %s", model, exc)
                last_exc = exc

        raise LLMError(f"All LLM models failed. Last error: {last_exc}")

    @retry(retry=retry_if_exception_type(_RETRYABLE), stop=stop_after_attempt(3), reraise=True)
    async def _call_api(self, model: str, messages: Sequence[dict], json_mode: bool, temperature: float | None) -> str:
        body = {
            "model": model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self._settings.llm_temperature,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        resp = await self._client.post("/chat/completions", json=body)
        resp.raise_for_status()

        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        if not content:
            raise LLMError("Empty response from LLM.")
        return content