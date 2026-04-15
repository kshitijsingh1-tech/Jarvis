import asyncio
import json
import os
import time
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from twilio.rest import Client

from ai_os.ai_provider import AIProviderError, get_ai_provider
from ai_os.kernel.kernel import run_cycle

app = FastAPI()

# ---------------- STATIC FILES ----------------
# We will serve the dashboard from static/index.html
app.mount("/static", StaticFiles(directory="static"), name="static")

from ai_os.tools.jarvis_tools import get_system_stats

@app.get("/stats")
async def system_stats():
    """Returns real-time system vitals for the dashboard."""
    return get_system_stats()

@app.get("/")
async def get_dashboard():
    return FileResponse("static/index.html")

# ---------------- WEBSOCKETS ----------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                continue

manager = ConnectionManager()

from ai_os.kernel.kernel import run_cycle, PENDING_APPROVALS

app = FastAPI()

# ... ( ConnectionManager and manager remain same )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                if payload.get("type") == "approval_response":
                    cycle_id = payload.get("cycle_id")
                    status = payload.get("status") # "approved" or "rejected"
                    
                    if cycle_id in PENDING_APPROVALS:
                        PENDING_APPROVALS[cycle_id]["status"] = status
                        PENDING_APPROVALS[cycle_id]["event"].set()
                        print(f"WS: Approval for {cycle_id} set to {status}")
            except Exception as e:
                print(f"WS Payload Error: {e}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ---------------- TWILIO ----------------
twilio_client = Client(
    os.environ["TWILIO_SID"],
    os.environ["TWILIO_AUTH_TOKEN"],
)

TWILIO_NUMBER = "whatsapp:+14155238886"

# ---------------- RATE CONTROL ----------------
last_user_message = {}
last_user_call_time = {}
conversation_memory = {}
MAX_HISTORY = 10


def ask_ai(user_number: str, user_msg: str):
    """
    Shared chat helper for entrypoints that want a plain conversational reply
    without invoking the multi-step agent loop.
    """

    now = time.time()

    if last_user_message.get(user_number) == user_msg:
        return None
    last_user_message[user_number] = user_msg

    if now - last_user_call_time.get(user_number, 0) < 6:
        return "Easy, give me a few seconds..."
    last_user_call_time[user_number] = now

    history = conversation_memory.get(user_number, [])
    history.append({"role": "user", "text": user_msg})
    history = history[-MAX_HISTORY:]

    messages = [
        {
            "role": "system",
            "content": "You are a helpful WhatsApp assistant. Reply naturally.",
        }
    ]
    for msg in history:
        role = "assistant" if msg["role"] == "bot" else "user"
        messages.append({"role": role, "content": msg["text"]})

    try:
        provider = get_ai_provider()
        reply = provider.chat(messages, purpose="chat", temperature=0.3)
        history.append({"role": "bot", "text": reply})
        conversation_memory[user_number] = history

        print("MEMORY:", conversation_memory[user_number])
        print("RAW AI:", reply)
        return reply
    except AIProviderError as exc:
        print("AI ERROR:", exc)
        return str(exc)


print("===== LOADED FROM =====", __file__)


@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    form = await request.form()

    user_msg = form.get("Body")
    user_number = form.get("From")

    print("User said:", user_msg, "from", user_number)

    # Status callback for real-time dashboard updates
    async def status_callback(event, data):
        payload = json.dumps({"event": event, "data": data})
        await manager.broadcast(payload)

    # run_cycle is now async
    reply = await run_cycle(user_msg, status_callback=status_callback)

    if reply is None:
        return PlainTextResponse("OK")

    print("BOT REPLY:", reply)

    try:
        # Twilio client.messages.create is synchronous, use asyncio.to_thread
        await asyncio.to_thread(
            twilio_client.messages.create,
            from_=TWILIO_NUMBER,
            to=user_number,
            body=reply
        )
        print("Reply sent to WhatsApp")
    except Exception as exc:
        print("TWILIO SEND ERROR:", exc)

    return PlainTextResponse("OK")
