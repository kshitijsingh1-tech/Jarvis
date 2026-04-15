# kernel/safety.py

import os

ALLOWED_ACTIONS = {
    "create_file",
    "read_file",
    "run_shell",
    "search_web",
    "search_youtube",
    "chat"
}

FORBIDDEN_KEYWORDS = [
    "format",
    "shutdown",
    "restart",
    "rm -rf",
    "del /f",
    "Remove-Item",
    "Stop-Computer",
    "Restart-Computer",
    "mkfs",
    "mkpart",
    "dd if=",
]

# Filesystem constraints
DATA_DIR = os.path.abspath("D:/lucky-ai/data")
PROJECT_DIR = os.path.abspath("D:/lucky-ai")


def is_path_safe(path: str, restrict_to_data: bool = True) -> bool:
    """
    Checks if a path is safe and doesn't use '..' to escape the allowed directory.
    """
    if ".." in path or path.startswith("/") or (len(path) > 1 and path[1] == ":"):
        return False
    
    # Check if the path stays inside the intended directory
    base = DATA_DIR if restrict_to_data else PROJECT_DIR
    target = os.path.abspath(os.path.join(base, path))
    
    return target.startswith(base)


def is_action_safe(action: dict) -> tuple[bool, str]:
    """
    Verifies whether an action is allowed to run on the system.
    Returns (is_safe, reason).
    """

    if not isinstance(action, dict):
        return False, "Action must be a dictionary."

    action_type = action.get("action")

    # 1️⃣ Only known actions allowed
    if action_type not in ALLOWED_ACTIONS:
        return False, f"Action '{action_type}' is unknown or not supported."

    # 2️⃣ Path Sanitization for file operations
    if action_type == "create_file":
        filename = action.get("filename", "")
        if not is_path_safe(filename, restrict_to_data=True):
            return False, f"Path '{filename}' is restricted. You must only create files in the 'data/' directory."

    if action_type == "read_file":
        filename = action.get("filename", "")
        if not is_path_safe(filename, restrict_to_data=False):
             return False, f"Path '{filename}' is restricted. You can only read files within the project directory."

    # 3️⃣ Shell Command Validation
    if action_type == "run_shell":
        command = action.get("command", "").lower()
        
        # Block specific dangerous keywords
        for word in FORBIDDEN_KEYWORDS:
            if word in command:
                return False, f"Command contains forbidden keyword: '{word}'"
        
        # Prevent absolute paths or root access in shell
        if command.startswith("/") or " /" in command or " c:" in command:
            return False, "Shell commands cannot use absolute paths or access system root."

    return True, ""
