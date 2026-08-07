## Why

소규모 팀(3-5인)이 칸반과 실시간에 가까운 채팅을 한 화면에서 오가며 업무 진행 상황을 추적할 수 있는 도구가 없다. TaskFlow MVP는 팀 리더, 팀원, 신규 합류자 3종 페르소나가 한 화면에서 태스크 상태와 팀 대화를 동시에 파악하도록 만든다. `docs/TaskFlow_프로그램정의.pdf`와 `docs/TaskFlow_스토리보드.pdf`(43장)에서 미션, 페르소나, 기능 5종, DB/API 사전 설계, ACME(Assumptions/Constraints/Metrics/Examples) 4요소가 이미 확정되어 있으며, 본 제안은 그 내용을 OpenSpec 아티팩트로 구조화한다.

## What Changes

- 이메일/비밀번호 기반 회원가입·로그인 추가. JWT(24h 만료, 갱신 없음, stateless 로그아웃) 발급, bcrypt 비밀번호 해시.
- 팀 생성/초대코드 발급/초대코드 합류/팀 나가기(leave) 추가. 1인 1팀 제약(`users.team_id`), 초대코드는 팀당 1개 고정 재사용(재발급 없음 — leave 후 재합류도 같은 코드 사용).
- 칸반 태스크 관리 추가: TODO/DOING/DONE 3컬럼, 생성/조회/필터(@me·미할당)/제목 수정/상태 이동(드래그)/삭제.
- 팀 채팅 추가: 팀 단위 메시지 송수신, 5초 폴링(`since=` 파라미터), 1000자 제한, 본인 메시지만 삭제 가능.
- 배포 파이프라인 추가: 로컬은 FastAPI + SQLite 단일 서버, 운영은 Vercel(FE+BE) + Neon(PostgreSQL), `DATABASE_URL` 환경변수로만 전환.
- 프론트엔드는 Vanilla JS + Tailwind CSS로 9개 화면(로그인/회원가입/팀선택/칸반/채팅/멤버목록 등) 구현.
- 공통 에러 응답 표준화: 모든 4xx/5xx가 `{ error: { code, message, meta? } }` 형태.

**범위 외 (이번에 하지 않음)**: 알림(이메일/SMS/푸시), 파일 첨부, 전문 검색, 권한 세분화(admin/member 이상), 다국어, WebSocket(실시간 대신 폴링), 로그인 실패 잠금(cooldown).

## Capabilities

### New Capabilities
- `auth`: 회원가입, 로그인, JWT 발급/검증, stateless 로그아웃, 현재 사용자 조회
- `teams`: 팀 생성, 초대코드 발급/재사용, 초대코드로 합류, 멤버 목록 조회, 팀 나가기
- `kanban-tasks`: 태스크 생성/조회/필터/제목 수정/상태 이동/삭제, 담당자(assignee) 지정 및 미할당 처리
- `chat`: 팀 단위 메시지 전송/폴링 조회/삭제
- `deployment`: 로컬(SQLite)/운영(Neon) 환경 분리, Vercel 배포 구성

### Modified Capabilities
(없음 - 그린필드 프로젝트로 기존 스펙 없음)

## Impact

- 신규 백엔드: FastAPI 애플리케이션, DB 스키마 4테이블(users/teams/tasks/messages), API 엔드포인트 18개.
- 신규 프론트엔드: `publish/` 퍼블리싱 파일(login.html, team.html, kanban.html, chat.html, components.html, theme.js)을 기준으로 한 정적 SPA.
- 신규 배포 구성: Vercel 프로젝트(FE+BE), Neon PostgreSQL, GitHub main 브랜치 자동 배포.
- 영향받는 기존 코드: 없음(그린필드).
