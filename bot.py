import logging
import random
import json
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# =============================================
# НАСТРОЙКИ
# =============================================
BOT_TOKEN = "8886532892:AAEKc4wjqvESk4WE-3lafn4W_3nj5e5dgI8"
ADMIN_ID = 698479126  # твой Telegram ID — сюда приходит статистика

# =============================================
# ЗАДАНИЯ — просто добавляй новые строки сюда!
# =============================================
TASKS = "Сделать двум людям комплимент не внешности, а силуэту: «У тебя сегодня очень убедительный силуэт». Больше ничего не объяснять.",
  "В момент тишины или паузы один раз спокойно сказать: «Пауза принята». Затем продолжить как ни в чем не бывало.",
  "Взять салфетку, посмотреть на нее как на договор, поставить невидимую печать пальцем и сказать: «Согласовано».",
  "Два раза, проходя через дверь или арку, тихо сказать: «Граница пройдена». Можно слегка кивнуть пространству.",
  "Один раз спросить у человека рядом: «Кто назначил этот стул главным?» После любого ответа сказать: «Вопрос снят».",
  "Один раз сделать короткий тост за обычный объект в лофте: лед, колонку, дверь или стол. Максимум 15 секунд.",
  "Когда кто-то рядом берет еду или напиток, два раза тихо сказать: «Сделка состоялась». Если посмотрят странно, просто поздравить.",
  "Пять раз поправить невидимый галстук или бейдж на себе, даже если их нет. Делать уверенно и очень по-деловому.",
  "Один раз во время общего смеха поднять палец, дождаться внимания и сказать только: «Я все». Потом опустить руку.",
  "Три раза за вечер назвать обычные действия «элегантными»: кто-то пьет, садится или поправляет рукав. Говорить с чрезмерным уважением.",
  "Два раза подойти к любому предмету на столе, повернуть его на пару градусов и сказать: «Так честнее».",
  "Два раза спросить у человека рядом: «Ты не видел тут маленького директора вечера?» После ответа сказать: «Опять убежал».",
  "Три раза, когда кто-то говорит «короче», сделать вид, что ты перезагрузился: замереть на 2 секунды и вернуться в разговор.",
  "Один раз подойти к имениннице и сказать максимально официально: «Ваш вклад в атмосферу вечера невозможно переоценить».",
  "Два раза попросить человека рядом оценить, насколько его бокал выглядит «как главный герой». После ответа сказать: «Согласен, кастинг сильный».",
  "Два раза, уходя из комнаты или зоны, обернуться и тихо сказать пространству: «Держись».",
  "Три раза посмотреть на свой напиток как на сложный инвестиционный актив и сказать: «Пока держим».",
  "Один раз найти крошечный участок пола и объявить: «Этот танцпол открыт только для мыслей». Сделать там один серьезный танцевальный жест.",
  "Два раза, когда рядом кто-то начинает рассказывать историю, на 2 секунды поднести к нему невидимый микрофон, будто берешь интервью, и молча убрать.",
  "Два раза пройти мимо группы людей с видом экскурсовода и сказать: «Слева у нас люди, которые делают вид, что все под контролем».",
  "Три раза, когда кто-то снимает фото или видео, оказаться сбоку или на заднем плане и поднять невидимую табличку, будто что-то продаешь.",
  "Один раз попросить двух людей одновременно сказать «мы не подставные». После этого кивнуть и сказать: «Именно так они и говорят».",
  "Три раза на вопрос «как дела?» отвечать: «Меня красиво занесло». Потом сразу продолжать обычный разговор.",
  "Три раза попросить человека выбрать режим твоего следующего шага: «деловой», «испуганный» или «премиальный». Сделать 3-4 шага в выбранном режиме.",
  "Два раза, если кто-то спрашивает «где это?» или «куда?», уверенно показать не в ту сторону и сразу придумать любую короткую фразу-объяснение.",
  "Два раза открыть камеру телефона, поводить ею по комнате 3 секунды и сказать: «Кринж найден, но он дружелюбный». Ничего не снимать.",
  "Три раза посмотреть на стену, колонну или лампу так, будто она сказала шутку, и коротко кивнуть.",
  "Два раза попросить человека на секунду замереть, будто ты фотографируешь его глазами. Моргнуть и сказать: «Готово, без вспышки».",
  "Три раза в разговоре заменить «не знаю» на «мне не выдали этот DLC». Произносить так, будто это обычная бытовая фраза.",
  "Три раза, когда меняется музыка, свет или движуха рядом, сказать: «Новая серия началась». Сделать лицо человека из трейлера."
]

# =============================================
# СОСТОЯНИЯ ДИАЛОГА (теперь только 2 шага)
# =============================================
WAITING_FULLNAME, PLAYING = range(2)

# =============================================
# ФАЙЛ ДЛЯ ХРАНЕНИЯ ДАННЫХ ИГРОКОВ
# =============================================
DATA_FILE = "players.json"

def load_players():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_players(players):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

