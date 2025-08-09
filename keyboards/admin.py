from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.lexicon_en import LEXICON_EN


def admin_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LEXICON_EN["new_course_button"], callback_data="new_course"
                )
            ],
            [
                InlineKeyboardButton(
                    text=LEXICON_EN["show_finished_courses_button"],
                    callback_data="show_finished_courses",
                )
            ],
        ]
    )
