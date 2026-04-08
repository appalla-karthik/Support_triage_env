from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace

import inference


def test_log_end_includes_task_name(capsys):
    inference.log_end(
        task="billing_refund_easy",
        success=True,
        steps=4,
        score=0.99,
        rewards=[0.44, 0.34, 0.18, -0.01],
    )

    captured = capsys.readouterr()
    assert "[END] task=billing_refund_easy" in captured.out
    assert "score=0.99" in captured.out


def test_main_emits_structured_stdout_on_bootstrap_failure(monkeypatch):
    async def failing_create_env():
        raise RuntimeError("bootstrap failed")

    monkeypatch.setattr(inference, "create_env", failing_create_env)
    monkeypatch.setattr(inference, "configured_task_names", lambda: ["billing_refund_easy"])
    monkeypatch.setattr(inference, "create_model_client", lambda: None)
    monkeypatch.setattr(inference, "write_run_artifact", lambda payload: None)

    buffer = StringIO()
    with redirect_stdout(buffer):
        inference.asyncio.run(inference.main())

    output = buffer.getvalue()
    assert "[START]" in output
    assert "[STEP] step=0 action=bootstrap" in output
    assert "[STEP] step=0 action=fatal_error" in output
    assert "[END] task=billing_refund_easy" in output