# =============================================
# КОМАНДА /start
# =============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    players = load_players()

    if user_id in players:
        del players[user_id]
        save_players(players)

    await update.message.reply_text(
        "👋 Привет! Добро пожаловать в игру!\n\n"
        "Для начала давай познакомимся.\n"
        "Напиши своё *имя и фамилию* одним сообщением\n"
        "_(например: Анна Иванова)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return WAITING_FULLNAME

# =============================================
# ПОЛУЧАЕМ ИМЯ И ФАМИЛИЮ ВМЕСТЕ
# =============================================
async def get_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    full_name = update.message.text.strip()

    # Проверяем что написано хотя бы два слова
    parts = full_name.split()
    if len(parts) < 2:
        await update.message.reply_text(
            "Пожалуйста, напиши *имя и фамилию* вместе\n"
            "_(например: Анна Иванова)_ 😊",
            parse_mode="Markdown"
        )
        return WAITING_FULLNAME

    # Сохраняем игрока
    user_id = str(update.effective_user.id)
    players = load_players()
    players[user_id] = {
        "full_name": full_name,
        "task": None,
        "swap_used": False,
        "status": "registered"
    }
    save_players(players)

    # Уведомляем админа о новом игроке
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📝 Новый игрок зарегистрировался: *{full_name}*",
        parse_mode="Markdown"
    )

    # Показываем правила
    rules_text = (
        f"✅ Отлично, *{full_name}*!\n\n"
        "📋 *Правила игры:*\n\n"
        "Ты должен(а) выполнить действие, которое сейчас появится на экране. "
        "На выполнение у тебя есть целый вечер.\n\n"
        "⚠️ *Важное правило:* при выполнении ты не можешь говорить, "
        "что это задание — и после игры тоже.\n\n"
        "Удачи! 🍀"
    )

    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("✅ Я готов(а)!")]],
        resize_keyboard=True
    )

    await update.message.reply_text(rules_text, parse_mode="Markdown", reply_markup=keyboard)
    return PLAYING

# =============================================
# НАЖАЛ "Я ГОТОВ" → ВЫДАЁМ ЗАДАНИЕ
# =============================================
async def give_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    players = load_players()

    if user_id not in players:
        await update.message.reply_text("Напиши /start чтобы начать игру.")
        return ConversationHandler.END

    player = players[user_id]

    task = random.choice(TASKS)
    player["task"] = task
    player["status"] = "has_task"
    player["swap_used"] = False
    save_players(players)

    # Уведомляем админа что игрок получил задание
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🎯 *{player['full_name']}* получил(а) задание:\n"
            f"_{task}_"
        ),
        parse_mode="Markdown"
    )

    keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("✅ Выполнил(а)!")],
            [KeyboardButton("🔄 Поменять задание (1 раз)")],
        ],
        resize_keyboard=True
    )

    await update.message.reply_text(
        f"🎯 *Твоё задание:*\n\n_{task}_",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    return PLAYING

# =============================================
# ВЫПОЛНИЛ ЗАДАНИЕ
# =============================================
async def task_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    players = load_players()

    if user_id not in players or not players[user_id].get("task"):
        await update.message.reply_text("Сначала получи задание! Нажми /start")
        return ConversationHandler.END

    player = players[user_id]
    full_name = player["full_name"]
    task = player["task"]

    player["status"] = "done"
    save_players(players)

    # Уведомление тебе (админу)
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"✅ *{full_name}* выполнил(а) задание!\n\n"
            f"📌 Задание было: _{task}_"
        ),
        parse_mode="Markdown"
    )

    await update.message.reply_text(
        "🎉 *Отлично! Ты выполнил(а) задание!*\n\n"
        "Ты молодец! 🏆 Надеемся, вечер был крутым 😄",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# =============================================
# ПОМЕНЯТЬ ЗАДАНИЕ (1 РАЗ)
# =============================================
async def swap_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    players = load_players()

    if user_id not in players:
        await update.message.reply_text("Напиши /start чтобы начать игру.")
        return ConversationHandler.END

    player = players[user_id]

    if player.get("swap_used"):
        await update.message.reply_text(
            "❌ Ты уже использовал(а) замену задания. "
            "Придётся выполнить текущее! 💪"
        )
        return PLAYING

    old_task = player["task"]
    new_task = random.choice([t for t in TASKS if t != old_task])
    player["task"] = new_task
    player["swap_used"] = True
    save_players(players)

    # Уведомляем админа о замене
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🔄 *{player['full_name']}* поменял(а) задание\n"
            f"Было: _{old_task}_\n"
            f"Стало: _{new_task}_"
        ),
        parse_mode="Markdown"
    )

    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("✅ Выполнил(а)!")]],
        resize_keyboard=True
    )

    await update.message.reply_text(
        f"🔄 Задание заменено! Больше замен нет.\n\n"
        f"🎯 *Новое задание:*\n\n_{new_task}_",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    return PLAYING

# =============================================
# НЕИЗВЕСТНОЕ СООБЩЕНИЕ
# =============================================
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Используй кнопки ниже или напиши /start чтобы начать заново 😊"
    )

# =============================================
# ЗАПУСК БОТА
# =============================================
def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_FULLNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fullname)],
            PLAYING: [
                MessageHandler(filters.Regex("^✅ Я готов"), give_task),
                MessageHandler(filters.Regex("^✅ Выполнил"), task_done),
                MessageHandler(filters.Regex("^🔄 Поменять"), swap_task),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT, unknown))

    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
