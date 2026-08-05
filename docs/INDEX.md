# Project-wide Change Index

프로젝트 전체 또는 여러 모듈에 영향을 주는 중요한 작업을 시간순으로 기록한다 (AGENTS.md 규칙 6).
각 항목: 날짜, 요약, 영향받은 모듈, 관련 ADR/PR.

## 2026-08-05
- Python 기반 커스텀 정적 사이트 빌더(하네스) 초기 골격 구축. 모듈 구조(`contracts`,
  `content_loader`, `renderer`, `link_checker`, `site_builder`)와 검증 하네스(`make verify`) 구축.
  영향: 저장소 전체.
- 디자인 시스템 적용(라이트/다크, sticky nav, 히어로, 프로젝트 카드) + 콘텐츠 구조 확장: Home에
  소개 섹션 직접 노출, `Project.achievements`(성과 불릿), 프로젝트별 상세 페이지(`/projects/<slug>/`,
  구조도 이미지 지원). `link_checker`의 `data:` URI 오처리 버그도 이 과정에서 발견해 수정.
  영향: `contracts`, `content_loader`(재사용), `renderer`, `link_checker`, `site_builder`, 전체 템플릿/CSS.
