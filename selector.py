# src/domain/selector.py

from typing import Optional
from domain.goal_manager import GoalManager
from domain.priority_engine import PriorityEngine
from domain.fairness_tracker import FairnessTracker
from domain.goal import Goal


class GoalSelector:

    def __init__(
        self,
        manager: GoalManager,
        engine: PriorityEngine,
        fairness: FairnessTracker
    ):
        self.manager = manager
        self.engine = engine
        self.fairness = fairness

    def select_next_goal(self) -> Optional[Goal]:

        ready_goals = self.manager.get_ready_goals()

        if not ready_goals:
            print("No ready goals.")
            return None

        scored_goals = []

        for goal in ready_goals:
            base_score = self.engine.compute_score(goal)
            fairness_adjustment = self.fairness.compute_adjustment(goal.goal_id)

            final_score = base_score + fairness_adjustment

            scored_goals.append((goal, final_score))

        scored_goals.sort(key=lambda x: x[1], reverse=True)

        selected_goal = scored_goals[0][0]

        self.fairness.record_selection(selected_goal.goal_id)

        print("\n---- FINAL SCORING ----")
        for goal, score in scored_goals:
            print(goal.goal_id, "=>", round(score, 4))

        print("Selected:", selected_goal.goal_id)

        return selected_goal