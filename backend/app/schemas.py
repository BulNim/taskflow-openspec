from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

# ── Auth ────────────────────────────────────────────────────────────────


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)  # 8자 이상 강제 (ACME Constraint)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    team_id: int | None  # NULL이면 팀 미소속 - 프론트에서 팀 선택 화면으로 분기

    class Config:
        from_attributes = True  # SQLAlchemy 모델 인스턴스에서 바로 직렬화


class AuthOut(BaseModel):
    token: str
    user: UserOut


# ── Teams ───────────────────────────────────────────────────────────────


class TeamCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=30)


class TeamJoinRequest(BaseModel):
    # 대문자 4자 + '-' + 숫자 4자 (예: FRNT-2026). 서버가 자동 생성하는 형식과 동일.
    invite_code: str = Field(pattern=r"^[A-Z]{4}-[0-9]{4}$")


class TeamOut(BaseModel):
    id: int
    name: str
    invite_code: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MemberOut(BaseModel):
    id: int
    email: str
    role: str  # "owner" | "member"
    created_at: datetime


# ── Kanban Tasks ────────────────────────────────────────────────────────


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    assignee_id: int | None = None  # 비워두면 "미할당" 상태로 생성
    due_date: date | None = None  # 선택적 마감일 (YYYY-MM-DD), 시간대 없이 날짜만


class TaskUpdateRequest(BaseModel):
    # PUT /tasks/{id} - 제목/담당자/마감일 수정 (상태 변경은 별도 PATCH 엔드포인트, 결정 #3)
    title: str = Field(min_length=1, max_length=100)
    assignee_id: int | None = None
    due_date: date | None = None  # None이면 마감일 해제


class TaskStatusRequest(BaseModel):
    status: str = Field(pattern=r"^(TODO|DOING|DONE)$")


class TaskOut(BaseModel):
    id: int
    team_id: int
    title: str
    status: str
    creator_id: int
    assignee_id: int | None
    due_date: date | None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Chat ────────────────────────────────────────────────────────────────


class MessageCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=1000)  # 1000자 제한 (ACME Constraint)


class MessageOut(BaseModel):
    id: int
    team_id: int
    user_id: int
    user_email: str  # 프론트에서 별도 조회 없이 바로 발신자 표시하도록 포함
    content: str
    created_at: datetime
