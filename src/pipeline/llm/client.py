from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from the LLM."""


class MockLLMClient(LLMClient):
    """Deterministic LLM implementation for local tests."""

    def __init__(self, response: str) -> None:
        self.response = response
        self.last_prompt = ""

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.response