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

## 2026-08-06 — 페이지 여백 재확대
- **무엇**: 캐시 무효화 이후에도 "변한 게 없다"는 신고 — 서버는 이미 최신인데 사용자 쪽엔 HTML
  자체가 캐시돼 있었을 가능성(시크릿 탭으로 확인 요청함)과 별개로, 이전 조정폭(1.25rem→1.5rem,
  4px)이 체감하기엔 너무 작았을 수 있어 `.wrap` 좌우 패딩을 1.75rem(28px)으로 한 번 더, 더 확실히
  키움.
- **왜**: "프로젝트 카드 시작점이 소개글 시작점과 같다"는 구체적 지적 — 둘 다 `.wrap`의 자식이라
  같은 여백을 공유하는 게 정상 구조이므로, 문제는 정렬 불일치가 아니라 그 공통 여백 자체가
  체감상 부족하다는 것으로 해석함.

## 2026-08-06 — 모바일 헤더 가로 오버플로우 (진짜 원인 발견)

- **증상**: 사용자가 "여백 문제가 아닌 것 같다"며 방향을 정정 — 개발자 도구로 모바일 화면을 보면
  "이상하게 보인다"고 재현 방법을 알려줌. 실제로 라이브 사이트를 헤드리스 Chrome으로 390px 폭
  스크린샷을 떠보니, 헤더 우측의 nav+다크모드 토글이 줄바꿈되지 않고 한 줄에 그대로 눌려 있었고
  "Contact" 글자와 프로젝트 카드가 화면 폭 밖으로 잘려 있었음 — **진짜 원인은 여백(`padding`)이
  아니라 `.header-right`(nav + 토글 버튼을 담는 flex 컨테이너)에 `flex-wrap`이 없어서 좁은 화면에서
  가로로 넘친 것**이었음.
- **수정**: 이전에 두 번 키웠던 `.wrap` 좌우 패딩(1.75rem)은 원인이 아니었으므로 1.25rem으로
  되돌림. `.header-right`에 `flex-wrap: wrap`, `justify-content: flex-end`,
  `gap: 0.75rem 1.25rem`(줄바꿈 시 세로 간격도 지정), `min-width: 0`(부모 flex 행 안에서 자기
  콘텐츠 크기 이하로 줄어들 수 있게 허용)을 추가.
- **검증 방법과 함께 발견한 두 번째 문제 (테스트 방법론 버그)**: 헤드리스 Chrome을
  `--window-size=390,844`로 띄워 스크린샷을 찍었는데, 수정 후에도 스크린샷이 수정 전과 완전히
  동일하게 나와 의아했음. Chrome DevTools Protocol(`Runtime.evaluate`)로 직접
  `window.innerWidth`를 물어보니 **390이 아니라 500**이 나옴 — 최신 Chrome(151, headless=new
  아키텍처)에서는 `--window-size` 플래그가 스크린샷 캡처 버퍼 크기만 정하고 실제 레이아웃
  뷰포트(=미디어 쿼리가 보는 폭)는 다른 값으로 남아 있었음(사용자 프로필로 이미 떠 있던 창
  크기를 물려받은 것으로 추정 — Chrome 싱글턴 프로세스 재사용). 그래서 여태 어떤 CSS를 고쳐도
  "그대로다"라고 보였던 것 — **CSS가 아니라 검증 스크린샷 자체가 실제로는 모바일 폭에서
  찍히지 않고 있었던 것**. `Emulation.setDeviceMetricsOverride`로 CDP에서 직접 390×844 뷰포트를
  강제한 뒤 재검증하니 `scrollWidth === innerWidth === 390`(가로 오버플로우 0), 헤더가 세로로
  스택되고 nav가 올바르게 줄바꿈됨을 확인 — 홈/프로젝트 두 페이지 모두 확인함.
- **위험/후속 작업**: 이 세션에서 헤드리스 Chrome 스크린샷으로 반응형 레이아웃을 검증할 때는
  `--window-size` 플래그를 신뢰하지 말고 CDP `Emulation.setDeviceMetricsOverride`로 뷰포트를
  명시적으로 강제해야 함 — 그렇지 않으면 실제로는 데스크톱 폭에서 렌더링된 화면을 모바일
  검증 결과로 착각할 수 있음.

## 2026-08-07 — `/projects/` 페이지 UX 개편 (카테고리 그룹핑 + 태그 필터 + 카드 간결화)

