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

## 2026-08-06 — 프로젝트 상세를 모달로도 열람 가능하게
- Home/프로젝트 목록 렌더링 컨텍스트에 `project_details`(slug → PageContent 전체 dict)를 추가로
  넘김. `project_card.html`이 이걸로 각 프로젝트의 `detail`을 직접 조회해서, "자세히 보기" 링크가
  `/projects/<slug>/` 대신 같은 페이지 안의 `#project-modal-<slug>` 앵커를 가리키고, 카드 바로
  뒤에 풀 detail 본문을 담은 모달(`:target` 기반 순수 CSS)을 렌더링하도록 확장.
- `/projects/<slug>/` 전용 페이지는 그대로 유지 — 모달 안에 "전체 페이지에서 보기" 링크로 연결
  (직접 링크 공유·SEO 목적).
- 모달 안에서는 구조도 이미지에 `lightbox_images`를 적용하지 않음 — 둘 다 URL 프래그먼트(`:target`)
  기반이라, 모달 안에서 라이트박스를 열면 그 프래그먼트가 모달의 것과 달라져 모달 자체가 닫혀버리는
  충돌이 생김. 전체 페이지(`project_detail.html`)에서만 라이트박스 사용.

## 2026-08-06 — 정적 자산 캐시 무효화 (`?v=` 쿼리스트링)
- **왜**: 모바일 여백 CSS를 고쳐서 배포했는데 사용자에게는 여전히 예전 스타일로 보인다는 신고.
  서버 응답(curl)은 이미 새 CSS였음 — 브라우저/CDN이 `/static/css/main.css`를 캐시 무효화 장치
  없이 그대로 캐싱하고 있었을 가능성이 큼.
- **무엇**: `_compute_asset_version(static_dir)` 추가 — `static/` 전체 파일을 sha256으로 훑어
  10자리 해시 하나를 만듦. `build_site`가 이 값을 계산해 **모든** `render_page` 호출(page/home
  루프, projects.html, project_detail.html 루프)에 `asset_version`으로 넘기고, `base.html`의
  `<link rel="stylesheet">`/`<script src>`에 `?v={{ asset_version }}`을 붙임. 정적 파일 내용이
  바뀌면 해시도 바뀌어서 브라우저가 새 URL로 인식 → 캐시 무효화.
- **테스트 안전장치**: 테스트 fixture의 `_BASE_TEMPLATE`에도 실제 템플릿처럼 `{{ asset_version }}`
  참조를 넣어둠 — `StrictUndefined`라서, 앞으로 누군가 `render_page` 호출부 중 하나에 이 인자를
  빼먹으면(예: 새 페이지 타입 추가 시) 그 즉시 테스트가 실패함.
- **위험/후속 작업**: `link_checker`가 `?v=...` 쿼리스트링이 붙은 경로도 정상적으로 검증하는지
  이번에 실제로 확인됨(`urlparse`가 쿼리를 분리해주는 덕분에 기존 코드 변경 없이 그대로 동작).
