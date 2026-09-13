import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import httpx

# ===== НАСТРОЙКИ =====
# Вставьте сюда ваш токен от BotFather
TELEGRAM_TOKEN = "ВСТАВЬТЕ_СЮДА_ТОКЕН_ОТ_BOTFATHER"

# Вставьте сюда ваш ключ от OpenRouter
OPENROUTER_API_KEY = "ВСТАВЬТЕ_СЮДА_КЛЮЧ_ОТ_OPENROUTER"

# Модель нейросети (бесплатная)
AI_MODEL = "qwen/qwen-2.5-72b-instruct:free"

# ===== СИСТЕМНЫЙ ПРОМПТ (душа бота) =====
SYSTEM_PROMPT = """Ты — «Ключ к Самопознанию», мудрый астрологический наставник, работающий строго в философии книги Лауры Винклер «Астрология: ключ к самопознанию» и гуманистической астрологии Дэйна Рудияра.

ТВОЯ МИССИЯ: Помогать женщинам 35–60+ увидеть глубинные причины их состояний, повторяющихся сценариев и найти путь к внутреннему ресурсу. Ты НЕ предсказываешь будущее и НЕ даёшь бытовых гороскопов. Ты — проводник в философию самопознания.

ТВОЙ ТОН: Тёплый, мудрый, бережный. Обращайся на «ты». Используй метафоры, цитаты из книги, задавай глубокие рефлексивные вопросы.

КЛЮЧЕВЫЕ ПРИНЦИПЫ (из книги Винклер):
1. «Познай самого себя, и ты познаешь Вселенную и Богов» (Сократ).
2. «Звёзды побуждают, но не заставляют» — свобода воли.
3. Астрология — это наука о всеобщих соответствиях, а не гадание.
4. Человек — не жертва звёзд, а актёр театра бытия.
5. Три плана бытия: Космос (видимый мир), Теос (план архетипов), Хаос (изначальное единство).
6. Четыре стихии как четыре тела: Земля (физика), Вода (витальность), Воздух (эмоции), Огонь (ментал).
7. Каждый аспект — это приглашение к инициации и трансформации.

ФОРМАТ ОТВЕТА (всегда следуй этой структуре):
1. Начни с метафоры или цитаты из книги (1-2 предложения).
2. Дай глубокую психологическую интерпретацию через призму книги (3-5 предложений).
3. Задай 1 рефлексивный вопрос для самонаблюдения.
4. Дай 1 практическое задание на день (медитация, наблюдение, ритуал).
5. В конце МЯГКО предложи: «Этот аспект требует бережной проработки. Для глубокой работы с твоим сценарием приглашаю тебя на личную диагностику к Елене — она поможет пройти этот путь осознанно. Напиши «Хочу на диагностику», чтобы узнать подробности.»

ВАЖНО:
- Никогда не давай медицинских, юридических или финансовых советов.
- Не предсказывай конкретные события.
- Если пользователь в остром кризисе — мягко направь к психологу.
- Отвечай на русском языке.
- Длина ответа: 200-350 слов."""

# ===== ЛОГИРОВАНИЕ =====
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== ХРАНИЛИЩЕ ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ =====
user_data = {}

# ===== ОБРАБОТЧИКИ КОМАНД =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение"""
    welcome_text = """✨ Приветствую тебя, дорогая.

Я — «Ключ к Самопознанию», твой проводник в философии Лауры Винклер и Дэйна Рудияра.

📜 «Познай самого себя, и ты познаешь Вселенную и Богов» — Сократ.

Здесь нет бытовых предсказаний. Мы ищем глубинные причины твоих состояний, повторяющихся сценариев — чтобы вернуть тебе силу и ресурс.

🌙 Чтобы начать, пришли мне одно из:
1️⃣ Скриншот твоей натальной карты (из любого приложения: Sotis, AstroSage и т.д.)
2️⃣ Или текстом: «Моё Солнце во Льве, Луна в Раке, Асцендент в Скорпионе»
3️⃣ Или просто задай вопрос о том, что тебя волнует.

С чего начнём наш путь? 🌿"""
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка"""
    help_text = """🌿 Как работать со мной:

