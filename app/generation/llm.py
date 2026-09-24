"""Claude/GPT API wrapper for answer generation."""

from app.config import settings
from app.generation.prompt_templates import RAG_SYSTEM_PROMPT, build_rag_prompt


class LLMClient:
    def __init__(self, provider: str = None, model: str = None):
        self.provider = provider or settings.LLM_PROVIDER
        self.model = model or settings.LLM_MODEL
        self._client = self._build_client()

    def _build_client(self):
        if self.provider == "anthropic":
            import anthropic

            return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        if self.provider == "openai":
            from openai import OpenAI

            return OpenAI(api_key=settings.OPENAI_API_KEY)
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate_answer(self, question: str, chunks: list[dict], max_tokens: int = 1000) -> str:
        prompt = build_rag_prompt(question, chunks)

        if self.provider == "anthropic":
            response = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=RAG_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text

        if self.provider == "openai":
            response = self._client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": RAG_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content

        raise ValueError(f"Unsupported LLM provider: {self.provider}")