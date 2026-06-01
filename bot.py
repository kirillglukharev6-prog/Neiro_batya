import telebot
import requests
import io
import logging

logging.basicConfig(level=logging.INFO)

# ТВОЙ ТОКЕН БОТА (полученный от @BotFather)
BOT_TOKEN = "7963359005:AAEq6D1ZpE0mX4C1v4G3w2G3w2G3w2G3w2G"
# ТВОЙ USER TOKEN (из личного кабинета Steos)
STEOS_TOKEN = "9711b88e-af02-438f-82f0-fa4a26f2ce07"
# ID голоса
VOICE_ID = 882

# АДРЕС API (из твоей документации)
TTS_URL = "https://public.api.voice.steos.io/api/v1/synthesis-by-text"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Батя на связи! Бот запущен и готов к работе.")

@bot.message_handler(commands=['нейро'])
def handle_neuro(message):
    user_text = message.text.replace('/нейро', '', 1).strip()
    if not user_text:
        bot.reply_to(message, "Ты забыл написать вопрос!")
        return

    bot.send_chat_action(message.chat.id, 'record_voice')

    # Формируем тело запроса согласно документации
    payload = {
        "userToken": STEOS_TOKEN,
        "voice_id": VOICE_ID,
        "text": user_text,
        "format": "mp3"
    }

    try:
        response = requests.post(TTS_URL, json=payload, timeout=15)
        if response.status_code == 200:
            bot.send_voice(message.chat.id, io.BytesIO(response.content))
        else:
            bot.reply_to(message, f"Ошибка API {response.status_code}: {response.text}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.infinity_polling()
    
