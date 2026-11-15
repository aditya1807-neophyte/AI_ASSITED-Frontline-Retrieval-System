# -*- coding: utf-8 -*-
"""
Interchangeable language-model provider for the RAG pipeline.

Supports Google Gemini, OpenAI-compatible, and Mock providers with
environment-based configuration. No hardcoded API keys.

Configuration:
- LLM_PROVIDER: "gemini", "openai", or "mock" (default: "gemini")
- GEMINI_API_KEY: Google Gemini API key (placeholder supported in .env)
- GEMINI_MODEL: Model identifier (default: "gemini-1.5-flash")
- OPENAI_API_KEY: API key for OpenAI-compatible providers
- OPENAI_API_URL: Custom API URL (optional)
- LLM_MODEL: Model identifier for OpenAI (default: "gpt-4o-mini")
"""

import os
import re
import json
import logging
import requests
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from app.core.config import get_settings

logger = logging.getLogger(__name__)

PLACEHOLDER_KEYS = {
    "",
    "your_gemini_api_key_here",
    "your_gemini_api_key",
    "YOUR_GEMINI_API_KEY",
    "your_api_key_here",
    "placeholder",
    "EMPTY",
    "none",
}


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @property
    def is_configured(self) -> bool:
        return bool(self._is_valid_config())

    @property
    def is_available(self) -> bool:
        return self.is_configured and self._check_availability()

    @abstractmethod
    def _is_valid_config(self) -> bool:
        pass

    @abstractmethod
    def _check_availability(self) -> bool:
        pass

    @abstractmethod
    def generate(self, prompt: str, context: str, query: str, api_key: Optional[str] = None) -> str:
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini API provider (supports gemini-1.5-flash, gemini-2.0-flash, etc.)."""

    def _get_model(self) -> str:
        model = (
            os.getenv("GEMINI_MODEL")
            or self.config.get("model")
            or getattr(get_settings(), "gemini_model", None)
            or "gemini-3.5-flash"
        ).strip()
        # Automatically upgrade deprecated / unavailable model identifiers
        if model in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"]:
            return "gemini-3.5-flash"
        return model

    def _get_api_key(self) -> str:
        # Check config, then environment variables, then settings
        key = (
            self.config.get("api_key")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("VITE_GEMINI_API_KEY")
            or ""
        )
        if not key or key in PLACEHOLDER_KEYS:
            settings = get_settings()
            key = getattr(settings, "gemini_api_key", None) or getattr(settings, "vite_gemini_api_key", None) or ""
        return (key or "").strip()

    def _is_valid_config(self, key: Optional[str] = None) -> bool:
        k = key if key is not None else self._get_api_key()
        return bool(k and k not in PLACEHOLDER_KEYS and not k.lower().startswith("your_"))

    def _check_availability(self) -> bool:
        # Availability is true if valid non-placeholder key is provided
        return self._is_valid_config()

    def generate(self, prompt: str, context: str, query: str, api_key: Optional[str] = None) -> str:
        """Generate response via Google Gemini API with automatic model fallback."""
        active_key = (api_key or "").strip() or self._get_api_key()
        if not self._is_valid_config(active_key):
            return self._create_placeholder_response(context, query)

        primary_model = self._get_model()
        # Models to try in order of preference
        candidate_models = [primary_model, "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
        seen = set()
        models_to_try = [m for m in candidate_models if m and not (m in seen or seen.add(m))]

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": f"Context from retrieved documents:\n{context}\n\nUser Question:\n{query}"
                        }
                    ],
                }
            ],
            "systemInstruction": {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            },
            "generationConfig": {
                "temperature": float(self.config.get("temperature", 0.2)),
                "maxOutputTokens": int(self.config.get("max_tokens", 2048)),
                "responseMimeType": "application/json",
            },
        }

        last_error = None
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={active_key}"
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=25)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            raw_text = parts[0].get("text", "")
                            return raw_text

                # If status is not 200, try next model
                err_detail = ""
                try:
                    err_json = response.json()
                    err_detail = err_json.get("error", {}).get("message", response.text)
                except Exception:
                    err_detail = response.text
                logger.warning(f"Model {model} returned {response.status_code}: {err_detail}. Trying fallback...")
                last_error = f"Gemini ({model}): {err_detail}"
            except Exception as e:
                logger.warning(f"Error querying {model}: {e}. Trying fallback...")
                last_error = str(e)

        raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

    def _create_placeholder_response(self, context: str, query: str) -> str:
        """Create structured response when Gemini API key is placeholder."""
        passages = [
            p.strip()
            for p in context.split("\n\n")
            if p.strip() and not p.strip().startswith("Query:")
        ]
        citations = [f"[source_{i + 1}]" for i in range(min(3, max(1, len(passages))))]
        top_snippet = "No specific passage retrieved."
        for p in passages:
            lines = [line.strip() for line in p.split("\n") if line.strip() and not line.startswith("(") and not line.startswith("---")]
            if lines:
                top_snippet = " ".join(lines)
                break

        if len(top_snippet) > 280:
            top_snippet = top_snippet[:280] + "..."

        return json.dumps({
            "direct_answer": f"Gemini API is integrated and ready! To activate live AI generation, please replace the placeholder 'your_gemini_api_key_here' with your real Google Gemini API key in the .env file.\n\nRetrieved knowledge: \"{top_snippet}\"",
            "citations": citations,
            "conditions": ["Set a valid GEMINI_API_KEY in .env to activate live Google Gemini generation."],
            "limitations": ["Live Gemini response paused: placeholder API key detected in .env."],
            "conflicts": [],
            "evidence_status": "supported_by_available_evidence" if passages else "insufficient_evidence",
            "next_action": "Add your Gemini API key to .env and ask again for live AI generated answers.",
        })


class OpenAICompatibleProvider(LLMProvider):
    """OpenAI-compatible provider (OpenAI, Azure, local servers)."""

    def _is_valid_config(self) -> bool:
        return bool(self.config.get("api_key") and self.config["api_key"] not in PLACEHOLDER_KEYS)

    def _check_availability(self) -> bool:
        try:
            url = self.config.get("api_url") or os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
            headers = {"Authorization": f"Bearer {self.config['api_key']}", "Content-Type": "application/json"}
            payload = {
                "model": self.config.get("model", "gpt-4o-mini"),
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 1,
                "temperature": 0,
            }
            response = requests.post(url, headers=headers, json=payload, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"LLM provider availability check failed: {e}")
            return False

    def generate(self, prompt: str, context: str, query: str, api_key: Optional[str] = None) -> str:
        try:
            active_key = (api_key or "").strip() or self.config.get("api_key")
            url = self.config.get("api_url") or os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
            headers = {"Authorization": f"Bearer {active_key}", "Content-Type": "application/json"}
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Context: " + context + "\n\nQuestion: " + query},
            ]
            payload = {
                "model": self.config.get("model", "gpt-4o-mini"),
                "messages": messages,
                "max_tokens": self.config.get("max_tokens", 1024),
                "temperature": self.config.get("temperature", 0.2),
            }
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for development and testing."""

    def _is_valid_config(self) -> bool:
        return True

    def _check_availability(self) -> bool:
        return True

    def generate(self, prompt: str, context: str, query: str, api_key: Optional[str] = None) -> str:
        return self._create_mock_response(context, query)

    def _create_mock_response(self, context: str, query: str) -> str:
        passages = [p.strip() for p in context.split("\n\n") if p.strip()]
        cited_sources = [f"[source_{i + 1}]" for i, p in enumerate(passages[:3])]

        return json.dumps({
            "direct_answer": "Based on the available evidence, here is the verified information from your knowledge base.",
            "citations": cited_sources,
            "conditions": ["Condition verified from retrieved evidence."],
            "limitations": ["Mock provider output."],
            "conflicts": [],
            "evidence_status": "supported_by_available_evidence",
            "next_action": "Review the cited sources and ask follow-up questions.",
        })


