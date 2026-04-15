# ai_os/schemas/action_schema.py

ALLOWED_ACTIONS = {
    "create_file": ["filename", "content"],
    "read_file": ["filename"],
    "run_shell": ["command"],
    "chat": ["response"]
}


def validate_action(action: dict) -> dict:
    """
    Ensures the AI output matches our expected structure.
    Repairs missing fields when possible.
    """

    if not isinstance(action, dict):
        return {"action": "chat", "response": "Invalid action format."}

    action_type = action.get("action")

    if action_type not in ALLOWED_ACTIONS:
        return {"action": "chat", "response": "Unknown action requested."}

    required_fields = ALLOWED_ACTIONS[action_type]

    # fill missing fields safely
    for field in required_fields:
        if field not in action:
            action[field] = ""

    return action
