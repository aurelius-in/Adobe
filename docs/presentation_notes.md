# Presentation notes (speaker guide)

## Narrative
- Problem: scale on-brand creatives across products/ratios/locales without manual ops.
- Solution: Firefly-first pipeline with provider fallbacks, deterministic local runs, and agentic orchestration.
- Outcomes: faster turnarounds, measurable brand/legal compliance, and reproducible provenance.

## Key decisions
- Provider abstraction with auto-selection (Firefly → OpenAI → Mock) to balance quality and availability.
- Deterministic Mock provider to ensure offline runs and fast CI.
- WCAG AA contrast enforcement to maintain accessibility.
- Logo area 3–6% to respect brand presence while avoiding clutter.
- Provenance sidecars for traceability and audits.
- JSON/CSV reports for BI ingestion and stakeholder review.

## Tradeoffs
- Firefly/OpenAI adapters are stubbed locally to avoid external calls; enable in production with keys.
- Color coverage is heuristic (HSV tolerance) for speed; can be upgraded with perceptual metrics.
- Orchestrator uses polling for simplicity; move to event-driven or queue-based later.

## Live walkthrough
1) `make setup` then `make run-sample` (Mock provider, offline).
2) Show `outputs/<campaign>/...` images and `.prov.json` sidecars.
3) Show `runs/<ts>/report.json` and `report.csv`.
4) Run `python -m app.main orchestrate --iterations 1` to show `runs/status.json`.
5) Optional: `streamlit run app/ui.py` and generate variants from the UI.

## Q&A cheat sheet
- Ratios: 1:1 (1024×1024), 9:16 (1080×1920), 16:9 (1920×1080)
- Logo area target: 3–6% of canvas, bottom-right placement.
- Contrast: WCAG AA ≥ 4.5:1, with automatic backdrop if needed.
- Reports: Counts, compliance avg/min, legal flags, per-variant details.
- Providers: Firefly v3 preferred; stubs in local build; Mock always available.
