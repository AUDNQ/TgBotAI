from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text="!help"),
         KeyboardButton(text="!choice_ai")]
    ],
    resize_keyboard=True
)


choice_ai =  InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Gemini 3.7 Flash", callback_data="Ai_Gemini 3.7 Flash")],
        [InlineKeyboardButton(text="Qwen3.7 Plus", callback_data="Ai_Qwen3.7 Plus")],
        [InlineKeyboardButton(text="Claude 3 Haiku", callback_data="Ai_Claude 3 Haiku")]
    ]
)
