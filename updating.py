import telebot
from dotenv import load_dotenv
import os


load_dotenv()
API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)
print(bot.get_webhook_info())


@bot.message_handler()
def greet(message):
    bot.send_message(message.chat.id, 'Bot under maintainance. Please check again later.')


bot.polling()
