## Why

칸반 카드에 마감일이 없어서 팀 리더가 "무엇이 급한지"를 한눈에 파악할 수 없다. 마감일과 D-day 표시, 마감 초과 시각화를 추가해 우선순위 판단을 쉽게 한다.

## What Changes

- 태스크에 선택적 마감일(`due_date`, 날짜만, nullable) 필드 추가.
- 칸반 카드에 남은 일수를 `D-N`(오늘이면 `D-DAY`, 지났으면 `D+N`) 배지로 표시.
- 마감일이 지난(오늘 날짜 기준 초과) 카드는 상태별 색 대신 **좌측 스트라이프를 항상 red**로 표시해 눈에 띄게 한다. 상태 라벨(TODO/DOING/DONE) 자체는 바뀌지 않는다.
- 마감일 설정/수정은 기존 "제목/담당자 수정" 권한과 동일하게 **creator 또는 팀 owner만** 가능.
- 색상은 `publish/theme.js`에 이미 정의된 토큰(`red.dot`, `red.text` 등)만 사용하고 새 색을 도입하지 않는다.

## Capabilities

### New Capabilities
(없음)

### Modified Capabilities
- `kanban-tasks`: 태스크 생성/수정 시 `due_date`를 지정할 수 있고, 마감일 초과 여부에 따라 카드 표시(D-day 배지, 스트라이프 색)가 달라진다.

## Impact

- 백엔드: `tasks` 테이블에 `due_date` 컬럼 추가(nullable), `POST/PUT /tasks` 요청/응답 스키마 확장.
- 프론트엔드: `kanban.html` 카드 렌더링(D-day 배지, red 스트라이프 오버라이드)과 상세 모달(날짜 입력 필드) 수정.
- 기존 데이터: 기존 태스크는 `due_date = NULL`로 유지되며 마감일 없는 카드로 계속 동작(**BREAKING 아님**).
