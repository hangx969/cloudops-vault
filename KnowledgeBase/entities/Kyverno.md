---
title: Kyverno
tags:
  - knowledgebase/entity
  - docker-kubernetes/security
  - kyverno
date: 2026-10-20
sources:
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter]]"
aliases:
  - Kyverno 策略引擎
---

# Kyverno

## 简介

Kyverno 是 Kubernetes 原生策略引擎，名称来自希腊语中的“govern”，于 2026 年 4 月从 CNCF 毕业。它通过 CRD 定义策略，在准入阶段验证或变更资源，也可以生成、验证镜像或清理配套资源。传统 ClusterPolicy 以 YAML 模式及 JMESPath 编写，较新的策略类型使用 CEL。

## 核心功能

- **验证（Validate）**：检查镜像来源、资源声明、运行权限等；Audit 记录违规，Enforce 拒绝不合规请求。
- **变更（Mutate）**：注入默认配置、添加标签或改写镜像地址；需要处理与 GitOps 期望状态的差异。
- **生成（Generate）**：根据 Namespace 等触发资源创建 ResourceQuota、LimitRange、NetworkPolicy 或其他配套资源。
- **镜像验证（Image Verify）**：校验容器镜像的签名与来源。
- **清理（Cleanup）**：按规则清理过期或不再需要的资源。
- **报告集成**：Policy Reporter 单独读取策略报告，提供 UI 和通知，不属于自动安装的内置 GUI。

## 架构

匹配的 API 请求经过准入链后才持久化，变更发生在最终验证之前：

```text
kubectl apply → API Server → Mutating Webhook → Validating Webhook → etcd
```

generate 等异步控制器动作还需检查下游资源和控制器权限，不能只看准入请求成功。

## 策略类型演进

1.18 公告建议从传统策略迁移到较新的类型；实际支持状态与迁移差异应按目标版本确认：

| 旧类型 | 新类型 | 说明 |
| --- | --- | --- |
| ClusterPolicy (validate) | ValidatingPolicy | 基于 CEL 的验证策略 |
| ClusterPolicy (mutate) | MutatingPolicy | 基于 CEL 的变更策略 |
| ClusterPolicy (generate) | GeneratingPolicy | 资源生成策略 |
| ClusterPolicy (imageVerify) | ImageValidatingPolicy | 镜像验证策略 |
| CleanupPolicy | DeletingPolicy | 资源清理策略 |

## 使用场景

- 限制 Pod 使用 Harbor 等受信任镜像仓库，或按命名空间改写 Artifactory 镜像地址。
- 检查非 root、privileged、hostPath、资源声明、标签、探针及 Service 类型。
- 为多租户命名空间生成资源配额和默认配置。
- 自动为资源添加标签、注解及镜像拉取配置。
- 在 CI 中通过 `kyverno apply` / `kyverno test` 验证策略与资源样本。

## 部署与运行边界

- 主文保留的 Chart `3.2.7` 对应 Kyverno `v1.12.6`，需要与较新 CEL 实战区分；高可用按各控制器配置副本与 PDB。
- `background: false` 不扫描未再提交的存量资源；`Audit` 不会关闭 mutate 或 generate。
- `failurePolicy` 处理 Webhook 调用失败，与 Audit/Enforce 处理策略违规的职责不同。
- 服务端 dry-run 用于验证准入链，离线 CLI 用于策略测试；两者都不能单独证明实际业务已成功运行。

## 相关概念与实体

- 策略即代码（Policy as Code）：将资源规范、例外和测试纳入版本管理。
- [[KnowledgeBase/entities/Kubernetes]]：运行平台与准入机制。
- [[KnowledgeBase/entities/Helm]]：Chart 与环境配置管理。
- [[KnowledgeBase/concepts/RBAC]]：控制器操作与策略例外的权限边界。
- [[Docker-Kubernetes/k8s-security-auth/helm部署trivy-operator|Trivy Operator]]：漏洞扫描与 Kyverno 的准入、镜像验证能力互补。

## 在本仓库中的覆盖

- [[Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter|Helm 部署 Kyverno 和 Policy Reporter]]：部署、十组策略、Harbor 与 Smart Remote 实战、测试、灰度上线及 1.18 迁移。
- [[KnowledgeBase/sources/kyverno-1.18-summary|Kyverno 部署与策略实践摘要]]：主文知识点及版本边界。
- [[KnowledgeBase/sources/k8s-security-auth-batch-summary|安全认证批量摘要]]：在 Kubernetes 安全工具链中的定位。

## 知识空白

- Kyverno 与 OPA/Gatekeeper 的系统性对比。
- 基于 CEL 的 ValidatingPolicy 编写实战。
- 多集群策略分发与例外治理。
- AI governance 策略定义实践。
