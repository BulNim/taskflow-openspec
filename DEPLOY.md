# 배포 가이드

로컬 구현과 자동 테스트는 완료되어 있습니다. 아래 절차는 Vercel/Neon 계정이 필요해 사용자가 직접 진행해야 합니다.

## 1. Neon PostgreSQL 프로비저닝
1. https://neon.tech 에서 프로젝트 생성
2. 연결 문자열(`postgres://...`)을 복사

## 2. Vercel 프로젝트 연결
1. `vercel link`로 이 레포를 Vercel 프로젝트에 연결
2. 프로젝트 설정 > Environment Variables에 추가:
   - `DATABASE_URL` = Neon 연결 문자열
   - `JWT_SECRET` = 임의의 안전한 문자열
   - `CORS_ORIGINS` = 배포된 프론트엔드 도메인 (예: `https://taskflow.vercel.app`)
3. GitHub 레포를 Vercel과 연결하면 `main` push 시 `vercel.json` 설정에 따라 프론트엔드(`frontend/`)와 백엔드(`backend/app/main.py`, Serverless Function)가 함께 배포됩니다.

## 3. 배포 후 스모크 테스트
회원가입 → 팀 생성 → 칸반 태스크 생성/상태변경 → 채팅 전송/폴링까지 실제 배포 URL에서 확인합니다.

## 로컬 개발 실행

```bash
# 백엔드
cd backend
python -m venv .venv && .venv/Scripts/activate  # Windows
pip install -r requirements-dev.txt
python scripts/init_db.py
uvicorn app.main:app --reload --port 8000

# 프론트엔드 (별도 터미널)
cd frontend
python -m http.server 5500
```

`frontend/api.js`는 `localhost`/`127.0.0.1`에서 자동으로 `http://127.0.0.1:8000`을 API 베이스로 사용합니다.
