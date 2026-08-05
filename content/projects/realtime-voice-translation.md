---
title: "외국인 근로자 실시간 음성 번역 서비스"
---

_2026.03 ~ 2026.05_

## 개요

D 건설사 건설 현장에서는 한국인 관리자가 아침 안전조례와 작업 지시를 한국어로 전달하지만,
외국인 근로자가 내용을 정확히 이해하기 어려운 문제가 있었다.

이를 해결하기 위해 관리자의 음성을 실시간으로 수집하고, 자체 STT 모델과 번역 서비스를 통해 약
20개 언어로 변환한 뒤 외국인 근로자의 휴대전화 웹 화면에 전달하는 실시간 번역 서비스를 구축했다.

관리자가 웹에서 방을 생성하고 QR 코드를 공유하면, 근로자는 별도의 애플리케이션 설치 없이 QR
코드로 접속해 자신의 언어를 선택할 수 있다. 관리자의 음성은 약 0.6초 단위로 처리되며, 건설 현장
전문용어의 번역 정확도를 높이기 위해 건설 용어집 기반 RAG를 번역 과정에 적용했다.

프로젝트는 시범 운영을 거쳐 실제 서비스로 전환됐으며, 현재 약 5개 건설 현장에서 약 2,000명이
사용하고 있다. 초기 목표인 동시 접속 8,000명을 기준으로 부하 테스트를 수행했고, 향후 16,000명까지
확장할 수 있도록 인프라를 설계했다.

## 역할

프론트엔드 1명, 백엔드 1명, 인프라 2명, PM 1명으로 구성된 5인 프로젝트에서 인프라 담당으로
참여했다. AWS 계정과 기존 H200 모델 서버를 제외한 **AWS 인프라, EKS, CI/CD, 모니터링, Redis,
PostgreSQL 운영 환경을 처음부터 설계하고 구축**했다.

**직접 수행한 업무**

- 전체 AWS 및 Kubernetes 아키텍처 설계
- Terraform 기반 VPC, Subnet, NAT Gateway, EKS, Node Group, Bastion, ECR, ALB, NLB, WAF, Route 53, IAM 구성
- 3개 AZ에 Public·Private Subnet을 분리한 네트워크 설계, Private EKS API + SSM Bastion 운영 접근 체계
- NAT Gateway와 Elastic IP를 통한 외부 통신 IP 고정
- 일반 애플리케이션·PostgreSQL·빌드 도구 전용 노드 그룹 분리, label/taint/toleration/node affinity 기반 배치 정책
- HPA를 통한 Pod 확장과 Karpenter를 통한 Node 확장 구성
- Helm 기반 Jenkins, ArgoCD, Redis, 모니터링 도구 배포
- Jenkins Kubernetes 동적 에이전트 + ECR 기반 CI 파이프라인, ArgoCD 기반 GitOps 배포·롤백 체계
- PostgreSQL, PgBouncer, Prisma 연동 환경 구축
- Prometheus, Grafana, Loki, Alloy 기반 모니터링·로그 환경 구축 (CloudWatch 비용 절감 목적)
- Artillery 기반 8,000명 동시 접속 부하 테스트 참여, Pod 메모리 증가 및 WebSocket scale-out 장애 분석
- H200 모델 서버와 AWS 간 통신을 위한 NLB·Nginx 및 고정 IP 경로 구성

**협업한 업무**

- 백엔드의 WebSocket 상태 공유 및 Redis 적용
- 자체 STT 모델과 AWS 서비스 간 연동, 건설 용어집 기반 번역 RAG 적용
- 부하 테스트 시나리오 작성 및 클라이언트 테스트
- H200 서버와 중계 서버 연동

## 구조도

_실제 구조도 이미지는 추후 추가 예정입니다. 우선 텍스트로 정리합니다._

