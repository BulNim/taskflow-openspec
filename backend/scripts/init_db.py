"""로컬 SQLite DB 초기화 스크립트. `python scripts/init_db.py`로 실행."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.db import Base, engine  # noqa: E402
from app import models  # noqa: F401,E402


def main():
    # 이미 존재하는 테이블은 건드리지 않고, 없는 테이블만 생성한다.
    Base.metadata.create_all(bind=engine)
    print("DB 초기화 완료:", engine.url)


if __name__ == "__main__":
    main()
