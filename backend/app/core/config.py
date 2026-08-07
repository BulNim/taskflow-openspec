import os

# 로컬은 SQLite 파일, 운영은 Neon PostgreSQL 연결 문자열을 환경변수로 주입한다.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./taskflow.db")

# JWT 서명 비밀키. 운영 배포 시 반드시 환경변수로 안전한 값을 설정해야 한다.
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"

# 토큰 만료 시간(시간 단위). 갱신(refresh) 토큰은 발급하지 않는다 - 만료 시 재로그인 필요.
JWT_EXPIRE_HOURS = 24

# 배포된 프론트엔드 도메인만 API 접근을 허용하기 위한 CORS 허용 목록.
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500").split(",") if o.strip()]
