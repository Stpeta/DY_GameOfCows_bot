from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config_data.config import load_config
from keyboards.admin_inline import games_list_kb, back_to_games_kb
from keyboards.player import hours_kb
from lexicon.lexicon_en import LEXICON_EN
from services.services import start_day, end_day
from services.game_creation import (
    GameCreation,
    list_admin_games,
    get_game_info,
    start_creation,
    set_title,
    set_description,
)

config = load_config()
admin_router = Router()
admin_router.message.filter(F.from_user.id.in_(config.tg_bot.admin_ids))


@admin_router.message(CommandStart())
async def admin_start(message: Message):
    games = list_admin_games(message.from_user.id)
    text = LEXICON_EN['/start_admin']
    await message.answer(text, reply_markup=games_list_kb(games))


@admin_router.callback_query(F.data == 'new_game')
async def cb_new_game(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await start_creation(callback.message, state)


@admin_router.callback_query(F.data.startswith('game_'))
async def cb_show_game(callback: CallbackQuery):
    game_id = int(callback.data.split('_')[1])
    game = get_game_info(game_id)
    if not game:
        await callback.answer('Game not found', show_alert=True)
        return
    text = f"{game.title}\n{game.description}\nDays played: {game.days_in_game}"
    await callback.message.edit_text(text, reply_markup=back_to_games_kb())
    await callback.answer()


@admin_router.callback_query(F.data == 'back_to_games')
async def cb_back(callback: CallbackQuery):
    games = list_admin_games(callback.from_user.id)
    await callback.message.edit_text(LEXICON_EN['/start_admin'], reply_markup=games_list_kb(games))
    await callback.answer()


@admin_router.message(GameCreation.title)
async def process_title(message: Message, state: FSMContext):
    await set_title(message, state)


@admin_router.message(GameCreation.description)
async def process_description(message: Message, state: FSMContext):
    await set_description(message, state)
@admin_router.message(Command('start_day'))
async def process_start_day(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer('Usage: /start_day <code>')
        return
    code = parts[1].strip()
    day = start_day(code)
    if not day:
        await message.answer(LEXICON_EN['unknown_code'])
        return
    from services.services import GAMES
    game = GAMES[code]
    for pid in game.players:
        await message.bot.send_message(pid, LEXICON_EN['day_prompt'].format(day=day),
                                       reply_markup=hours_kb())
    await message.answer(f'Day {day} started for game {code}')


@admin_router.message(Command('end_day'))
async def process_end_day(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer('Usage: /end_day <code>')
        return
    code = parts[1].strip()
    result = end_day(code)
    if not result:
        await message.answer(LEXICON_EN['unknown_code'])
        return
    from services.services import GAMES
    game = GAMES[code]
    table_lines = [
        f"{game.players[pid].nickname}: {info['hours']}h -> {info['coins']:.1f} coins"
        for pid, info in result['results'].items()
    ]
    table = '\n'.join(table_lines)
    for pid in result['results'].keys():
        await message.bot.send_message(
            pid,
            LEXICON_EN['day_result'].format(
                day=game.current_day,
                level=result['field_level'],
                table=table
            )
        )
    await message.answer(f"Day {game.current_day} ended. Field level: {result['field_level']:.1f}")
