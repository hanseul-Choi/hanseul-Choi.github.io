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

## 2026-08-05 — 디자인 패스 + 콘텐츠 구조 확장
- **무엇**: 미니멀/뉴트럴 디자인 시스템 적용(라이트+다크 자동, sticky nav, 히어로, 프로젝트 카드,
  인라인 SVG 아이콘). 이어서 사용자 피드백 반영: Home에 "소개" 섹션을 직접 노출, `Project.achievements`
  (성과 불릿) 추가, 프로젝트별 상세 페이지(`/projects/<slug>/`, `content/projects/*.md` 기반, 구조도
  이미지 등 장문 콘텐츠 지원) 신설.
- **왜**: "Home에 나에 대한 게 보이면 좋겠다", "성과 항목 필요", "상세 페이지에 구조도" 요청.
- **버그 발견 (실제 빌드 중 잡음)**: `link_checker`가 `data:` URI를 내부 경로로 오인해 `OSError:
  File name too long`으로 빌드가 죽는 문제 발견 (구조도 이미지를 data URI로 데모하다 발견). 스킴
  allowlist를 "스킴이 있으면 무조건 외부"로 일반화해서 근본 수정 (`src/sitebuilder/link_checker/docs/HISTORY.md`).
- **위험/후속 작업**: 더미 프로젝트/구조도는 Artifact 미리보기로만 확인했고 실제 `data/`, `content/`는
  건드리지 않음. 실제 콘텐츠 반영은 프로젝트 문서 수령 후.
