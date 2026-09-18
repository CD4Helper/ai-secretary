"""Telegram bot that talks to DeepSeek, with memory from memory.md."""

import json
import os
from dotenv import load_dotenv
from telebot import TeleBot, util
from openai import OpenAI, APIError, APIConnectionError, APITimeoutError

# Load API key, bot token, and Telegram ID from .env
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
print("API Key loaded:", api_key is not None)

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
print("Bot Token loaded:", bot_token is not None)

# .env values are text; Telegram IDs are numbers
my_id = int(os.getenv("MY_TELEGRAM_ID"))

# Connect to DeepSeek using the key
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com", timeout=30)

# Connect to Telegram using the token
bot = TeleBot(bot_token)

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


# Only respond to messages from me
def is_me(message):
    return message.from_user.id == my_id


# Message handlers
@bot.message_handler(commands=["start", "help"], func=is_me)
def send_welcome(message):
    bot.reply_to(message, "Hi! I'm your AI secretary. Send me a message.")


@bot.message_handler(func=is_me)
def handle_message(message):
    history.append({"role": "user", "content": message.text})
    try:
        # Send message to DeepSeek
        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=[system_message] + history,
        )

        # Pull the reply text out of DeepSeek's response
        reply = response.choices[0].message.content

        # Telegram caps messages at 4096 characters
        for part in util.smart_split(reply, chars_per_string=4000):
            bot.send_message(message.chat.id, part)
        print("Model:", response.model)  # Shows only in the terminal
    except (APIConnectionError, APITimeoutError):
        history.pop()
        bot.reply_to(message, "Couldn't reach DeepSeek. Try again in a moment.")
        return
    except APIError as e:
        history.pop()
        bot.reply_to(message, "DeepSeek returned an error. Check the terminal.")
        print("DeepSeek error:", e)
        return
    history.append({"role": "assistant", "content": reply})

    # Indent + ensure_ascii keep the file human-readable, including Chinese
    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


# Keep checking Telegram for new messages
bot.infinity_polling()
