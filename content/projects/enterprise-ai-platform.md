---
title: "기업용 AI 플랫폼 · OpenAPI 구축/운영"
---

_2025.03 ~ 현재_

## 기술

- **Platform:** Kubernetes, kubeadm, CRI-O, Cilium, Helm, Argo CD, Jenkins, Kong
- **Cloud & Infrastructure:** AWS, On-Premise, ALB, NLB, Harbor, Proxy, Firewall
- **GPU & AI Serving:** H100, A100, V100, MIG, NVLink, InfiniBand, vLLM
- **Messaging & Database:** Kafka, PostgreSQL, MariaDB, Elasticsearch
- **Observability:** Prometheus, Grafana, Elasticsearch
- **Security:** HashiCorp Vault, Kubernetes Secret, TLS
- **Languages:** Python, Shell Script

## 개요

롯데이노베이트의 아이멤버는 자체 LLM과 GPT·Claude·Gemini 등 외부 상용 AI를 통합해, 사내
데이터 기반의 생성형 AI와 업무 자동화 기능을 제공하는 기업용 AI 플랫폼이다.

생성형 AI 챗봇뿐만 아니라 회의록 작성, 문서 체크리스트, PPT 생성 등의 업무 기능을 제공했으며,
사내 데이터와 민감정보를 안전하게 처리할 수 있도록 개발계·운영계와 외부 연계 환경을 분리해
운영했다.

보안 요구가 높은 금융권 고객사에는 외부망과 차단된 온프레미스 Kubernetes 환경으로 플랫폼을
구축했다. 또한 외부 고객이 AI 모델을 API 형태로 사용할 수 있도록 별도의 AWS OpenAPI 클러스터를
운영했다.

이러한 환경에서 H100·A100·V100 기반 모델 서빙, Kubernetes, API Gateway, Kafka, 데이터베이스,
CI/CD 및 모니터링 체계를 통합 운영하고, 신규 모델 배포와 서비스 장애 대응을 수행했다.

## 역할

**플랫폼 및 Kubernetes 운영**

- kubeadm 기반 개발계·운영계·유틸리티 Kubernetes 클러스터 운영, Control Plane 3대와 CPU·GPU Worker Node로 구성된 온프레미스 환경 관리
- CRI-O Container Runtime 및 Cilium CNI 운영, NLP·Vision·STT 등 서비스 영역별 Namespace 관리
- Helm Chart 직접 작성 및 애플리케이션 배포 표준화, Argo CD Project를 활용한 개발계·운영계 배포 분리
- Deployment, Service, Ingress, ConfigMap, Secret, PVC 관리 · Node Label과 `nodeSelector`로 CPU·GPU 워크로드 배치
- HPA, readiness/liveness probe 및 resource request·limit 운영
- Kong Ingress와 사내 Load Balancer를 연결한 API 진입 경로 관리

**GPU 및 모델 서빙**

- H100 24장, A100 32장, V100 40장 등 **90장 이상의 GPU 자원 운영**
- 자체 LLM 및 AI 업무 모델을 포함한 **약 60개 모델 서비스 관리**
- GPU, HBM, CPU, Memory 자원 사용량 모니터링
- H100 MIG를 활용한 GPU 자원 분할 및 소규모 모델 배치 효율화
- NVLink 기반 동일 노드 내 다중 GPU 모델 서빙, InfiniBand 기반 노드 간 분산 학습·서빙 PoC
- 모델 OOM 발생 시 다중 GPU 할당 및 Node 배치 조정
- vLLM 기반 모델의 요청 대기·배치 처리 병목 분석, 대용량 모델의 NAS 로딩 병목 분석 및 GPU Node Local Cache 구성

**CI/CD 및 모델 배포**

- 신규 모델별 Dockerfile, Jenkins Pipeline, Helm Chart 구성 · GitLab 소스 기반 Jenkins 이미지 빌드
- Harbor Registry Push 및 Argo CD 배포 연동, 신규 모델의 Ingress·Kong Route·Health Check 구성
- 주 1회 이상, 회당 4개 이상의 모델을 개발계·운영계에 배포. 배포 요청부터 API 서빙까지 약 1시간 이내 구성
- 배포 후 장애 발생 시 이미지 버전 변경 및 Argo CD Rollback 수행

