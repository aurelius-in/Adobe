from __future__ import annotations
import json
import os
import subprocess
import time
import glob
import pathlib
from typing import Any, Dict


ROOT = pathlib.Path(__file__).resolve().parent.parent


def _latest_run_dir() -> pathlib.Path | None:
    runs = sorted(
        ROOT.joinpath("runs").glob("*"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    return runs[0] if runs else None


def _read_metrics_from_report() -> Dict[str, Dict[str, Any]]:
    """Parse runs/<ts>/report.json written by RunReporter.

    Schema per app/models.RunReport:
      {
        "run_id": str,
        "provider": str,
        "totals": {"variants": int},
        "variants": [
          {
            "campaign_id": str,
            "product_id": str,
            "ratio": str,
            "locale": str,
            "seed": int | null,
            "path_post": str,
            "path_hero": str | null,
            "provider": str
          }
        ],
        "compliance": {"avg": float, "min": float},
        "legal_flags": [str]
      }

    We derive metrics by reading the provenance sidecar next to each post path when available
    and mapping them by absolute asset path for quick lookup.
    """
    run_dir = _latest_run_dir()
    if not run_dir:
        return {}
    report = run_dir / "report.json"
    if not report.exists():
        return {}
    try:
        data = json.loads(report.read_text(encoding="utf-8"))
        variants = data.get("variants", [])
        out: Dict[str, Dict[str, Any]] = {}
        for v in variants:
            post_path = v.get("path_post") or ""
            if not post_path:
                continue
            prov_path = f"{post_path}.prov.json"
            metrics: Dict[str, Any] = {}
            try:
                if os.path.exists(prov_path):
                    prov = json.loads(pathlib.Path(prov_path).read_text(encoding="utf-8"))
                    # Normalize likely metrics fields we care about for scoring
                    if "logo_area_pct" in prov:
                        metrics["logo_area_pct"] = prov["logo_area_pct"] if prov["logo_area_pct"] is not None else 0
                    # Optional placeholders if other analyzers populate them later
                    if "contrast_ok" in prov:
                        metrics["contrast_ok"] = prov["contrast_ok"]
                    if "text_fit_ok" in prov:
                        metrics["text_fit_ok"] = prov["text_fit_ok"]
            except Exception:
                metrics = {}
            out[post_path] = metrics
        return out
    except Exception:
        return {}


def runner(
    brief: str = "briefs/sample_brief.json",
    out: str = "outputs",
    provider: str = "auto",
    seed: int = 1234,
    layout: str = "banner",
    ratio: str = "1:1",
) -> Dict[str, Any]:
    # Prefer in-process call to avoid shell/Click parsing issues on Windows
    try:
        import app.main as cli_main  # type: ignore

        cli_main.generate(
            brief=brief,
            out=out,
            provider=provider,
            ratios=ratio,
            locales="en-US",
            max_variants=1,
            seed=seed,
            overlay_style=layout,
            log_json=True,
        )
    except Exception:
        # Fallback to subprocess if direct call fails unexpectedly
        cmd = [
            "python",
            "-m",
            "app.main",
            "generate",
            "--brief",
            brief,
            "--out",
            out,
            "--provider",
            provider,
            "--ratios",
            ratio,
            "--locales",
            "en-US",
            "--max-variants",
            "1",
            "--seed",
            str(seed),
            "--overlay-style",
            layout,
            "--log-json",
        ]
        subprocess.run(cmd, check=True)
    # give filesystem a moment and then pull latest artifact
    time.sleep(0.2)
    metrics_by_path = _read_metrics_from_report()
    # find candidate image by latest post.png in outputs
    candidates = sorted(
        glob.glob(f"{out}/**/post.png", recursive=True),
        key=os.path.getmtime,
        reverse=True,
    )
    asset_path = candidates[0] if candidates else ""
    prov_path = asset_path + ".prov.json" if asset_path else ""
    metrics = metrics_by_path.get(asset_path, {})
    return {
        "asset_path": asset_path,
        "prov_path": prov_path,
        "metrics": metrics,
        "seed": seed,
        "adapter": provider,
    }


