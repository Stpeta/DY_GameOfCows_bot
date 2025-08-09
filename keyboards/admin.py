from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.lexicon_en import LEXICON_EN


def admin_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LEXICON_EN["new_game_button"], callback_data="new_game"
                )
            ],
            [
                InlineKeyboardButton(
                    text=LEXICON_EN["show_finished_games_button"],
                    callback_data="show_finished_games",
                )
            ],
        ]
    )
