# tools/tool_manager.py

from ai_os.tools.file_tools import create_file, read_file
from ai_os.tools.shell_tools import run_shell
from ai_os.tools.web_tools import search_web, search_youtube
from ai_os.tools.jarvis_tools import set_brightness, get_system_stats, open_app, git_repo_sync
from ai_os.tools.code_tools import write_engineering_code
from ai_os.tools.dev_tools import list_files_recursive, search_code, read_project_file

# Actions that require Manual Approval via the Dashboard
APPROVAL_REQUIRED_ACTIONS = {
    "run_shell",
    "git_sync",
    "modify_file", # For future use
    "create_file"
}

def execute_action(action: dict):
    """
    Central place where actions are executed.
    No other part of the system should run tools directly.
    """

    action_type = action.get("action")

    # --- Dev Intelligence Tools ---
    if action_type == "list_files":
        directory = action.get("directory", ".")
        depth = action.get("depth", 2)
        return list_files_recursive(directory, max_depth=depth)

    elif action_type == "search_code":
        pattern = action.get("pattern", "")
        directory = action.get("directory", ".")
        return search_code(pattern, directory)

    elif action_type == "read_project_file":
        filename = action.get("filename", "")
        return read_project_file(filename)

    # --- Standard Tools ---
    elif action_type == "create_file":
        filename = action.get("filename", "new_file.txt")
        content = action.get("content","")
        return create_file(filename, content)

    elif action_type == "read_file":
        filename = action.get("filename")
        return read_file(filename)

    elif action_type == "run_shell":
        command = action.get("command", "")
        return run_shell(command)

    elif action_type == "search_web":
        query = action.get("query", "")
        return search_web(query)

    elif action_type == "search_youtube":
        query = action.get("query", "")
        return search_youtube(query)

    # --- JARVIS Engineering Tools ---
    elif action_type == "set_brightness":
        level = action.get("level", 50)
        return set_brightness(level)

    elif action_type == "get_system_stats":
        return str(get_system_stats())

    elif action_type == "open_app":
        app_name = action.get("app_name", "")
        return open_app(app_name)

    elif action_type == "git_sync":
        message = action.get("message", "JARVIS: Automated engineering sync")
        return git_repo_sync(message)

    elif action_type == "write_code":
        request = action.get("request", "")
        target_file = action.get("target_file", "generated_script.py")
        return write_engineering_code(request, target_file)

    elif action_type == "chat":
        # Chat actions just return text response
        return action.get("response", "")

    return "Unknown action"
