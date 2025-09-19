from __future__ import annotations

from pathlib import Path
from typing import Union

from PIL import Image


def _is_remote(uri: str) -> bool:
    return uri.startswith("s3://") or uri.startswith("azure://") or uri.startswith("dropbox://")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_image(dest: Union[str, Path], img: Image.Image, format: str = "PNG") -> str:
    dest_str = str(dest)
    if _is_remote(dest_str):
        # Stubs for future cloud adapters
        raise NotImplementedError("Remote storage not implemented in local build")
    p = Path(dest_str)
    ensure_parent(p)
    img.save(p, format=format)
    return dest_str


def write_bytes(dest: Union[str, Path], data: bytes) -> str:
    dest_str = str(dest)
    if _is_remote(dest_str):
        raise NotImplementedError("Remote storage not implemented in local build")
    p = Path(dest_str)
    ensure_parent(p)
    p.write_bytes(data)
    return dest_str


