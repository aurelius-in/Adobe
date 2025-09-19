from __future__ import annotations

import hashlib
import random
from typing import Any, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from .base import BaseProvider, GenerateResult


class MockProvider(BaseProvider):
    name = "mock"

    def __init__(self) -> None:
        try:
            self.font = ImageFont.truetype("assets/fonts/NotoSans-Regular.ttf", 28)
        except Exception:
            self.font = ImageFont.load_default()

    def health_check(self) -> bool:
        return True

    def _bg_from_seed(self, seed: Optional[int]) -> Tuple[int, int, int]:
        if seed is None:
            rnd = random.Random(1234)
        else:
            rnd = random.Random(seed)
        return (rnd.randint(32, 224), rnd.randint(32, 224), rnd.randint(32, 224))

    def generate_image(
        self,
        prompt: str,
        size: Tuple[int, int],
        seed: Optional[int] = None,
        style_ref: Optional[bytes] = None,
        negative_prompt: Optional[str] = None,
    ) -> GenerateResult:
        width, height = size
        bg = self._bg_from_seed(seed)
        img = Image.new("RGB", (width, height), bg)
        draw = ImageDraw.Draw(img)
        text = f"{prompt[:60]}\n{width}x{height}\nseed={seed}"
        draw.multiline_text((24, 24), text, fill=(255, 255, 255), font=self.font, spacing=6)
        return GenerateResult(
            image=img,
            metadata={
                "provider": self.name,
                "seed": seed,
                "prompt": prompt,
                "size": {"width": width, "height": height},
            },
        )


