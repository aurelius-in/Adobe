from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional, List

import typer


app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def generate(
    brief: Path = typer.Option(..., exists=True, readable=True, help="Path to brief JSON/YAML"),
    out: Path = typer.Option(Path("outputs"), help="Output directory"),
    provider: str = typer.Option(
        "auto",
        help="Provider: auto|firefly|openai|mock",
        case_sensitive=False,
    ),
    ratios: str = typer.Option("1:1,9:16,16:9", help="Comma-separated aspect ratios"),
    locales: str = typer.Option("en-US", help="Comma-separated locales"),
    max_variants: int = typer.Option(2, min=1),
    seed: Optional[int] = typer.Option(None),
    overlay_style: str = typer.Option("banner"),
    log_json: bool = typer.Option(False, help="Emit JSON logs to runs/<ts>/run.log"),
):
    """Generate creatives from a campaign brief.

    This command wires through to the pipeline implementation at runtime.
    The pipeline will auto-select a provider and produce outputs+reports.
    """
    # Defer heavy imports to allow CLI help to be snappy
    from app.pipeline.ingest import load_brief_and_rules
    from app.pipeline.generator import select_provider
    from app.pipeline.report import RunContext, RunReporter
    from app.pipeline.utils import ensure_run_dirs, now_ts
    from app.pipeline.compositor import compose_variants
    from app.pipeline.legal import scan_legal
    from app.pipeline.compliance import score_compliance

    from app.logging_config import configure_logging
    from app.pipeline.utils import ensure_run_dirs

    ratios_list = [r.strip() for r in ratios.split(",") if r.strip()]
    locales_list = [l.strip() for l in locales.split(",") if l.strip()]

    run_id = now_ts()
    run_dir, log_path = ensure_run_dirs(run_id, json_logs=log_json)
    configure_logging(json_logs=log_json, log_file=log_path)

    brief_model, brand_rules = load_brief_and_rules(brief)
    provider_impl = select_provider(provider)

    reporter = RunReporter(RunContext(run_id=run_id, provider=provider_impl.name))
    try:
        compose_variants(
            brief_model,
            brand_rules,
            provider_impl,
            ratios_list,
            locales_list,
            out,
            reporter,
            max_variants=max_variants,
            seed=seed,
            overlay_style=overlay_style,
        )

        # After generation, run scans and finalize report
        scan_legal(brief_model, reporter)
        score_compliance(brief_model, brand_rules, reporter)
        reporter.finalize(out)
    finally:
        reporter.save(run_dir)


@app.command()
def orchestrate(
    briefs_dir: Path = typer.Option(Path("briefs")),
    poll_seconds: int = typer.Option(15),
    out: Path = typer.Option(Path("outputs")),
    iterations: int = typer.Option(1, help="Loop iterations before exit (for local runs)"),
):
    """Run the agentic orchestrator to watch briefs and trigger the pipeline."""
    from app.agents.orchestrator import Orchestrator, OrchestratorConfig

    cfg = OrchestratorConfig(briefs_dir=briefs_dir, poll_seconds=poll_seconds, output_dir=out)
    orch = Orchestrator(cfg)
    orch.start(max_iterations=iterations)


def main() -> None:
    app()


if __name__ == "__main__":
    main()


