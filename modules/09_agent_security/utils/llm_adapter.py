"""Local LLM adapter for Module 9 agent decisions."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class LLMConfig:
    model_name: str = "distilgpt2"
    max_new_tokens: int = 120
    temperature: float = 0.2


class LocalLLMAdapter:
    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig()
        self._generator = None
        self._load_error = None
        try:
            from transformers import pipeline

            self._generator = pipeline("text-generation", model=self.config.model_name)
        except Exception as exc:
            self._load_error = str(exc)

    @property
    def available(self) -> bool:
        return self._generator is not None

    def generate(self, prompt: str) -> str:
        if not self.available:
            return ""
        pad_token_id = None
        try:
            pad_token_id = self._generator.tokenizer.eos_token_id
        except Exception:
            pad_token_id = None
        out = self._generator(
            prompt,
            max_new_tokens=self.config.max_new_tokens,
            temperature=self.config.temperature,
            do_sample=self.config.temperature > 0,
            truncation=True,
            pad_token_id=pad_token_id,
        )
        return out[0]["generated_text"][len(prompt) :].strip()

    def generate_json(self, prompt: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        text = self.generate(prompt)
        if not text:
            return fallback

        # Prefer explicit JSON object in the output.
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return fallback
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except Exception:
            return fallback
