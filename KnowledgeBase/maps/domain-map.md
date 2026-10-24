---
title: 领域地图
tags:
  - knowledgebase/map
  - knowledgebase/navigation
aliases:
  - Domain Map
date: 2026-10-20
sources:
  - "[[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD同步故障排查]]"
  - "[[AI/Obsidian/github-pages-quartz]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/01-k8s基础-架构-组件-资源]]"
  - "[[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶]]"
  - "[[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础]]"
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio]]"
  - "[[CloudComputing/云原生]]"
  - "[[Azure/2_AKS-basics]]"
  - "[[Python/python-运维开发/python-kubernetes-module]]"
  - "[[GPU-DeepLearning/GPU-basics]]"
  - "[[Python/python-运维开发/python-Linux-operation]]"
  - "[[Python/python-网络编程-前端/python-Web框架Django]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/22-Python调用k8s-api实现资源管理]]"
  - "[[Database/MySQL入门]]"
  - "[[Linux-Shell/shell-scripts]]"
  - "[[Linux-Shell/Linux-learning-notes]]"
  - "[[Linux-Shell/ansible安装-rockylinux8]]"
  - "[[Linux-Shell/开源堡垒机jumpserver部署]]"
  - "[[Azure/3_AKS-workload-identity]]"
  - "[[Azure/8_Azure-devops-basics]]"
  - "[[Azure/14_Kusto Query]]"
  - "[[Aliyun/计算/ECS]]"
  - "[[Aliyun/网络/VPC]]"
  - "[[Aliyun/网络/负载均衡SLB]]"
  - "[[Aliyun/网络/WAF]]"
  - "[[Aliyun/网络/DDoS高防]]"
  - "[[Aliyun/ACP考试]]"
  - "[[Azure/6_Azure-Networking]]"
  - "[[Networking/计算机网络基础]]"
  - "[[AI/ClaudeCode/Claude Code 基础指南]]"
  - "[[AI/OpenClaw/OpenClaw-基础-安装]]"
  - "[[AI/OpenClaw/Openclaw-多智能体]]"
  - "[[AI/企业级私有化大模型/基于docker部署vLLM和LiteLLM私有化大模型]]"
  - "[[AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM]]"
  - "[[AI/企业级私有化大模型/大模型精度与量化：FP64到NVFP4]]"
  - "[[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]]"
  - "[[Go/go-基础-01-环境配置-基础]]"
  - "[[Go/go-基础-03-变量-数据类型-运算]]"
  - "[[Go/go-基础-04-分支-循环]]"
  - "[[Go/go-基础-05-函数-包]]"
  - "[[Go/go-基础-02-数组-切片-map]]"
  - "[[Go/go-面向对象]]"
  - "[[Go/go-接口]]"
  - "[[Go/go-基础-06-错误处理]]"
  - "[[Go/go-web开发]]"
  - "[[Go/云原生开发-基础]]"
  - "[[Go/client-go-K8s客户端开发]]"
  - "[[Docker-Kubernetes/k8s-CICD/发布go-python-java代码到K8S环境]]"
  - "[[CloudComputing/深入剖析Kubernetes]]"
  - "[[CloudComputing/Auth]]"
  - "[[HPC/CentOS7-slurm23.02-二进制安装]]"
  - "[[HPC/PBS]]"
  - "[[Database/源码安装redis-6.2.6-centos7]]"
  - "[[Middlewares/Kafka]]"
  - "[[Middlewares/RabbitMQ]]"
  - "[[OS/OS]]"
  - "[[OS/计算机组成原理]]"
  - "[[Networking/HTTP基础]]"
  - "[[IaC/terraform/01_terraform_基础概念与第一个项目]]"
  - "[[Git/git-learning]]"
  - "[[SoftwareTesting/软件工程基础]]"
  - "[[C++/C++LearningNotes]]"
  - "[[AI/企业级私有化大模型/KV Cache-从原理到集群调度]]"
---

# 领域地图

> [!info] 按技术领域导航全库 18 个领域、377 篇学习笔记，每个领域标注覆盖范围、重点子目录、代表性文章和关联领域。
> 篇数按 Git 已跟踪的 Markdown 与本次迁移文章统计（不含各目录 index.md 导航页和 AI/ 下 280 篇引用/嵌入内容），统计日期 2026-10-03。

