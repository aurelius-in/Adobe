from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, ValidationError, model_validator


class Product(BaseModel):
    id: str
    name: str
    prompt_hints: Optional[str] = None
    base_asset: Optional[str] = Field(default=None, description="Path to existing asset")


class BrandPalette(BaseModel):
    primary_hex: str
    secondary_hex: Optional[str] = None


class Brief(BaseModel):
    campaign_id: str
    brand: str
    markets: List[str]
    audience: str
    locales: List[str]
    aspect_ratios: List[str]
    message: Dict[str, str]
    call_to_action: Dict[str, str]
    brand_palette: BrandPalette
    products: List[Product]

    @model_validator(mode="after")
    def validate_required_locales(self) -> "Brief":
        for loc in self.locales:
            if loc not in self.message:
                raise ValueError(f"Missing message for locale {loc}")
            if loc not in self.call_to_action:
                raise ValueError(f"Missing call_to_action for locale {loc}")
        return self


class VariantSpec(BaseModel):
    ratio: str
    width: int
    height: int


class VariantResult(BaseModel):
    campaign_id: str
    product_id: str
    ratio: str
    locale: str
    seed: Optional[int] = None
    path_post: str
    path_hero: Optional[str] = None
    provider: str


class RunReport(BaseModel):
    run_id: str
    provider: str
    totals: Dict[str, int]
    variants: List[VariantResult]
    compliance: Dict[str, float] = Field(default_factory=dict)
    legal_flags: List[str] = Field(default_factory=list)


