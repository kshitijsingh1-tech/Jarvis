# Mistral Coding Agent Documentation

## Overview

The AI stack now runs through one abstraction layer: `ai_os/ai_provider.py`.
Everything else either calls that provider directly or routes through a brain that uses it.

Execution flow:

1. Config loads from `.env`.
2. `load_dotenv()` in `ai_os/ai_provider.py` reads those values.
3. `ProviderSettings` in `ai_os/ai_provider.py` resolves runtime config.
4. `get_ai_provider()` in `ai_os/ai_provider.py` creates a singleton provider.
5. Callers use `generateText()`, `generateCode()`, or `chat()` in `ai_os/ai_provider.py`.
6. The provider checks Ollama availability with `ensure_ollama_ready()` in `ai_os/ai_provider.py`.
7. The provider sends OpenAI-compatible requests to `http://localhost:11434/v1/chat/completions`.
8. Agent/tool flows use `ProviderBrain` in `ai_os/brain/provider_brain.py`.
9. The kernel router now always returns that brain in `ai_os/kernel/router.py`.

## 1. Environment Config

File: `.env`

- Line 1: `PYTHONPATH` keeps local imports working.
- Line 2: `USE_OLLAMA=true` makes local Ollama the primary provider.
- Line 3: `OLLAMA_BASE_URL=http://localhost:11434/v1` points to Ollama's OpenAI-compatible API.
- Line 4: `OLLAMA_API_KEY=ollama` is the placeholder bearer token Ollama expects.
- Lines 5-8: `OLLAMA_MODEL`, `OLLAMA_CHAT_MODEL`, `OLLAMA_CODE_MODEL`, `OLLAMA_AGENT_MODEL` all use `mistral`.
- Line 9: `AI_ENABLE_FALLBACK=false` disables cloud fallback right now.
- Lines 10-12: cloud settings remain available for later switching.

## 2. Provider Module

File: `ai_os/ai_provider.py`

- Lines 1-7: imports for JSON parsing, env/config, typing, HTTP, and dotenv loading.
- Line 10: `load_dotenv()` ensures `.env` values are available automatically.
- Lines 13-17: default constants for Ollama URL, key, and default model names.
- Lines 20-21: `AIProviderError` gives one consistent error type for all AI failures.
- Lines 24-28: `_env_flag()` converts true/false env vars into booleans.
- Lines 31-49: `ProviderSettings` is the central config object.
- Lines 33-35: top-level flags for provider choice, fallback, timeout.
- Lines 37-42: Ollama base URL, key, and routed models.
- Lines 44-49: cloud base URL, key, and routed models for optional fallback.

- Lines 52-62: `AIProvider` constructor stores settings and a reusable HTTP session.
- Lines 64-80: `generate_text()` wraps a text prompt into chat messages and routes with purpose `chat`.
- Lines 82-98: `generate_code()` does the same but routes with purpose `code`.
- Lines 100-125: `chat()` is the main request entrypoint.
- Line 111: picks the model using `_resolve_model()`.
- Lines 116-123: if `USE_OLLAMA=true`, it checks Ollama first, normalizes the model name, and sends the request.
- Line 125: if Ollama is disabled, it uses the cloud provider directly.

- Lines 127-161: `ensure_ollama_ready()`.
- Lines 133-141: calls `GET /models` on Ollama to confirm the server is up.
- Lines 143-147: returns a helpful startup error if Ollama is not reachable.
- Lines 149-153: collects the installed model IDs from Ollama.
- Lines 154-160: if the configured model is missing, raises a useful error.
- Lines 155-160: includes available local models in the error.
- Lines 154-160 also handle short names like `mistral` when Ollama reports `mistral:latest`.

- Lines 162-177: `_request_with_fallback()` retries on cloud only if fallback is enabled.
- Lines 178-196: `_request()` sends non-streaming requests.
- Line 184: always uses OpenAI-compatible `/chat/completions`.
- Lines 188-193: sends `Authorization: Bearer ...` and JSON body.
- Line 196: extracts plain text from the OpenAI-style response.

