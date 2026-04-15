from ai_os.ai_provider import chat


SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are Mistral running locally through Ollama. "
        "Be concise, practical, and helpful for software work."
    ),
}


def main():
    messages = [SYSTEM_MESSAGE]

    print("Local Mistral chat. Type 'exit' to stop.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break

        messages.append({"role": "user", "content": user_input})
        reply = chat(messages, purpose="chat", temperature=0.2)
        print(f"Mistral: {reply}\n")
        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
