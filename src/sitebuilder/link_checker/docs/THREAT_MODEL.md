# THREAT_MODEL — link_checker

## 자산
- 빌드 서버/로컬 머신의 네트워크 접근 (SSRF 방지 대상), 파일시스템(출력 디렉터리 밖 파일)

## 현재 구현 범위
`check_internal_links`은 **오프라인** 검사만 수행한다 (내부 링크 존재 여부, 이미지 alt 누락).
외부(http/https) 링크 검사는 아직 구현되어 있지 않다 (docs/HISTORY.md 참고). 아래 위협/대응은
외부 링크 검사 기능을 추가할 때 반드시 지켜야 하는 설계 제약이며, 그 전까지는 해당 위협이
코드 경로 자체가 없으므로 발생하지 않는다.

## 위협
1. **SSRF (Server-Side Request Forgery)** — *외부 링크 검사 추가 시 적용*: 프로젝트 데이터의
   `live_url`/`repo_url`에 `http://169.254.169.254/...`(클라우드 메타데이터) 또는 내부망
   주소가 들어가고, 외부 링크 검사 기능이 이를 그대로 요청하는 경우.
   - 대응(구현 전 필수 설계): 외부 링크 검사는 기본 꺼짐(default-deny). 켤 경우 스킴은
     `http`/`https`만, 호스트가 사설 IP 대역(`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`,
     `192.168.0.0/16`, `169.254.0.0/16`)으로 resolve되면 요청을 거부한다.
   - 구현 시 반드시 추가할 테스트: `test_checker.py::test_rejects_private_ip_targets`.
2. **경로 순회로 출력 디렉터리 밖 파일 접근** — *현재 구현됨*: `href="../../etc/passwd"` 같은
   내부 링크를 그대로 파일시스템에서 열어보는 경우.
   - 대응: 링크 대상 경로를 항상 출력 디렉터리 기준으로 `resolve()` 후 하위 경로인지 검증,
     아니면 "escapes output dir"로 `broken_link` 이슈 처리.
   - 테스트: `test_checker.py::test_flags_link_escaping_output_dir`.

## 신뢰 경계
- 콘텐츠 데이터는 저장소 소유자만 작성 (신뢰된 입력)이지만, "링크가 죽어있는지"를 검사하는
  도구 특성상 향후 outbound 네트워크 요청 기능이 커질 수 있으므로 allowlist/default-deny
  원칙을 처음부터 문서화해두고, 구현 시 이 문서를 갱신한다 (AGENTS.md 규칙 12).