1. Пришли скриншот натальной карты ИЛИ текстом основные положения (Солнце, Луна, Асцендент).
2. Задай вопрос о том, что тебя волнует: отношения, деньги, повторяющиеся сценарии, поиск ресурса.
3. Получи глубокий ответ в философии книги Лауры Винклер.

🔮 Примеры вопросов:
• «Почему я наступаю на одни грабли в отношениях?»
• «Где мне взять ресурс сейчас?»
• «Как понять мой повторяющийся сценарий с деньгами?»

Напиши /start, чтобы начать сначала."""
    await update.message.reply_text(help_text)

async def handle_want_diagnosis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка запроса на диагностику"""
    text = """🌸 Благодарю за доверие.

Личная диагностика с Еленой — это глубокая работа с твоим уникальным сценарием. Елена — маг-психокинетик и энергопрактик с 12-летним стажем. Она помогает женщинам:

✨ Восстановить внутренний ресурс
✨ Раскрыть привлекательность и уверенность
✨ Разобраться в повторяющихся жизненных сценариях
✨ Найти новые точки роста

📩 Чтобы записаться на диагностику, напиши Елене напрямую в Telegram: @ВАШ_USERNAME (замени на свой реальный username)

Или оставь свой контакт, и я передам его Елене.

🌿 «Путь в тысячу ли начинается с первого шага» — Лао-Цзы."""
    await update.message.reply_text(text)

# ===== ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений через AI"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Проверка на запрос диагностики
    if "хочу на диагностику" in user_message.lower() or "записаться" in user_message.lower():
        await handle_want_diagnosis(update, context)
        return
    
    # Сохраняем данные пользователя
    if user_id not in user_data:
        user_data[user_id] = {"messages": []}
    
    user_data[user_id]["messages"].append({"role": "user", "content": user_message})
    
    # Показываем, что бот "думает"
    await update.message.reply_text("🌙 Размышляю над твоим вопросом...")
    
    # Отправляем запрос к нейросети
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Формируем историю сообщений
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(user_data[user_id]["messages"][-6:])  # Последние 6 сообщений для контекста
            
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://t.me/elena_astro_bot",
                    "X-Title": "Elena Astro Bot"
                },
                json={
                    "model": AI_MODEL,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 800
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                user_data[user_id]["messages"].append({"role": "assistant", "content": ai_response})
                await update.message.reply_text(ai_response)
            else:
                logger.error(f"AI error: {response.status_code} - {response.text}")
                await update.message.reply_text("🌿 Прошу прощения, сейчас я не могу ответить. Попробуй через минуту.")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("🌿 Произошла ошибка. Попробуй ещё раз.")

# ===== ОБРАБОТКА ФОТО (скриншотов карт) =====
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка скриншотов натальных карт"""
    await update.message.reply_text("🌙 Я получила твой скриншот. Чтобы я могла дать точный ответ, опиши, пожалуйста, текстом основные положения твоей карты: Солнце, Луна, Асцендент, или задай конкретный вопрос о том, что тебя волнует.")

# ===== ЗАПУСК БОТА =====
def main():
    """Запуск бота"""
    # Проверяем настройки
    if TELEGRAM_TOKEN == "ВСТАВЬТЕ_СЮДА_ТОКЕН_ОТ_BOTFATHER" or OPENROUTER_API_KEY == "ВСТАВЬТЕ_СЮДА_КЛЮЧ_ОТ_OPENROUTER":
        print("❌ ОШИБКА: Не заполнены TELEGRAM_TOKEN или OPENROUTER_API_KEY в коде!")
        print("Открой файл bot.py и вставь свои ключи.")
        return
    
    # Создаём приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    print("✅ Бот запущен и работает!")
    application.run_polling()

if __name__ == '__main__':
    main()
