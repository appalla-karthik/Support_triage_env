from __future__ import annotations

import threading
from typing import Any, ClassVar

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
    _shared_lock: ClassVar[threading.RLock] = threading.RLock()
    _shared_simulator: ClassVar[SupportTriageSimulator] = SupportTriageSimulator()
    _shared_state: ClassVar[SupportTriageState] = SupportTriageState()

    def __init__(self):
        super().__init__()

    def reset(
        self, seed: int | None = None, episode_id: str | None = None, **kwargs: Any
    ) -> SupportTriageObservation:
        with self._shared_lock:
            observation = self._shared_simulator.reset(
                seed=seed,
                episode_id=episode_id,
                **kwargs,
            )
            type(self)._shared_state = self._shared_simulator.state()
            return observation

    def step(
        self,
        action: SupportTriageAction,
        timeout_s: float | None = None,
        **kwargs: Any,
    ) -> SupportTriageObservation:
        del timeout_s, kwargs
        with self._shared_lock:
            observation, reward, done, _ = self._shared_simulator.step(action)
            observation.reward = reward.value
            observation.done = done
            type(self)._shared_state = self._shared_simulator.state()
            return observation

    @property
    def state(self) -> SupportTriageState:
        with self._shared_lock:
            return type(self)._shared_state.model_copy(deep=True)

    def get_metadata(self) -> EnvironmentMetadata:
        return EnvironmentMetadata(
            name="Support Triage Environment",
            description=(
                "A real-world customer support triage simulator with deterministic "
                "task graders and shaped rewards."
            ),
            version="0.1.0",
            author="Karthik Appalla",
        )

