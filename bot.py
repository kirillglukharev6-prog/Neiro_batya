import telebot
import requests
import io
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ТОКЕНЫ — Вставь сюда свои настоящие ключи внутри кавычек!
BOT_TOKEN = "8883767139:AAEpVdN2rH429LdXjaHtBSDnUOWeHTV8Oxk" 
STEOS_TOKEN = "9711b88e-af02-438f-82f0-fa4a26f2ce07"

# ID голосов: 515 — Жириновский, 185 — Гоблин, 552 — Лунтик
VOICE_ID = 515

# Самый точный прямой адрес для моментального получения MP3 файла
TTS_URL = "https://public.api.voice.steos.io/api/v1/tts/tts-binary"
MAX_TEXT_LENGTH = 800  # Лимит символов

bot = telebot.TeleBot(BOT_TOKEN)

def synthesize_voice(text: str) -> bytes | None:
    """Отправляет запрос на синтез речи. Возвращает байты аудио или None."""
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
        response = requests.post(
            TTS_URL,
            headers=headers,
            json=payload,
            verify=False,
            timeout=15
        )
        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"TTS ошибка {response.status_code}: {response.text[:300]}")
            return None
    except requests.exceptions.Timeout:
        logger.error("TTS запрос превысил таймаут")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"TTS сетевая ошибка: {e}")
        return None

def build_answer(user_text: str) -> str:
    """Формирует текст ответа."""
    return (
        f"Ну ты и спросил, конечно! "
        f"Насчёт {user_text} я тебе так скажу: "
        f"хватит страдать ерундой, иди займись делом!"
    )

@bot.message_handler(commands=['нейро'])
def handle_neuro(message):
    user_text = message.text.replace('/нейро', '', 1).strip()

    if not user_text:
        bot.reply_to(message, "Ты забыл написать вопрос, лапоть!")
        return

    if len(user_text) > MAX_TEXT_LENGTH:
        bot.reply_to(message, f"Слишком длинный текст! Максимум {MAX_TEXT_LENGTH} символов.")
        return

    bot.send_chat_action(message.chat.id, 'record_voice')

    answer_text = build_answer(user_text)
    audio_bytes = synthesize_voice(answer_text)

    if audio_bytes:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "voice.mp3"
        bot.send_voice(message.chat.id, audio_file, caption=answer_text[:1024])
    else:
        bot.reply_to(message, f"Не удалось синтезировать голос. Проверь логи или настройки.")

@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    bot.reply_to(
        message,
        "Привет! Используй команду:\n/нейро <вопрос>\n\nПример:\n/нейро Как дела?"
    )

if __name__ == "__main__":
    logger.info("Бот успешно запущен!")
    bot.infinity_polling(none_stop=True, interval=1)
    
