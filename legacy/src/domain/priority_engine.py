# src/domain/priority_engine.py

from datetime import datetime
from domain.goal import Goal, GoalStatus


class PriorityEngine:

    def compute_score(self, goal: Goal) -> float:

        if goal.status in [GoalStatus.COMPLETED, GoalStatus.FAILED, GoalStatus.ARCHIVED]:
            return 0.0

        # -------------------------
        # Urgency Score
        # -------------------------

        urgency_score = 0.0

        if goal.deadline:
            time_left = (goal.deadline - datetime.utcnow()).total_seconds()

            if time_left <= 0:
                urgency_score = 1.0
            else:
                # Normalize: closer deadline → higher urgency
                urgency_score = min(1.0, 1 / (time_left / 86400 + 1))

        # -------------------------
        # Score Components
        # -------------------------

        priority_component = goal.priority_weight
        progress_component = 1 - goal.progress
        confidence_component = 1 - goal.confidence

        score = (
            priority_component * 0.4
            + urgency_score * 0.3
            + progress_component * 0.2
            + confidence_component * 0.1
        )

        return round(score, 4)