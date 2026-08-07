from fastapi import Depends, Header
from sqlalchemy.orm import Session

from .core.db import get_db
from .core.errors import AppError
from .core.security import decode_access_token
from .models import Task, Team, User


# 모든 보호된 라우트가 쓰는 공통 인증 의존성. Authorization 헤더에서
# Bearer 토큰을 꺼내 검증하고, 실패하는 모든 경우(헤더 없음/형식 오류/서명 불일치/
# 만료/유저 삭제됨)를 401 TOKEN_EXPIRED 하나로 통일한다.
def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise AppError(401, "TOKEN_EXPIRED", "인증이 만료되었습니다")
    token = authorization.removeprefix("Bearer ").strip()
    user_id = decode_access_token(token)
    if user_id is None:
        raise AppError(401, "TOKEN_EXPIRED", "인증이 만료되었습니다")
    user = db.get(User, user_id)
    if user is None:
        raise AppError(401, "TOKEN_EXPIRED", "인증이 만료되었습니다")
    return user


# /teams/{team_id}/* 라우트에서 재사용하는 팀 멤버십 검증 의존성.
# 경로의 team_id와 로그인한 사용자의 team_id가 다르면(=팀 소속이 아니면) 403.
def require_team_member(team_id: int, user: User = Depends(get_current_user)) -> User:
    if user.team_id != team_id:
        raise AppError(403, "FORBIDDEN", "이 팀에 접근할 권한이 없습니다")
    return user


# 태스크 삭제/상태변경(PATCH)/수정(PUT)에서 공통으로 쓰는 권한 체크.
# creator(만든 사람) 또는 team owner만 허용하며, 그 외 일반 멤버는 담당자여도 불가
# (explore 단계에서 확정된 결정 - 스토리보드 와이어프레임의 "자유 드래그"보다 좁은 권한).
def require_task_permission(task: Task, team: Team, user: User) -> None:
    is_creator = task.creator_id == user.id
    is_owner = team.owner_id == user.id
    if not (is_creator or is_owner):
        raise AppError(403, "FORBIDDEN", "권한이 없습니다")
