from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def hours_kb() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text=str(i)) for i in range(1, 6)],
        [KeyboardButton(text=str(i)) for i in range(6, 11)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
