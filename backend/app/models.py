from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship  # noqa: F401

from .core.db import Base


def utcnow():
    return datetime.now(timezone.utc)


# 사용자 계정. team_id가 NULL이면 아직 어느 팀에도 소속되지 않은 상태 - 이 경우
# 프론트엔드가 팀 선택 화면으로 강제 라우팅한다 (1인 1팀 제약, ACME Assumption #1).
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# 팀. invite_code는 팀 생성 시 서버가 자동 생성하며 이후 재발급되지 않는다 -
# 멤버가 팀을 나가도(leave) 동일한 코드로 다시 합류할 수 있다.
class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    invite_code: Mapped[str] = mapped_column(String(9), unique=True, nullable=False, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# 칸반 태스크. assignee_id는 nullable - 담당자 없는 카드는 "미할당"으로 표시되며
# 누구나 담당자로 지정할 수 있다. 상태 변경/삭제/제목수정은 creator 또는 team owner만 가능
# (deps.require_task_permission에서 검증). team_id+created_at 인덱스는 칸반 정렬/조회용.
class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (Index("ix_tasks_team_created", "team_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="TODO")  # TODO | DOING | DONE
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)  # 날짜만, 시간대는 다루지 않음
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# 팀 채팅 메시지. team_id+created_at 인덱스는 5초 폴링(since= 파라미터) 조회 성능을 위한 것.
# 삭제는 작성자 본인만 가능하며 team owner도 예외가 아니다 (결정 #6).
class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (Index("ix_messages_team_created", "team_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # 메시지 응답에 발신자 이메일을 바로 포함시키기 위한 eager-load 관계.
    user: Mapped["User"] = relationship("User", lazy="joined")
