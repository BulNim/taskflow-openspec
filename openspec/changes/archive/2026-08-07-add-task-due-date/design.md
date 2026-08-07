## Context

See proposal.md - Why. `tasks` 테이블과 `TaskOut`/`TaskCreateRequest`/`TaskUpdateRequest` 스키마(`backend/app/models.py`, `schemas.py`)에 필드를 추가하고, `frontend/kanban.html`의 카드 렌더링(`cardHtml`)과 상세 모달(`openModal`)을 확장한다. 색 토큰은 `frontend/theme.js`(= `publish/theme.js`)의 `STRIPE`/`LABEL` 객체에 이미 `red`가 정의되어 있어 새 토큰 없이 그대로 재사용한다.

## Goals / Non-Goals

**Goals:**
- 마감일을 선택적으로 설정/해제할 수 있게 한다.
- D-day 배지와 마감 초과 시 red 스트라이프를 클라이언트에서 순수 계산으로 표시한다(서버가 "초과 여부"를 별도 필드로 내려주지 않고, 서버는 `due_date`만 주고 판단은 클라이언트가 오늘 날짜와 비교해서 한다 - 서버·클라이언트 시간대 불일치 리스크를 줄이기 위해 날짜만 다룬다).

**Non-Goals:**
- 마감 임박 알림(이메일/푸시)은 범위 외 - proposal.md의 기존 범위 외 정책(알림 없음)과 동일하게 유지.
- 반복 마감일, 시간 단위 마감(HH:MM)은 범위 외 - 날짜 단위만 지원.

## Decisions

### 1. `due_date`는 날짜(DATE) 타입, 시간 없음
시간까지 다루면 서버(UTC/KST)와 클라이언트 로컬 시간대 비교가 복잡해진다. TaskFlow는 이미 ACME Assumption에서 "단일 시간대(KST)"를 전제하므로, 날짜만 비교해 "오늘 KST 날짜 기준 지났는지"로 단순화한다.
- 대안: datetime + 시간대 변환 — 정밀하지만 이번 범위(칸반 우선순위 파악)에는 과함. 기각.

### 2. 초과 여부는 서버가 계산하지 않고 클라이언트가 계산
`due_date`만 API로 내려주고, "초과 여부"와 "D-N 문구"는 프론트엔드에서 `new Date()` 대비 계산한다. 폴링/캐시된 응답이 하루를 넘겨도(자정 경과) 클라이언트가 매 렌더링 시 다시 계산하므로 별도 무효화 로직이 필요 없다.
- 대안: 서버가 `is_overdue` boolean을 응답에 포함 — 요청 시점에 고정되어 화면을 오래 열어두면 자정 경과 시 갱신 안 됨. 기각.

### 3. DONE 태스크는 마감 초과여도 강조하지 않음
완료된 작업까지 red로 강조하면 "지금 급한 일"이라는 신호의 의미가 흐려진다. `kanban-tasks` 스펙의 "마감 초과 카드 강조" 요구사항에 이 예외를 명시했다.

### 4. 상세 모달에 date input 추가, 담당자 select 옆에 배치
기존 담당자 select와 같은 스타일(`window.UI.input`류)로 `<input type="date">`를 추가한다. 별도 컴포넌트 없이 네이티브 date picker를 사용해 구현을 단순화한다.

## Risks / Trade-offs

- [Risk] 클라이언트 로컬 시각이 서버(KST) 기준과 다르면 D-day 계산이 사용자마다 다르게 보일 수 있다 → Mitigation: ACME Assumption("단일 시간대 KST, 모던 브라우저")을 그대로 따르며, 이번 범위에서는 타임존 보정을 하지 않는다(기존 프로젝트 전제와 동일한 수준의 리스크).
- [Risk] 기존 데이터에는 `due_date` 컬럼이 없어 마이그레이션이 필요하다 → Mitigation: nullable 컬럼 추가이므로 기존 SQLite 파일도 `ALTER TABLE` 한 줄로 무중단 적용 가능 (로컬은 재생성해도 무방, 운영은 아직 배포 전이라 영향 없음).