- **무엇**: 프로젝트가 5~8개로 늘어날 걸 대비해 `/projects/` 페이지를 재구성.
  - `Project`에 필수 `category` 필드 추가(기존 3개는 각각 "AI/플랫폼", "인프라", "실시간 시스템").
    `tags`에는 공백을 포함한 값을 금지하는 검증도 추가 — 아래 CSS 필터가 태그를 공백 구분
    토큰으로 매칭하기 때문("Argo CD" → "ArgoCD"로 변경).
  - `/projects/` 페이지를 카테고리 섹션(h2 헤더)으로 묶어서 표시. 그룹 순서는 별도 필드 없이
    각 카테고리에서 가장 낮은 `order`를 가진 프로젝트가 나온 순서를 그대로 따름
    (`pipeline._group_projects_by_category`).
  - 카드에는 성과 상위 2개·태그 상위 5개만 보이고 나머지는 "+N개 더"/"+N"으로 축약
    (`renderer._truncated` 필터). 전체 목록은 기존처럼 모달/상세 페이지에서 그대로 노출.
  - 기술 태그 필터 칩을 페이지 상단에 추가 — 새 JS 없이 순수 CSS(라디오 버튼 + 형제 결합자 +
    `:has()`)로 구현. 태그 클릭 시 해당 태그 없는 카드를 숨기고, 카드가 하나도 안 남은
    카테고리 섹션은 헤더까지 함께 숨김.
  - Home의 "Featured Projects"는 그룹핑/필터 없이 기존처럼 단순 큐레이션 그리드 유지(카드
    간결화만 공유 컴포넌트라 자동으로 적용됨).
- **왜**: "프로젝트가 여러 개 적을 텐데 UX에 맞게 구성해줄 수 있어?" 요청 — 예상 규모(5~8개),
  개선 방향(태그 필터/카드 간결화/정렬-구분 기준), 정렬 기준(역할·도메인 카테고리)을 각각
  확인받고 진행.
- **버그(구현 중 자체 발견)**: 처음 구현에서 필터 라디오를 `<fieldset>`으로 감쌌더니 CSS
  `:checked ~ .project-groups` 형제 결합자가 전혀 매칭되지 않는 문제 발생 — `~`는 같은 부모
  아래의 실제 형제 요소에만 적용되는데, `<fieldset>`이 한 겹 더 감싸면서 라디오와
  `.project-groups`가 형제가 아니게 됨. 라디오/라벨과 `.project-groups`를 `.projects-filterable`
  (flex 컨테이너) 아래 평평한 형제로 재배치하고, `.project-groups`에 `flex: 1 1 100%`를 줘서
  칩 줄 다음에 항상 새 줄로 내려오게 해서 해결. 헤드리스 Chrome + CDP로 실제 클릭까지
  시뮬레이션해서 필터가 카드/섹션을 정확히 숨기는지 확인한 뒤에야 발견함 — 코드만 보고는
  놓쳤을 문제.
- **위험/후속 작업**: 태그 필터는 단일 선택(라디오)만 지원 — 다중 태그 동시 필터링이 필요해지면
  체크박스 기반으로 다시 설계해야 함(여러 활성 필터의 AND 조건을 CSS만으로 표현하는 게 더
  복잡해짐). 카테고리 이름은 자유 텍스트라 `data/projects.yaml`만 수정하면 새 카테고리를 바로
  추가할 수 있음.

## 2026-08-07 — 카드의 "+N개 더"를 인라인 펼치기로 변경

- **무엇**: 위 UX 개편에서 성과 불릿의 "+N개 더"가 클릭 불가능한 정적 텍스트였는데, 클릭하면
  나머지 불릿이 카드 안에서 바로 펼쳐지도록 변경. 케이스 스터디 본문의 문제/해결 섹션에 이미
  쓰던 것과 같은 순수 CSS `<details>/<summary>` 방식(JS 없음). `renderer._truncated` 필터가
  이제 `hidden`(숨겨진 항목 리스트)도 함께 반환하도록 확장해서 템플릿에서 `limit` 값을 다시
  하드코딩하지 않고 그대로 씀.
- **왜**: "카드에서 더보기를 눌렀을 때 불릿도 밑에 펼쳐졌으면 좋겠어" 요청.
- **위험/후속 작업**: 태그 쪽 "+N" 오버플로 표시는 아직 정적 텍스트로 남아 있음 — 같은 방식으로
  펼치길 원하면 동일한 패턴을 재사용하면 됨.

## 2026-08-07 — "+N개 더" 펼친 뒤 같은 자리에 "가리기"가 아니라 목록 맨 아래로

