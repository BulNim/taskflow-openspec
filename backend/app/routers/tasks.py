from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.errors import AppError
from ..deps import get_current_user, require_task_permission, require_team_member
from ..models import Task, Team, User
from ..schemas import TaskCreateRequest, TaskOut, TaskStatusRequest, TaskUpdateRequest

router = APIRouter(tags=["tasks"])


# /tasks/{id} 계열 엔드포인트(팀 id가 경로에 없음)에서 공통으로 쓰는 헬퍼.
# 태스크를 찾고, 로그인 사용자가 그 태스크가 속한 팀의 멤버인지 확인한 뒤
# 권한 체크(require_task_permission)에 필요한 team까지 함께 반환한다.
def _get_task_and_team(task_id: int, user: User, db: Session) -> tuple[Task, Team]:
    task = db.get(Task, task_id)
    if not task:
        raise AppError(404, "NOT_FOUND", "해당 항목을 찾을 수 없습니다")
    if user.team_id != task.team_id:
        raise AppError(403, "FORBIDDEN", "이 팀에 접근할 권한이 없습니다")
    team = db.get(Team, task.team_id)
    return task, team


# 태스크 생성. 상태는 항상 TODO로 시작하며, assignee_id를 생략하면 "미할당" 카드가 된다.
@router.post("/teams/{team_id}/tasks", response_model=TaskOut, status_code=201)
def create_task(
    team_id: int,
    payload: TaskCreateRequest,
    user: User = Depends(require_team_member),
    db: Session = Depends(get_db),
):
    task = Task(
        team_id=team_id,
        title=payload.title,
        status="TODO",
        creator_id=user.id,
        assignee_id=payload.assignee_id,
        due_date=payload.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


# 칸반 목록 조회. filter=all(기본)/me(내 담당)/unassigned(미할당)로 좁혀서 조회할 수 있고,
# 항상 최근 생성순(created_at desc)으로 정렬한다.
@router.get("/teams/{team_id}/tasks", response_model=list[TaskOut])
def list_tasks(
    team_id: int,
    filter: str = Query(default="all", pattern="^(all|me|unassigned)$"),
    user: User = Depends(require_team_member),
    db: Session = Depends(get_db),
):
    query = db.query(Task).filter(Task.team_id == team_id)
    if filter == "me":
        query = query.filter(Task.assignee_id == user.id)
    elif filter == "unassigned":
        query = query.filter(Task.assignee_id.is_(None))
    tasks = query.order_by(Task.created_at.desc()).all()
    return [TaskOut.model_validate(t) for t in tasks]


# 단일 태스크 상세 조회. 상세/수정 모달을 열 때 사용.
@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task, _ = _get_task_and_team(task_id, user, db)
    return TaskOut.model_validate(task)


# 칸반 드래그(또는 모바일 상태 변경 시트)로 호출되는 상태 전환 전용 엔드포인트.
# PUT(제목/담당자 수정)과 의도적으로 분리되어 있다 (결정 #3 - REST 의미 + 드래그 별도 처리).
# creator 또는 team owner만 가능 - 담당자여도 그 둘이 아니면 403.
@router.patch("/tasks/{task_id}/status", response_model=TaskOut)
def update_task_status(
    task_id: int,
    payload: TaskStatusRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task, team = _get_task_and_team(task_id, user, db)
    require_task_permission(task, team, user)
    task.status = payload.status
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


# 제목/담당자 수정. creator 또는 team owner만 가능.
@router.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task, team = _get_task_and_team(task_id, user, db)
    require_task_permission(task, team, user)
    task.title = payload.title
    task.assignee_id = payload.assignee_id
    task.due_date = payload.due_date
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


# 태스크 삭제(되돌릴 수 없음). creator 또는 team owner만 가능하며,
# owner는 본인이 만들지 않은 태스크도 삭제할 수 있다 (오버라이드 권한).
@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task, team = _get_task_and_team(task_id, user, db)
    require_task_permission(task, team, user)
    db.delete(task)
    db.commit()
    return {}
