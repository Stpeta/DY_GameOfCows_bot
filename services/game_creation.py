from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from typing import List

from aiogram.fsm.state import State, StatesGroup

DB_PATH = 'games.db'


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                creator_id INTEGER NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                days_in_game INTEGER NOT NULL DEFAULT 0,
                code TEXT NOT NULL UNIQUE
            )
            """
        )


init_db()


class GameCreation(StatesGroup):
    """States for creating a new game."""

    title = State()
    description = State()


@dataclass
class GameInfo:
    id: int
    title: str
    description: str
    created_at: int
    creator_id: int
    is_active: bool
    days_in_game: int
    code: str


def create_game_record(creator_id: int, title: str, description: str, code: str) -> int:
    """Insert game into DB and return row id."""
    with _get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO games(title, description, created_at, creator_id, is_active, days_in_game, code) "
            "VALUES(?, ?, ?, ?, 1, 0, ?)",
            (title, description, int(time.time()), creator_id, code),
        )
        return cur.lastrowid


def list_admin_games(admin_id: int) -> List[GameInfo]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM games WHERE creator_id=? AND is_active=0 ORDER BY created_at DESC",
            (admin_id,),
        ).fetchall()
    return [GameInfo(**dict(r)) for r in rows]


def get_game_info(game_id: int) -> GameInfo | None:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM games WHERE id=?", (game_id,)).fetchone()
    return GameInfo(**dict(row)) if row else None
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from services.services import generate_code, create_game


async def start_creation(message: Message, state: FSMContext) -> None:
    """Start the game creation dialog."""
    await state.set_state(GameCreation.title)
    await message.answer("Enter game title:")


async def set_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text.strip())
    await state.set_state(GameCreation.description)
    await message.answer("Enter game description:")


async def set_description(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    title = data.get("title")
    description = message.text.strip()
    code = generate_code()
    # save to in-memory game structure
    create_game(message.from_user.id, title, description)
    create_game_record(message.from_user.id, title, description, code)
    await state.clear()
    await message.answer(f"Game '{title}' created with code {code}")
