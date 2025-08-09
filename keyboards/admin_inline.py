from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def games_list_kb(games) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=g.title, callback_data=f"game_{g.id}")]
               for g in games]
    buttons.append([InlineKeyboardButton(text="New game", callback_data="new_game")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_to_games_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back", callback_data="back_to_games")]
    ])
