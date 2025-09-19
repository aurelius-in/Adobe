from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


def build_mcp_context(
    *,
    campaign_id: str,
    markets: List[str],
    provider: str,
    run_id: str,
    variants_expected: int,
    variants_generated: int,
    shortfalls: List[Dict],
    compliance_avg: float,
    compliance_min: float,
    legal_flags: List[str],
    eta_next_update_minutes: int = 30,
    requested_actions: List[str] | None = None,
) -> Dict:
    return {
        "campaign_id": campaign_id,
        "markets": markets,
        "provider": provider,
        "run_id": run_id,
        "variants_expected": variants_expected,
        "variants_generated": variants_generated,
        "shortfalls": shortfalls,
        "compliance": {"avg": compliance_avg, "min": compliance_min},
        "legal_flags": legal_flags,
        "eta_next_update_minutes": eta_next_update_minutes,
        "requested_actions": requested_actions or [],
    }


def render_status_email(context: Dict) -> str:
    lines = []
    lines.append(f"Campaign: {context['campaign_id']}")
    lines.append(f"Provider: {context['provider']}  Run: {context['run_id']}")
    lines.append(f"Markets: {', '.join(context['markets'])}")
    lines.append("")
    lines.append(
        f"Variants: {context['variants_generated']}/{context['variants_expected']}\n"
        f"Compliance avg/min: {context['compliance']['avg']:.1f}/{context['compliance']['min']:.1f}"
    )
    if context.get("legal_flags"):
        lines.append("Legal flags: " + ", ".join(context["legal_flags"]))
    if context.get("shortfalls"):
        lines.append("Shortfalls:")
        for s in context["shortfalls"]:
            lines.append(f"- {s.get('product')} {s.get('ratio')}: {s.get('reason')}")
    if context.get("requested_actions"):
        lines.append("")
        lines.append("Requested actions:")
        for a in context["requested_actions"]:
            lines.append(f"- {a}")
    lines.append("")
    lines.append(f"Next update in ~{context['eta_next_update_minutes']} minutes")
    return "\n".join(lines)


