# src/domain/fairness_tracker.py

from datetime import datetime
from typing import Dict


class FairnessTracker:

    def __init__(self):
        self.selection_count: Dict[str, float] = {}
        self.last_selected_at: Dict[str, datetime] = {}

        # tuning parameters
        self.decay_rate = 0.1
        self.starvation_threshold_seconds = 60
        self.starvation_boost_value = 0.2

    def record_selection(self, goal_id: str):
        now = datetime.utcnow()

        self.selection_count[goal_id] = (
            self.selection_count.get(goal_id, 0) + 1
        )

        self.last_selected_at[goal_id] = now

    def compute_adjustment(self, goal_id: str) -> float:
        now = datetime.utcnow()

        count = self.selection_count.get(goal_id, 0)
        last_selected = self.last_selected_at.get(goal_id)

        # Apply decay to selection count
        decayed_count = count * (1 - self.decay_rate)

        self.selection_count[goal_id] = decayed_count

        fairness_penalty = decayed_count * 0.2

        starvation_boost = 0.0

        if last_selected:
            seconds_since = (now - last_selected).total_seconds()
            if seconds_since > self.starvation_threshold_seconds:
                starvation_boost = self.starvation_boost_value

        return -fairness_penalty + starvation_boost