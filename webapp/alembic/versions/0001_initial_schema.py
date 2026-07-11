"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("puuid", sa.String(length=64), nullable=True),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("puuid", name="uq_players_puuid"),
    )

    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=128), nullable=False),
        sa.Column(
            "source",
            sa.Enum("SCRAPED", "RIOT_API", name="matchsource"),
            nullable=False,
        ),
        sa.Column("map_name", sa.String(length=64), nullable=True),
        sa.Column("played_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("team1_rounds_won", sa.Integer(), nullable=False),
        sa.Column("team2_rounds_won", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("external_id", name="uq_matches_external_id"),
    )

    op.create_table(
        "match_players",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("agent", sa.String(length=32), nullable=False),
        sa.Column("team", sa.Enum("TEAM_1", "TEAM_2", name="team"), nullable=False),
        sa.UniqueConstraint("match_id", "player_id", name="uq_match_player"),
    )

    op.create_table(
        "rounds",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("outcome", sa.String(length=64), nullable=True),
        sa.Column("planted", sa.Boolean(), nullable=False),
        sa.Column("plant_time", sa.Float(), nullable=True),
        sa.Column("exploded", sa.Boolean(), nullable=False),
        sa.Column("defused", sa.Boolean(), nullable=False),
        sa.Column("defuse_time", sa.Float(), nullable=True),
        sa.UniqueConstraint("match_id", "round_number", name="uq_match_round"),
    )

    op.create_table(
        "round_player_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("round_id", sa.Integer(), sa.ForeignKey("rounds.id"), nullable=False),
        sa.Column(
            "match_player_id",
            sa.Integer(),
            sa.ForeignKey("match_players.id"),
            nullable=False,
        ),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("kills", sa.Integer(), nullable=False),
        sa.Column("deaths", sa.Integer(), nullable=False),
        sa.Column("assists", sa.Integer(), nullable=False),
        sa.Column("loadout", sa.Integer(), nullable=False),
        sa.Column("remaining", sa.Integer(), nullable=False),
        sa.UniqueConstraint("round_id", "match_player_id", name="uq_round_match_player"),
    )

    op.create_table(
        "kill_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("round_id", sa.Integer(), sa.ForeignKey("rounds.id"), nullable=False),
        sa.Column(
            "killer_match_player_id",
            sa.Integer(),
            sa.ForeignKey("match_players.id"),
            nullable=True,
        ),
        sa.Column(
            "death_match_player_id",
            sa.Integer(),
            sa.ForeignKey("match_players.id"),
            nullable=True,
        ),
        sa.Column("weapon", sa.String(length=32), nullable=False),
        sa.Column("event_time_seconds", sa.Float(), nullable=False),
        sa.Column("source_meta", sa.JSON(), nullable=True),
    )

    op.create_table(
        "impact_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("round_id", sa.Integer(), sa.ForeignKey("rounds.id"), nullable=False),
        sa.Column(
            "match_player_id",
            sa.Integer(),
            sa.ForeignKey("match_players.id"),
            nullable=False,
        ),
        sa.Column("kill_impact", sa.Float(), nullable=False),
        sa.Column("death_impact", sa.Float(), nullable=False),
        sa.Column("impact", sa.Float(), nullable=False),
        sa.Column("breakdown", sa.JSON(), nullable=True),
        sa.UniqueConstraint(
            "round_id", "match_player_id", name="uq_impact_round_match_player"
        ),
    )


def downgrade() -> None:
    op.drop_table("impact_scores")
    op.drop_table("kill_events")
    op.drop_table("round_player_stats")
    op.drop_table("rounds")
    op.drop_table("match_players")
    op.drop_table("matches")
    op.drop_table("players")
    sa.Enum(name="matchsource").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="team").drop(op.get_bind(), checkfirst=True)
