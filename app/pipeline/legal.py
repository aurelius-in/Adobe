from __future__ import annotations

from pathlib import Path
from typing import List

from app.models import Brief


def scan_legal(brief: Brief, reporter) -> List[str]:
    words = [w.strip().lower() for w in Path("legal/prohibited_words.txt").read_text(encoding="utf-8").splitlines() if w.strip()]
    text_blobs = []
    text_blobs.extend(brief.message.values())
    text_blobs.extend(brief.call_to_action.values())
    haystack = "\n".join(text_blobs).lower()
    hits = sorted({w for w in words if w and w in haystack})
    reporter.add_legal_flags(hits)
    return hits


