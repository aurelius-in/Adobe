from __future__ import annotations

from typing import Dict


def localize_text(blob_by_locale: Dict[str, str], locale: str) -> str:
    if locale in blob_by_locale:
        return blob_by_locale[locale]
    # Fallback: first available
    for _, txt in blob_by_locale.items():
        return txt
    return ""


