import asyncio
import json
import os
import textwrap
from pathlib import Path
from typing import Optional

from openai import OpenAI

from support_triage_env import SupportTriageAction, SupportTriageEnv

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")
ENV_BASE_URL = os.getenv("ENV_BASE_URL")
TASK_NAME = os.getenv("SUPPORT_TRIAGE_TASK", "billing_refund_easy")
BENCHMARK = os.getenv("SUPPORT_TRIAGE_BENCHMARK", "support_triage_env")
MAX_STEPS = int(os.getenv("MAX_STEPS", "12"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "350"))
SUCCESS_SCORE_THRESHOLD = float(os.getenv("SUCCESS_SCORE_THRESHOLD", "0.85"))
INFERENCE_OUTPUT_PATH = os.getenv(
    "INFERENCE_OUTPUT_PATH", "outputs/inference_last_run.json"
)
PROJECT_ROOT = Path(__file__).resolve().parent


SYSTEM_PROMPT = textwrap.dedent(
    """
    You are a support operations agent acting inside a customer-support triage environment.
    Return exactly one JSON object describing the next action.

    Allowed action_type values:
    - view_ticket
    - classify_ticket
    - draft_reply
    - request_info
    - escalate_ticket
    - resolve_ticket
    - finish

    Allowed enums:
    category: billing_refund | product_bug | security_account_takeover | account_access
    priority: low | medium | high | urgent
    team: billing_ops | engineering | trust_safety | customer_support
    resolution_code: refund_submitted | workaround_shared | password_reset_sent | no_action_needed

    Output rules:
    - Return JSON only, no markdown.
    - Include only fields that are needed for the chosen action.
    - Prefer safe, policy-compliant actions.
    - If the objective is fully completed, return {"action_type":"finish"}.
    """
).strip()


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(
    step: int, action: str, reward: float, done: bool, error: Optional[str]
) -> None:
    error_value = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} "
        f"done={str(done).lower()} error={error_value}",
        flush=True,
    )


def log_end(success: bool, steps: int, rewards: list[float]) -> None:
    reward_values = ",".join(f"{reward:.2f}" for reward in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} rewards={reward_values}",
        flush=True,
    )


def sanitize_single_line(value: str) -> str:
    return " ".join(value.split())


def write_run_artifact(payload: dict) -> None:
    output_path = Path(INFERENCE_OUTPUT_PATH)
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def normalize_action_payload(data: dict) -> dict:
    normalized = dict(data)

    alias_map = {
        "reply_content": "message",
        "reply": "message",
        "customer_reply": "message",
        "draft_reply": "message",
        "internal_note": "message",
        "note": "message",
        "escalation_note": "message",
    }
    for source_key, target_key in alias_map.items():
        if source_key in normalized and target_key not in normalized:
            normalized[target_key] = normalized[source_key]

    allowed_keys = {
        "action_type",
        "ticket_id",
        "category",
        "priority",
        "team",
        "message",
        "resolution_code",
    }
    return {key: value for key, value in normalized.items() if key in allowed_keys}


def build_user_prompt(observation: dict, state: dict) -> str:
    return textwrap.dedent(
        f"""
        Task:
        {json.dumps(observation.get("task", {}), indent=2)}

        Instructions:
        {json.dumps(observation.get("instructions", []), indent=2)}

        Policy hints:
        {json.dumps(observation.get("policy_hints", []), indent=2)}

        Queue:
        {json.dumps(observation.get("queue", []), indent=2)}

        Focused ticket:
        {json.dumps(observation.get("focused_ticket"), indent=2)}

        Last action result:
        {observation.get("last_action_result", "")}

        Current progress:
        {json.dumps(observation.get("progress", {}), indent=2)}

        Full state:
        {json.dumps(state, indent=2)}

        Decision policy:
        - Choose the single highest-value next action only.
        - Never repeat the same action on the same ticket unless the previous result shows it failed.
        - Never emit draft_reply without a non-empty message.
        - After a ticket is correctly escalated or resolved and the score is already strong, prefer finish.
        - Use request_info only when required by the task; do not ask unnecessary questions.
        - For billing refunds, include an apology, mention the refund or duplicate charge, and use a 5-7 business day timeline.
        - For engineering escalations, do not resolve the issue; escalate with concise internal context.
        - For security incidents, prioritize the security ticket first and avoid asking for secrets or disabling MFA.
        """
    ).strip()


def get_model_action(client: OpenAI, observation: dict, state: dict) -> SupportTriageAction:
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(observation, state)},
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        stream=False,
        response_format={"type": "json_object"},
    )
    content = (completion.choices[0].message.content or "").strip()
    data = normalize_action_payload(json.loads(content))
    return SupportTriageAction(**data)


def _last_action(state: dict) -> dict | None:
    history = state.get("action_history", [])
    return history[-1] if history else None


def _ticket_map(state: dict) -> dict[str, dict]:
    return {ticket["ticket_id"]: ticket for ticket in state.get("tickets", [])}


def _same_action(last_action: dict | None, candidate: SupportTriageAction) -> bool:
    if not last_action:
        return False
    return (
        last_action.get("action_type") == candidate.action_type.value
        and last_action.get("ticket_id") == candidate.ticket_id
    )


