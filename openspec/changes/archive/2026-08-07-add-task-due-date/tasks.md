## 1. 백엔드 - 데이터 모델

- [x] 1.1 `Task` 모델에 `due_date`(nullable, DATE) 컬럼 추가
- [x] 1.2 `TaskOut`/`TaskCreateRequest`/`TaskUpdateRequest` 스키마에 `due_date` 필드 추가 (YYYY-MM-DD 형식, nullable)
- [x] 1.3 로컬 SQLite DB에 컬럼 반영 확인 (기존 DB 삭제 후 재생성 또는 마이그레이션)

## 2. 백엔드 - API

- [x] 2.1 `POST /teams/{id}/tasks`에서 `due_date` 저장 지원
- [x] 2.2 `PUT /tasks/{id}`에서 `due_date` 수정/해제(NULL) 지원 - creator/owner 권한 재사용
- [x] 2.3 `GET .../tasks`, `GET /tasks/{id}` 응답에 `due_date` 포함
- [x] 2.4 pytest: 마감일 설정/해제/권한(비권한자 수정 거부) 테스트 추가

## 3. 프론트엔드 - 표시

- [x] 3.1 카드에 D-day 배지 렌더링 (`D-N`/`D-DAY`/`D+N`), 마감일 없으면 배지 숨김
- [x] 3.2 마감 초과 + 미완료(TODO/DOING) 카드는 좌측 스트라이프를 `theme.js`의 `red` 토큰으로 오버라이드
- [x] 3.3 마감 초과 + DONE 카드는 평소 green 스트라이프 유지 (강조 안 함)

## 4. 프론트엔드 - 입력

- [x] 4.1 상세 모달에 마감일 `<input type="date">` 추가, 저장 시 `PUT /tasks/{id}`에 `due_date` 포함
- [x] 4.2 권한 없는 사용자는 날짜 입력도 비활성화 (기존 제목/담당자와 동일한 권한 규칙)
- [x] 4.3 태스크 인라인 생성 폼에는 마감일 입력을 추가하지 않음 (생성은 빠르게, 마감일은 상세 모달에서 나중에 설정 - proposal 범위)

## 5. 검증

- [x] 5.1 브라우저로 마감일 설정 → D-N 배지 → 과거 날짜로 마감 초과 → red 스트라이프 확인 (Playwright로 확인, D+218 배지)
- [x] 5.2 DONE 상태 + 마감 초과 조합에서 강조되지 않는지 확인 (Playwright로 확인, green 스트라이프 유지)
- [x] 5.3 pytest 전체 재실행, 기존 테스트 회귀 없음 (26개 전부 통과)
