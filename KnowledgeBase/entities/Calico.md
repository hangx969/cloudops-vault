---
title: Calico
tags:
  - knowledgebase/entity
  - kubernetes/networking
  - cni
date: 2026-10-20
sources:
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/MetalLB实战-裸机Kubernetes-LoadBalancer]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-Calico]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源]]"
  - "[[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤]]"
  - "[[Docker-Kubernetes/k8s-installation-management/2025最新-企业级高可用集群-基于rockylinux]]"
  - "[[Docker-Kubernetes/k8s-installation-management/k8s部署防火墙端口配置]]"
  - "[[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.394)的DevOps工具链-基于yaml]]"
  - "[[Docker-Kubernetes/CKA-CKS/CKA-备考]]"
---

## 简介

Calico 是 Kubernetes 生态中最流行的 CNI（Container Network Interface）网络插件之一，支持 IPIP 隧道和 BGP 直连两种网络模式。它提供网络策略（NetworkPolicy）支持，与 Service 网络和 Ingress 形成 K8s 三层网络协作体系。

## 核心功能

- **与 MetalLB 分工**：Calico 3.18 起可宣告 LoadBalancer 地址，MetalLB controller 负责分配 IP；需配置 Calico 的 `serviceLoadBalancerIPs`，并避免让两个组件建立冲突的 BGP 会话。FRR-K8s 不会自动合并 Calico 的既有会话，详见 [[Docker-Kubernetes/k8s-networking-service-mesh/MetalLB实战-裸机Kubernetes-LoadBalancer]]
- **Pod 网络**：为每个 Pod 分配独立 IP，跨主机的 Pod 可通过 IP 直接互访
- **多种网络模式**：支持 IPIP（节点上创建 tunl0 隧道）、BGP（节点作为 vRouter，不建隧道）、VXLAN 和 host-gw，通过 `CALICO_IPV4POOL_IPIP`、`CALICO_NETWORKING_BACKEND` 切换
- **网络安全策略**：提供网络流量控制和访问授权，支持网络隔离与多租户
- **核心组件**：Felix（每个节点上的 agent，负责网络接口、路由、ACL 等）、BIRD（BGP Client，分发 Felix 写入内核的路由）、BGP Route Reflector（大规模网络中集中分发路由）
- **网卡探测**：通过 `IP_AUTODETECTION_METHOD` 指定跨节点通信使用的网卡

## 使用场景

- kubeadm 或二进制方式部署 K8s 集群后，安装 Calico 作为 CNI 插件
- 节点间二层不通或跨子网部署时，使用 IPIP 模式（可设为 CrossSubnet）实现跨节点通信
- 大规模集群网络：笔记建议小规模集群选 Flannel、Weave Net，大规模集群选 Calico、Cilium
- 需要网络隔离或多租户的集群

## 相关概念与实体

- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：Calico 作为 K8s CNI 插件
- [[KnowledgeBase/entities/Ingress|Ingress]]：与 Calico 协作的三层网络之一
- [[KnowledgeBase/entities/ArgoCD|ArgoCD]]：部署中涉及 Calico DNS 问题
- [[KnowledgeBase/concepts/ServiceMesh|ServiceMesh]]：东西流量管理的上层方案

## 在本仓库中的覆盖

- [[Docker-Kubernetes/k8s-networking-service-mesh/MetalLB实战-裸机Kubernetes-LoadBalancer]]：BGP 会话冲突、IP 分配与宣告职责，以及 Calico / MetalLB 的共存条件。
- `Docker-Kubernetes/k8s-installation-management/` 中涉及 Calico CNI 部署
- `Docker-Kubernetes/k8s-basic-resources/` 中涉及 K8s 三层网络协作（Calico + Service + Ingress）
- ArgoCD 部署中涉及 Calico 与 CoreDNS 的 DNS 解析问题排查
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-Calico|K8s基础-Calico]]：Calico 功能与组件，IPIP、BGP、VXLAN、host-gw 模式对比与配置，以及与 Flannel、Weave Net、Cilium 的对比
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源|k8s基础-架构-组件-资源]]：Calico 作为集群 Addon，负责 Pod IP 分配与跨节点通信
- [[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤|安装k8s-1.35-基于rockylinux10-最新步骤]]：下载 calico.yaml，用脚本插入 `IP_AUTODETECTION_METHOD` 指定网卡，并验证跨节点网络
- [[Docker-Kubernetes/k8s-installation-management/2025最新-企业级高可用集群-基于rockylinux|2025最新-企业级高可用集群-基于rockylinux]]：禁止 NetworkManager 管理 Calico 网卡，指定网卡后部署 Calico
- [[Docker-Kubernetes/k8s-installation-management/k8s部署防火墙端口配置|k8s部署防火墙端口配置]]：按 IPIP、VXLAN、BGP、Typha 模式列出需要放行的端口
- [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.394)的DevOps工具链-基于yaml|K8s DevOps 工具链：Jenkins 2.394]]：Pod 沙箱创建报 Calico `Unauthorized` 时，删除 Calico 及其 CNI 配置后重新部署的排障记录
- [[Docker-Kubernetes/CKA-CKS/CKA-备考|CKA-备考]]：CKA 练习环境中安装 Calico，并用 busybox 测试网络

## 知识空白

- 仓库中尚无 calicoctl 的使用，以及 IPPool、BGPPeer 等 Calico 自定义资源的配置
- 仓库中尚无通过 Tigera Operator 安装和管理 Calico 的实践
- 仓库中尚无 Calico 扩展网络策略（如 GlobalNetworkPolicy）的配置示例
- 仓库中尚无 Calico eBPF 数据面、WireGuard 加密等进阶特性的实践
