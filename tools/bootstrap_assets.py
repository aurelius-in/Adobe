import os
from pathlib import Path
from PIL import Image, ImageDraw
import httpx


ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
LOGO_PATH = ASSETS_DIR / "logos" / "brand_logo.png"
FONT_PATH = ASSETS_DIR / "fonts" / "NotoSans-Regular.ttf"


def ensure_dirs() -> None:
    (ASSETS_DIR / "source").mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / "logos").mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / "fonts").mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs").mkdir(parents=True, exist_ok=True)
    (ROOT / "runs").mkdir(parents=True, exist_ok=True)


def create_placeholder_logo(path: Path) -> None:
    if path.exists():
        return
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Simple roundel with brand primary color (#FF3A2E)
    draw.ellipse([(16, 16), (240, 240)], fill=(255, 58, 46, 255))
    draw.rectangle([(108, 64), (148, 192)], fill=(255, 255, 255, 255))
    img.save(path)


def download_font(path: Path) -> None:
    if path.exists():
        return
    url = (
        "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/"
        "NotoSans/NotoSans-Regular.ttf"
    )
    try:
        with httpx.Client(timeout=20) as client:
            r = client.get(url)
            r.raise_for_status()
            path.write_bytes(r.content)
    except Exception:
        # Leave missing; runtime can fall back to PIL default font
        pass


def create_gitkeeps() -> None:
    for rel in [
        "assets/source/.gitkeep",
        "outputs/.gitkeep",
        "runs/.gitkeep",
    ]:
        p = ROOT / rel
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("")


def main() -> None:
    ensure_dirs()
    create_placeholder_logo(LOGO_PATH)
    download_font(FONT_PATH)
    create_gitkeeps()


if __name__ == "__main__":
    main()


