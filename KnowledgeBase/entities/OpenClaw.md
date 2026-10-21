---
title: OpenClaw
tags:
  - knowledgebase/entity
date: 2026-10-21
sources:
  - "[[AI/AI-视觉/AI代码动画与科普视频制作]]"
  - "[[AI/OpenClaw/OpenClaw-基础-安装]]"
  - "[[AI/OpenClaw/OpenClaw-Skills-Plugins]]"
  - "[[AI/OpenClaw/OpenClaw-Channels]]"
  - "[[AI/OpenClaw/Openclaw-AIOps]]"
  - "[[AI/OpenClaw/Openclaw-多智能体]]"
  - "[[AI/OpenClaw/CoPaw]]"
  - "[[AI/OpenClaw/Ubuntu-2510-Setup-Guide]]"
  - "[[AI/OpenClaw/OpenClaw-Workspace-运维]]"
  - "[[AI/AIOps/agents身份文件/aiops/IDENTITY]]"
  - "[[AI/OpenClaw/OpenClaw-K8s智能运维实战]]"
  - "[[AI/OpenClaw/飞书CLI画板-一句话生成架构图]]"
---

# OpenClaw

## 简介
OpenClaw 是一个大模型驱动的通用 AI Agent 平台，能够操作电脑、管理文件、调用 API，支持多智能体协作、AIOps 运维自动化、Channels 通道管理、Skills 插件扩展以及 CoPaw 交互界面。通过 npm 安装，需要 Node.js 22+ 和 Python 环境，配置文件位于 `~/.openclaw/openclaw.json`。本仓库记录了其安装部署、核心功能模块与实战用法。

## 核心功能模块

