from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BudgetState:
    limits: dict[str, int | float] = field(default_factory=dict)
    usage: dict[str, int | float] = field(default_factory=dict)
    paused: bool = False

    def consume(self, metric: str, amount: int | float = 1) -> bool:
        if amount < 0:
            raise ValueError("amount cannot be negative")
        new_value = self.usage.get(metric, 0) + amount
        limit = self.limits.get(metric)
        if limit is not None and new_value > limit:
            self.paused = True
            return False
        self.usage[metric] = new_value
        return True
