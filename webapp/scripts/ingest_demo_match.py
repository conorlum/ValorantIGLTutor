import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.adapters.demo_match_source import load_match
from app.db import SessionLocal
from app.models import ImpactScore, MatchPlayer, Player, Round
from app.scoring.impact import compute_impact_for_match


def main(filename: str) -> None:
    db = SessionLocal()
    try:
        match = load_match(db, filename)
        compute_impact_for_match(db, match.id)

        rows = (
            db.query(Player.display_name, ImpactScore.impact)
            .join(MatchPlayer, MatchPlayer.player_id == Player.id)
            .join(ImpactScore, ImpactScore.match_player_id == MatchPlayer.id)
            .join(Round, Round.id == ImpactScore.round_id)
            .filter(Round.match_id == match.id)
            .all()
        )

        totals: dict[str, list[float]] = {}
        for display_name, impact in rows:
            totals.setdefault(display_name, []).append(impact)

        averages = {name: sum(values) / len(values) for name, values in totals.items()}
        for name, avg in sorted(averages.items(), key=lambda item: item[1], reverse=True):
            print(f"{name}: {round(avg)}")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/ingest_demo_match.py <filename>")
        sys.exit(1)
    main(sys.argv[1])
