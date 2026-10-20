---
title: AI 工作流专题地图
tags:
  - knowledgebase/map
  - knowledgebase/ai
aliases:
  - AI Workflow Map
date: 2026-10-20
sources:
  - "[[AI/AI-视觉/Anatomy-Skill-交互模型与科普视频]]"
  - "[[AI/Obsidian/github-pages-quartz]]"
  - "[[AI/ClaudeCode/Claude Code 基础指南]]"
  - "[[AI/ClaudeCode/Claude Code 扩展体系]]"
  - "[[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams]]"
  - "[[AI/ClaudeCode/Claude-Skill质检工具-SkillCraft]]"
  - "[[AI/ClaudeCode/Claude-Code-Harness实战-最小可用系统]]"
  - "[[AI/ClaudeCode/CLAUDE.md最佳实践-21条指令清单]]"
  - "[[AI/ClaudeCode/CLAUDE.md最佳实践-12条规则模板]]"
  - "[[AI/Code review和知识图谱/code-review-graph-本地代码知识图谱]]"
  - "[[AI/Codex/Codex-Harness架构-任务循环与扩展]]"
  - "[[AI/Codex/Codex-使用技巧和最佳实践]]"
  - "[[AI/Code review和知识图谱/AI代码审查闭环-验证优先与敏感信息清理]]"
  - "[[AI/Code review和知识图谱/CodeGraph-代码语义知识图谱]]"
  - "[[AI/Code review和知识图谱/Graphify-软件工程知识图谱工具]]"
  - "[[AI/Code review和知识图谱/Understand-Anything-代码知识图谱可视化]]"
  - "[[AI/OpenClaw/OpenClaw-基础-安装]]"
  - "[[AI/OpenClaw/OpenClaw-Channels]]"
  - "[[AI/OpenClaw/OpenClaw-Skills-Plugins]]"
  - "[[AI/OpenClaw/CoPaw]]"
  - "[[AI/OpenClaw/Openclaw-AIOps]]"
  - "[[AI/OpenClaw/Openclaw-多智能体]]"
  - "[[AI/OpenClaw/Ubuntu-2510-Setup-Guide]]"
  - "[[AI/OpenClaw/OpenClaw-K8s智能运维实战]]"
  - "[[AI/Hermes-agent/Hermes-Agent-满配指南与生态资源]]"
  - "[[AI/Hermes-agent/Ubuntu 25.10 安装与使用 Hermes Agent 指南]]"
  - "[[AI/Hermes-agent/Hermes与OpenClaw对比及飞书接入指南]]"
  - "[[AI/Hermes-agent/Hermes-Curator-Skill膨胀治理]]"
  - "[[AI/行业动态/Claude-Code创始人红杉大会七个判断]]"
  - "[[AI/行业动态/Anthropic工程师力推HTML取代Markdown-Karpathy附议]]"
  - "[[AI/行业动态/AI时代的Git版本管理最佳实践]]"
  - "[[AI/行业动态/Karpathy-大模型输出理解技巧-文字图解网页视频]]"
  - "[[AI/AI-视觉/Effective-HTML-Agent页面工作流]]"
  - "[[AI/AI-视觉/Markdown-Viewer-Skills-Markdown中直接画图]]"
  - "[[AI/AI-视觉/html-anything-AI生成HTML全场景工具]]"
  - "[[AI/AI-视觉/AI-Animation-Skill-科普动画]]"
  - "[[AI/ClaudeCode/HarnessKit]]"
  - "[[AI/GithubCopilot/Copilot CLI]]"
  - "[[AI/提示词/提示词]]"
  - "[[AI/Obsidian/obsidian-claude-code-AI知识库完整指南]]"
  - "[[AI/Obsidian/Obsidian可视化Skills-Excalidraw-Mermaid-Canvas]]"
  - "[[Python/python-运维开发/python-kubernetes-module]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/Prometheus基础]]"
  - "[[Python/python-运维开发/python-Linux-operation]]"
---

# 🤖 AI 工作流专题地图

