from __future__ import annotations

from pathlib import Path
from typing import Dict

from PIL import Image

from app.models import Brief


def _logo_area_pct(img_path: Path, logo_area_bounds: tuple[int, int]) -> float:
    # This placeholder assumes logo was resized targeting the mid of min/max.
    # Real implementation would measure the composited logo area.
    return float(sum(logo_area_bounds) / 2)


def score_compliance(brief: Brief, brand_rules: Dict, reporter) -> Dict[str, float]:
    # Minimal placeholder scoring; extend with color coverage and contrast stats
    logo_min = float(brand_rules.get("brand", {}).get("logo_area_pct_min", 3))
    logo_max = float(brand_rules.get("brand", {}).get("logo_area_pct_max", 6))
    score = 90.0
    reasons = []
    reporter.set_compliance({"score": score})
    return {"score": score}


