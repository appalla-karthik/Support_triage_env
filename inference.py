import asyncio
import json
import os
import textwrap
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
    data = json.loads(content)
    return SupportTriageAction(**data)


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
        success = final_score >= SUCCESS_SCORE_THRESHOLD
    finally:
        try:
            await env.close()
        finally:
            log_end(success=success, steps=steps_taken, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())