- Lines 198-232: `_stream_request()` handles server-sent event streaming.
- Lines 213-230: parses `data:` frames and yields token deltas.
- Lines 234-242: `_raise_for_status()` turns HTTP failures into readable provider errors.
- Lines 244-260: `_extract_text()` supports both string content and multipart text blocks.
- Lines 262-268: `_resolve_model()` selects chat/code/agent model by purpose.
- Lines 270-279: `_build_messages()` builds OpenAI-style message arrays.
- Lines 281-289: `_base_url()` and `_headers()` centralize transport details.
- Lines 291-297: fallback gating and error normalization.
- Lines 300-307: singleton instance management.
- Lines 310-319: public convenience API: `generateText()`, `generateCode()`, `chat()`.

## 3. Agent Brain

File: `ai_os/brain/provider_brain.py`

- Lines 1-3: imports provider access plus JSON extraction and schema validation.
- Lines 6-41: structured-action system prompt used for agent/tool execution.
- Line 44: plain chat system prompt.
- Lines 47-52: `ProviderBrain` stores the shared provider instance.
- Lines 53-84: `decide_action()` is the main brain logic.
- Lines 58-69: for tool goals like `create_file` or `read_file`, it requests one JSON action from the model.
- Line 68: parses model output into JSON.
- Line 69: validates and repairs the action shape.
- Lines 71-79: for normal chat, it returns a direct text response.
- Lines 80-84: all provider errors become safe user-facing chat messages.

## 4. Router

File: `ai_os/kernel/router.py`

- Line 1: imports `ProviderBrain`.
- Line 3: creates a single `provider_brain`.
- Lines 6-12: `choose_brain()` now always returns that brain.
- Result: routing, detection, model choice, and fallback are centralized instead of split across Gemini/Ollama classes.

## 5. App Entry Point

File: `main.py`

- Lines 1-9: imports FastAPI, Twilio, kernel loop, and provider access.
- Line 11: creates the FastAPI app.
- Lines 14-20: Twilio client and WhatsApp sender configuration.
- Lines 22-26: duplicate/rate-limit/history state.

- Lines 29-70: `ask_ai()`.
- Lines 35-43: duplicate-message and rate-limit protection.
- Lines 45-47: appends the latest user message and truncates history.
- Lines 49-57: builds OpenAI-style chat history for the provider.
- Lines 59-67: calls `provider.chat(... purpose="chat")`.
- Lines 62-63: stores assistant reply back into memory.
- Lines 68-70: provider failures return a readable error string.

- Lines 76-102: `/webhook`.
- Lines 78-81: reads WhatsApp webhook fields.
- Line 85: runs the autonomous kernel cycle.
- Lines 92-100: sends the reply through Twilio.

## 6. Backward Compatibility Files

File: `ai_os/brain/ollama_brain.py`

- Keeps the old `OllamaBrain` import path alive.
- It now inherits from `ProviderBrain` instead of calling `ollama` directly.

File: `ai_os/brain/gemini_brain.py`

- Keeps the old `GeminiBrain` import path alive.
- It no longer talks to Gemini directly.

## 7. Local Test Harness

File: `brain1/test_brain.py`

- Line 3: imports the shared provider instead of `ollama`.
- Line 7: creates provider instance.
- Line 63: uses `provider.chat(... purpose="agent")`.
- This means even the CLI-style local agent test now uses the same abstraction layer.

## What Changed Conceptually

Before:

- `main.py` called Gemini directly.
- `ollama_brain.py` called `ollama` directly.
- `gemini_brain.py` called Gemini directly.
- Routing logic was split and inconsistent.

Now:

- All AI traffic goes through one transport layer.
- Ollama is primary.
- Model routing is env-driven.
- Streaming support exists in the provider.
- Cloud fallback is available but disabled.
- Agent, chat, and code paths share one implementation.
