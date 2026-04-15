# kernel/planner.py

def extract_intent(message: str) -> dict:
    """
    Converts human language into a structured goal
    This is NOT the AI reasoning yet.
    This is system-level interpretation.
    """

    msg = message.lower()

    # FILE CREATION
    if "create file" in msg or "make file" in msg:
        return {
            "goal": "create_file",
            "raw": message
        }

    # READ FILE
    if "read file" in msg or "open file" in msg:
        return {
            "goal": "read_file",
            "raw": message
        }

    # GENERAL QUESTION
    return {
        "goal": "chat",
        "raw": message
    }