```
[한국인 관리자] → 방 생성/마이크 입력/QR 공유 → [Web Frontend]
        │ WebSocket
        ▼
[AWS Public Entry: Route 53 → WAF → Public ALB]
        ▼
┌─────────────────────────────────────────────┐
│              Private EKS Cluster            │
│                                              │
│  [app Node Group]        [app-db Node Group] │
│  Frontend/Backend API/    PostgreSQL 전용     │
│  WebSocket/Redis Client   (taint 적용)        │
│                                              │
│  [build Node Group]                          │
│  Jenkins / ArgoCD                            │
│                                              │
│  HPA: Pod 1~5개 · Karpenter: app Node 자동 확장│
└──────────────────┬───────────────────────────┘
                   │ NLB / 고정 통신 경로
                   ▼
        [사내 중계 서버]
        Room별 AWS Backend WebSocket 1개
        H200 STT 요청 중계 · 결과 분배
                   ▼
        [H200 Model Server]
        STT · NLP/번역 · 건설 용어집 RAG · TTS
        Nginx 단일 포트 라우팅
                   ▼
        선택 언어로 WebSocket 전달 → [외국인 근로자 모바일 웹]
```

**운영 및 배포 구조**

```
운영자 PC → AWS SSM → Bastion EC2 → Private EKS API → kubectl / helm

GitLab → Jenkins 동적 Agent Pod → BuildKit 이미지 빌드 → Amazon ECR Push
       → Helm Image Tag 반영 → ArgoCD Sync → EKS Rolling Update
```

## 문제 및 해결

### 1. HPA 확장 시 WebSocket 상태 불일치

**문제** — 초기에는 WebSocket 방 정보와 연결 상태가 각 Backend Pod의 메모리에 관리됐다. 부하
증가로 HPA가 Backend Pod를 여러 개로 확장하자 동일한 방의 사용자 연결이 서로 다른 Pod에
분산됐고, 각 Pod가 다른 Pod의 방 상태를 알 수 없어 ping 메시지와 번역 결과가 정상 전달되지
않았다.

**분석** — Artillery 부하 테스트 중 scale-out 시점에 WebSocket 실패를 확인했다. 애플리케이션
로그에는 명확한 예외가 남지 않았지만, 단일 Pod에서는 정상 동작하고 다중 Pod 환경에서만
문제가 발생해 Pod 로컬 메모리에 의존한 상태 관리 문제로 판단했다.

**해결** — EKS 내부에 Helm 기반 Redis를 배포하고, Backend가 공통 Room·연결 상태를 공유할 수
있도록 Redis 접속 환경을 제공했다. Backend 개발자와 Redis endpoint·연결 규격을 조율하고,
HPA scale-out·scale-in 환경에서 WebSocket 연결과 메시지 전달을 재검증했다.

**결과** — Pod가 1개에서 최대 5개까지 확장되는 환경에서도 WebSocket 방 상태와 번역 결과가
정상적으로 전달되는 것을 확인했다. Redis 기반 공유 상태 환경을 구축해 다중 Pod 간 상태
불일치 문제를 해결했다.

### 2. 장시간 부하에서 API Pod 메모리 증가

**문제** — 부하 테스트 중 API Pod의 메모리 사용량이 시간에 따라 계속 증가하는 현상을
확인했다. Backend Pod에는 아래와 같은 resource 제한이 적용돼 있었고, 증가가 지속되면 HPA
확장과 서비스 불안정으로 이어질 가능성이 있었다.

