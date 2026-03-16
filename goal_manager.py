# src/domain/goal_manager.py

from typing import Dict, List
from domain.goal import Goal, GoalStatus


class GoalManager:

    def __init__(self):
        self.goals: Dict[str, Goal] = {}

    # -------------------------
    # CRUD
    # -------------------------

    def add_goal(self, goal: Goal):
        self.goals[goal.goal_id] = goal

    def get_goal(self, goal_id: str) -> Goal:
        return self.goals.get(goal_id)

    def all_goals(self) -> List[Goal]:
        return list(self.goals.values())

    # -------------------------
    # Dependency Check
    # -------------------------

    def is_goal_ready(self, goal: Goal) -> bool:
        """
        A goal is ready if:
        - It is ACTIVE
        - All dependencies are COMPLETED
        """

        if goal.status != GoalStatus.ACTIVE:
            return False

        for dep_id in goal.dependencies:
            dep_goal = self.get_goal(dep_id)
            if not dep_goal or dep_goal.status != GoalStatus.COMPLETED:
                return False

        return True

    # -------------------------
    # Executable Goals
    # -------------------------

    def get_ready_goals(self) -> List[Goal]:
        return [
            goal for goal in self.goals.values()
            if self.is_goal_ready(goal)
        ]