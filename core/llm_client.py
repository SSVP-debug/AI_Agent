"""
Thin, typed wrapper around the Gemini API. Agents never import google.genai
directly — they go through LLMClient so retry, error handling, and (if we
ever swap providers) the provider boundary live in exactly one place.
"""
from __future__ import annotations

import time
import logging
from dataclasses import dataclass

from google import genai
from google.genai import errors as genai_errors

from config import Settings

logger = logging.getLogger(__name__)


class LLMError(RuntimeError):
    """Raised for non-retryable LLM failures (bad request, auth, etc.)."""


class LLMRateLimitError(RuntimeError):
    """Raised when retries are exhausted after repeated rate-limit responses."""


@dataclass
class LLMClient:
    settings: Settings

    def __post_init__(self) -> None:
        self._client = genai.Client(api_key=self.settings.gemini_api_key)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_output_tokens: int = 2000,
    ) -> str:
        """
        Call Gemini with a system + user prompt. Retries transient failures
        (rate limits, 5xx, network) with exponential backoff; fails fast on
        non-retryable errors (bad request, auth).
        """
        last_error: Exception | None = None

        for attempt in range(1, self.settings.llm_max_retries + 1):
            try:
                response = self._client.models.generate_content(
                    model=self.settings.gemini_model,
                    contents=user_prompt,
                    config={
                        "system_instruction": system_prompt,
                        "temperature": temperature,
                        "max_output_tokens": max_output_tokens,
                    },
                )
                text = getattr(response, "text", None)
                if not text:
                    raise LLMError("Gemini returned an empty response.")
                return text

            except genai_errors.ClientError as e:
                # 4xx: bad request / auth — not retryable, except 429 rate limit.
                if getattr(e, "code", None) == 429:
                    last_error = e
                    self._backoff(attempt)
                    continue
                raise LLMError(f"Gemini rejected the request: {e}") from e

            except genai_errors.ServerError as e:
                # 5xx: transient, worth retrying.
                last_error = e
                self._backoff(attempt)
                continue

            except Exception as e:  # network errors, SDK-internal issues
                last_error = e
                self._backoff(attempt)
                continue

        raise LLMRateLimitError(
            f"Gemini call failed after {self.settings.llm_max_retries} attempts: {last_error}"
        ) from last_error

    @staticmethod
    def _backoff(attempt: int) -> None:
        delay = min(2 ** attempt, 20)
        logger.warning("LLM call failed, retrying in %ss (attempt %s)", delay, attempt)
        time.sleep(delay)
