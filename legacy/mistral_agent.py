from ai_os.kernel.kernel import run_cycle


def main():
    print("Local Mistral agent. Type 'exit' to stop.\n")
    print("Examples:")
    print("- read file notes.txt")
    print("- create file demo.py with hello world")
    print("- run git status")
    print("- summarize this project\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break

        reply = run_cycle(user_input)
        print(f"Agent: {reply}\n")


if __name__ == "__main__":
    main()
