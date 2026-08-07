from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.errors import AppError
from ..deps import get_current_user, require_team_member
from ..models import Message, User
from ..schemas import MessageCreateRequest, MessageOut

router = APIRouter(tags=["messages"])


# Message 모델 → 응답 스키마 변환. user_email을 매번 포함시켜 프론트가
# 발신자 이름을 얻기 위한 추가 조회를 하지 않도록 한다.
def _to_out(m: Message) -> MessageOut:
    return MessageOut(
        id=m.id,
        team_id=m.team_id,
        user_id=m.user_id,
        user_email=m.user.email,
        content=m.content,
        created_at=m.created_at,
    )


# 메시지 전송. 길이 제한(1000자)은 schemas.MessageCreateRequest에서 1차 검증된다.
@router.post("/teams/{team_id}/messages", response_model=MessageOut, status_code=201)
def send_message(
    team_id: int,
    payload: MessageCreateRequest,
    user: User = Depends(require_team_member),
    db: Session = Depends(get_db),
):
    message = Message(team_id=team_id, user_id=user.id, content=payload.content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return _to_out(message)


# 채팅 폴링 조회. since 파라미터가 없으면 최초 진입으로 간주해 최근 50개를
# 오래된 순으로 반환하고, since가 있으면 그 이후 생성된 메시지만 오름차순으로 반환한다.
# 클라이언트는 매 5초마다 마지막으로 받은 메시지의 created_at을 since로 다시 보낸다.
@router.get("/teams/{team_id}/messages", response_model=list[MessageOut])
def list_messages(
    team_id: int,
    since: datetime | None = Query(default=None),
    user: User = Depends(require_team_member),
    db: Session = Depends(get_db),
):
    query = db.query(Message).filter(Message.team_id == team_id)
    if since is not None:
        query = query.filter(Message.created_at > since)
        messages = query.order_by(Message.created_at.asc()).all()
    else:
        messages = query.order_by(Message.created_at.desc()).limit(50).all()
        messages = list(reversed(messages))  # 최신 50개를 다시 시간 오름차순으로
    return [_to_out(m) for m in messages]


# 메시지 삭제. 작성자 본인만 가능하며 team owner도 예외가 아니다 (결정 #6 -
# "본인 메시지만" 정책, 신뢰 기반 커뮤니티 모델).
@router.delete("/messages/{message_id}")
def delete_message(message_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    message = db.get(Message, message_id)
    if not message:
        raise AppError(404, "NOT_FOUND", "해당 항목을 찾을 수 없습니다")
    if user.team_id != message.team_id:
        raise AppError(403, "FORBIDDEN", "이 팀에 접근할 권한이 없습니다")
    if message.user_id != user.id:
        raise AppError(403, "NOT_OWNER", "본인의 메시지만 삭제할 수 있습니다")
    db.delete(message)
    db.commit()
    return {}
