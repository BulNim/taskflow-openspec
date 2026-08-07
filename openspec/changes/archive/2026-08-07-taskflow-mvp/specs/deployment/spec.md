## Purpose

로컬 개발 환경과 운영 배포 환경을 코드 변경 없이 환경변수 하나로 전환할 수 있게 하여, 학습 단순성과 실전 배포 표준을 동시에 만족시킨다.

## ADDED Requirements

### Requirement: 로컬/운영 환경 분리
시스템은 `DATABASE_URL` 환경변수만으로 로컬 SQLite와 운영 PostgreSQL(Neon) 사이를 전환하는 것을 SHALL 지원한다. 애플리케이션 코드는 두 환경에서 동일해야 한다.

#### Scenario: 로컬 실행
- **WHEN** `DATABASE_URL`이 로컬 SQLite 파일 경로로 설정된 상태로 서버를 실행한다
- **THEN** 시스템은 SQLite 파일을 데이터 저장소로 사용하여 정상 동작한다

#### Scenario: 운영 실행
- **WHEN** `DATABASE_URL`이 Neon PostgreSQL 연결 문자열로 설정된 상태로 배포된다
- **THEN** 시스템은 PostgreSQL을 데이터 저장소로 사용하여 동일하게 동작한다

### Requirement: 자동 배포
시스템은 GitHub `main` 브랜치로의 push 시 프론트엔드(정적 파일)와 백엔드(Serverless Functions)가 Vercel에 함께 자동 배포되는 것을 SHALL 지원한다.

#### Scenario: main 브랜치 push
- **WHEN** `main` 브랜치에 코드가 push된다
- **THEN** Vercel은 프론트엔드와 백엔드를 함께 자동으로 재배포한다

### Requirement: CORS 허용 도메인 명시
시스템은 배포된 프론트엔드 도메인만 백엔드 API에 CORS로 접근할 수 있도록 허용 도메인을 명시적으로 설정하는 것을 SHALL 요구한다.

#### Scenario: 허용되지 않은 오리진의 요청
- **WHEN** 허용 목록에 없는 오리진에서 API를 호출한다
- **THEN** 브라우저는 CORS 정책에 의해 응답을 차단한다
