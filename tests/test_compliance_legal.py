from pathlib import Path

from app.pipeline.ingest import load_brief_and_rules
from app.pipeline.legal import scan_legal
from app.pipeline.report import RunContext, RunReporter


def test_legal_scan_flags_none_for_sample():
    brief, _ = load_brief_and_rules(Path("briefs/sample_brief.json"))
    reporter = RunReporter(RunContext(run_id="t", provider="mock"))
    hits = scan_legal(brief, reporter)
    assert isinstance(hits, list)
    # Sample brief intentionally avoids banned terms
    assert len(hits) == 0


