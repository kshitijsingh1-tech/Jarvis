# Using Mistral Across Environments

## What You Have Now

This repo now exposes local Mistral in three practical ways:

1. Direct chat via `chat_with_mistral.py`
2. Tool-using agent mode via `mistral_agent.py`
3. Shared Python API via `ai_os.ai_provider`

All of them route to Ollama through the OpenAI-compatible endpoint:

`http://localhost:11434/v1`

## 1. Terminal Chat

Run:

```powershell
.\ai\Scripts\python.exe .\chat_with_mistral.py
```

This gives you a simple local assistant conversation.

## 2. Terminal Agent

Run:

```powershell
.\ai\Scripts\python.exe .\mistral_agent.py
```

This lets Mistral decide whether to:

- answer directly
- read files
- create files
- run safe shell commands in the repo

Examples:

```text
read file data/notes.txt
create file hello.py with a script that prints hello
run git status
summarize this codebase
```

## 3. Python API

```python
from ai_os.ai_provider import generateText, generateCode, chat

reply = generateText("Explain recursion simply")
code = generateCode("Write a Python function that prints hello")

messages = [
    {"role": "system", "content": "You are a coding assistant."},
    {"role": "user", "content": "Write a FastAPI example."},
]
result = chat(messages, purpose="chat")
```

## 4. Editor and Other Tools

Any client that supports an OpenAI-compatible API can be pointed at:

- Base URL: `http://localhost:11434/v1`
- API key: `ollama`
- Model: `mistral`

That includes many editor plugins, custom scripts, and internal tools.

## 5. Current Limits

This is a practical local assistant, not a full Codex replacement.

Current tool support:

- read files
- create files
- run safe shell commands
- answer directly

If you want, the next step is to add:

- file editing tools
- patch application
- project-wide search tools
- persistent session history
- a browser UI
- editor integration helpers