**네트워크 및 보안**

- Kong, 사내 Load Balancer, ALB, NLB, NodePort 통신 경로 운영, 내부망·외부망 방화벽 및 Proxy Whitelist 관리
- CRI-O·애플리케이션·Node별 Proxy·`NO_PROXY` 정책 관리, Kong TLS 인증서와 API Endpoint 운영
- Kubernetes Secret 및 환경변수 기반 민감정보 관리, 개발계에 Vault를 적용한 Secret 중앙관리 체계 도입
- 금융권 고객사 완전 폐쇄망 AI 플랫폼 구축·운영 지원, AWS OpenAPI 클러스터와 온프레미스 모델 서버 간 방화벽 통신 관리

**모니터링 및 장애 대응**

- Prometheus·Grafana 기반 Pod·Node·GPU 자원 모니터링, Kong 로그로 Endpoint별 5xx·504 오류 집계
- Kafka Consumer Lag·리밸런싱 및 메시지 처리 오류 분석, PostgreSQL·MariaDB Connection과 실행 쿼리 점검
- CPU Throttling, Network/Disk I/O, Load Average 분석, kubelet·CRI-O·Kernel·Core Dump 로그를 연계한 NodeNotReady 분석
- 일평균 1~5건의 운영 문의 및 장애 대응, 반복 장애에 대한 점검 명령어·운영 체크리스트 작성

## 구조도

_실제 구조도 이미지는 추후 추가 예정입니다. 우선 텍스트로 정리합니다._

```
                           [사내 사용자]
                                  │
                          [아이멤버 Web] — 사내 Load Balancer
                                  │
                          [Kong Gateway] TLS / Auth / Routing
        ┌─────────────────────────┼────────────────────────┐
        ▼                         ▼                        ▼
 [개발계 Cluster]          [운영계 Cluster]        [외부 AI 서비스]
  kubeadm/CRI-O/Cilium     kubeadm/CRI-O/Cilium    GPT/Claude/Gemini
        │                         │
   NLP · STT/회의록 · Vision · 업무 자동화 API (PPT/체크리스트)
        │                         │
        └────────────┬────────────┘
                      ▼
             [AI Model Serving]
             H100/A100/V100 · vLLM · MIG · NVLink · InfiniBand
             NAS / Node Local Cache

[Utility Cluster]              [Data & Messaging]
Jenkins → Harbor               Kafka
Argo CD → 개발계·운영계 배포     PostgreSQL / MariaDB
Prometheus / Grafana           Elasticsearch
Elasticsearch

[외부 고객] → [AWS OpenAPI Cluster] (ALB/NLB) → 온프레미스 모델 서버 연동

[금융권 고객사] → 완전 폐쇄망 Kubernetes Cluster (자체 AI 모델, GPU Worker Node, 외부망 차단)
```

## 문제 및 해결

### 1. Kafka Consumer 리밸런싱으로 인한 회의록 처리 실패

**상황** — 회의록 서비스는 STT와 NLP 처리를 Kafka 메시지로 순차 수행하는 비동기 구조였다.
초기에는 STT와 NLP가 서로 다른 Topic을 쓰면서도 동일한 Consumer Group을 사용했는데, 모델
추론이 길어지면 Consumer Polling이 지연됐고 리밸런싱 이후 과거 요청이 뒤늦게 소비되며 만료된
토큰으로 작업이 실행됐다. 회의록 요청 성공률이 약 70% 수준까지 낮아졌다.

**원인** — 역할이 다른 STT·NLP Consumer가 동일 Consumer Group 사용, 장시간 추론 중
`max.poll.interval.ms` 초과, 리밸런싱으로 메시지 재할당, 오래된 메시지 처리 시 인증 토큰 만료,
추론 실패 대응용 Timeout·Retry·복구 로직 부족.

**해결** — STT·NLP Consumer Group을 서비스별로 분리하고, `max_poll_interval_ms`를 모델 추론
시간에 맞춰 5분으로 조정했다. 모델 추론 Timeout·Retry 정책을 추가하고, 만료된 토큰을 사용하는
작업을 차단했다. 일시적 추론 실패에도 작업을 복구하도록 재처리 로직을 보완하고, 수정 후 7일간
Kafka 로그와 처리 결과를 모니터링했다.

