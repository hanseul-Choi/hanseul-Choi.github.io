# Project History

버그 수정 및 기능 수정 시 참고해야 하는 프로젝트 전체 이력 (AGENTS.md 규칙 4, 7). 모듈 내부의
세부 이력은 `src/sitebuilder/<module>/docs/HISTORY.md`를 참고한다.

## 2026-08-05 — 저장소 초기 골격
- **무엇**: Python(Jinja2 기반) 커스텀 정적 사이트 빌더로 저장소 구성. 모듈 구조(`contracts`,
  `content_loader`, `renderer`, `link_checker`, `site_builder`)와 검증 하네스(`make verify`) 구축.
- **왜**: harness engineering(모듈화된 빌드/테스트/CI 하네스) 학습·연습 목적.
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

## 2026-08-05 — 실제 콘텐츠 반영
- **무엇**: 사용자가 전달한 경력 문서로 `data/site.yaml`(이름 "최한슬", 소개, GitHub/LinkedIn/Email
  소셜 링크), `data/projects.yaml`(프로젝트 3개 + 성과), `content/pages/{index,about,contact}.md`,
  `content/projects/*.md`(프로젝트별 상세 — 인프라 구조/트러블슈팅) 전부 placeholder에서 실제 내용으로 교체.
- **왜**: 사용자가 LinkedIn 경력 내용을 전달하고 이름/이메일 공개 여부/LinkedIn URL을 확정.
- **위험/후속 작업**: 프로젝트 상세 페이지에는 아직 실제 스크린샷/구조도 이미지가 없음 (텍스트만).
  이미지 파일이 생기면 `data/projects.yaml`의 `image_url`과 각 상세 md의 이미지 삽입만 추가하면 됨.

## 2026-08-06 — 수동 다크모드 토글 (사이트 최초의 JS)
- **무엇**: `prefers-color-scheme` 자동 다크모드는 이미 있었으나, 시스템 설정과 무관하게 방문자가
  직접 라이트/다크를 고를 수 있는 토글 버튼 추가. `:root[data-theme="dark"|"light"]` 속성 선택자가
  미디어쿼리보다 우선하도록 CSS 토큰을 재구성하고, `static/js/theme-toggle.js`(클릭 시 속성 전환 +
  localStorage 저장)와 `<head>`의 동기 인라인 스크립트(첫 페인트 전에 저장된 값 적용, FOUC 방지)를 추가.
- **왜**: "다크모드로 구성해줄 수 있어?" 요청에 옵션 3개(토글 버튼/자동 유지+색만 조정/다크 전용)
  제시했고 사용자가 토글 버튼을 선택 — 페이지 이동 간 선택이 유지되려면 JS 없이는 불가능하다는 점을
  안내하고 진행.
- **위험/후속 작업**: 이 저장소의 다른 모든 인터랙션(nav, collapsible_h3, lightbox, 프로젝트 모달)은
  여전히 순수 CSS. 부수적으로 `link_checker`가 `<script src>`/`<link href>`를 전혀 검사하지 않던
  걸 발견해서 같은 PR에서 함께 고침 (`src/sitebuilder/link_checker/docs/HISTORY.md` 참고).

## 2026-08-06 — 기본 테마를 다크로 전환
- **무엇**: `:root` 기본 토큰 자체를 다크 값으로 바꾸고 `@media (prefers-color-scheme: dark)`
  블록을 제거. 이제 방문자의 시스템 설정과 무관하게 첫 방문은 항상 다크로 보이고, 토글로
  라이트를 명시적으로 선택했을 때만 밝게 바뀜. 토글 아이콘 로직과 `theme-toggle.js`의
  `currentTheme()`(시스템 선호도 분기 제거, "light가 아니면 dark"로 단순화)도 맞춰서 정리.
- **왜**: "default는 다크모드로 해줘" 요청.
