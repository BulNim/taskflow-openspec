## MODIFIED Requirements

### Requirement: 태스크 생성
시스템은 팀 멤버가 팀 칸반에 태스크를 생성하는 것을 SHALL 지원한다. 태스크는 제목(1-100자), 상태(기본 TODO), 생성자(creator), 선택적 담당자(assignee), 선택적 마감일(due_date, 날짜만, nullable)을 가진다.

#### Scenario: 정상 생성
- **WHEN** 팀 멤버가 1-100자 제목으로 `POST /teams/{id}/tasks`를 호출한다
- **THEN** 시스템은 201로 태스크를 생성하고 상태를 TODO로, creator를 호출자로 설정한다

#### Scenario: 마감일과 함께 생성
- **WHEN** 팀 멤버가 제목과 함께 `due_date`(YYYY-MM-DD)를 지정해 `POST /teams/{id}/tasks`를 호출한다
- **THEN** 시스템은 201로 태스크를 생성하고 지정된 마감일을 저장한다

### Requirement: 태스크 제목/담당자 수정
시스템은 creator 또는 팀 owner가 태스크의 제목, 담당자, 마감일을 수정하는 것을 SHALL 지원한다. 마감일은 값을 비워(NULL) 해제할 수 있다.

#### Scenario: 제목 수정
- **WHEN** creator 또는 팀 owner가 `PUT /tasks/{id}`를 호출한다
- **THEN** 시스템은 200으로 제목/담당자를 갱신한다

#### Scenario: 마감일 설정/해제
- **WHEN** creator 또는 팀 owner가 `due_date`를 포함해 `PUT /tasks/{id}`를 호출한다
- **THEN** 시스템은 200으로 마감일을 갱신하며, `due_date`가 NULL이면 마감일이 해제된다

## ADDED Requirements

### Requirement: 마감일 D-day 표시
시스템은 마감일이 설정된 태스크의 `due_date`를 API 응답에 SHALL 포함해, 클라이언트가 오늘 날짜 기준 남은 일수를 D-day 배지로 표시할 수 있게 한다. 마감일이 없는 태스크는 배지를 표시하지 않는다.

#### Scenario: 마감 전 태스크
- **WHEN** 태스크의 `due_date`가 오늘보다 미래이다
- **THEN** 클라이언트는 남은 일수를 `D-N` 형태로 표시한다 (예: 3일 남았으면 `D-3`)

#### Scenario: 오늘이 마감일
- **WHEN** 태스크의 `due_date`가 오늘 날짜와 같다
- **THEN** 클라이언트는 `D-DAY`로 표시한다

#### Scenario: 마감일 없는 태스크
- **WHEN** 태스크의 `due_date`가 NULL이다
- **THEN** 클라이언트는 D-day 배지를 표시하지 않는다

### Requirement: 마감 초과 카드 강조
클라이언트는 `due_date`가 오늘보다 과거이고 상태가 DONE이 아닌 태스크에 대해, 카드 좌측 스트라이프 색을 상태(TODO/DOING/DONE)와 무관하게 SHALL 항상 red(`publish/theme.js`의 `red.dot`/`red.text` 토큰)로 표시하고 D-day 배지를 `D+N`(N일 초과) 형태로 SHALL 표시한다. 상태값 자체(TODO/DOING/DONE)는 변경되지 않는다 - DONE으로 완료된 태스크는 마감이 지났더라도 초과 표시를 하지 않는다.

#### Scenario: 마감 초과, 미완료
- **WHEN** 태스크의 `due_date`가 오늘보다 과거이고 상태가 DONE이 아니다
- **THEN** 클라이언트는 좌측 스트라이프를 red로, 배지를 `D+N`으로 표시한다

#### Scenario: 마감 초과, 완료됨
- **WHEN** 태스크의 `due_date`가 오늘보다 과거이지만 상태가 DONE이다
- **THEN** 클라이언트는 마감 초과로 강조하지 않고 평소 상태색(green)을 유지한다
