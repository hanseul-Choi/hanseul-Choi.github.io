# Harness Overview

## 모듈 다이어그램

```
                    ┌─────────────────────┐
                    │   site_builder       │   ← App Shell (유일하게 다른 모듈을 조립)
                    │   (CLI: build/serve) │
                    └──────────┬───────────┘
                               │ 조립
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐     ┌────────────────┐     ┌────────────────┐
│ content_loader │     │   renderer     │     │  link_checker   │
│ (data/*.yaml,  │     │ (Jinja2 엔진,  │     │ (빌드 결과물의  │
│  content/*.md  │     │  templates/)   │     │  내부 링크/     │
│  → 검증된 객체)│     │                │     │  alt 텍스트 검사)│
└───────┬────────┘     └───────┬────────┘     └────────┬────────┘
        │                      │                        │
        └──────────────┬───────┴────────────────────────┘
                        ▼
              ┌───────────────────┐
              │     contracts     │   ← 공유 Pydantic 모델 (Project, NavItem, SiteConfig ...)
              │  (모든 모듈이 의존 │      다른 기능 모듈은 서로 직접 의존하지 않음
              │   가능한 유일한    │
              │   공유 표면)       │
              └───────────────────┘
```

## 규칙

- `content_loader`, `renderer`, `link_checker`는 서로를 import하지 않는다. 공유가 필요하면
  `contracts`에 모델/타입을 추가한다.
- `site_builder`만 나머지 네 모듈을 모두 import해서 파이프라인을 조립한다.
- 각 모듈은 자신의 최상위 `__init__.py`에서 공개할 이름만 export한다. 다른 모듈은
  `from sitebuilder.renderer import render_page`처럼 공개 API만 import하고,
  `from sitebuilder.renderer.engine import _internal_fn`처럼 내부 파일을 직접 import하지 않는다.
  이 규칙은 `import-linter`(`pyproject.toml`의 `[tool.importlinter]`)로 자동 검증된다.

## 빌드 파이프라인 (site_builder.pipeline.build_site)

1. `content_loader`로 `data/navigation.yaml`, `data/projects.yaml`, `content/pages/*.md`를 읽고
   Pydantic 모델로 검증.
2. `renderer`로 각 페이지를 `templates/*.html` + Jinja2 컴포넌트(`templates/components/`)로 렌더링.
3. 정적 자원(`static/`)을 출력 디렉터리로 복사.
4. `link_checker`로 출력 디렉터리를 스캔해 내부 링크 깨짐/이미지 alt 누락을 검사.
5. 하나라도 실패하면 0이 아닌 종료 코드로 빌드 실패.

## 검증 하니스 (`make verify`)

```
ruff check .        # 린트
ruff format --check # 포맷 검사
mypy src            # strict 타입 체크
lint-imports         # import-linter, 모듈 경계 강제
pytest --cov         # 유닛 테스트 + 커버리지
python -m sitebuilder build --strict   # 실제 빌드 + link_checker 통과 확인
```
