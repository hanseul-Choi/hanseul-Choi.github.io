# Claude Code — Project Rules Pointer

이 저장소의 작업 규칙은 [`AGENTS.md`](./AGENTS.md)에 정의되어 있다. Claude Code는 항상
`AGENTS.md`를 루트 규칙으로 읽고 따른다. 이 파일은 Claude Code가 프로젝트 메모리로 자동 로드하는
`CLAUDE.md` 관례를 지키기 위한 포인터일 뿐, 내용이 갈라지지 않도록 규칙 본문은 여기 두지 않는다.

사용자(개인)의 전역 지침(`~/.claude/CLAUDE.md`)이 있다면 그것과 이 저장소의 `AGENTS.md`가
충돌할 경우, `AGENTS.md`의 모듈/테스트/검증 관련 규칙이 이 저장소 내 작업에서는 더 구체적인
규칙으로 우선 적용된다. 단, "큰 변경 전 확인", "테스트/린트 검증", "사용자 이해 확인" 같은
전역 워크플로 지침은 그대로 유지된다.
