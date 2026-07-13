import logging
from typing import Generator

from core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified LLM client supporting OpenAI, Claude, and fallback."""

    def generate(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        if settings.OPENAI_API_KEY:
            return self._openai_generate(messages, temperature, max_tokens)
        if settings.ANTHROPIC_API_KEY:
            return self._claude_generate(messages, temperature, max_tokens)
        return self._fallback_generate(messages)

    def generate_stream(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Generator[str, None, None]:
        if settings.OPENAI_API_KEY:
            yield from self._openai_stream(messages, temperature, max_tokens)
        else:
            yield self._fallback_generate(messages)

    def _openai_generate(self, messages, temperature, max_tokens) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    def _openai_stream(self, messages, temperature, max_tokens) -> Generator[str, None, None]:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        stream = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def _claude_generate(self, messages, temperature, max_tokens) -> str:
        from anthropic import Anthropic
        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_messages = [m for m in messages if m["role"] != "system"]
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            system=system,
            messages=user_messages,
            temperature=temperature,
        )
        return response.content[0].text

    def _fallback_generate(self, messages) -> str:
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        return (
            "I'm currently running in demo mode without an AI API key configured. "
            f"Based on your question about '{last_user[:100]}', please configure "
            "OPENAI_API_KEY or ANTHROPIC_API_KEY for full AI responses."
        )
