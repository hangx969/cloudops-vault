---
title: k8s-networking-service-mesh 来源批量摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/networking
date: 2026-09-15
sources:
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/helm部署external-dns]]"
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx]]"
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/k8s集群网络安全]]"
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio]]"
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/企业项目接入istio实战]]"
aliases:
  - "k8s-networking-service-mesh 批量摘要"
---

## 元信息

- **原始目录**: `Docker-Kubernetes/k8s-networking-service-mesh/`
- **文档数量**: 本批次收录 5 篇（`k8s-networking-service-mesh/` 目录现有 7 篇）
- **领域**: Kubernetes 网络、Ingress 控制器、服务网格（Istio）、DNS 与网络安全
- **摄入日期**: 2026-04-17

## 摘要

本目录覆盖了 Kubernetes 集群网络层面的核心主题，包括 Ingress 控制器（ingress-nginx）部署与配置、外部 DNS 自动同步（External-DNS）、服务网格 Istio 的多种部署方式与流量管理实践，以及集群网络安全工具（kube-bench、kube-hunter 等）。文档从基础概念到企业级落地实战，完整展示了从南北流量到东西流量的精细化管理方案。

## 关键知识点

1. External-DNS 不是 DNS 服务器本身，而是将 K8s Service 和 Ingress 的域名自动同步到外部 DNS 提供商的工具：source 字段指定监控的 Ingress/Service，provider 字段指定 DNS 服务商；对接 Azure DNS 时可通过 SPN、Managed Identity 或 Workload Identity 认证。
2. 裸金属环境部署 ingress-nginx 可采用 hostNetwork 模式（Pod 使用宿主机网络栈，开启 80/443 端口），需配合 ClusterFirstWithHostNet DNS 策略解决无法解析集群内部服务名的问题；建议 DaemonSet 或至少 3 副本，确保每个节点都能接收请求。
3. 服务网格解决服务间通信、流量精细化管理、安全通信、多语言治理和可观测性问题；Istio 可通过 istioctl + IstioOperator 或 Helm 分步安装，工作模式分为 Sidecar 与 Ambient（L4/L7 分层）。
4. Istio 核心资源 Gateway、VirtualService、DestinationRule 各有职责并组合使用，支撑域名发布、重写/重定向、灰度、A/B 测试、负载均衡、熔断、故障注入、超时和重试。
5. 企业项目接入 Istio 分两种场景：Sidecar 管理东西流量，IngressGateway 管理南北流量；新项目按 Istio 规范创建 Deployment/Service 和核心资源，已部署项目需修改 Deployment/Service，建议所有 Deployment 配置 version 标签。
6. 集群安全检测工具分工：kube-bench 检查集群是否符合 CIS 安全标准，kube-hunter 自动化查找集群安全漏洞，kubeaudit/Polaris 评估 Pod 和 Deployment 配置安全性。

## 各文档摘要

### [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署external-dns|Helm 部署 External-DNS]]

**核心内容**: External-DNS 将 K8s Service 和 Ingress 资源的域名自动同步到外部 DNS 提供商（如 Azure DNS），实现域名记录的自动化管理。

- 不是 DNS 服务器本身，而是对接外部 DNS 提供商的同步工具
- 支持 Azure DNS 集成，通过 SPN、Managed Identity 或 Workload Identity 认证
- 通过 source 字段监控 Ingress/Service，通过 provider 字段指定 DNS 服务商

### [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx|Helm 部署 Ingress-Nginx]]

**核心内容**: 在 K8s 中部署 ingress-nginx 控制器作为七层代理，支持 hostNetwork 模式和 ClusterFirstWithHostNet DNS 策略。

- hostNetwork 模式：Pod 使用宿主机网络栈，开启 80/443 端口
- ClusterFirstWithHostNet：解决 hostNetwork 模式下无法解析集群内部服务名的问题
- 建议 DaemonSet 或至少 3 副本确保每个节点都能接收请求
- 适用于裸金属（Bare-metal）环境的部署方案

### [[Docker-Kubernetes/k8s-networking-service-mesh/k8s集群网络安全|K8s 集群网络安全]]

**核心内容**: 介绍 Docker 容器逃逸漏洞（CVE-2019-5736）原理和 K8s 集群安全测试工具集（kube-bench、kube-hunter、kubeaudit、Polaris）。

