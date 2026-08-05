---
title: "외국인 근로자 실시간 음성 번역 서비스"
---

## 개요

건설 현장의 외국인 근로자에게 안전조례를 약 20개 언어로 실시간 전달하는 서비스입니다. AWS 인프라와
EKS를 Terraform으로 설계·구축했고, 시범 운영을 거쳐 실제 약 5개 건설 현장, 약 2,000명이 사용하는
서비스로 전환했습니다.

## 인프라 구조

- 3개 AZ의 Public/Private Subnet, Private EKS API, SSM Bastion, NAT EIP, ALB·NLB·WAF·Route 53 구성
- 앱·PostgreSQL·빌드용 Node Group을 분리하고 label·taint·affinity 적용
- HPA로 Backend Pod를 1~5개로 확장, Karpenter로 app Node 자동 증설
- Jenkins 동적 Agent·ECR·ArgoCD 기반 CI/CD 및 롤백 구축
- Prometheus·Grafana·Loki·Alloy로 CloudWatch 로그 비용 절감 및 Pod 모니터링
- AWS 인프라를 Terraform 변수로 고객사별 재사용 가능하게 설계, 사내 H200과 고정 NAT IP로 연동

## 부하 테스트 & 트러블슈팅

- Artillery로 40개 방 × 200명, 총 8,000명 규모의 동시 WebSocket·실제 번역 부하 테스트 수행
- HPA scale-out 시 Pod의 로컬 상태 불일치로 발생한 WebSocket 장애를 분석하고, Redis 기반 공유
  상태로 해결
- WebSocket 종료 후 API Pod 메모리가 증가하는 문제를 `kubectl top`·`docker stats`로 발견하고
  cleanup 로직 개선
