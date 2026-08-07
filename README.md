# hanseul-Choi.github.io

개인 포트폴리오 사이트. **Live: https://hanseul-Choi.github.io**

## 이 저장소는 무엇인가

**Python + Jinja2**로 만든 모듈화된 정적 사이트 빌더로 포트폴리오를 빌드합니다. 콘텐츠(`content/`,
`data/`)와 템플릿(`templates/`)을 조합해 `dist/`에 정적 HTML을 생성하고, GitHub Actions가 빌드한
뒤 결과물(`dist/`)만 GitHub Pages에 배포합니다. `dist/`는 빌드 산출물이라 git에 커밋하지 않습니다
(`.gitignore` 참고).

저장소 작업 규칙(테스트 우선, 모듈 경계, 검증 게이트 등)은 [`AGENTS.md`](AGENTS.md)에 있습니다.

## 디렉터리 구조

```
.
├── src/sitebuilder/  # 사이트 빌더 본체 (아래 "모듈 구조" 참고)
├── content/
│   ├── pages/        # 정적 페이지 콘텐츠 (index.md, about.md, contact.md)
│   └── projects/     # 프로젝트 상세 콘텐츠 (Markdown, 프로젝트별 1파일)
├── data/
│   ├── site.yaml       # 사이트 제목/소개 등 메타 정보
│   ├── navigation.yaml  # 상단 내비게이션 항목
│   └── projects.yaml   # 프로젝트 목록/요약/성과 불릿 (홈·프로젝트 카드에 쓰임)
├── templates/        # Jinja2 템플릿 (base.html, home.html, project_detail.html 등)
├── static/           # CSS/JS/이미지 등 정적 자산 (빌드 시 dist/static/으로 복사)
├── tests/            # src/sitebuilder/ 각 모듈에 대응하는 pytest 스위트
├── docs/             # 저장소 전반 문서 (HISTORY, INDEX, architecture 개요)
└── dist/             # 빌드 산출물 (gitignore, `make build`로 생성)
```

콘텐츠 수정은 `content/pages/*.md`(Markdown + frontmatter)와 `data/*.yaml`(내비게이션/프로젝트/
사이트 메타)에서 합니다. 화면 구조를 바꾸려면 `templates/`, 스타일은 `static/css/main.css`를 만집니다.

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

## CI/CD

`.github/workflows/ci.yml`이 push/PR마다 `quality`(lint+typecheck+imports+test) →
`build`(사이트 빌드) → `deploy`(GitHub Pages 배포, `master` push에서만) 순서로 실행됩니다.