```
resources:
  requests:
    cpu: "250m"
    memory: "256Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

**분석** — Bastion에서 `kubectl top pod`로 Pod별 CPU·메모리를 실시간 확인하고, 개발 환경에서는
`docker stats`로 서비스별 메모리 증가를 추적했다. WebSocket 종료 이후에도 메모리가 정상
수준으로 반환되지 않는 것을 확인해, 번역 요청·WebSocket 종료 과정에서 일부 버퍼 또는 연결
객체가 정리되지 않는 것으로 판단했다.

**해결** — WebSocket disconnect·exception 경로에서 연결 객체와 번역 작업을 정리하도록
Backend를 수정하고, 종료 후 남아 있는 요청·버퍼 참조를 제거하도록 개선했다. 수정 후 동일
부하를 재현해 검증하고, Grafana·Prometheus로 Pod 리소스 변화를 지속 확인할 수 있도록 구성했다.

**결과** — 부하 종료 이후 API Pod의 메모리 사용량이 정상 수준으로 회복되는 것을 확인했으며,
OOMKilled로 이어지기 전 메모리 누수 가능성을 발견하고 개선했다.

### 3. 8,000명 동시 접속 WebSocket 부하 검증

**문제** — 여러 건설 현장에서 동시에 사용될 예정이었고, 고객 요구사항으로 최대 8,000명의
동시 접속을 안정적으로 처리해야 했다. 한 방에는 최대 200명이 접속하고, 총 40개 방에서 음성
인식과 번역 결과가 실시간으로 전달되는 구조였다.

**해결** — Artillery로 WebSocket 연결과 실제 번역 요청 부하를 생성해 40개 방에 방당 200명을
접속시켜 총 8,000명 동시 접속을 테스트했다. 0.6초 단위 음성 데이터와 실제 번역 API 호출을
포함해 1시간 이상 연결을 유지하며 검증했다. HPA는 CPU·메모리 사용률 80% 기준으로 Backend
Pod를 최소 1개~최대 5개까지 자동 확장하고, 수용량이 부족하면 Karpenter가 app Node를 최대
3대까지 확장하도록 구성했다. 부하 종료 후에는 약 30분의 안정화 시간을 두고 scale-in되도록
설정했다.

**결과** — `40개 방 × 방당 200명`의 총 8,000명 동시 접속 환경에서 WebSocket 연결 및 실제
번역 결과 전달을 검증했다. 고객 요구사항인 3초 이내 전달 기준을 충족했고, 테스트 환경에서는
대부분 약 1초 이내에 번역 결과가 전달됨을 확인했다.

### 4. Private EKS와 외부 모델 서버 간 고정 통신 경로 구축

**문제** — AWS 서비스와 사내 H200 모델 서버 간 통신이 필요했지만, 사내 방화벽은 허용된 고정
IP와 제한된 포트만 열 수 있었다. 또한 향후 다른 고객사에 서비스를 제공할 경우 고객사별 AWS
인프라는 새로 생성하되, 사내 중계 서버와 H200 모델 서버는 공통으로 사용해야 했다.

**해결** — Private Subnet의 outbound 통신을 NAT Gateway의 Elastic IP 하나로 고정하고, 사내
방화벽에 이 고정 NAT IP를 허용하도록 구성했다. NLB로 고정된 inbound 연결 경로를 제공하고,
사내 중계 서버를 AWS와 H200 사이의 공통 연결 계층으로 설계했다. H200 서버에는 제한된 포트
하나만 개방하고 Nginx로 STT·NLP 요청을 내부 서비스에 라우팅했다. 고객사별 인프라는 Terraform
변수만 변경해 재구축할 수 있도록 모듈화했다.

**결과** — 고객사별 AWS 환경을 독립적으로 배포하면서도 기존 중계 서버 및 H200 모델 인프라를
재사용할 수 있는 구조를 구축했다.

### 5. 워크로드 특성에 따른 EKS 노드 격리

**문제** — 일반 서비스, PostgreSQL, Jenkins 빌드는 CPU·메모리 사용 특성이 서로 달랐다. 특히
Jenkins 빌드나 DB 부하가 실시간 WebSocket 서비스와 같은 노드에서 발생하면 서비스 안정성에
영향을 줄 수 있었고, PostgreSQL의 EBS PVC는 가용 영역에 종속되므로 노드 재배치도 고려해야 했다.

**해결** — 노드 그룹을 `app`(Frontend·Backend·WebSocket 등 일반 서비스), `app-db`(PostgreSQL·
PgBouncer 전용), `build`(Jenkins·ArgoCD 등 빌드)로 분리했다. 각 노드 그룹에 label·taint를
적용하고 Helm values의 toleration·node affinity로 Pod 배치를 강제했다. PostgreSQL은 EBS
PVC의 AZ 종속성을 고려해 app-db 노드를 특정 AZ에 고정했다.

**결과** — 빌드·DB·실시간 서비스 간 자원 경합을 줄이고, 각 워크로드의 확장·장애 범위를 분리했다.

### 6. CloudWatch 비용을 고려한 관측 환경 구축

**문제** — EKS 및 Pod 로그를 CloudWatch에 장기간 저장할 경우 운영 비용이 증가할 것으로 예상됐다.

**해결** — Prometheus로 Pod·Node 메트릭을 수집하고 Grafana 대시보드로 CPU·메모리·Pod 상태를
확인했다. Alloy로 로그를 수집하고 Loki로 저장·검색했으며, Jenkins·ArgoCD와 함께 build
노드에 운영 도구를 배치했다.

**결과** — CloudWatch 의존도를 줄이면서, 애플리케이션 로그와 Pod 모니터링을 자체 환경
(Prometheus·Grafana·Loki·Alloy)에서 확인할 수 있는 체계를 구축했다.

## 성과

- D 건설사 외국인 근로자를 위한 실시간 음성 번역 서비스의 AWS 인프라를 Terraform으로 처음부터 구축
- 시범 운영 이후 실제 서비스로 전환되어 약 5개 현장, 약 2,000명 사용
- 약 20개 언어의 실시간 STT·번역 결과 제공, 건설 전문용어 번역을 위한 용어집 기반 RAG 연동
- `40개 방 × 200명` 기준 8,000명 동시 WebSocket 부하 테스트 통과, 고객 요구사항 3초 이내 전달 충족
- HPA로 Backend Pod를 1~5개까지 확장, Karpenter로 app Node 자동 증설
- 다중 Pod 환경의 WebSocket 상태 불일치를 분석하고 Redis 공유 상태 환경 구축
- Pod 메모리 증가 현상을 모니터링으로 발견하고 WebSocket·번역 요청 cleanup 개선 지원
- EKS API를 private only로 구성, SSM Bastion을 통한 운영 접근 적용
- NAT Elastic IP로 사내 H200 모델 서버와의 outbound IP 고정
- 일반 서비스·PostgreSQL·빌드 워크로드를 전용 노드 그룹으로 격리
- Jenkins·ECR·ArgoCD 기반 CI/CD 및 롤백 체계, Prometheus·Grafana·Loki·Alloy 기반 모니터링 구축
- 고객사별 AWS 환경을 Terraform 변수 변경으로 재사용할 수 있는 구조 설계

## 회고

실시간 AI 서비스의 확장성은 단순히 Pod 수를 늘리는 것만으로 확보되지 않는다는 점을
경험했다. WebSocket처럼 연결 상태를 유지하는 서비스는 Pod 로컬 메모리에 세션·방 정보를
저장하면 scale-out 이후 상태가 분산될 수 있어, 애플리케이션 상태를 외부 저장소로 분리하고
스케일 인·배포 시 기존 연결을 안전하게 종료하는 구조가 필요하다는 점을 확인했다.

또한 Terraform과 EKS를 처음부터 구성하면서 보안·비용·운영 편의성 사이의 균형을 고려했다.
Private EKS API와 SSM Bastion을 적용했지만, 비용 제약으로 NAT Gateway를 단일 구성하고
PostgreSQL을 EKS 내부 단일 Pod로 운영하는 등 가용성보다 비용을 우선한 결정도 있었다.

향후 개선한다면 다음을 적용하고 싶다.

- Terraform state를 S3 backend로 이전하고 state locking 적용
- 개발·검증·운영 환경별 tfvars 및 state 분리
- NAT Gateway 다중 AZ 구성 또는 VPC Endpoint 확대
- PostgreSQL을 RDS Multi-AZ 또는 고가용성 DB 구조로 이전
- Redis 고가용성 및 영속화 정책 구성
- PodDisruptionBudget과 graceful shutdown 적용, WebSocket 연결이 남은 Pod의 scale-in 유예
- `preStop` hook과 `terminationGracePeriodSeconds`를 이용한 연결 종료 처리
- ArgoCD image updater 또는 승인 기반 이미지 태그 자동화
- 번역 지연, WebSocket 연결 수, 메시지 누락률을 정량화한 SLI·SLO 구성
- 16,000명 확장을 위한 다중 H200 모델 서버와 중계 서버 확장 전략 수립
