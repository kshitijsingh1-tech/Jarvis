# memory/short_term.py

MAX_MEMORY = 10  # last 10 interactions

conversation_history = []


def store_interaction(user_message: str, action: dict, result: str):
    """
    Saves the last interactions so the AI has context
    """

    entry = {
        "user": user_message,
        "action": action,
        "result": result
    }

    conversation_history.append(entry)

    # keep memory bounded
    if len(conversation_history) > MAX_MEMORY:
        conversation_history.pop(0)


def get_memory():
    """
    Returns recent conversation history
    """
    return conversation_history