# 0002 — Ratios and compositor rules
**Date:** 2025-09-20

**Context**
Social sizes that actually matter: square, tall, wide. We need exact pixels and readable text.

**Decision**
Use 1:1 (1024×1024), 9:16 (1080×1920), 16:9 (1920×1080).
Cover/contain hero, never stretch; safe margins; line wrap.

**Consequences**
- Looks consistent across channels.
- Easy to test with hard dimensions.
- Not every edge‑case covered (e.g., very long copy).
