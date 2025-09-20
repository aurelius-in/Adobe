from __future__ import annotations

from __future__ import annotations

import json
from colorsys import rgb_to_hsv
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image

from app.models import Brief


def _hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    s = hex_str.strip().lstrip("#")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _pct_primary_coverage(img: Image.Image, primary_hex: str, tol: Dict[str, float]) -> float:
    # Downscale for speed
    small = img.convert("RGB").resize((min(200, img.width), int(img.height * (min(200, img.width) / img.width))), Image.BILINEAR)
    # heads-up: HSV buckets are a little blunt — gradients can slip thru
    target_rgb = _hex_to_rgb(primary_hex)
    tr, tg, tb = target_rgb
    th, ts, tv = rgb_to_hsv(tr / 255.0, tg / 255.0, tb / 255.0)
    th = th * 360.0
    htol = float(tol.get("h", 10))
    stol = float(tol.get("s", 35)) / 100.0
    vtol = float(tol.get("v", 35)) / 100.0

    def in_tol(r: int, g: int, b: int) -> bool:
        h, s, v = rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        h = h * 360.0
        # Hue wrap-around
        dh = min(abs(h - th), 360.0 - abs(h - th))
        return (dh <= htol) and (abs(s - ts) <= stol) and (abs(v - tv) <= vtol)

    pixels = list(small.getdata())
    matches = sum(1 for (r, g, b) in pixels if in_tol(r, g, b))
    return (matches / max(1, len(pixels))) * 100.0


def score_compliance(brief: Brief, brand_rules: Dict, reporter) -> Dict[str, float]:
    brand_cfg = brand_rules.get("brand", {})
    logo_min = float(brand_cfg.get("logo_area_pct_min", 3))
    logo_max = float(brand_cfg.get("logo_area_pct_max", 6))
    primary_hex = brand_cfg.get("primary_hex", "#000000")
    hsv_tol = brand_cfg.get("hsv_tolerance", {"h": 10, "s": 35, "v": 35})

    per_variant_scores: List[float] = []
    for v in getattr(reporter, "variants", []):
        # Load provenance
        prov_path = Path(str(v.path_post) + ".prov.json")
        logo_pct = None
        if prov_path.exists():
            try:
                prov = json.loads(prov_path.read_text(encoding="utf-8"))
                logo_pct = prov.get("logo_area_pct")
            except Exception:
                pass

        score = 100.0
        if logo_pct is not None:
            if logo_pct < logo_min:
                score -= min(20.0, (logo_min - logo_pct) * 4)
            if logo_pct > logo_max:
                score -= min(20.0, (logo_pct - logo_max) * 4)

        # Primary color coverage heuristic
        try:
            with Image.open(v.path_post) as im:
                pct = _pct_primary_coverage(im, primary_hex, hsv_tol)
            # Penalize if primary color coverage extremely low (<3%)
            if pct < 3.0:
                score -= 10.0
        except Exception:
            pass

        per_variant_scores.append(max(0.0, min(100.0, score)))

    avg = sum(per_variant_scores) / max(1, len(per_variant_scores))
    mn = min(per_variant_scores) if per_variant_scores else 0.0
    summary = {"avg": round(avg, 2), "min": round(mn, 2)}
    reporter.set_compliance(summary)
    return summary


