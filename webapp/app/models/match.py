import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class MatchSource(str, enum.Enum):
    SCRAPED = "scraped"
    RIOT_API = "riot_api"


class Team(str, enum.Enum):
    TEAM_1 = "team-1"
    TEAM_2 = "team-2"


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    source: Mapped[MatchSource] = mapped_column(Enum(MatchSource), nullable=False)
    map_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    played_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    team1_rounds_won: Mapped[int] = mapped_column(Integer, default=0)
    team2_rounds_won: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    match_players: Mapped[list["MatchPlayer"]] = relationship(
        back_populates="match", cascade="all, delete-orphan"
    )
    rounds: Mapped[list["Round"]] = relationship(
        back_populates="match", cascade="all, delete-orphan"
    )


class MatchPlayer(Base):
    __tablename__ = "match_players"
    __table_args__ = (UniqueConstraint("match_id", "player_id", name="uq_match_player"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    agent: Mapped[str] = mapped_column(String(32), nullable=False)
    team: Mapped[Team] = mapped_column(Enum(Team), nullable=False)

    match: Mapped["Match"] = relationship(back_populates="match_players")
    player: Mapped["Player"] = relationship(back_populates="match_players")
