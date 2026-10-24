---
title: K8s PodDisruptionBudget 实战
tags:
  - knowledgebase/source
  - docker-kubernetes/k8s
  - high-availability
date: 2026-10-24
sources:
  - "[[Docker-Kubernetes/k8s-basic-resources/17-k8s-PodDisruptionBudget实战]]"
aliases:
  - PDB实战摘要
---

# K8s PodDisruptionBudget 实战

## 元信息
- **原始文档**：[[Docker-Kubernetes/k8s-basic-resources/17-k8s-PodDisruptionBudget实战]]
- **领域**：Kubernetes / 高可用
- **摄入日期**：2026-06-06

## 摘要
讲解 PodDisruptionBudget（PDB）如何约束 Eviction API 驱逐，并区分节点排空、控制器滚动更新与非自愿故障。覆盖两种预算配置、百分比取整、服务与 Worker 场景、常见陷阱，以及完整 Deployment/PDB 和驱逐验证示例。

## 关键知识点
1. PDB 约束经过 Eviction API 的驱逐；`kubectl drain` 默认使用该接口。直接删除、Deployment 滚动更新及节点故障不受它阻止，但这些操作造成的不健康副本会减少可用预算。
2. `minAvailable` 与 `maxUnavailable` 二选一，百分比均向上取整。3 副本配置 `minAvailable: "80%"` 要求保留 3 个健康副本，`maxUnavailable: "20%"` 则允许 1 个不可用。
3. Deployment 的 `maxUnavailable/maxSurge` 约束 rollout，PDB 约束 Eviction；两者分别设计，不能认为 PDB 会阻止控制器删除旧 Pod。
4. 检查单副本或预算等于总副本数时能否维护、HPA 最小副本数下的取整结果，以及 selector 范围。`policy/v1` 中 `{}` 选择命名空间内所有 Pod，未设置或 null 则不选择 Pod。
5. 文中三副本示例使用 Deployment `maxUnavailable: 0/maxSurge: 1` 与 PDB `minAvailable: 2`，还需就绪探针、优雅终止与可调度容量；这不是所有支付服务的通用保障。
6. 查看 `ALLOWED DISRUPTIONS`、PDB 健康统计、Pod Ready 状态及实际维护错误；Eviction 测试会真实驱逐测试 Pod，被预算阻止时返回 429。`--force` 不绕过 PDB，`--disable-eviction` 改用直接删除。

## 涉及的概念与实体
- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/concepts/高可用架构]]

## 值得注意
- PDB 是知识库中 K8s 基础资源的补充——已有 Pod/Deployment/Service/RBAC/CRD 等，PDB 补齐了"中断保护"这一维度
- 与 HPA（扩缩容）存在交互关系，配置时需联动考虑
- 文章的四大陷阱是生产环境高频踩坑点，可作为 PDB 配置的检查清单
