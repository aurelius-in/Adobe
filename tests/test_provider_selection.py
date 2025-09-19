from app.pipeline.generator import select_provider


def test_provider_auto_uses_mock_without_keys():
    provider = select_provider("auto")
    assert provider.name == "mock"