---

## ☸️ Docker-Kubernetes（171 篇）

**覆盖范围：** 从 Docker 容器基础到企业级 Kubernetes 全生命周期管理，包含安装部署、核心资源、监控日志、CI/CD、网络、安全、存储、扩缩容。

**重点子目录：**
- `k8s-basic-resources/`（25 篇）— Pod、Deployment、Service、Ingress、Storage 等核心资源
- `k8s-monitoring-logging/`（20 篇）— Prometheus、Grafana、EFK、Loki、Jaeger、Skywalking
- `k8s-CICD/`（25 篇）— Jenkins、ArgoCD、GitLab、Tekton、Kustomize、GitHub Actions
- `k8s-installation-management/`（20 篇）— K8s 1.20~1.35 多版本安装、生产优化、故障排查
- `docker/`（14 篇）— Docker 基础、镜像离线分发与各类服务部署
- `k8s-networking-service-mesh/`（7 篇）— Istio、Ingress-Nginx、NetworkPolicy

**代表性文章：**
- [[Docker-Kubernetes/k8s-basic-resources/01-k8s基础-架构-组件-资源|k8s基础-架构-组件-资源]] — K8s 架构总览
- [[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤|安装k8s-1.35-基于rockylinux10-最新步骤]] — 最新版安装
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶|Prometheus-Stack：生产部署与运维]] — 可观测性全家桶
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础|ArgoCD基础]] — GitOps 核心
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD同步故障排查|ArgoCD 同步故障排查]] — 同步故障与生产边界
- [[Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio|k8s精细化流量管理-istio]] — 服务网格

**关联领域：** [[CloudComputing/云原生|云原生]]、[[Azure/2_AKS-basics|2_AKS-basics]]、[[Python/python-运维开发/python-kubernetes-module|python-kubernetes-module]]、[[GPU-DeepLearning/GPU-basics|GPU-basics]]

---

## 🐍 Python（28 篇）

**覆盖范围：** Python 语言基础、Web 框架、网络编程、运维自动化开发、数据分析。

**重点子目录：**
- `python-运维开发/`（10 篇）— ==核心亮点==，K8s API、MySQL/PG/ES 自动化、Fabric
- `python-基础/`（8 篇）— 数据类型、OOP、函数、异常处理
- `python-网络编程-前端/`（6 篇）— Django、Flask、Requests、Socket、爬虫
- `python-数据分析-AI大模型/`（2 篇）— Excel/Word 处理、机器学习

**代表性文章：**
- [[Python/python-运维开发/python-Linux-operation|python-Linux-operation]] — Linux 运维核心模块（1737 行）
- [[Python/python-运维开发/python-kubernetes-module|python-kubernetes-module]] — K8s API 自动化
- [[Python/python-网络编程-前端/python-Web框架Django|python-Web框架Django]] — Django 全栈

**关联领域：** [[Docker-Kubernetes/k8s-basic-resources/22-Python调用k8s-api实现资源管理|Python调用k8s-api实现资源管理]]、[[Database/MySQL入门|MySQL入门]]、[[Linux-Shell/shell-scripts|shell-scripts]]

---

## 🐧 Linux-Shell（11 篇）

**覆盖范围：** Linux 系统管理、Shell 脚本、SSH、网络配置、Ubuntu 运维、开发环境搭建。

**代表性文章：**
- [[Linux-Shell/Linux-learning-notes|Linux-learning-notes]] — Linux 全面学习笔记（含 9 个实操专题）
- [[Linux-Shell/shell-scripts|shell-scripts]] — Shell 脚本实战
- [[Linux-Shell/ansible安装-rockylinux8|ansible安装-rockylinux8]] — Ansible 自动化
- [[Linux-Shell/开源堡垒机jumpserver部署|开源堡垒机jumpserver部署]] — 安全运维

**关联领域：** 所有技术领域的基础底盘，特别是 Docker-Kubernetes、HPC、Python

---

## ☁️ Azure（17 篇）

**覆盖范围：** Azure VM/VMSS、AKS、DevOps、存储、网络、安全策略、排障工具链。

