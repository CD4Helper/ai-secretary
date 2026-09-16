import os
from dotenv import load_dotenv
from telebot import TeleBot

# load the Telegram Bot Token from .env
load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
print("Key loaded:", bot_token is not None)
bot = TeleBot(bot_token)

# The body part of the bot
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

# This keep the bot active
bot.infinity_polling()