**결과** — 회의록 처리 성공률을 약 70%에서 99% 수준으로 개선했고, 수정 이후 7일 동안 동일한
리밸런싱 오류가 재발하지 않았다.

### 2. NAS 기반 대용량 모델 로딩 병목

**상황** — 32B급 대용량 모델을 원격 NAS에 저장하고 Pod에서 PVC로 연결해 로딩했다. NAS 파일
복사 속도는 빨랐지만 모델을 NAS에서 직접 로딩할 때는 1시간 이상 소요돼, 신규 모델 배포를 근무
외 시간에 진행해야 했다.

**원인** — 단순 대역폭보다 로딩 과정의 I/O 패턴이 병목이었다. SCP는 파일을 순차적으로 읽어
대역폭을 효율적으로 쓰지만, 모델 로딩은 다수의 가중치·메타데이터 파일에 반복 접근한다. NAS의
Random I/O·Metadata 처리에서 네트워크 왕복 지연이 누적됐고, `mmap` 페이지 폴트마다 원격
파일시스템에 반복 접근했다.

**해결** — 배포 시 Init Container가 모델 전체를 매번 복사하는 대신, 서비스 배포 전 대상 GPU
Node의 로컬 디스크로 모델을 미리 복제하는 사전 다운로드 Job을 구성했다. 모델 Pod는 NAS가
아닌 Node Local Path를 읽도록 하고, 사용하지 않는 이전 모델·이미지를 정기적으로 정리했다.
디스크 사용량을 확인해 캐시 용량을 관리하고, 모델 버전 변경 시 새 파일을 내려받는 운영 절차를
만들었다.

**결과** — 1시간 이상 걸리던 NAS 직접 로딩 병목을 완화해 업무 시간에도 대용량 모델을 배포할
수 있게 됐고, 다운로드와 서비스 기동 단계를 분리해 배포 실패 원인 파악도 쉬워졌다.

### 3. H100 MIG 기반 GPU 자원 효율화

**상황** — 일부 모델은 H100의 연산 성능은 필요했지만 GPU Memory 80GB 전체를 쓰지 않았다.
모델마다 H100 한 장을 독점 배치하면 유휴 HBM이 남았고, 작은 모델을 추가 배포하려면 GPU를
더 늘려야 하는 비효율이 있었다.

**해결** — H100 4장에 MIG를 적용해 모델의 HBM 요구사항에 따라 자원을 분할했다 — H100 2장은
GPU당 40GB Instance 2개, 나머지 2장은 GPU당 20GB Instance 3개 + 10GB Instance 1개. Node와
MIG Profile에 Label을 적용하고, 모델별 HBM 요구량에 따라 `nodeSelector`로 배치했다. 대규모
모델은 전체/다중 GPU에, 소규모 모델은 적절한 MIG Instance에 배치했다.

**결과** — H100 4장을 최대 12개의 독립 GPU 자원 단위로 구성해, H100 성능이 필요한 소규모
모델의 동시 배포 수를 늘렸다. 체감 성능 저하 없이 유휴 GPU Memory를 활용했고, 추가 GPU 증설
없이 기존 장비 활용도를 개선했다.

### 4. CRI-O Proxy 누락으로 인한 ImagePullBackOff

**상황** — 개발계 Argo CD Pod가 외부 Registry `quay.io`에서 이미지를 가져오지 못하고
`ImagePullBackOff` 상태가 됐다. Worker Node에서 직접 `curl`을 실행하면 정상 통신됐고, 해당
Node에는 대상 이미지가 캐시돼 있지 않았다.

**원인** — 사용자 로그인 Shell에는 Proxy가 적용돼 있었지만, 실제 이미지 Pull을 수행하는
CRI-O systemd 서비스에는 Proxy 환경변수가 적용되지 않았다. Node의 사용자 명령은 외부와
통신할 수 있었지만 Container Runtime은 Registry에 접근할 수 없었다.

**해결** — CRI-O용 systemd Drop-in 설정을 만들어 `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY`를
적용하고, Kubernetes Service·Pod 대역과 사내망 대역을 `NO_PROXY`에 추가했다. `systemctl
daemon-reload` 후 CRI-O를 재시작하고, `systemctl show crio`로 Proxy 환경변수·Drop-in 적용
여부를 확인한 뒤 이미지 캐시가 없는 상태에서 재검증했다.

