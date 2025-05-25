import SimpleLLM.language.llm_providers.openai_llm as openai_llm
import SimpleLLM.language.llm_providers.openrouter_llm as openrouter_llm
from enum import Enum


class LLMProvider(Enum):
    OPENAI = 1
    OPENROUTER = 2


class LLM:
    def __init__(self, provider=LLMProvider.OPENAI, model_name="gpt-3.5-turbo", temperature=0.7, top_p=1.0, max_tokens=2000):
        self.provider = provider
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens

    @staticmethod
    def create(provider=LLMProvider.OPENAI, model_name="gpt-3.5-turbo", temperature=0.7, top_p=1.0, max_tokens=2000):
        """Factory method to create an LLM instance."""
        return LLM(provider, model_name, temperature, top_p, max_tokens)

    def generate_text(self, user_prompt, system_prompt=""):
        """Generate text using the specified LLM provider."""
        if self.provider == LLMProvider.OPENAI:
            return openai_llm.generate_text(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                model=self.model_name,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens
            )
        elif self.provider == LLMProvider.OPENROUTER:
            return openrouter_llm.generate_text(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                model=self.model_name,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate_text_stream(self, user_prompt, system_prompt=""):
        """Generate streaming text using the specified LLM provider."""
        if self.provider == LLMProvider.OPENAI:
            return openai_llm.generate_text_stream(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                model=self.model_name,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens
            )
        elif self.provider == LLMProvider.OPENROUTER:
            return openrouter_llm.generate_text_stream(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                model=self.model_name,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
