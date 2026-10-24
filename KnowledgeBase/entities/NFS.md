---
title: NFS
tags:
  - knowledgebase/entity
  - storage
date: 2026-04-17
sources:
  - "[[Docker-Kubernetes/k8s-basic-resources/13-k8s基础-storage]]"
  - "[[Docker-Kubernetes/k8s-storage/helm部署nfs-subdir-external-provisioner]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署mysql主从高可用]]"
  - "[[Docker-Kubernetes/k8s-CICD/Gitlab/k8s部署Gitlab(11.8.1)-基于yaml]]"
  - "[[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.426.3)的Devops工具链-基于yaml]]"
  - "[[Linux-Shell/Ubuntu基础操作]]"
  - "[[HPC/CentOS7-slurm23.02-二进制安装]]"
aliases:
  - Network File System
---

## 简介

NFS（Network File System）是经典的网络文件系统协议，在 Kubernetes 中常用作 PV/PVC 的后端存储。NFS 部署简单但缺乏高可用性，适合开发测试环境和非关键数据持久化（如 Jenkins 工作空间、GitLab 数据），不推荐用于生产数据库。

## 核心功能

- **目录共享与挂载**：服务端在 `/etc/exports` 中导出目录并用 `exportfs -arv` 生效，客户端用 `mount -t nfs` 挂载，可写入 `/etc/fstab` 永久挂载
- **访问权限控制**：基于 RPC 的 AUTH_UNIX 认证要求客户端与服务端 UID/GID 一致，通过 `root_squash`、`no_root_squash`、`all_squash` 控制用户映射
- **多客户端共享**：多个 Pod 可同时挂载同一共享目录（ReadWriteMany）
- **K8s 持久化后端**：支持 Pod 直接挂载 nfs 卷、静态 PV/PVC，以及通过 nfs-subdir-external-provisioner 或 csi-driver-nfs 实现 StorageClass 动态供给
- **挂载选项调优**：在 StorageClass 的 `mountOptions` 中设置 `nfsvers`、`rsize`/`wsize` 等参数

## 使用场景

- 开发测试环境中为 Jenkins、GitLab、MySQL、Redis 等有状态服务提供持久化存储
- 为 K8s 集群提供动态 StorageClass，使 PVC 自动绑定 PV
- HPC 集群中由管理节点共享 `/software` 等目录，供计算节点挂载使用
- 单台 Linux 服务器上共享数据盘目录

## 相关概念与实体

- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：NFS 作为 K8s PV/PVC 后端
- [[KnowledgeBase/entities/Jenkins|Jenkins]]：使用 NFS 持久化工作空间
- [[KnowledgeBase/entities/GitLab|GitLab]]：使用 NFS 持久化数据
- [[KnowledgeBase/concepts/StorageClass|StorageClass]]：NFS Provisioner 动态存储
- [[KnowledgeBase/entities/MySQL|MySQL]]：学习环境中用 NFS 为 MySQL 提供持久化存储，笔记提示生产环境不推荐
- [[KnowledgeBase/entities/Prometheus|Prometheus]]：Prometheus 使用 NFS StorageClass 时的挂载选项优化与挂载失败排查
- [[KnowledgeBase/entities/Slurm|Slurm]]：HPC 集群通过 NFS 共享软件目录

## 在本仓库中的覆盖

- `Docker-Kubernetes/k8s-storage/` 中涉及 NFS 作为 PV 后端存储
- `Docker-Kubernetes/k8s-CICD/` 中涉及 Jenkins、GitLab 使用 NFS 持久化
- `Docker-Kubernetes/k8s-monitoring-logging/` 中涉及 Elasticsearch 使用 NFS 存储
- `Docker-Kubernetes/k8s-db-middleware/` 中涉及中间件存储方案
- [[Docker-Kubernetes/k8s-basic-resources/13-k8s基础-storage|k8s基础-storage]]：NFS 服务搭建与访问权限（squash 选项）、Pod 直接挂载、NFS PV/PVC 实验，以及基于 nfs-subdir 与 csi-driver-nfs 的 StorageClass
- [[Docker-Kubernetes/k8s-storage/helm部署nfs-subdir-external-provisioner|helm部署nfs-subdir-external-provisioner]]：NFS 服务端部署与客户端挂载测试，用 Helm 安装 nfs-subdir-external-provisioner 实现动态 PV
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶|Prometheus-Stack：生产部署与运维]]：NFS StorageClass 挂载选项优化，以及 NFS 挂载失败的排查步骤
- [[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署mysql主从高可用|k8s基于yaml部署mysql主从高可用]]：部署 nfs-subdir-external-provisioner，为 MySQL StatefulSet 提供持久化存储
- [[Docker-Kubernetes/k8s-CICD/Gitlab/k8s部署Gitlab(11.8.1)-基于yaml|k8s部署Gitlab(11.8.1)-基于yaml]]：NFS 共享目录配合静态 PV/PVC，为 GitLab、PostgreSQL、Redis 持久化数据
- [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.426.3)的Devops工具链-基于yaml|K8s DevOps 工具链：Jenkins 2.426.3]]：NFS 共享目录与 PV/PVC 持久化 Jenkins 数据
- [[Linux-Shell/Ubuntu基础操作|Ubuntu基础操作]]：在 Ubuntu 上用 nfs-kernel-server 共享目录，以及 `no_root_squash` 的安全提示
- [[HPC/CentOS7-slurm23.02-二进制安装|CentOS7-slurm23.02-二进制安装]]：HPC 控制节点通过 NFS 共享 `/software` 目录，计算节点挂载使用

## 知识空白

- 仓库中尚无 NFS 服务端高可用方案的实践，多篇笔记只提示其存在单点风险
- 仓库中尚无 NFSv4 基于 Kerberos 的认证与加密配置
- 仓库中尚无通过 NFS 协议接入云上托管文件存储（如阿里云 NAS）的实践