**결과** — 외부 Registry 이미지 Pull이 정상화돼 Argo CD Pod가 약 5초 내 정상 기동했다. Node
Shell과 Container Runtime의 Proxy 설정을 구분해 점검하는 운영 절차를 정립했다.

### 5. GPT·SSE API의 504 오류 개선

**상황** — 운영계에서 Kong을 통해 호출되는 GPT·Gemini·Claude SSE API에 504 오류가 반복
발생했다. Kong 로그 분석 결과 일간 100건 이상, 월간 약 6,000건이 발생했고 대부분 장시간
연결을 유지하는 SSE Endpoint에 집중돼 있었다. 동시 요청 테스트에서는 앞선 응답이 끝날 때까지
다음 요청 처리가 지연되는 현상도 확인됐다.

**분석** — Gateway 설정만 보지 않고 요청이 통과하는 전체 계층을 나눠 확인했다 — Kong 로그
Endpoint별 집계, Java Backend의 Tomcat Thread·Connection 수, Python API의 Worker 수와
동시 요청 처리 방식, Backend 연결 단계의 Connection Timeout, 요청마다 새로 생성되던
`httpx.AsyncClient`의 Connection Pool 비효율, UUID 빈 문자열 처리 누락과 로깅 코드 오류,
Kong·Nginx의 SSE Buffer·Timeout 설정, 외부 AI API의 응답시간·Retry 횟수까지 확인했다.

**해결** — Backend Connection Pool 크기를 확장하고 `httpx.AsyncClient`를 Singleton으로
재사용해 TCP Connection Pool을 유지했다. Backend 연결이 일정 시간 이상 지연되면 요청을
종료하고 최대 3회 재시도하도록 했다. UUID의 `None`·빈 문자열 처리 로직을 수정하고, SSE
Metadata·결과 로그를 정리했다. Kong·Nginx의 SSE Buffer·Timeout을 조정하고, Gateway/Backend/
외부 AI API의 오류 로그를 계층별로 분리했다.

**결과** — 일간 504 오류를 100건 이상에서 약 1건 미만 수준으로, 월간 약 6,000건 수준의 SSE
오류를 대폭 완화했다. 잔여 오류는 3~5분 이상 걸리는 장기 요청과 외부 AI 응답 지연 중심으로
계속 모니터링하고 있다.

### 6. Proxy Whitelist 누락으로 인한 GPT 통신 장애

**상황** — 개발계에서 GPT API를 호출하면 Backend가 JSON 응답 대신 `Access Denied` HTML
페이지를 반환했다. 애플리케이션 요청은 정상 생성됐지만 GPT Server까지 전달되지 않았다.

**원인** — 기존 네트워크 경로에 신규 Proxy가 추가됐는데, 신규 Proxy에서 Backend Server로
이어지는 통신 경로가 Whitelist에 반영되지 않았다.

**해결** — HTML 응답과 상태 코드로 애플리케이션이 아닌 중간 Proxy 문제로 범위를 좁히고,
요청 경로의 Proxy·방화벽 정책을 확인했다. Proxy에서 Backend Server로 연결되는 IP·Port를
Whitelist에 추가하고, Application Pod와 Worker Node에서 각각 통신을 재검증했다.

**결과** — 개발계 GPT Server 통신이 정상화됐고, 외부 AI 연결 장애 시 Application·Proxy·
Firewall 계층을 구분해 점검하는 절차를 정립했다.

### 7. NodeNotReady 장애 분석

**상황** — 개발계 Worker Node가 일시적으로 `NodeNotReady`가 됐다가 다시 `Ready`로 복구됐다.
kubelet 로그에는 Container Runtime 응답 실패와 PLEG 비정상 상태가 기록돼 있었다.

**분석** — kubelet, CRI-O, Kernel, Core Dump 로그를 같은 시간대로 맞춰 분석했다.

```
Gunicorn Process Core Dump
        ↓
CRI-O Container 종료 지연
        ↓
Runtime RPC DeadlineExceeded
        ↓
kubelet PLEG·Housekeeping 지연
        ↓
NodeNotReady
```

