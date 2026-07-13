from collections import defaultdict

import networkx as nx
from sqlalchemy.orm import Session

from app.models import ImpactScore, KillEvent, MatchPlayer, Round, RoundPlayerStat
from app.models.match import Team

_KILL_ORDER_GRAPH = nx.DiGraph()
_KILL_ORDER_GRAPH.add_weighted_edges_from(
    [
        ("5v5", "4v5", 150),
        ("5v5", "5v4", 150),
        ("4v5", "3v5", 130),
        ("4v5", "4v4", 140),
        ("5v4", "4v4", 140),
        ("5v4", "5v3", 130),
        ("3v5", "2v5", 90),
        ("3v5", "3v4", 120),
        ("4v4", "3v4", 170),
        ("4v4", "4v3", 170),
        ("5v3", "4v3", 120),
        ("5v3", "5v2", 90),
        ("2v5", "1v5", 50),
        ("2v5", "2v4", 70),
        ("3v4", "2v4", 130),
        ("3v4", "3v3", 160),
        ("4v3", "3v3", 160),
        ("4v3", "4v2", 130),
        ("5v2", "4v2", 70),
        ("5v2", "5v1", 50),
        ("1v5", "0v5", 40),
        ("1v5", "1v4", 60),
        ("2v4", "1v4", 80),
        ("2v4", "2v3", 130),
        ("3v3", "2v3", 180),
        ("3v3", "3v2", 180),
        ("4v2", "3v2", 130),
        ("4v2", "4v1", 80),
        ("5v1", "4v1", 60),
        ("5v1", "5v0", 40),
        ("1v4", "0v4", 50),
        ("1v4", "1v3", 70),
        ("2v3", "1v3", 140),
        ("2v3", "2v2", 170),
        ("3v2", "2v2", 170),
        ("3v2", "3v1", 140),
        ("4v1", "3v1", 70),
        ("4v1", "4v0", 50),
        ("1v3", "0v3", 70),
        ("1v3", "1v2", 120),
        ("2v2", "1v2", 200),
        ("2v2", "2v1", 200),
        ("3v1", "2v1", 120),
        ("3v1", "3v0", 70),
        ("1v2", "0v2", 130),
        ("1v2", "1v1", 190),
        ("2v1", "1v1", 190),
        ("2v1", "2v0", 130),
        ("1v1", "0v1", 250),
        ("1v1", "1v0", 250),
    ]
)


def _categorize_econ(loadout: int) -> int:
    if loadout < 1000:
        return 8  # SAVE
    if loadout < 3300:
        return 6  # ECON
    return 4  # FULL BUY


def _kill_order_bonus(team1_kill_index: int, team2_kill_index: int, kill_team: Team, self_kill: bool) -> float:
    before_node = f"{team1_kill_index}v{team2_kill_index}"
    if self_kill:
        if kill_team == Team.TEAM_1:
            team2_kill_index -= 1
        else:
            team1_kill_index -= 1
    else:
        if kill_team == Team.TEAM_1:
            team1_kill_index -= 1
        else:
            team2_kill_index -= 1
    after_node = f"{team1_kill_index}v{team2_kill_index}"

    try:
        return _KILL_ORDER_GRAPH[before_node][after_node]["weight"]
    except KeyError:
        return 100


def _time_factor(round_row: Round, kill_time: float, for_death: bool = False) -> float:
    # Mirrors the original's chronological state machine (planted/plantedTime/
    # exploded/defused flags updated as the event log is walked), reconstructed
    # from the round's final planted/plant_time/exploded/defuse_time. The
    # post-plant window and ramp only apply once a plant has actually happened
    # in this round, and only to kills at or after the plant.
    plant_time = round_row.plant_time if round_row.planted else None

    exploded_effective = round_row.exploded and plant_time is not None and kill_time >= plant_time + 45
    defused_effective = (
        round_row.defused and round_row.defuse_time is not None and kill_time >= round_row.defuse_time
    )
    if exploded_effective or defused_effective:
        return 0.5

    if plant_time is not None and kill_time >= plant_time:
        if plant_time + 38 <= kill_time <= plant_time + 45:
            # A kill in this window is denying/clutching a near-explosion round, so
            # it's highly valuable. A death in this window isn't the mirror-image
            # punishment -- the round is basically already decided in the killer's
            # favor by then -- so it gets the same discount as a death after the
            # round has already been decided (exploded/defused).
            return 0.5 if for_death else 1.75
        return 1 + (kill_time - plant_time) / 53

    return 1


