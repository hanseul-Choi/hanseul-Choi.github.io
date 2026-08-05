# POLICY — site_builder (App Shell)

## 역할
`content_loader`, `renderer`, `link_checker`를 조립해 전체 빌드 파이프라인을 실행하고,
Typer 기반 CLI(`build`, `serve`)를 노출한다. AGENTS.md 규칙 25에 따라 다른 기능 모듈을
모두 import할 수 있는 유일한 모듈이다.

## 규칙
- `content_loader`, `renderer`, `link_checker`, `contracts`의 공개 API(`__init__.py`)만
  import한다. 각 모듈의 내부 서브모듈을 직접 import하지 않는다.
- 출력 디렉터리 쓰기는 명시적으로 허용된 경로(`--output` 인자, 기본값 `dist/`)로 제한한다.
  상위 디렉터리(`..`)로 벗어나는 출력 경로는 거부한다 (default-deny + 경로 검증).
- `serve` 명령은 로컬 개발 전용이며 기본적으로 `127.0.0.1`에만 바인딩한다. `0.0.0.0` 바인딩은
  명시적 플래그 없이는 허용하지 않는다.
- 빌드 실패(콘텐츠 검증 실패, 링크 검사 실패)는 항상 0이 아닌 종료 코드를 반환한다 — CI가
  실패를 놓치지 않도록.

## 변경 시 체크리스트
- [ ] 파이프라인 단계를 추가/변경하면 `pipeline.py`의 각 단계별 실패 시 종료 코드/에러 메시지
      테스트 추가
- [ ] CLI 인자를 추가하면 `--help` 출력과 계약 테스트를 함께 갱신
