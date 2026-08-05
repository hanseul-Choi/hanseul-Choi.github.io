# HISTORY — contracts

## 2026-08-05 — 초기 계약 정의
- `SiteConfig`, `NavItem`, `Project`, `PageContent` Pydantic 모델 최초 작성.
- 위험 요소: 아직 실제 프로젝트 데이터가 없어 스키마가 실제 콘텐츠로 검증되지 않음. 문서 전달 후
  `data/projects.yaml`을 채울 때 스키마 부족(예: 이미지, 기간, 역할 필드 누락)이 드러날 수 있음.

## 2026-08-05 — 디자인 패스: Project.image_url 추가
- `Project`에 `image_url: str | None = None` 추가. 값이 없으면 프로젝트 카드가 CSS 그라디언트 +
  아이콘 placeholder로 대체 렌더링됨 (`templates/components/project_card.html`). 실제 스크린샷이
  생기면 이 필드만 채우면 됨 — 예상대로 아직 예측했던 "이미지 필드 누락" 갭이 실제로 드러남.

## 2026-08-05 — 콘텐츠 패스: Project.achievements 추가
- `Project`에 `achievements: list[str] = []` 추가 (성과/지표 불릿 리스트, 예: "응답속도 200ms→80ms
  단축"). 카드와 상세 페이지 양쪽에 체크마크 리스트로 렌더링. `PageContent`는 변경 없음 — 프로젝트
  상세 설명(구조도 등 장문 콘텐츠)은 `content_loader.load_pages()`를 `content/projects/`에 재사용해
  얻은 `PageContent`를 `site_builder.pipeline`에서 `Project`와 slug로 매칭해 합성 (계약 자체는 안 늘림).
