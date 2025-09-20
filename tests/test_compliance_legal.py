from pathlib import Path

from app.pipeline.ingest import load_brief_and_rules
from app.pipeline.compositor import compose_variants
from app.pipeline.generator import select_provider
from app.pipeline.report import RunContext, RunReporter
from app.pipeline.legal import scan_legal
from app.pipeline.report import RunContext, RunReporter


def test_legal_scan_flags_none_for_sample():
    brief, _ = load_brief_and_rules(Path("briefs/sample_brief.json"))
    reporter = RunReporter(RunContext(run_id="t", provider="mock"))
    hits = scan_legal(brief, reporter)
    assert isinstance(hits, list)
    # Sample brief intentionally avoids banned terms
    assert len(hits) == 0


def test_logo_area_within_bounds(tmp_path):
    brief, rules = load_brief_and_rules(Path("briefs/sample_brief.json"))
    provider = select_provider("mock")
    reporter = RunReporter(RunContext(run_id="t2", provider=provider.name))
    compose_variants(
        brief,
        rules,
        provider,
        ["1:1"],
        [brief.locales[0]],
        tmp_path,
        reporter,
        max_variants=1,
        seed=1234,
    )
    # Read provenance sidecar
    prod_id = brief.products[0].id
    prov_path = tmp_path / brief.campaign_id / prod_id / "1x1" / "post.png.prov.json"
    assert prov_path.exists()
    import json

    prov = json.loads(prov_path.read_text(encoding="utf-8"))
    assert prov["logo_area_pct"] is not None
    min_pct = float(rules["brand"]["logo_area_pct_min"])
    max_pct = float(rules["brand"]["logo_area_pct_max"])
    assert min_pct <= prov["logo_area_pct"] <= max_pct


