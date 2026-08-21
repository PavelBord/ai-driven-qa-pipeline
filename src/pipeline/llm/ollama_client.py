from __future__ import annotations

import httpx

from pipeline.llm.client import LLMClient


class OllamaClient(LLMClient):
    """LLM client for local Ollama server."""

    def __init__(
        self,
        model: str = "gemma4:12b",
        base_url: str = "http://localhost:11434",
        timeout: float = 180.0,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=timeout)

    def generate(
        self,
        prompt: str,
        json_mode: bool = False,
    ) -> str:

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0,
                "num_predict": 1500,
            },
        }

        if json_mode:
            payload["format"] = "json"

        response = self.client.post(
            f"{self.base_url}/api/generate",
            json=payload,
        )

        response.raise_for_status()

        data = response.json()

        result = data.get("response")

        if not isinstance(result, str):
            raise TypeError(
                "Ollama returned invalid response"
            )

        if not result.strip():
            raise ValueError(
                "Ollama returned empty response"
            )

        return result