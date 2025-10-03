from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml

from app.models import Brief


def _deep_update(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k] = _deep_update(base[k], v)
        else:
            base[k] = v
    return base


def load_brief_and_rules(brief_path: Path) -> Tuple[Brief, Dict[str, Any]]:
    raw = json.loads(Path(brief_path).read_text(encoding="utf-8"))
    brief = Brief(**raw)
    # Load default rules, then merge local overrides if present
    base_rules = yaml.safe_load(Path("brand/brand_rules.yaml").read_text(encoding="utf-8")) or {}
    local_path = Path("brand/brand_rules.local.yaml")
    if local_path.exists():
        local_rules = yaml.safe_load(local_path.read_text(encoding="utf-8")) or {}
        rules = _deep_update(base_rules, local_rules)
    else:
        rules = base_rules
    return brief, rules


