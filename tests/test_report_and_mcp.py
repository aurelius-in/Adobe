from pathlib import Path

from app.pipeline.ingest import load_brief_and_rules
from app.pipeline.generator import select_provider
from app.pipeline.compositor import compose_variants
from app.pipeline.report import RunContext, RunReporter
from app.agents.mcp import build_mcp_context, render_status_email


def test_run_report_json_created(tmp_path):
    brief, rules = load_brief_and_rules(Path("briefs/sample_brief.json"))
    provider = select_provider("mock")
    reporter = RunReporter(RunContext(run_id="t-report", provider=provider.name))
    out_dir = tmp_path / "outputs"
    compose_variants(
        brief,
        rules,
        provider,
        ["1:1"],
        [brief.locales[0]],
        out_dir,
        reporter,
        max_variants=1,
        seed=1234,
    )
    reporter.finalize(out_dir)
    run_dir = tmp_path / "runs" / reporter.ctx.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    reporter.save(run_dir)
    assert (run_dir / "report.json").exists()


def test_mcp_context_and_email():
    ctx = build_mcp_context(
        campaign_id="fall-refresh-2025",
        markets=["US", "MX"],
        provider="mock",
        run_id="t",
        variants_expected=6,
        variants_generated=4,
        shortfalls=[{"product": "cool-lime", "ratio": "16:9", "reason": "asset missing"}],
        compliance_avg=92.0,
        compliance_min=88.0,
        legal_flags=[],
        eta_next_update_minutes=30,
        requested_actions=["IT: increase Firefly quota", "Creative: approve alt layout"],
    )
    email = render_status_email(ctx)
    assert "fall-refresh-2025" in email
    assert "Variants: 4/6" in email
    assert "Compliance avg/min: 92.0/88.0" in email

