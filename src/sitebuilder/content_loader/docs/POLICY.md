# POLICY — content_loader

## 역할
`data/*.yaml`(내비게이션, 프로젝트 목록, 사이트 설정)과 `content/pages/*.md`(Markdown +
frontmatter)를 읽어 `contracts`의 Pydantic 모델로 검증된 객체로 변환한다.

## 규칙
- `contracts`만 import한다. `renderer`, `link_checker`, `site_builder`를 import하지 않는다.
- 모든 파일 읽기는 명시적으로 전달된 base 디렉터리 아래로 제한한다 (경로 순회 방지, 아래
  THREAT_MODEL.md 참고).
- YAML 파싱은 `yaml.safe_load`만 사용한다 (`yaml.load` 금지 — 임의 Python 객체 역직렬화 방지).
- 스키마에 맞지 않는 데이터는 조용히 무시하지 않고 `ContentLoadError`를 발생시켜 빌드를 실패시킨다.

## 변경 시 체크리스트
- [ ] 새 콘텐츠 소스 형식을 추가하면 실패 케이스(빈 파일, 잘못된 YAML, 스키마 불일치) 테스트 추가
- [ ] 경로 처리 로직을 바꾸면 THREAT_MODEL.md의 경로 순회 시나리오 테스트 재확인
