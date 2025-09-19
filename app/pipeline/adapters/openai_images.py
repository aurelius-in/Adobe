from __future__ import annotations

import os
from typing import Optional, Tuple

from PIL import Image

from .base import BaseProvider, GenerateResult, ProviderError


class OpenAIImagesProvider(BaseProvider):
    name = "openai"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def health_check(self) -> bool:
        return bool(self.api_key)

    def generate_image(
        self,
        prompt: str,
        size: Tuple[int, int],
        seed: Optional[int] = None,
        style_ref: Optional[bytes] = None,
        negative_prompt: Optional[str] = None,
    ) -> GenerateResult:
        # Placeholder to avoid external calls. Error to encourage Mock for local.
        raise ProviderError(
            "OpenAIImagesProvider not active in this local build. Use provider=mock."
        )


