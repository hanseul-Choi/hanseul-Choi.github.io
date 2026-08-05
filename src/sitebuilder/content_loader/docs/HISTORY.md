# HISTORY — content_loader

## 2026-08-05 — 초기 구현
- `load_navigation`, `load_projects`, `load_site_config`, `load_pages` 최초 작성.
- 경로 순회 방지 로직과 `yaml.safe_load` 사용을 THREAT_MODEL.md에 따라 처음부터 적용.
- 후속 작업: 실제 프로젝트 문서 수령 후 `data/projects.yaml` 채우면서 스키마 필드 부족 여부 재검토.

## 2026-08-05 — 콘텐츠 패스: load_pages()를 프로젝트 상세 콘텐츠에 재사용
- 새 로더 함수를 추가하지 않고, 기존 `load_pages(content_dir)`를 `content/projects/`에도 그대로
  호출해서 프로젝트별 장문 설명(구조도 등)을 읽음. "디렉터리의 마크다운 파일들을 읽는다"는 이 함수의
  책임이 이미 재사용 가능한 수준으로 일반적이었기 때문 — 매칭(어떤 파일이 어떤 프로젝트에 대응하는지)은
  이 모듈의 일이 아니라 `site_builder`(App Shell)의 일로 남김.
