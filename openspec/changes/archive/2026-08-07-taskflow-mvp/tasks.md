## 1. 프로젝트 셋업

- [x] 1.1 `backend/`(FastAPI), `frontend/`(정적 파일) 디렉터리 구조 생성
- [x] 1.2 FastAPI 프로젝트 초기화 (SQLAlchemy, pydantic, bcrypt, python-jose 등 의존성 설치)
- [x] 1.3 `DATABASE_URL` 환경변수 기반 SQLite/PostgreSQL 전환 설정
- [x] 1.4 `publish/`의 login.html, team.html, kanban.html, chat.html, theme.js를 `frontend/`로 이관하고 구조 정리 (디자인 토큰은 그대로, 실제 API 연동 로직으로 재작성)

## 2. DB 스키마

- [x] 2.1 `users` 테이블 생성 (id, email UNIQUE, password_hash, team_id FK NULL, created_at)
- [x] 2.2 `teams` 테이블 생성 (id, name, invite_code UNIQUE, owner_id FK, created_at)
- [x] 2.3 `tasks` 테이블 생성 (id, team_id FK, title, status, creator_id FK, assignee_id FK NULL, created_at)
- [x] 2.4 `messages` 테이블 생성 (id, team_id FK, user_id FK, content, created_at)
- [x] 2.5 인덱스 추가: `tasks(team_id, created_at)`, `messages(team_id, created_at)`, `teams(invite_code)` UNIQUE, `users(team_id)`
- [x] 2.6 로컬 SQLite 마이그레이션 스크립트 작성 및 실행 확인

## 3. 공통 인프라

- [x] 3.1 전역 예외 핸들러 구현: `{ error: { code, message, meta? } }` 표준 응답
- [x] 3.2 JWT 발급/검증 유틸리티 구현 (24h 만료, 갱신 없음)
- [x] 3.3 인증 의존성(dependency) 구현: 토큰 검증 실패 시 401 `TOKEN_EXPIRED`
- [x] 3.4 팀 멤버십 검증 의존성 구현: `/teams/{id}/*` 라우트에서 `user.team_id == id` 확인, 실패 시 403 `FORBIDDEN`
- [x] 3.5 creator/owner 권한 체크 함수 구현 (태스크 삭제·상태변경·수정에서 재사용)
- [x] 3.6 CORS 허용 도메인 설정 (Vercel 배포 도메인 명시)

## 4. Auth API (specs/auth)

- [x] 4.1 `POST /auth/signup` 구현 — 이메일 형식/중복, 비밀번호 8자 이상 검증 + bcrypt 해시
- [x] 4.2 `POST /auth/login` 구현 — 자격 증명 검증, JWT 발급, 이메일 존재 여부 비노출
- [x] 4.3 `POST /auth/logout` 구현 — stateless 200 응답
- [x] 4.4 `GET /auth/me` 구현
- [x] 4.5 signup/login 각 에러 케이스(400/401/409) 단위 테스트 작성

## 5. Teams API (specs/teams)

- [x] 5.1 `POST /teams` 구현 — 팀 생성, 초대코드 자동 생성(`AAAA-9999` 형식), owner 지정, `users.team_id` 갱신
- [x] 5.2 `POST /teams/join` 구현 — 초대코드 검증(형식/존재/이미 소속), `users.team_id` 갱신
- [x] 5.3 `DELETE /teams/{id}/leave` 구현 — `users.team_id`를 NULL로, 초대코드는 유지(재사용 가능)
- [x] 5.3b `GET /teams/{id}` 구현 — 팀 이름/초대코드/owner 재조회 (스토리보드에 있었으나 최초 구현에서 누락, 이후 추가)
- [x] 5.4 `GET /teams/{id}/members` 구현 — owner/member 역할 포함 멤버 목록
- [x] 5.5 비멤버 접근 차단 미들웨어 적용 및 403 케이스 테스트

## 6. Kanban Tasks API (specs/kanban-tasks)

