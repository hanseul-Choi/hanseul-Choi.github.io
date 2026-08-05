# THREAT_MODEL — renderer

## 자산
- 최종 사용자(사이트 방문자)의 브라우저 — 악성 스크립트 삽입(XSS) 방지 대상

## 위협
1. **저장형 XSS / 템플릿 인젝션**: 콘텐츠 데이터(`data/projects.yaml`, Markdown 본문)에
   `<script>` 등이 섞여 그대로 HTML에 출력되는 경우.
   - 대응: Jinja2 `autoescape=True` 필수. Markdown → HTML 변환 결과만 `| safe`로 신뢰하고,
     그 외 사용자/데이터 필드는 절대 `| safe`를 붙이지 않는다.
   - 테스트: `test_engine.py::test_escapes_html_in_project_summary`로 `<script>` 문자열이
     이스케이프되어 렌더링되는지 검증.
2. **신뢰할 수 없는 템플릿 로드**: 외부에서 주입된 경로로 임의 템플릿 파일을 로드.
   - 대응: `FileSystemLoader(templates_dir)`의 `templates_dir`는 `site_builder`가 고정 상수로만
     전달, 사용자 입력으로 대체되지 않는다.

## 신뢰 경계
- 현재는 저장소 소유자만 `data/`, `content/`를 작성한다고 가정 (신뢰된 입력). 그럼에도
  autoescape는 기본값으로 항상 켜서, 향후 외부 입력(예: 방명록/댓글)이 추가되어도 안전하도록 한다.
