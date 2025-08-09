from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random
import string
import time

# ---------- Data models ----------


@dataclass
class Player:
    tg_id: int
    real_name: str
    nickname: str
    coins: float = 0.0
    total_hours: int = 0
    moves: List[int] = field(default_factory=list)

    @property
    def average_hours(self) -> float:
        if not self.moves:
            return 0.0
        return self.total_hours / len(self.moves)


@dataclass
class Game:
    code: str
    title: str
    description: str
    decay: float
    recovery: float
    host_id: int
    field_level: float = 100.0
    created_at: float = field(default_factory=time.time)
    players: Dict[int, Player] = field(default_factory=dict)
    current_day: int = 0
    awaiting_moves: Dict[int, Optional[int]] = field(default_factory=dict)


# In-memory storage for games
GAMES: Dict[str, Game] = {}


# ---------- Utility functions ----------

def generate_code() -> str:
    """Generate a unique 8 digit code for a game."""
    while True:
        code = ''.join(random.choices(string.digits, k=8))
        if code not in GAMES:
            return code


def list_games() -> List[Game]:
    return list(GAMES.values())


def create_game(host_id: int, title: str, description: str,
                decay: float = 2.0, recovery: float = 1.0,
                code: str | None = None) -> Game:
    if code is None:
        code = generate_code()
    game = Game(code=code,
                title=title,
                description=description,
                decay=decay,
                recovery=recovery,
                host_id=host_id)
    GAMES[code] = game
    return game


def join_game(code: str, tg_id: int, real_name: str, nickname: str) -> Optional[Player]:
    game = GAMES.get(code)
    if not game:
        return None
    if tg_id in game.players:
        return game.players[tg_id]
    player = Player(tg_id=tg_id, real_name=real_name, nickname=nickname)
    game.players[tg_id] = player
    return player


def get_game_by_player(tg_id: int) -> Optional[Game]:
    for game in GAMES.values():
        if tg_id in game.players:
            return game
    return None


def start_day(code: str) -> Optional[int]:
    game = GAMES.get(code)
    if not game:
        return None
    game.current_day += 1
    game.awaiting_moves = {pid: None for pid in game.players.keys()}
    return game.current_day


def submit_hours(code: str, player_id: int, hours: int) -> bool:
    game = GAMES.get(code)
    if not game or player_id not in game.awaiting_moves:
        return False
    game.awaiting_moves[player_id] = hours
    return True


def end_day(code: str):
    game = GAMES.get(code)
    if not game:
        return None
    if not game.awaiting_moves:
        return None
    total_hours = sum(h for h in game.awaiting_moves.values() if h is not None)
    num_players = len(game.awaiting_moves)
    avg_hours = total_hours / num_players if num_players else 0
    if avg_hours > 5:
        game.field_level = max(0.0, game.field_level - (avg_hours - 5) * game.decay)
    elif avg_hours < 5:
        game.field_level = min(100.0, game.field_level + (5 - avg_hours) * game.recovery)
    results = {}
    for pid, hours in game.awaiting_moves.items():
        if hours is None:
            continue
        player = game.players[pid]
        coins = hours * game.field_level
        player.coins += coins
        player.total_hours += hours
        player.moves.append(hours)
        results[pid] = {"hours": hours, "coins": coins}
    game.awaiting_moves = {}
    return {"results": results, "field_level": game.field_level, "avg_hours": avg_hours}


def finish_game(code: str) -> Optional[Game]:
    return GAMES.pop(code, None)
