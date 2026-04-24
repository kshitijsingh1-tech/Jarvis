# Jarvis: An Autonomous Agentic Operating System

Jarvis is a modular, multi-step AI agent framework designed to function as a low-level "OS" for development and automation. Inspired by advanced coding assistants, it bridges the gap between simple LLM chat interfaces and fully autonomous agents capable of interacting with the file system, shell, and web.

##  The Kernel: Modular Intelligence
At the heart of the project is the **Kernel**, which manages a sophisticated thinking cycle. Instead of a single-shot response, Lucky AI-OS operates in a loop:
1.  **Intent Extraction**: Analyzes the user's objective to determine if tool usage is required.
2.  **Brain Routing**: Selects the most efficient LLM (e.g., Gemini, Mistral, or Ollama) for the specific task context.
3.  **Action Decision**: Proposes a "thought" and a resulting "action" (tool call).
4.  **HITL Approval**: Sensitive actions (like shell commands) are routed to the dashboard for human verification.
5.  **Tool Execution**: Executes the action and captures the output (e.g., terminal results, file contents).
6.  **Looping**: Feeds results back into the brain, repeating until the goal is achieved (capped at 5 steps for safety).

##  Tool Ecosystem
Lucky AI-OS is equipped with a versatile toolset managed by a centralized `ToolManager`:
- **Shell Tools**: Allows the agent to run terminal commands, install dependencies, and manage processes.
- **File Tools**: Scoped file system access (read/write) for managing project data and code.
- **Web Tools**: Capability to search the web and extract content from URLs, enabling real-time research.
- **Dev Tools**: Specialized functions for codebase exploration, pattern matching, and project-aware assistance.
- **System Vitals**: Real-time monitoring of CPU, RAM, and disk usage for the host machine.

## Human-in-the-Loop & Dashboard
Safety is paramount in an OS-level agent. Lucky AI-OS features a **"Thinking Dashboard"** built with FastAPI and WebSockets. 
- **Real-time Visualization**: Users can see the agent's internal "Chain of Thought" as it happens.
- **Approval System**: Critical commands wait for user approval via the dashboard before execution, preventing unintended system changes.
- **Interactive Console**: A premium, dark-mode interface with motion graphics that provides a professional dev environment experience.

##  WhatsApp Connectivity
Beyond the dashboard, the system integrates with the **Twilio WhatsApp API**. This allows users to control the agent remotely—sending a message like "Deploy the latest changes" or "Search for the latest news on NVIDIA" directly from their phone, with the agent handling the complex multi-step execution in the background.

## Technical Stack
- **Backend**: FastAPI (Python) for high-performance async execution.
- **LLM Abstraction**: Custom `AIProvider` layer supporting Google Gemini, Mistral (local/API), and Ollama.
- **Real-time Communication**: WebSockets for dashboard state syncing.
- **Messaging**: Twilio WhatsApp integration.
- **Persistence**: Short-term conversational memory with a roadmap for vector-based long-term retrieval.

Lucky AI-OS represents a transition from "AI as a tool" to "AI as an operator," providing a robust foundation for building personalized, autonomous development assistants that are both powerful and safe.
