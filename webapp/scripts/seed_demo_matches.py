import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.adapters.scraped_source import load_match
from app.db import SessionLocal
from app.scoring.impact import compute_impact_for_match

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TRACKER_JSONS_DIR = _REPO_ROOT / "TrackerHTMLJsons"


def main() -> None:
    filenames = sorted(p.stem for p in _TRACKER_JSONS_DIR.glob("*.json"))
    if not filenames:
        print(f"No match JSONs found under {_TRACKER_JSONS_DIR}")
        sys.exit(1)

    db = SessionLocal()
    try:
        for filename in filenames:
            match = load_match(db, filename)
            compute_impact_for_match(db, match.id)
            print(f"Seeded {filename}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
