# ADR 0001: Python + Jinja2 커스텀 빌더로 포트폴리오 사이트 구축

- 상태: 채택됨
- 날짜: 2026-08-05

## 배경

`hanseul-Choi.github.io`는 원래 minimal-mistakes Jekyll 테마의 소스코드 원본이 그대로 들어와
있던 저장소였다 (개인 콘텐츠 없음, 업스트림 전용 CI 포함). 이를 개인 포트폴리오로 개발하며,
사용자는 다음을 요구했다:

- 기능 개발 시 상세한 테스트 코드
- 기술 스택은 가능하면 Python/Kotlin/Java (그 외 언어 사용 시 상세 설명)
- "harness engineering" 연습 — 모듈화된 빌드/테스트/CI 하니스 구축

## 검토한 대안

1. **Jekyll 유지 + minimal-mistakes 커스터마이징 + `remote_theme` 전환**
   - 장점: GitHub Pages 네이티브 빌드, 설정 최소화.
   - 단점: Ruby/Liquid 기반이라 지침의 언어 선호와 어긋나고, 우리가 직접 짜는 코드가 적어
     harness engineering 목적에 맞지 않음.
2. **MkDocs + Material 테마**
   - 장점: 성숙한 Python 도구, 빠른 구축.
   - 단점: 설정/콘텐츠 중심이라 우리가 설계하는 모듈화 코드가 거의 없음.
3. **Pelican**
   - 장점: Python 블로그 생성기, Jinja2 템플릿.
   - 단점: 블로그 중심 구조라 포트폴리오 커스터마이징에 추가 우회가 필요.
4. **커스텀 Jinja2 기반 Python 정적 사이트 빌더 (채택)**
   - 장점: 모듈 경계, 계약(Pydantic), 테스트 하니스를 전부 직접 설계 가능. harness engineering
     목적에 가장 부합. 모듈화 요구사항을 코드 구조로 직접 만족.
   - 단점: 우리가 유지보수해야 하는 코드량이 가장 많음.

## 결정

4번(커스텀 Jinja2 기반 Python 빌더)을 채택한다. GitHub Pages는 Python 빌드를 네이티브
지원하지 않으므로, GitHub Actions에서 `make verify`(품질 게이트) 통과 후 빌드 산출물을
`actions/upload-pages-artifact` + `actions/deploy-pages`로 배포한다.

## 결과

- 저장소에서 Jekyll/Ruby 관련 파일을 전량 제거.
- `src/sitebuilder/` 아래 `contracts`, `content_loader`, `renderer`, `link_checker`,
  `site_builder`(App Shell) 모듈로 구성.
- 모듈 간 의존은 각 모듈의 공개 API(`__init__.py`) 또는 `contracts`의 공유 모델을 통해서만
  허용하며 `import-linter`로 강제.
- 단일 검증 진입점 `make verify` (ruff, mypy strict, import-linter, pytest --cov, 사이트 빌드).
