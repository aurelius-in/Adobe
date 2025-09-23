creative-automation-pipeline
============================

One-line: Generate social creatives from a brief. Uses a local Mock provider by default.

Why
---
This pipeline turns a campaign brief into on-brand assets across common ratios. It picks a provider that works in your env. It writes simple reports so you can check what happened.

Quick start
-----------
1) Python 3.11.

2) Setup
```bash
make setup
```

3) Run sample (no API keys)
```bash
make run-sample
```

CLI
---
Run with auto provider:
```bash
python -m app.main generate \
  --brief briefs/sample_brief.json \
  --out outputs \
  --provider auto \
  --ratios 1:1,9:16,16:9 \
  --locales en-US,es-MX \
  --max-variants 2 \
  --seed 1234 \
  --overlay-style banner \
  --log-json
```

Run with Mock explicitly:
```bash
python -m app.main generate --brief briefs/sample_brief.json --provider mock
```

Orchestrator
------------
```bash
python -m app.main orchestrate --iterations 1
```

UI (optional)
-------------
```bash
streamlit run app/ui.py
```

Providers
---------
- Firefly: preferred when keys are set
- OpenAI Images: fallback when available
- Mock: pure Pillow; deterministic; always available

Auto-select tries Firefly → OpenAI → Mock.

Brief schema (short)
--------------------
Required:
- campaign_id, brand, markets, audience
- locales, aspect_ratios
- message[locale], call_to_action[locale]
- brand_palette.primary_hex
- products[] with id, name, optional prompt_hints and base_asset

See `briefs/sample_brief.json` for a full example.

Outputs
-------
- `outputs/<campaign>/<product>/<ratio>/{hero.png, post.png, *.prov.json}`
- `runs/<timestamp>/{run.log,report.json,report.csv}`

Composition
-----------
- Ratios: 1:1 (1024×1024), 9:16 (1080×1920), 16:9 (1920×1080)
- Fit hero with cover/contain without distortion; add padding when needed
- Overlay message + CTA with bundled font; line-wrap; safe margins
- Logo bottom-right with margin; target 3–6% canvas area
- Text contrast aims for WCAG AA ≥ 4.5:1
- Provenance sidecar `{image}.prov.json`

Architecture
------------
```mermaid
flowchart LR
  %% ---------- Styles ----------
  classDef node fill:#2b2b2b,stroke:#9aa0a6,color:#fff,rx:6,ry:6
  classDef store fill:#1f2937,stroke:#9aa0a6,color:#fff,rx:6,ry:6
  classDef proc  fill:#334155,stroke:#9aa0a6,color:#fff,rx:6,ry:6
  classDef note  fill:#0f172a,stroke:#64748b,color:#cbd5e1,rx:6,ry:6

  %% ---------- Ingest ----------
  Briefs[(briefs/*.json\nUTF-8 (no BOM))]:::store
  Ingest[Ingest\nschema validate]:::proc
  Orchestrator[Orchestrator]:::proc
  Briefs --> Ingest
  Orchestrator -.-> |watch inbox\n& de-dupe by campaign_id| Ingest

  %% ---------- Generation ----------
  subgraph Generation
    direction LR
    Generator[Generator\nprovider adapter]:::proc
    Compositor[Compositor\nratios (1:1, 9:16, 16:9)\n+ overlay-style]:::proc
    Generator --> |seeded (deterministic)| Compositor
  end
  Ingest --> Generator

  %% ---------- Providers ----------
  subgraph Providers
    direction LR
    Firefly[Firefly]:::node
    OpenAI[OpenAI]:::node
    Mock[Mock]:::node
  end
  Generator --> |adapter call| Providers

  %% ---------- Quality & Policy ----------
  Compliance[Brand checks\nlogo area %, palette,\ncontrast ≥ 4.5:1]:::proc
  Legal[Legal scan\nper locale]:::proc
  Compositor --> Compliance
  Ingest --> Legal

  %% ---------- Outputs & Reporting ----------
  Outputs[/outputs/<campaign>/<product>/<ratio>/\npost.png | hero.png/]:::store
  Report[Report writer]:::proc
  Runs[(runs/<run_id>/report.csv)]:::store
  Deliverables[[deliverables/*.zip]]:::store

  Compliance --> Outputs
  Outputs --> Report
  Legal --> Report
  Report --> Runs
  Runs --> Deliverables

  %% ---------- Heartbeat / status (control, dashed) ----------
  Orchestrator -.-> |status.json heartbeat| Runs

  %% ---------- Notes ----------
  SeedNote[#"Determinism via seed + overlay-style"]:::note
  SeedNote -.-> Generator

```

Make targets
------------
- setup: venv + install + bootstrap assets (logo/font if missing)
- fmt: black
- lint: ruff + black --check
- test: pytest -q
- run-sample: generate creatives with Mock provider

Environment
-----------
Copy `.env.example` to `.env` and set keys if you want external providers. The app runs without keys using Mock.

Assumptions
-----------
- If the bundled font or placeholder logo is missing, `make setup` bootstraps them.
- Firefly and OpenAI adapters degrade sanely when keys/quotas are unavailable.

Screenshots
-----------
Drop a few outputs in `docs/screens/*.png` after a run and link them here later. (yep, TODO but not a blocker)

