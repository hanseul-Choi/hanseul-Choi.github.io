# HISTORY — renderer

## 2026-08-05 — 초기 구현
- `create_environment`, `render_page` 최초 작성. autoescape 기본 활성화.
- 후속 작업: 프로젝트 카드 외에 갤러리/타임라인 등 추가 컴포넌트가 필요해지면 이 문서에 기록.

## 2026-08-05 — 디자인 패스: 필터/글로벌 추가
- `initials` 필터 추가 (히어로 아바타 placeholder용, 이름 → 1~2글자).
- `build_year` 글로벌 추가 (footer 저작권 연도, 매 렌더 시점에 계산되는 callable — 빌드 시점에 고정된
  값이 아님. `serve`처럼 오래 떠 있는 프로세스가 연도 경계를 넘어도 stale 값이 안 나오게 하려는 의도).