- [x] 6.1 `POST /teams/{id}/tasks` 구현 — 제목 1-100자 검증, TODO 기본값
- [x] 6.2 `GET /teams/{id}/tasks` 구현 — 전체/@me/미할당 필터, 최근 생성순 정렬
- [x] 6.3 `GET /tasks/{id}` 구현 — 단일 태스크 상세
- [x] 6.4 `PATCH /tasks/{id}/status` 구현 — creator/owner 전용 권한 체크 적용
- [x] 6.5 `PUT /tasks/{id}` 구현 — 제목/담당자 수정, creator/owner 전용
- [x] 6.6 `DELETE /tasks/{id}` 구현 — creator/owner 전용, owner는 타인 태스크도 삭제 가능
- [x] 6.7 권한 매트릭스(본인 카드/타인 카드 × owner/member) 테스트 작성

## 7. Chat API (specs/chat)

- [x] 7.1 `POST /teams/{id}/messages` 구현 — 1000자 검증(서버측), 발신자/시각 기록
- [x] 7.2 `GET /teams/{id}/messages` 구현 — `since=` 파라미터 기반 증분 조회, 최초 진입 시 최근 50개
- [x] 7.3 `GET /messages/{id}` 구현
- [x] 7.4 `DELETE /messages/{id}` 구현 — 작성자 본인만, owner도 예외 없음(403 `NOT_OWNER`)
- [x] 7.5 메시지 누락 0건 보장 테스트 (연속 전송 → 폴링 재연결 → 전체 노출 확인)

## 8. 프론트엔드 — 인증/팀 흐름

- [x] 8.1 로그인/회원가입 화면 연동 (초기/입력중/처리중 상태, 클라이언트 검증)
- [x] 8.2 JWT localStorage 저장/조회/삭제 + 401 응답 시 자동 `/login` redirect
- [x] 8.3 팀 선택 화면 연동 (`team_id` NULL 사용자 강제 진입, 팀 만들기/초대코드 합류)
- [x] 8.4 팀 멤버 목록 사이드 패널 연동

## 9. 프론트엔드 — 칸반/채팅

- [x] 9.1 칸반 3컬럼 렌더링 + 필터(전체/@me/미할당) + 빈 상태(empty state) 처리
- [x] 9.2 태스크 인라인 생성 (TODO 컬럼 `+` → 입력 → Enter 저장)
- [x] 9.3 HTML5 드래그앤드롭으로 상태 변경, 권한 없는 카드는 드래그 비활성화 또는 403 처리 + 모바일 길게 누르기 상태 변경 시트(터치 기기는 HTML5 DnD 미지원이라 대체 UI 필요, 최초 구현에서 누락되어 이후 추가)
- [x] 9.4 태스크 상세/수정 모달 (상태·담당자 변경, 삭제 확인 다이얼로그)
- [x] 9.5 채팅 화면: 5초 폴링, 메시지 카운터(1000자), 본인 메시지 삭제 UI
- [x] 9.6 모바일 반응형: 칸반 컬럼 스와이프(<768px), 채팅 풀스크린, 햄버거 메뉴 (Tailwind 반응형 클래스 적용 — 실기기 수동 확인은 미실시)

## 10. 배포 (specs/deployment)

- [ ] 10.1 Vercel 프로젝트 생성 및 GitHub 레포 연결 (main push 자동 배포) — 사용자의 Vercel 계정 필요, `DEPLOY.md` 참고
- [ ] 10.2 Neon PostgreSQL 프로비저닝, 운영 `DATABASE_URL` 설정 — 사용자의 Neon 계정 필요, `DEPLOY.md` 참고
- [x] 10.3 백엔드를 Vercel Serverless Functions로 배포 구성 (`vercel.json` 라우팅 작성)
- [x] 10.4 프론트엔드 정적 파일 배포 구성 (`vercel.json`에 `frontend/` 정적 서빙 포함)
- [ ] 10.5 배포 후 스모크 테스트: 회원가입→팀생성→칸반→채팅 전 흐름 확인 — 실제 배포 후 사용자 확인 필요

## 11. 검증

- [x] 11.1 결정 추적표 10건이 구현/스펙에 반영되었는지 최종 대조
- [x] 11.2 ACME Metrics 정성 검증: 기능 5종 정상 흐름(브라우저로 확인), 에러 응답 100% 표준 형태(테스트로 확인), 권한 격리 100%(테스트로 확인)
- [x] 11.3 신규 합류자 시나리오 수동 테스트 (회원가입→팀생성→칸반→채팅, Playwright로 확인)
