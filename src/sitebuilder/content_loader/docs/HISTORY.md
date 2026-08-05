# HISTORY — content_loader

## 2026-08-05 — 초기 구현
- `load_navigation`, `load_projects`, `load_site_config`, `load_pages` 최초 작성.
- 경로 순회 방지 로직과 `yaml.safe_load` 사용을 THREAT_MODEL.md에 따라 처음부터 적용.
- 후속 작업: 실제 프로젝트 문서 수령 후 `data/projects.yaml` 채우면서 스키마 필드 부족 여부 재검토.
