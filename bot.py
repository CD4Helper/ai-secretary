import os
from dotenv import load_dotenv
from telebot import TeleBot

# load the Telegram Bot Token from .env
load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
my_id = int(os.getenv("MY_TELEGRAM_ID")) # Telegram ID is number so int() is important
print("Key loaded:", bot_token is not None)
bot = TeleBot(bot_token)

# The body part of the bot
@bot.message_handler(commands=['start', 'help'], func=lambda message: message.from_user.id == my_id)
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda message: message.from_user.id == my_id)
def echo_all(message):
    bot.reply_to(message, message.text)

# This keep the bot active
bot.infinity_polling()
