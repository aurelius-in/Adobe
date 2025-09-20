# Known issues (honest list)

- HSV color mask is conservative; on gradients it may under‑count brand color presence. Good enough for a PoC.
- Long copy can feel tight on 9:16. I added a “bottom‑strip” style as a fallback; still not perfect.
- Contrast check is AA (4.5:1). AAA would be safer for small text, but it can get heavy‑handed on photos.
- Legal term scan is just substring matching. It’s intentionally simple; real policy should be a ruleset per market.
- Mock provider images are… ugly. That’s by design so you can tell what’s real vs placeholder.
