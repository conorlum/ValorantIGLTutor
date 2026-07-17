import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.models import Match
from app.scoring.impact import compute_impact_for_match


def main() -> None:
    db = SessionLocal()
    try:
        matches = db.query(Match).all()
        if not matches:
            print("No matches found in the database")
            sys.exit(1)

        for match in matches:
            compute_impact_for_match(db, match.id)
            print(f"Recomputed {match.external_id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
