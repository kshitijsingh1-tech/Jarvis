import json

from ai_os.ai_provider import get_ai_provider
from ai_os.automation.tools import create_file, read_file

messages = []
provider = get_ai_provider()

SYSTEM_PROMPT = """
You are an AI assistant with tools.

TOOLS:

1) create_file
Creates a file.
Format:
{
  "action": "create_file",
  "filename": "...",
  "content": "..."
}

2) read_file
Reads a file.
Format:
{
  "action": "read_file",
  "filename": "..."
}

Rules:
- Respond ONLY JSON when using a tool
- Otherwise respond normally
""".strip()

messages.append({"role": "system", "content": SYSTEM_PROMPT})


def extract_json(text):
    start = text.find("{")
    if start == -1:
        return None

    stack = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            stack += 1
        elif text[index] == "}":
            stack -= 1
            if stack == 0:
                return text[start:index + 1]
    return None


print("Agent ready. Type exit to stop.\n")

while True:
    user = input("You: ")
    if user.lower() == "exit":
        break

    messages.append({"role": "user", "content": user})
    reply = provider.chat(messages, purpose="agent", temperature=0.0)

    print("\nRAW AI:", reply)

    try:
        json_text = extract_json(reply)

        if json_text:
            data = json.loads(json_text)

            if data.get("action") == "create_file":
                result = create_file(data["filename"], data["content"])
                print("ACTION RESULT:", result)
                messages.append({"role": "assistant", "content": result})
                continue

            if data.get("action") == "read_file":
                result = read_file(data["filename"])
                print("ACTION RESULT:", result)
                messages.append({"role": "assistant", "content": result})
                continue

    except Exception as exc:
        print("Parse error:", exc)

    print("AI:", reply)
    messages.append({"role": "assistant", "content": reply})