- **무엇**: 바로 위 변경에서 "+N개 더"를 펼쳐도 그 버튼이 같은 위치에 그대로 남아있었는데,
  펼친 뒤에는 그 버튼이 사라지고 펼쳐진 불릿 맨 아래에 "가리기" 버튼이 새로 나타나도록 변경.
  여전히 `<details>` 하나의 네이티브 토글만 쓰고(JS 없음), `.achievements-more`를 flex column으로
  만들어 `summary`에 `order`를 줘서(닫힘: 위/`order:1`, 열림: 아래/`order:3`) 같은 버튼이
  콘텐츠 아래로 위치를 옮기게 하고, `summary` 안에 "+N개 더"/"가리기" 두 라벨을 넣고
  `[open]` 여부로 하나만 보이게 전환.
- **왜**: "그 2개더 버튼이 눌리면 가려지고 불릿 맨 아래에 가리기 버튼이 생겨야할 거 같아" 요청.
- **위험/후속 작업**: 헤드리스 Chrome 스크린샷 클리핑(`Page.captureScreenshot`의 `clip`)이 이
  세션의 Emulation 뷰포트 오버라이드와 좌표계가 안 맞아 잘린 스크린샷이 계속 빈 영역만 나오는
  문제가 있었음 — 클리핑 대신 전체 페이지 스크린샷 + `scrollIntoView`로 우회. `getBoundingClientRect()`
  기반 좌표를 `Page.captureScreenshot`의 `clip`에 그대로 넘기지 말 것.

## 2026-08-07 — 태그 "+N"도 같은 방식으로 펼치기/접기

- **무엇**: 성과 불릿에 적용한 것과 같은 "누르면 펼쳐지고, 펼치면 맨 끝에 접기 버튼" 패턴을
  태그 목록의 "+N" 오버플로 표시에도 적용. 태그는 세로 목록이 아니라 줄바꿈되는 pill
  가로 목록이라 achievements와 같은 flex-column `order` 트릭 대신, `.tags`(이미 flex-wrap)
  안에 `.tags-toggle`(`<details>` 감싼 `<li>`)과 `.tag-hidden`(숨겨진 태그) `<li>`들을 평평한
  형제로 두고 flex `order` + `:has()`로 구현: 닫힘 상태는 `.tags-toggle`이 순서상 먼저(보이는
  태그 바로 뒤), 열림 상태(`.tags-toggle:has(> details[open])`)는 숨은 태그들을 먼저 보여주고
  `.tags-toggle` 자신의 order를 더 뒤로 밀어서 "가리기"가 펼쳐진 태그 뒤에 오게 함. 여전히
  JS 없음.
- **왜**: "그 태그도 마찬가지로 눌리고 접히는 느낌이었으면 좋겠어" 요청 — achievements에 이미
  적용한 패턴과의 일관성 요구.
- **위험/후속 작업**: 없음 — 헤드리스 Chrome + CDP로 열림/닫힘 두 상태 모두 스크린샷과 DOM
  속성(`order`, 숨김 태그의 `display`)으로 확인함.

## 2026-08-07 — AI 인프라 어필용 태그 확장 + 성과 수치 보강

- **무엇**: `data/projects.yaml`의 프로젝트별 태그를 각 케이스 스터디의 "## 기술" 절에 이미
  문서화된 실제 스택에서 골라 확장 — AI 인프라 지향 신호가 강한 항목(H100, vLLM, NVLink,
  InfiniBand, Karpenter, CUDA, PyTorch 등)을 우선순위 앞쪽(카드에서 접지 않고도 보이는 상위
  5개 태그)에 오도록 순서도 재배치. `realtime-voice-translation.md`의 성과 불릿 2개는 같은
  문서 다른 절에 이미 있던 수치(Pod 1~5개 확장, 노드 그룹 3개)를 끌어와 정량화.
- **왜**: "태그들 더 추가해줄 수 있어? AI 인프라 쪽으로 어필하는 사람의 태그가 필요해. 성과도
  되도록 수치화된 결과가 있었으면 좋겠어" 요청.
- **위험/후속 작업**: 두 항목은 문서 안에서 끌어올 수치가 없어 사용자에게 직접 문의함 —
  (1) enterprise-ai-platform의 NAS 모델 로딩 병목 개선 후 정확한 로딩 시간, (2) 
  realtime-voice-translation의 API Pod 메모리 증가 폭·개선 후 수치. 답변 오면 각 성과 불릿에
  반영 예정.

