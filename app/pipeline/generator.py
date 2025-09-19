from __future__ import annotations

import os
from typing import List, Tuple

from app.models import Brief, Product
from .adapters.base import BaseProvider
from .adapters.mock import MockProvider
from .adapters.firefly import FireflyProvider
from .adapters.openai_images import OpenAIImagesProvider


def select_provider(name: str) -> BaseProvider:
    name = (name or "auto").lower()

    candidates: List[BaseProvider]
    # Placeholders for future: Firefly, OpenAI
    firefly_key = os.getenv("FIREFLY_API_KEY")
    firefly_ws = os.getenv("FIREFLY_WORKSPACE_ID")
    openai_key = os.getenv("OPENAI_API_KEY")
    firefly_provider: BaseProvider | None = FireflyProvider(firefly_key, firefly_ws) if firefly_key else None
    openai_provider: BaseProvider | None = OpenAIImagesProvider(openai_key) if openai_key else None
    mock_provider = MockProvider()

    if name == "firefly":
        return mock_provider if not firefly_provider else firefly_provider
    if name == "openai":
        return mock_provider if not openai_provider else openai_provider
    if name == "mock":
        return mock_provider

    # auto order: Firefly -> OpenAI -> Mock
    for p in [firefly_provider, openai_provider, mock_provider]:
        if p and p.health_check():
            return p
    return mock_provider


def build_prompt(brief: Brief, product: Product, locale: str) -> str:
    msg = brief.message.get(locale) or next(iter(brief.message.values()))
    hints = product.prompt_hints or ""
    return f"{brief.brand} {product.name}: {msg}. {hints}".strip()


