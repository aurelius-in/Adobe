from __future__ import annotations
import itertools
from typing import Any, Dict, List
from ..agent_base import Agent, AgentContext, require


def _score(metrics: Dict[str, Any]) -> int:
    s = 0
    s += 1 if metrics.get("contrast_ok") else 0
    s += 1 if metrics.get("text_fit_ok") else 0
    pct = metrics.get("logo_area_pct", 0)
    s += 1 if 0.03 <= pct <= 0.06 else 0
    return s


class ExplorerAgent(Agent):
    name = "explorer"

    def plan(self, seeds, layouts, ratios):
        combos = itertools.product(seeds, layouts, ratios)
        return [{"seed": s, "layout": l, "ratio": r} for s, l, r in combos]

    def run(self, ctx: AgentContext) -> AgentContext:
        require(ctx, "plan", "runner")
        results: List[Dict[str, Any]] = []
        for c in ctx["plan"]:
            out = ctx["runner"](seed=c["seed"], layout=c["layout"], ratio=c["ratio"])
            # out should include {"asset_path", "metrics", "prov_path"}
            out["score"] = _score(out.get("metrics", {}))
            results.append(out)
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        ctx["ranked"] = results
        return ctx


