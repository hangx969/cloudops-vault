---
title: Nginx
tags:
  - knowledgebase/entity
  - web-server
  - load-balancer
date: 2026-04-17
sources:
  - "[[Docker-Kubernetes/k8s-basic-resources/12-k8s基础-ingress]]"
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx]]"
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署oauth2proxy]]"
  - "[[Docker-Kubernetes/docker/docker部署nginx-tomcat-httpd-go-python服务]]"
  - "[[Docker-Kubernetes/docker/docker部署lnmp网站]]"
  - "[[Docker-Kubernetes/k8s-installation-management/legacy-versions/二进制安装k8s高可用集群]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/Kubernetes原生部署Prometheus与Grafana]]"
  - "[[Python/python-运维开发/python-nginx]]"
---

## 简介

Nginx 是高性能的 Web 服务器和反向代理，广泛用于负载均衡、静态资源服务和 API 网关。在 Kubernetes 生态中，ingress-nginx 是最流行的 Ingress 控制器实现。在本仓库中还涉及 LNMP 架构部署、Keepalived + Nginx 高可用方案、OAuth2 Proxy 集成等场景。

## 核心功能

- **Web 服务与反向代理**：处理大量并发 HTTP 请求，提供静态资源服务、反向代理、负载均衡与 HTTP 缓存
- **四层代理**：通过 `stream` 模块做 TCP 负载均衡，如把请求代理到多台 kube-apiserver
- **Ingress 控制器（ingress-nginx）**：把 Ingress 规则自动转换为 Nginx 配置并 reload，通过注解实现 HTTPS、认证、会话保持、重定向与重写、限速、黑白名单、灰度发布等
- **外部认证**：通过 `auth-url`、`auth-signin` 注解把认证检查交给 OAuth2 Proxy
- **指标监控**：编译 nginx-module-vts 模块，再用 exporter 将指标接入 Prometheus

## 使用场景

- K8s 集群的七层流量入口（ingress-nginx，以 hostNetwork 或 NodePort 方式暴露）
- 与 Keepalived 组合，为 kube-apiserver 等后端提供带 VIP 的高可用四层入口
- 容器化部署 Web 服务或 LNMP 栈
- 为集群内服务（如 Jenkins、Grafana）统一接入 OAuth2 认证
- 用 Python 脚本自动检查配置语法、重启服务和更新配置

## 相关概念与实体

- [[KnowledgeBase/entities/Ingress|Ingress]]：ingress-nginx 是最常用的 Ingress 控制器
- [[KnowledgeBase/entities/Docker|Docker]]：LNMP 栈容器化部署
- [[KnowledgeBase/entities/Docker-Compose|Docker Compose]]：LNMP 栈编排
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：K8s 集群流量入口
- [[KnowledgeBase/concepts/高可用架构|高可用架构]]：Keepalived + Nginx 四层代理实现 apiserver 高可用入口
- [[KnowledgeBase/entities/Helm|Helm]]：用 Helm 部署 ingress-nginx
- [[KnowledgeBase/entities/Prometheus|Prometheus]]：通过 VTS 模块和 exporter 监控 Nginx
- [[KnowledgeBase/concepts/Python运维开发|Python运维开发]]：用 Python 脚本自动化运维 Nginx

## 在本仓库中的覆盖

- `Docker-Kubernetes/k8s-networking-service-mesh/` 中涉及 ingress-nginx 控制器部署（hostNetwork 模式）
- `Docker-Kubernetes/docker/` 中涉及 Nginx Dockerfile 部署和 LNMP 栈
- `Python/` 中涉及 Python 自动化运维 Nginx 的脚本
- `Docker-Kubernetes/k8s-security-auth/` 中涉及 Nginx + OAuth2 Proxy 认证
- [[Docker-Kubernetes/k8s-basic-resources/12-k8s基础-ingress|k8s基础-ingress]]：Ingress Controller 原理，ingress-nginx 注解配置（HTTPS、认证、会话保持、重定向与重写、限速、黑白名单、自定义错误页、灰度发布）、常见错误与高并发优化
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx|helm部署ingress-nginx]]：Helm 部署 ingress-nginx（hostNetwork 模式）、HTTPS 证书、hostNetwork 与 NodePort 的流量路径、集成 oauth2-proxy 及流量镜像
- [[Docker-Kubernetes/k8s-security-auth/helm部署oauth2proxy|helm部署oauth2proxy]]：利用 ingress-nginx 外部认证集成 OAuth2 Proxy 的认证流程
- [[Docker-Kubernetes/docker/docker部署nginx-tomcat-httpd-go-python服务|docker部署nginx-tomcat-httpd-go-python服务]]：在容器内安装 Nginx，以及用 Dockerfile 构建 Nginx 镜像
- [[Docker-Kubernetes/docker/docker部署lnmp网站|Docker部署LNMP网站]]：用 Compose 编排 Nginx、PHP-FPM 与 MySQL，并挂载 Nginx 配置
- [[Docker-Kubernetes/k8s-installation-management/legacy-versions/二进制安装k8s高可用集群|二进制安装k8s高可用集群]]：Nginx stream 四层代理加 Keepalived VIP 实现 apiserver 高可用
- [[Docker-Kubernetes/k8s-monitoring-logging/Kubernetes原生部署Prometheus与Grafana|Kubernetes原生部署Prometheus与Grafana]]：编译 nginx-module-vts，并用 nginx-vts-exporter 接入 Prometheus
- [[Python/python-运维开发/python-nginx|python-nginx]]：Nginx 安装，以及用 Python 检查配置语法、自动重启服务和追加 server 块

## 知识空白

- 仓库中尚无原生 Nginx upstream 负载均衡算法（如 ip_hash、least_conn）与 proxy_cache 缓存配置的说明
- 仓库中尚无独立部署 Nginx 的性能调优实践，现有高并发优化仅针对 ingress-nginx Controller
- 仓库中尚无 Nginx 平滑升级与版本迁移的操作记录
