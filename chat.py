import json
import os
from dotenv import load_dotenv
from openai import OpenAI, APITimeoutError, APIConnectionError

# load the API key from .env
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
print("Key loaded:", api_key is not None)

# Connect to DeepSeek using the key
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com", timeout=30)

# Facts about me, sent as the system message
if os.path.exists("memory.md"):
    with open("memory.md", "r") as f:
        memory = f.read()
else:
    memory = ""
    print("The memory.md file is missing")

system_message = {"role": "system", "content": memory}

# Conversation memory: the whole chat, sent every time.
if os.path.exists("history.json"):
    with open("history.json", "r") as f:
        history = json.load(f)
else:
    history = []

print("Type 'quit' to exit.")
while True: 
    # Type a message
    message = input("You: ")
    if message == "quit":
        break
    history.append({"role": "user", "content": message})

    # Handle network failures instead of crashing
    try:
        # Send the message to DeepSeek
        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=[system_message] + history,
        )

        # Pull the reply text out of DeepSeek's response
        reply = response.choices[0].message.content
        model = response.model

        # Print the reply
        print("DeepSeek:", reply)
        print("Model:", model)

    except (APIConnectionError, APITimeoutError):
        history.pop()
        print("Couldn't reach DeepSeek. Try again in a moment.")
        continue

    history.append({"role": "assistant", "content": reply})
    with open("history.json", "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False) # indent + ensure_ascii keep the file human-readable, including Chinese