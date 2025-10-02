from orchestrator.agents.explorer import _score


def test_score_triple_pass():
    assert _score({"contrast_ok": True, "text_fit_ok": True, "logo_area_pct": 0.04}) == 3


def test_score_logo_bounds():
    assert _score({"contrast_ok": False, "text_fit_ok": False, "logo_area_pct": 0.02}) == 0
    assert _score({"contrast_ok": False, "text_fit_ok": False, "logo_area_pct": 0.07}) == 0
    assert _score({"contrast_ok": False, "text_fit_ok": False, "logo_area_pct": 0.04}) == 1


