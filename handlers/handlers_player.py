from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from config_data.config import load_config
from lexicon.lexicon_en import LEXICON_EN
from keyboards.player import hours_kb
from services.services import join_game, get_game_by_player, submit_hours

config = load_config()
player_router = Router()
player_router.message.filter(~F.from_user.id.in_(config.tg_bot.admin_ids))


@player_router.message(CommandStart())
async def player_start(message: Message):
    await message.answer(LEXICON_EN['/start_player'])


@player_router.message(Command('join'))
async def join_game_cmd(message: Message):
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer('Usage: /join <code> <real_name> <nickname>')
        return
    _, code, real_name, nickname = parts
    player = join_game(code, message.from_user.id, real_name, nickname)
    if not player:
        await message.answer(LEXICON_EN['unknown_code'])
        return
    await message.answer(LEXICON_EN['join_success'].format(title=get_game_by_player(message.from_user.id).title,
                                                           nickname=nickname))


@player_router.message(F.text.in_({str(i) for i in range(1, 11)}))
async def receive_hours(message: Message):
    game = get_game_by_player(message.from_user.id)
    if not game or message.from_user.id not in game.awaiting_moves:
        await message.answer(LEXICON_EN['not_in_game'])
        return
    hours = int(message.text)
    submit_hours(game.code, message.from_user.id, hours)
    await message.answer(LEXICON_EN['wait_others'])