def _traded_factor(round_kills: list[dict], checking_kill: dict, self_kill: bool) -> float:
    if self_kill:
        return 1

    time_to_trade = 10
    killer_id = checking_kill["killer_match_player_id"]
    death_time = checking_kill["event_time_seconds"]

    for kill in round_kills:
        if kill["death_match_player_id"] == killer_id:
            trade_time = kill["event_time_seconds"] - death_time
            if 0 <= trade_time <= time_to_trade:
                return trade_time / time_to_trade

    return 1


def _check_for_resurrection(kill_index: int, round_kills: list[dict]) -> bool:
    match_player_id = round_kills[kill_index]["death_match_player_id"]
    for later_kill in round_kills[kill_index + 1 :]:
        if later_kill["death_match_player_id"] == match_player_id or later_kill["killer_match_player_id"] == match_player_id:
            return True
    return False


def _did_team_win(outcome: str, team: Team) -> bool:
    team_letter = outcome.split("Team ")[1][0]
    return (team_letter == "A" and team == Team.TEAM_1) or (team_letter == "B" and team == Team.TEAM_2)


def _rounds_since_last_win(round_outcomes: dict[int, str], round_number: int, team: Team) -> int:
    loss_streak = 0
    r = round_number - 1
    while r > 0:
        if _did_team_win(round_outcomes[r], team):
            return loss_streak
        loss_streak += 1
        r -= 1
    return loss_streak


def _min_next_round_econ_bonus(round_outcomes: dict[int, str], round_number: int, team: Team) -> int:
    loss_streak = _rounds_since_last_win(round_outcomes, round_number, team)
    if loss_streak == 0:
        return 1900
    if loss_streak == 1:
        return 2400
    return 2900


def _econ_swing_risk_factor(
    round_outcomes: dict[int, str],
    round_player_stats: dict[int, dict[int, dict]],
    match_players: dict[int, MatchPlayer],
    round_number: int,
    team: Team,
) -> float:
    if round_number in (1, 13):
        return 1.5
    if round_number in (12, 24):
        return 1
    if round_number > 24:
        return 1

    loadout_threshold = 3400
    vandal_cost = 2900
    econ_bonus = _min_next_round_econ_bonus(round_outcomes, round_number, team)

    cant_buy_next = 0
    can_buy_next = 0
    can_buy_if_win = 0
    can_buy_double = 0
    can_buy_if_win_double = 0
    need_to_buy_next = 0
    bought_in = 0

    for match_player_id, stat in round_player_stats[round_number].items():
        if match_players[match_player_id].team != team:
            continue

        remaining = stat["remaining"]
        need_to_buy_next += 1 if stat["deaths"] > 0 else 0
        current_loadout = stat["loadout"]

        if remaining + econ_bonus < loadout_threshold:
            cant_buy_next += 1
        if remaining + econ_bonus >= loadout_threshold:
            can_buy_next += 1
        if remaining + 3000 >= loadout_threshold:
            can_buy_if_win += 1
        if remaining + econ_bonus >= loadout_threshold + vandal_cost:
            can_buy_next -= 1
            can_buy_double += 1
        if remaining + 3000 >= loadout_threshold + vandal_cost:
            can_buy_if_win -= 1
            can_buy_if_win_double += 1
        if current_loadout >= loadout_threshold:
            bought_in += 1

    swing_factor = round((bought_in + cant_buy_next - can_buy_double + 3) * 0.01, 2)

    if can_buy_next + 2 * can_buy_double >= 5:
        low_risk = 0.7 - round((can_buy_next + 2 * can_buy_double) * 0.05, 2)
        return round(low_risk + bought_in * swing_factor, 1)

    if round_number in (2, 14):
        swing_factor = 0.15
        return round(1 + (cant_buy_next * swing_factor) + ((need_to_buy_next - can_buy_next) * 0.1), 2)

    if can_buy_next + can_buy_double < 5:
        return round(
            1
            + (0.67 * (bought_in * swing_factor) + (cant_buy_next * swing_factor))
            + ((need_to_buy_next - (can_buy_if_win + 2 * can_buy_if_win_double)) * swing_factor),
            2,
        )

    return 1


