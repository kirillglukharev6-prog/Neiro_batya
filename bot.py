import telebot
import requests
import io
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ТОКЕНЫ
BOT_TOKEN = "8883767139:AAEpVdN2rH429LdXjaHtBSDnUOWeHTV8Oxk" 
STEOS_TOKEN = "9711b88e-af02-438f-82f0-fa4a26f2ce07"

# ID Фуфелшмерца
VOICE_ID = 882

# ОБНОВЛЕННЫЙ АДРЕС ИЗ НОВОЙ ДОКУМЕНТАЦИИ API
TTS_URL = "https://public.api.voice.steos.io/api/v2/tts/synthesize"

bot = telebot.TeleBot(BOT_TOKEN)
last_tts_error = "Ошибок пока нет"

def synthesize_voice(text: str) -> bytes | None:
    global last_tts_error
    headers = {
        "Authorization": STEOS_TOKEN,
        "Content-Type": "application/json"
    }
    # В v2 API параметры передаются именно так
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
    logger.info("Бот успешно запущен!")
    bot.infinity_polling(none_stop=True, skip_pending=True)
    
