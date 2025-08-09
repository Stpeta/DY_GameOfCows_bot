from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from config_data.config import load_config
from keyboards.admin import admin_main_kb
from keyboards.player import hours_kb
from lexicon.lexicon_en import LEXICON_EN
from services.services import create_game, list_games, start_day, end_day

config = load_config()
admin_router = Router()
admin_router.message.filter(F.from_user.id.in_(config.tg_bot.admin_ids))


@admin_router.message(CommandStart())
async def admin_start(message: Message):
    games = list_games()
    text = LEXICON_EN['/start_admin']
    if games:
        text += '\n\n' + '\n'.join(f"{g.title} ({g.code})" for g in games)
    await message.answer(text, reply_markup=admin_main_kb())


@admin_router.message(Command('newgame'))
async def process_newgame(message: Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer('Usage: /newgame <title> <description>')
        return
    _, title, description = parts
    game = create_game(message.from_user.id, title, description)
    await message.answer(LEXICON_EN['game_created'].format(title=title, code=game.code))


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
