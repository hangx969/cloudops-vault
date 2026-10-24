---
title: Operator 模式
tags:
  - knowledgebase/concept
  - kubernetes/extensibility
date: 2026-05-04
sources:
  - "[[Docker-Kubernetes/k8s-basic-resources/21-k8s基础-自定义CRD资源]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/Operator部署Redis集群]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/Operator部署mysql集群]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/helm部署strimzi-kafka]]"
aliases:
  - Operator Pattern
  - K8s Operator
---

# Operator 模式

## 定义

Operator 模式是 Kubernetes 中将 CRD（自定义资源定义）与自定义 Controller 相结合的开发模式，用于将复杂有状态应用的运维知识编码为软件。通过 Operator，用户可以像管理原生 K8s 资源一样，以声明式方式管理数据库、缓存、消息队列等复杂系统的部署、扩缩容、备份、恢复等运维操作。

## 核心要点

- Operator 由两部分组成：CRD（定义资源模型）+ Controller（监视资源状态并执行控制逻辑）
- 工作流程：找到 Operator（operatorhub.io 或 GitHub） -> 部署 Controller -> 创建 CRD -> 创建自定义资源实例
- 适合复杂有状态应用（数据库、缓存、消息队列），简单微服务更适合用 Helm
- Operator 开发需要 Go 语言知识，但大多数主流中间件已有社区维护的 Operator
- 本仓库中覆盖的 Operator 实例：
  - OT-Redis-Operator：注册 RedisCluster CRD，声明式创建 Redis 集群（3主3从）
  - MySQL NDB Operator：注册 NdbCluster CRD，管理 NDB Cluster 分布式数据库
  - Strimzi Operator：注册 Kafka/Topic/User 等 CRD，管理生产级 Kafka 集群
  - KubeBlocks Operator：统一管理 30+ 种数据库和有状态中间件

## 与其他概念的关系

- [[KnowledgeBase/concepts/CRD]]：Operator 基于 CRD 扩展 K8s API，CRD 是 Operator 的基础
- [[KnowledgeBase/entities/Kubernetes]]：Operator 是 K8s 原生的扩展模式，体现声明式 API 的设计哲学
- [[KnowledgeBase/entities/Prometheus]]：Prometheus Operator 是社区中最知名的 Operator 之一
- [[KnowledgeBase/concepts/高可用架构]]：Operator 常用于自动化管理有状态服务的高可用部署
- [[KnowledgeBase/entities/Helm]]：Helm 与 Operator 互补，Helm 适合简单部署，Operator 适合需要持续运维的复杂应用
- [[KnowledgeBase/concepts/Finalizer]]：Operator 的 Controller 通常在 Reconcile 循环中通过 Finalizer 实现资源删除前的外部资源清理逻辑，清理逻辑必须幂等

## 在本仓库中的覆盖

- [[Docker-Kubernetes/k8s-basic-resources/21-k8s基础-自定义CRD资源]]：Operator 的定义、组成（CRD + Controller）、使用步骤、与 Helm 的对比
- [[Docker-Kubernetes/k8s-db-middleware/Operator部署Redis集群]]：OT-Redis-Operator 部署 Redis 集群的完整实践
- [[Docker-Kubernetes/k8s-db-middleware/Operator部署mysql集群]]：MySQL NDB Operator 部署分布式数据库集群
- [[Docker-Kubernetes/k8s-db-middleware/helm部署strimzi-kafka]]：Strimzi Operator 部署 Kafka 集群，展示 CRD 资源的层次化管理

## 知识空白

- Operator 开发框架（kubebuilder、Operator SDK）的实战使用
- Operator 的生命周期管理（OLM - Operator Lifecycle Manager）
- Operator 的测试策略和最佳实践
- Operator 的安全考量（RBAC 权限、准入控制）
