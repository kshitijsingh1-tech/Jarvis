# src/domain/goal.py

from datetime import datetime
from typing import Optional, List, Set


class GoalStatus:
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    BLOCKED = "blocked"
    COMPLETION_PENDING = "completion_pending"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class Goal:

    def __init__(
        self,
        goal_id: str,
        description: str,
        priority_weight: float = 0.5,
        deadline: Optional[datetime] = None,
        parent_id: Optional[str] = None,
        tags: Optional[Set[str]] = None,
    ):
        self.goal_id = goal_id
        self.description = description
        self.priority_weight = priority_weight
        self.deadline = deadline
        self.parent_id = parent_id

        self.children_ids: List[str] = []
        self.dependencies: List[str] = []

        self.tags: Set[str] = tags or set()

        self.status = GoalStatus.CREATED
        self.progress = 0.0
        self.confidence = 1.0

        self.created_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()

    # -------------------------
    # Lifecycle Methods
    # -------------------------

    def activate(self):
        if self.status in [GoalStatus.COMPLETED, GoalStatus.FAILED]:
            raise ValueError("Cannot activate completed or failed goal.")
        self.status = GoalStatus.ACTIVE
        self._touch()

    def pause(self):
        if self.status == GoalStatus.ACTIVE:
            self.status = GoalStatus.PAUSED
            self._touch()

    def complete(self):
        self.status = GoalStatus.COMPLETED
        self.progress = 1.0
        self._touch()

    def fail(self):
        self.status = GoalStatus.FAILED
        self._touch()

    # -------------------------
    # Progress & Confidence
    # -------------------------

    def update_progress(self, value: float):
        if not 0.0 <= value <= 1.0:
            raise ValueError("Progress must be between 0 and 1.")

        self.progress = value

        if self.progress == 1.0:
            self.status = GoalStatus.COMPLETION_PENDING

        self._touch()

    def update_confidence(self, value: float):
        if not 0.0 <= value <= 1.0:
            raise ValueError("Confidence must be between 0 and 1.")
        self.confidence = value
        self._touch()

    # -------------------------
    # Hierarchy Management
    # -------------------------

    def add_child(self, child_id: str):
        if child_id not in self.children_ids:
            self.children_ids.append(child_id)
            self._touch()

    def add_dependency(self, goal_id: str):
        if goal_id not in self.dependencies:
            self.dependencies.append(goal_id)
            self._touch()

    # -------------------------
    # Utility
    # -------------------------

    def is_blocked(self):
        return self.status == GoalStatus.BLOCKED

    def _touch(self):
        self.last_updated = datetime.utcnow()