- CVE-2019-5736：Docker 18.09.2 以下 runC 漏洞，攻击者可覆写宿主机 runc 二进制文件提权
- kube-bench：检查集群是否符合 CIS 安全标准
- kube-hunter：自动化查找集群安全漏洞
- kubeaudit/Polaris：评估 Pod 和 Deployment 配置安全性

### [[Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio|Istio 服务网格：架构、部署与精细化流量治理]]

**核心内容**: 介绍服务网格背景、Istio 架构和核心资源，并贯通 istioctl/Helm 部署、Sidecar/Ambient 选型以及 Bookinfo 流量治理实践。

- 服务网格解决的问题：服务间通信、流量精细化管理、安全通信、多语言治理、可观测性
- 安装路径：istioctl + IstioOperator、Helm 分步安装，以及 Kubernetes 1.23 + Istio 1.13.1 历史环境记录
- 工作模式：Sidecar 与 Ambient 的 L4/L7 分层、成本边界、分批迁移和回滚策略
- 核心资源：Gateway、VirtualService、DestinationRule 的职责与组合关系
- 实践主线：Bookinfo 域名发布、重写/重定向、灰度、A/B 测试、负载均衡、熔断、故障注入、超时和重试

### [[Docker-Kubernetes/k8s-networking-service-mesh/企业项目接入istio实战|企业项目接入 Istio 实战]]

**核心内容**: 企业项目接入 Istio 的两种场景（Sidecar 东西流量管理 vs IngressGateway 南北流量管理）及完整实战案例。

- 新项目按 Istio 规范创建 Deployment/Service 和核心资源
- 已部署项目需修改 Deployment/Service，按需转换为 IngressGateway
- 测试架构：前端 UI + 后端 Receive/Order/Handler Service + MySQL
- 建议所有 Deployment 配置 version 标签

## 涉及的概念与实体

- [[KnowledgeBase/concepts/ServiceMesh]]: 服务网格架构，流量治理下沉到基础设施
- [[KnowledgeBase/entities/Ingress|Ingress]]: K8s 七层代理入口，南北流量管理
- [[Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio#Sidecar 与 Ambient 工作模式|Sidecar]]: Envoy 代理注入模式
- [[Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio#Bookinfo 流量治理实践|流量管理]]: 熔断、超时、重试、金丝雀发布、蓝绿部署
- [[KnowledgeBase/entities/Istio]]: 服务网格平台
- [[Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio#Envoy|Envoy]]: 数据面代理
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx|Ingress-Nginx]]: K8s Ingress 控制器
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署external-dns|External-DNS]]: DNS 自动同步工具
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源#Addons(CoreDNS,Calico)|CoreDNS]]: K8s 集群 DNS 服务
- [[Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio#Pilot|Pilot]]: Istio 控制面服务发现组件

## 交叉主题发现

1. **南北流量 vs 东西流量**: Ingress-Nginx 负责集群外到集群内的南北流量，Istio 侧重于集群内服务间的东西流量管理，两者可以协同工作。
2. **DNS 解析链路**: External-DNS（外部域名同步） -> CoreDNS（集群内解析） -> Ingress-Nginx/Istio Gateway（流量入口），形成完整的 DNS 到流量转发链路。
3. **安全多层防护**: 集群网络安全工具（kube-bench 等）提供基础安全检测，Istio 提供 mTLS 全链路加密，与 `k8s-security-auth` 目录的 Kyverno 策略引擎形成多层安全体系。
4. **hostNetwork 与 DNS 策略**: Ingress-Nginx 的 hostNetwork 模式需要 ClusterFirstWithHostNet DNS 策略，这与 ArgoCD DNS 排查（k8s-CICD 目录）的 CoreDNS 问题密切相关。
5. **微服务架构演进**: 从 SpringCloud/Nacos 到 Istio 的服务治理演进，反映了基础设施层面的关注点分离趋势。

## 值得注意

- **Sidecar 与 Ambient 选型**: 两者不是简单的新旧替代关系，应根据功能、资源成本和迁移风险选择；原文给出的 L4 相比 L7 资源节省区间属特定场景观测值，不能当作通用承诺，迁移宜分域、分批并保留回滚路径。
- **流量治理先压测**: 灰度、重试、熔断和故障注入均应先在测试环境压测，并确保有明确的回滚步骤和流量恢复路径。
- **版本边界**: Istio 指南中的 Kubernetes 1.23 + Istio 1.13.1 部署步骤为历史环境记录；CVE-2019-5736 影响 Docker 18.09.2 以下版本，攻击者可利用 runC 漏洞覆写宿主机 runc 二进制文件提权。
