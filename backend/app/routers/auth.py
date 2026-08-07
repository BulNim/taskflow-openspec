from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.errors import AppError
from ..core.security import create_access_token, hash_password, verify_password
from ..deps import get_current_user
from ..models import User
from ..schemas import AuthOut, LoginRequest, SignupRequest, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


# 이메일 중복 확인 후 bcrypt로 비밀번호를 해시해 계정을 만들고, 가입 즉시
# 로그인 상태로 만들기 위해 JWT를 함께 발급한다 (이메일 인증 절차 없음).
@router.post("/signup", response_model=AuthOut, status_code=201)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise AppError(409, "EMAIL_TAKEN", "이미 가입된 이메일입니다")
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return AuthOut(token=token, user=UserOut.model_validate(user))


# 이메일 존재 여부를 노출하지 않기 위해 "이메일 없음"과 "비밀번호 틀림"을
# 동일한 401 INVALID_CREDENTIALS 하나로 합쳐서 응답한다 (보안 고려사항).
@router.post("/login", response_model=AuthOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise AppError(401, "INVALID_CREDENTIALS", "이메일 또는 비밀번호가 일치하지 않습니다")
    token = create_access_token(user.id)
    return AuthOut(token=token, user=UserOut.model_validate(user))


# JWT는 stateless라 서버에 블랙리스트를 두지 않는다 (결정 #5). 클라이언트가
# localStorage 토큰을 지우는 것으로 로그아웃을 완료하고, 서버는 200만 반환한다.
@router.post("/logout")
def logout(user: User = Depends(get_current_user)):
    return Response(status_code=200, content="{}", media_type="application/json")


# 프론트엔드가 페이지 진입 시 현재 로그인 사용자 정보(특히 team_id)를 확인해
# 팀 선택/칸반 중 어디로 라우팅할지 판단하는 데 사용한다.
@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)
