from __future__ import annotations

import asyncio
import os
from typing import Optional, Tuple

import httpx
from PIL import Image

from .base import BaseProvider, GenerateResult, ProviderError


class FireflyProvider(BaseProvider):
    name = "firefly"

    def __init__(self, api_key: str, workspace_id: str | None = None) -> None:
        self.api_key = api_key
        self.workspace_id = workspace_id

    def health_check(self) -> bool:
        return bool(self.api_key)

    async def _generate_async(
        self,
        prompt: str,
        size: Tuple[int, int],
        seed: Optional[int] = None,
        style_ref: Optional[bytes] = None,
        negative_prompt: Optional[str] = None,
    ) -> GenerateResult:
        # Placeholder async structure for Firefly v3; requires real endpoint wiring.
        # Intentionally not performing network calls in this repository.
        raise ProviderError(
            "FireflyProvider called without concrete API integration in this local build. "
            "Use provider=mock for offline runs."
        )

    def generate_image(
        self,
        prompt: str,
        size: Tuple[int, int],
        seed: Optional[int] = None,
        style_ref: Optional[bytes] = None,
        negative_prompt: Optional[str] = None,
    ) -> GenerateResult:
        try:
            return asyncio.run(
                self._generate_async(
                    prompt=prompt,
                    size=size,
                    seed=seed,
                    style_ref=style_ref,
                    negative_prompt=negative_prompt,
                )
            )
        except RuntimeError:
            # Event loop already running (e.g., Streamlit). Provide a clear error.
            raise ProviderError(
                "Firefly async generation requires integration; not supported in UI loop."
            )


