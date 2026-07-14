from fastapi import Request
from sqlalchemy.orm import Session

from app.models import Player

SESSION_KEY = "player_id"


def get_current_player(request: Request, db: Session) -> Player | None:
    player_id = request.session.get(SESSION_KEY)
    if player_id is None:
        return None
    return db.get(Player, player_id)
