from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml

from app.models import Brief


def load_brief_and_rules(brief_path: Path) -> Tuple[Brief, Dict[str, Any]]:
    raw = json.loads(Path(brief_path).read_text(encoding="utf-8"))
    brief = Brief(**raw)
    rules = yaml.safe_load(Path("brand/brand_rules.yaml").read_text(encoding="utf-8"))
    return brief, rules


