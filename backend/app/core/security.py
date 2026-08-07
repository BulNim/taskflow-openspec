from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from .config import JWT_ALGORITHM, JWT_EXPIRE_HOURS, JWT_SECRET


# 회원가입 시 평문 비밀번호를 bcrypt로 해시하여 저장한다 (평문 저장 금지).
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


# 로그인 시 입력한 비밀번호와 저장된 해시를 비교한다.
def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


# 로그인/회원가입 성공 시 발급하는 JWT. sub에 사용자 id, exp에 24시간 뒤 만료 시각을 담는다.
# 갱신(refresh) 토큰은 없으므로 만료되면 재로그인해야 한다.
def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


# 요청 헤더의 Bearer 토큰을 검증하고 사용자 id를 반환한다. 서명 불일치, 만료,
# 형식 오류 등 모든 실패 케이스는 None으로 통일해 호출부에서 401로 처리하게 한다.
def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None
