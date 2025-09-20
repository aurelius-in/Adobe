from pathlib import Path
from PIL import Image

from app.pipeline.ingest import load_brief_and_rules
from app.pipeline.generator import select_provider
from app.pipeline.compositor import compose_variants, RATIO_TO_SIZE
from app.pipeline.report import RunContext, RunReporter


def test_outputs_dimensions(tmp_path):
    brief, rules = load_brief_and_rules(Path("briefs/sample_brief.json"))
    provider = select_provider("mock")
    reporter = RunReporter(RunContext(run_id="test", provider=provider.name))
    compose_variants(
        brief,
        rules,
        provider,
        ["1:1", "9:16", "16:9"],
        brief.locales,
        tmp_path,
        reporter,
        max_variants=1,
        seed=1234,
    )
    for prod in [p.id for p in brief.products]:
        for ratio, (w, h) in RATIO_TO_SIZE.items():
            ratio_dir = ratio.replace(":", "x")
            post = tmp_path / brief.campaign_id / prod / ratio_dir / "post.png"
            assert post.exists()
            with Image.open(post) as im:
                assert im.size == (w, h)


