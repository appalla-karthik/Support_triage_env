from __future__ import annotations

from typing import Any

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import EnvironmentMetadata

from support_triage_env.models import (
    SupportTriageAction,
    SupportTriageObservation,
    SupportTriageState,
)
from support_triage_env.simulator import SupportTriageSimulator


class SupportTriageOpenEnvEnvironment(
    Environment[SupportTriageAction, SupportTriageObservation, SupportTriageState]
):
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self):
        super().__init__()
        self._simulator = SupportTriageSimulator()
        self._state = SupportTriageState()

    def reset(
        self, seed: int | None = None, episode_id: str | None = None, **kwargs: Any
    ) -> SupportTriageObservation:
        observation = self._simulator.reset(
            seed=seed,
            episode_id=episode_id,
            **kwargs,
        )
        self._state = self._simulator.state()
        return observation

    def step(
        self,
        action: SupportTriageAction,
        timeout_s: float | None = None,
        **kwargs: Any,
    ) -> SupportTriageObservation:
        del timeout_s, kwargs
        observation, reward, done, _ = self._simulator.step(action)
        observation.reward = reward.value
        observation.done = done
        self._state = self._simulator.state()
        return observation

    @property
    def state(self) -> SupportTriageState:
        return self._state

    def get_metadata(self) -> EnvironmentMetadata:
        return EnvironmentMetadata(
            name="Support Triage Environment",
            description=(
                "A real-world customer support triage simulator with deterministic "
                "task graders and shaped rewards."
            ),
            version="0.1.0",
            author="OpenAI Codex",
        )

