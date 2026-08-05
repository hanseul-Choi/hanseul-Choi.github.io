# Project History

버그 수정 및 기능 수정 시 참고해야 하는 프로젝트 전체 이력 (AGENTS.md 규칙 4, 7). 모듈 내부의
세부 이력은 `src/sitebuilder/<module>/docs/HISTORY.md`를 참고한다.

## 2026-08-05 — 저장소 재출발
- **무엇**: minimal-mistakes 테마 원본(Rakefile, gemspec, docs/, test/, _includes/_layouts/_sass/assets,
  업스트림 전용 .github 워크플로 등) 전량 삭제. Jekyll을 완전히 걷어내고 Python(Jinja2 기반) 커스텀
  빌더로 전환.
- **왜**: 기존 저장소가 개인 사이트가 아니라 테마 자체의 소스코드였음 (플레이스홀더 미설정,
  업스트림 전용 CI 포함). 사용자가 harness engineering(모듈화된 빌드/테스트/CI 하니스) 학습·연습
  목적으로 Python 스택 전환을 요청.
- **위험/후속 작업**: 실제 프로젝트 소개 콘텐츠(`data/projects.yaml`)는 아직 비어 있음 — 문서
  전달 후 채워야 함. 사이트 메타(`data/site.yaml`)의 이름/소개/소셜 링크도 placeholder 상태.
