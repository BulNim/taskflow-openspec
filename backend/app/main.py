from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import CORS_ORIGINS
from .core.db import Base, engine
from .core.errors import register_error_handlers
from .routers import auth, messages, tasks, teams

# 앱 시작 시 테이블이 없으면 생성한다 (로컬 SQLite 편의용).
# 운영(PostgreSQL/Neon)에서도 동일하게 동작하지만, 실제 마이그레이션이 필요해지면
# Alembic 등의 도구로 교체하는 것을 권장한다.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow MVP API")

# 배포된 프론트엔드 도메인만 API를 호출할 수 있도록 허용 목록을 명시한다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 모든 라우터의 예외를 { error: { code, message } } 형태로 표준화.
register_error_handlers(app)

app.include_router(auth.router)
app.include_router(teams.router)
app.include_router(tasks.router)
app.include_router(messages.router)


# Vercel/모니터링에서 서버 생존 여부만 빠르게 확인하기 위한 엔드포인트.
@app.get("/health")
def health():
    return {"status": "ok"}
