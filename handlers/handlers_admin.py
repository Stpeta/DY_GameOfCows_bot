from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from config_data.config import load_config
from keyboards.admin import admin_main_kb
from keyboards.player import hours_kb
from lexicon.lexicon_en import LEXICON_EN
from services.game_creation import create_game_db, finished_games_count
from services.services import create_game, start_day, end_day

config = load_config()
admin_router = Router()
admin_router.message.filter(F.from_user.id.in_(config.tg_bot.admin_ids))
admin_router.callback_query.filter(F.from_user.id.in_(config.tg_bot.admin_ids))


@admin_router.message(CommandStart())
async def admin_start(message: Message):
    count = finished_games_count()
    text = LEXICON_EN['admin_menu'].format(count=count)
    await message.answer(text, reply_markup=admin_main_kb())


class NewGame(StatesGroup):
    title = State()
    description = State()


@admin_router.callback_query(F.data == 'new_game')
async def new_game_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(LEXICON_EN['ask_title'])
    await state.set_state(NewGame.title)


@admin_router.message(NewGame.title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(LEXICON_EN['ask_description'])
    await state.set_state(NewGame.description)


@admin_router.message(NewGame.description)
async def process_description(message: Message, state: FSMContext):
    data = await state.get_data()
    title = data['title']
    description = message.text
    db_game = create_game_db(title, description, message.from_user.id)
    create_game(message.from_user.id, title, description, code=db_game.registration_code)
    await message.answer(LEXICON_EN['game_created_code'].format(title=title, code=db_game.registration_code))
    await state.clear()


@admin_router.callback_query(F.data == 'finished_games')
async def show_finished_games(callback: CallbackQuery):
    await callback.answer(LEXICON_EN['feature_not_implemented'], show_alert=True)


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
