from __future__ import annotations

import os
from typing import Optional, Tuple

from PIL import Image

from .base import BaseProvider, GenerateResult, ProviderError
import io
import base64
import os
try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


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
        if OpenAI is None:
            raise ProviderError("openai package not installed")
        api_key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ProviderError("OPENAI_API_KEY not set")

        client = OpenAI(api_key=api_key)
        # OpenAI image API expects square sizes like 256|512|1024
        # Pick the smaller side for cost; compositor will resize/crop later
        target = min(size[0], size[1])
        target = 1024 if target >= 1024 else 512 if target >= 512 else 256

        # Seed support may vary; include it if available via extra headers/params later
        prompt_text = prompt
        try:
            resp = client.images.generate(
                model="gpt-image-1",
                prompt=prompt_text,
                size=f"{target}x{target}",
            )
        except Exception as e:  # pragma: no cover
            raise ProviderError(str(e))

        # Decode base64 image
        try:
            b64 = resp.data[0].b64_json  # type: ignore[attr-defined]
            img_bytes = base64.b64decode(b64)
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        except Exception as e:  # pragma: no cover
            raise ProviderError(f"Failed to decode OpenAI image: {e}")

        return GenerateResult(image=img, metadata={"size": target})


