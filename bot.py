import telebot
import requests
import io
import logging
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ТОКЕНЫ
BOT_TOKEN = "7963359005:AAEq6D1ZpE0mX4C1v4G3w2G3w2G3w2G3w2G" 
STEOS_TOKEN = "9711b88e-af02-438f-82f0-fa4a26f2ce07"

# ID Доктора Фуфелшмерца
VOICE_ID = 882

# Список адресов API для проверки
URLS_TO_TRY = [
    "https://public.api.voice.steos.io/api/v2/tts/synthesize",
    "https://public.api.voice.steos.io/api/v1/tts/synthesize",
    "https://public.api.voice.steos.io/api/v1/tts/tts-binary"
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
    
    for url in URLS_TO_TRY:
        try:
            logger.info(f"Запрос звука на: {url}")
            response = requests.post(url, headers=headers, json=payload, verify=False, timeout=8)
            if response.status_code == 200:
                return response.content
            else:
                last_tts_error = f"Код {response.status_code} на {url}"
                continue
        except Exception as e:
            last_tts_error = f"Сбой {url}: {e}"
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
        bot.reply_to(message, f"Ошибка озвучки!\n{last_tts_error}")

if __name__ == "__main__":
    logger.info("Жесткий сброс старых сессий Telegram...")
    bot.remove_webhook()
    time.sleep(1)
    
    logger.info("Бот запущен в режиме безопасного пуллинга!")
    
    offset = 0
    while True:
        try:
            # Ручной сбор обновлений с защитой от долгого зависания сессий
            updates = bot.get_updates(offset=offset, timeout=10, allowed_updates=["message"])
            for update in updates:
                if update.message:
                    bot.process_new_messages([update.message])
                offset = update.update_id + 1
        except telebot.apihelper.ApiTelegramException as e:
            if e.error_code == 409:
                # Если копия всё же дерётся в памяти, плавно ждём и продолжаем без падения
                time.sleep(2)
            else:
                logger.error(f"Ошибка Telegram API: {e}")
                time.sleep(1)
        except Exception as e:
            logger.error(f"Ошибка цикла: {e}")
            time.sleep(1)
            
