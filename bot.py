import telebot
import requests
import json
import io
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ТВОИ ТОКЕНЫ
BOT_TOKEN = "8883767139:AAEpVdN2rH429LdXjaHtBSDnUOWeHTV8Oxk" 
STEOS_TOKEN = "9711b88e-af02-438f-82f0-fa4a26f2ce07"

# Пробуем отправить на базовый эндпоинт tts
VOICE_ID = 515

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['нейро'])
def handle_neuro(message):
    user_text = message.text.replace('/нейro', '').strip()
    
    if not user_text:
        bot.reply_to(message, "Ты забыл написать вопрос, лапоть!")
        return

    bot.send_chat_action(message.chat.id, 'record_voice')

    answer_text = f"Ну ты и спросил, конечно! Насчет '{user_text}' я тебе так скажу: хватит страдать ерундой, иди займись делом!"

    # Пробуем еще один официальный вариант адреса
    url = "https://api.voice.steos.io/v1/tts"
    
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
        response = requests.post(url, headers=headers, json=payload, verify=False)
        
        if response.status_code == 200:
            audio_file = io.BytesIO(response.content)
            audio_file.name = "voice.mp3"
            bot.send_voice(message.chat.id, audio_file, caption=answer_text)
        else:
            # ТУТ ИЗМЕНЕНИЕ: бот пришлет развернутый текст ошибки от сервера
            error_details = response.text[:200]  # Берем первые 200 символов ответа
            bot.reply_to(message, f"Ошибка {response.status_code}. Ответ сервера: {error_details}")
            
    except Exception as e:
        bot.reply_to(message, f"Батя заглючил: {e}")

if __name__ == "__main__":
    print("Бот успешно запущен!")
    bot.infinity_polling()
    