**代表性文章：**
- [[Azure/2_AKS-basics|2_AKS-basics]] — AKS 基础
- [[Azure/3_AKS-workload-identity|3_AKS-workload-identity]] — Workload Identity
- [[Azure/8_Azure-devops-basics|8_Azure-devops-basics]] — Azure DevOps
- [[14_Kusto Query|14_Kusto Query]] — KQL 查询语言（2208 行）

**关联领域：** [[Aliyun/计算/ECS|ECS]]（对标 VM）、[[Docker-Kubernetes/k8s-basic-resources/01-k8s基础-架构-组件-资源|k8s基础-架构-组件-资源]]

---

## 🏔️ Aliyun（21 篇）

**覆盖范围：** 阿里云全产品线 — 计算(ECS/ESS/SMC)、网络(VPC/SLB/WAF/DDoS)、存储(OSS/CORS)、数据库(RDS/DTS)、资源管理。

**代表性文章：**
- [[Aliyun/网络/VPC|VPC]] — 专有网络架构
- [[Aliyun/网络/负载均衡SLB|负载均衡SLB]] — CLB/ALB/NLB 全家族
- [[Aliyun/网络/WAF|WAF]] + [[Aliyun/网络/DDoS高防|DDoS高防]] — 安全矩阵
- [[Aliyun/ACP考试|ACP考试]] — ACP 认证备考

**关联领域：** [[Azure/6_Azure-Networking|6_Azure-Networking]]、[[Networking/计算机网络基础|计算机网络基础]]

---

## 🤖 AI（74 篇）

**覆盖范围：** Claude Code（13 篇）、OpenClaw（10 篇）、提示词（8 篇）、AI 视觉（7 篇）、企业级私有化大模型（6 篇）、代码审查与知识图谱（6 篇）、行业动态（6 篇）、Obsidian（6 篇）、Hermes Agent（4 篇）、RAG（3 篇）、AIOps（2 篇）、Codex（2 篇）、GitHub Copilot（1 篇）。

**重点子目录：**
- `ClaudeCode/`（13 篇）— 基础指南、扩展体系（MCP/Skills/Plugin）、CLAUDE.md 最佳实践、多智能体协作、Harness 与省 Token
- `OpenClaw/`（10 篇）— 基础安装、Channels、Skills、AIOps、多智能体、CoPaw

**代表性文章：**
- [[Claude Code 基础指南|Claude Code 基础指南]] — Claude Code 全面指南
- [[AI/OpenClaw/OpenClaw-基础-安装|OpenClaw-基础-安装]] — OpenClaw 入门
- [[AI/OpenClaw/Openclaw-多智能体|Openclaw-多智能体]] — 多智能体架构（2974 行，全库最大）
- [[AI/Obsidian/github-pages-quartz|Obsidian 笔记发布到 GitHub Pages]] — Quartz 4 的完整 workflow、链接兼容与验收。

**关联领域：** 与所有领域潜在交叉（AI 辅助编码、运维、知识管理）


**企业级私有化大模型：**
- [[基于docker部署vLLM和LiteLLM私有化大模型]] — vLLM/LiteLLM 私有化部署、权重与 KV Cache 显存规划
- [[AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM]] — Kubernetes GPU 服务部署上下文
- [[AI/企业级私有化大模型/大模型精度与量化：FP64到NVFP4]] — FP64 到 NVFP4 的数值格式、量化与训练/推理取舍
- [[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]] — 四种推理 Runtime 选型、模型与镜像离线交付、GPU 显存及容器化部署
- [[KnowledgeBase/concepts/混合精度与模型量化]] — 统一连接数值精度、显存、吞吐、硬件和软件栈

---

## 🔤 Go（11 篇）

**覆盖范围：** Go 语言完整学习路径 + 云原生开发基础。

