from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
from PIL import Image


class ProviderError(Exception):
    pass


@dataclass
class GenerateResult:
    image: Image.Image
    metadata: Dict[str, Any]


class BaseProvider(ABC):
    name: str = "base"

    @abstractmethod
    def health_check(self) -> bool:
        ...

    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        size: Tuple[int, int],
        seed: Optional[int] = None,
        style_ref: Optional[bytes] = None,
        negative_prompt: Optional[str] = None,
    ) -> GenerateResult:
        ...


