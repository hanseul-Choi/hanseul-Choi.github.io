# POLICY — renderer

## 역할
Jinja2 환경을 구성하고, `contracts` 모델(페이지/프로젝트/내비게이션)을 `templates/*.html`에
렌더링해 HTML 문자열을 만든다.

## 규칙
- `contracts`만 import한다. `content_loader`, `link_checker`, `site_builder`를 import하지 않는다.
- Jinja2 `Environment`는 반드시 `autoescape=True`로 생성한다 (XSS/템플릿 인젝션 방지, 아래
  THREAT_MODEL.md 참고). `autoescape=False`로 바꾸는 PR은 이 문서를 먼저 갱신해야 한다.
- 템플릿 파일 경로는 `templates/` 하위로 고정 (`FileSystemLoader`에 절대/상대 임의 경로를
  전달하지 않는다).
- 템플릿에서 실행 가능한 임의 Python 표현식을 허용하지 않는다 (기본 Jinja2 sandbox 밖 기능 사용 금지).

## 변경 시 체크리스트
- [ ] 새 컴포넌트(`templates/components/*.html`) 추가 시 렌더링 결과에 대한 BeautifulSoup 기반
      구조 검증 테스트 추가
- [ ] autoescape 관련 설정을 만지면 THREAT_MODEL.md의 XSS 시나리오 테스트 필수 통과
