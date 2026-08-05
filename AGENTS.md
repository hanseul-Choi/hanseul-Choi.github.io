# Portfolio Site — Agent & Contributor Rules

이 문서는 Codex, Claude Code, Gemini CLI 및 사람이 이 저장소에서 함께 작업할 때 지키는 공유 규칙이다.
이 저장소는 Python 기반 커스텀 정적 사이트 빌더(하네스)로, `src/sitebuilder/` 아래 기능 모듈로
나뉘어 있다. 모듈 구조는 `docs/architecture/harness-overview.md`를 참고한다.

1. 작업 전 항상 `README.md`, 관련 ADR(`docs/adr/`), 대상 모듈의 `docs/POLICY.md`(있다면 `docs/THREAT_MODEL.md`),
   그리고 제공된 Issue/티켓 컨텍스트를 읽는다.
2. Issue가 제공되면 구현 전에 Acceptance Criteria를 먼저 추출한다.
3. `src/sitebuilder/<module>/`를 수정할 때는 항상 `src/sitebuilder/<module>/docs/POLICY.md`,
   (존재한다면) `src/sitebuilder/<module>/docs/THREAT_MODEL.md`를 함께 읽는다.
4. 버그 수정 및 기능 수정을 진행할 때는 `docs/HISTORY.md`, `src/sitebuilder/<module>/docs/HISTORY.md`를 함께 읽는다.
5. 변경할 동작을 재현하는 실패 테스트를 먼저 상세하게 작성하고 실패를 확인한 뒤 구현한다 (TDD).
6. 프로젝트 전체 또는 여러 모듈에 영향을 주는 중요한 작업은 `docs/INDEX.md`에 기록한다.
7. 모듈 내부의 중요한 동작 변경, 위험 요소, 후속 작업은 `src/sitebuilder/<module>/docs/HISTORY.md`에 기록한다.
8. 문서 간 규칙이 충돌하는 경우 더 구체적이고 더 엄격한 규칙을 따른다. 하위 문서(모듈 `docs/POLICY.md`)는
   상위 규칙(이 문서)을 완화하거나 무효화할 수 없다.
9. 필수 문서가 존재하지 않거나 현재 작업과 불일치하는 경우 이를 임의로 추정하지 않고 결과 보고에
   누락 또는 불일치를 기록한다.
10. 기능 모듈(`content_loader`, `renderer`, `link_checker`, `site_builder`) 간 직접 의존을 만들지 않는다.
    다른 모듈의 내부 서브모듈을 import하지 않고, 각 모듈 최상위 `__init__.py`(공개 API) 또는
    `src/sitebuilder/contracts/`의 공유 모델만 사용한다. 이 규칙은 `import-linter` 계약으로
    자동 강제되며 `make verify`에 포함된다.
11. 신규 데이터 계약(콘텐츠 스키마, CLI 인터페이스, 모듈 간 인터페이스)에는 Pydantic 모델, 명시적
    에러 타입, 그리고 pytest 계약 테스트를 함께 추가한다.
12. 신규 파일 접근/외부 명령 실행/외부 네트워크 요청 기능은 기본 거부(default-deny) + allowlist를
    적용한다 (예: `link_checker`의 외부 URL 검사 대상 도메인, `site_builder`가 쓰기 가능한 출력 경로).
13. 코드 변경 후 반드시 `make verify`(ruff + mypy strict + import-linter + pytest --cov + 사이트 빌드)를
    실행한다.
14. 실행하지 못한 검증은 완료했다고 보고하지 않는다.
15. 변경 범위 밖의 리팩터링을 하지 않는다.
16. 새 production dependency를 추가하면 선택 이유와 보안/설치크기 영향을 결과 보고에 기록한다.
17. 테스트 삭제·skip·커버리지 임계치 하향은 사용자 승인 없이 금지한다.
18. 생성 코드라도 개발자가 빠르게 이해할 수 있는 명시적이고 작은 경계(작은 함수, 명확한 타입 힌트)를 우선한다.
19. Token, password, private key, passphrase, 실제 개인 연락처/사내 정보를 코드·로그·문서에 기록하지 않는다.
20. `Any` 타입, `# type: ignore`, 근거 없이 예외를 삼키는 `except Exception: pass`를 사용하지 않는다.
    mypy strict 모드로 강제한다.
21. 하위 `src/sitebuilder/<module>/docs/POLICY.md`는 이 루트 문서를 보충하는 더 엄격한 지역 규칙만
    추가할 수 있으며, 루트 규칙을 완화하거나 대체하지 않는다.
22. 둘 이상의 사람 또는 AI가 병렬 작업할 때 같은 branch/worktree나 같은 파일을 동시에 수정하지 않는다.
    수정 허용·금지 경로를 작업 컨텍스트에 기록한다.
23. 공유 계약(`src/sitebuilder/contracts/`, CLI 인터페이스)을 바꾸는 작업은 하위 모듈 구현 전에
    계약과 실패 테스트를 먼저 확정한다.
24. 작업을 넘길 때 base commit, 현재 diff, 변경된 계약/정책, 실행한 검증, 남은 작업과 blocker를 기록한다.
25. 모듈 공개 API는 각 모듈의 최상위 `__init__.py`로 제한한다. `site_builder`(App Shell)만 다른
    모든 기능 모듈을 조립할 수 있다.
26. 로컬 개발/빌드/테스트 실행 방법은 `README.md`, 설계 배경은 `docs/adr/`를 따른다.

## 이 저장소에서의 매핑 요약

| 원본 개념(Rust 예시) | 이 저장소 |
|---|---|
| `modules/<module>/docs/POLICY.md` | `src/sitebuilder/<module>/docs/POLICY.md` |
| `modules/<module>/docs/THREAT_MODEL.md` | `src/sitebuilder/<module>/docs/THREAT_MODEL.md` (해당 모듈에만) |
| `modules/<module>/docs/HISTORY.md` | `src/sitebuilder/<module>/docs/HISTORY.md` |
| `docs/INDEX.md`, `docs/HISTORY.md` | 동일 경로 |
| `packages/*` port / public API | `src/sitebuilder/contracts/` + 각 모듈 `__init__.py` |
| TypeScript/Rust contract | Pydantic 모델 + `typing.Protocol` |
| `pnpm verify` | `make verify` |
| App Shell | `site_builder` 모듈 |
| `any`/`@ts-ignore`/`unsafe` 금지 | `Any`/`# type: ignore`/무근거 예외 삼킴 금지 (mypy strict) |
