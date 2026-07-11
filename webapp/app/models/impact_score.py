from sqlalchemy import JSON, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class ImpactScore(Base):
    __tablename__ = "impact_scores"
    __table_args__ = (
        UniqueConstraint("round_id", "match_player_id", name="uq_impact_round_match_player"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.id"), nullable=False)
    match_player_id: Mapped[int] = mapped_column(ForeignKey("match_players.id"), nullable=False)
    kill_impact: Mapped[float] = mapped_column(Float, nullable=False)
    death_impact: Mapped[float] = mapped_column(Float, nullable=False)
    impact: Mapped[float] = mapped_column(Float, nullable=False)
    # Mirrors today's ImpactDisplay breakdown: econ/time/swing/damage components.
    breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    round: Mapped["Round"] = relationship()
