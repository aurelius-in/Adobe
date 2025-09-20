# 0001 — Provider abstraction and auto-selection

Date: 2025-09-20

## Context
Creatives need to render locally and in CI without external keys. When keys are present, call a real service. Teams swap vendors sometimes.

## Decision
Define provider adapters with a small interface. Implement `firefly`, `openai`, and `mock`. Default `--provider auto` tries Firefly → OpenAI → Mock based on keys and a health check.

## Consequences
- Simple local runs via Mock; predictable outputs.
- Real providers can slot in later with minimal pipe churn.
- Auto can hide misconfig; CLI allows explicit `--provider mock`.
- Health check is coarse for now; deeper probe later if needed.

