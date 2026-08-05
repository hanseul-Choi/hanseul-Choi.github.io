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
