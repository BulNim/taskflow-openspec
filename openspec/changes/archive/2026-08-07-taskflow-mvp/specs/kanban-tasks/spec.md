## Purpose

팀원이 TODO/DOING/DONE 3컬럼 칸반으로 태스크를 만들고 상태를 옮기며 업무 진행 상황을 한 화면에서 추적하도록 한다.

## ADDED Requirements

### Requirement: 태스크 생성
시스템은 팀 멤버가 팀 칸반에 태스크를 생성하는 것을 SHALL 지원한다. 태스크는 제목(1-100자), 상태(기본 TODO), 생성자(creator), 선택적 담당자(assignee)를 가진다.

#### Scenario: 정상 생성
- **WHEN** 팀 멤버가 1-100자 제목으로 `POST /teams/{id}/tasks`를 호출한다
- **THEN** 시스템은 201로 태스크를 생성하고 상태를 TODO로, creator를 호출자로 설정한다

### Requirement: 태스크 목록 조회 및 필터
시스템은 팀 멤버가 팀의 태스크 목록을 조회하는 것을 SHALL 지원하며, 전체/`@me`(담당자=나)/미할당(담당자 없음) 필터와 최근 생성순 정렬을 제공해야 한다.

#### Scenario: 전체 조회
- **WHEN** 팀 멤버가 필터 없이 `GET /teams/{id}/tasks`를 호출한다
- **THEN** 시스템은 200과 함께 해당 팀의 모든 태스크를 최근 생성순으로 반환한다

#### Scenario: 내 태스크 필터
- **WHEN** 팀 멤버가 `@me` 필터로 조회한다
- **THEN** 시스템은 `assignee_id`가 호출자인 태스크만 반환한다 (creator 기준이 아님)

#### Scenario: 미할당 필터
- **WHEN** 팀 멤버가 미할당 필터로 조회한다
- **THEN** 시스템은 `assignee_id`가 NULL인 태스크만 반환한다

### Requirement: 담당자(assignee) 지정
시스템은 태스크에 담당자를 지정하거나 비워두는(nullable) 것을 SHALL 지원한다. 담당자가 없는 태스크는 누구나 담당자로 지정할 수 있다.

#### Scenario: 담당자 없는 태스크 표시
- **WHEN** 태스크의 `assignee_id`가 NULL이다
- **THEN** 시스템은 해당 태스크를 "미할당" 상태로 노출한다

### Requirement: 태스크 상태 이동
시스템은 태스크의 상태(TODO/DOING/DONE)를 변경하는 것을 SHALL 지원하되, **creator 또는 팀 owner만** 상태를 변경할 수 있다. 그 외 멤버가 시도하면 거부해야 한다.

#### Scenario: 권한자의 상태 변경
- **WHEN** 태스크의 creator 또는 팀 owner가 `PATCH /tasks/{id}/status`를 호출한다
- **THEN** 시스템은 200으로 상태를 변경한다

#### Scenario: 비권한자의 상태 변경 시도
- **WHEN** creator도 owner도 아닌 팀 멤버가 다른 사람의 태스크 상태 변경을 시도한다
- **THEN** 시스템은 403 `FORBIDDEN`을 반환하고 상태를 변경하지 않는다

### Requirement: 태스크 제목/담당자 수정
시스템은 creator 또는 팀 owner가 태스크의 제목과 담당자를 수정하는 것을 SHALL 지원한다.

#### Scenario: 제목 수정
- **WHEN** creator 또는 팀 owner가 `PUT /tasks/{id}`를 호출한다
- **THEN** 시스템은 200으로 제목/담당자를 갱신한다

### Requirement: 태스크 삭제
시스템은 creator 또는 팀 owner만 태스크를 삭제하는 것을 SHALL 지원한다. owner는 타인이 만든 태스크도 삭제할 수 있다(오버라이드). 그 외 멤버는 삭제할 수 없다.

#### Scenario: 권한자의 삭제
- **WHEN** creator 또는 팀 owner가 `DELETE /tasks/{id}`를 호출한다
- **THEN** 시스템은 200으로 태스크를 삭제한다(되돌릴 수 없음)

#### Scenario: 비권한자의 삭제 시도
- **WHEN** creator도 owner도 아닌 멤버가 삭제를 시도한다
- **THEN** 시스템은 403 `FORBIDDEN`을 반환한다

### Requirement: 단일 태스크 상세 조회
시스템은 팀 멤버가 단일 태스크의 상세 정보(제목, 상태, creator, assignee, 생성 시각)를 조회하는 것을 SHALL 지원한다.

#### Scenario: 상세 조회
- **WHEN** 팀 멤버가 `GET /tasks/{id}`를 호출한다
- **THEN** 시스템은 200과 함께 태스크 상세 정보를 반환한다
