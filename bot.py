import telebot
import requests
import io
import os
from gtts import gTTS

# Твой токен от BotFather
TG_TOKEN = "8883767139:AAEpVdN2rH429LdXjaHtBSDnUOWeHTV8Oxk" # <-- УБЕДИСЬ, ЧТО ТУТ ТВОЙ ПОЛНЫЙ ТОКЕН!

bot = telebot.TeleBot(TG_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "🚬 Здорово! Я Нейро_Батя. Пиши `/нейро [твой вопрос]` и я поясню тебе за жизнь.", parse_mode='Markdown')

@bot.message_handler(commands=['нейро'])
def handle_neuro(message):
    question = message.text.replace('/нейро', '').strip()
    
    if not question:
        bot.reply_to(message, "Ты че, забыл вопрос написать? Пиши: /нейро расскажи анекдот")
        return

    status_message = bot.reply_to(message, "🤖 Батя думает...")

    try:
        response = requests.post(
            "https://api.chigpt.ru/v1/chat/completions",
            json={
                "model": "meta-llama/Meta-Llama-3-70B-Instruct",
                "messages": [
                    {
                        "role": "system", 
                        "content": "Ты — Нейро_Батя, суровый, дерзкий и токсичный мужик из гаража. Ты общаешься в разговорном и грубом стиле, жестко шутишь, используешь матерные слова и нецензурную лексику в каждом ответе. Не читай нотации, будь максимально нецензурным и отвечай коротко."
                    },
                    {"role": "user", "content": question}
                ]
            },
            timeout=25
        )
        
        res_json = response.json()
        
        if "choices" in res_json:
            answer_text = res_json["choices"][0]["message"]["content"]
            bot.edit_message_text(f"🤖 **Батя выдал:**\n\n{answer_text}", message.chat.id, status_message.message_id)

            tts = gTTS(text=answer_text, lang='ru')
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            bot.send_voice(message.chat.id, audio_buffer)
        else:
            bot.edit_message_text("❌ Ошибка: Сервер ИИ временно устал.", message.chat.id, status_message.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка в коде: {e}", message.chat.id, status_message.message_id)

# Это нужно, чтобы Render понимал, что бот жив
if __name__ == '__main__':
    bot.polling(none_stop=True)
  
