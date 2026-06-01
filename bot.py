import telebot
import requests
import io
import logging
import urllib3
from threading import Thread
from flask import Flask

# Отключаем предупреждения об SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ТОКЕНЫ
BOT_TOKEN = "8883767139:AAEpVdN2rH429LdXjaHtBSDnUOWeHTV8Oxk" 
STEOS_TOKEN = "9711b88e-af02-438f-82f0-fa4a26f2ce07"

# Настройки голоса
VOICE_ID = 882
TTS_URL = "https://public.api.voice.steos.io/api/v1/tts/synthesize"

bot = telebot.TeleBot(BOT_TOKEN)
last_tts_error = "Ошибок пока нет"

# СОЗДАЕМ МИКРО-САЙТ ДЛЯ ОБМАНА RENDER
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот Фуфелшмерца активен и работает!"

def run_flask():
    # Render автоматически передает порт 10000 в этот скрипт
    app.run(host='0.0.0.0', port=10000)

def synthesize_voice(text: str) -> bytes | None:
    global last_tts_error
    headers = {
        "Authorization": STEOS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "voice_id": VOICE_ID,
        "text": text,
        "format": "mp3"
    }
    try:
        response = requests.post(TTS_URL, headers=headers, json=payload, verify=False, timeout=15)
        if response.status_code == 200:
            return response.content
        else:
            last_tts_error = f"Код: {response.status_code}, Ответ: {response.text[:150]}"
            return None
    except Exception as e:
        last_tts_error = f"Сетевой сбой: {e}"
        return None

@bot.message_handler(commands=['нейро'])
def handle_neuro(message):
    user_text = message.text.replace('/нейро', '', 1).strip()

    if not user_text:
        bot.reply_to(message, "Ты забыл написать вопрос, лапоть!")
        return

    bot.send_chat_action(message.chat.id, 'record_voice')

    answer_text = f"Ну ты и спросил, конечно! Насчёт {user_text} я тебе так скажу: хватит страдать ерундой, иди займись делом!"
    audio_bytes = synthesize_voice(answer_text)

    if audio_bytes:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "voice.mp3"
        bot.send_voice(message.chat.id, audio_file, caption=answer_text[:1024])
    else:
        bot.reply_to(message, f"Ошибка озвучки!\n{last_tts_error}")

if __name__ == "__main__":
    # 1. Запускаем "сайт" в отдельном потоке, чтобы Render был доволен
    server_thread = Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()
    logger.info("Микро-сервер Flask запущен на порту 10000")

    # 2. Очищаем старые зависшие сессии Телеграма
    bot.remove_webhook()
    
    # 3. Запускаем самого бота
    logger.info("Бот успешно запущен!")
    bot.infinity_polling(none_stop=True, skip_pending=True)
    
