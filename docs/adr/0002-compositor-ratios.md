# 0002 — Compositor ratios and fit rules

Date: 2025-09-20

## Context
Platforms want exact pixel sizes. Odd crop rules can tank click-through if pillarboxed.

## Decision
Use fixed sizes: 1:1 (1024×1024), 9:16 (1080×1920), 16:9 (1920×1080). Fit hero with cover (favor 9:16 cover) or contain only when unavoidable. Place logo bottom-right, target 3–6% of canvas area.

## Consequences
- Consistent outputs, avoids fuzzy resizes.
- Cover on 9:16 reduces pillars; better for Reels. 
- Some crops will cut edges; acceptable trade.
- Alt layouts can come later for long text.

