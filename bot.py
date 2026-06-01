import telebot
import logging

logging.basicConfig(level=logging.INFO)

# Твой токен
TOKEN = "8883767139:AAEpVdN2rH429LdXjaHtBSDnUOWeHTV8Oxk"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Бот запущен и работает! Я готов к работе.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Привет! Я слышу тебя, но API озвучки сейчас отключен, так как нет рабочего адреса.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.polling(none_stop=True)
    
