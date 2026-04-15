from ai_os.kernel.planner import extract_intent
from ai_os.kernel.router import choose_brain
from ai_os.kernel.safety import is_action_safe
from ai_os.tools.tool_manager import execute_action, APPROVAL_REQUIRED_ACTIONS
from ai_os.memory.short_term import store_interaction


import asyncio
import uuid

# In-memory storage for pending approvals
# Maps cycle_id -> { "event": asyncio.Event, "status": "pending" | "approved" | "rejected" }
PENDING_APPROVALS = {}

async def run_cycle(user_message: str, status_callback=None):
    """
    Multi-step autonomous thinking cycle of the AI-OS (Async version)
    """
    cycle_id = str(uuid.uuid4())[:8]

    async def emit(event, data):
        if status_callback:
            # Include cycle_id so the dashboard knows which request is asking for help
            data["cycle_id"] = cycle_id
            await status_callback(event, data)

    print(f"\n--- AI OS CYCLE START ({cycle_id}) ---")
    await emit("cycle_start", {"message": user_message})

    # ... (rest of step 1 & 2 remains same)
    intent = await asyncio.to_thread(extract_intent, user_message)
    await emit("intent_extracted", {"intent": intent})

    brain = await asyncio.to_thread(choose_brain, intent)
    await emit("brain_selected", {"brain": brain.name})

    context = user_message
    final_response = ""

    for step in range(5):
        print(f"\n--- Step {step + 1} ---")
        await emit("step_start", {"step": step + 1})

        action = await asyncio.to_thread(brain.decide_action, {"raw": context})
        print("Proposed Action:", action)
        await emit("action_proposed", {"action": action})

        if action.get("action") == "chat":
            final_response = action.get("response", "")
            await emit("final_response", {"response": final_response})
            break

        # Safety Check
        is_safe, reason = is_action_safe(action)
        if not is_safe:
            print(f"⚠️ Safety Block: {reason}")
            await emit("safety_block", {"reason": reason})
            context += f"\nSafety Error: {reason}. Please try a safer alternative."
            continue

        # --- HITL (Manual Approval) Logic ---
        action_type = action.get("action")
        if action_type in APPROVAL_REQUIRED_ACTIONS:
            print(f"⏳ Waiting for Manual Approval on '{action_type}'...")
            
            approval_event = asyncio.Event()
            PENDING_APPROVALS[cycle_id] = {"event": approval_event, "status": "pending"}
            
            await emit("waiting_for_approval", {"action": action})
            
            # Wait for main.py to trigger this event via WebSocket feedback
            await approval_event.wait()
            
            status = PENDING_APPROVALS[cycle_id]["status"]
            del PENDING_APPROVALS[cycle_id]
            
            if status == "rejected":
                print("❌ Action rejected by user.")
                await emit("action_rejected", {"action": action_type})
                context += f"\nUser Rejected: You tried to run {action_type}, but I (the user) declined. Try something else or explain why you needed it."
                continue
            
            print("✅ Action approved by user.")
            await emit("action_approved", {"action": action_type})

        # Execute tool
        await emit("executing_tool", {"action": action.get("action")})
        result = await asyncio.to_thread(execute_action, action)
        print("Execution Result:", result)
        await emit("tool_result", {"result": result})

        store_interaction(user_message, action, result)
        context += f"\nTool Result: {result}"

    else:
        final_response = "Task execution limit reached."
        await emit("final_response", {"response": final_response})

    print(f"\n--- AI OS CYCLE END ({cycle_id}) ---\n")
    await emit("cycle_end", {})

    return final_response