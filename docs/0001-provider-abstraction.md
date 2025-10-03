# 0001 — Provider abstraction
**Date:** 2025-09-20

**Context**
We need Firefly first, but reviewers must run this without keys.

**Decision**
Define a simple `Provider` interface and auto‑select Firefly → OpenAI → Mock based on a quick health check.

**Consequences**
- Easy to swap providers later.
- Local runs always work (Mock). 
- Slight extra surface area, but worth it.
