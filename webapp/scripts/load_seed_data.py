import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import engine

_SEED_FILE = Path(__file__).resolve().parents[1] / "seed_data" / "demo_matches.sql"


def main() -> None:
    sql = _SEED_FILE.read_text(encoding="utf-8-sig")
    with engine.begin() as conn:
        conn.exec_driver_sql(sql)
    print(f"Loaded seed data from {_SEED_FILE.name}")


if __name__ == "__main__":
    main()
