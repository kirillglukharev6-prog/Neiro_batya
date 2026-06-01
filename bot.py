import telebot
import requests
import io
import os
from gtts import gTTS

# Сервер заберет эти токены из вкладки Environment, которую мы заполнили!
TG_TOKEN = os.getenv("TG_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

bot = telebot.TeleBot(TG_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "🚬 Здорово! Я Нейро_Батя. Пиши /нейро [твой вопрос] и я поясню тебе за жизнь.")

@bot.message_handler(commands=['нейро'])
def handle_neuro(message):
    question = message.text.replace('/нейро', '').strip()
    
    if not question:
        bot.reply_to(message, "Ты че, забыл вопрос написать? Пиши: /нейро расскажи анекдот")
        return

    status_message = bot.reply_to(message, "🤖 Батя думает...")

    try:
        # Стучимся на правильный бесплатный сервер GitHub ИИ
        response = requests.post(
            "https://models.inference.ai.azure.com/chat/completions",
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama-3-70b-instruct", 
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
            # Убрали звездочки, чтобы Телеграм не ругался на разметку текста
            bot.edit_message_text(f"🤖 Батя выдал:\n\n{answer_text}", message.chat.id, status_message.message_id)

            tts = gTTS(text=answer_text, lang='ru')
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            bot.send_voice(message.chat.id, audio_buffer)
        else:
            bot.edit_message_text("❌ Ошибка сервера ИИ. Попробуй позже.", message.chat.id, status_message.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка в коде: {e}", message.chat.id, status_message.message_id)

if __name__ == '__main__':
    bot.polling(none_stop=True)
    