def compute_impact_for_match(db: Session, match_id: int) -> None:
    rounds = db.query(Round).filter_by(match_id=match_id).order_by(Round.round_number).all()
    rounds_by_number: dict[int, Round] = {r.round_number: r for r in rounds}
    round_number_by_round_id: dict[int, int] = {r.id: r.round_number for r in rounds}
    round_outcomes: dict[int, str] = {r.round_number: r.outcome for r in rounds}

    match_players: dict[int, MatchPlayer] = {
        mp.id: mp for mp in db.query(MatchPlayer).filter_by(match_id=match_id).all()
    }

    round_player_stats: dict[int, dict[int, dict]] = defaultdict(dict)
    for stat in db.query(RoundPlayerStat).join(Round).filter(Round.match_id == match_id).all():
        round_number = round_number_by_round_id[stat.round_id]
        round_player_stats[round_number][stat.match_player_id] = {
            "score": stat.score,
            "kills": stat.kills,
            "deaths": stat.deaths,
            "assists": stat.assists,
            "loadout": stat.loadout,
            "remaining": stat.remaining,
        }

    round_kills: dict[int, list[dict]] = defaultdict(list)
    for kill in (
        db.query(KillEvent).join(Round).filter(Round.match_id == match_id).order_by(KillEvent.id).all()
    ):
        round_number = round_number_by_round_id[kill.round_id]
        round_kills[round_number].append(
            {
                "killer_match_player_id": kill.killer_match_player_id,
                "death_match_player_id": kill.death_match_player_id,
                "event_time_seconds": kill.event_time_seconds,
                "acs_bonus": (kill.source_meta or {}).get("acs_bonus", 0),
            }
        )

    # Econ-differential factor per kill.
    for round_number, kills in round_kills.items():
        for kill in kills:
            killer_id = kill["killer_match_player_id"]
            death_id = kill["death_match_player_id"]
            self_kill = killer_id == death_id
            killer_econ = round_player_stats[round_number][killer_id]["loadout"]
            death_econ = round_player_stats[round_number][death_id]["loadout"]
            if self_kill:
                kill["econ_differential_factor"] = _categorize_econ(death_econ)
            else:
                kill["econ_differential_factor"] = _categorize_econ(killer_econ) / _categorize_econ(death_econ)

    # Kill-order bonuses, decorated per kill.
    for round_number, kills in round_kills.items():
        round_row = rounds_by_number[round_number]
        team1_kill_index = 5
        team2_kill_index = 5

        team1_swing = _econ_swing_risk_factor(
            round_outcomes, round_player_stats, match_players, round_number, Team.TEAM_1
        )
        team2_swing = _econ_swing_risk_factor(
            round_outcomes, round_player_stats, match_players, round_number, Team.TEAM_2
        )

        for kill_index, kill in enumerate(kills):
            killer_id = kill["killer_match_player_id"]
            death_id = kill["death_match_player_id"]
            self_kill = killer_id == death_id
            killer_team = match_players[killer_id].team

            econ_swing_risk_factor = team1_swing if killer_team == Team.TEAM_2 else team2_swing
            kill_order_bonus = _kill_order_bonus(team1_kill_index, team2_kill_index, killer_team, self_kill)

            kill["kill_order_bonus"] = kill_order_bonus if not self_kill else 0
            kill["kill_order_bonus_x_econ"] = (
                kill_order_bonus * kill["econ_differential_factor"] if not self_kill else 0
            )
            kill["kill_order_bonus_x_time"] = (
                kill_order_bonus * _time_factor(round_row, kill["event_time_seconds"]) if not self_kill else 0
            )
            kill["kill_order_bonus_x_swing"] = kill_order_bonus * econ_swing_risk_factor if not self_kill else 0

            death_order_bonus = kill_order_bonus * _traded_factor(kills, kill, self_kill)
            kill["death_order_bonus"] = death_order_bonus

            if self_kill:
                if kill["econ_differential_factor"] == 4:
                    death_econ_factor = 0.9
                elif kill["econ_differential_factor"] == 6:
                    death_econ_factor = 0.75
                else:
                    death_econ_factor = 0.15
            else:
                death_econ_factor = kill["econ_differential_factor"]

            kill["death_order_bonus_x_econ"] = death_order_bonus * death_econ_factor
            kill["death_order_bonus_x_time"] = death_order_bonus * _time_factor(
                round_row, kill["event_time_seconds"], for_death=True
            )
            kill["death_order_bonus_x_swing"] = death_order_bonus * econ_swing_risk_factor

            resurrection = _check_for_resurrection(kill_index, kills)
            if not resurrection:
                if self_kill:
                    if killer_team == Team.TEAM_1:
                        team2_kill_index -= 1
                    else:
                        team1_kill_index -= 1
                else:
                    if killer_team == Team.TEAM_1:
                        team1_kill_index -= 1
                    else:
                        team2_kill_index -= 1

    # Aggregate per (round, match_player) and write impact_scores.
    for round_number, mp_stats in round_player_stats.items():
        round_row = rounds_by_number[round_number]
        kills = round_kills.get(round_number, [])

        for match_player_id, stat in mp_stats.items():
            acs = stat["score"]
            kill_order_bonus_x_econ_sum = 0.0
            kill_order_bonus_x_time_sum = 0.0
            kill_order_bonus_x_swing_sum = 0.0
            kill_factor_sum = 0.0
            kills_in_round = 0

            for kill in kills:
                if kill["killer_match_player_id"] == match_player_id:
                    acs -= kill["acs_bonus"]
                    kill_factor_sum += kill["econ_differential_factor"]
                    kills_in_round += 1
                    kill_order_bonus_x_econ_sum += kill["kill_order_bonus_x_econ"]
                    kill_order_bonus_x_time_sum += kill["kill_order_bonus_x_time"]
                    kill_order_bonus_x_swing_sum += kill["kill_order_bonus_x_swing"]

            adjust_acs_for_multikill = -50 * kills_in_round if kills_in_round > 1 else 0
            damage_and_assists = acs - adjust_acs_for_multikill
            kill_factor_average = kill_factor_sum / (kills_in_round if kills_in_round else 1)

            death_order_bonus_x_econ_sum = 0.0
            death_order_bonus_x_time_sum = 0.0
            death_order_bonus_x_swing_sum = 0.0
            for kill in kills:
                if kill["death_match_player_id"] == match_player_id:
                    death_order_bonus_x_econ_sum += kill["death_order_bonus_x_econ"]
                    death_order_bonus_x_time_sum += kill["death_order_bonus_x_time"]
                    death_order_bonus_x_swing_sum += kill["death_order_bonus_x_swing"]

            kill_factor = kill_factor_average if kill_factor_average != 0 else 1
            damages = round(damage_and_assists * kill_factor * 1.25)
            kill_impact = round(
                damages
                + (kill_order_bonus_x_econ_sum + kill_order_bonus_x_time_sum + kill_order_bonus_x_swing_sum) / 3
            )
            death_impact = round(
                (death_order_bonus_x_econ_sum + death_order_bonus_x_time_sum + death_order_bonus_x_swing_sum) / 3
            )
            impact = kill_impact - death_impact

            breakdown = {
                "damage": damages,
                "econ_impact": round(kill_order_bonus_x_econ_sum - death_order_bonus_x_econ_sum),
                "time_impact": round(kill_order_bonus_x_time_sum - death_order_bonus_x_time_sum),
                "swing_impact": round(kill_order_bonus_x_swing_sum - death_order_bonus_x_swing_sum),
            }

            impact_score = (
                db.query(ImpactScore)
                .filter_by(round_id=round_row.id, match_player_id=match_player_id)
                .one_or_none()
            )
            if impact_score is None:
                impact_score = ImpactScore(round_id=round_row.id, match_player_id=match_player_id)
                db.add(impact_score)

            impact_score.kill_impact = kill_impact
            impact_score.death_impact = death_impact
            impact_score.impact = impact
            impact_score.breakdown = breakdown

    db.commit()
