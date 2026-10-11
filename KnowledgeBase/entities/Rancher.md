---
title: Rancher
tags:
  - knowledgebase/entity
  - kubernetes/management
date: 2026-10-04
sources:
  - "[[Docker-Kubernetes/k8s-UI-tools/rancher(v2.6.4)管理k8s集群]]"
  - "[[Docker-Kubernetes/container-platform/部署轻量级的K8S平台-K3S]]"
  - "[[Azure/Jfrog-artifactory-Azure]]"
  - "[[开源存储Longhorn，K8s的轻量块存储]]"
aliases:
  - SUSE Rancher
---

## 简介

Rancher 是 SUSE 旗下的企业级 Kubernetes 多集群管理平台，提供统一的 Web UI 管理多个 K8s 集群（本地、云端、边缘）。同时也是 K3S（轻量级 K8s 发行版）的母公司，在 IoT/边缘计算场景有广泛应用。

## 核心功能

- **多集群管理**：通过 Web UI 集中管理多个 K8s 集群，支持导入已有集群（在目标集群执行导入命令后，agent 运行在 cattle-system 命名空间）
- **工作负载管理**：在 UI 中创建命名空间、Deployment、Service、Ingress 等资源，不熟悉 K8s 概念的用户也能部署容器
- **多云支持**：支持 AWS、Azure、Google Cloud 等云提供商
- **安全与访问控制**：提供用户认证、访问控制、镜像安全扫描等能力
- **应用商店**：通过 Catalog 浏览和安装预定义的应用模板

## 使用场景

- 统一管理混合云与本地数据中心中的多个 K8s 集群
- 为不熟悉 K8s 的用户提供图形化的应用部署入口
- 用单个 Docker 容器快速部署 Rancher，纳管实验集群
- 边缘计算、物联网场景使用 Rancher 维护的 K3s 发行版

## 相关概念与实体

- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：Rancher 管理的目标平台
- [[KnowledgeBase/concepts/高可用架构|高可用架构]]：Rancher 自身的 HA 部署
- [[KnowledgeBase/entities/Helm|Helm]]：本仓库中的 Rancher 以 Docker 单容器方式部署，尚无 Helm 部署记录（见知识空白）
- [[KnowledgeBase/entities/Docker|Docker]]：以 Docker 容器方式运行 Rancher
- [[KnowledgeBase/entities/Ingress|Ingress]]：在 Rancher UI 中创建 Ingress 规则发布应用
- [[KnowledgeBase/entities/AKS|AKS]]：尝试通过 Rancher 导入 AKS 集群，因区域识别问题中止

- [[KnowledgeBase/sources/longhorn-block-storage-summary|Longhorn 来源摘要]]：Rancher Labs 发起的独立存储项目，提供 Kubernetes 块存储；SUSE Harvester 将其作为存储底座

## 在本仓库中的覆盖

- `Docker-Kubernetes/k8s-UI-tools/` 中涉及 Rancher 作为 K8s UI 管理工具
- `Docker-Kubernetes/container-platform/` 中涉及 K3S 和 Rancher 在边缘/IoT 场景的应用
- 与 Dashboard、Lens、k9s 等 K8s UI 工具形成生态对比
- [[Docker-Kubernetes/k8s-UI-tools/rancher(v2.6.4)管理k8s集群|rancher(v2.6.4)管理k8s集群]]：Rancher 介绍与优势、Docker 方式部署、导入已有 K8s 集群，并在 UI 中创建 Deployment、Service 与 Ingress（附未解决的域名访问问题）
- [[Docker-Kubernetes/container-platform/部署轻量级的K8S平台-K3S|部署轻量级的K8S平台-K3S]]：Rancher 维护的 K3s 发行版的特点、安装、节点加入与高可用部署，以及 AutoK3s 工具
- [[Azure/Jfrog-artifactory-Azure|Jfrog-artifactory-Azure]]：在 VM 中运行 Rancher 容器并尝试导入 AKS，因区域识别问题中止

- [[开源存储Longhorn，K8s的轻量块存储|Longhorn 轻量块存储]]：Rancher Labs 的存储项目起源、SUSE/CNCF 发展背景和 Harvester 使用场景

## 知识空白

- 仓库中尚无通过 Helm 在 K8s 上高可用部署 Rancher 的实践，现有部署均为单容器方式
- 仓库中尚无使用 Rancher 创建和托管 RKE、RKE2 集群的内容
- 仓库中尚无 Rancher 的备份恢复与版本升级流程
- 仓库中尚无 Rancher Fleet 等 GitOps 能力的使用
