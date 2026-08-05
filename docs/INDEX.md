# Project-wide Change Index

프로젝트 전체 또는 여러 모듈에 영향을 주는 중요한 작업을 시간순으로 기록한다 (AGENTS.md 규칙 6).
각 항목: 날짜, 요약, 영향받은 모듈, 관련 ADR/PR.

## 2026-08-05
- 기존 minimal-mistakes Jekyll 테마 소스를 전량 제거하고, Python 기반 커스텀 정적 사이트
  빌더(하니스)로 전환. 모듈 구조(`contracts`, `content_loader`, `renderer`, `link_checker`,
  `site_builder`)와 검증 하니스(`make verify`) 초기 골격 구축.
  영향: 저장소 전체. 관련: `docs/adr/0001-python-jinja2-harness.md`.
