import random
import string

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.errors import AppError
from ..deps import get_current_user, require_team_member
from ..models import Team, User
from ..schemas import MemberOut, TeamCreateRequest, TeamJoinRequest, TeamOut

router = APIRouter(prefix="/teams", tags=["teams"])


# 대문자 4자 + '-' + 숫자 4자(예: FRNT-2026) 형식의 고유 초대코드를 생성한다.
# 충돌 시 재시도하며, 코드는 팀 생성 후 절대 재발급하지 않는다 (leave 후 재합류도 동일 코드).
def generate_invite_code(db: Session) -> str:
    while True:
        letters = "".join(random.choices(string.ascii_uppercase, k=4))
        digits = "".join(random.choices(string.digits, k=4))
        code = f"{letters}-{digits}"
        if not db.query(Team).filter(Team.invite_code == code).first():
            return code


# 팀 생성. 생성자가 자동으로 owner가 되며, 이미 다른 팀에 소속된 사용자는
# 1인 1팀 제약(ACME Assumption)에 의해 새 팀을 만들 수 없다.
@router.post("", response_model=TeamOut, status_code=201)
def create_team(payload: TeamCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.team_id is not None:
        raise AppError(409, "ALREADY_IN_TEAM", "이미 팀에 소속되어 있습니다")
    team = Team(name=payload.name, invite_code=generate_invite_code(db), owner_id=user.id)
    db.add(team)
    db.flush()  # team.id를 미리 확보하기 위해 커밋 전 flush
    user.team_id = team.id
    db.commit()
    db.refresh(team)
    return TeamOut.model_validate(team)


# 초대코드로 기존 팀에 합류. 코드 형식은 schemas.TeamJoinRequest의 정규식으로
# 1차 검증되고, 여기서는 존재 여부만 확인한다.
@router.post("/join", response_model=TeamOut)
def join_team(payload: TeamJoinRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.team_id is not None:
        raise AppError(409, "ALREADY_IN_TEAM", "먼저 기존 팀을 나가야 합니다")
    team = db.query(Team).filter(Team.invite_code == payload.invite_code).first()
    if not team:
        raise AppError(404, "NOT_FOUND", "해당 초대코드를 찾을 수 없습니다")
    user.team_id = team.id
    db.commit()
    db.refresh(team)
    return TeamOut.model_validate(team)


# 팀 정보(이름/초대코드/owner) 재조회. 팀 생성 직후 1회성으로만 노출되던 초대코드를
# 언제든 다시 확인할 수 있도록 한다 (결정 추적표 #8 - GET /messages/{id} 대신 이 API로 대체).
@router.get("/{team_id}", response_model=TeamOut)
def get_team(team_id: int, user: User = Depends(require_team_member), db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    return TeamOut.model_validate(team)


# 팀 나가기. team_id를 NULL로 되돌릴 뿐 초대코드는 그대로 유지되므로
# 나중에 동일한 코드로 다시 합류할 수 있다.
@router.delete("/{team_id}/leave")
def leave_team(team_id: int, user: User = Depends(require_team_member), db: Session = Depends(get_db)):
    user.team_id = None
    db.commit()
    return {}


# 팀 멤버 목록. owner/member 역할만 구분하며 추방·역할 변경 기능은 범위 외.
@router.get("/{team_id}/members", response_model=list[MemberOut])
def list_members(team_id: int, requester: User = Depends(require_team_member), db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    members = db.query(User).filter(User.team_id == team_id).order_by(User.created_at).all()
    return [
        MemberOut(
            id=m.id,
            email=m.email,
            role="owner" if m.id == team.owner_id else "member",
            created_at=m.created_at,
        )
        for m in members
    ]
