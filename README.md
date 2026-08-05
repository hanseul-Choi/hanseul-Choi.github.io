# hanseul-Choi.github.io

개인 포트폴리오 사이트. **Live: https://hanseul-Choi.github.io**

> 사이트 제목/소개/프로젝트 내용은 아직 placeholder입니다 (`data/site.yaml`, `data/projects.yaml`,
> `content/pages/about.md` 참고). 프로젝트 소개 문서를 받으면 채워질 예정입니다.

## 이 저장소는 무엇인가

Jekyll 테마를 쓰는 대신, **Python + Jinja2로 직접 만든 작은 정적 사이트 빌더("하니스")**로
포트폴리오를 빌드합니다. GitHub Pages는 Python 빌드를 네이티브 지원하지 않으므로, GitHub
Actions가 이 빌더로 사이트를 빌드한 뒤 결과물(`dist/`)만 GitHub Pages에 배포합니다.

이 선택의 배경은 [`docs/adr/0001-python-jinja2-harness.md`](docs/adr/0001-python-jinja2-harness.md)에,
저장소 작업 규칙(테스트 우선, 모듈 경계, 검증 게이트 등)은 [`AGENTS.md`](AGENTS.md)에 있습니다.

## 모듈 구조

```
src/sitebuilder/
├── contracts/       # 공유 Pydantic 모델 (Project, NavItem, SiteConfig, PageContent)
├── content_loader/  # data/*.yaml, content/pages/*.md 읽고 검증
├── renderer/        # Jinja2 렌더링 (templates/)
├── link_checker/    # 빌드 결과물의 깨진 링크 / alt 텍스트 오프라인 검사
└── site_builder/    # App Shell — 위 네 모듈을 조립, CLI(build/serve) 제공
```

각 모듈은 자신의 `docs/POLICY.md`(+`THREAT_MODEL.md`, `HISTORY.md`)를 가지고 있고, 모듈 간
경계는 `import-linter`로 자동 강제됩니다. 자세한 그림은
[`docs/architecture/harness-overview.md`](docs/architecture/harness-overview.md) 참고.

## 로컬 개발

의존성 관리는 [`uv`](https://docs.astral.sh/uv/)를 사용합니다.

```bash
make install     # .venv 생성 + 의존성 설치
make build        # 사이트를 dist/ 로 빌드
make serve        # dist/ 를 http://127.0.0.1:8000 에서 미리보기
```

콘텐츠 수정은 `content/pages/*.md`(Markdown + frontmatter), `data/*.yaml`(내비게이션/프로젝트/
사이트 메타)에서 합니다. 템플릿은 `templates/`.

## 테스트 & 검증

기능 추가/수정 후에는 항상 아래를 실행합니다 (AGENTS.md 규칙 13).

```bash
make verify
```

`make verify`는 다음을 순서대로 실행합니다:

| 단계 | 도구 | 확인 내용 |
|---|---|---|
| lint | `ruff check` / `ruff format --check` | 코드 스타일 |
| typecheck | `mypy --strict` | 타입 정확성 |
| imports | `import-linter` | 모듈 간 의존 경계 (contracts만 공유, 서로 직접 참조 금지) |
| test | `pytest --cov` (커버리지 90% 미만 시 실패) | 유닛 테스트 |
| build | `python -m sitebuilder build` | 실제 빌드 + 링크/alt 검사 통과 여부 |

개별 명령은 `make lint`, `make typecheck`, `make imports`, `make test`로 따로 실행할 수 있습니다.
커밋 전 자동 실행을 원하면 `pre-commit install`로 `.pre-commit-config.yaml`을 활성화하세요.

현재 테스트는 77개, 커버리지 95%입니다 (`make verify`로 직접 재현 가능).

## CI/CD

`.github/workflows/ci.yml`이 push/PR마다 `quality`(lint+typecheck+imports+test) →
`build`(사이트 빌드) → `deploy`(GitHub Pages 배포, `master` push에서만) 순서로 실행됩니다.

## 프로젝트 소개

_TODO: 프로젝트 소개 문서를 받으면 이 섹션과 `data/projects.yaml`을 채웁니다._
