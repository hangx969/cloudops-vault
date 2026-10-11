---
title: K8s 1.37 原生 HPA Scale-to-Zero 与 KEDA 迁移实践
tags:
  - knowledgebase/source
  - kubernetes/autoscaling
  - docker-kubernetes/scaling
date: 2026-09-15
sources:
  - "[[Docker-Kubernetes/k8s-scaling/k8s-HPA-VPA]]"
aliases:
  - HPA Scale-to-Zero 摘要
  - HPAScaleToZero 摘要
---

# K8s 1.37 原生 HPA Scale-to-Zero 与 KEDA 迁移实践

## 元信息

- **来源文章**：[告别 KEDA：K8s 1.37 原生 HPA Scale-to-Zero 落地实战](https://mp.weixin.qq.com/s/HBmYINXQDECAR664aF31mQ?scene=1&click_id=1921215008)
- **整合文档**：[[Docker-Kubernetes/k8s-scaling/k8s-HPA-VPA#五、Kubernetes 1.37 原生 HPA Scale-to-Zero|Kubernetes 自动扩缩容实战 → Scale-to-Zero]]
- **来源作者**：WAKE UP技术
- **发布时间**：2026-08-13
- **领域**：Kubernetes HPA、External/Object 指标、事件驱动扩缩容与 Worker 成本优化
- **摄入日期**：2026-09-06

## 摘要

本文介绍来源文章所述的 Kubernetes 1.37 Beta `HPAScaleToZero`，说明原生 HPA 如何基于 External/Object 指标把队列消费者和其他异步 Worker 缩到 0。文章给出了控制面特性门控、`autoscaling/v2` HPA、Prometheus Adapter 外部指标链路、稳定窗口和扩容策略的配置示例，并讨论冷启动、就绪探针、指标源故障和双重控制等生产风险。最后给出延迟敏感度分类和从 KEDA 平滑迁移的三阶段清单。

## 关键知识点

1. Resource（CPU/内存）指标无法在 0 副本时表达每 Pod 平均需求；Scale-to-Zero 需要与副本数无关的 External/Object 指标。
2. Kubernetes 官方文档将 `HPAScaleToZero` 标为 1.37 起 Beta 且默认启用；kube-apiserver 与 kube-controller-manager 都必须启用该门控。
3. HPA 示例使用 `minReplicas: 0`、`maxReplicas: 20`、`autoscaling/v2` 和队列指标 `queue_messages_visible`，以 `AverageValue: "1"` 避免零目标值成为计算分母，并配置 300 秒缩容稳定窗口。
4. Prometheus 可以采集队列深度或 Kafka consumer group lag，经 Prometheus Adapter 暴露为 `external.metrics.k8s.io`，供 HPA 读取。
5. HPA 中的 `metric.name` 必须与 Adapter 显式暴露的指标名一致，否则指标会显示 `<unknown>`，扩缩容无法按预期工作。
6. 从 0 拉起 Worker 会经历调度、拉镜像、启动进程、建立依赖连接和预热；镜像预拉、节点池亲和、readinessProbe 和消息重试可以降低风险。
7. 延迟敏感、同步、SLA 严苛的负载通常应保留 `minReplicas: 1`；异步、批处理、队列消费者和 webhook receiver 更适合缩到 0。
8. KEDA 仍适合直接连接 Kafka、RabbitMQ、AWS SQS 等事件源；原生 HPA 适合已有 External 指标链路、希望减少额外组件的场景。
9. 迁移期间不能让原生 HPA 和 KEDA 的 ScaledObject 同时管理同一个 Deployment；应使用不同 Deployment 进行并行观察，再切换流量。
10. Scale-to-Zero 后应将“期望副本数为 0 且指标源健康”视为正常态，重点告警指标源不可达以及队列有积压但副本长期为 0。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/Prometheus|Prometheus]]
- [[Docker-Kubernetes/k8s-scaling/k8s-HPA-VPA|K8s 自动扩缩容：HPA、VPA 与 Scale-to-Zero]]
- [[Docker-Kubernetes/k8s-scaling/k8s-基于KEDA的弹性能力|KEDA：事件驱动扩缩容与 KServe 实战]]
- [[Docker-Kubernetes/k8s-scaling/k8s-HPA-VPA#五、Kubernetes 1.37 原生 HPA Scale-to-Zero|HPA Scale-to-Zero 章节]]

## 值得注意

- 2026-09-15 已对照 Kubernetes 官方 HPA 与 feature gate 文档校正版本状态和目标值表达；上线前仍应核对目标发行版与集群实际行为。
- `HPAScaleToZero` 的缩零能力依赖 External/Object 指标和指标适配链路；Prometheus、Prometheus Adapter、APIService 和 HPA 指标名需要逐层验证。
- 示例强调的是异步 Worker 的成本与延迟权衡，不能把缩零能力直接套用到低延迟 API、长连接服务或需要预热缓存的服务。
