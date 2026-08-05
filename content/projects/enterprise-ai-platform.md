---
title: "기업용 AI 플랫폼 · OpenAPI 구축/운영"
---

## 개요

3만 명 이상이 사용하는 기업용 AI 플랫폼의 개발·운영과 금융권 폐쇄망 Kubernetes 환경 운영을 담당했습니다.
2025년 3월부터 현재까지 진행 중인 프로젝트입니다.

## 인프라 구조

- kubeadm·CRI-O·Cilium 기반 클러스터, Kong과 사내 LB를 활용한 AI API Gateway 관리
- H100·A100·V100 GPU 90장 이상, AI 모델 약 60개의 배포·자원 관리
- H100 4장에 MIG(Multi-Instance GPU)를 적용해 최대 12개의 독립 GPU 단위로 분할, 모델 배치 효율화
- AWS OpenAPI와 온프레미스 H100·V100 간 방화벽·네트워크 연동

## CI/CD & 운영

- Jenkins·Harbor·Argo CD·Helm 기반 CI/CD로 신규 모델을 약 1시간 이내 서빙
- Prometheus·Grafana와 Kubernetes·Linux 로그로 GPU, CPU, DB, Network, NodeNotReady 등 장애 분석

## 트러블슈팅

- STT·NLP Kafka Consumer Group과 복구 정책을 개선해 서비스 처리 성공률을 30%에서 99%로 끌어올렸습니다.
- Connection Pool·SSE Buffer·Timeout을 개선해 GPT 504 오류를 하루 100건 이상에서 2~5건 수준으로
  줄였습니다.
