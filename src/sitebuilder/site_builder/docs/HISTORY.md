# HISTORY — site_builder

## 2026-08-05 — 초기 구현
- `pipeline.build_site`와 Typer CLI(`build`, `serve`) 최초 작성.
- `serve`는 `http.server` 기반 단순 정적 서버 (live reload 없음) — 향후 필요 시 watchdog 기반
  자동 리빌드 추가 예정 (지금은 범위 밖으로 명시적으로 제외).
- **버그 발견 (테스트로 잡음)**: `build` CLI 명령이 `project_root`를 `REPO_ROOT` 상수로 하드코딩해서
  `pipeline.build_site`에 전달하고 있었음 — output-dir 가드(THREAT_MODEL.md #1)가 저장소 밖의
  모든 output_dir을 무조건 거부해버려서, CliRunner로 임시 디렉터리를 가리키는 정상적인 테스트조차
  실패했다. `--project-root` 옵션을 추가해 호출자가 명시적으로 override할 수 있게 수정
  (기본값은 그대로 `REPO_ROOT`라 실제 배포 동작은 변하지 않음). AGENTS.md 규칙 5(실패 테스트 먼저
  작성)가 실제로 설계 결함을 잡아낸 사례.

## 2026-08-05 — 디자인 패스: 홈 페이지 라우팅 분리
- `build_site`에서 `slug == "index"`인 페이지는 `page.html`이 아니라 `home.html`(히어로 + featured
  projects)로 렌더링하도록 분기. `featured_projects=projects[:3]`을 컨텍스트에 추가.
- 모든 페이지 렌더링에 `current_path`를 추가로 넘겨서 nav의 활성 링크 표시(`is-active`)를 지원.

## 2026-08-05 — 콘텐츠 패스: 프로젝트 상세 페이지
- `build_site`에 `project_content_dir` 필수 인자 추가. `content_loader.load_pages(project_content_dir)`로
  읽은 결과를 slug 기준으로 `Project`와 매칭해서, 매칭되는 프로젝트마다 `/projects/<slug>/`에
  `project_detail.html`로 상세 페이지를 생성. 매칭되는 마크다운 파일이 없는 프로젝트는 조용히 건너뜀
  (상세 페이지도, "자세히 보기" 링크도 안 생김 — 에러 아님, 의도된 동작).
- `detail_slugs`(상세 페이지가 있는 slug 집합)를 홈/프로젝트 목록 렌더링 컨텍스트에 넘겨서
  `project_card.html`이 "자세히 보기" 링크를 조건부로 표시하도록 함.
- CLI(`build`)에 `--project-content-dir` 옵션 추가 (기본값 `content/projects/`).