OOM·Kernel Warning은 없었고, kubelet Housekeeping이 약 11분 동안 지연됐다. CRI-O에서
Container 종료 Timeout이 발생했고, 같은 시간대에 특정 Gunicorn Process의 `SIGABRT` Core
Dump가 발생했다. Container ID를 역추적해 MCP SSE Server Pod로 원인 범위를 좁혔다.

**후속 조치** — 대상 Pod에 CPU·Memory request·limit을 적용하고 자원 여유가 있는 Node로
재배치했다. inotify Watch 한도를 상향하고, 재발 시 CPU Steal·Run Queue·I/O Wait·Memory·
Disk·Network 상태를 확인할 수 있도록 `sar` 수집 환경을 구성했다. Core Dump와 Runtime 로그를
보존하도록 장애 점검 절차를 정리했다.

**결과** — 장애와 연관된 Pod·Runtime 구간까지 원인 범위를 좁혔고, 재발 시 자원 고갈·I/O
지연·Runtime 문제를 정량적으로 판별할 수 있는 진단 환경을 마련했다.

## 성과

- 3만 명 이상이 사용하는 기업용 AI 플랫폼의 개발계·운영계 인프라 운영
- 개발계·운영계·유틸리티 및 금융권 고객사 폐쇄망 Kubernetes 환경 관리
- H100·A100·V100 포함 90장 이상의 GPU 자원 운영, 자체 LLM 포함 약 60개 모델 서비스 관리
- 주 1회 이상, 회당 4개 이상의 신규 모델 배포 — 요청부터 CI/CD·Ingress·API 서빙까지 약 1시간 이내
- H100 4장에 MIG를 적용해 최대 12개의 독립 GPU 자원 단위 구성
- 회의록 Kafka 처리 성공률 약 70% → 99%로 개선
- GPT·SSE 504 오류 일 100건 이상 → 약 1건 미만으로 감소
- 32B급 모델의 NAS 로딩 병목을 분석하고 GPU Node Local Cache 적용
- CRI-O Proxy 누락으로 발생한 외부 Registry `ImagePullBackOff` 해결
- Kong·Kafka·DB·GPU·Kubernetes·Linux 계층을 연계한 장애 분석 체계 구축
- 금융권 완전 폐쇄망 환경에 기업용 AI 플랫폼 구축·운영 지원
- 외부 고객용 AWS OpenAPI와 온프레미스 모델 환경 간 네트워크 연동 운영
- 일평균 1~5건의 운영 문의와 장애 대응 수행

## 회고

AI 플랫폼의 장애는 단일 애플리케이션이나 GPU 계층만 봐서는 원인을 찾기 어렵다는 점을
경험했다. 하나의 AI 요청은 Kong, Backend, Kafka, Database, Model Server, GPU, 외부 AI
API까지 여러 계층을 거친다. GPT·SSE 504 장애도 Gateway Timeout 조정만으로는 해결되지
않았고, Backend Thread, HTTP Connection Pool, 요청 처리 코드, SSE Buffer, 외부 AI 응답시간을
계층별로 확인해야 했다.

또한 Kafka Consumer Group, CRI-O Proxy, NAS 모델 로딩처럼 애플리케이션 외부의 설정이 서비스
성공률과 배포시간에 직접 영향을 준다는 점을 확인했다. 반복되는 장애는 개별 명령어 대응에
그치지 않고 공통 점검 항목과 운영 체크리스트로 정리했다.

향후에는 다음을 개선하고 싶다.

- GPT·SSE API의 p50·p95·p99와 Endpoint별 SLO 정의
- Kong, Backend, 외부 AI 요청에 대한 분산 추적 도입
- Kafka Consumer Lag·리밸런싱·처리 성공률 대시보드 구축
- 모델별 GPU·HBM 사용량과 요청량을 연결한 Capacity Planning
- MIG Profile별 모델 성능 및 비용 효율 벤치마크
- NAS와 Node Local Cache의 모델 버전·용량 자동 관리
- Vault를 운영계까지 확대하고 Secret Rotation 자동화
- NodeNotReady 발생 시 `sar`, Core Dump, Runtime 로그 자동 수집
- CPU Throttling, DB Connection, 외부 API Retry를 포함한 운영 Runbook 고도화
- 장기 SSE 요청을 비동기 작업과 결과 조회 방식으로 분리하는 구조 검토
