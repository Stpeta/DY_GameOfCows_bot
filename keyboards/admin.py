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


def waiting_players_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LEXICON_EN["start_game_button"], callback_data="start_game"
                ),
                InlineKeyboardButton(
                    text=LEXICON_EN["finish_game_button"], callback_data="finish_game"
                ),
            ]
        ]
    )


def host_game_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LEXICON_EN["start_day_button"], callback_data="start_day"
                ),
                InlineKeyboardButton(
                    text=LEXICON_EN["finish_game_button"], callback_data="finish_game"
                ),
            ]
        ]
    )


def host_day_keyboard(day: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LEXICON_EN["end_day_button"].format(day=day),
                    callback_data="end_day",
                ),
                InlineKeyboardButton(
                    text=LEXICON_EN["finish_game_button"], callback_data="finish_game"
                ),
            ]
        ]
    )
