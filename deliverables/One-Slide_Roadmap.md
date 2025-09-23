```gantt
    dateFormat  YYYY-MM-DD
    title One-slide Roadmap (practical)
    excludes  weekends
    axisFormat %b %d

    %% ---------- Week 0–1 (MVP) ----------
    section Week 0–1 (MVP)
    MVP pipeline: brief → variants → overlays → outputs     :done,    w01, 2025-09-01, 14d
    CSV/JSON reporting + deterministic seeds                 :done,    rep, 2025-09-01, 14d

    %% ---------- Week 2–3 ----------
    section Week 2–3
    Firefly v3 adapter integration                           :active,  ff3, after w01, 14d
    Brand checks (logo %, palette, contrast)                 :          brand, after ff3, 7d
    Legal term flags per locale                              :          legal, after brand, 3d

    %% ---------- Week 4 ----------
    section Week 4
    Orchestrator agent (watcher, dedupe)                     :          orch, 2025-10-06, 7d
    MCP/alerts + provenance sidecars                         :          mcp,  after orch, 5d
    Bundle deliverables + README verification                :          bundle, after mcp, 2d

    %% ---------- Week 5+ ----------
    section Week 5+
    Cloud storage adapters                                   :          cloud, 2025-10-13, 10d
```
    Per-channel spec packs                                   :          specs, after cloud, 7d
    A/B loop & metrics dashboard                             :          ab,    after specs, 10d
