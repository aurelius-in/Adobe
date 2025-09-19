import json
import pytest

from app.models import Brief


def test_brief_missing_locale_message_fails(tmp_path):
    data = {
        "campaign_id": "x",
        "brand": "b",
        "markets": ["US"],
        "audience": "aud",
        "locales": ["en-US"],
        "aspect_ratios": ["1:1"],
        "message": {},
        "call_to_action": {"en-US": "Go"},
        "brand_palette": {"primary_hex": "#000000"},
        "products": [{"id": "p", "name": "n"}],
    }
    with pytest.raises(Exception):
        Brief(**data)


