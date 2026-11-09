import asyncio
import logging
import requests
import os
from aiogram.types import BufferedInputFile
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from transformers import pipeline
from huggingface_hub import InferenceClient

TOKEN = "9259216256:AAHR2bm9FEV0odlQRi_-DWM1kqa_cEjTttU"
HF_TOKEN = "токен hug" 

logging.basicConfig(level=logging.INFO)
session = AiohttpSession()
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

print("Загрузка модели тональности...")
sentiment_pipeline = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment")
print("Модель загружена!")


hf_client = InferenceClient(token=HF_TOKEN)

img_cache = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я умею:\n1. Анализировать тональность текста (просто напиши что-нибудь).\n2. Генерировать картинки: /imagine кот в космосе")

@dp.message(Command("imagine"))
async def cmd_imagine(message: types.Message):
    prompt = message.text.replace("/imagine", "").strip().lower()
    if not prompt:
        await message.answer("Напиши, что нарисовать. Пример: /imagine кот в космосе")
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")

    
    if prompt in img_cache:
        await message.answer_photo(img_cache[prompt], caption="(Взято из кэша)")
        return

    try:
        
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        response = requests.get(img_url, params={"width": 512, "height": 512, "nologo": "true"}, timeout=60)
        
        if response.status_code == 200:
            img_bytes = response.content
            
            if len(img_bytes) < 5000: 
                raise Exception("Сервер вернул слишком маленький файл.")

            
            with open("temp_image.png", "wb") as f:
                f.write(img_bytes)
                
            img_cache[prompt] = img_bytes
            
     
            from aiogram.types import FSInputFile
            photo = FSInputFile("temp_image.png")
            await message.answer_photo(photo, caption=f"Ваш запрос: {prompt}")
            
        else:
            raise Exception(f"Сервер вернул код {response.status_code}")
            
    except Exception as e:
        await message.answer(f"Ошибка при генерации: {e}")

    return
    
    try:
        result = sentiment_pipeline(text)[0]
        
       
        label_map = {
            "POSITIVE": "😊 Позитивная",
            "NEGATIVE": "😡 Негативная",
            "NEUTRAL": "😐 Нейтральная"
        }
        label = label_map.get(result["label"], result["label"])
        score = round(result["score"] * 100, 1)
        
        await message.answer(f"Тональность: {label}\nУверенность: {score}%")
    except Exception as e:
        await message.answer(f"Ошибка анализа: {e}")

async def main():
    print("Бот (Задание 10) запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())