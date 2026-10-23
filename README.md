# CloudOps Vault · 云原生与基础设施知识库

**📖 在线浏览：[hangx969.github.io/cloudops-vault](https://hangx969.github.io/cloudops-vault/)**（随 main 分支自动更新）

[![Deploy Pages](https://github.com/hangx969/cloudops-vault/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/hangx969/cloudops-vault/actions/workflows/deploy-pages.yml)

网站使用 [Quartz 4](https://github.com/jackyzha0/quartz/tree/v4) 构建。

涵盖云原生技术、基础设施自动化、编程语言、AI/ML 和现代 DevOps 实践的综合知识库。

> **~360 篇学习笔记 · 18 个技术领域 · 159 篇知识编译层文件**

## 🧭 知识库导航（KnowledgeBase）

可以按技术领域、工具或概念查找相关笔记，通过交叉引用延伸阅读，并在分析报告中查看主题覆盖与待补充方向。

**→ [进入知识库首页](./KnowledgeBase/INDEX.md)**

| 类型 | 说明 | 入口 |
| --- | --- | --- |
| 📋 全库盘点 | 文档逐一索引 | [repository-inventory](./KnowledgeBase/inventory/repository-inventory.md) |
| 🗺️ 领域地图 | 按技术领域导航 | [domain-map](./KnowledgeBase/maps/domain-map.md) |
| 🔧 工具地图 | 按工具/平台聚合 | [tool-map](./KnowledgeBase/maps/tool-map.md) |
| ☸️ K8s 专题 | K8s 生态导航（Docker-Kubernetes 共 168 篇） | [kubernetes-map](./KnowledgeBase/maps/kubernetes-map.md) |
| 🤖 AI 专题 | Claude Code + Codex + OpenClaw + Hermes Agent + AI 视觉 | [ai-workflow-map](./KnowledgeBase/maps/ai-workflow-map.md) |
| ☁️ 云平台专题 | Aliyun vs Azure 对标 | [cloud-platform-map](./KnowledgeBase/maps/cloud-platform-map.md) |
| 🐧 Linux 运维 | 系统管理 + HPC + GPU | [linux-ops-map](./KnowledgeBase/maps/linux-ops-map.md) |
| 🐍 Python 运维 | 27 篇 Python 开发导航 | [python-devops-map](./KnowledgeBase/maps/python-devops-map.md) |
| 📈 覆盖分析 | 主题深度与缺口识别 | [topic-coverage-analysis](./KnowledgeBase/analysis/topic-coverage-analysis.md) |
| ✏️ 写作建议 | 推荐补写方向 | [next-writing-suggestions](./KnowledgeBase/analysis/next-writing-suggestions.md) |

## 🚀 推荐阅读路径

按目标选择一条路线，再沿顺序阅读；已有相关基础可以跳过入门部分。

### AI 编程与 Agent 协作

1. [AI 编程协作提示词](./AI/提示词/AI编程协作提示词.md) → 明确需求、改动范围和验证方式。
2. [Claude Code 使用指南](./AI/ClaudeCode/Claude%20Code%20基础指南.md) → 熟悉项目启动、交互模式与基本工作流。
3. [CLAUDE.md 维护工程](./AI/ClaudeCode/CLAUDE.md维护工程-四层加载与指令预算.md) → 维护项目规则，理解加载层级与指令预算。
4. [Claude Code 扩展体系](./AI/ClaudeCode/Claude%20Code%20扩展体系.md) → 按需接入 MCP、Skills 与 Plugin。
5. [多智能体协作](./AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams.md) → 根据任务选择 Subagents 或 Agent Teams。
6. [AI 代码审查闭环](./AI/Code%20review和知识图谱/AI代码审查闭环-验证优先与敏感信息清理.md) → 用实际验证、质量门禁与代码审查验收改动。

### AI Agent 与智能运维

1. [OpenClaw 基础与安装](./AI/OpenClaw/OpenClaw-基础-安装.md) → 了解平台架构，搭建运行环境。
2. [OpenClaw Workspace 运维](./AI/OpenClaw/OpenClaw-Workspace-运维.md) → 理清配置与工作区内容的边界。
3. [OpenClaw Skills 与插件](./AI/OpenClaw/OpenClaw-Skills-Plugins.md) → 配置和扩展 Agent 能力。
4. [OpenClaw K8s 智能运维实战](./AI/OpenClaw/OpenClaw-K8s智能运维实战.md) → 从只读巡检、诊断逐步进入低风险变更。

### AI 知识管理与笔记发布

1. [Obsidian + Claude Code：AI 知识库指南](./AI/Obsidian/obsidian-claude-code-AI知识库完整指南.md) → 搭建知识库，建立摄入、查询与维护流程。
2. [Obsidian 可视化 Skills](./AI/Obsidian/Obsidian可视化Skills-Excalidraw-Mermaid-Canvas.md) → 用 Excalidraw、Mermaid 和 Canvas 表达知识关系。
3. [远程 Vault 与 MCP 实践](./AI/Obsidian/Obsidian-Agent知识系统-远程Vault与MCP.md) → 从本地笔记走向 Agent 维护与团队共享。
4. [Quartz 4 笔记发布](./AI/Obsidian/github-pages-quartz.md) → 用 GitHub Actions 构建并发布 Obsidian 笔记。

### AI 私有化模型部署

1. [本地部署选型：Ollama、vLLM、SGLang 与 vLLM-Omni](./AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni.md) → 根据工作负载选择推理框架与部署方式。
2. [大模型精度与量化](./AI/企业级私有化大模型/大模型精度与量化：FP64到NVFP4.md) + [KV Cache 原理](./AI/企业级私有化大模型/KV%20Cache-从原理到集群调度.md) → 理解精度、显存占用与推理缓存。
3. [Docker 部署 vLLM 与 LiteLLM](./AI/企业级私有化大模型/基于docker部署vLLM和LiteLLM私有化大模型.md) → 先跑通单机推理服务与模型网关。
4. [K8s 部署 vLLM 与 LiteLLM](./AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM.md) → 进入 GPU 环境、集群部署与配套组件配置。
5. [为何用 KServe 管理 vLLM 推理服务？](./AI/企业级私有化大模型/一个%20Deployment%20就能跑%20vLLM，为什么还需要%20KServe？.md) → 从 Deployment 部署进一步学习推理服务管理。

### Kubernetes 基础与应用管理

1. [Docker 基础](./Docker-Kubernetes/docker/docker基础.md) → 掌握镜像、容器与基本操作。
2. [K8s 架构、组件与资源](./Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源.md) → 建立集群架构与资源模型的整体认识。
3. [Pod](./Docker-Kubernetes/k8s-basic-resources/k8s基础-pod.md) + [Deployment](./Docker-Kubernetes/k8s-basic-resources/k8s基础-deployment.md) → 学习容器生命周期、应用发布与滚动更新。
4. [Service](./Docker-Kubernetes/k8s-basic-resources/k8s基础-Service.md) → 理解服务发现与应用访问。
5. [Helm v3 安装与使用](./Docker-Kubernetes/helm/helmv3-安装与使用.md) → 用 Chart 安装、升级和管理应用。

专题阅读：[[Docker-Kubernetes/k8s-basic-resources/k8s基础-健康探针|Kubernetes 健康探针]] → 在理解 Pod 与 Service 后，学习启动、就绪、存活检查与重启风暴排查。

### GitOps 交付与可观测性

1. [Kustomize 入门：Base 与 Overlay](./Docker-Kubernetes/k8s-CICD/Kustomize/Kustomize入门-Base与Overlay多环境配置.md) → 组织多环境配置，管理共用基础与环境差异。
2. [ArgoCD 基础](./Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础.md) → 建立从 Git 到集群的应用同步流程。
3. [Argo CD 多集群 GitOps 实战](./Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD多集群GitOps实战.md) → 进一步学习 ApplicationSet 与多集群分发。
4. [Prometheus 基础](./Docker-Kubernetes/k8s-monitoring-logging/Prometheus基础.md) → 理解指标采集、PromQL 与标签处理。
5. [Prometheus-Stack：生产部署与运维](./Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶.md) → 部署监控栈，进入 Grafana 与告警管理。
6. [OpenTelemetry 统一可观测性实战](./Docker-Kubernetes/k8s-monitoring-logging/OpenTelemetry实战-统一Traces-Metrics-Logs.md) → 串联 Traces、Metrics 与 Logs。

### 云平台与 Terraform 自动化

1. [阿里云 VPC](./Aliyun/网络/VPC.md) + [Azure 网络](./Azure/6_Azure-Networking.md) → 理解云网络基础与平台差异。
2. [Landing Zone](./Aliyun/资源管理/Landing%20Zone.md) → 学习企业上云的账号、网络与治理规划。
3. [ACK 网络规划](./Aliyun/网络/ACK网络规划与成本优化.md) + [AKS 基础](./Azure/2_AKS-basics.md) → 将云网络知识应用到托管 Kubernetes。
4. [Terraform 基础系列学习路线](./IaC/terraform/README.md) → 按 01–15 的顺序学习配置、状态、模块、重构、CI 与 ACK/Helm 实战。
5. [FinOps 云成本优化实战](./Aliyun/资源管理/FinOps-云成本优化实战.md) → 建立成本基线，识别闲置资源并持续优化。

## 🏗️ 架构说明

本知识库采用 **三层架构**（基于 [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 模式）：

| 层级 | 说明 | 所有权 |
| --- | --- | --- |
| **Raw Sources** | 顶层主题目录中的 markdown 文件 | 人类策划，只读不改 |
| **Wiki** | `KnowledgeBase/` 目录下的所有内容 | LLM 创建和维护 |
| **Schema** | `AGENTS.md` 规约文件 | 人类与 LLM 共同演进 |

详见 [AGENTS.md](./AGENTS.md) 了解完整的页面模板、操作流程和命名约定。