## 2026-08-07 — `/projects/` 태그 필터 기능 제거

- **무엇**: 카테고리 그룹핑(섹션 헤더)은 유지하되, 상단의 기술 태그 필터 칩(전체 + 태그별
  클릭 필터링) 기능 자체를 제거. `templates/projects.html`을 필터 이전의 단순 카테고리
  그룹핑 구조로 되돌리고, 이제 안 쓰는 것들을 함께 정리:
  - `pipeline._collect_tags()`와 `all_tags` context 변수 — 필터 칩 목록 생성용이었음
  - `project_card.html`의 `data-tags` 속성 — 필터의 CSS 매칭용이었음, 카드 자체 렌더링에는
    불필요
  - `static/css/main.css`의 `.projects-filterable`/`.tag-filter-input`/`.tag-chip`,
    `.sr-only`(필터 라벨에만 쓰였음)
  - 관련 pytest(`TestCollectTags`, 태그 필터 wiring 테스트) 제거
- **왜**: "project 눌렀을 때 태그별로 프로젝트 보이는 기능 이거 굳이 안필요한거 같아" 요청.
- **위험/후속 작업**: 카드 내부의 태그 "+N" 펼치기/접기(`.tags-more`)는 이 필터와 별개
  기능이라 그대로 유지함 — 태그를 숨김/펼침하는 것이지 프로젝트 목록을 필터링하는 게 아님.

## 2026-08-07 — realtime-voice-translation 회고 "향후 개선" 목록 수정

- **무엇**: `content/projects/realtime-voice-translation.md` 회고의 "향후 개선한다면" 목록을
  사용자 요청대로 수정 — PostgreSQL 이전 대상을 RDS Multi-AZ에서 Amazon Aurora(PostgreSQL
  호환)로 변경, PodDisruptionBudget·`preStop` hook 항목 2개 제거, SLI·SLO 뒤에 AIOps 관련
  항목 2개 신설: (1) Prophet·LSTM 기반 시계열 예측으로 부하 발생 전에 HPA·Karpenter가 먼저
  확장하는 동적 오토스케일링, (2) 장애 로그·메트릭 자동 분석 기반 초기 장애보고서 생성과
  반복 운영 작업(재기동·캐시 정리 등) AIOps 자동화.
- **왜**: "PostgreSQL을 RDS 대신 Aurora로, PodDisruptionBudget·preStop hook 항목은 잘 몰라서
  제거, 모니터링 기반 AIOps로 Prophet·LSTM 동적 오토스케일링과 장애보고서·운영 자동화 내용을
  추가해달라"는 요청 — 문구 정리는 위임받아 직접 작성.

## 2026-08-07 — 나머지 두 프로젝트 회고 리뷰 + AIOps 항목 확대

- **무엇**: 사용자 요청으로 `enterprise-ai-platform`·`airport-rail-crowd-monitoring` 회고의
  "향후 개선" 목록을 처음부터 다시 검토. 두 문서 다 "회고에서만 언급되고 본문(기술/역할/
  구조도)에는 전혀 안 나오는 용어"가 있는지 확인한 결과:
  - `enterprise-ai-platform`: 전 항목이 본문에서 이미 다룬 내용에 뿌리를 두고 있어 특이사항 없음.
  - `airport-rail-crowd-monitoring`: `SQLAlchemy Session 경계` 항목은 본문 어디에도 없어
    확인을 요청 → 사용자가 그대로 유지 결정. `Prometheus·Grafana` 모니터링 항목도 본문에
    없어 확인을 요청 → 사용자가 "실제로 구성돼 있다"고 확인, `data/projects.yaml` 태그에
    `Prometheus`·`Grafana` 추가.
  - 사용자가 confirm한 AIOps 방향(음성 번역 프로젝트에 먼저 적용)을 나머지 두 프로젝트
    회고에도 각각 2개 항목씩 추가: 예측(Prophet·LSTM 시계열 예측 기반 사전 Capacity
    Planning/이상 탐지)과 장애·운영 자동화(장애보고서 자동 생성, 반복 작업 자동화) 쌍으로
    세 프로젝트 전체에 일관된 톤을 맞춤.
- **왜**: "다른 프로젝트 회고도 한번 훑어봐줄래" 요청에 대한 리뷰 결과 보고 후, "AIOps 방향
  항목을 추가해줘. 1번[SQLAlchemy] 그대로 두고 2번[Prometheus/Grafana]도 태그랑 다 넣어줘.
  실제로 구성되어있어"라는 확정 답변을 받아 진행.
