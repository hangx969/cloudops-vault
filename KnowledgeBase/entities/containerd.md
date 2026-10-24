---
title: containerd
tags:
  - knowledgebase/entity
  - container-runtime
date: 2026-04-17
sources:
  - "[[Docker-Kubernetes/k8s-installation-management/k8s-cgroup-v2深度解析-迁移实战与避坑指南]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/24-k8s基础-容器运行时-containerd]]"
  - "[[Docker-Kubernetes/k8s-installation-management/升级/k8s迁移容器运行时-版本升级]]"
  - "[[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤]]"
  - "[[Docker-Kubernetes/k8s-installation-management/升级/k8s-1.37-升级须知-breaking-changes]]"
  - "[[Docker-Kubernetes/k8s-image-management/Harbor 部署与使用指南]]"
  - "[[Docker-Kubernetes/k8s-ai-gpu/k8s配置NVIDIA GPU]]"
  - "[[Docker-Kubernetes/CKA-CKS/CKS-备考]]"
---

## 简介

containerd 是从 Docker 中剥离出的工业级容器运行时，自 Kubernetes 1.24 起成为默认容器运行时（取代 dockershim）。它实现了 CRI（Container Runtime Interface）标准，负责镜像管理、容器生命周期管理和底层存储/网络。

## 核心功能

- **镜像管理**：拉取、存储、分发容器镜像
- **容器生命周期**：创建、启动、停止、删除容器
- **CRI 实现**：标准化接口对接 kubelet
- **cgroup v2 支持**：≥ 1.6 完整支持，需配置 `SystemdCgroup = true`（v2 环境必须与 kubelet cgroupDriver 保持一致）

## 使用场景

- 作为 kubeadm 部署 K8s 集群的节点容器运行时，配置 SystemdCgroup、pause 镜像和镜像加速
- 把存量集群节点的运行时从 Docker 迁移到 containerd，或在升级 K8s 前把 containerd 升级到受支持的版本
- 对接 Harbor 等私有镜像仓库（TLS、认证与 mirror 配置）
- 为 GPU 节点配置 NVIDIA 运行时，或通过 RuntimeClass 使用 runsc（gVisor）等额外运行时
- 集群故障、kubectl 不可用时，在节点上用 nerdctl 或 crictl 查看容器

## 相关概念与实体

- [[KnowledgeBase/concepts/容器运行时|容器运行时]]：containerd 所属的概念类别
- [[KnowledgeBase/entities/Docker|Docker]]：containerd 从 Docker 项目中剥离而来
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：K8s 1.24+ 默认运行时
- [[KnowledgeBase/entities/AKS|AKS]]：Azure AKS 默认使用 containerd
- [[KnowledgeBase/entities/Harbor|Harbor]]：containerd 从 Harbor 私有仓库拉取镜像的 Registry 配置
- [[KnowledgeBase/entities/NVIDIA|NVIDIA]]：用 nvidia-ctk 为 containerd 配置 NVIDIA 运行时

## 在本仓库中的覆盖

- `Docker-Kubernetes/k8s-installation-management/` 中涉及 containerd 作为 K8s 运行时的配置
- `Docker-Kubernetes/k8s-basic-resources/` 中涉及容器运行时选型
- [[Docker-Kubernetes/k8s-installation-management/k8s-cgroup-v2深度解析-迁移实战与避坑指南|K8s cgroup v2：资源隔离原理、迁移与生产避坑]]：containerd cgroup v2 配置与迁移踩坑
- Azure AKS 集群默认使用 containerd 运行时
- [[Docker-Kubernetes/k8s-basic-resources/24-k8s基础-容器运行时-containerd|k8s基础-容器运行时-containerd]]：CRI 接口与调用链（Docker → containerd → runc），ctr、nerdctl、crictl 对比，以及 ctr 命名空间的注意事项
- [[Docker-Kubernetes/k8s-installation-management/升级/k8s迁移容器运行时-版本升级|k8s迁移容器运行时-版本升级]]：把节点运行时从 Docker 迁移到 containerd（生成配置、调整 kubelet 参数与节点注解）
- [[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤|安装k8s-1.35-基于rockylinux10-最新步骤]]：安装 containerd，启用 SystemdCgroup、替换 pause 镜像，并用 config_path + hosts.toml 配置镜像加速
- [[Docker-Kubernetes/k8s-installation-management/升级/k8s-1.37-升级须知-breaking-changes|k8s-1.37-升级须知-breaking-changes]]：K8s 移除对 containerd 1.x 的支持，containerd 升级 SOP，以及 CRI API 与镜像格式的兼容陷阱
- [[Docker-Kubernetes/k8s-image-management/Harbor 部署与使用指南|Harbor 部署与使用指南]]：在 containerd 中配置 Harbor 的 TLS、认证与 mirror，以及 crictl、nerdctl 使用的证书目录
- [[Docker-Kubernetes/k8s-ai-gpu/k8s配置NVIDIA GPU|k8s配置NVIDIA GPU]]：用 nvidia-ctk 为 containerd 配置 NVIDIA 运行时并验证
- [[Docker-Kubernetes/CKA-CKS/CKS-备考|CKS-备考]]：创建指向 runsc 处理程序的 RuntimeClass，让 Pod 运行在 gVisor 上

## 知识空白

- 仓库中尚无 containerd 快照器（snapshotter）原理与选型的说明，相关内容只出现在默认配置文件中
- 仓库中尚无 containerd 自身监控指标的采集与告警实践
- 仓库中尚无 containerd 与 CRI-O 等其他 CRI 运行时的对比分析
