---
title: Ingress
tags:
  - knowledgebase/entity
date: 2026-10-24
sources:
  - "[[KnowledgeBase/sources/k8s-networking-service-mesh-batch-summary|k8s-networking-service-mesh 来源批量摘要]]"
aliases:
  - Ingress Controller
  - Ingress-Nginx
---

# Ingress

## 简介
Kubernetes Ingress 是描述 HTTP/HTTPS 入口路由的 API 资源，需要具体控制器实现流量转发与 TLS 终止。社区 ingress-nginx 已于 2026 年 3 月退役；该实现的退役不等于 Ingress API 被移除。基础资源长文保留存量配置与实验，新部署需评估维护中的控制器或 Gateway API 实现。

## 核心功能

### 存量 ingress-nginx 的部署边界
- **hostNetwork 模式**：Pod 使用宿主机网络栈，直接开启 80/443 端口，适用于裸金属（Bare-metal）环境
- **ClusterFirstWithHostNet** DNS 策略：解决 hostNetwork 模式下无法解析集群内部服务名的问题
- DaemonSet 按匹配节点运行，Deployment 副本数不保证覆盖每个节点；前端 LB、拓扑分布与实际后端共同决定入口可达性
- 旧 [[KnowledgeBase/entities/Helm|Helm]] Chart 和镜像用于维护或迁移实验，不作为当前新集群的默认安装推荐

### DNS 解析链路
- External-DNS 向外部 DNS 提供商同步记录，CoreDNS 通常负责集群内服务发现；二者并非请求必须依次经过的串行代理。客户端解析入口地址后，再连接 Ingress 控制器或 [[KnowledgeBase/entities/Istio|Istio]] Gateway。

### 南北流量 vs 东西流量
- Ingress 负责集群外到集群内的**南北流量**管理
- Istio 侧重于集群内服务间的**东西流量**管理
- 两者可以协同工作，Ingress 作为外部入口，Istio 管理内部服务间通信

### 与其他组件的集成
- 多篇文章中 Ingress 与 OAuth2 Proxy 配合实现访问控制（如 Pact Broker 部署）
- Jenkins DevOps 平台中 Harbor 必须用 NodePort 而非 Ingress 暴露（JNLP Pod 内 CoreDNS 无法解析 Ingress 域名）

## 使用场景
- 南北流量入口：HTTP/HTTPS 路由到集群内部 Service
- TLS 终止：配合 Cert-Manager 自动化证书管理
- 多域名/多路径路由：单入口点分发到不同微服务

## 在本仓库中的覆盖
核心文章位于 `Docker-Kubernetes/k8s-basic-resources/`，Ingress Controller 的 Helm 部署位于 `Docker-Kubernetes/k8s-networking-service-mesh/`。


- [[Docker-Kubernetes/k8s-basic-resources/12-k8s基础-ingress|k8s基础-ingress]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx|helm部署ingress-nginx]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署external-dns|helm部署external-dns]]
- [[cert-manager 实战：Helm 部署、TLS 自动签发与续期|cert-manager 实战：Helm 部署、TLS 自动签发与续期]]
- [[Docker-Kubernetes/k8s-basic-resources/11-k8s基础-Service|k8s基础-Service]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/k8s集群网络安全|k8s集群网络安全]]

## 相关概念与实体
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/Istio|Istio]]
- [[KnowledgeBase/entities/Helm|Helm]]
- [[KnowledgeBase/entities/Cert-Manager|Cert-Manager]]
- [[KnowledgeBase/concepts/证书管理|证书管理]]

## 知识空白
- Kubernetes Gateway API 作为 Ingress 的继任者
- Ingress Controller 对比（Nginx vs Traefik vs Envoy）
