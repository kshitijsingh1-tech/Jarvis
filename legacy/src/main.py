from domain.goal import Goal
from domain.goal_manager import GoalManager
from domain.priority_engine import PriorityEngine


def test_goal_manager():

    manager = GoalManager()
    engine = PriorityEngine()

    for g in manager.get_ready_goals():
     score = engine.compute_score(g)
     print(g.goal_id, "score:", score)

    # Create goals
    g1 = Goal("G1", "Complete Research Paper")
    g2 = Goal("G2", "Collect Data")
    g3 = Goal("G3", "Write Draft")

    # g3 depends on g2
    g3.add_dependency("G2")

    # Add goals
    manager.add_goal(g1)
    manager.add_goal(g2)
    manager.add_goal(g3)

    # Activate goals
    g1.activate()
    g2.activate()
    g3.activate()

    print("READY GOALS (before completion):")
    for g in manager.get_ready_goals():
        print(g.goal_id)

    # Complete dependency
    g2.complete()

    print("\nREADY GOALS (after G2 completed):")
    for g in manager.get_ready_goals():
        print(g.goal_id)


if __name__ == "__main__":
    test_goal_manager()