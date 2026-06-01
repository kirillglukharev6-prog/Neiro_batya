import telebot
import requests
import json
import io

# ТВОИ ТОКЕНЫ (Вставь сюда свой токен от BotFather)
BOT_TOKEN = "8883767139:AAEpVdN2rH429LdXjaHtBSDnUOWeHTV8Oxk"
STEOS_TOKEN = "9711b88e-af02-438f-82f0-fa4a26f2ce07"

# ТУТ ВЫБИРАЙ ГОЛОС БАТИ:
# 515 — Жириновский
# 185 — Гоблин (Пучков)
# 552 — Лунтик
VOICE_ID = 515

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['нейро'])
def handle_neuro(message):
    # Отрезаем команду /нейро, берем только текст
    user_text = message.text.replace('/нейро', '').strip()
    
    if not user_text:
        bot.reply_to(message, "Ты забыл написать вопрос, лапоть!")
        return

    # Показываем в ТГ статус «Записывает голосовое сообщение»
    bot.send_chat_action(message.chat.id, 'record_voice')

    # Наш ответ-заглушка
    answer_text = f"Ну ты и спросил, конечно! Насчет '{user_text}' я тебе так скажу: хватит страдать ерундой, иди займись делом!"

    # Настройки для отправки на сайт SteosVoice
    url = "https://api.voice.steos.io/v1/tts/tts-binary"
    headers = {
        "Authorization": STEOS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "voice_id": VOICE_ID,
        "text": answer_text,
        "format": "mp3"
    }

    try:
        # Отправляем запрос на генерацию голоса
        response = requests.post(url, headers=headers, json=payload, verify=False)
        
        if response.status_code == 200:
            # Превращаем байты аудио в файл для отправки
            audio_file = io.BytesIO(response.content)
            audio_file.name = "voice.mp3"
            
            # Отправляем голосовуху с подписью текста
            bot.send_voice(message.chat.id, audio_file, caption=answer_text)
        else:
            bot.reply_to(message, f"Ошибка озвучки (Код: {response.status_code})")
            
    except Exception as e:
        bot.reply_to(message, f"Батя заглючил: {e}")

# Запуск бота
if __name__ == "__main__":
    print("Бот успешно запущен!")
    bot.infinity_polling()
    
