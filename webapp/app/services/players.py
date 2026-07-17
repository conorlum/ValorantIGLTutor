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
    """Looks up a player from a "Name#Tag" search box.

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
    average_kill_impact: float
    average_death_impact: float


@dataclass
class PlayerProfile:
    player: Player
    overall_average_impact: float
    matches: list[MatchBreakdown]
    agent_counts: Counter = field(default_factory=Counter)
    avg_econ_kill: float = 0.0
    avg_econ_death: float = 0.0
    avg_clutch_kill: float = 0.0
    avg_clutch_death: float = 0.0
    avg_post_plant_kill: float = 0.0
    avg_post_plant_death: float = 0.0
    avg_traded_teammate: float = 0.0
    avg_traded_by_teammate: float = 0.0
    top_traded_teammate: list[tuple[str, int]] = field(default_factory=list)
    top_traded_by_teammate: list[tuple[str, int]] = field(default_factory=list)


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

    total_econ_kill = 0.0
    total_econ_death = 0.0
    total_clutch_kill = 0.0
    total_clutch_death = 0.0
    total_post_plant_kill = 0.0
    total_post_plant_death = 0.0
    total_traded_teammate = 0
    total_traded_by_teammate = 0
    traded_teammate_totals: dict[str, int] = {}
    traded_by_teammate_totals: dict[str, int] = {}

    for match_player in match_players:
        scores = db.query(ImpactScore).filter_by(match_player_id=match_player.id).all()
        if not scores:
            continue

        impacts = [score.impact for score in scores]
        kill_impacts = [score.kill_impact for score in scores]
        death_impacts = [score.death_impact for score in scores]

        match = db.get(Match, match_player.match_id)
        matches.append(
            MatchBreakdown(
                match=match,
                agent=match_player.agent,
                team=match_player.team.value if hasattr(match_player.team, "value") else match_player.team,
                average_impact=sum(impacts) / len(impacts),
                average_kill_impact=sum(kill_impacts) / len(kill_impacts),
                average_death_impact=sum(death_impacts) / len(death_impacts),
            )
        )
        all_impacts.extend(impacts)
        agent_counts[match_player.agent] += 1

        teammate_names = {
            mp.id: mp.player.display_name
            for mp in db.query(MatchPlayer).filter_by(match_id=match_player.match_id).all()
        }

        for score in scores:
            breakdown = score.breakdown or {}
            total_econ_kill += breakdown.get("econ_kill", 0)
            total_econ_death += breakdown.get("econ_death", 0)
            total_clutch_kill += breakdown.get("clutch_kill", 0)
            total_clutch_death += breakdown.get("clutch_death", 0)
            total_post_plant_kill += breakdown.get("post_plant_kill", 0)
            total_post_plant_death += breakdown.get("post_plant_death", 0)
            total_traded_teammate += breakdown.get("traded_teammate", 0)
            total_traded_by_teammate += breakdown.get("traded_by_teammate", 0)
            for teammate_id, count in breakdown.get("traded_teammate_targets", {}).items():
                name = teammate_names.get(int(teammate_id))
                if name:
                    traded_teammate_totals[name] = traded_teammate_totals.get(name, 0) + count
            for teammate_id, count in breakdown.get("traded_by_teammate_sources", {}).items():
                name = teammate_names.get(int(teammate_id))
                if name:
                    traded_by_teammate_totals[name] = traded_by_teammate_totals.get(name, 0) + count

    overall_average = sum(all_impacts) / len(all_impacts) if all_impacts else 0.0
    matches_played = len(matches)

    def _avg(total: float) -> float:
        return total / matches_played if matches_played else 0.0

    def _top4(totals: dict[str, int]) -> list[tuple[str, int]]:
        return sorted(totals.items(), key=lambda item: item[1], reverse=True)[:4]

    return PlayerProfile(
        player=player,
        overall_average_impact=overall_average,
        matches=matches,
        agent_counts=agent_counts,
        avg_econ_kill=_avg(total_econ_kill),
        avg_econ_death=_avg(total_econ_death),
        avg_clutch_kill=_avg(total_clutch_kill),
        avg_clutch_death=_avg(total_clutch_death),
        avg_post_plant_kill=_avg(total_post_plant_kill),
        avg_post_plant_death=_avg(total_post_plant_death),
        avg_traded_teammate=_avg(total_traded_teammate),
        avg_traded_by_teammate=_avg(total_traded_by_teammate),
        top_traded_teammate=_top4(traded_teammate_totals),
        top_traded_by_teammate=_top4(traded_by_teammate_totals),
    )
