---
title: 知识库入口
tags:
  - knowledgebase/index
  - knowledgebase/navigation
aliases:
  - 知识库首页
  - KB Index
date: 2026-10-22
---

# 📚 Learning Notes 知识库

> [!info] 知识库说明
> 本知识库基于 [Karpathy LLM Wiki 模式](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 构建。
> 原始来源（顶层主题目录）只读不改，LLM 在本目录中生成和维护所有编译内容。
>
> - **Schema 文件**：[[AGENTS|AGENTS.md]]（统一规约）；[[CLAUDE|CLAUDE.md]] 仅通过 `@AGENTS.md` 导入
> - **操作日志**：[log.md](log.md)
> - **扫描日期**：2026-04-17
> - **核心定位**：云原生运维工程师的全栈技术知识库

---

## 🧠 概念页（Concepts）

抽象概念的独立知识页面。

| 页面 | 摘要 |
|------|------|
| [CICD](concepts/CICD.md) | 持续集成与持续交付，覆盖 Jenkins、ArgoCD、GitLab CI、Tekton 等工具链 |
| [Observability](concepts/Observability.md) | 可观测性三大支柱：日志、指标、链路追踪 |
| [日志系统](concepts/日志系统.md) | EFK/ELK、Loki 等日志采集与分析方案 |
| [服务网格](concepts/服务网格.md) | Istio 为代表的服务网格架构与流量管理 |
| [容器运行时](concepts/容器运行时.md) | containerd、Docker Engine 等容器运行时技术 |
| [自动化运维](concepts/自动化运维.md) | Ansible、Python 脚本、Terraform 等自动化运维实践 |
| [Python运维开发](concepts/Python运维开发.md) | Python 在运维场景中的应用：自动化脚本、Web 运维平台、API 调用 |
| [StorageClass](concepts/StorageClass.md) | Kubernetes 动态存储分配：Provisioner、回收策略、PV/PVC 绑定 |
| [高可用架构](concepts/高可用架构.md) | 消除单点故障的冗余与故障切换架构设计 |
| [CRD](concepts/CRD.md) | Kubernetes 自定义资源定义，扩展 API 的核心机制 |
| [Operator模式](concepts/Operator模式.md) | CRD + Controller 模式，自动化有状态应用运维 |
| [Finalizer](concepts/Finalizer.md) | Kubernetes 资源删除前钩子机制，防止外部资源泄漏 |
| [RBAC](concepts/RBAC.md) | Kubernetes 基于角色的访问控制 |
| [联邦集群](concepts/联邦集群.md) | Kubernetes 多集群统一管理与跨集群调度 |
| [ServiceMesh](concepts/ServiceMesh.md) | → 服务网格（别名页）|
| [[KnowledgeBase/concepts/AI代码审查|AI 代码审查]] | 以完整上下文、确定性门禁、真实运行和人工判断验证 AI 生成代码 |
| [[KnowledgeBase/concepts/提示词工程|提示词工程]] | 通过目标、上下文、约束、交互流程和验证标准提升模型输出的可靠性 |
| [[KnowledgeBase/concepts/混合精度与模型量化|混合精度与模型量化]] | 大模型数值格式、混合精度、低比特量化及其显存/吞吐取舍 |
| [[KnowledgeBase/concepts/P2P分发|P2P 分发]] | 通过分块、Peer 交换与缓存降低大规模数据分发的源站压力 |
| [[KnowledgeBase/concepts/证书管理|证书管理]] | TLS 证书与私钥的签发、校验、分发、续期、审计和安全边界 |

- [[KnowledgeBase/concepts/基础设施即代码|基础设施即代码]] — 基础设施即代码（IaC）将资源的期望配置写成可版本管理的代码或声明。它让配置差异可以审查，让环境搭建和变更有可重复的输入，但仍需要身份、状态和实际平台验收配合。
- [[KnowledgeBase/concepts/Terraform状态管理|Terraform状态管理]] — Terraform 状态管理维护配置地址与实际对象之间的绑定，以及运行所需的已知属性和元数据。状态用于变更计算与身份跟踪，不等于完整基础设施或业务数据备份。
- [[KnowledgeBase/concepts/Terraform模块化|Terraform模块化]] — Terraform 模块化把一组相关配置组织成具有输入、输出和版本要求的复用单元。子模块资源仍属于调用它的根配置 State，因此代码复用边界与独立执行边界需要分别设计。

- [[KnowledgeBase/concepts/自动扩缩容|自动扩缩容]] — HPA、VPA、KEDA 与节点容量协同，涵盖 requests、迁移保护和扩容延迟。

- [[KnowledgeBase/concepts/分布式存储|分布式存储]] — 数据放置、冗余、一致性、故障恢复与文件 / 对象 / 块接口。

---

## 🔧 实体页（Entities）

具体工具、平台、项目的独立知识页面。

| 页面 | 摘要 |
|------|------|
| [Kubernetes](entities/Kubernetes.md) | 容器编排平台，159 篇 Kubernetes 相关文章覆盖全生命周期 |
| [Docker](entities/Docker.md) | 容器运行时，14 篇覆盖基础、镜像分发与服务部署实战 |
| [Helm](entities/Helm.md) | Kubernetes 包管理器 |
| [[KnowledgeBase/entities/Cert-Manager|Cert-Manager]] | Kubernetes 原生证书生命周期控制器，支持 ACME、自签名与自动续期 |
| [ArgoCD](entities/ArgoCD.md) | GitOps 持续交付工具 |
| [Jenkins](entities/Jenkins.md) | CI/CD 自动化服务器 |
| [Prometheus](entities/Prometheus.md) | 云原生监控系统 |
| [Grafana](entities/Grafana.md) | 可视化与仪表盘平台 |
| [Istio](entities/Istio.md) | 服务网格平台 |
| [Ingress](entities/Ingress.md) | Kubernetes 入口控制器 |
| [Azure](entities/Azure.md) | Microsoft 公有云平台 |
| [AKS](entities/AKS.md) | Azure 托管 Kubernetes 服务 |
| [Aliyun](entities/Aliyun.md) | 阿里云公有云平台 |
| [[KnowledgeBase/entities/Terraform\|Terraform]] | 基础系列、Provider、状态、模块、容器与协作 |
| [Claude-Code](entities/Claude-Code.md) | AI 编程助手 |
| [[KnowledgeBase/entities/Codex|Codex]] | AI 编程助手；Harness 任务循环、配置、工具执行与工作流优化 |
| [MCP](entities/MCP.md) | Model Context Protocol |
| [OpenClaw](entities/OpenClaw.md) | 开源 AI 工具平台 |
| [Obsidian](entities/Obsidian.md) | 知识管理与笔记工具 |
| [Hermes-Agent](entities/Hermes-Agent.md) | AI Agent 框架（持久记忆、自我进化） |
| [Slurm](entities/Slurm.md) | HPC 作业调度系统 |
| [Harbor](entities/Harbor.md) | 企业级 OCI 镜像仓库，可作为 Dragonfly P2P 分发源站并配置预热策略 |
| [[KnowledgeBase/entities/Dragonfly|Dragonfly]] | 面向云原生与 AI 基础设施的 P2P 镜像和大文件分发系统 |
| [Redis](entities/Redis.md) | 高性能键值数据库（stub） |
| [GitLab](entities/GitLab.md) | DevOps 全生命周期平台（stub） |
| [Loki](entities/Loki.md) | 轻量级日志聚合系统（stub） |
| [MySQL](entities/MySQL.md) | 开源关系型数据库（stub） |
| [[KnowledgeBase/entities/NVIDIA|NVIDIA]] | GPU 硬件厂商，覆盖 Tensor Core 精度与 NVFP4 相关内容 |
| [PBS](entities/PBS.md) | HPC 作业调度系统（stub） |
| [containerd](entities/containerd.md) | K8s 默认容器运行时（stub） |
| [[KnowledgeBase/entities/CUDA|CUDA]] | NVIDIA GPU 计算平台，关联精度格式与硬件支持 |
| [Calico](entities/Calico.md) | K8s CNI 网络插件（stub） |
| [Docker Compose](entities/Docker-Compose.md) | 单机多容器编排工具（stub） |
| [Kustomize](entities/Kustomize.md) | K8s 原生无模板配置定制工具，覆盖 Base/Overlay、多环境差异与当前字段边界 |
| [NFS](entities/NFS.md) | 网络文件系统存储（stub） |
| [Nginx](entities/Nginx.md) | Web 服务器与反向代理（stub） |
| [PostgreSQL](entities/PostgreSQL.md) | 开源关系型数据库（stub） |
| [Rancher](entities/Rancher.md) | K8s 多集群管理平台（stub） |
| [[KnowledgeBase/entities/Kyverno\|Kyverno]] | K8s 原生策略引擎：验证、变更、生成与策略报告 |
| [[KnowledgeBase/entities/Ollama|Ollama]] | 面向本地开发、Demo 与 PoC 的模型下载、管理和运行工具 |
| [[KnowledgeBase/entities/vLLM|vLLM]] | 高吞吐 LLM Serving Runtime，覆盖 KV Cache、并行推理与 OpenAI 兼容 API |
| [[KnowledgeBase/entities/ModelScope|ModelScope]] | 模型与数据集平台，可作为国内模型下载及离线资产准备入口 |

- [[KnowledgeBase/entities/Kafka|Kafka]] — 事件流与消费语义、副本可靠性、生产配置、ZooKeeper/KRaft 及 Kubernetes 排障。

- [[KnowledgeBase/entities/Cluster Autoscaler|Cluster Autoscaler]] — 基于 Pod 调度需求扩容节点组，并在满足迁移条件时安全缩容。

- [[KnowledgeBase/entities/Ceph|Ceph]] — RADOS 统一底座、CRUSH / PG、三种存储接口、运维及 Kubernetes 接入。

---

## 📄 来源摘要（Sources）

每篇原始来源文档的知识提炼摘要。

### AI/ClaudeCode（已摄入 ✅）

| 页面 | 原始来源 | 摘要 |
|------|---------|------|
| [ClaudeCode基础指南](sources/ClaudeCode基础指南-summary.md) | [AI/ClaudeCode/Claude Code 基础指南](../AI/ClaudeCode/Claude%20Code%20基础指南.md) | 3 种模式、Extended Thinking、Claude.md、Spec 工作流、5 大实战场景 |
| [AI知识库完整指南](sources/obsidian-claude-AI知识库完整指南-summary.md) | [[AI/Obsidian/obsidian-claude-code-AI知识库完整指南\|Obsidian + Claude Code：AI 知识库指南]] | Markdown 母语论证、Karpathy Wiki 三层架构、30 分钟四步上手、六大操作谱系、三个集成工具、改造计划 |
| [Obsidian可视化Skills](sources/obsidian-visual-skills-summary.md) | [[AI/Obsidian/Obsidian可视化Skills-Excalidraw-Mermaid-Canvas\|Obsidian 可视化 Skills]] | AI Skills 生成可编辑图表：Excalidraw/Mermaid/Canvas 三种格式 |
| [Skill Craft](sources/skill-craft-summary.md) | [AI/ClaudeCode/Claude-Skill质检工具-SkillCraft](../AI/ClaudeCode/Claude-Skill质检工具-SkillCraft.md) | Skill 质量工程：7 类失效模式、三层评估体系、check/fix/create/audit 四模式 |
| [Harness 实战](sources/harness-system-summary.md) | [[AI/ClaudeCode/Claude-Code-Harness实战-最小可用系统\|Harness 实战：从零搭建最小可用系统]] | Harness 四层安全约束：约束层/工具层/中间件层/编排层 + Hooks 拦截器 + Git 门禁 |
| [CLAUDE.md 完全指南](sources/claude-md-complete-guide-summary.md) | [[CLAUDE.md最佳实践-12条规则模板\|Mnilax 的 CLAUDE.md：12 条规则]] / [[CLAUDE.md最佳实践-21条指令清单\|Mayank Agarwal：21 条 CLAUDE.md 指令]] / [[CLAUDE.md维护工程-四层加载与指令预算]] | 12 条行为规则（错误率 41%→3%）+ 21 条指令清单（五维度）+ 四层加载/指令预算/rules/ 精准投放/配置体系四角色 |
| [CLAUDE.md 维护工程](sources/claude-md-maintenance-summary.md) | [[CLAUDE.md维护工程-四层加载与指令预算]] | 四层加载体系、LLM 指令预算（arXiv 论文）、rules/ 精准投放、配置体系四角色分工 |
| [CodeGraph](sources/codegraph-summary.md) | [[CodeGraph-代码语义知识图谱\|CodeGraph：Claude Code 代码知识图谱]] | 代码语义图谱，工具调用减少 92%、探索速度提升 71%，19 种语言 + 框架路由映射，本地 AST 不依赖外部 |
| [Fable 5 System Prompt](sources/claude-fable5-system-prompt-summary.md) | [[AI/ClaudeCode/Claude-Fable-5-system-prompt]] | Claude Fable 5 完整系统提示词（~125K 字符）：Mythos-class 新层级、行为规约体系、~15 个内置工具、沙箱架构、Artifact/Claudeception、版权硬限制 |
| [Git Worktree AI 实践](sources/git-worktree-ai-dev-summary.md) | [[Git-Worktree-AI开发实践指南\|Vibe Coding 的 Git Worktree 实践]] | 一个 AI 会话 = 一个 Worktree，并行开发/紧急修复/多方案探索，5 个实践踩坑 |

### AI/Obsidian（增量）

- [[KnowledgeBase/sources/github-pages-quartz-summary|GitHub Pages：Quartz 4 来源摘要]] — Quartz 4 的固定版本、完整 workflow、Obsidian 适配与发布验收；原文：[[AI/Obsidian/github-pages-quartz|构建流程复现文档]]。

### AI/Codex（已摄入 ✅）

| 页面 | 原始来源 | 摘要 |
|------|---------|------|
| [[KnowledgeBase/sources/codex-harness-architecture-summary|Codex Harness 架构]] | [[AI/Codex/Codex-Harness架构-任务循环与扩展]] | 从 App Server、Session、Agent 主循环，到上下文、工具执行、状态记忆及 Skills/MCP/Hooks/子 Agent 扩展 |
| [[KnowledgeBase/sources/codex-使用技巧和最佳实践-summary|Codex 使用技巧和最佳实践]] | [[AI/Codex/Codex-使用技巧和最佳实践]] | 配置与权限基线、主动澄清、Token 优化、HANDOFF 上下文交接和多 Harness 协作 |

### AI/提示词（已摄入 ✅）

| 页面 | 原始来源 | 摘要 |
|------|---------|------|
| [[KnowledgeBase/sources/12个常用Prompt-summary|12 个常用 Prompt]] | [[AI/提示词/提示词]] | 12 个提示词，覆盖问题澄清、学习研究、解题、决策与自我探索；已按主题并入提示词库 |

### AI/AIOps/AIOps-skills（自研 Skills ✅）

| 页面 | 原始来源 | 摘要 |
|------|---------|------|
| [k8s-report-skills](sources/k8s-report-skills-summary.md) | [AI/AIOps/AIOps-skills/k8s-report-skills](../AI/AIOps/AIOps-skills/k8s-report-skills/SKILL.md) | Python 版：kubernetes 客户端 + Jinja2，6 大巡检维度，Agent API 集成 |
| ↑ 同上 | [AI/AIOps/AIOps-skills/k8s-inspect-skills](../AI/AIOps/AIOps-skills/k8s-inspect-skills/SKILL.md) | Shell 版：kubectl + 深色仪表盘 HTML，7 大模块含证书/网络检查 |

### AI/AI-视觉（已摄入 ✅）

| 页面 | 原始来源 | 摘要 |
|------|---------|------|
| [[KnowledgeBase/sources/effective-html-agent-workflow-summary|Effective HTML Agent 页面工作流]] | [[AI/AI-视觉/Effective-HTML-Agent页面工作流]] | 任务路由、线框→原型→图表→视觉设计，以及 HTML 直出、自包含交付、设计范本和同类工具边界 |

### AI/AIOps/agents身份文件（OpenClaw 多智能体定义 ✅）

| 页面 | 原始来源 | 摘要 |
|------|---------|------|
| [多智能体定义导出](sources/openclaw-agents-export-summary.md) | [AI/AIOps/agents身份文件/](../AI/AIOps/agents身份文件/) | 8 个智能体（aiops/linux/container/k8s/architect/backend/frontend/pm）完整定义文件 + 4 个 Skills |

### Docker-Kubernetes（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [Docker](sources/docker-batch-summary.md) | 13 | Docker 基础、镜像离线分发、GPU 配置与服务部署实战（GitLab/Prometheus/Loki 等） |
| [[KnowledgeBase/sources/docker-image-download-summary|Docker 镜像无引擎下载]] | 1 | Registry 直接拉取、多架构选择、断点续传、重试与 tar 离线导入 |
| [Docker 安全加固](sources/docker-security-capabilities-summary.md) | 1 | Capabilities 最小化、no-new-privileges 防提权、User Namespace/只读文件系统/资源限制纵深防御 |
| [[KnowledgeBase/sources/k8s-basic-resources-batch-summary\|K8s 基础资源]] | 22 | Pod/Deployment/Service/Ingress/ConfigMap/Storage/RBAC/CRD/Operator/API Server 深度剖析/Finalizer；StatefulSet Recreate Alpha 与 PVC/PV 生命周期 |
| [[KnowledgeBase/sources/kubectl-server-side-apply-summary|kubectl Server-side Apply]] | 1 | CSA 三路合并、SSA 字段所有权、CRD schema 与 Helm 4 迁移边界 |
| [[KnowledgeBase/sources/kubectx-kubens-multi-cluster-summary|kubectx 与 kubens 多集群切换]] | 1 | context/namespace 快速切换、fzf、kube-ps1、多 kubeconfig 合并及生产防误操作 |
| [[KnowledgeBase/sources/k8s-probe-restart-storm-summary|K8s 健康探针重启风暴]] | 1 | Liveness 误判外部依赖抖动引发 300+ Pod 连锁重启，覆盖探针分工、时间窗口、监控和治理 |
| [K8s 标签与选择器](sources/k8s-labels-selectors-summary.md) | 1 | 5 条 SRE 铁律（selector 匹配/节点调度/成本归因/版本陷阱/单值原则）、4 个翻车案例、`app.kubernetes.io/*` 命名规范 |
| [K8s 容器设计模式](sources/k8s-container-design-patterns-summary.md) | 1 | Sidecar/Init Container/Ambassador/Adapter 四大模式：核心理念、场景、完整 YAML、选型对比 |
| [K8s PDB 实战](sources/k8s-pdb-summary.md) | 1 | PodDisruptionBudget 自愿中断保护、四大配置陷阱、与 drain/滚动更新/HPA 的配合 |
| [K8s 安装管理](sources/k8s-installation-management-batch-summary.md) | 17 | v1.20→v1.35 安装演进、企业高可用、etcd HA、运行时迁移、cgroup v2 |
| [K8s CGroup v2](sources/k8s-cgroup-v2-summary.md) | 1 | cgroup v1→v2 架构演进、K8s 实战配置（kubelet/containerd 对齐）、5 个生产踩坑案例、Prometheus 监控告警 |
| [K8s 监控日志](sources/k8s-monitoring-logging-batch-summary.md) | 20 | Prometheus 全栈、EFK/Loki 日志、Jaeger/SkyWalking 链路追踪、日志管理+六种采集方案+审计日志（三合一）、OpenTelemetry 统一可观测性、集群巡检脚本 |
| [K8s CI/CD](sources/k8s-CICD-batch-summary.md) | 21 | Jenkins/ArgoCD/GitLab CI/Tekton/Kustomize/GitHub Actions/Claude Code AI CI/CD |
| [[KnowledgeBase/sources/kustomize-base-overlay-summary|Kustomize Base 与 Overlay 多环境配置]] | 1 | Base/Overlay 分层、六个常用字段、构建/差异检查/部署顺序与弃用字段边界 |
| [K8s 发布策略](sources/k8s-release-strategy-summary.md) | 1 | 蓝绿部署/金丝雀发布三种方案（原生/Nginx Ingress/Argo Rollouts）、选型决策树、数据库兼容性 |
| [K8s 网络与服务网格](sources/k8s-networking-service-mesh-batch-summary.md) | 5 | Ingress-Nginx/External-DNS/Calico/Istio 流量管理 |
| [K8s 安全认证](sources/k8s-security-auth-batch-summary.md) | 8 | Cert-Manager/External Secrets/Kyverno（部署、策略与1.18迁移）/OAuth2 Proxy/Trivy/SonarQube/Security Context |
| [[KnowledgeBase/sources/cert-manager-tls-automation-summary|cert-manager TLS 自动化]] | 1 | Helm 安装、自签名 Pod TLS、HTTP01/DNS01、Cloudflare/Azure DNS、续期、排障与回滚 |
| [[KnowledgeBase/sources/kyverno-1.18-summary\|Kyverno 部署与策略实践]] | 1 | Helm/HA、十组策略、Harbor/Smart Remote、审计灰度与 1.18 安全及 CEL 迁移 |
| [K8s 扩缩容与存储](sources/k8s-scaling-storage-batch-summary.md) | 9 | HPA/VPA、KEDA/KServe、Goldilocks 与 FinOps + 原生 HPA Scale-to-Zero + PV/PVC 数据保护 + NFS/Ceph/CubeFS 存储 |
| [KServe + KEDA 请求指标扩缩容](sources/kserve-keda-request-autoscaling-summary.md) | 1 | KServe/vLLM 指标经 Prometheus、KEDA、External Metrics API 驱动 HPA，实现 1→2→1 扩缩容 |
| [[KnowledgeBase/sources/k8s-hpa-scale-to-zero-1.37-summary|K8s 1.37 HPA Scale-to-Zero]] | 1 | HPAScaleToZero Beta、External/Object 指标、Worker 缩零、冷启动防抖与 KEDA 迁移清单 |
| [PV/PVC 回收策略](sources/k8s-pv-pvc-reclaim-policy-summary.md) | 1 | PVC 删除后的 PV 回收策略、Released 复用风险、快照与 StatefulSet 安全删除 |
| [[KnowledgeBase/sources/k8s-volume-health-monitor-summary|Kubernetes Volume Health Monitor]] | 1 | CSI 卷健康状态写入 PVC/Pod/CSINode、VolumeHealthMonitor Alpha 前提、Prometheus 分级告警与自动修复边界 |
| [K8s 中间件与 UI](sources/k8s-db-middleware-UI-batch-summary.md) | 19 | Redis/MySQL/PostgreSQL/Kafka/RabbitMQ 部署 + Dashboard/Rancher/k9s 管理工具 |
| [RabbitMQ HA](sources/rabbitmq-ha-summary.md) | 1 | Helm 部署 RabbitMQ 高可用集群（StatefulSet）、aliyun Chart 配置、旧版 API 兼容修复 |
| [K8s 杂项](sources/k8s-misc-batch-summary.md) | 19 | Helm 工具链/CKA-CKS/KubeBlocks/Harbor/Dragonfly/K3S/Velero/GPU |
| [[KnowledgeBase/sources/dragonfly-harbor-p2p-distribution-summary|Dragonfly 与 Harbor P2P 分发]] | 1 | Harbor 源站卸载、Peer 分块交换、AI 大文件分发、新旧架构和版本边界 |
| [K8s NVIDIA Device Plugin](sources/k8s-nvidia-device-plugin-summary.md) | 1 | NVIDIA GPU 驱动与 Container Toolkit 前置检查、Device Plugin/Helm/GPU Operator 部署、验证与故障排查 |
| [K8s 备份与灾备](sources/k8s-backup-dr-summary.md) | 1 | 三层容灾架构（etcd 快照/Velero/应用数据）、自动化备份 CronJob、六大生产避坑、RTO/RPO 目标 |

- [[KnowledgeBase/sources/longhorn-block-storage-summary|Longhorn 轻量块存储]] — 每卷引擎与多副本、同步复制、快照备份、v2 SPDK、云盘/Ceph/Rook 分工与实现校核。

- [[KnowledgeBase/sources/deepseek-3fs-summary|DeepSeek 3FS 来源摘要]] — AI 集群存储负载、四组件架构、USRBIO/RDMA、CRAQ、性能口径与社区缓存集成。

- [[KnowledgeBase/sources/argocd-sync-troubleshooting-summary|ArgoCD 同步故障排查 来源摘要]] — 五类同步问题、三组原文案例、配置示例与官方资料校正。

- [[KnowledgeBase/sources/kubectl-krew-plugins-summary|kubectl 插件指南 来源摘要]] — 本机 Krew 安装清单、14 个业务插件的运维用法、ACK D7 实测与参数边界。

- [[KnowledgeBase/sources/k8s-cluster-autoscaler-summary|Cluster Autoscaler 节点扩缩容来源摘要]] — 节点组选择、缩容保护、Helm 部署、参数、监控排障与上线回滚。

- [[KnowledgeBase/sources/k8s-node-swap-summary|Kubernetes NodeSwap 配置与验证来源摘要]] — LimitedSwap、QoS 与额度公式、k3s drop-in、逐节点上线及四项验证。

- [[KnowledgeBase/sources/metallb-loadbalancer-summary|MetalLB 裸机 LoadBalancer 实战]] — 地址池与宣告、Layer2 / BGP、nginx 外部验证、多地址池和故障切换边界。

### Azure（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [Azure](sources/azure-batch-summary.md) | 17 | VM/VMSS、AKS 全栈、网络/存储、DevOps Pipeline、Policy 治理、诊断工具链 |

### Aliyun（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [Aliyun](sources/aliyun-batch-summary.md) | 19 | ECS/ESS 计算、VPC/SLB/WAF/DDoS 网络安全纵深、OSS 存储、RDS/DTS 数据库、Landing Zone |

### Python（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [Python](sources/python-batch-summary.md) | 27 | 基础语法、运维开发（SSH/subprocess/K8s API）、网络编程/前端、数据分析/AI、项目实战 |
| [Script-Server](sources/script-server-summary.md) | 1 | Python 脚本 Web 化工具，JSON 配置零改动包装脚本为 Web 应用，支持 LDAP/OAuth + 审计日志 |

### Linux-Shell（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [Linux-Shell](sources/linux-shell-batch-summary.md) | 11 | 系统管理、Shell 脚本、SSH/网络、存储/LVM/NFS、zsh/vim/rsync 工具链 |

### AI - OpenClaw 与其他（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [AI-OpenClaw](sources/ai-openclaw-misc-batch-summary.md) | 8 | OpenClaw 全栈（安装/Skills/Channels/AIOps/多智能体）、Copilot CLI |
| [[AI/OpenClaw/OpenClaw-Workspace-运维]] | 1 | Workspace 运维实战——目录规划、多 Agent 隔离、记忆管理、故障排查、安全加固、备份恢复 |
| [飞书CLI画板](sources/feishu-cli-whiteboard-summary.md) | 1 | 飞书 CLI 画板生成能力，AI Agent 一句话生成可编辑架构图/流程图/思维导图 |

### AI/CloudOps-Agent（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [CloudOps-Agent](sources/cloudops-agent-batch-summary.md) | 58 | 三语言（Go/Java/Python）智能 OnCall Agent，RAG/ReAct/Plan-Execute-Replan 架构，Eino/Spring AI Alibaba/LangChain 框架 |

### AI/RAG-Agent（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [RAG-Agent](sources/rag-agent-batch-summary.md) | 33 | 企业级 RAG 知识库系统，Spring Boot 3.4.2 + ES 8.10 混合检索 + Kafka 异步处理 + MinIO 存储 |
| [RAG PDF 解析](sources/rag-pdf-parsing-summary.md) | 1 | PDF 解析难点（无语义结构）、三大技术路线（文本提取/OCR/VLM）、四类工具方案、7 个生产问题 |
| [[Confluence-Wiki-RAG知识库增强检索系统]] | 1 | Confluence + Qdrant + LiteLLM + FastAPI + Vue 全链路 RAG，正文/评论/附件/图片/draw.io 全量打通 |
| [OpenRAG 生产级架构](sources/openrag-production-summary.md) | 1 | 企业级 RAG 平台完整架构：四面分离/异步导入/Chunk建模/混合检索/Reranker/权限模型/K8s高并发/缓存/可观测性/演进路线（21章） |

### AI/Hermes-agent（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [Hermes-agent](sources/hermes-agent-batch-summary.md) | 4 | 满配指南与生态资源、Ubuntu 安装、架构解析与 OpenClaw 对比、Curator Skill 膨胀治理 |

### AI/行业动态（已摄入 ✅）

| 页面 | 原始来源 | 摘要 |
|------|---------|------|
| [Boris Cherny 红杉大会](sources/boris-cherny-sequoia-summary.md) | [[AI/行业动态/Claude-Code创始人红杉大会七个判断\|Claude Code 创始人：红杉大会的 7 个判断]] | Claude Code 创始人 7 个行业判断：代码民主化、MCP 定位、SaaS 护城河瓦解、创业黄金期 |
| [HTML 取代 Markdown](sources/html-vs-markdown-summary.md) | [[AI/行业动态/Anthropic工程师力推HTML取代Markdown-Karpathy附议\|HTML 取代 Markdown：Anthropic 工程师的建议]] | Anthropic 工程师 5 大论据力推 HTML、Karpathy 附议进化路线、Token 成本权衡、哥白尼式智能观 |
| [AI 时代 Git 实践](sources/ai-git-best-practices-summary.md) | [AI/行业动态/AI时代的Git版本管理最佳实践](../AI/行业动态/AI时代的Git版本管理最佳实践.md) | 11 条 Agent Git 最佳实践、Jujutsu/GitButler 新工具、隔离/透明/自动化三原则 |

- [[KnowledgeBase/sources/karpathy-llm-output-understanding-summary|Karpathy 输出理解技巧]] — ASD-STE100 写作、图解、HTML 与定制讲解视频；原始文章：[[AI/行业动态/Karpathy-大模型输出理解技巧-文字图解网页视频]]。

### AI/HarnessKit（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [HarnessKit](sources/harnesskit-summary.md) | 1 | AI 编码智能体统一管理工具，Rust 编写，支持 7 种 Agent 的 Skills/MCP/Plugins/Hooks 跨平台管理与安全审计 |

### AI/工具（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [Graphify](sources/graphify-summary.md) | 1 | 软件工程知识图谱工具，代码 AST 本地解析 + 文档 AI 语义提取，支持关系查询/MCP Server/团队协作 |
| [shiji-kb 知识图谱构造方法论](sources/shiji-kb-knowledge-graph-summary.md) | 1 | 开源古籍知识工程：AI 将《史记》57 万字结构化（10 万实体/3185 事件/7652 关系），沉淀 26 个可复用 Skill（9 大阶段） |
| [K8s MCP Server + Dify](sources/k8s-mcp-server-dify-summary.md) | 1 | Dify + Kubernetes MCP Server 智能运维，实时集群感知/自然语言运维/自动故障分析/企业知识库 |
| [AIOps Golang 工具链](sources/aiops-golang-k8s-toolchain-summary.md) | 1 | Go 三层递进工具链：Cobra CLI 基座 → Function Calling ChatOps → RAG 故障诊断，含完整源码 |
| [[KnowledgeBase/sources/ai-code-review-validation-loop-summary|AI 代码审查验证闭环]] | 1 | 质量门禁、完整仓库上下文、真实运行、安全扫描、敏感信息清理与对抗式测试 |

### AI/企业级私有化大模型（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [[KnowledgeBase/sources/model-precision-quantization-summary|大模型精度与量化：FP64 到 NVFP4 来源摘要]] | 1 | FP64/FP32/TF32/BF16/FP16/FP8/INT8/INT4/NVFP4 的结构、scale、显存估算及训练/推理选择 |
| [[KnowledgeBase/sources/kserve-vllm-inferenceservice-summary|KServe 部署 vLLM 来源摘要]] | 1 | InferenceService Standard、Envoy Gateway、PVC 模型存储、GPU 资源与 OpenAI 兼容 API 完整链路 |
| [[KnowledgeBase/sources/local-llm-runtime-selection-summary|大模型本地部署选型来源摘要]] | 1 | Ollama/vLLM/SGLang/vLLM-Omni 选型、模型与镜像离线交付、GPU 显存和容器化边界 |

### IaC/Terraform 基础系列（已摄入 ✅）

- [[KnowledgeBase/maps/terraform-map|Terraform 基础学习地图]] — 15 篇正文与学习路线入口，以生产结构改编的离线输入、OSS、CMS、TFE 和 ACK 示例组织。

- [[KnowledgeBase/sources/iac-terraform-basics-summary|Terraform 基础概念与第一个项目 来源摘要]] — 用临时策略的离线校验实验理解配置、State 和资源，再观察创建、变更与清理。
- [[KnowledgeBase/sources/iac-terraform-hcl-summary|Terraform HCL 语法与配置文件 来源摘要]] — 借 CMS 输入读懂 HCL 块、类型和引用，区分文件组织与资源执行顺序。
- [[KnowledgeBase/sources/iac-terraform-variables-outputs-summary|Terraform 变量、locals 与 outputs 来源摘要]] — 用 CMS 风格 map 输入解释变量赋值、nullable/optional、输出与敏感值边界。
- [[KnowledgeBase/sources/iac-terraform-expressions-summary|Terraform 表达式、函数与模板 来源摘要]] — 通过告警筛选、标签合并和 OSS 策略模板学习 for、函数、JSON 编码与 dynamic。
- [[KnowledgeBase/sources/iac-terraform-providers-summary|Terraform Provider、版本与认证 来源摘要]] — 核对 AliCloud 版本、STS/AssumeRole 和 alias，用空 OSS Bucket 练习 ACL、标签更新与清理。
- [[KnowledgeBase/sources/iac-terraform-resources-dependencies-summary|Terraform Resource、Data Source 与依赖 来源摘要]] — 从账号查询、EIP 过滤和 CMS 依赖链区分 Data Source、资源所有权与生命周期。
- [[KnowledgeBase/sources/iac-terraform-count-for-each-summary|Terraform count 与 for_each 来源摘要]] — 用 CMS 告警对象比较 count 索引与 for_each key，并解释 dynamic 和地址迁移。
- [[KnowledgeBase/sources/iac-terraform-state-summary|Terraform State、漂移与状态操作 来源摘要]] — 观察 OSS 标签漂移和外部删除，区分普通计划、refresh-only 与退出管理。
- [[KnowledgeBase/sources/iac-terraform-backends-workspaces-summary|Terraform Backend、Workspace 与多环境 来源摘要]] — 说明生产 TFE remote Backend、OSS Backend 的区别，以及状态迁移和多环境权限边界。
- [[KnowledgeBase/sources/iac-terraform-modules-summary|Terraform Module 开发与复用 来源摘要]] — 从生产 CMS 联系人与组裁剪模块，贯穿输入、输出、Provider 映射和状态边界。
- [[KnowledgeBase/sources/iac-terraform-import-refactoring-summary|Terraform Import、moved 与 removed 来源摘要]] — 以 OSS Bucket/ACL 导入和 CMS 地址重构说明 import、moved、removed 与跨 State 移交。
- [[KnowledgeBase/sources/iac-terraform-workflow-troubleshooting-summary|Terraform 工作流、Plan 阅读与排错 来源摘要]] — 用 CMS 项目阅读计划、诊断部分失败，并区分本地保存计划与 TFE Workspace Run。
- [[KnowledgeBase/sources/iac-terraform-testing-cicd-summary|Terraform 测试与 CI/CD 协作 来源摘要]] — 为 CMS 教学模块补充 mock 计划测试、固定版本的 CI 和计划退出码、审批执行流程。
- [[KnowledgeBase/sources/iac-terraform-container-summary|Terraform ACK、Kubernetes 与 Helm 来源摘要]] — 沿 ACK 凭据连接链管理实验 Namespace 与 Helm Release，用 Chart 校验和触发更新。
- [[KnowledgeBase/sources/iac-terraform-docs-summary|Terraform terraform-docs 模块文档生成 来源摘要]] — 为 CMS 模块生成接口文档，保留人工说明，并提供注入、Go template 与 CI 检查配置。

### Go（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [Go](sources/go-batch-summary.md) | 9 | 环境配置→变量→控制流→函数→数据结构→OOP→错误处理→云原生选型 |

### HPC / CloudComputing / GPU（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [HPC-Cloud-GPU](sources/hpc-cloud-gpu-batch-summary.md) | 15 | Slurm 调度/PBS/GPU 管理、云原生/微服务/ServiceMesh、GPU 硬件/CUDA/驱动 |

### 杂项领域（已摄入 ✅）

- [[KnowledgeBase/sources/kafka-basics-production-summary|Kafka 入门、生产配置与 Kubernetes 排障]] — 整合主文、迁出的生产章节、参数校正和旧版 ZooKeeper 故障排查。

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [杂项](sources/misc-domains-batch-summary.md) | 18 | Database(MySQL/Redis/MongoDB) + Middlewares(Kafka/RabbitMQ/RocketMQ) + OS + Networking + IaC(Terraform) + Git + C++ + SoftwareTesting |

> [!info] 摄入覆盖
> 2026-10-03 统计为 18 个领域、377 篇学习笔记（Markdown 清单含迁移文章，不含各目录 index.md 导航页和 280 篇引用/嵌入内容），详见 [[KnowledgeBase/inventory/repository-inventory|全库文档盘点]]。2026-09-29 检查时有 33 篇尚无来源摘要，历史清单见 [[KnowledgeBase/maintenance/wiki-lint-2026-09-29|Wiki 健康检查 2026-09-29]]。

> Terraform 系列于 2026-10-02 新增 12 篇正文和 1 个学习路线入口；上面的全库篇数保留为 2026-09-29 盘点快照，本次系列以 [[KnowledgeBase/maps/terraform-map|Terraform 学习地图]] 为当前导航。

- [[KnowledgeBase/sources/distributed-storage-overview-summary|分布式存储全景来源摘要]] — 四条发展路线、三次负载变化、29 篇项目目录和阅读路径。
- [[KnowledgeBase/sources/ceph-storage-summary|Ceph 架构、部署与 Kubernetes 集成来源摘要]] — 原理、硬件、恢复、版本边界和完整旧版示例。

---

## 🗺️ 主题地图（Maps）

| 页面 | 摘要 |
|------|------|
| [领域地图](maps/domain-map.md) | 按技术领域导航全库 |
| [工具地图](maps/tool-map.md) | 按工具/平台聚合知识 |
| [Kubernetes 专题](maps/kubernetes-map.md) | K8s 生态知识导航（Docker-Kubernetes 共 173 篇） |
| [AI 工作流专题](maps/ai-workflow-map.md) | Claude Code + OpenClaw + AI 辅助运维 |
| [Claude Code & OpenClaw 专题](maps/claude-code-openclaw-map.md) | AI 编程与开源 AI 工具 |
| [云平台专题](maps/cloud-platform-map.md) | Aliyun + Azure 对标 |
| [Linux 运维专题](maps/linux-ops-map.md) | Linux 系统管理与 Shell 脚本 |
| [Python 运维开发专题](maps/python-devops-map.md) | Python 运维场景应用 |

- [[KnowledgeBase/maps/terraform-map|Terraform 基础学习地图]] — 入门顺序、逐篇来源摘要与实验边界。

---

## 📊 分析报告（Analysis）

| 页面 | 摘要 |
|------|------|
| [主题覆盖分析](analysis/topic-coverage-analysis.md) | 主要主题的覆盖度与空白评估（2026-04-16 快照，篇数已更新） |
| [高价值知识缺口](analysis/high-value-gaps.md) | 优先填补的知识空白 |
| [后续写作建议](analysis/next-writing-suggestions.md) | 推荐下一步写作方向 |
| [多Agent vs 单Agent架构决策分析](analysis/multi-agent-vs-single-agent.md) | 分析多Agent何时是伪需求，提出信息隔离与并发需求的决策框架 |

- [[KnowledgeBase/analysis/title-review-2026-10-04|文章标题审阅]] — 49 条网页标题与关联引用已按确认方案更新并验收，26 条离线建议未执行；保留原题对照与执行记录。

- [[KnowledgeBase/analysis/WeKnora与CloudOps-Vault适配评估|WeKnora 与 CloudOps Vault 适配评估]] — 基于 v0.8.3 评估检索问答、Wiki 与同步方案，并核实本机 M4 Pro、Colima 配额及 ARM64 镜像兼容性。

---

## 📋 盘点与维护

| 页面 | 摘要 |
|------|------|
| [全库文档盘点](inventory/repository-inventory.md) | 全部文档逐一列出 |
| [领域内容特点分析](inventory/domain-summary.md) | 18 个领域的成熟度与优先级 |
| [[KnowledgeBase/maintenance/wiki-lint-2026-09-29|Wiki 健康检查 2026-09-29]] | 六维健康检查与两轮处理：修复失效链接，删除剪藏暂存目录引用与过时摘要，统一篇数，补全页面格式 |
| [命名规范](maintenance/naming-normalization.md) | 文件命名约定 |
| [增量维护流程](maintenance/update-workflow.md) | 新增文档后的更新步骤 |

- [[KnowledgeBase/maintenance/title-audit-2026-10-04|标题审阅清单]] — 856 个文件的取值标题、正文 H1、标题载体、发布状态与逐项结论。

---

## 🏗️ 按领域导航

| 领域 | 篇数 | 成熟度 | 入口 |
|------|------|:------:|------|
| Docker-Kubernetes | 173 | 🟢 | [kubernetes-map](maps/kubernetes-map.md) |
| Python | 28 | 🟢 | [python-devops-map](maps/python-devops-map.md) |
| Linux-Shell | 11 | 🟡 | [linux-ops-map](maps/linux-ops-map.md) |
| Azure | 17 | 🟢 | [cloud-platform-map](maps/cloud-platform-map.md) |
| Aliyun | 21 | 🟢 | [cloud-platform-map](maps/cloud-platform-map.md) |
| AI | 74 | 🟢 | [ai-workflow-map](maps/ai-workflow-map.md) |
| Go | 11 | 🟡 | [go-基础-01-环境配置-基础](../Go/go-基础-01-环境配置-基础.md) |
| CloudComputing | 7 | 🟡 | [云原生](../CloudComputing/云原生.md) |
| HPC | 4 | 🟡 | [CentOS7-slurm23.02-二进制安装](../HPC/CentOS7-slurm23.02-二进制安装.md) |
| GPU-DeepLearning | 4 | 🟠 | [GPU-basics](../GPU-DeepLearning/GPU-basics.md) |
| Database | 3 | 🟡 | [MySQL入门](../Database/MySQL入门.md) |
| Middlewares | 3 | 🟠 | [Kafka](../Middlewares/Kafka.md) |
| OS | 3 | 🟠 | [OS](../OS/OS.md) |
| Networking | 2 | 🟠 | [计算机网络基础](../Networking/计算机网络基础.md) |
| IaC | 16（含学习路线） | 🟢 | [[IaC/terraform/README\|Terraform 基础系列]] |
| Git | 2 | 🟠 | [git-learning](../Git/git-learning.md) |
| SoftwareTesting | 2 | 🟠 | [软件工程基础](../SoftwareTesting/软件工程基础.md) |
| C++ | 1 | 🟠 | [C++LearningNotes](../C++/C++LearningNotes.md) |

> 篇数按 git 跟踪的 Markdown 文件统计（不含各目录 index.md 导航页；AI 不含 280 篇引用/嵌入内容），统计日期 2026-09-29。

---

## ⭐ 推荐优先阅读

### 云原生核心路径
1. [云原生](../CloudComputing/云原生.md) → 理解云原生哲学
2. [docker基础](../Docker-Kubernetes/docker/docker基础.md) → 容器基础
3. [k8s基础-架构-组件-资源](../Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源.md) → K8s 架构
4. [安装k8s-1.35-基于rockylinux10-最新步骤](../Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤.md) → 最新版安装
5. [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶|Prometheus-Stack：生产部署与运维]] → 可观测性

