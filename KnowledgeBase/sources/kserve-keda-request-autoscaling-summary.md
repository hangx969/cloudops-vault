---
title: KServe + KEDA 实战：基于请求指标实现服务自动扩缩容
tags:
  - knowledgebase/source
  - kubernetes/autoscaling
  - kubernetes/serving
date: 2026-09-06
aliases:
  - KServe KEDA 请求指标扩缩容摘要
---

# KServe + KEDA 实战：基于请求指标实现服务自动扩缩容

## 元信息

- **原始文档**：[[Docker-Kubernetes/k8s-scaling/k8s-基于KEDA的弹性能力#KServe + KEDA：基于请求指标的模型服务实战|KEDA 事件驱动自动扩缩容中的 KServe 实战]]
- **领域**：Kubernetes 模型服务、请求指标监控与自动扩缩容
- **摄入日期**：2026-09-06

## 摘要

本文通过一个 KServe + vLLM Demo，展示如何使用 KEDA 查询 Prometheus 中的请求指标，并将结果通过 External Metrics API 提供给 HPA。示例使用 `vllm:num_requests_running` 与 `vllm:num_requests_waiting` 之和作为扩缩容信号，结合 KServe Predictor、HAMi DRA GPU 共享和 ServiceMonitor，验证服务从 1 个副本扩到 2 个、负载停止后再缩回 1 个副本。

## 关键知识点

1. 扩缩容链路为：KServe Predictor Deployment → vLLM `/metrics` → Prometheus → KEDA → External Metrics API → HPA。
2. KEDA 2.17.2 不仅需要 Operator，还需要 `external.metrics.k8s.io` Metrics API Server 正常可用；只有 CRD 就绪并不代表 HPA 能读到指标。
3. `running + waiting` 同时反映正在执行和排队中的请求，比单独使用 CPU 或内存更贴近推理服务的请求压力。
4. KServe 的 `autoscalerClass: keda`、`minReplicas`、`maxReplicas` 和 `autoScaling.metrics` 可直接声明外部 Prometheus 指标及目标值。
5. Prometheus Stack 需要通过 ServiceMonitor 选择 KServe 生成的 Predictor Service；Prometheus Operator 会将 EndpointSlice 中的每个 Predictor Pod 作为独立 Target。
6. 示例中 `target.value: 1`、`minReplicas: 1`、`maxReplicas: 2`，负载值达到 2 时扩容；HPA 缩容稳定窗口为 300 秒。
7. 单 GPU 节点通过 HAMi DRA 为每个副本申请 3Gi 显存和 20% GPU 核心，支持在 Demo 中运行两个 Predictor 副本。
8. 观察扩容应同时检查 Prometheus 查询、ScaledObject、HPA、Deployment 和 Pod；缩容还需考虑 KEDA 轮询、HPA 同步和模型 Pod 终止时间。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/Prometheus|Prometheus]]
- [[Docker-Kubernetes/k8s-scaling/k8s-基于KEDA的弹性能力|KEDA：事件驱动扩缩容与 KServe 实战]]
- [[Docker-Kubernetes/k8s-scaling/k8s-基于KEDA的弹性能力#KServe + KEDA：基于请求指标的模型服务实战|KServe 请求指标扩缩容章节]]

## 值得注意

- 本文记录的是 KServe、KEDA、kube-prometheus-stack 和 KServe GPU 镜像的实测 Demo，版本、字段和生成资源名称应以目标集群实际版本为准。
- 生产环境不应只看扩缩容对象是否创建成功，还要确认 External Metrics API、Prometheus Target、指标查询结果、模型加载时间和 GPU 调度都正常。
- 持续负载命令会一直运行并持续产生推理请求，验证结束后必须在压测终端按 `Ctrl+C` 停止。
