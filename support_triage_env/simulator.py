from __future__ import annotations

import copy
import random
import uuid
from typing import Any

from support_triage_env.graders import BaseTaskGrader, build_graders
from support_triage_env.models import (
    ActionLogEntry,
    ActionType,
    GradingSnapshot,
    QueueTicketView,
    SupportTriageAction,
    SupportTriageObservation,
    SupportTriageReward,
    SupportTriageState,
    TaskCard,
    TicketMessage,
    TicketRecord,
    TicketStatus,
)
from support_triage_env.tasks import TaskScenario, build_task_scenario, task_ids


class SupportTriageSimulator:
    """Local Gym-style simulator with step/reset/state APIs."""

    def __init__(self):
        self._rng = random.Random(0)
        self._task_order = task_ids()
        self._task_index = 0
        self._scenario: TaskScenario | None = None
        self._grader: BaseTaskGrader | None = None
        self._last_reward = SupportTriageReward(
            value=0.0,
            task_score=0.0,
            score_delta=0.0,
            components={},
            penalties={},
            rationale=[],
        )
        self._state = SupportTriageState()

    def reset(
        self,
        seed: int | None = None,
        episode_id: str | None = None,
        task_id: str | None = None,
        **_: Any,
    ) -> SupportTriageObservation:
        if seed is not None:
            self._rng = random.Random(seed)

        if task_id is None:
            task_id = self._task_order[self._task_index % len(self._task_order)]
            self._task_index += 1

        if task_id not in self._task_order:
            raise ValueError(f"Unknown task_id '{task_id}'")

        scenario = build_task_scenario(task_id, self._rng)
        self._scenario = scenario
        self._grader = build_graders({task_id: scenario})[task_id]
        initial_state = SupportTriageState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            task_id=scenario.card.task_id,
            difficulty=scenario.card.difficulty,
            objective=scenario.card.objective,
            max_steps=scenario.card.max_steps,
            focused_ticket_id=None,
            tickets=[copy.deepcopy(ticket) for ticket in scenario.tickets],
            action_history=[],
            cumulative_reward=0.0,
            final_score=0.0,
            done=False,
            progress=GradingSnapshot(score=0.0),
        )
        initial_grade = self._grader.grade(initial_state)
        initial_payload = initial_state.model_dump()
        initial_payload["final_score"] = initial_grade.score
        initial_payload["progress"] = initial_grade
        self._state = SupportTriageState(**initial_payload)
        self._last_reward = SupportTriageReward(
            value=0.0,
            task_score=initial_grade.score,
            score_delta=0.0,
            components={},
            penalties={},
            rationale=["Episode reset."],
        )
        return self._build_observation(
            scenario,
            last_action_result="New queue loaded. Review the tickets and begin triage.",
            reward=self._last_reward,
        )

    def step(
        self, action: SupportTriageAction
    ) -> tuple[SupportTriageObservation, SupportTriageReward, bool, dict[str, Any]]:
        if not self._state.task_id:
            raise RuntimeError("Call reset() before step().")
        if self._scenario is None or self._grader is None:
            raise RuntimeError("No active scenario loaded. Call reset() before step().")

        scenario = self._scenario
        previous_score = self._state.progress.score
        invalid_reasons: list[str] = []
        repeated_penalty = 0.0
        result_message = ""

        if self._state.done:
            reward = SupportTriageReward(
                value=0.0,
                task_score=self._state.final_score,
                score_delta=0.0,
                components={},
                penalties={},
                rationale=["Episode already finished. Call reset() to start again."],
            )
            observation = self._build_observation(
                scenario,
                last_action_result="Episode already finished.",
                reward=reward,
            )
            return observation, reward, True, {"state": self.state().model_dump()}

        self._state.step_count += 1

        last_entry = self._state.action_history[-1] if self._state.action_history else None
        if (
            last_entry
            and last_entry.action_type == action.action_type
            and last_entry.ticket_id == action.ticket_id
        ):
            repeated_penalty = 0.03

        if action.action_type != ActionType.FINISH:
            ticket = self._find_ticket(action.ticket_id, invalid_reasons)
        else:
            ticket = None

        if action.action_type == ActionType.VIEW_TICKET and ticket is not None:
            self._state.focused_ticket_id = ticket.ticket_id
            result_message = f"Opened {ticket.ticket_id}: {ticket.subject}"
        elif action.action_type == ActionType.CLASSIFY_TICKET and ticket is not None:
            if action.category is None or action.priority is None or action.team is None:
                invalid_reasons.append(
                    "classify_ticket requires category, priority, and team."
                )
            else:
                ticket.current_category = action.category
                ticket.current_priority = action.priority
                ticket.assigned_team = action.team
                ticket.current_status = TicketStatus.IN_PROGRESS
                self._state.focused_ticket_id = ticket.ticket_id
                result_message = (
                    f"{ticket.ticket_id} classified as {action.category.value}, "
                    f"{action.priority.value}, assigned to {action.team.value}."
                )
        elif action.action_type == ActionType.DRAFT_REPLY and ticket is not None:
            if not action.message:
                invalid_reasons.append("draft_reply requires a customer-facing message.")
            else:
                ticket.outbound_messages.append(action.message)
                ticket.messages.append(
                    TicketMessage(role="agent", content=action.message)
                )
                ticket.current_status = TicketStatus.IN_PROGRESS
                self._state.focused_ticket_id = ticket.ticket_id
                result_message = f"Saved outbound reply for {ticket.ticket_id}."
        elif action.action_type == ActionType.REQUEST_INFO and ticket is not None:
            if not action.message:
                invalid_reasons.append("request_info requires the requested details.")
            else:
                ticket.requested_information.append(action.message)
                ticket.outbound_messages.append(action.message)
                ticket.messages.append(
                    TicketMessage(role="agent", content=action.message)
                )
                ticket.current_status = TicketStatus.WAITING_FOR_CUSTOMER
                result_message = f"Requested additional information from {ticket.ticket_id}."
        elif action.action_type == ActionType.ESCALATE_TICKET and ticket is not None:
            if action.team is None:
                invalid_reasons.append("escalate_ticket requires a destination team.")
            else:
                ticket.assigned_team = action.team
                ticket.current_status = TicketStatus.ESCALATED
                if action.message:
                    ticket.internal_notes.append(action.message)
                self._state.focused_ticket_id = ticket.ticket_id
                result_message = f"Escalated {ticket.ticket_id} to {action.team.value}."
        elif action.action_type == ActionType.RESOLVE_TICKET and ticket is not None:
            if action.resolution_code is None:
                invalid_reasons.append("resolve_ticket requires a resolution_code.")
            else:
                ticket.current_status = TicketStatus.RESOLVED
                ticket.resolution_code = action.resolution_code
                if action.message:
                    ticket.internal_notes.append(action.message)
                self._state.focused_ticket_id = ticket.ticket_id
                result_message = (
                    f"Resolved {ticket.ticket_id} with {action.resolution_code.value}."
                )
        elif action.action_type == ActionType.FINISH:
            result_message = "Episode finished by agent."
            self._state.done = True
        else:
            if not invalid_reasons:
                invalid_reasons.append(f"Unsupported action {action.action_type.value}.")

        if invalid_reasons:
            result_message = " ".join(invalid_reasons)

        self._state.action_history.append(
            ActionLogEntry(
                step_number=self._state.step_count,
                action_type=action.action_type,
                ticket_id=action.ticket_id,
                summary=result_message,
            )
        )

        grade = self._grader.grade(self._state)
        self._state.progress = grade
        self._state.final_score = grade.score

        invalid_penalty = 0.07 if invalid_reasons else 0.0
        step_penalty = 0.01
        reward_value = round(
            (grade.score - previous_score) - step_penalty - repeated_penalty - invalid_penalty,
            4,
        )
        reward = SupportTriageReward(
            value=reward_value,
            task_score=grade.score,
            score_delta=round(grade.score - previous_score, 4),
            components=grade.components,
            penalties={
                **grade.penalties,
                "step_cost": step_penalty,
                **({"repeat_action": repeated_penalty} if repeated_penalty else {}),
                **({"invalid_action": invalid_penalty} if invalid_penalty else {}),
            },
            rationale=[
                result_message,
                *grade.violations,
                *([] if not invalid_reasons else invalid_reasons),
            ],
        )
        self._last_reward = reward

        if self._state.step_count >= scenario.card.max_steps:
            self._state.done = True
            result_message += " Maximum step count reached."

        self._state.cumulative_reward = round(
            self._state.cumulative_reward + reward.value, 4
        )

        observation = self._build_observation(
            scenario,
            last_action_result=result_message,
            reward=reward,
        )
        info = {
            "reward": reward.model_dump(),
            "grading": grade.model_dump(),
            "state": self.state().model_dump(),
        }
        return observation, reward, self._state.done, info

    def state(self) -> SupportTriageState:
        return self._state.model_copy(deep=True)

    def _find_ticket(
        self, ticket_id: str | None, invalid_reasons: list[str]
    ) -> TicketRecord | None:
        if not ticket_id:
            invalid_reasons.append("This action requires a ticket_id.")
            return None
        for ticket in self._state.tickets:
            if ticket.ticket_id == ticket_id:
                return ticket
        invalid_reasons.append(f"Unknown ticket_id '{ticket_id}'.")
        return None

    def _build_observation(
        self,
        scenario: TaskScenario,
        last_action_result: str,
        reward: SupportTriageReward,
    ) -> SupportTriageObservation:
        focused_ticket = None
        if self._state.focused_ticket_id:
            for ticket in self._state.tickets:
                if ticket.ticket_id == self._state.focused_ticket_id:
                    focused_ticket = ticket.model_copy(deep=True)
                    break

        return SupportTriageObservation(
            done=self._state.done,
            reward=reward.value,
            task=TaskCard(**scenario.card.model_dump()),
            instructions=list(scenario.instructions),
            policy_hints=list(scenario.policy_hints),
            queue=[
                QueueTicketView(**ticket.to_queue_view().model_dump())
                for ticket in self._state.tickets
            ],
            focused_ticket=focused_ticket,
            last_action_result=last_action_result,
            progress=self._state.progress.model_copy(deep=True),
            available_actions=[action.value for action in ActionType],
        )
