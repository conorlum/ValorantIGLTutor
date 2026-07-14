from collections import Counter
from dataclasses import dataclass, field

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import ImpactScore, Match, MatchPlayer, Player, Round


@dataclass
class PlayerListEntry:
    display_name: str
    matches_played: int
    average_impact: float


def list_players(db: Session) -> list[PlayerListEntry]:
    rows = (
        db.query(Player.display_name, MatchPlayer.match_id, ImpactScore.impact)
        .join(MatchPlayer, MatchPlayer.player_id == Player.id)
        .join(ImpactScore, ImpactScore.match_player_id == MatchPlayer.id)
        .all()
    )

    impacts: dict[str, list[float]] = {}
    match_ids: dict[str, set[int]] = {}
    for display_name, match_id, impact in rows:
        impacts.setdefault(display_name, []).append(impact)
        match_ids.setdefault(display_name, set()).add(match_id)

    entries = [
        PlayerListEntry(
            display_name=name,
            matches_played=len(match_ids[name]),
            average_impact=sum(values) / len(values),
        )
        for name, values in impacts.items()
    ]
    entries.sort(key=lambda e: e.average_impact, reverse=True)
    return entries


def get_player_or_404(db: Session, display_name: str) -> Player:
    player = db.query(Player).filter_by(display_name=display_name).one_or_none()
    if player is None:
        raise HTTPException(status_code=404, detail=f"No player '{display_name}'")
    return player


def find_player_by_search_query(db: Session, query: str) -> Player | None:
    """Looks up a player from a tracker.gg-style "Name#Tag" search box.

    The scraped demo data has no real Riot ID tag, so any trailing "#..."
    is stripped before matching -- typing it out of habit still works.
    """
    name = query.split("#", 1)[0].strip()
    if not name:
        return None
    return db.query(Player).filter(Player.display_name.ilike(name)).one_or_none()


@dataclass
class MatchBreakdown:
    match: Match
    agent: str
    team: str
    average_impact: float


@dataclass
class PlayerProfile:
    player: Player
    overall_average_impact: float
    matches: list[MatchBreakdown]
    agent_counts: Counter = field(default_factory=Counter)


def get_player_profile(db: Session, player: Player) -> PlayerProfile:
    match_players = (
        db.query(MatchPlayer)
        .filter_by(player_id=player.id)
        .join(Match, Match.id == MatchPlayer.match_id)
        .order_by(Match.played_at.nullslast(), Match.id)
        .all()
    )

    matches: list[MatchBreakdown] = []
    all_impacts: list[float] = []
    agent_counts: Counter = Counter()

    for match_player in match_players:
        impacts = [
            score.impact
            for score in db.query(ImpactScore).filter_by(match_player_id=match_player.id).all()
        ]
        if not impacts:
            continue

        match = db.get(Match, match_player.match_id)
        matches.append(
            MatchBreakdown(
                match=match,
                agent=match_player.agent,
                team=match_player.team.value if hasattr(match_player.team, "value") else match_player.team,
                average_impact=sum(impacts) / len(impacts),
            )
        )
        all_impacts.extend(impacts)
        agent_counts[match_player.agent] += 1

    overall_average = sum(all_impacts) / len(all_impacts) if all_impacts else 0.0

    return PlayerProfile(
        player=player,
        overall_average_impact=overall_average,
        matches=matches,
        agent_counts=agent_counts,
    )