### AI 赋能运维
1. [Claude Code 基础指南](../AI/ClaudeCode/Claude%20Code%20基础指南.md) → Claude Code 入门
2. [[AI/ClaudeCode/Claude Code 扩展体系|扩展体系]] → MCP、Skills、Slash Commands、Plugin；含 Skill 创建指南与对比 Eval
3. [OpenClaw-基础-安装](../AI/OpenClaw/OpenClaw-基础-安装.md) → OpenClaw 入门
4. [[AI/Obsidian/obsidian-claude-code-AI知识库完整指南|Obsidian + Claude Code：AI 知识库指南]] → 知识库完整指南

### 云平台实战
1. [VPC](../Aliyun/网络/VPC.md) + [Azure-Networking](../Azure/6_Azure-Networking.md) → 云网络对比
2. [负载均衡SLB](../Aliyun/网络/负载均衡SLB.md) + [AKS-basics](../Azure/2_AKS-basics.md) → 负载均衡与 K8s 托管服务
3. [python-Linux-operation](../Python/python-运维开发/python-Linux-operation.md) → 自动化运维脚本


## 📌 KV Cache

### 概念页

- [[KnowledgeBase/concepts/KV Cache|KV Cache]] — Attention K/V 复用、Prefill/Decode、PagedAttention、显存带宽与集群调度

### 来源摘要

- [[KnowledgeBase/sources/kv-cache-inference-cluster-summary|KV Cache 从诞生到集群调度来源摘要]] — KV Cache 生命周期、Prefill/Decode、显存带宽瓶颈、Prefix Cache、PD 分离与负载均衡

### 技术文章

- [[AI/企业级私有化大模型/KV Cache-从原理到集群调度]] — 从 Attention 复用到集群调度的完整技术文章


## 📄 来源摘要（增量）

### AI/AI-视觉

- [[KnowledgeBase/sources/anatomy-skill-interactive-explainer-summary|AI 代码动画与科普视频制作]] — 22 种技术与工具、16 类风格、HTML 模板与 Anatomy 工作流；原始文章：[[AI/AI-视觉/AI代码动画与科普视频制作]]。
