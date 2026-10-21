---
title: Claude Code
tags:
  - knowledgebase/entity
  - ai/claude-code
date: 2026-10-21
sources:
  - "[[AI/AI-视觉/AI代码动画与科普视频制作]]"
  - "[[Claude Code 基础指南]]"
  - "[[AI/ClaudeCode/Claude Code 扩展体系]]"
  - "[[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams]]"
  - "[[AI/Obsidian/obsidian-claude-code-AI知识库完整指南]]"
  - "[[AI/AIOps/AIOps-skills/k8s-report-skills/SKILL]]"
  - "[[AI/AIOps/AIOps-skills/k8s-inspect-skills/SKILL]]"
  - "[[AI/ClaudeCode/Claude-Skill质检工具-SkillCraft]]"
  - "[[AI/ClaudeCode/Claude-Code-Harness实战-最小可用系统]]"
  - "[[AI/行业动态/Claude-Code创始人红杉大会七个判断]]"
  - "[[AI/ClaudeCode/CLAUDE.md最佳实践-21条指令清单]]"
  - "[[AI/ClaudeCode/CLAUDE.md最佳实践-12条规则模板]]"
  - "[[code-review-graph-本地代码知识图谱]]"
  - "[[AI/ClaudeCode/Claude-Code为什么用grep不用RAG]]"
  - "[[AI/ClaudeCode/Claude-Fable-5-system-prompt]]"
  - "[[Git-Worktree-AI开发实践指南]]"
  - "[[AI/Code review和知识图谱/AI代码审查闭环-验证优先与敏感信息清理]]"
  - "[[AI/AI-视觉/Effective-HTML-Agent页面工作流]]"
aliases:
  - "CC"
---

# Claude Code

## 简介

Claude Code (CC) 是 Anthropic 推出的 CLI 形态 AI 编程助手。它以项目文件夹为作用域（单一项目原则），提供 3 种交互模式，并通过 MCP、Skills、SubAgents、Slash Commands、Plugin 五层扩展机制构成完整的智能工作流系统——不只是聊天机器人，而是可编排、可扩展、可沉淀知识的开发基础设施。

## 核心功能：7 层能力栈

### 1. 基础交互层

CC 提供 3 种操作模式：

- **Normal 模式**：每步操作需人工确认，适合探索和学习
- **Plan 模式**：先讨论方案再执行，适合复杂任务的前期规划
- **Auto-accept 模式**：自动执行所有操作，适合重复性任务

Extended Thinking 支持 4 级思考深度，通过自然语言触发：

| 触发词 | 思考深度 | 适用场景 |
|--------|---------|---------|
| `think` | 基础 | 简单逻辑推理 |
| `think hard` | 中等 | 多步骤问题 |
| `think harder` | 深度 | 复杂架构决策 |
| `ultrathink` | 最深 | 高难度系统设计 |

### 2. 记忆层（CLAUDE.md / AGENTS.md）

CC 通过 Markdown 指令文件保存跨会话的规则，分两级：

- **用户级** (`~/.claude/CLAUDE.md`)：全局偏好，跨项目生效
- **项目级**（项目根目录 `CLAUDE.md` 或 `AGENTS.md`）：项目特定的规范、技术栈、约定