### Skills 插件生态
- 通过 **Clawhub** 官方工具管理 Skill 的搜索、安装与升级
- 办公类 Skills：PDF/Excel/PPT 文档处理
- **Agent-browser**（Vercel Labs）：基于 accessibility-tree 快照的浏览器自动化
- 百度搜索 Skill：弥补模型知识截止日期的关键能力
- **second-brain**：个人知识库插件，语义检索 + 自动关联 + 主题聚合 + 知识发现，本地存储不上云
- **AI-Animation-Skill**：44 个 HTML 科普动画模板，AI 自动选模板生成可录制的动画文件，详见 [[AI/AI-视觉/AI代码动画与科普视频制作#3. 模板路线：AI-Animation-Skill|AI-Animation-Skill]]
- **self-improving-agent**：实现"做事-复盘-记录-沉淀-改进"的自我进化行为模式
- **skill-vetter**：四步安全审查流程（来源/代码/权限/风险评级）
- **ClawDeckX**：可视化管理面板
- **feishu-whiteboard-themes**：飞书画板风格美化 Skill，根据图表类型自动推荐视觉风格，[开源地址](https://github.com/inhai-wiki/feishu-whiteboard-themes)，详见 [[AI/OpenClaw/飞书CLI画板-一句话生成架构图]]

### Channels 通道管理
- **飞书 Channel**：支持自动安装和手动安装，Connection Mode 选 WebSocket，需配置事件订阅 `im.message.receive_v1`
- **QQ Channel**：通过腾讯官方快捷接入通道，扫码创建机器人
- 常见排障：代理环境变量残留会导致通信失败，需清理 systemd 服务中的 proxy 环境变量

### AIOps 运维自动化
- 通过飞书 + OpenClaw 远程管理 [[KnowledgeBase/entities/Kubernetes|Kubernetes]] 集群
- 使用 kubectl Skill 以自然语言下发 K8s 管理命令（查询节点、Pod 状态、异常诊断）
- 邮箱 Skill（imap-smtp-email）支持发送 K8s 巡检报告
- 定时任务推荐用 `openclaw cron add` 命令行方式添加

### 多智能体协同
- 解决单智能体"上下文窗口稀释"和线性执行效率低的痛点
- 角色定义三要素：身份定义、任务边界、输出格式约束
- 核心配置文件体系：**IDENTITY.md**（外在人设）、**SOUL.md**（核心价值观）、**AGENTS.md**（工作习惯）
- 飞书多账号路由：通过 `channels.feishu.accounts` + `bindings` 实现一个 bot 对应一个 agent
- agent-to-agent 通信：通过 `tools.agentToAgent` 和 `subagents.allowAgents` 配置
- 标准流程：PM 输出需求分析 -> 架构师分发 -> 前后端并行开发

### Workspace 运维
- Workspace 将 Agent 运行环境拆分为**配置体系**（AGENTS.md/SOUL.md/TOOLS.md 等）和**内容体系**（USER.md/memory/）
- 多 Agent 通过独立 Workspace 实现配置、记忆、权限三重隔离
- Skill 三级加载：系统级 → Workspace 级 → 会话级（高覆盖低）
- 记忆系统支持 builtin（文件系统）和 qmd（结构化语义）两种方案
- 生产安全：权限 700/600 基线、敏感信息环境变量化、审计日志覆盖

### 模型接入
- 支持 OpenAI 协议接入自定义模型（魔塔/Deepseek/GitHub Copilot）
- GitHub Copilot 原生支持，通过 OAuth 设备授权流程接入
- 可通过配置文件或自然语言添加模型

## 使用场景
- **智慧办公与自媒体**：PPT 生成、Excel 与邮件处理、会议处理，以及素材收集、资讯聚合与内容分发
- **远程 K8s 运维**：在飞书中用自然语言通过 kubectl Skill 查询节点与 Pod、诊断异常；按只读 → 诊断 → 变更三阶段逐步放权，并用 OPA 策略设置护栏
- **定时巡检与报告**：用 `openclaw cron add` 添加定时任务，通过 imap-smtp-email Skill 发送 K8s 巡检报告
- **多智能体协作**：PM 输出需求分析，架构师分发任务，前后端并行开发；AIOps 团队的 aiops、linux、container、k8s 智能体各自附带系统初始化、容器运行时与 K8s 集群安装 Skills
- **图表与知识管理**：借助飞书 CLI 画板一句话生成可编辑架构图，用 second-brain 在本地构建个人知识库

## CoPaw 对比
[[AI/OpenClaw/CoPaw|CoPaw]] 是阿里推出的对标 OpenClaw 的 AI Agent 产品，基于 AgentScope 框架。通过 pip 安装，`copaw init --defaults` 初始化，`copaw app` 启动，访问 `127.0.0.1:8088` 使用 WebUI。

## 与 Hermes Agent 的对比
[[AI/Hermes-agent/Hermes与OpenClaw对比及飞书接入指南|Hermes Agent：OpenClaw 对比与飞书接入]] 从六个维度对比了两者：
- **技术栈**：Hermes 采用 Python 轻量后端，OpenClaw 基于 TypeScript 全平台产品
- **工具注册**：Hermes 自注册 + 自动发现，OpenClaw 依托 Clawhub 插件生态
- **记忆系统**：Hermes 有机记忆（MEMORY.md/USER.md 冻结快照），OpenClaw 模块化方案（builtin/qmd）
- **安全模型**：Hermes 选择性信任，OpenClaw 默认安全
- **多智能体**：Hermes 子代理委托（深度限制 2），OpenClaw IDENTITY/SOUL/AGENTS 角色体系
- **部署运维**：Hermes 单进程自包含，OpenClaw Gateway + Worker 分布式架构

## 与 Claude Code 的关系
OpenClaw 和 [[KnowledgeBase/entities/Claude-Code|Claude Code]] 同属 AI Agent 工具，但定位不同：OpenClaw 侧重多智能体协同和渠道对接（飞书/QQ），Claude Code 侧重代码开发场景的 CLI 交互。两者的 Skills/[[KnowledgeBase/entities/MCP|MCP]] 插件扩展机制有可比性。

## 在本仓库中的覆盖
主要集中在 `AI/OpenClaw/` 目录（10 篇文章）和 `AI/AIOps/agents身份文件/` 目录（8 个智能体定义文件集）。

- [[KnowledgeBase/sources/ai-openclaw-misc-batch-summary|AI-OpenClaw 批量摘要]]：OpenClaw 全栈（安装/Skills/Channels/AIOps/多智能体）、Copilot CLI
- [[KnowledgeBase/sources/openclaw-agents-export-summary|多智能体定义导出摘要]]：8 个智能体完整定义文件 + 4 个 Skills
- [[AI/OpenClaw/OpenClaw-基础-安装|OpenClaw-基础-安装]]：定位、应用场景与架构分层，模型 API 准备，Windows/Linux 安装与引导配置，多供应商模型接入（含 GitHub Copilot）
- [[AI/OpenClaw/Openclaw-多智能体|Openclaw-多智能体]]：角色拆分与 IDENTITY/SOUL/AGENTS 角色定义文件，多智能体开发团队和 AIOps 团队的飞书接入实践
- [[AI/OpenClaw/Openclaw-AIOps|Openclaw-AIOps]]：基于飞书 + kubectl Skill 远程管理 K8s，配置邮箱 Skill 发送巡检报告
- [[AI/OpenClaw/OpenClaw-Channels|OpenClaw-Channels]]：飞书（自带版与官方版）和 QQ Channel 配置
- [[AI/OpenClaw/OpenClaw-Skills-Plugins|OpenClaw-Skills-Plugins]]：Clawhub 管理 Skills，办公、自我进化、second-brain、记忆插件、skill-vetter、浏览器与百度搜索等 Skills
- [[AI/OpenClaw/CoPaw|CoPaw]]：阿里对标 OpenClaw 的 Agent 产品，pip 安装与 WebUI 启动
- [[AI/OpenClaw/OpenClaw-Workspace-运维|OpenClaw-Workspace-运维]]：配置与内容分离、多 Agent 隔离、记忆系统、Skill 加载层级、故障排查与备份恢复
- [[AI/OpenClaw/Ubuntu-2510-Setup-Guide|Ubuntu-2510-Setup-Guide]]：Ubuntu 25.10 新机初始化，含 SSH、免密 sudo、APT 国内源、开发工具、中文输入法与 VMware Tools
- [[AI/OpenClaw/OpenClaw-K8s智能运维实战|OpenClaw K8s 运维：从只读巡检到低风险变更]]：三阶段渐进（只读→诊断→变更）+ OPA 护栏 + 60 秒诊断修复实战
- [[AI/OpenClaw/飞书CLI画板-一句话生成架构图|飞书CLI画板-一句话生成架构图]]：飞书 CLI 画板生成能力，AI Agent 一句话生成可编辑架构图
- [[AI/Hermes-agent/Hermes与OpenClaw对比及飞书接入指南|Hermes Agent：OpenClaw 对比与飞书接入]]：Hermes Agent 与 OpenClaw 的架构对比及飞书接入
- [[AI/AI-视觉/AI代码动画与科普视频制作#3. 模板路线：AI-Animation-Skill|AI-Animation-Skill]]：以 Skill 形式运行在 OpenClaw 等 Agent 中的 HTML 科普动画模板集，可通过 ClawHub 安装

## 智能体定义文件（AI/AIOps/agents身份文件/）

从多智能体文档导出的 8 个智能体完整定义，可直接部署：

| 智能体 | 角色 | 附带 Skills |
|--------|------|-------------|
| [[AI/AIOps/agents身份文件/aiops/IDENTITY\|aiops]] | AIOps 架构师（调度核心） | k8s-install-orchestrator |
| [[AI/AIOps/agents身份文件/linux/IDENTITY\|linux]] | Linux 专家 | rocky-linux10-init |
| [[AI/AIOps/agents身份文件/container/IDENTITY\|container]] | 容器专家 | docker-runtime-install |
| [[AI/AIOps/agents身份文件/k8s/IDENTITY\|k8s]] | K8s 专家 | k8s-cluster-install |
| [[AI/AIOps/agents身份文件/architect/IDENTITY\|architect]] | 架构师 | — |
| [[AI/AIOps/agents身份文件/backend-engineer/IDENTITY\|backend]] | 后端工程师 | — |
| [[AI/AIOps/agents身份文件/frontend-engineer/IDENTITY\|frontend]] | 前端工程师 | — |
| [[AI/AIOps/agents身份文件/pm/IDENTITY\|pm]] | 产品经理 | — |

## 相关概念与实体
- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]
- [[KnowledgeBase/entities/MCP|MCP]]
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]

## 知识空白
- ~~OpenClaw 与 Kubernetes 集群的 AIOps 集成~~（已有 K8s 智能运维实战文章覆盖）
- 多智能体在 DevOps 场景中的应用
- OpenClaw Skills 与 MCP 协议的对比
