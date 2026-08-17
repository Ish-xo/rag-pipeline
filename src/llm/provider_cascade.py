import os
import time
import asyncio
import logging
from typing import List, AsyncGenerator, Tuple, Optional
from dotenv import load_dotenv

from src.llm.prompts import ULTRON_RAG_SYSTEM_PROMPT, ULTRON_RAG_USER_PROMPT
from src.llm.harness import ResilienceHarness
from src.llm.schemas import SourceCitation

load_dotenv()
logger = logging.getLogger("ultron.provider_cascade")

class LLMProviderCascade:
    """
    Sequential LLM Failover Cascade:
    1. Groq (llama-3.3-70b-versatile) - Primary low-latency provider
    2. Cerebras (llama-3.3-70b) - High-throughput fallback
    3. Google Gemini (gemini-2.5-flash) - Reliable fallback
    4. Mock / Graceful Fallback - Emergency response if all providers fail
    """
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.cerebras_api_key = os.getenv("CEREBRAS_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.harness = ResilienceHarness(max_retries=1, base_delay=0.1)

    async def _call_groq(self, prompt: str) -> str:
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not configured")
        
        from groq import AsyncGroq
        client = AsyncGroq(api_key=self.groq_api_key)
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": ULTRON_RAG_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()

    async def _stream_groq(self, prompt: str) -> AsyncGenerator[str, None]:
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not configured")
        
        from groq import AsyncGroq
        client = AsyncGroq(api_key=self.groq_api_key)
        stream = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": ULTRON_RAG_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=300,
            stream=True
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def _call_cerebras(self, prompt: str) -> str:
        if not self.cerebras_api_key:
            raise ValueError("CEREBRAS_API_KEY not configured")
        
        from cerebras.cloud.sdk import AsyncCerebras
        client = AsyncCerebras(api_key=self.cerebras_api_key)
        response = await client.chat.completions.create(
            model="llama-3.3-70b",
            messages=[
                {"role": "system", "content": ULTRON_RAG_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()

    async def _stream_cerebras(self, prompt: str) -> AsyncGenerator[str, None]:
        if not self.cerebras_api_key:
            raise ValueError("CEREBRAS_API_KEY not configured")
        
        from cerebras.cloud.sdk import AsyncCerebras
        client = AsyncCerebras(api_key=self.cerebras_api_key)
        stream = await client.chat.completions.create(
            model="llama-3.3-70b",
            messages=[
                {"role": "system", "content": ULTRON_RAG_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=300,
            stream=True
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def _call_gemini(self, prompt: str) -> str:
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        # Using google-genai or google.generativeai
        try:
            from google import genai
            client = genai.Client(api_key=self.google_api_key)
            full_prompt = f"{ULTRON_RAG_SYSTEM_PROMPT}\n\n{prompt}"
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
            )
            return response.text.strip()
        except ImportError:
            import google.generativeai as genai
            genai.configure(api_key=self.google_api_key)
            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=ULTRON_RAG_SYSTEM_PROMPT)
            response = await asyncio.to_thread(model.generate_content, prompt)
            return response.text.strip()

    async def generate_answer(
        self, query_text: str, context_passages: List[SourceCitation]
    ) -> Tuple[str, str, float]:
        """
        Runs the sequential LLM failover cascade for non-streaming response.
        Returns: (answer_text, provider_name, execution_time_ms)
        """
        start_time = time.time()

        # Format context passages
        formatted_context = "\n".join(
            [f"[{c.id}] {c.text}" for c in context_passages]
        ) if context_passages else "No relevant context found."

        user_prompt = ULTRON_RAG_USER_PROMPT.format(
            context_passages=formatted_context, query_text=query_text
        )

        providers = [
            ("Groq", self._call_groq),
            ("Cerebras", self._call_cerebras),
            ("Gemini", self._call_gemini),
        ]

        for provider_name, func in providers:
            try:
                logger.info(f"Attempting LLM generation via '{provider_name}'...")
                answer = await self.harness.execute(
                    provider_name, lambda f=func: f(user_prompt)
                )
                elapsed_ms = (time.time() - start_time) * 1000
                logger.info(f"LLM generation succeeded via '{provider_name}' in {elapsed_ms:.1f}ms")
                return answer, provider_name, elapsed_ms
            except Exception as e:
                logger.warning(f"LLM Provider '{provider_name}' failed: {e}")

        # Emergency Fallback if all API calls fail or no keys are configured
        elapsed_ms = (time.time() - start_time) * 1000
        fallback_answer = (
            f"Based on the provided documents: " +
            (context_passages[0].text[:150] + "..." if context_passages else "No context available.")
        )
        logger.warning("All core LLM providers failed or unconfigured. Returned fallback response.")
        return fallback_answer, "Fallback/Offline", elapsed_ms

    async def generate_stream(
        self, query_text: str, context_passages: List[SourceCitation]
    ) -> AsyncGenerator[Tuple[str, str], None]:
        """
        Yields (token_chunk, provider_name) in real time for low TTFT latency.
        Falls back sequentially if stream creation fails.
        """
        formatted_context = "\n".join(
            [f"[{c.id}] {c.text}" for c in context_passages]
        ) if context_passages else "No relevant context found."

        user_prompt = ULTRON_RAG_USER_PROMPT.format(
            context_passages=formatted_context, query_text=query_text
        )

        # Try Groq streaming first
        if self.groq_api_key and not self.harness.get_breaker("Groq").is_open():
            try:
                async for chunk in self._stream_groq(user_prompt):
                    yield chunk, "Groq"
                return
            except Exception as e:
                logger.warning(f"Groq streaming failed: {e}")

        # Try Cerebras streaming next
        if self.cerebras_api_key and not self.harness.get_breaker("Cerebras").is_open():
            try:
                async for chunk in self._stream_cerebras(user_prompt):
                    yield chunk, "Cerebras"
                return
            except Exception as e:
                logger.warning(f"Cerebras streaming failed: {e}")

        # Fallback to non-streaming generate_answer if streaming fails
        answer, provider_name, _ = await self.generate_answer(query_text, context_passages)
        yield answer, provider_name
