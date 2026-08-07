## Context

See proposal.md - Why. 기술 스택과 DB/API 형태는 이미 `docs/TaskFlow_프로그램정의.pdf` / `docs/TaskFlow_스토리보드.pdf`에서 사전 확정되어 AI가 임의로 결정하지 않도록 명시되어 있다: 백엔드 FastAPI + PostgreSQL(운영, Neon)/SQLite(로컬), 프론트엔드 Vanilla JS + Tailwind. UI는 `publish/`의 퍼블리싱 파일(login.html, team.html, kanban.html, chat.html, theme.js)이 문서보다 강한 기준이며 클래스 규칙을 그대로 따른다.

## Goals / Non-Goals

**Goals:**
- 스토리보드의 결정 추적표 10건(특히 Critical 1-4: users-teams 멤버십, 신규 합류자 행동, PUT/PATCH 분리, assignee 정의)을 스펙과 구현에 그대로 반영한다.
- 인증→팀 소속→칸반/채팅 접근이라는 단일 분기 흐름을 백엔드 미들웨어 수준에서 일관되게 강제한다.
- 로컬 개발과 운영 배포가 코드 변경 없이 `DATABASE_URL` 하나로 전환되게 한다.

**Non-Goals:**
- 실시간(WebSocket) 동기화, 알림, 파일 첨부, 전문 검색, 세분화된 권한(admin/member 이상), 다국어, 로그인 실패 잠금 — proposal의 범위 외 항목과 동일하게 이번 change에서 구현하지 않는다.
- 성능/드래그 반응성(<50ms, API 100ms)은 자동화 도구로 측정하지 않고 정성적 확인으로 검증한다 (ACME Metrics 결정 #7).

## Decisions

### 1. 저장소 구조: 단일 레포, `backend/` + `frontend/` 분리
백엔드(FastAPI)와 프론트엔드(정적 파일)를 하나의 Git 레포 안에 두 디렉터리로 나눈다. Vercel이 같은 레포에서 정적 파일 배포와 Serverless Functions 배포를 동시에 지원하므로 별도 레포/모노레포 도구 없이 단순하게 유지한다.
- 대안: 프론트/백 별도 레포 — 배포 파이프라인이 두 개로 늘어나고 Day 2 학습 목적에 비해 과함. 기각.

### 2. 인증/인가: JWT + 팀 멤버십 미들웨어
모든 `/teams/{id}/*` 라우트는 공통 의존성(dependency)에서 JWT를 검증하고 `user.team_id == id`를 확인한다. 실패 시 401(토큰 문제)과 403(멤버십 문제)을 구분해서 반환한다.
- creator/owner 전용 작업(태스크 삭제, 상태 변경, 태스크 제목 수정)은 별도의 권한 체크 함수로 라우트 핸들러 안에서 검증한다 (미들웨어 레벨이 아님 — 리소스별 creator/owner 비교가 필요하므로).
- 대안: 역할 기반 세분화 권한 시스템 — 이번 MVP 범위 외(ACME Assumptions/Constraints)로 기각.

### 3. 칸반 상태 변경 권한: creator/owner로 제한 (스토리보드 대비 축소)
스토리보드 슬라이드 19의 와이어프레임은 팀원이 자유롭게 드래그하는 그림이지만, explore 단계에서 사용자가 "상태 변경도 creator/owner만 가능"으로 확정했다. `PATCH /tasks/{id}/status`는 DELETE와 동일한 권한 체크 함수를 재사용한다.
- 트레이드오프: 담당자가 아닌 팀원은 남의 카드를 못 옮긴다. 페르소나 "팀원"의 핵심 행동(드래그)이 제약되지만, 명시적 사용자 결정이므로 스펙(`kanban-tasks`)에 그대로 반영했다.

### 4. 채팅 폴링: `since=` 타임스탬프 커서
클라이언트는 마지막으로 받은 메시지의 `created_at`을 다음 요청의 `since` 파라미터로 보낸다. 서버는 `WHERE team_id = ? AND created_at > ?` 인덱스(`messages(team_id, created_at)`)로 조회한다.
- 대안: 메시지 id 커서 — 시각 정렬과 `created_at` 인덱스를 칸반 정렬에도 재사용하므로 타임스탬프 커서로 통일.

### 5. 에러 응답 표준
모든 예외를 FastAPI 전역 예외 핸들러에서 `{ error: { code, message, meta? } }` 형태로 직렬화한다. `code`는 SCREAMING_SNAKE, `message`는 한국어 사용자 노출 문구.

## Risks / Trade-offs

- [Risk] 5초 폴링은 팀 규모(≤5명 동시 접속 가정)를 넘어서면 DB 부하가 커진다 → Mitigation: Assumptions에 명시된 "팀당 5명 이하" 전제를 유지하고, 초과 시나리오는 범위 외로 문서화.
- [Risk] JWT 갱신이 없어 24시간 후 강제 재로그인 — 작업 중 세션이 끊길 수 있다 → Mitigation: 클라이언트가 401 수신 시 즉시 `/login`으로 안내(직전 URL 저장 없음, 스토리보드 결정 그대로).
- [Risk] 칸반 상태 변경을 creator/owner로 제한하면 실제 사용성이 스토리보드 와이어프레임과 어긋날 수 있다 → Mitigation: tasks.md와 스펙에 이 결정을 명확히 남겨 구현/QA 단계에서 재해석되지 않도록 한다.

## Open Questions

(없음 — explore 단계에서 주요 모호성은 모두 사용자와 확정함)
