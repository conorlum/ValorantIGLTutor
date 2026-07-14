from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.db import get_db
from app.routers import auth, matches, players
from app.templates import templates

app = FastAPI(title="ValoMaths")
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)
app.mount("/static", StaticFiles(directory=str(Path(__file__).resolve().parent / "static")), name="static")
app.include_router(auth.router)
app.include_router(matches.router)
app.include_router(players.router)


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(request, "landing.html", {})


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
