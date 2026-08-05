# HISTORY — contracts

## 2026-08-05 — 초기 계약 정의
- `SiteConfig`, `NavItem`, `Project`, `PageContent` Pydantic 모델 최초 작성.
- 위험 요소: 아직 실제 프로젝트 데이터가 없어 스키마가 실제 콘텐츠로 검증되지 않음. 문서 전달 후
  `data/projects.yaml`을 채울 때 스키마 부족(예: 이미지, 기간, 역할 필드 누락)이 드러날 수 있음.
