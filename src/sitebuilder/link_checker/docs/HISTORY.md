# HISTORY — link_checker

## 2026-08-05 — 초기 구현
- 오프라인 내부 링크/이미지 alt 검사만 구현 (`check_internal_links`). 외부 링크 검사는 아직
  구현하지 않음 (THREAT_MODEL.md의 SSRF 대응이 먼저 필요하므로 범위에서 제외, 후속 작업으로 기록).

## 2026-08-05 — 버그 수정: `data:` URI를 내부 경로로 오인
- **증상**: 프로젝트 상세 페이지에 `data:image/svg+xml;base64,...` 형태의 이미지를 넣고 빌드하면
  `OSError: [Errno 63] File name too long`으로 빌드 전체가 죽음.
- **원인**: `_resolve_internal_target`이 `http`/`https`/`mailto`/`tel` 4개만 "외부 스킴"으로
  허용목록에 두고, 그 외 스킴(`data:`, `blob:` 등)은 스킴이 있는데도 내부 상대경로처럼 취급해서
  `output_dir` 기준 파일로 resolve하려다 base64 블롭을 파일명으로 `stat()`하게 됨.
  프로젝트 이미지가 데이터 URI일 수 있다는 걸 처음 설계에서 놓쳤음.
- **수정**: 허용목록 대신 "스킴이 하나라도 있으면 무조건 외부/스킵"으로 일반화. 회귀 테스트
  `test_data_uri_image_is_skipped_not_crashed_on` 추가.

## 2026-08-06 — `<script src>`/`<link href>` 검사 추가
- **발견 경위**: 다크모드 토글 기능으로 사이트 최초의 외부 JS 파일(`static/js/theme-toggle.js`)을
  추가하면서, `check_internal_links`가 `<a>`/`<img>`만 보고 `<script src>`나 `<link href>`
  (스타일시트)는 전혀 검사하지 않는다는 걸 알아챔 — 예를 들어 `main.css` 경로가 깨져도 빌드는
  "링크 이슈 0건"으로 조용히 통과했을 것.
- **수정**: `<script src>`(inline 스크립트는 `src` 속성이 없어 자동 제외)와 `<link href>`를
  같은 `_check_internal_target`로 검사하도록 확장. 회귀 테스트 4개 추가(깨진/정상 script src,
  inline script 무시, 깨진/정상 link href).
