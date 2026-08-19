from __future__ import annotations

import httpx

from pipeline.llm.client import LLMClient


class OllamaClient(LLMClient):
    """LLM client for a local Ollama server."""

    def __init__(self,model: str = "qwen3.5:9b",
        base_url: str = "http://localhost:11434",
        timeout: float = 120.0,
        client: httpx.Client | None = None) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=180.0)

    def generate(self, prompt: str) -> str:
        response = self.client.post(f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "think": False,
                "options": {
                    "temperature": 0,
                    "num_predict": 1500,
                },
            },
        )

        response.raise_for_status()

        data = response.json()

        result = data.get("response")


        if not isinstance(result, str):
            raise TypeError("Ollama returned an invalid response.")

        if not result.strip():
            raise ValueError("Ollama returned empty response.")

        return result