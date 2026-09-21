"""Shared assistant logic: DeepSeek connection, memory, and history."""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
print("API Key loaded:", api_key is not None)

# Connect to DeepSeek using the key
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com", timeout=30)

# Facts about me, sent as the system message
if os.path.exists("memory.md"):
    with open("memory.md", "r", encoding="utf-8") as f:
        memory = f.read()
else:
    memory = ""
    print("The memory.md file is missing")

system_message = {"role": "system", "content": memory}

# Conversation memory: the whole chat, sent every time
if os.path.exists("history.json"):
    with open("history.json", "r", encoding="utf-8") as f:
        history = json.load(f)
else:
    history = []


def ask_deepseek():
    """Return DeepSeek's reply to the conversation so far."""
    # Send the whole conversation to DeepSeek
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[system_message] + history,
    )

    # Pull the reply text out of DeepSeek's response
    reply = response.choices[0].message.content
    print("Model:", response.model)  # Shows only in the terminal
    return reply


def save_history():
    """Save the conversation to history.json so it survives restarts."""
    with open("history.json", "w", encoding="utf-8") as f:
        # Indent + ensure_ascii keep the file human-readable, including Chinese
        json.dump(history, f, indent=2, ensure_ascii=False)
