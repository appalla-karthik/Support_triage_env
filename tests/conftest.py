from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


if "openenv.core" not in sys.modules:
    action_t = TypeVar("action_t")
    observation_t = TypeVar("observation_t")
    state_t = TypeVar("state_t")

    class EnvClient(Generic[action_t, observation_t, state_t]):
        async def connect(self) -> None:
            return None

        async def close(self) -> None:
            return None

        @classmethod
        async def from_docker_image(cls, _image_name: str):
            return cls()

    class StepResult(Generic[observation_t]):
        def __init__(self, observation, reward=None, done: bool = False):
            self.observation = observation
            self.reward = reward
            self.done = done

    openenv_module = types.ModuleType("openenv")
    core_module = types.ModuleType("openenv.core")
    client_types_module = types.ModuleType("openenv.core.client_types")
    env_server_module = types.ModuleType("openenv.core.env_server")
    env_server_types_module = types.ModuleType("openenv.core.env_server.types")

    class Action(BaseModel):
        pass

    class Observation(BaseModel):
        pass

    class State(BaseModel):
        pass

    core_module.EnvClient = EnvClient
    client_types_module.StepResult = StepResult
    env_server_types_module.Action = Action
    env_server_types_module.Observation = Observation
    env_server_types_module.State = State

    openenv_module.core = core_module

    sys.modules["openenv"] = openenv_module
    sys.modules["openenv.core"] = core_module
    sys.modules["openenv.core.client_types"] = client_types_module
    sys.modules["openenv.core.env_server"] = env_server_module
    sys.modules["openenv.core.env_server.types"] = env_server_types_module


if "openai" not in sys.modules:
    class APIStatusError(Exception):
        pass

    class OpenAI:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    openai_module = types.ModuleType("openai")
    openai_module.APIStatusError = APIStatusError
    openai_module.OpenAI = OpenAI
    sys.modules["openai"] = openai_module
