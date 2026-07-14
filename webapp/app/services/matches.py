from dataclasses import dataclass

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import ImpactScore, KillEvent, Match, MatchPlayer, Player, Round


def list_matches(db: Session) -> list[Match]:
    return db.query(Match).order_by(Match.played_at.desc().nullslast(), Match.id.desc()).all()


def list_matches_for_player(db: Session, player_id: int) -> list[Match]:
    return (
        db.query(Match)
        .join(MatchPlayer, MatchPlayer.match_id == Match.id)
        .filter(MatchPlayer.player_id == player_id)
        .order_by(Match.played_at.desc().nullslast(), Match.id.desc())
        .all()
    )


def get_match_or_404(db: Session, external_id: str) -> Match:
    match = db.query(Match).filter_by(external_id=external_id).one_or_none()
    if match is None:
        raise HTTPException(status_code=404, detail=f"No match '{external_id}'")
    return match


@dataclass
class PlayerSummary:
    match_player_id: int
    display_name: str
    agent: str
    team: str
    average_impact: float
    impact_by_round: dict[int, float]


@dataclass
class MatchSummary:
    players: list[PlayerSummary]
    round_numbers: list[int]
    round_outcomes: dict[int, str | None]


def get_match_summary(db: Session, match: Match) -> MatchSummary:
    rows = (
        db.query(
            MatchPlayer.id,
            Player.display_name,
            MatchPlayer.agent,
            MatchPlayer.team,
            Round.round_number,
            ImpactScore.impact,
        )
        .join(Player, Player.id == MatchPlayer.player_id)
        .join(ImpactScore, ImpactScore.match_player_id == MatchPlayer.id)
        .join(Round, Round.id == ImpactScore.round_id)
        .filter(MatchPlayer.match_id == match.id)
        .order_by(Round.round_number)
        .all()
    )

    by_player: dict[int, PlayerSummary] = {}
    round_numbers: set[int] = set()

    for match_player_id, display_name, agent, team, round_number, impact in rows:
        round_numbers.add(round_number)
        summary = by_player.get(match_player_id)
        if summary is None:
            summary = PlayerSummary(
                match_player_id=match_player_id,
                display_name=display_name,
                agent=agent,
                team=team.value if hasattr(team, "value") else team,
                average_impact=0.0,
                impact_by_round={},
            )
            by_player[match_player_id] = summary
        summary.impact_by_round[round_number] = impact

    for summary in by_player.values():
        values = summary.impact_by_round.values()
        summary.average_impact = sum(values) / len(values) if values else 0.0

    players = sorted(by_player.values(), key=lambda p: p.average_impact, reverse=True)
    round_outcomes = {
        r.round_number: r.outcome
        for r in db.query(Round).filter_by(match_id=match.id).all()
    }
    return MatchSummary(
        players=players,
        round_numbers=sorted(round_numbers),
        round_outcomes=round_outcomes,
    )


@dataclass
class KillLogEntry:
    killer_display_name: str | None
    killer_agent: str | None
    death_display_name: str | None
    death_agent: str | None
    weapon: str
    event_time_seconds: float


@dataclass
class RoundPlayerImpact:
    display_name: str
    agent: str
    team: str
    kill_impact: float
    death_impact: float
    impact: float
    breakdown: dict | None


@dataclass
class RoundDetail:
    round_number: int
    outcome: str | None
    planted: bool
    plant_time: float | None
    exploded: bool
    defused: bool
    defuse_time: float | None
    kills: list[KillLogEntry]
    player_impacts: list[RoundPlayerImpact]


def get_round_detail(db: Session, match: Match, round_number: int) -> RoundDetail:
    round_row = db.query(Round).filter_by(match_id=match.id, round_number=round_number).one_or_none()
    if round_row is None:
        raise HTTPException(status_code=404, detail=f"No round {round_number} for match '{match.external_id}'")

    match_players = {
        mp.id: mp for mp in db.query(MatchPlayer).filter_by(match_id=match.id).all()
    }
    players_by_id = {p.id: p for p in db.query(Player).all()}

    def _display_name(match_player_id: int | None) -> str | None:
        if match_player_id is None:
            return None
        mp = match_players.get(match_player_id)
        return players_by_id[mp.player_id].display_name if mp else None

    def _agent(match_player_id: int | None) -> str | None:
        if match_player_id is None:
            return None
        mp = match_players.get(match_player_id)
        return mp.agent if mp else None

    kill_events = (
        db.query(KillEvent)
        .filter_by(round_id=round_row.id)
        .order_by(KillEvent.event_time_seconds)
        .all()
    )
    kills = [
        KillLogEntry(
            killer_display_name=_display_name(k.killer_match_player_id),
            killer_agent=_agent(k.killer_match_player_id),
            death_display_name=_display_name(k.death_match_player_id),
            death_agent=_agent(k.death_match_player_id),
            weapon=k.weapon,
            event_time_seconds=k.event_time_seconds,
        )
        for k in kill_events
    ]

    impact_scores = db.query(ImpactScore).filter_by(round_id=round_row.id).all()
    player_impacts = []
    for score in impact_scores:
        mp = match_players[score.match_player_id]
        player_impacts.append(
            RoundPlayerImpact(
                display_name=players_by_id[mp.player_id].display_name,
                agent=mp.agent,
                team=mp.team.value if hasattr(mp.team, "value") else mp.team,
                kill_impact=score.kill_impact,
                death_impact=score.death_impact,
                impact=score.impact,
                breakdown=score.breakdown,
            )
        )
    player_impacts.sort(key=lambda p: p.impact, reverse=True)

    return RoundDetail(
        round_number=round_row.round_number,
        outcome=round_row.outcome,
        planted=round_row.planted,
        plant_time=round_row.plant_time,
        exploded=round_row.exploded,
        defused=round_row.defused,
        defuse_time=round_row.defuse_time,
        kills=kills,
        player_impacts=player_impacts,
    )
