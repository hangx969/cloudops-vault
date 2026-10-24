---
title: kubectl apply 背后的真相：为什么 Server-side Apply 正在成为标配
tags:
  - knowledgebase/source
  - kubernetes/apply
  - kubernetes/ssa
date: 2026-09-12
aliases:
  - Server-side Apply 来源摘要
---

# kubectl apply 背后的真相：为什么 Server-side Apply 正在成为标配

## 元信息

- **原始文档**：[[Docker-Kubernetes/k8s-basic-resources/02-k8s基础-yaml-apply]]
- **领域**：Kubernetes 声明式配置与字段所有权
- **摄入日期**：2026-09-12

## 摘要

文章对比 Client-side Apply（CSA）和 Server-side Apply（SSA）的差异。CSA 依赖 last-applied、live state 与新 manifest 的三路合并，多工具共同修改同一对象时可能静默覆盖；SSA 将结构化差异计算和字段所有权追踪放到 API Server，通过 `managedFields` 暴露冲突。文章进一步说明 CRD schema 对列表合并语义的影响，以及 Helm 4 release 迁移到 SSA 时的兼容性和冲突处理。

## 关键知识点

1. CSA 会先读取 live state，在本地计算 strategic merge patch；列表的 map/atomic 语义来自 OpenAPI schema。
2. last-applied 注解只在 `kubectl apply` 时更新，HPA、Operator 等绕过该注解的修改可能被后续 apply 静默覆盖。
3. SSA 使用 `application/apply-patch+yaml`，由 API Server 负责 create-or-update、字段所有权记录和冲突检测。
4. `managedFields` 记录每个 field manager 拥有的字段；排障时可通过 `--show-managed-fields` 查看归属。
5. 缺少结构化 schema 的 CRD 列表会按 atomic 处理；CRD 作者应正确声明 `x-kubernetes-list-type` 和 `x-kubernetes-list-map-keys`。
6. Helm 3/Helm 4 混用可能令 release 在 SSA 与客户端更新之间切换，迁移前应审查既有字段所有权冲突。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/entities/Helm]]
- [[KnowledgeBase/entities/ArgoCD]]

## 值得注意

- SSA 的冲突提示不是异常副作用，而是把 CSA 可能隐藏的字段争用显式化。
- 对已有资源迁移 SSA 前，应先查看 `managedFields`，识别 kubectl、Helm、Argo CD、Operator 等管理器的字段边界。
- 文章关于 Helm 4 默认行为属于来源撰写时的版本语境，实际迁移时仍应结合当前 Helm 版本验证。
