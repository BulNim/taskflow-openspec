from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL

# SQLite는 기본적으로 단일 스레드만 허용하므로, FastAPI의 스레드 기반 처리와
# 함께 쓰려면 check_same_thread=False가 필요하다. PostgreSQL(운영)에는 불필요.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# FastAPI 의존성 - 요청마다 새 DB 세션을 열고, 요청이 끝나면 반드시 닫는다.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
