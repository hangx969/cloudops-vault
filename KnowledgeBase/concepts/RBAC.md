---
title: RBAC
tags:
  - knowledgebase/concept
  - kubernetes/security
date: 2026-10-11
sources:
  - "[[Docker-Kubernetes/k8s-basic-resources/18-k8s基础-认证-授权-准入]]"
  - "[[kuebctl-插件krew]]"
aliases:
  - Role-Based Access Control
  - 基于角色的访问控制
---

# RBAC

## 定义
RBAC（Role-Based Access Control，基于角色的访问控制）是 Kubernetes 自 1.6 版本起采用的授权机制。其核心思路是将对资源的操作权限定义到角色（Role/ClusterRole）中，再通过绑定（RoleBinding/ClusterRoleBinding）将角色赋予用户、组或 ServiceAccount，从而实现细粒度的 API 访问控制。

## 核心要点
- **Role vs ClusterRole**：Role 是命名空间级别的权限定义，仅作用于所在 Namespace 的资源；ClusterRole 是集群级别的权限定义，可用于集群范围资源（如 Node）、非资源端点（如 /healthz）以及跨命名空间的资源
- **RoleBinding vs ClusterRoleBinding**：RoleBinding 将 Role 或 ClusterRole 绑定到指定 Namespace 内的主体；ClusterRoleBinding 将 ClusterRole 绑定到集群范围内的主体
- **Subjects（主体）**：可绑定的主体包括 User、Group、ServiceAccount 三种类型
- **Rules 定义**：通过 apiGroups、resources、resourceNames、verbs 四个字段精确控制权限范围。verbs 包括 get、list、watch、create、update、patch、delete 等操作
- **ServiceAccount 与 RBAC 配合**：SA 可作为 Pod 内应用访问 API Server 的身份凭证，通过 RBAC 绑定实现应用级别的权限控制
- **RBAC 只能添加权限，不支持显式拒绝**：无法通过 RBAC 规则显式禁止某项操作
- **K8s 内置面向用户的 ClusterRole**：cluster-admin（最高权限）、admin、edit、view，可直接用于常见授权场景
- **RoleBinding 绑定 ClusterRole 的技巧**：用户通过 RoleBinding 绑定到 ClusterRole 时，仅获得 RoleBinding 所在命名空间的权限，适用于多命名空间复用同一权限定义的场景

- **权限排查顺序**：whoami 核对当前身份，rolesum 查看目标主体的角色来源，who-can 从操作反查具有 RBAC 权限的主体，再用 auth can-i 检查目标身份的授权结果。角色分析需要读取相应资源；使用 --as 模拟身份还需要 impersonation 权限，授权成功也不代表实际操作一定通过准入策略

## 与其他概念的关系
- [[KnowledgeBase/entities/Kubernetes]]：RBAC 是 K8s 安全体系中认证-授权-准入三层架构的授权层核心机制
- [[KnowledgeBase/concepts/CRD]]：自定义资源（CRD）同样需要通过 RBAC 授权才能被访问和操作

## 在本仓库中的覆盖
- [[Docker-Kubernetes/k8s-basic-resources/18-k8s基础-认证-授权-准入]]：完整覆盖了 RBAC 的概念、Role/ClusterRole 定义、RoleBinding/ClusterRoleBinding 用法、ServiceAccount 与 RBAC 配合、生产环境权限管理实践（ns查询、日志查看、命令执行、资源编辑等场景）以及准入控制器

- [[kuebctl-插件krew|kubectl 插件指南]]：whoami、rolesum、who-can 与 auth can-i 的分工、CI ServiceAccount 的 Forbidden 排查，以及静态 RBAC 分析和实际授权查询的边界

## 知识空白
- 尚未深入覆盖 RBAC 审计（Audit）与 rakkess 工具
- 尚未覆盖 RBAC 与 OPA/Gatekeeper 策略引擎的配合使用
- 尚未覆盖 RBAC aggregation（聚合 ClusterRole）机制
