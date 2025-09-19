from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from app.models import Brief, Product, VariantResult
from .adapters.base import BaseProvider
from .generator import build_prompt
from .utils import write_json


RATIO_TO_SIZE: Dict[str, Tuple[int, int]] = {
    "1:1": (1024, 1024),
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
}


def _relative_luminance(rgb: Tuple[int, int, int]) -> float:
    # sRGB to relative luminance
    def channel(c: int) -> float:
        v = c / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def _contrast_ratio(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
    l1 = _relative_luminance(c1)
    l2 = _relative_luminance(c2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def _compute_logo_size(canvas: Tuple[int, int], logo_img: Image.Image, area_pct: float) -> Tuple[int, int]:
    target_area = (canvas[0] * canvas[1]) * (area_pct / 100.0)
    aspect = logo_img.width / logo_img.height
    height = int((target_area / aspect) ** 0.5)
    width = int(height * aspect)
    return max(1, width), max(1, height)


def _cover_resize(img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    tw, th = target_size
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    resized = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def _draw_text_block(
    canvas: Image.Image,
    text_lines: List[str],
    font: ImageFont.FreeTypeFont,
    min_contrast: float,
    padding: int = 32,
) -> None:
    draw = ImageDraw.Draw(canvas, "RGBA")
    # Measure text block
    widths: List[int] = []
    heights: List[int] = []
    for line in text_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])
    text_w = max(widths) if widths else 0
    text_h = sum(heights) + (len(text_lines) - 1) * 8

    x = padding
    y = canvas.height - padding - text_h - 16

    # Sample background under text area to estimate contrast
    crop = canvas.crop((x, y, min(canvas.width - padding, x + text_w + 16), y + text_h + 16)).convert("RGB")
    avg = tuple(int(sum(channel) / len(channel)) for channel in zip(*list(crop.getdata())))
    text_color = (255, 255, 255)
    ratio = _contrast_ratio(text_color, avg)
    if ratio < min_contrast:
        # Draw translucent dark backdrop to lift contrast
        draw.rectangle((x - 12, y - 12, x + text_w + 24, y + text_h + 24), fill=(0, 0, 0, 180))
    # Draw lines
    line_y = y
    for line in text_lines:
        draw.text((x, line_y), line, fill=text_color, font=font)
        bbox = draw.textbbox((0, 0), line, font=font)
        line_h = bbox[3] - bbox[1]
        line_y += line_h + 8


def compose_variants(
    brief: Brief,
    brand_rules: Dict,
    provider: BaseProvider,
    ratios: Iterable[str],
    locales: Iterable[str],
    out_dir: Path,
    reporter,
    max_variants: int = 1,
    seed: Optional[int] = None,
    overlay_style: str = "banner",
) -> None:
    font_path = brand_rules.get("overlay", {}).get("text_font", "assets/fonts/NotoSans-Regular.ttf")
    try:
        font = ImageFont.truetype(font_path, 48)
    except Exception:
        font = ImageFont.load_default()
    logo_path = brand_rules.get("brand", {}).get("logo_path", "assets/logos/brand_logo.png")
    logo_img = Image.open(logo_path).convert("RGBA") if Path(logo_path).exists() else None
    min_contrast = float(brand_rules.get("overlay", {}).get("min_contrast_ratio", 4.5))

    for product in brief.products:
        for ratio in ratios:
            if ratio not in RATIO_TO_SIZE:
                continue
            size = RATIO_TO_SIZE[ratio]
            for loc in locales:
                for variant_index in range(max_variants):
                    # Create hero: reuse base_asset if available else generate
                    if product.base_asset and Path(product.base_asset).exists():
                        hero_src = Image.open(product.base_asset).convert("RGB")
                    else:
                        prompt = build_prompt(brief, product, loc)
                        gen = provider.generate_image(prompt=prompt, size=size, seed=(seed or 1234) + variant_index)
                        hero_src = gen.image.convert("RGB")
                    hero = _cover_resize(hero_src, size)

                    # Compose post by adding overlays and logo
                    post = hero.copy().convert("RGBA")
                    lines = [
                        brief.message.get(loc) or next(iter(brief.message.values())),
                        f"{brief.call_to_action.get(loc) or next(iter(brief.call_to_action.values()))}",
                    ]
                    _draw_text_block(post, lines, font, min_contrast=min_contrast)

                    if logo_img is not None:
                        area_pct = (brand_rules.get("brand", {}).get("logo_area_pct_min", 3)
                                    + brand_rules.get("brand", {}).get("logo_area_pct_max", 6)) / 2
                        lw, lh = _compute_logo_size(size, logo_img, area_pct)
                        logo_rs = logo_img.resize((lw, lh), Image.LANCZOS)
                        margin = max(16, min(size) // 40)
                        post.alpha_composite(logo_rs, dest=(size[0] - lw - margin, size[1] - lh - margin))

                    # Save files
                    base = out_dir / brief.campaign_id / product.id / ratio
                    base.mkdir(parents=True, exist_ok=True)
                    hero_path = base / "hero.png"
                    post_path = base / "post.png"
                    hero.save(hero_path, format="PNG")
                    post.convert("RGB").save(post_path, format="PNG")

                    # Provenance
                    prov = {
                        "provider": provider.name,
                        "product_id": product.id,
                        "ratio": ratio,
                        "locale": loc,
                    }
                    write_json(Path(str(post_path) + ".prov.json"), prov)

                    reporter.add_variant(
                        VariantResult(
                            campaign_id=brief.campaign_id,
                            product_id=product.id,
                            ratio=ratio,
                            locale=loc,
                            seed=seed,
                            path_post=str(post_path),
                            path_hero=str(hero_path),
                            provider=provider.name,
                        )
                    )


