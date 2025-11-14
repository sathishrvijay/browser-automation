"""
Lightweight dataclasses used across the agentic automation system.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ActionPlan:
    action: str
    selector_type: Optional[str] = None
    selector_value: Optional[str] = None
    value: Optional[str] = None
    wait_for: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActionPlan":
        return cls(
            action=data.get("action", ""),
            selector_type=data.get("selector_type"),
            selector_value=data.get("selector_value"),
            value=data.get("value"),
            wait_for=data.get("wait_for"),
            metadata={"raw": data},
        )

    def to_dict(self) -> Dict[str, Any]:
        base = {
            "action": self.action,
            "selector_type": self.selector_type,
            "selector_value": self.selector_value,
            "value": self.value,
            "wait_for": self.wait_for,
        }
        base.update(self.metadata)
        return base


@dataclass
class StepResult:
    step_number: int
    description: Dict[str, Any]
    action_plan: ActionPlan
    success: bool
    message: str

