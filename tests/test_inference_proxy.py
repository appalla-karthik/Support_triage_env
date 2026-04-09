from types import SimpleNamespace

import inference


def test_create_model_client_uses_proxy_env(monkeypatch):
    captured: dict[str, str] = {}

    def fake_openai(*, base_url: str, api_key: str):
        captured["base_url"] = base_url
        captured["api_key"] = api_key
        return SimpleNamespace()

    monkeypatch.setattr(inference, "API_BASE_URL", "https://proxy.example/v1")
    monkeypatch.setattr(inference, "HF_TOKEN", "hf-token")
    monkeypatch.setenv("OPENAI_API_KEY", "should-not-be-used")
    monkeypatch.setattr(inference, "OpenAI", fake_openai)

    client = inference.create_model_client()

    assert client is not None
    assert captured == {
        "base_url": "https://proxy.example/v1",
        "api_key": "hf-token",
    }


def test_create_model_client_requires_hf_token(monkeypatch):
    monkeypatch.setattr(inference, "API_BASE_URL", "https://proxy.example/v1")
    monkeypatch.setattr(inference, "HF_TOKEN", None)
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")

    try:
        inference.create_model_client()
    except ValueError as exc:
        assert "HF_TOKEN environment variable is required" in str(exc)
    else:
        raise AssertionError("Expected create_model_client to require HF_TOKEN")


def test_create_model_client_uses_default_api_base(monkeypatch):
    captured: dict[str, str] = {}

    def fake_openai(*, base_url: str, api_key: str):
        captured["base_url"] = base_url
        captured["api_key"] = api_key
        return SimpleNamespace()

    monkeypatch.setattr(inference, "API_BASE_URL", "https://api.openai.com/v1")
    monkeypatch.setattr(inference, "HF_TOKEN", "hf-token")
    monkeypatch.setattr(inference, "OpenAI", fake_openai)

    client = inference.create_model_client()

    assert client is not None
    assert captured == {
        "base_url": "https://api.openai.com/v1",
        "api_key": "hf-token",
    }


def test_ensure_proxy_request_makes_chat_completion(monkeypatch):
    calls: list[dict] = []

    class FakeCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace()

    client = SimpleNamespace(
        chat=SimpleNamespace(completions=FakeCompletions())
    )
    monkeypatch.setattr(inference, "MODEL_NAME", "gpt-test")

    inference.ensure_proxy_request(client)

    assert len(calls) == 1
    assert calls[0]["model"] == "gpt-test"
    assert calls[0]["stream"] is False
    assert calls[0]["max_tokens"] == 8