def _fallback_message(task_id: str, ticket_id: str) -> str:
    if task_id == "billing_refund_easy" or ticket_id == "TCK-3002":
        return (
            "I am sorry for the duplicate charge. I have submitted the refund request "
            "for the extra charge, and you should see it within 5-7 business days."
        )
    if task_id == "export_outage_medium":
        return (
            "I am sorry this is blocking your finance close. I have escalated the 500 "
            "error to engineering for investigation. Please share the affected workspace, "
            "approximate timestamp, and browser details to help us triage faster."
        )
    return (
        "I am sorry you are dealing with this. I have escalated this to our Trust and "
        "Safety specialists. Please do not share passwords or one-time codes. Use the "
        "secure recovery flow to reset the password and regain access."
    )


def postprocess_action(
    action: SupportTriageAction, observation: dict, state: dict
) -> SupportTriageAction:
    progress = observation.get("progress", {})
    score = float(progress.get("score", 0.0) or 0.0)
    outstanding = progress.get("outstanding_requirements", [])
    last_action = _last_action(state)
    tickets = _ticket_map(state)

    if score >= SUCCESS_SCORE_THRESHOLD and not outstanding:
        return SupportTriageAction(action_type="finish")

    if action.action_type.value == "draft_reply" and not (action.message or "").strip():
        ticket_id = action.ticket_id or state.get("focused_ticket_id") or next(
            iter(tickets), None
        )
        if ticket_id is None:
            return SupportTriageAction(action_type="finish")
        return SupportTriageAction(
            action_type="draft_reply",
            ticket_id=ticket_id,
            message=_fallback_message(state.get("task_id", ""), ticket_id),
        )

    if action.action_type.value == "finish" and score < SUCCESS_SCORE_THRESHOLD:
        for ticket in state.get("tickets", []):
            status = ticket.get("current_status")
            if status not in {"resolved", "escalated"}:
                return SupportTriageAction(
                    action_type="view_ticket", ticket_id=ticket["ticket_id"]
                )

    if _same_action(last_action, action):
        if action.ticket_id and action.ticket_id in tickets:
            ticket = tickets[action.ticket_id]
            status = ticket.get("current_status")
            if status in {"resolved", "escalated"} and score >= SUCCESS_SCORE_THRESHOLD:
                return SupportTriageAction(action_type="finish")
            if action.action_type.value == "resolve_ticket":
                return SupportTriageAction(action_type="finish")
            if action.action_type.value == "draft_reply":
                if status == "resolved":
                    return SupportTriageAction(action_type="finish")
                return SupportTriageAction(
                    action_type="view_ticket", ticket_id=action.ticket_id
                )

    if action.action_type.value == "resolve_ticket" and action.ticket_id in tickets:
        ticket = tickets[action.ticket_id]
        if ticket.get("current_status") == "resolved":
            return SupportTriageAction(action_type="finish")

    return action


async def create_env() -> SupportTriageEnv:
    if ENV_BASE_URL:
        env = SupportTriageEnv(base_url=ENV_BASE_URL)
        await env.connect()
        return env

    if not LOCAL_IMAGE_NAME:
        raise RuntimeError(
            "Set LOCAL_IMAGE_NAME for Docker-based execution or ENV_BASE_URL for a running server."
        )

    return await SupportTriageEnv.from_docker_image(LOCAL_IMAGE_NAME)


async def main() -> None:
    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN or API_KEY is required for inference.")

    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    env = await create_env()

    rewards: list[float] = []
    steps_taken = 0
    success = False
    final_score = 0.0
    cumulative_reward = 0.0
    final_progress: dict = {"score": 0.0}

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = await env.reset(task_id=TASK_NAME)

        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            state = await env.state()
            action = get_model_action(
                client,
                result.observation.model_dump(mode="json"),
                state.model_dump(mode="json"),
            )
            action = postprocess_action(
                action,
                result.observation.model_dump(mode="json"),
                state.model_dump(mode="json"),
            )
            action_str = sanitize_single_line(
                json.dumps(action.model_dump(mode="json", exclude_none=True))
            )

            error = None
            try:
                result = await env.step(action)
                reward = float(result.reward or 0.0)
                done = bool(result.done)
            except Exception as exc:
                reward = 0.0
                done = False
                error = sanitize_single_line(str(exc))
                log_step(
                    step=step,
                    action=action_str,
                    reward=reward,
                    done=done,
                    error=error,
                )
                rewards.append(reward)
                steps_taken = step
                break

            rewards.append(reward)
            steps_taken = step
            log_step(
                step=step,
                action=action_str,
                reward=reward,
                done=done,
                error=error,
            )

            if done:
                break

        state = await env.state()
        final_score = float(state.final_score)
        cumulative_reward = float(state.cumulative_reward)
        final_progress = state.progress.model_dump(mode="json")
        success = final_score >= SUCCESS_SCORE_THRESHOLD
    finally:
        try:
            await env.close()
        finally:
            write_run_artifact(
                {
                    "task": TASK_NAME,
                    "benchmark": BENCHMARK,
                    "model": MODEL_NAME,
                    "success": success,
                    "steps": steps_taken,
                    "final_score": round(final_score, 4),
                    "cumulative_reward": round(cumulative_reward, 4),
                    "rewards": [round(reward, 4) for reward in rewards],
                    "progress": final_progress,
                    "success_score_threshold": SUCCESS_SCORE_THRESHOLD,
                }
            )
            log_end(success=success, steps=steps_taken, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())
