---
title: K8s健康探针重启风暴复盘
tags:
  - knowledgebase/source
  - docker-kubernetes/k8s-probe
date: 2026-09-06
aliases:
  - Pod探针重启风暴摘要
---

# K8s 健康探针重启风暴复盘

## 元信息

- **原始文档**：[[Docker-Kubernetes/k8s-basic-resources/k8s基础-pod#探针失效真实案例]]
- **领域**：Kubernetes / Pod / 健康探针
- **摄入日期**：2026-09-06

## 摘要

一次生产 Liveness Probe 参数收紧，将数据库连接池瞬时抖动误判为进程死亡，触发大量 Pod 重启。剩余副本承受更多流量后健康检查继续超时，故障进一步传播到依赖服务，形成重启风暴。复盘说明 Liveness、Readiness 和 Startup Probe 必须职责分离，并通过灰度变更、探针监控和故障演练验证参数。

## 关键知识点

1. Liveness 只应检查重启能够修复的进程内部故障，不能把数据库、缓存、消息队列等外部依赖波动直接转化为重启。
2. Readiness 应先通过摘流提供恢复空间；破坏性的 Liveness 重启应更保守。
3. Startup Probe 将慢启动阶段与运行阶段分离，避免应用初始化期间被 Liveness 误杀。
4. 健康检查端点本身应轻量、限时并具有明确语义；/startup、/live、/ready 分别承担不同职责。
5. 探针批量变更属于高风险操作，需要灰度、快速回滚、重启率告警和依赖变慢故障演练。
6. PDB 不能阻止 Liveness 触发的容器重启，HPA 的最小副本数也不能保证副本保持 Ready。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/concepts/高可用架构]]
- [[KnowledgeBase/sources/k8s-pdb-summary|K8s PDB 实战]]
- [[KnowledgeBase/sources/k8s-basic-resources-batch-summary|K8s 基础资源]]

## 值得注意

- 原文提出的 Liveness 与 Readiness 容忍窗口倍数是经验性建议，不是 Kubernetes 通用公式。
- 原文给出的 Prometheus 指标名是示意形式，实际指标取决于探针观测方案。
- PDB 与 HPA 各有保护边界，不能把它们视为探针重启风暴的直接防线。