本仓库以 [[AGENTS|AGENTS.md]] 为统一规约，根目录 [[CLAUDE|CLAUDE.md]] 仅包含 `@AGENTS.md`，供 Claude Code 导入同一套规则。该写法见 [Claude Code 官方文档](https://code.claude.com/docs/en/memory#share-one-file-with-other-coding-tools)。

创建方式：`/init` 命令自动生成，或通过 `# memory` 手动追加。

**CLAUDE.md 最佳实践**（详见两篇专题文章）：
- **200 行天花板**：超过 200 行遵循率急剧下降（Mnilax 实测 18 条规则合规率从 76% 掉到 52%）
- **Karpathy 4 条基础规则**（先思后码/简单至上/外科手术式修改/目标驱动）覆盖 ~40% 失败模式
- **Mnilax 12 条完整模板**（补齐 Token 预算/暴露冲突/先读后写/测试意图/检查点/约定优先/显式失败）将错误率从 41% 降到 3%
- **Mayank 21 条指令清单**（沟通方式/行为准则/个人上下文/记忆连续性/开发者安全）覆盖非开发者场景 + MEMORY.md/ERRORS.md 记忆系统

**Spec 工作流**是记忆层的高级应用，解决长对话中上下文丢失问题，分 4 步：
1. 需求文档 → 2. 技术方案文档 → 3. TODO 拆解 → 4. spec.md 整合

每步产出物都持久化为文件，即使上下文窗口截断也不会丢失关键信息。

### 3. MCP 扩展层

MCP (Model Context Protocol) 为 CC 提供外部工具集成能力。

**必装三件套：**
- **memory**：跨会话持久化记忆
- **context7**：实时拉取最新库文档，避免训练数据过时
- **sequential-thinking**：结构化多步推理，提升复杂问题解决质量

**已记录的 10+ MCP 服务器：**

| 服务器 | 用途 |
|--------|------|
| atlassian | Jira/Confluence 集成 |
| bitbucket | 代码仓库操作 |
| playwright | 浏览器自动化测试 |
| filesystem | 文件系统操作 |
| github | GitHub API 集成 |
| exa | AI 搜索引擎 |
| deepwiki | GitHub 仓库文档生成 |
| drawio | 流程图/架构图生成 |
| mcp-obsidian | Obsidian 笔记库集成 |
| context7 | 实时文档查询 |

### 4. Skills 技能层

Skills（2025 年 10 月推出）是自动触发的能力包，采用渐进式加载设计：

- **元数据优先**：CC 启动时只加载 Skills 的描述信息（metadata）
- **按需加载**：匹配到用户意图后才注入完整 Skill 内容（作为 system prompt）

**3 层使用模式：**
1. **单点自动化**：单个 Skill 完成特定任务（如代码审查、文档生成）
2. **编排式工作流**：多个 Skills 按序协作完成复杂流程
3. **团队智能**：Skills 沉淀团队最佳实践，新成员即插即用

**质量治理**：Skill 写出来 ≠ 用得稳。LLM 存在 7 类系统性失效模式（约束衰减、工具漂移、输出膨胀、依赖链断裂、并行孤岛、触发模糊、幻觉填充），可通过 [Skill Craft](https://github.com/3stoneBrother/skill-craft) 工具的 check/fix/create/audit 四模式进行质量工程治理。

### 5. SubAgents 子智能体

SubAgent 是独立的 Claude 副本，可并行执行任务。每个 SubAgent 由 5 个组件定义：

| 组件 | 作用 |
|------|------|
| name | 标识符 |
| description | 能力描述 |
| tools | 可用工具集 |
| model | 使用的模型 |
| system | 系统提示词 |

数据流向：SubAgent 执行 → 结果返回 CC → CC 汇总后呈现给用户。SubAgent 之间不直接通信，由 CC 主进程协调。

### 5.5 Agent Teams 多智能体团队

Agent Teams 是 SubAgents 的升级形态——多个 Claude Code 实例组成团队协作：

| 对比项 | SubAgents | Agent Teams |
|--------|-----------|-------------|
| 通信 | 只能向主 Agent 汇报 | 队友之间直接互发消息 |
| 协调 | 主 Agent 管理 | 共享任务列表，自主认领 |
| 适用 | 聚焦型任务 | 复杂协作（评审、调试、跨层开发） |
| 成本 | 较低 | 较高（每个队友独立上下文窗口） |

核心组件：Team Lead（协调者）+ Teammates（独立工作者）+ Task List（共享任务）+ Mailbox（消息系统）。支持 in-process 和 split panes（tmux/iTerm2）两种显示模式。当前为实验性功能（需 v2.1.32+）。

### 6. Slash Commands 斜杠命令

斜杠命令是存放在 `.claude/commands/` 目录下的手动触发工作流快捷方式。

**与 Skills 的关键区别：**
- Skills：作为 **system prompt** 注入，自动触发
- Slash Commands：作为 **user message** 注入，手动触发

Slash Commands 可以编排 Skills + SubAgents + MCP，是构建自定义工作流的入口。

### 7. Plugin 插件

Plugin 是应用级打包容器，将多种扩展机制捆绑为一个可分发单元：

| 组成 | 数量上限 |
|------|---------|
| Skills | 5 |
| Slash Commands | 10 |
| MCP 服务器 | 3 |
| SubAgents | 2 |
| Hooks | (未详细展开) |

**建议：Plugin 不超过 3 个**，避免启动卡顿和功能重复。

## 使用场景：关键工作流模式

### Spec 驱动开发
需求文档 → 技术方案文档 → TODO 拆解 → spec.md → 逐项实现。每步产出持久化文件，解决长任务中上下文丢失问题。

### 事故应急响应
1. 并行分流：3 个 SubAgent 同时采集日志、指标、变更记录
2. 根因分析：sequential-thinking MCP 结构化推理
3. 方案生成：输出 3 套缓解方案供选择
4. 执行修复

实测 MTTR 从 45 分钟降至 12 分钟。

### 遗留项目接手
1. Explore SubAgent 扫描项目结构
2. 并行分析：架构 + 数据库 + 安全性三路 SubAgent
3. 技术债评估与优先级排序
4. 知识沉淀：通过 memory MCP 持久化分析结果

### 代码审查
1. 自动检测文件类型
2. 分派专业 SubAgent（前端/后端/安全/性能）
3. 输出按严重级别分级的审查报告

实测生产事故率降低 60%。

## 最佳实践

1. **单一项目原则**：每个项目单独文件夹，避免上下文混乱
2. **Plan 模式优先**：先讨论方案再执行，减少返工
3. **三件套起步**：memory + context7 + sequential-thinking MCP
4. **文档驱动**：Spec 工作流解决上下文丢失问题
5. **知识沉淀**："好的工具链会自己长知识"——让 Claude.md 和 memory 持续积累
6. **Plugin 不超过 3 个**：避免启动卡顿和功能冲突

## 推荐 MCP 组合

| 场景 | 推荐组合 |
|------|---------|
| 日常开发 | filesystem + github + memory |
| 深度工作 | sequential-thinking + context7 + memory |
| 自动化任务 | playwright + filesystem |
| 学习新技术 | context7 + deepwiki + exa |

## 相关概念与实体

- [[KnowledgeBase/entities/MCP|MCP]]：Claude Code 的外部工具集成协议
- [[KnowledgeBase/entities/Obsidian|Obsidian]]：通过 Claudian 插件 + MCP 集成的知识管理平台
- [[KnowledgeBase/entities/OpenClaw|OpenClaw]]：开源 AI 工具平台
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]：CC 的核心应用场景之一

## 在本仓库中的覆盖

- [[AI/AI-视觉/AI代码动画与科普视频制作|AI 代码动画与科普视频制作]]：用代码构建 Canvas、SVG 或 Three.js 画面，结合模板与 Anatomy 交互模型，再通过配音、录制或逐帧渲染制作讲解视频；保留安装方式、风格提示词和作者体验边界。
- [[Claude Code 基础指南]]：模式选择、思考模式、Claude.md、Spec 工作流、实战场景、最佳实践（最全面的综合指南）
- [[AI/ClaudeCode/Claude Code 扩展体系]]：四层扩展机制全解——MCP（10+ 服务器配置）、Skills（3 层使用模式 + 创建指南：触发边界、三层职责、步骤出口、确认门与对比 Eval + 质量治理 + excalidraw-diagram-generator 等开源推荐）、Slash Commands（手动工作流）、Plugin（打包分发）
- [[AI/AI-视觉/Effective-HTML-Agent页面工作流]]：Effective HTML 页面工作流——任务判断、线框、交互原型、架构图、计划和视觉设计，并支持通过插件安装。
- [[KnowledgeBase/sources/effective-html-agent-workflow-summary|Effective HTML 来源摘要]]：HTML 直出、自包含视觉交付、设计范本及与 Markdown Viewer Skills、html-anything、Mermaid 的定位对比。
- [[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams]]：SubAgent（5 组件架构、适用场景评级）+ Agent Teams（Team Lead/Teammates/Task List/Mailbox、竞争假设调试）+ 开源 Agent 生态（wshobson/agents：112 个 Agent、72 个插件）
- [[AI/Obsidian/obsidian-claude-code-AI知识库完整指南|Obsidian + Claude Code：AI 知识库指南]]：Obsidian 集成方案（Claudian + Skills + MCP）、Markdown 母语论证、30 分钟上手路径、Karpathy Wiki 三层架构
- [[AI/AIOps/AIOps-skills/k8s-report-skills/SKILL]]：自研 K8s 巡检 Skill（Python 版）——kubernetes 客户端 + Jinja2 HTML 报告，Agent API 集成
- [[AI/AIOps/AIOps-skills/k8s-inspect-skills/SKILL]]：自研 K8s 巡检 Skill（Shell 版）——kubectl + 深色仪表盘 HTML 报告，7 大巡检模块含证书和网络检查
- [[KnowledgeBase/sources/ClaudeCode基础指南-summary|ClaudeCode基础指南摘要]]：3 种模式、Extended Thinking、Claude.md、5 大实战场景
- [[KnowledgeBase/sources/obsidian-claude-AI知识库完整指南-summary|AI知识库完整指南摘要]]：Claudian/Skills/MCP 三种集成方式、Markdown 母语论证、Karpathy Wiki 三层架构
- [[AI/ClaudeCode/Claude-Skill质检工具-SkillCraft]]：Skill 质量工程——7 类失效模式、三层评估体系、check/fix/create/audit 四模式
- [[KnowledgeBase/sources/skill-craft-summary|Skill Craft 摘要]]：Skill 质量工程工具的核心方法论
- [[AI/ClaudeCode/Claude-Code-Harness实战-最小可用系统|Harness 实战：从零搭建最小可用系统]]：Harness 四层约束架构——约束层/工具层/中间件层/编排层 + Git 门禁，含完整拦截器代码
- [[KnowledgeBase/sources/harness-system-summary|Harness 实战摘要]]：Harness 安全约束系统的核心方法论
- [[AI/行业动态/Claude-Code创始人红杉大会七个判断|Claude Code 创始人：红杉大会的 7 个判断]]：Boris Cherny（Claude Code 创始人）在红杉大会上的 7 个行业判断——代码不再稀缺、古登堡类比、判断力>编码、SaaS 护城河瓦解、创业黄金期、MCP 不会死、Computer Use 价值
- [[KnowledgeBase/sources/boris-cherny-sequoia-summary|红杉大会摘要]]：7 个行业判断的知识提炼

- [[AI/ClaudeCode/CLAUDE.md最佳实践-21条指令清单|Mayank Agarwal：21 条 CLAUDE.md 指令]]：Mayank Agarwal 21 条指令——沟通方式/行为准则/个人上下文/MEMORY.md 记忆连续性/开发者安全五个维度
- [[AI/ClaudeCode/CLAUDE.md最佳实践-12条规则模板|Mnilax 的 CLAUDE.md：12 条规则]]：Mnilax 12 条规则模板——Karpathy 4 条 + 8 条新规则，30 个代码库实测错误率 41%→3%，含 200 行天花板发现和 6 条反面经验

- [[code-review-graph-本地代码知识图谱|code-review-graph：本地代码知识图谱指南]]：本地代码知识图谱工具——Tree-sitter AST 解析→SQLite 图谱→MCP 接入 Claude Code，blast-radius 影响范围分析，2900 文件增量索引 2 秒
- [[AI/Code review和知识图谱/AI代码审查闭环-验证优先与敏感信息清理]]：以质量门禁、完整仓库上下文、真实运行、安全扫描、敏感信息清理和对抗式测试构成 AI 代码审查闭环
- [[AI/ClaudeCode/Claude-Code为什么用grep不用RAG|Claude Code 为何用 grep 而非 RAG 检索代码？]]：Agentic Search 架构解析——Glob+Grep(ripgrep)+Read 替代 RAG，Boris Cherny 播客原话+亚马逊论文实锤+Cursor 反面论证
- [[AI/ClaudeCode/Claude-Fable-5-system-prompt]]：Claude Fable 5 完整系统提示词——Mythos-class 新层级、行为规约体系、~15 个内置工具、沙箱架构、Artifact/Claudeception、MCP 连接器流程、版权硬限制、Skill 强制规则
- [[Git-Worktree-AI开发实践指南|Vibe Coding 的 Git Worktree 实践]]：Git Worktree 并行开发实践——"一个 AI 会话 = 一个 Worktree"原则、紧急修复/多方案探索场景、5 个实践踩坑（与 CC 原生 EnterWorktree 工具吻合）

## 内部架构（来自 Fable 5 系统提示词）

- **模型层级**：Claude Fable 5 = Mythos-class，能力位于 Opus 之上；Fable 5（公开版，含额外安全措施）与 Mythos 5（审批组织版）共享底层模型
- **产品生态**：Claude Code + Claude Cowork（知识工作桌面应用）+ Chrome/Excel/PowerPoint Agent（beta）
- **沙箱**：Ubuntu 24 容器，文件系统每次任务重置，网络白名单
- **Claudeception**：Artifact 可直接调用 Anthropic API（使用 sonnet-4 模型，无需 key）
- **版权硬限制**：单源引用 ≤15 词，每源最多 1 次引用，禁止复制歌词/诗歌

## 知识空白

- ~~Claude Code 的 **Hooks 机制**~~（已有 Harness 实战文章覆盖 PreToolUse/PostToolUse hooks）
- ~~Claude 产品线全貌~~（已有 Fable 5 系统提示词覆盖：Claude Code / Cowork / Chrome / Excel / PowerPoint Agent）
- Claude Code 的**计费模型和成本优化**策略
- Claude Code 与其他 AI 编程工具（Cursor、GitHub Copilot）的**横向对比**
- Claude Code **API 模式 vs CLI 模式**的差异
