---
title: Finalizer
tags:
  - knowledgebase/concept
  - kubernetes/lifecycle
date: 2026-10-24
sources:
  - "[[Docker-Kubernetes/k8s-basic-resources/20-k8s基础-Finalizer与资源删除]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/10-k8s基础-namespace-资源分配]]"
  - "[[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础]]"
  - "[[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD Image Updater]]"
  - "[[Docker-Kubernetes/k8s-storage/k8s删除PVC后PV数据保护与复用避坑]]"
aliases:
  - Finalizers
  - 终结器
---

# Finalizer

## 定义

Finalizer 是 Kubernetes 资源对象 `metadata.finalizers` 字段中的字符串列表，本身是等待清理的标记，不包含可执行代码。只要该列表非空，apiserver 收到删除请求后不会立即从 etcd 移除对象，而是先设置 `deletionTimestamp` 使其进入 `Terminating` 状态，等待对应 Controller 执行清理逻辑并移除自己的 Finalizer，列表清空后对象才会被真正删除。

## 核心要点

- 存在意义：防止资源关联的外部资源（云盘、负载均衡器等）因 K8s 对象被删除而泄漏
- 删除流程：`kubectl delete` → 检查 `finalizers` 非空 → 设置 `deletionTimestamp` 进入 Terminating → Controller 观察到该时间戳并执行清理 → 清理完成后移除自身 Finalizer → 列表清空后对象才被真正从 etcd 删除
- 内置 Finalizer：`kubernetes.io/pvc-protection`（PVC 保护）、`kubernetes.io/pv-protection`（PV 保护）、`foregroundDeletion`（前台删除，等待依赖资源先删除）、`orphan`（孤儿删除，不自动删除依赖资源）
- 第三方 Operator/工具也广泛使用自定义 Finalizer，例如 ArgoCD 的 `resources-finalizer.argocd.argoproj.io`（确保删除 Application/AppProject 前先清理其管理的所有资源）；第三方条目应按实际资源和版本读取确认
- 资源"删不掉"的五大常见场景：① 对应 Controller 已被卸载、② Controller 清理逻辑报错（如外部 API 凭证过期）、③ Namespace 内某资源卡住导致整个 Namespace 卡在 Terminating、④ 前台级联删除等待带 finalizer 的下游对象，实际死锁还取决于清理代码、⑤ Controller 因节点/网络问题无法与 apiserver 通信
- 手动移除 Finalizer（`kubectl patch --type=merge -p '{"metadata":{"finalizers":null}}'`）等同于跳过清理逻辑，可能导致外部资源泄漏，应先尝试恢复 Controller，仅在已核实外部依赖和清理结果或明确接受残留风险后精确移除相应条目
- 开发 Operator 时的 Finalizer 实现原则：清理逻辑必须幂等、清理失败时不移除 Finalizer（返回 `RequeueAfter` 重试）、Finalizer 命名用 `域名/功能` 格式避免冲突、需处理部分清理进度
- 与 Pod 级别优雅终止机制的区分：Finalizer 保留 API 对象，`preStop` 与 `terminationGracePeriodSeconds` 控制容器退出；Pod 带 finalizer 时也可能已开始终止，两条过程不构成严格的先后关系

## 与其他概念的关系

- [[KnowledgeBase/concepts/CRD]]：删除 Namespace 会级联删除其下的自定义资源实例，若这些实例带有 Finalizer 且对应 Controller 异常，会导致 Namespace 卡在 Terminating
- [[KnowledgeBase/concepts/Operator模式]]：Finalizer 的清理逻辑通常由 Operator 的 Controller 在 Reconcile 循环中实现（`controllerutil.AddFinalizer`/`RemoveFinalizer`），是 Operator 模式管理资源全生命周期的关键环节
- [[KnowledgeBase/entities/Kubernetes]]：Finalizer 是 K8s 声明式删除模型的核心机制之一
- [[KnowledgeBase/entities/ArgoCD]]：ArgoCD 用 `resources-finalizer.argocd.argoproj.io` 确保删除 Application/AppProject 时级联清理其管理的所有下游资源

## 在本仓库中的覆盖

- [[Docker-Kubernetes/k8s-basic-resources/20-k8s基础-Finalizer与资源删除]]：Finalizer 的完整机制、内置/常见 Finalizer 清单、五大"删不掉"场景的诊断与修复、controller-runtime 中编写 Finalizer 的完整代码示例、与 Graceful Shutdown 机制的区分
- [[Docker-Kubernetes/k8s-basic-resources/10-k8s基础-namespace-资源分配]]：Namespace 因 `spec.finalizers` 未清空卡在 Terminating 的实战修复脚本（导出 JSON 清空 finalizers 后 PUT 到 `/finalize` 端点）
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础]]、[[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD Image Updater]]：ArgoCD Application/AppProject 上配置 `resources-finalizer.argocd.argoproj.io` 的实际 YAML 用法
- [[Docker-Kubernetes/k8s-storage/k8s删除PVC后PV数据保护与复用避坑]]：说明 CSI 驱动和 `kubernetes.io/pvc-protection` 可能使 PVC 停留在 `Terminating`，强制清理前需确认外部资源已安全处理

## 知识空白

- Finalizer 与 Admission Webhook 的交互（Webhook 是否会拦截带 Finalizer 资源的更新请求）
- 大规模集群中残留 Finalizer 资源的批量巡检与告警方案
- OwnerReference + 垃圾回收（Garbage Collection）与 Finalizer 协同工作的完整案例
