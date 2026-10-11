---
title: Hermes Agent
tags:
  - knowledgebase/entity
  - AI/hermes-agent
date: 2026-05-05
sources:
  - "[[AI/Hermes-agent/Hermes-Agent-满配指南与生态资源]]"
  - "[[AI/Hermes-agent/Ubuntu 25.10 安装与使用 Hermes Agent 指南]]"
  - "[[AI/Hermes-agent/Hermes与OpenClaw对比及飞书接入指南]]"
  - "[[AI/Hermes-agent/Hermes-Curator-Skill膨胀治理]]"
aliases:
  - Hermes
  - hermes-agent
---

# Hermes Agent

## 简介

Hermes Agent 是 Nous Research 推出的开源 AI Agent 框架，核心特色是**持久记忆**（MEMORY.md/USER.md 分离 + 前缀缓存）、**自动技能提炼**（Skill Factory 复盘后自动生成新技能）和**跨会话自我进化**能力。Python 轻量后端架构，从 OpenClaw 生态演进而来。

- GitHub：https://github.com/NousResearch/hermes-agent

## 核心功能

- **五层架构**：入口/编排 → Agent 核心 → 工具注册 → 状态/持久 → 平台适配，层间单向依赖
- **持久记忆系统**：内置 MEMORY.md（~2200 字符）/ USER.md（~1375 字符），支持 Hindsight 知识图谱扩展
- **子代理委托**：深度限制 2 层，ThreadPoolExecutor 最多 3 并行，子代理无权修改父级记忆
- **Skill Factory**：任务完成后复盘，自动生成可复用技能
- **Hermes Curator**：后台 Skill 维护系统——监测→降级（30天陈旧/90天归档）→复盘（廉价模型合并重复项）→锁定优先，防止 Skill 无限膨胀
- **Maestro 协作框架**：基于 Beads 架构支持跨 Agent 协作
- **Web Dashboard**：默认端口 9119，Gateway/API 默认端口 8642
- **飞书集成**：WebSocket 模式，无需公网 Webhook

## 使用场景

- 需要长期记忆和上下文积累的个人 AI 助手
- 多 Agent 协作的复杂任务编排
- 与企业 IM（飞书）集成的智能对话
- Token 精细管控的成本敏感场景

## 相关概念与实体

- [[KnowledgeBase/entities/OpenClaw|OpenClaw]]：Hermes 的前身，支持 `hermes claw migrate` 迁移
- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]：同为 AI Agent 工具，RTK 等生态工具可跨平台使用

## 在本仓库中的覆盖

- [[AI/Hermes-agent/Hermes-Agent-满配指南与生态资源]]：五大配置模块实操 + 高阶进化工具 + 生态资源合集
- [[AI/Hermes-agent/Ubuntu 25.10 安装与使用 Hermes Agent 指南]]：Ubuntu 完整部署、Web Dashboard、OpenClaw 迁移、飞书集成
- [[AI/Hermes-agent/Hermes与OpenClaw对比及飞书接入指南|Hermes Agent：OpenClaw 对比与飞书接入]]：五层架构深度解析、记忆系统、与 OpenClaw 六维对比
- [[AI/Hermes-agent/Hermes-Curator-Skill膨胀治理|Hermes Agent：Skill 膨胀与上下文治理]]：Curator 四步工作流（监测/降级/复盘/锁定）、Skill 与记忆的区别、Agent 四种记忆类型

## 知识空白

- Hermes 在生产环境的稳定性和性能表现
- Hermes 与 Claude Code 的功能详细对比
