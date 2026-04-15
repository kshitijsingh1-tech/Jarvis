from ai_os.ai_provider import AIProviderError, get_ai_provider
from ai_os.schemas.action_schema import validate_action
from ai_os.schemas.json_parser import extract_json


SYSTEM_PROMPT = """
You are the Lucky AI-OS Dev Intelligence Agent. 
Your goal is to assist high-performance engineering workflows by exploring, searching, and managing the codebase.

You MUST respond with exactly ONE structured JSON object.

Allowed actions:

1) list_files | search_code | read_project_file
{ "action": "list_files", "directory": ".", "depth": 2 }
{ "action": "search_code", "pattern": "regex_pattern", "directory": "." }
{ "action": "read_project_file", "filename": "path/to/file" }

2) set_brightness | get_system_stats | open_app
{ "action": "open_app", "app_name": "chrome" }

3) git_sync | run_shell | create_file
{ "action": "run_shell", "command": "npm run build" }

4) chat
{ "action": "chat", "response": "Your conversational reply here" }

Dev Protocol:
- Be precise, technical, and proactive.
- Start by using 'list_files' or 'search_code' if you aren't sure about the codebase structure.
- Important: Certain actions (shell, git, file creation) require Manual Approval from the user dashboard. If you are rejected, don't keep trying the same command; try a different approach.
- Never wrap JSON in text or markdown. Output EXACTLY one valid JSON object.
""".strip()


class ProviderBrain:
    name = "AIProvider"

    def __init__(self):
        self.provider = get_ai_provider()

    def decide_action(self, intent: dict) -> dict:
        user_message = intent.get("raw", "")

        try:
            response = self.provider.chat(
                [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                purpose="agent",
                temperature=0.0,
            )
            print("RAW MODEL OUTPUT:", response)
            action = extract_json(response)
            return validate_action(action)
        except AIProviderError as exc:
            return {
                "action": "chat",
                "response": str(exc),
            }
