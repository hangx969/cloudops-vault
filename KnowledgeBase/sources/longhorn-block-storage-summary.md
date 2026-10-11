---
title: Longhorn 轻量块存储来源摘要
tags:
  - knowledgebase/source
  - kubernetes/storage
date: 2026-10-04
aliases:
  - Longhorn 架构与运维摘要
---

# Longhorn 轻量块存储来源摘要

## 元信息

- **原始文档**：[[开源存储Longhorn，K8s的轻量块存储|开源存储Longhorn，K8s的轻量块存储]]
- **外部来源**：[Aspirer2004 原文](https://mp.weixin.qq.com/s/LZX1go03KjwCv_XC3oiqJQ)，发布于 2026-09-19
- **领域**：Kubernetes 存储
- **摄入日期**：2026-10-04

## 摘要

文章解释 Longhorn 为何面向中小规模和边缘 Kubernetes 集群采用每卷独立引擎与多副本模型，以及同步复制、快照、集群外备份和 Dashboard 的作用。v2 引擎采用 SPDK，文章同时讨论 NVMe、大页内存、迁移规划及性能实测要求。最后比较云盘、Longhorn、Ceph RBD 与 Rook 的职责和使用场景，强调副本放置、备份目标和预留空间应在投产前规划。

## 关键知识点

1. **每卷独立管理**：每个卷由一个引擎和多个副本组成；这是逻辑实例模型，不能直接推导为每卷固定四个 Pod，实际托管方式见正文校核。
2. **故障域与放置**：副本应分散到不同节点；节点标签、磁盘标签和预留空间用于适配 SSD/HDD 等不同硬件与业务。
3. **同步复制**：已确认的写入由多个副本保护，写延迟受网络和磁盘影响；原文“串行复制链”的表述与官方并行写 IO 说明有出入。
4. **重建有条件**：原文将重建概括为增量同步，但官方区分完整、增量和快速重建，不能保证所有故障恢复都只传差异。
5. **三层数据保护**：副本防硬件故障，快照用于回滚和克隆，集群外 S3 兼容存储或 NFS 备份用于灾难恢复；增量快照仍需要容量规划。
6. **标准接口与运维**：CSI、StorageClass、PVC、VolumeSnapshot 对接 Kubernetes，Recurring Job 按卷调度快照、备份与保留策略，Dashboard 展示健康状态和事件。
7. **v1/v2 并存**：原文以 1.12.0 为 v2 GA 节点，按 StorageClass 区分引擎并规划迁移；性能改善为官方宣称，不能替代目标环境的压测和故障演练。
8. **职责与选型**：Longhorn 提供存储，Rook 运维 Ceph 等系统；不同后端的 StorageClass 可在同一集群并存，选择应考虑规模、性能要求与运维能力。

## 涉及的概念与实体

- [[KnowledgeBase/concepts/StorageClass]]：按存储类选择后端、引擎和副本放置策略。
- [[KnowledgeBase/concepts/高可用架构]]：节点故障域、存储冗余及引擎恢复期间的 IO 中断。
- [[KnowledgeBase/entities/Kubernetes]]：CSI 和控制器编排。
- [[KnowledgeBase/entities/Rancher]]：Longhorn 的项目起源及 SUSE 生态。
- [[KnowledgeBase/entities/NFS]]：集群外备份目标之一。

## 值得注意

- 原文对每卷 Pod 数量、串行复制链、重建方式、快照空间和故障后果存在简化或出入，相关实现应结合官方资料理解；“安装后即可投产”和性能预期仍是原文主张。
- 本文中的部署、迁移、压测与故障演练说明未作实操验证；仓库已有的 [[AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM|基于 K8s 部署 vLLM 和 LiteLLM]] 可用于阅读单节点 Longhorn 安装、PVC 使用与磁盘容量排障实例。