class ChatInterface:
    """Chat interface for the RAG pipeline with dynamic provider switching."""

    def __init__(self):
        self._cached_provider: Optional[LLMProvider] = None
        self._last_state: tuple = ()

    def _get_provider(self) -> LLMProvider:
        provider_name = (os.getenv("LLM_PROVIDER") or "").strip().lower()
        gemini_key = (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("VITE_GEMINI_API_KEY")
            or ""
        ).strip()
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()

        # If explicitly openai and key is present
        if provider_name == "openai" and openai_key and openai_key not in PLACEHOLDER_KEYS:
            return OpenAICompatibleProvider({
                "provider": "openai",
                "api_key": openai_key,
                "api_url": os.getenv("OPENAI_API_URL"),
                "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
                "max_tokens": 1024,
                "temperature": 0.2,
            })
        elif provider_name == "mock":
            return MockLLMProvider({
                "provider": "mock",
                "max_tokens": 1024,
                "temperature": 0.2,
            })
        else:
            # Default to GeminiProvider
            return GeminiProvider({
                "provider": "gemini",
                "api_key": gemini_key,
                "model": os.getenv("GEMINI_MODEL") or getattr(get_settings(), "gemini_model", "gemini-3.5-flash"),
                "max_tokens": 2048,
                "temperature": 0.2,
            })

    @property
    def llm_provider(self) -> LLMProvider:
        """Return dynamically updated provider so changes to .env take effect immediately."""
        current_state = (
            os.getenv("LLM_PROVIDER"),
            os.getenv("GEMINI_API_KEY"),
            os.getenv("GOOGLE_API_KEY"),
            os.getenv("VITE_GEMINI_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GEMINI_MODEL"),
        )
        if self._cached_provider is None or self._last_state != current_state:
            self._cached_provider = self._get_provider()
            self._last_state = current_state
        return self._cached_provider

    @llm_provider.setter
    def llm_provider(self, value: LLMProvider):
        self._cached_provider = value

    @property
    def is_configured(self) -> bool:
        return self.llm_provider.is_configured

    @property
    def is_available(self) -> bool:
        return self.llm_provider.is_available

    def generate(self, prompt: str, context: str, query: str, api_key: Optional[str] = None) -> str:
        """Compatibility method for direct generate call."""
        return self.generate_response(prompt, context, query, api_key=api_key)

    def generate_response(self, prompt: str, context: str, query: str, api_key: Optional[str] = None) -> str:
        """Generate a response using the configured provider."""
        provider = self.llm_provider
        # If provider is available (or custom api_key provided or Gemini in placeholder mode), generate
        if provider.is_available or api_key or isinstance(provider, GeminiProvider):
            return provider.generate(prompt, context, query, api_key=api_key)
        else:
            return self._extractive_summary(context, query)

    def _extractive_summary(self, context: str, query: str) -> str:
        """Generate extractive summary when AI is unavailable."""
        if not context.strip():
            return "No evidence was retrieved for this query. Try asking a more specific question or add documents to the knowledge base."

        passages = [p.strip() for p in context.split("\n\n") if p.strip()]
        if not passages:
            return "No relevant evidence found."

        top_passages = passages[:3]
        summary = "Based on the retrieved evidence:\n\n" + "\n\n".join(top_passages)

        if len(passages) > 3:
            summary += f"\n\n... (showing 3 of {len(passages)} relevant passages)"

        return summary


# Singleton chat interface
_chat_interface = None


def get_llm_provider() -> ChatInterface:
    """Get the singleton chat interface."""
    global _chat_interface
    if _chat_interface is None:
        _chat_interface = ChatInterface()
    return _chat_interface
