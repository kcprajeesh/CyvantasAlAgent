from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentSpec:
    id: str
    name: str
    description: str = ""
    version: str = "1"
    risk_level: str = "low"
    requires: tuple[str, ...] = ()
    produces: tuple[str, ...] = ()
    tools: tuple[str, ...] = ()
    scope_types: tuple[str, ...] = ()
    can_execute: bool = False
    can_write_files: bool = False
    can_network: bool = False
    can_browser: bool = False
    max_concurrency: int = 1


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, AgentSpec] = {}

    def register(self, spec: AgentSpec) -> None:
        if spec.id in self._agents:
            raise ValueError(f"agent already registered: {spec.id}")
        if spec.max_concurrency < 1:
            raise ValueError("max_concurrency must be >= 1")
        self._agents[spec.id] = spec

    def get(self, agent_id: str) -> AgentSpec:
        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise KeyError(f"unknown agent: {agent_id}") from exc

    def list(self) -> list[AgentSpec]:
        return sorted(self._agents.values(), key=lambda item: item.id)
