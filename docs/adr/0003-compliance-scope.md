# 0003 — Compliance scope (v0)

Date: 2025-09-20

## Context
Brand checks can sprawl. Need a small start that still catches obvious misses.

## Decision
Score three things: logo area %, primary color coverage (HSV bucket), and text contrast ≥ 4.5:1. Defer fine typography, kerning, and safe-area rules.

## Consequences
- Fast, works offline.
- Sometimes undercounts primary on gradients (HSV buckets are blunt).
- Gives a single number to track in reports.
- Leaves room for richer checks later without breaking shape.

