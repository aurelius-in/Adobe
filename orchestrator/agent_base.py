from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict


class AgentContext(dict[str, Any]):
    """Mutable blackboard shared by agents (brief, workdir, artifacts, scores)."""


class Agent(ABC):
    name: str = "agent"

    def __init__(self, cfg: Dict[str, Any] | None = None):
        self.cfg = cfg or {}

    @abstractmethod
    def run(self, ctx: AgentContext) -> AgentContext:
        ...


def require(ctx: AgentContext, *keys: str):
    missing = [k for k in keys if k not in ctx]
    if missing:
        raise ValueError(f"Missing in context: {missing}")


