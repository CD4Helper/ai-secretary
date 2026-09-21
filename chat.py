"""Terminal chat with the assistant, for testing without Telegram."""

from openai import APIError, APITimeoutError, APIConnectionError

from assistant import history, ask_deepseek, save_history

print("Type 'quit' to exit.")
while True:
    # Type a message
    message = input("You: ")
    if message == "quit":
        break
    history.append({"role": "user", "content": message})

    # Handle DeepSeek errors instead of crashing
    try:
        reply = ask_deepseek()
        if not reply:
            history.pop()
            print("DeepSeek returned an empty reply.")
            continue
        print("DeepSeek:", reply)
    except (APIConnectionError, APITimeoutError):
        history.pop()
        print("Couldn't reach DeepSeek. Try again in a moment.")
        continue
    except APIError as e:
        history.pop()
        print("DeepSeek error:", e)
    history.append({"role": "assistant", "content": reply})
    save_history()
