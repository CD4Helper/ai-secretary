"""Telegram bot that talks to DeepSeek."""

import os

from dotenv import load_dotenv
from openai import APIError, APIConnectionError, APITimeoutError
from telebot import TeleBot, util

from assistant import history, ask_deepseek, save_history

# Load bot token and Telegram ID from .env
load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
print("Bot Token loaded:", bot_token is not None)

# .env values are text; Telegram IDs are numbers
my_id = int(os.getenv("MY_TELEGRAM_ID"))

# Connect to Telegram using the token
bot = TeleBot(bot_token)


def is_me(message):
    """Return True only for messages sent by me."""
    return message.from_user.id == my_id


def send_reply(chat_id, reply):
    """Send a reply to Telegram, split if it exceeds the message limit."""
    for part in util.smart_split(reply, chars_per_string=4000):
        bot.send_message(chat_id, part)


# Message handlers
@bot.message_handler(commands=["start", "help"], func=is_me)
def send_welcome(message):
    bot.reply_to(message, "Hi! I'm your AI secretary. Send me a message.")


@bot.message_handler(func=is_me)
def handle_message(message):
    history.append({"role": "user", "content": message.text})
    try:
        reply = ask_deepseek()
        if not reply:
            history.pop()
            bot.reply_to(message, "DeepSeek returned an empty reply.")
            return
        send_reply(message.chat.id, reply)
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
    save_history()


# Keep checking Telegram for new messages
bot.infinity_polling()
