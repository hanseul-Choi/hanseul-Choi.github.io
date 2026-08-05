# POLICY — contracts

## 역할
다른 모든 기능 모듈(`content_loader`, `renderer`, `link_checker`, `site_builder`)이 공유하는
유일한 데이터 표면. `Project`, `NavItem`, `PageContent`, `SiteConfig` 등 Pydantic 모델과
공용 예외 타입(`ContractValidationError` 등)을 정의한다.

## 규칙
- 이 모듈은 다른 어떤 기능 모듈도 import하지 않는다 (의존성 최하단).
- 모델 필드를 변경하거나 제거하는 것은 breaking change로 간주하고, AGENTS.md 규칙 23에 따라
  구현 전에 계약과 실패 테스트를 먼저 확정한다.
- 모든 모델은 `pydantic.BaseModel` 기반, `model_config = ConfigDict(extra="forbid")`로 알 수
  없는 필드 유입을 즉시 실패시킨다 (콘텐츠 데이터 오타를 조용히 무시하지 않기 위함).
- 외부 I/O(파일/네트워크 접근)를 이 모듈에서 수행하지 않는다 — 순수 데이터 정의만 둔다.

## 변경 시 체크리스트
- [ ] 기존 필드 제거/타입 변경 시 다른 모듈의 테스트가 깨지는지 `make verify`로 확인
- [ ] 새 필드 추가 시 기본값을 지정하거나, 모든 데이터 소스(`data/*.yaml`)를 함께 갱신
