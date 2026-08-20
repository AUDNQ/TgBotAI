from aiogram.types import Message, CallbackQuery
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.utils.chat_action import ChatActionSender
from aiogram.filters import Command
from aiogram.enums import ChatType
from db import user_register, is_user_registered, view_dialogue, add_dialogue, view_ai, add_ai
from chat_engine import get_user_id, get_simple_user_id, process_ai, process_photo, process_file
import os
import keyboards as kb
from loader import bot, client

HELP_TEXT = """
👋 Привет! Мои команды:
!start — старт.
!help — помощь.
!restart — перезапуск.
!choice_ai - поменять ИИ модель.

Можно писать и с /.

👥 В группах и супергруппах: чтобы я ответил, начни сообщение с моего @username, иначе я не увижу его."""

ai = {
    "Gemini 3.7 Flash": "google/gemini-3.7-flash",
    "Qwen3.7 Plus": "qwen/qwen3.7-plus",
    "Claude 3 Haiku": "anthropic/claude-3-haiku"
}

router = Router()

@router.message(Command("start", prefix=["/", "!"]))
async def cmd_start(message: Message):
    user_id = get_simple_user_id(message=message)
    if not user_id:
        return
    answer = await user_register(user_id)
    if answer:
        await message.reply("Вы зарегистрированны напишите команду !help.")
    else:
        await message.reply("Вы уже зарегистрированны.")


@router.message(Command("help", prefix=["/", "!"]))
async def cmd_help(message: Message):
    await message.reply(HELP_TEXT)


@router.message(Command("restart", prefix=["/", "!"]))
async def cmd_restart(message: Message):
    user_id = get_simple_user_id(message=message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        user_dialogue = [{"role": "system", "content": "Привет! Ты ИИ чат-бот Nestra в Telegram. Ты умеешь отвечать на текст и анализировать картинки и файлы, которые тебе присылают. Не используй Markdown-разметку (звёздочки, решётки и т.д.) — она не отображается в Telegram."}]
        await add_dialogue(user_id, user_dialogue)
        await message.reply("История очищена.")
    else:
        await message.reply("Зарегистрируйтесь через !start.")


@router.message(Command("choice_ai", prefix=["/", "!"]))
async def cmd_choice_ai(message: Message):
    user_id = get_simple_user_id(message=message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        await message.reply("Выберите ИИ модель.", reply_markup = kb.choice_ai)
    else:
        await message.reply("Зарегистрируйтесь через !start.")


@router.callback_query(F.data.startswith("Ai_"))
async def chek_ai(callback: CallbackQuery):
    ai_name = callback.data.split("_")[1]
    user_ai = ai.get(ai_name)
    try:
        user_id = get_simple_user_id(callback=callback)
        await callback.answer(f"Вы выбрали {ai_name}!!!")
        answer = await add_ai(user_id, user_ai)
        if answer:
            await callback.message.reply(f"Вы выбрали {ai_name}. Изменение сохранены.")
        else:
            await callback.message.reply(f"Ошибка попробуйте еще раз.")
    except Exception as e:
            print(e)


@router.message(F.text & ~F.text.startswith(("/", "!")))
async def cmd_text(message: Message):
    user_id = await get_user_id(message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        try:
            async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
                user_message = message.text
                name = message.from_user.first_name or message.from_user.username or "Пользователь"
                assistant_reply = await process_ai(client, user_id, user_message, name)
                await message.reply(assistant_reply)
        except Exception as e:
            print(e)
            await message.reply("Ошибка ответа ИИ :(")
    else:
        await message.reply("Зарегистрируйтесь через !start.")


@router.message(F.photo)
async def cmd_photo(message: Message):
    user_id = await get_user_id(message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        caption = message.caption or ""
        name = message.from_user.first_name or message.from_user.username or "Пользователь"
        photo = message.photo[-1]
        file = await bot.download(photo.file_id)
        user_message = process_photo(file, caption)
        async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
            try:
                assistant_reply = await process_ai(client, user_id, user_message, name)
                await message.reply(assistant_reply)
            except Exception as e:
                print(e)
                await message.reply("Ошибка ответа ИИ :(")
    else:
        await message.reply(f"Зарегистрируйтесь через !start.")


@router.message(F.document)
async def cmd_document(message: Message):
    user_id = await get_user_id(message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        caption = message.caption or ""
        file = await bot.download(message.document.file_id)
        file.name = message.document.file_name
        try:
            user_message = process_file(file, caption)
        except Exception as e:
            print(e)
            await message.reply("Ошибка обработки файла =(")
            return
        name = message.from_user.first_name or message.from_user.username or "Пользователь"
        async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
            try:
                assistant_reply = await process_ai(client, user_id, user_message, name)
                await message.reply(assistant_reply)
            except Exception as e:
                print(e)
                await message.reply("Ошибка ответа ИИ :(")
    else:
        await message.reply("Зарегистрируйтесь через !start.")
