import logging
from typing import AsyncGenerator

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified LLM client supporting OpenAI, Claude, and fallback."""

    async def generate(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        if settings.OPENAI_API_KEY:
            return await self._openai_generate(messages, temperature, max_tokens)
        if settings.ANTHROPIC_API_KEY:
            return await self._claude_generate(messages, temperature, max_tokens)
        return await self._fallback_generate(messages)

    async def generate_stream(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        if settings.OPENAI_API_KEY:
            async for chunk in self._openai_stream(messages, temperature, max_tokens):
                yield chunk
        else:
            response = await self._fallback_generate(messages)
            yield response

    async def _openai_generate(self, messages, temperature, max_tokens) -> str:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    async def _openai_stream(self, messages, temperature, max_tokens) -> AsyncGenerator[str, None]:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        stream = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def _claude_generate(self, messages, temperature, max_tokens) -> str:
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_messages = [m for m in messages if m["role"] != "system"]
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            system=system,
            messages=user_messages,
            temperature=temperature,
        )
        return response.content[0].text

    async def _fallback_generate(self, messages) -> str:
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        return (
            "I'm currently running in demo mode without an AI API key configured. "
            f"Based on your question about '{last_user[:100]}', please configure "
            "OPENAI_API_KEY or ANTHROPIC_API_KEY for full AI responses."
        )
