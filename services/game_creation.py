import random
import string

from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import GameModel


def generate_registration_code(length: int = 8) -> str:
    """Generate a random registration code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def create_game_db(title: str, description: str, host_id: int) -> GameModel:
    """Create a game in database and return model instance."""
    code = generate_registration_code()
    with SessionLocal() as session:
        game = GameModel(
            title=title,
            description=description,
            host_telegram_id=host_id,
            registration_code=code,
            is_active=True,
        )
        session.add(game)
        session.commit()
        session.refresh(game)
        return game


def finished_games_count() -> int:
    with SessionLocal() as session:
        return session.query(GameModel).filter_by(is_active=False).count()
