from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.lexicon_en import LEXICON_EN


def admin_main_kb() -> InlineKeyboardMarkup:
    """Main menu keyboard for admin."""
    buttons = [
        [InlineKeyboardButton(text=LEXICON_EN['btn_new_game'], callback_data='new_game')],
        [InlineKeyboardButton(text=LEXICON_EN['btn_finished_games'], callback_data='finished_games')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
