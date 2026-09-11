import os
from dotenv import load_dotenv
from openai import OpenAI

# B: load the API key from .env
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
print("Key loaded:", api_key is not None)

# D: Connect to DeepSeek using the key
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# Conversation memory: the whole chat, sent everytime.
history = []

print("Type 'quit' to exit.")
while True: 
    # C: Type a message
    message = input("You: ")
    if message == "quit":
        break
    history.append({"role": "user", "content": message})

    # E: Send the message to DeepSeek
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=history,
    )

    # F: Pull the reply text out of DeepSeek's response
    reply = response.choices[0].message.content
    model = response.model
    history.append({"role": "assistant", "content": reply})

    # A: Print the reply
    print("DeepSeek:", reply)
    print("Model:", model)