> [!info] 专题范围
> 覆盖 AI/ 目录下的 AI Agent、视觉交付、运维应用和行业动态文档。

---

## 核心概念
- [[KnowledgeBase/entities/Claude-Code|Claude-Code]] — AI 编码与知识管理助手
- [[KnowledgeBase/entities/Codex|Codex]] — AI 编程助手，支持 Harness 任务循环、配置化交互与工具扩展
- [[KnowledgeBase/entities/OpenClaw|OpenClaw]] — AI 多智能体运维平台
- [[KnowledgeBase/entities/MCP|MCP]] — Model Context Protocol
- [[KnowledgeBase/entities/Obsidian|Obsidian]] — 知识管理工具

---

## 📖 推荐阅读顺序

### Claude Code 路径
1. [[Claude Code 基础指南|Claude Code 基础指南]] — 入门必读
2. [[AI/ClaudeCode/Claude Code 扩展体系|扩展体系]] — MCP + Skills + Slash Commands + Plugin 四层扩展机制
3. [[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams|多智能体协作]] — Subagents 与 Agent Teams
4. [[AI/ClaudeCode/Claude-Skill质检工具-SkillCraft|Skill Craft 质检工具]] — 7 类失效模式 + 三层评估 + 四模式质量工程
5. [[AI/ClaudeCode/Claude-Code-Harness实战-最小可用系统|Harness 实战：从零搭建最小可用系统]] — 四层约束架构 + Git 门禁，系统强制执行安全边界
6. [[AI/ClaudeCode/CLAUDE.md最佳实践-21条指令清单|Mayank Agarwal：21 条 CLAUDE.md 指令]] — 五维度通用指令清单（沟通/行为/上下文/记忆/安全）
7. [[AI/ClaudeCode/CLAUDE.md最佳实践-12条规则模板|Mnilax 的 CLAUDE.md：12 条规则]] — Karpathy 4 条 + 8 条新规则，实测错误率 41%→3%
8. [[code-review-graph-本地代码知识图谱|code-review-graph：本地代码知识图谱指南]] — 本地 AST 图谱 + MCP 接入，blast-radius 影响范围分析

### Codex 路径
1. [[AI/Codex/Codex-Harness架构-任务循环与扩展|Codex Harness 架构]] — App Server、Agent 主循环、上下文、工具执行、状态记忆与扩展入口
2. [[AI/Codex/Codex-使用技巧和最佳实践|Codex 使用技巧和最佳实践]] — 配置、安全边界、主动澄清、Token 优化、HANDOFF 与多 Harness 协作

### AI 代码审查与知识图谱
1. [[AI/Code review和知识图谱/AI代码审查闭环-验证优先与敏感信息清理|AI 代码审查闭环]] — 质量门禁、真实运行、安全扫描、敏感信息清理与对抗式测试
2. [[AI/Code review和知识图谱/code-review-graph-本地代码知识图谱|code-review-graph：本地代码知识图谱指南]] — 用本地 AST 图谱分析调用链与改动影响范围
3. [[AI/Code review和知识图谱/CodeGraph-代码语义知识图谱|CodeGraph：Claude Code 代码知识图谱]] — 预建代码语义关系，减少 Agent 扫描成本
4. [[AI/Code review和知识图谱/Graphify-软件工程知识图谱工具|Graphify]] — 统一查询代码、文档与多媒体资料关系
5. [[AI/Code review和知识图谱/Understand-Anything-代码知识图谱可视化|Understand-Anything]] — 代码库结构可视化与交互问答

### OpenClaw 路径
1. [[AI/OpenClaw/OpenClaw-基础-安装|OpenClaw-基础-安装]] — 入门安装
2. [[AI/OpenClaw/OpenClaw-Channels|OpenClaw-Channels]] — Channel 配置
3. [[AI/OpenClaw/OpenClaw-Skills-Plugins|OpenClaw-Skills-Plugins]] — Skills 插件开发
4. [[AI/OpenClaw/CoPaw|CoPaw]] — CoPaw 工具
5. [[AI/OpenClaw/Openclaw-AIOps|Openclaw-AIOps]] — AIOps 运维场景
6. [[AI/OpenClaw/Openclaw-多智能体|Openclaw-多智能体]] — 多智能体架构（2974 行，全库最大文档）
7. [[AI/OpenClaw/Ubuntu-2510-Setup-Guide|Ubuntu-2510-Setup-Guide]] — Ubuntu 环境搭建
8. [[AI/OpenClaw/OpenClaw-K8s智能运维实战|OpenClaw K8s 运维：从只读巡检到低风险变更]] — 三阶段渐进（只读→诊断→变更）+ OPA 护栏 + 实战案例

