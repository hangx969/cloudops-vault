---
title: Ceph
tags:
  - knowledgebase/entity
  - storage/ceph
date: 2026-10-11
sources:
  - "[[Docker-Kubernetes/k8s-storage/开源存储Ceph]]"
  - "[[Docker-Kubernetes/k8s-storage/分布式存储全景-架构与发展路线]]"
aliases:
  - Ceph Storage
  - Ceph 存储平台
---

# Ceph

## 简介

Ceph 是在通用服务器上构建的分布式存储平台，通过 RADOS 对象层统一承载 RBD 块设备、RGW 对象接口和 CephFS 文件系统。CRUSH 计算数据放置，PG 管理对象分组及副本恢复，MON 维护权威地图和仲裁。

## 核心功能

- RBD：面向虚拟机和应用卷的块接口，支持快照与克隆。
- RGW：S3 兼容的 HTTP 对象接口，可横向扩展并配置多站点同步。
- CephFS：由 MDS 管理目录元数据的共享文件系统。
- 数据保护：副本或纠删码、故障恢复、scrub 与 deep scrub。
- 编排与监控：cephadm 或 Rook 管理集群，MGR 提供管理模块和指标。

## 使用场景

- OpenStack、Proxmox 等私有云的虚拟机磁盘。
- 需要共享硬件与维护体系的块、对象和文件服务。
- 数据集、模型和产物的长期存储，按负载配合缓存或并行访问层。
- 有持续扩展需求并具备相应维护能力的平台。

## 相关概念与实体

- [[KnowledgeBase/concepts/分布式存储]]：数据放置、冗余、一致性与恢复的具体实现。
- [[KnowledgeBase/concepts/StorageClass]]：通过 Ceph CSI 暴露 RBD / CephFS 卷。
- [[KnowledgeBase/concepts/高可用架构]]：MON quorum、OSD 故障域和池的副本策略。
- [[KnowledgeBase/entities/Kubernetes]]：Rook 编排与 CSI 卷接入。
- [[KnowledgeBase/entities/Prometheus]]、[[KnowledgeBase/entities/Grafana]]：指标采集和容量、恢复状态观察。

## 在本仓库中的覆盖

- [[Docker-Kubernetes/k8s-storage/开源存储Ceph|Ceph：架构原理、部署与 Kubernetes 集成]]：原理、硬件、恢复、成本、发行版和完整旧版示例。
- [[Docker-Kubernetes/k8s-storage/分布式存储全景-架构与发展路线]]：Ceph 在统一存储发展路线中的位置。
- [[KnowledgeBase/sources/ceph-storage-summary]]：关键机制和示例版本边界。

## 知识空白

- 当前版本 cephadm / Rook 与 Ceph CSI 的完整可执行部署清单。
- 生产故障演练、备份恢复和滚动升级的实测记录。
- 同一硬件上的 RBD、RGW、CephFS 与纠删码性能对比。
