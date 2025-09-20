# Presentation notes (speaker guide)

## Narrative
- Problem: scale on-brand creatives across products/ratios/locales without manual ops.
  - In plain terms: too many assets, not enough hours. People copy/paste a lot, which is where mistakes slip in and review cycles get slow.
- Solution: Firefly-first pipeline with provider fallbacks, deterministic local runs, and agentic orchestration.
  - This just means “try the fancy API if keys exist; if not, still run locally and show something real.” No mystery boxes.
- Outcomes: faster turnarounds, measurable brand/legal compliance, and reproducible provenance.
  - The point is speed with guardrails: quick assets, a score that says how close to brand we are, and small JSON files that show where each image came from.

## Key decisions
- Provider abstraction with auto-selection (Firefly → OpenAI → Mock) to balance quality and availability.
  - Why: keys/quotas fail at the worst time. Auto select keeps demos and tests moving. You can force `--provider mock` when you want predictable output.
- Deterministic Mock provider to ensure offline runs and fast CI.
  - It draws clear placeholders with the prompt + size. Looks basic but is super handy for repeatable runs.
- WCAG AA contrast enforcement to maintain accessibility.
  - If text would be hard to read, the pipeline drops in a subtle dark backdrop. Not perfect typography, just the right nudge.
- Logo area 3–6% to respect brand presence while avoiding clutter.
  - Small enough to not shout, big enough to pass most brand guidelines. We measure it and write the % to provenance.
- Provenance sidecars for traceability and audits.
  - Each image gets a `{image}.prov.json` next to it. If someone asks “where did this come from?”, the answer is right there.
- JSON/CSV reports for BI ingestion and stakeholder review.
  - Plain CSV so Excel folks can open it without a fight. JSON for machines.

## Tradeoffs
- Firefly/OpenAI adapters are stubbed locally to avoid external calls; enable in production with keys.
  - So local runs never fail because of a quota blip. It’s a choice: demo reliability over API realism.
- Color coverage is heuristic (HSV tolerance) for speed; can be upgraded with perceptual metrics.
  - This approach favors fast checks that catch obvious misses. Gradients can fool it a bit, which is… fine for v0.
- Orchestrator uses polling for simplicity; move to event-driven or queue-based later.
  - It’s a while-loop. Not elegant, but easy to read. If this ships, swap in events.

## Live walkthrough
1) `make setup` then `make run-sample` (Mock provider, offline).
   - Shows the flow without any keys. Keep it under a minute.
2) Show `outputs/<campaign>/...` images and `.prov.json` sidecars.
   - Open one sidecar and point at `logo_area_pct` so folks see the number.
3) Show `runs/<ts>/report.json` and `report.csv`.
   - Mention how CSV fields map to a simple dashboard if needed.
4) Run `python -m app.main orchestrate --iterations 1` to show `runs/status.json`.
   - It’s a tiny loop that notices briefs and triggers the same pipeline. Think “cron-lite.”
5) Optional: `streamlit run app/ui.py` and generate variants from the UI.
   - Good for non-CLI folks. Keep expectations modest: it’s a helper, not THE tool.

## Q&A cheat sheet
- Ratios: 1:1 (1024×1024), 9:16 (1080×1920), 16:9 (1920×1080)
  - These match common placements; exact px avoids blurry resizes later.
- Logo area target: 3–6% of canvas, bottom-right placement.
  - Center looks nice sometimes, but bottom-right keeps text clear. Rules can change per brand.
- Contrast: WCAG AA ≥ 4.5:1, with automatic backdrop if needed.
  - The backdrop is semi-transparent so the hero still shows through.
- Reports: Counts, compliance avg/min, legal flags, per-variant details.
  - The single “avg” number is for quick readouts; drill-down stays in JSON.
- Providers: Firefly v3 preferred; stubs in local build; Mock always available.
  - If keys work, great. If not, the Mock keeps the demo moving.
