from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple


def now_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_run_dirs(run_id: str, json_logs: bool = False) -> Tuple[Path, Path | None]:
    run_dir = Path("runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "run.log" if json_logs else None
    if log_path:
        log_path.touch(exist_ok=True)
    return run_dir, log_path


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # slightly verbose on purpose; readability > clever
    txt = json.dumps(data, indent=2, ensure_ascii=False)
    path.write_text(txt)