### Hermes Agent 路径
1. [[AI/Hermes-agent/Hermes-Agent-满配指南与生态资源|满配指南与生态资源]] — 五大配置模块 + 高阶进化 + 资源合集
2. [[AI/Hermes-agent/Ubuntu 25.10 安装与使用 Hermes Agent 指南|Ubuntu 安装指南]] — 部署与 OpenClaw 迁移
3. [[AI/Hermes-agent/Hermes与OpenClaw对比及飞书接入指南|Hermes Agent：OpenClaw 对比与飞书接入]] — 五层架构、记忆系统、飞书接入
4. [[AI/Hermes-agent/Hermes-Curator-Skill膨胀治理|Hermes Agent：Skill 膨胀与上下文治理]] — Skill 生命周期管理、四步工作流、Agent 四种记忆

### AI 行业动态
1. [[AI/行业动态/Claude-Code创始人红杉大会七个判断|Claude Code 创始人：红杉大会的 7 个判断]] — 代码价值重估、MCP 定位、SaaS 护城河瓦解、创业机会窗口
2. [[AI/行业动态/Anthropic工程师力推HTML取代Markdown-Karpathy附议|HTML 取代 Markdown：Anthropic 工程师的建议]] — Anthropic 工程师 5 大论据 + Karpathy 进化路线 + 哥白尼式智能观
3. [[AI/行业动态/AI时代的Git版本管理最佳实践|AI 时代 Git 实践]] — 11 条最佳实践 + Jujutsu/GitButler 新工具 + 隔离/透明/自动化三原则

4. [[AI/行业动态/Karpathy-大模型输出理解技巧-文字图解网页视频|Karpathy：大模型输出理解技巧]] — 受控语言、图解、交互网页与讲解视频，附提示词、STE 边界和旁白路线

### AI 视觉与 HTML 交付路径
1. [[AI/AI-视觉/Effective-HTML-Agent页面工作流|Effective HTML 页面工作流]] — 任务判断、线框、交互原型、架构图、计划和视觉设计；直接输出自包含 HTML，并对比 HTML 与 Markdown 的交付边界、20 个设计范本和同类工具定位
2. [[AI/AI-视觉/Markdown-Viewer-Skills-Markdown中直接画图|Markdown Viewer Skills：AI 文档配图]] — 在 Markdown 中嵌入 PlantUML、Vega、Graphviz 等图表
3. [[AI/AI-视觉/html-anything-AI生成HTML全场景工具|html-anything]] — 面向报告、演示文稿、动画和社交卡片的全场景 HTML 生成
4. [[AI/AI-视觉/AI-Animation-Skill-科普动画|AI-Animation-Skill]] — 使用 HTML 模板生成可录制的科普动画
5. [[AI/AI-视觉/Anatomy-Skill-交互模型与科普视频|Anatomy Skill]] — 可交互的结构模型与带配音的科普视频，附案例、额度耗时记录及内容核对边界

### 补充
- [[HarnessKit|HarnessKit]] — AI 编码智能体统一管理工具（Skills/MCP/Plugins/Hooks 跨 Agent 管理）
- [[AI/GithubCopilot/Copilot CLI|Copilot CLI]] — GitHub Copilot CLI
- [[AI/提示词/提示词|提示词库]] — 按需求澄清、学习研究、分析决策、AI 编程、写作表达和自我探索分类
- [[KnowledgeBase/concepts/提示词工程|提示词工程]] — 目标、上下文、约束、交互流程与验证闭环
- [[KnowledgeBase/sources/effective-html-agent-workflow-summary|Effective HTML 来源摘要]] — HTML 直出、自包含视觉交付、设计范本和同类工具边界

