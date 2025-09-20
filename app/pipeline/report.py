from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

from app.models import RunReport, VariantResult
from .utils import write_json


@dataclass
class RunContext:
    run_id: str
    provider: str


class RunReporter:
    def __init__(self, ctx: RunContext) -> None:
        self.ctx = ctx
        self.variants: List[VariantResult] = []
        self.compliance: Dict[str, float] = {}
        self.legal_flags: List[str] = []
        self.timings_ms: Dict[str, float] = {}
        # tiny nit: timings_ms is not fully populated yet — left for later

    def add_variant(self, v: VariantResult) -> None:
        self.variants.append(v)

    def add_legal_flags(self, flags: List[str]) -> None:
        self.legal_flags.extend(flags)

    def set_compliance(self, scores: Dict[str, float]) -> None:
        self.compliance = scores

    def finalize(self, out_root: Path) -> None:
        totals = {
            "variants": len(self.variants),
        }
        self._report = RunReport(
            run_id=self.ctx.run_id,
            provider=self.ctx.provider,
            totals=totals,
            variants=self.variants,
            compliance=self.compliance,
            legal_flags=self.legal_flags,
        )

        # CSV
        csv_path = Path("runs") / self.ctx.run_id / "report.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "campaign_id",
                    "product_id",
                    "ratio",
                    "locale",
                    "seed",
                    "path_post",
                    "path_hero",
                    "provider",
                ],
            )
            writer.writeheader()
            for v in self.variants:
                writer.writerow(v.model_dump())

    def save(self, run_dir: Path) -> None:
        write_json(run_dir / "report.json", self._report.model_dump())


