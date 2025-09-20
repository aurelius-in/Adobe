import json
from pathlib import Path

import streamlit as st

from app.pipeline.ingest import load_brief_and_rules
from app.pipeline.generator import select_provider
from app.pipeline.compositor import compose_variants, RATIO_TO_SIZE
from app.pipeline.report import RunContext, RunReporter

st.set_page_config(page_title="Creative Automation", layout="wide")
st.markdown(
    "<style> .stMarkdown p { word-wrap: break-word; } .stCaption { white-space: normal; } </style>",
    unsafe_allow_html=True,
)

st.title("Creative Automation Pipeline")

with st.sidebar:
    st.header("Run settings")
    brief_file = st.selectbox(
        "Brief file",
        options=sorted([str(p) for p in Path("briefs").glob("*.json")]),
    )
    provider_name = st.selectbox("Provider", options=["auto", "mock", "firefly", "openai"], index=0)
    ratios = st.multiselect("Ratios", options=list(RATIO_TO_SIZE.keys()), default=list(RATIO_TO_SIZE.keys()))
    locales_input = st.text_input("Locales (comma)", value="en-US,es-MX")
    max_variants = st.number_input("Max variants", min_value=1, max_value=5, value=1)
    seed = st.number_input("Seed", min_value=0, value=1234)
    run_btn = st.button("Run generation")

status = st.empty()

if run_btn and brief_file:
    brief, rules = load_brief_and_rules(Path(brief_file))
    provider = select_provider(provider_name)
    reporter = RunReporter(RunContext(run_id="ui", provider=provider.name))
    out_dir = Path("outputs")

    locales = [x.strip() for x in locales_input.split(",") if x.strip()]
    compose_variants(
        brief,
        rules,
        provider,
        ratios,
        locales,
        out_dir,
        reporter,
        max_variants=max_variants,
        seed=int(seed),
    )
    reporter.finalize(out_dir)
    status.success(f"Generated {len(reporter.variants)} variants with provider {provider.name}")

    st.subheader("Report")
    st.json(reporter._report.model_dump())

    st.subheader("Gallery")
    cols = st.columns(3)
    col_idx = 0
    for v in reporter.variants:
        with cols[col_idx % 3]:
            st.caption(f"{v.product_id} – {v.ratio} – {v.locale}")
            st.image(str(v.path_post))
        col_idx += 1