**推荐顺序：** [[go-基础-01-环境配置-基础|go-基础-01-环境配置-基础]] → [[go-基础-03-变量-数据类型-运算|go-基础-03-变量-数据类型-运算]] → [[go-基础-04-分支-循环|go-基础-04-分支-循环]] → [[go-基础-05-函数-包|go-基础-05-函数-包]] → [[go-基础-02-数组-切片-map|go-基础-02-数组-切片-map]] → [[Go/go-面向对象|go-面向对象]] → [[Go/go-接口|go-接口]] → [[go-基础-06-错误处理|go-基础-06-错误处理]] → [[Go/go-web开发|go-web开发]] → [[Go/云原生开发-基础|云原生开发-基础]] → [[Go/client-go-K8s客户端开发|client-go-K8s客户端开发]]

**来源摘要：** [[KnowledgeBase/sources/go-batch-summary|Go 批量摘要]]

**关联领域：** [[CloudComputing/云原生|云原生]]、[[Docker-Kubernetes/k8s-CICD/发布go-python-java代码到K8S环境|发布go-python-java代码到K8S环境]]

---

## ☁️ CloudComputing（7 篇）

**覆盖范围：** 云计算架构理论、云原生概念、OpenStack、K8s 深入剖析、认证协议（SSO/OAuth）。

**代表性文章：**
- [[CloudComputing/云原生|云原生]] — 云原生哲学
- [[CloudComputing/深入剖析Kubernetes|深入剖析Kubernetes]] — K8s 理论深入
- [[CloudComputing/Auth|Auth]] — 认证协议

**关联领域：** Docker-Kubernetes（实操对照）、Aliyun/Azure（云平台实践）

---

## 🖥️ HPC（4 篇）

**覆盖范围：** Slurm 和 PBS 作业调度系统，覆盖 CentOS 7 / Ubuntu 22.04 多版本部署。

**代表性文章：**
- [[HPC/CentOS7-slurm23.02-二进制安装|CentOS7-slurm23.02-二进制安装]] — 最全面的 Slurm 部署指南（1449 行）
- [[HPC/PBS|PBS]] — PBS 调度系统

**关联领域：** [[GPU-DeepLearning/GPU-basics|GPU-basics]]、[[Linux-Shell/Linux-learning-notes|Linux-learning-notes]]

---

## 其他领域

| 领域 | 篇数 | 核心文章 | 关联 |
|------|------|----------|------|
| GPU-DeepLearning | 4 | [[GPU-DeepLearning/GPU-basics|GPU-basics]] | HPC、Docker |
| Database | 3 | [[Database/MySQL入门|MySQL入门]]、[[Database/源码安装redis-6.2.6-centos7|源码安装redis-6.2.6-centos7]] | Python 运维 |
| Middlewares | 3 | [[Middlewares/Kafka\|Kafka：入门、生产配置与 Kubernetes 排障]]、[[Middlewares/RabbitMQ\|RabbitMQ]] | 事件流、生产可靠性与 K8s 中间件部署 |
| OS | 3 | [[OS/OS|OS]]、[[OS/计算机组成原理|计算机组成原理]] | 理论基础 |
| Networking | 2 | [[Networking/计算机网络基础|计算机网络基础]]、[[Networking/HTTP基础|HTTP基础]] | 云网络基础 |
| IaC | 16（含学习路线） | [[IaC/terraform/README\|Terraform 基础系列]]、[[KnowledgeBase/maps/terraform-map\|学习地图]] | 自动化运维 |
| Git | 2 | [[Git/git-learning|git-learning]] | 开发工具 |
| SoftwareTesting | 2 | [[SoftwareTesting/软件工程基础|软件工程基础]] | 软件工程 |
| C++ | 1 | [[C++/C++LearningNotes|C++LearningNotes]] | 编程语言 |

**来源摘要：** [[KnowledgeBase/sources/misc-domains-batch-summary|杂项领域批量摘要]]、[[KnowledgeBase/sources/kafka-basics-production-summary|Kafka 入门与生产运维摘要]]、[[KnowledgeBase/sources/iac-terraform-container-summary|Terraform 容器管理摘要]]


## 🤖 AI · 企业级私有化大模型（增量）

- [[AI/企业级私有化大模型/KV Cache-从原理到集群调度]] — KV Cache 生命周期、Prefill/Decode、显存带宽瓶颈与 Prefix Cache/PD 分离/负载均衡
- [[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]] — Ollama、vLLM、SGLang、vLLM-Omni 定位与从单机到模型平台的演进
