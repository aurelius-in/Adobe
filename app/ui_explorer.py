from __future__ import annotations
import json
import pathlib
import streamlit as st
from orchestrator.agent_base import AgentContext
from orchestrator.agents.explorer import ExplorerAgent
from app.explorer_runner import runner


st.set_page_config(page_title="CAPE Explorer", layout="wide")
# Logo (if present) and title
_LOGO_PATH = (pathlib.Path(__file__).resolve().parent.parent / "cape_logo.png")
if _LOGO_PATH.exists():
    st.image(str(_LOGO_PATH), width=160)
st.title("CAPE Explorer")

# Controls
with st.sidebar:
    st.header("Controls")
    seed_start = st.number_input("Seed start", min_value=1, max_value=999999, value=1234, step=1)
    seed_count = st.slider("Seed count", 1, 12, 6)
    layouts = st.multiselect("Layouts", ["banner", "badge", "stacked"], default=["banner", "badge"])
    ratios = st.multiselect("Ratios", ["1:1", "9:16", "16:9"], default=["1:1", "9:16", "16:9"])
    brief = st.text_input("Brief path", "briefs/sample_brief.json")
    provider = st.selectbox("Provider", ["auto", "mock"], index=0)
    outdir = st.text_input("Output dir", "outputs")

seeds = list(range(seed_start, seed_start + seed_count))
agent = ExplorerAgent()

if st.button("Generate batch"):
    plan = agent.plan(seeds, layouts, ratios)
    ctx = AgentContext(plan=plan, runner=lambda **kw: runner(brief=brief, out=outdir, provider=provider, **kw))
    ctx = agent.run(ctx)
    st.session_state["ranked"] = ctx["ranked"]

ranked = st.session_state.get("ranked", [])
stars = st.session_state.get("stars", set())
cols = st.columns(3)

for i, item in enumerate(ranked):
    with cols[i % 3]:
        cap = f"Score {item.get('score', 0)} | seed {item.get('seed', '')}"
        if pathlib.Path(item.get("asset_path", "")).exists():
            st.image(item["asset_path"], use_container_width=True, caption=cap)
        else:
            st.write(item.get("asset_path", ""))
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⭐", key=f"star_{i}"):
                stars.add(item.get("asset_path", ""))
        with c2:
            st.write("Metrics")
            st.json(item.get("metrics", {}), expanded=False)
        with c3:
            prov_path = item.get("prov_path", "")
            if prov_path and pathlib.Path(prov_path).exists():
                st.download_button(
                    "Sidecar",
                    data=pathlib.Path(prov_path).read_text(encoding="utf-8"),
                    file_name=pathlib.Path(prov_path).name,
                )

st.session_state["stars"] = stars

st.markdown("---")
st.subheader("Winners")
if stars:
    manifest = [{"asset": p} for p in sorted(stars) if p]
    st.code(json.dumps(manifest, indent=2), language="json")
    st.download_button(
        "Download winners manifest",
        data=json.dumps(manifest, indent=2),
        file_name="winners.json",
    )
else:
    st.caption("Star images to build a winners manifest.")


