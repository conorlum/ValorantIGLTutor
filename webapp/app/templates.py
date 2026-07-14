from pathlib import Path

from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.db import SessionLocal
from app.services.auth import get_current_player


def _inject_current_player(request: Request) -> dict:
    db = SessionLocal()
    try:
        return {"current_player": get_current_player(request, db)}
    finally:
        db.close()


templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent / "templates"),
    context_processors=[_inject_current_player],
)
