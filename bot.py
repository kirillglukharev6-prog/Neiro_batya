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

# ID Доктора Фуфелшмерца
VOICE_ID = 882

# Список всех возможных адресов API (от старых к самым новым v2)
URLS_TO_TRY = [
    "https://public.api.voice.steos.io/api/v2/tts/synthesize",
    "https://public.api.voice.steos.io/api/v1/tts/tts-binary",
    "https://api.voice.steos.io/api/v1/tts/tts-binary"
]

bot = telebot.TeleBot(BOT_TOKEN)
last_tts_error = "Ошибок пока нет"

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
    
    # Бот по очереди проверит каждый адрес из списка
    for url in URLS_TO_TRY:
        try:
            logger.info(f"Пробуем отправить запрос на: {url}")
            response = requests.post(url, headers=headers, json=payload, verify=False, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Успешно! Рабочий адрес найден: {url}")
                return response.content
            else:
                last_tts_error = f"Адрес {url} вернул код {response.status_code}. Ответ: {response.text[:100]}"
                continue # Если 404 или другая ошибка, переходим к следующему адресу
        except Exception as e:
            last_tts_error = f"Сбой сети на {url}: {e}"
            continue
            
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
        bot.reply_to(message, f"Ошибка озвучки!\nПоследний лог: {last_tts_error}")

if __name__ == "__main__":
    logger.info("Сбрасываем старые конфликты...")
    bot.remove_webhook()
    
    logger.info("Бот успешно запущен!")
    bot.infinity_polling(none_stop=True, skip_pending=True)
    
