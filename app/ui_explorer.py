from __future__ import annotations
import json
import pathlib
import streamlit as st
from orchestrator.agent_base import AgentContext
from orchestrator.agents.explorer import ExplorerAgent
from app.explorer_runner import runner


st.set_page_config(page_title="CAPE Explorer", layout="wide")
# Tighten top/left padding
st.markdown(
    """
    <style>
    /* Hide Streamlit's default header bar and tighten content padding */
    [data-testid="stHeader"] { display: none; }
    div.block-container { padding-top: 10px; padding-left: 10px; }
    /* Hide image fullscreen/expand button */
    [data-testid="StyledFullScreenButton"],
    button[title="View fullscreen"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)
# Logo (if present) and top bar
_LOGO_PATH = (pathlib.Path(__file__).resolve().parent.parent / "cape_logo.png")
top_logo, top_title = st.columns([1, 8])
with top_logo:
    if _LOGO_PATH.exists():
        st.image(str(_LOGO_PATH), width=80)
with top_title:
    if "controls_visible" not in st.session_state:
        st.session_state["controls_visible"] = True
    # Controls button (only when hidden) + Title on one row
    ctl_col, title_col = st.columns([1, 12])
    with ctl_col:
        if not st.session_state["controls_visible"]:
            if st.button("Controls", key="show_controls"):
                st.session_state["controls_visible"] = True
    with title_col:
        st.markdown(
            "<div style='color: rgba(255,213,79,0.60); font-size:20px; margin-top:8px;'>Creative Automation Pipeline Explorer</div>",
            unsafe_allow_html=True,
        )

# Defaults from session (used when controls hidden)
defaults = {
    "seed_start": 1234,
    "seed_count": 6,
    "layouts": ["banner", "bottom-strip", "center-card"],
    "ratios": ["1:1", "9:16", "16:9"],
    "brief": "briefs/sample_brief.json",
    "provider": "auto",
    "outdir": "outputs",
    "notes": "",
    "style_tags": [],
    "headline": "",
    "cta": "Shop now",
    "font_size": 72,
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

logo_file = None
brand_img_file = None
generate_clicked = False

if st.session_state["controls_visible"]:
    c1, c2, images_col = st.columns([1, 1, 2])
    with c1:
        if st.button("✕", key="hide_controls_left", help="Hide controls"):
            st.session_state["controls_visible"] = False
        st.number_input("Seed start", min_value=1, max_value=999999, step=1, key="seed_start")
        st.slider("Seed count", 1, 12, key="seed_count")
        st.multiselect("Layouts", ["banner", "bottom-strip", "center-card"], key="layouts", default=st.session_state["layouts"])
        st.multiselect("Ratios", ["1:1", "9:16", "16:9"], key="ratios", default=st.session_state["ratios"])
        st.text_input("Brief path", key="brief")
        st.selectbox("Provider", ["auto", "mock", "openai"], key="provider")
    with c2:
        st.text_input("Output dir", key="outdir")
        st.text_area("Notes", placeholder="Optional extra guidance", height=80, key="notes")
        st.markdown("---")
        st.subheader("Brand")
        logo_file = st.file_uploader("Logo", type=["png","jpg","jpeg"], accept_multiple_files=False)
        brand_img_file = st.file_uploader("Brand image (optional)", type=["png","jpg","jpeg"], accept_multiple_files=False)
        st.multiselect(
            "Style tags",
            [
                "bright",
                "punchy",
                "subdued",
                "subtle",
                "pastels",
                "primary colors",
                "exciting",
                "mellow",
                "calm",
            ],
            key="style_tags",
            default=st.session_state.get("style_tags", []),
            help="Adds adjectives to the prompt",
        )
        st.markdown("---")
        st.subheader("Text overrides")
        st.text_input("Headline", key="headline")
        cta_options = [
            "Shop now",
            "Learn more",
            "Sign up",
            "Buy now",
            "Get started",
            "Try it",
            "Join now",
            "Download",
            "Try now",
            "Get the app",
            "Free Trial",
            "Get yours",
        ]
        st.radio("CTA", options=cta_options, index=cta_options.index(st.session_state.get("cta", cta_options[0])), horizontal=True, key="cta")
        st.slider("Font size", min_value=16, max_value=200, key="font_size")
        generate_clicked = st.button("Generate batch", type="primary")
else:
    images_col = st

seeds = list(range(st.session_state["seed_start"], st.session_state["seed_start"] + st.session_state["seed_count"]))
agent = ExplorerAgent()

if generate_clicked:
    plan = agent.plan(seeds, st.session_state["layouts"], st.session_state["ratios"])
    # pass notes via env var used in build_prompt
    import os
    extra_parts = []
    if st.session_state["notes"]:
        extra_parts.append(st.session_state["notes"])
    if st.session_state["style_tags"]:
        extra_parts.append("style: " + ", ".join(st.session_state["style_tags"]))
    os.environ["CAPE_EXTRA_HINTS"] = ". ".join(p.strip() for p in extra_parts if p and p.strip())
    # Push text overrides and font size into env for compositor
    if st.session_state["headline"]:
        os.environ["CAPE_UI_HEADLINE"] = st.session_state["headline"]
    else:
        os.environ.pop("CAPE_UI_HEADLINE", None)
    os.environ["CAPE_UI_CTA"] = st.session_state["cta"]
    os.environ["CAPE_OVERLAY_FONT_SIZE"] = str(st.session_state["font_size"])
    # Save uploaded brand assets to predictable paths and point brand rules at them via local override
    if logo_file or brand_img_file:
        import os, json
        from pathlib import Path
        brand_dir = Path("brand")
        brand_dir.mkdir(parents=True, exist_ok=True)
        rules_local = brand_dir / "brand_rules.local.yaml"
        logo_path = None
        brand_img_path = None
        if logo_file:
            logo_path = brand_dir / "uploaded_logo.png"
            logo_path.write_bytes(logo_file.getvalue())
        if brand_img_file:
            brand_img_path = brand_dir / "uploaded_brand_image.png"
            brand_img_path.write_bytes(brand_img_file.getvalue())
        # merge minimal override
        lines = ["brand:"]
        if logo_path:
            lines.append(f"  logo_path: \"{str(logo_path).replace('\\','/')}\"")
        if rules_local.exists():
            # simple append to not clobber existing customizations
            rules_local.write_text(rules_local.read_text(encoding="utf-8") + "\n" + "\n".join(lines), encoding="utf-8")
        else:
            rules_local.write_text("\n".join(lines), encoding="utf-8")

    ctx = AgentContext(plan=plan, runner=lambda **kw: runner(brief=st.session_state["brief"], out=st.session_state["outdir"], provider=st.session_state["provider"], **kw))
    ctx = agent.run(ctx)
    st.session_state["ranked"] = ctx["ranked"]

ranked = st.session_state.get("ranked", [])
stars = st.session_state.get("stars", set())
cols = st.columns(3)

for i, item in enumerate(ranked):
    with cols[i % 3]:
        cap = f"Score {item.get('score', 0)} | seed {item.get('seed', '')}"
        if pathlib.Path(item.get("asset_path", "")).exists():
            st.image(item["asset_path"], use_column_width=True, caption=cap)
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
                    key=f"prov_dl_{i}",
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


