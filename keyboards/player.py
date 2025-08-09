from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def hours_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=str(i), callback_data=f"hours_{i}")]
        for i in range(1, 11)
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