---

## 📂 主要文档

### Claude Code（目录共 13 篇，此处列出 5 篇）

| 文章 | 主题 | 关键词 |
|------|------|--------|
| [[AI/ClaudeCode/Claude Code 基础指南|ClaudeCode基础指南]] | 全面指南 | 安装、配置、使用场景 |
| [[AI/ClaudeCode/Claude Code 扩展体系|扩展体系]] | 四层扩展机制 | MCP、Skills、Slash Commands、Plugin |
| [[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams|多智能体协作]] | Subagents 与 Agent Teams | 并行任务、团队协作 |
| [[AI/ClaudeCode/Claude-Skill质检工具-SkillCraft|Skill Craft 质检工具]] | Skill 质量工程 | 7 类失效模式、三层评估、check/fix/create/audit |
| [[AI/ClaudeCode/Claude-Code-Harness实战-最小可用系统\|Harness 实战：从零搭建最小可用系统]] | 安全约束系统 | 四层架构、Hooks 拦截器、规范先行、Git 门禁 |

### Obsidian 知识库（目录共 6 篇，此处列出 3 篇）

| 文章 | 主题 | 关键词 |
|------|------|--------|
| [[AI/Obsidian/obsidian-claude-code-AI知识库完整指南\|Obsidian + Claude Code：AI 知识库指南]] | 完整指南 | Markdown 母语、三层架构、30 分钟上手、六大操作、改造计划 |
| [[AI/Obsidian/Obsidian可视化Skills-Excalidraw-Mermaid-Canvas\|Obsidian 可视化 Skills]] | AI 可视化 | Excalidraw、Mermaid、Canvas、Skills |
| [[AI/Obsidian/github-pages-quartz\|Quartz 4 发布笔记]] | 网站发布 | GitHub Actions、Pages artifact、日夜主题、wikilink 与旧路由兼容 |

### AI 视觉与 HTML 交付（目录共 8 篇笔记，此处列出 5 篇）

| 文章 | 主题 | 关键词 |
|------|------|--------|
| [[AI/AI-视觉/Effective-HTML-Agent页面工作流|Effective HTML 页面工作流]] | Agent 页面制作与 HTML 交付 | 任务路由、线框、原型、架构图、视觉设计、自包含 HTML、HTML vs Markdown、设计范本 |
| [[AI/AI-视觉/Markdown-Viewer-Skills-Markdown中直接画图\|Markdown Viewer Skills：AI 文档配图]] | Markdown 文档配图 | PlantUML、Vega、Graphviz、技能路由 |
| [[AI/AI-视觉/html-anything-AI生成HTML全场景工具|html-anything]] | 全场景 HTML 生成 | Web 原型、演示文稿、视频、社交卡片、导出 |
| [[AI/AI-视觉/AI-Animation-Skill-科普动画|AI-Animation-Skill]] | HTML 科普动画 | 模板、动画、视频录制 |
| [[AI/AI-视觉/Anatomy-Skill-交互模型与科普视频\|Anatomy Skill]] | 交互模型与科普视频 | 结构拆解、讲解配音、学习深度、额度与耗时 |

### OpenClaw（目录共 10 篇，此处列出 7 篇）

| 文章 | 主题 | 关键词 |
|------|------|--------|
| [[AI/OpenClaw/OpenClaw-基础-安装|OpenClaw-基础-安装]] | 基础安装 | 环境搭建、配置 |
| [[AI/OpenClaw/OpenClaw-Channels|OpenClaw-Channels]] | Channel | 通信通道、集成 |
| [[AI/OpenClaw/OpenClaw-Skills-Plugins|OpenClaw-Skills-Plugins]] | Skills 插件 | 自定义能力 |
| [[AI/OpenClaw/CoPaw|CoPaw]] | CoPaw | 交互式工具 |
| [[AI/OpenClaw/Openclaw-AIOps|Openclaw-AIOps]] | AIOps | 智能运维 |
| [[AI/OpenClaw/Openclaw-多智能体|Openclaw-多智能体]] | 多智能体 | Agent 协作、工作流编排 |
| [[AI/OpenClaw/Ubuntu-2510-Setup-Guide|Ubuntu-2510-Setup-Guide]] | Ubuntu 配置 | 开发环境 |

