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
