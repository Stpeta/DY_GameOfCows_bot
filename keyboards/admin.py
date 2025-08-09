from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def admin_main_kb() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text='/newgame')],
        [KeyboardButton(text='/start_day'), KeyboardButton(text='/end_day')],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
