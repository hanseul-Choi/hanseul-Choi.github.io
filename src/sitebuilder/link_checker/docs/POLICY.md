# POLICY — link_checker

## 역할
빌드된 출력 디렉터리(HTML 파일들)를 스캔해서 `<a href>`, `<img src>`, `<script src>`,
`<link href>`(스타일시트 등)가 실제 존재하는 파일을 가리키는지, 이미지에 `alt` 속성이 있는지
검사한다. 외부(http/https) 링크 검사는 기본적으로 끄고, 켤 경우 allowlist된 도메인만 요청한다.

## 규칙
- `contracts`만 import한다. `content_loader`, `renderer`, `site_builder`를 import하지 않는다.
- 기본 동작은 네트워크 요청을 하지 않는다 (오프라인, 결정적, 빠른 테스트를 위해). 외부 링크
  검사는 명시적 옵션(`check_external=True`)으로만 켜지고, 이 경우에도 요청 대상 스킴은
  `http`/`https`만 허용한다 (아래 THREAT_MODEL.md 참고).
- 출력 디렉터리 밖의 경로를 절대 열지 않는다.

## 변경 시 체크리스트
- [ ] 새 검사 항목(예: heading 구조, meta description) 추가 시 유닛 테스트 함께 추가
- [ ] 외부 링크 검사 기능을 확장하면 SSRF 시나리오 테스트 재확인
