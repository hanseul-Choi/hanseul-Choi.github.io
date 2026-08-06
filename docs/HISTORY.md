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

## 2026-08-06 — 장애: GitHub Pages가 legacy Jekyll 자동 빌드와 경합
- **증상**: "내용이 다 사라지고 디자인도 이상하다"는 사용자 신고. 라이브 사이트가 우리 빌더가 만든
  페이지가 아니라 README.md를 GitHub 기본 Jekyll 테마로 렌더링한 페이지("Hanlien")로 나오고 있었음.
- **원인**: 저장소의 GitHub Pages 설정이 `build_type: legacy`(브랜치에서 자동 Jekyll 빌드)로 남아
  있었음 — PR #1에서 `remote_theme`/Jekyll을 걷어내고 GitHub Actions(`actions/deploy-pages`)
  배포로 전환했을 때, 저장소 Settings의 Pages Source를 "GitHub Actions"로 바꾸는 걸 놓침.
  그 결과 push마다 우리 워크플로(`verify-and-deploy`)와 GitHub의 자동 Jekyll 빌드
  (`pages-build-deployment`)가 **동시에** 같은 Pages에 배포를 시도했고, 매번 나중에 끝나는 쪽이
  이겼다 — 그동안은 운 좋게 우리 배포가 나중에 끝나서 정상으로 보였을 뿐, 처음부터 경쟁 상태였음.
- **수정**: `gh api -X PUT repos/.../pages -f build_type=workflow`로 Pages Source를 GitHub
  Actions 전용으로 전환해 legacy 자동 빌드 자체를 껐다. 이후 이 커밋을 `master`에 바로 push해
  실제 배포를 다시 트리거함 (참고: `deploy` job은 `github.event_name == 'push'` 조건이라
  `workflow_dispatch`로는 안 돎 — 그래서 커밋 push가 필요했음).
- **위험/후속 작업**: 이 경합 상태는 처음부터 있었고 우연히 지금까지 안 드러났을 뿐임 — 앞으로
  push 직후엔 라이브를 다시 확인하는 습관이 필요. `verify-and-deploy` 워크플로의 `deploy` job
  조건을 `workflow_dispatch`에서도 동작하도록 완화하면 이런 상황에서 수동 재배포가 더 쉬워짐
  (지금은 이 문서 커밋처럼 실제 push가 있어야만 함) — 후속 개선 후보.

## 2026-08-06 — 모바일 여백/레이아웃 개선
- **무엇**: "모바일에서 여백이 없어보여" 피드백 반영. `.wrap` 기본 좌우 패딩을 1.25rem→1.5rem로
  키워 화면 가장자리 여백을 더 확보. `max-width: 40rem` 반응형 구간을 새로 추가해 히어로/섹션/
  페이지의 세로 패딩과 모달 내부 패딩을 화면 폭에 맞게 줄이고(바깥 여백은 그대로 두고 내부만
  압축), 프로젝트 그리드를 1열로 강제, 다크모드 토글·버튼류 탭 타겟을 ~44px로 키움.
- **왜**: 이 세션에는 실제 모바일 기기/브라우저 도구가 없어 코드 리뷰로만 원인을 짚었음 —
  `.wrap` 패딩 자체는 존재했고 어떤 템플릿도 wrap 없이 렌더링되지 않는 걸 확인했지만, 정확한
  시각적 확인은 못 함.
- **위험/후속 작업**: 사용자가 실제 기기에서 재확인 필요. 여전히 이상해 보이면 스크린샷과 함께
  다시 알려달라고 요청함.

## 2026-08-06 — 정적 자산 캐시 무효화
- **무엇**: 모바일 여백 수정을 배포했는데도 사용자에게 예전 스타일이 계속 보인다는 후속 신고.
  서버 응답은 이미 새 CSS였어서(curl로 확인) 브라우저/CDN 캐시가 원인으로 강하게 의심됨 —
  `/static/css/main.css`, `/static/js/theme-toggle.js`를 캐시 무효화 장치 없이 고정 경로로
  서빙하고 있었음. `static/` 전체를 해시해서 `?v=<hash>` 쿼리스트링을 자동으로 붙이도록 수정
  (`src/sitebuilder/site_builder/docs/HISTORY.md` 참고).
- **왜**: 정적 사이트에서 CSS/JS 변경이 배포 직후 반영 안 되는 건 흔한 함정인데 처음 설계에서
  놓쳤음. 사용자에게는 우선 강력 새로고침으로 확인해달라고 안내하고, 근본 수정을 병행함.
