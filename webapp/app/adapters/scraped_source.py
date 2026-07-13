import re
import sys
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import ImpactScore, KillEvent, Match, MatchPlayer, Player, Round, RoundPlayerStat
from app.models.match import MatchSource, Team

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import trackerScraper  # noqa: E402

_MAP_NAME_RE = re.compile(r"^[A-Za-z]+")


def _map_name(filename: str) -> str | None:
    match = _MAP_NAME_RE.match(filename)
    return match.group(0) if match else None


def _team_from_outcome_letter(letter: str) -> Team:
    return Team.TEAM_1 if letter == "A" else Team.TEAM_2


def _get_or_create_player(db: Session, display_name: str) -> Player:
    player = db.query(Player).filter_by(display_name=display_name).one_or_none()
    if player is None:
        player = Player(display_name=display_name)
        db.add(player)
        db.flush()
    return player


def load_match(db: Session, filename: str) -> Match:
    existing = db.query(Match).filter_by(external_id=filename).one_or_none()
    if existing is not None:
        # RoundPlayerStat/KillEvent/ImpactScore reference match_players by raw FK
        # (no ORM relationship), so cascading through Match's relationships alone
        # picks an unsafe delete order. Delete children explicitly, FK-safe order.
        round_ids = [r.id for r in db.query(Round.id).filter_by(match_id=existing.id).all()]
        if round_ids:
            db.query(ImpactScore).filter(ImpactScore.round_id.in_(round_ids)).delete(synchronize_session=False)
            db.query(KillEvent).filter(KillEvent.round_id.in_(round_ids)).delete(synchronize_session=False)
            db.query(RoundPlayerStat).filter(RoundPlayerStat.round_id.in_(round_ids)).delete(synchronize_session=False)
        db.query(Round).filter_by(match_id=existing.id).delete(synchronize_session=False)
        db.query(MatchPlayer).filter_by(match_id=existing.id).delete(synchronize_session=False)
        db.delete(existing)
        db.flush()

    round_outcomes = trackerScraper.parseRoundOutcome(filename)
    round_kill_logs = trackerScraper.parseRoundKillList(filename)
    players_round_info = trackerScraper.parsePlayerRoundInfo(filename)
    agent_team_to_username = trackerScraper.reverseAgentTeamToPlayerUsername(players_round_info)

    team1_wins = sum(1 for outcome in round_outcomes.values() if outcome.startswith("Team A"))
    team2_wins = sum(1 for outcome in round_outcomes.values() if outcome.startswith("Team B"))

    match = Match(
        external_id=filename,
        source=MatchSource.SCRAPED,
        map_name=_map_name(filename),
        played_at=None,
        team1_rounds_won=team1_wins,
        team2_rounds_won=team2_wins,
    )
    db.add(match)
    db.flush()

    match_players: dict[str, MatchPlayer] = {}
    for username, info in players_round_info.items():
        player = _get_or_create_player(db, username)
        match_player = MatchPlayer(
            match_id=match.id,
            player_id=player.id,
            agent=info["Agent"],
            team=Team(info["Team"]),
        )
        db.add(match_player)
        match_players[username] = match_player
    db.flush()

    round_count = len(next(iter(players_round_info.values()))["RoundInfo"])

    for i in range(round_count):
        round_number = i + 1
        round_index_str = str(round_number)
        events = round_kill_logs[round_index_str]

        planted = False
        plant_time = None
        exploded = False
        defused = False
        defuse_time = None
        for event in events:
            if event["Event"] == "Planted":
                planted = True
                plant_time = event["eventTime"]
            elif event["Event"] == "Exploded":
                exploded = True
            elif event["Event"] == "Defused":
                defused = True
                defuse_time = event["eventTime"]

        db_round = Round(
            match_id=match.id,
            round_number=round_number,
            outcome=round_outcomes.get(round_index_str),
            planted=planted,
            plant_time=plant_time,
            exploded=exploded,
            defused=defused,
            defuse_time=defuse_time,
        )
        db.add(db_round)
        db.flush()

        for username, match_player in match_players.items():
            round_info = players_round_info[username]["RoundInfo"][i]
            db.add(
                RoundPlayerStat(
                    round_id=db_round.id,
                    match_player_id=match_player.id,
                    score=round_info["Score"],
                    kills=round_info["Kills"],
                    deaths=round_info["Deaths"],
                    assists=round_info["Assists"],
                    loadout=round_info["Loadout"],
                    remaining=round_info["Remaining"],
                )
            )

        for event in events:
            if event["Event"] != "Kill":
                continue

            killer_username = agent_team_to_username.get(event["killerTeam"] + event["killerCharacter"])
            death_username = agent_team_to_username.get(event["deathTeam"] + event["deathCharacter"])

            db.add(
                KillEvent(
                    round_id=db_round.id,
                    killer_match_player_id=match_players[killer_username].id if killer_username else None,
                    death_match_player_id=match_players[death_username].id if death_username else None,
                    weapon=event["killWeapon"],
                    event_time_seconds=event["eventTime"],
                    source_meta={"acs_bonus": event["ACS_Bonus"]},
                )
            )

    db.commit()
    return match
