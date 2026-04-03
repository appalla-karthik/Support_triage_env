from __future__ import annotations

from typing import Any

from openenv.core import EnvClient
from openenv.core.client_types import StepResult

from support_triage_env.models import (
    ActionLogEntry,
    GradingSnapshot,
    QueueTicketView,
    SupportTriageAction,
    SupportTriageObservation,
    SupportTriageState,
    TaskCard,
    TicketRecord,
)


class SupportTriageEnv(
    EnvClient[SupportTriageAction, SupportTriageObservation, SupportTriageState]
):
    def _step_payload(self, action: SupportTriageAction) -> dict[str, Any]:
        payload = action.model_dump(exclude_none=True)
        payload.pop("metadata", None)
        return payload

    def _parse_result(self, payload: dict[str, Any]) -> StepResult[SupportTriageObservation]:
        obs_data = payload.get("observation", {})
        observation = SupportTriageObservation(
            done=payload.get("done", False),
            reward=payload.get("reward"),
            task=TaskCard(**obs_data["task"]),
            instructions=obs_data.get("instructions", []),
            policy_hints=obs_data.get("policy_hints", []),
            queue=[QueueTicketView(**item) for item in obs_data.get("queue", [])],
            focused_ticket=(
                TicketRecord(**obs_data["focused_ticket"])
                if obs_data.get("focused_ticket")
                else None
            ),
            last_action_result=obs_data.get("last_action_result", ""),
            progress=GradingSnapshot(**obs_data.get("progress", {"score": 0.0})),
            available_actions=obs_data.get("available_actions", []),
            metadata=obs_data.get("metadata", {}),
        )
        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict[str, Any]) -> SupportTriageState:
        return SupportTriageState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            task_id=payload.get("task_id"),
            difficulty=payload.get("difficulty"),
            objective=payload.get("objective", ""),
            max_steps=payload.get("max_steps", 0),
            focused_ticket_id=payload.get("focused_ticket_id"),
            tickets=[TicketRecord(**ticket) for ticket in payload.get("tickets", [])],
            action_history=[
                ActionLogEntry(**entry) for entry in payload.get("action_history", [])
            ],
            cumulative_reward=payload.get("cumulative_reward", 0.0),
            final_score=payload.get("final_score", 0.0),
            done=payload.get("done", False),
            progress=GradingSnapshot(**payload.get("progress", {"score": 0.0})),
        )
