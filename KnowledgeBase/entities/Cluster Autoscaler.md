---
title: Cluster Autoscaler
tags:
  - knowledgebase/entity
  - kubernetes/autoscaling
date: 2026-10-11
sources:
  - "[[Docker-Kubernetes/k8s-scaling/K8s Cluster Autoscaler]]"
  - "[[Docker-Kubernetes/k8s-scaling/k8s-HPA-VPA]]"
  - "[[Docker-Kubernetes/k8s-scaling/k8s成本优化方案-FinOps实战]]"
aliases:
  - Kubernetes Cluster Autoscaler
  - 节点自动扩缩容
---

# Cluster Autoscaler

## 简介

Cluster Autoscaler（CA）依据 Pod 的调度需求调整 Kubernetes Worker 节点数。当新增节点能够解决 Pod 无法调度的问题时，它扩容节点组；当节点长期低利用且重要 Pod 可以安全迁移时，它回收节点。

## 核心功能

- **扩容模拟**：结合 requests、标签、污点、亲和性和存储约束，判断新增节点能否容纳待调度 Pod。
- **节点组选择**：通过 expander 选择要扩容的 Node Group，并遵守节点组的最小值和最大值。
- **安全缩容**：检查其他节点是否能接收 Pod，通过 Eviction API 驱逐，并遵守 PDB 与迁移保护条件。
- **运行观测**：提供日志、状态 ConfigMap 与 Prometheus 格式指标，用于检查扩缩容失败和节点组容量上限。

## 使用场景

- HPA 增加副本后，现有节点容量不足，需要补充可调度的节点。
- 业务负载下降后，在满足 Pod 迁移条件的前提下回收长期不需要的节点。
- 已围绕 ASG、VMSS 或 MIG 建立节点组管理体系，希望接入 Kubernetes 节点弹性。

## 相关概念与实体

- [[KnowledgeBase/concepts/自动扩缩容]]：HPA、VPA、事件驱动伸缩与节点扩缩容各有不同职责。
- [[KnowledgeBase/entities/Kubernetes]]：提供调度、requests、PDB 和 Pod 生命周期机制。
- [[KnowledgeBase/entities/Helm]]：安装 CA 并配置镜像版本、Provider 和自动发现。
- [[KnowledgeBase/entities/Prometheus]]：采集 CA 指标，监控未调度 Pod、扩缩容结果和容量上限。
- [[KnowledgeBase/concepts/高可用架构]]：缩容需要兼顾副本可用性、优雅终止与数据迁移。

## 在本仓库中的覆盖

- [[Docker-Kubernetes/k8s-scaling/K8s Cluster Autoscaler]]：节点组选择、缩容保护、生产部署、调优、排障、上线验证与回滚。
- [[Docker-Kubernetes/k8s-scaling/k8s-HPA-VPA]]：CA 在自动扩缩容体系中的位置，以及 requests 与 HPA/VPA 的关系。
- [[Docker-Kubernetes/k8s-scaling/k8s成本优化方案-FinOps实战]]：CA 与 Karpenter 的成本和节点选型比较；其中“CA 仅缩容空节点”的表述与节点迁移机制不一致，参见 [[KnowledgeBase/sources/k8s-cluster-autoscaler-summary#值得注意]]。

## 知识空白

- AWS、Azure、GCP、AliCloud 等平台的完整权限与节点组配置示例。
- 从零节点启动时的节点模板、多可用区与卷调度验证。
- 本仓库尚未记录本篇扩容、缩容与回滚流程的实际执行结果。
