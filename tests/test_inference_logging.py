from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace

import inference


def test_log_end_includes_task_name(capsys):
    inference.log_end(
        success=True,
        steps=4,
        score=0.99,
        rewards=[0.44, 0.34, 0.18, -0.01],
    )

    captured = capsys.readouterr()
    assert captured.out.strip() == "[END] success=true steps=4 score=0.99 rewards=0.44,0.34,0.18,-0.01"


def test_main_emits_structured_stdout_on_bootstrap_failure(monkeypatch):
    def failing_create_model_client():
        raise ValueError("HF_TOKEN environment variable is required")

    monkeypatch.setattr(inference, "create_model_client", failing_create_model_client)
    monkeypatch.setattr(inference, "configured_task_names", lambda: ["billing_refund_easy"])
    monkeypatch.setattr(inference, "write_run_artifact", lambda payload: None)

    buffer = StringIO()
    with redirect_stdout(buffer):
        inference.asyncio.run(inference.main())

    output = buffer.getvalue()
    assert "[START] task=billing_refund_easy" in output
    assert "[STEP] step=0 action=fatal_error" in output
    assert "[END] success=false steps=0 score=0.01 rewards=" in output
