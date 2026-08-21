from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        json_mode: bool = False,
    ) -> str:
        pass