### 行业动态（目录共 6 篇，此处列出 3 篇）

| 文章 | 主题 | 关键词 |
|------|------|--------|
| [[AI/行业动态/Claude-Code创始人红杉大会七个判断\|Claude Code 创始人：红杉大会的 7 个判断]] | AI 行业趋势 | 代码民主化、MCP 定位、SaaS 瓦解、创业机会、Computer Use |
| [[AI/行业动态/Anthropic工程师力推HTML取代Markdown-Karpathy附议\|HTML 取代 Markdown：Anthropic 工程师的建议]] | AI 输出格式 | HTML vs Markdown、信息密度、交互性、一次性编辑器、哥白尼式智能观 |
| [[AI/行业动态/AI时代的Git版本管理最佳实践\|AI 时代 Git 实践]] | Agent Git 工作流 | Atomic Commit、Checkpoint、Stacked PR、Jujutsu、GitButler、AGENT.md |

---

## 📑 来源摘要
- [[KnowledgeBase/sources/anatomy-skill-interactive-explainer-summary|Anatomy Skill 来源摘要]] — 交互模型、配音视频、作者体验记录与适用边界
- [[KnowledgeBase/sources/ai-code-review-validation-loop-summary|AI 代码审查验证闭环]] — 完整上下文、真实运行、安全与信息清理
- [[KnowledgeBase/sources/12个常用Prompt-summary|12 个常用 Prompt 摘要]] — 问题澄清、学习研究、解决问题、决策与自我探索
- [[KnowledgeBase/sources/cloudops-agent-batch-summary|CloudOps-Agent 批量摘要]] — 58 篇，三语言智能 OnCall Agent
- [[KnowledgeBase/sources/rag-agent-batch-summary|RAG-Agent 批量摘要]] — 33 篇，企业 RAG 知识库系统
- [[KnowledgeBase/sources/hermes-agent-batch-summary|Hermes-agent 批量摘要]] — 4 篇，Hermes Agent 安装、资源合集、架构解析与 Curator Skill 治理
- [[KnowledgeBase/sources/k8s-report-skills-summary|K8s 巡检 Skills 摘要]] — K8s 集群巡检 Python/Shell 技能
- [[KnowledgeBase/sources/obsidian-claude-AI知识库完整指南-summary|AI知识库完整指南摘要]] — Obsidian+Claude Code 完整指南（理念+工具+操作+计划）
- [[KnowledgeBase/sources/github-pages-quartz-summary|Quartz 4 发布流程摘要]] — Quartz 4 的固定版本、完整 workflow 与迁移验收。
- [[KnowledgeBase/sources/codex-harness-architecture-summary|Codex Harness 架构摘要]] — Agent 主循环、上下文与工具执行的架构解读

---

## 🔗 与其他领域的连接

- **K8s 自动化：** AI 辅助 K8s 资源管理 → [[Python/python-运维开发/python-kubernetes-module|python-kubernetes-module]]
- **监控告警：** AI 辅助告警分析 → [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus基础|Prometheus基础]]
- **知识管理：** Obsidian 知识库 → 本知识库（KnowledgeBase/）
- **日常运维：** AI 辅助 Linux 运维 → [[Python/python-运维开发/python-Linux-operation|python-Linux-operation]]

---

## 🛠️ 相关工具
[[KnowledgeBase/entities/Claude-Code|Claude-Code]]、[[KnowledgeBase/entities/OpenClaw|OpenClaw]]、[[KnowledgeBase/entities/Hermes-Agent|Hermes Agent]]、[[KnowledgeBase/entities/MCP|MCP]]、[[KnowledgeBase/entities/Obsidian|Obsidian]]、[[HarnessKit|HarnessKit]]
