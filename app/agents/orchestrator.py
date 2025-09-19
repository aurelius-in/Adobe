from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from app.pipeline.ingest import load_brief_and_rules
from app.pipeline.generator import select_provider
from app.pipeline.compositor import compose_variants
from app.pipeline.report import RunContext, RunReporter


@dataclass
class OrchestratorConfig:
    briefs_dir: Path = Path("briefs")
    poll_seconds: int = 15
    output_dir: Path = Path("outputs")


class Orchestrator:
    def __init__(self, cfg: OrchestratorConfig) -> None:
        self.cfg = cfg
        self._seen: set[str] = set()

    def _status_path(self) -> Path:
        return Path("runs") / "status.json"

    def _write_status(self, data: Dict) -> None:
        p = self._status_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2))

    def run_once(self) -> None:
        briefs = sorted(self.cfg.briefs_dir.glob("*.json"))
        status: Dict[str, Dict] = json.loads(self._status_path().read_text()) if self._status_path().exists() else {}
        for b in briefs:
            if b.name in self._seen:
                continue
            brief, rules = load_brief_and_rules(b)
            provider = select_provider("auto")
            reporter = RunReporter(RunContext(run_id=str(int(time.time())), provider=provider.name))
            compose_variants(
                brief,
                rules,
                provider,
                brief.aspect_ratios,
                brief.locales,
                self.cfg.output_dir,
                reporter,
                max_variants=1,
                seed=1234,
            )
            reporter.finalize(self.cfg.output_dir)
            status[brief.campaign_id] = {
                "provider": provider.name,
                "variants": reporter._report.totals.get("variants", 0),
            }
            self._seen.add(b.name)
        self._write_status(status)

    def start(self, max_iterations: int | None = None) -> None:
        i = 0
        while True:
            self.run_once()
            i += 1
            if max_iterations is not None and i >= max_iterations:
                break
            time.sleep(self.cfg.poll_seconds)


