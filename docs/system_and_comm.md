# Agentic system design and communications

## Agents
- Orchestrator watches `briefs/`, triggers generation, and maintains `runs/status.json`.
- Provider auto-selection prefers Firefly, then OpenAI, then Mock for offline.

## MCP JSON template
```json
{
  "campaign_id": "...",
  "markets": ["US", "MX"],
  "provider": "firefly|openai|mock",
  "run_id": "...",
  "variants_expected": 0,
  "variants_generated": 0,
  "shortfalls": [{"product":"...", "ratio":"...", "reason":"..."}],
  "compliance": {"avg": 0, "min": 0},
  "legal_flags": [],
  "eta_next_update_minutes": 30,
  "requested_actions": ["IT: increase Firefly quota", "Creative: approve alt layout"]
}
```

## Sample stakeholder email (delay due to provisioning)
```text
Subject: Creative pipeline status – fall-refresh-2025 (Run 20250101T120000Z)

Hi team,

We generated 6/12 variants for fall-refresh-2025 using provider mock.
Compliance avg/min is 92/88 with no legal flags. Shortfalls remain for
cool-lime at 16:9 due to source asset gap. Next update in ~30 minutes.

Requested actions:
- IT: increase Firefly quota to 10 req/min.
- Creative: approve alt layout for narrow text blocks.

Thanks,
Automation Orchestrator
```
