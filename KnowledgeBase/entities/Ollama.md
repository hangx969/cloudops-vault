---
title: Ollama
tags:
  - knowledgebase/entity
  - ai/local-inference
date: 2026-09-13
sources:
  - "[[2.4-Ollama+DeepSeek本地部署（新人必看）]]"
  - "[[基于docker部署vLLM和LiteLLM私有化大模型]]"
  - "[[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]]"
aliases:
  - Ollama 本地推理
---

# Ollama

## 简介

Ollama 是面向开发者和个人用户的本地模型下载、管理与运行工具。它把模型缓存、Runtime、命令行和 API 封装为统一体验，重点是快速上手，而不是大规模 GPU Serving 的极限吞吐。

## 核心功能

- 使用 `ollama pull`、`run`、`list`、`rm` 管理和运行模型；
- 支持 Windows、Linux、macOS 与 Apple Silicon；
- 为本地开发、Demo、PoC 和 Prompt 验证提供低门槛入口；
- 通过本地 API 连接 RAG、Agent 或应用原型。

## 使用场景

- 开发者电脑上的快速模型体验；
- RAG/Agent 项目的本地联调；
- 在正式迁移到 vLLM 或 SGLang 前验证模型与 Prompt；
- 不需要复杂并行、调度和集群能力的轻量服务。

## 相关概念与实体

- [[KnowledgeBase/entities/vLLM]]：面向生产高吞吐 LLM Serving。
- [[KnowledgeBase/entities/ModelScope]]：可作为模型资产下载来源。
- [[KnowledgeBase/entities/Docker]]：用于隔离本地或服务器侧依赖。
- [[KnowledgeBase/concepts/KV Cache]]：高吞吐 Serving 中需要显式规划的缓存资源。

## 在本仓库中的覆盖

- [[2.4-Ollama+DeepSeek本地部署（新人必看）]]：Ollama 与 DeepSeek 的本地部署实践。
- [[基于docker部署vLLM和LiteLLM私有化大模型]]：本地体验与生产 Serving 的定位差异。
- [[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]]：与 vLLM、SGLang、vLLM-Omni 的完整选型对比。

## 知识空白

- Ollama 模型格式、量化与 GPU/CPU 后端的系统对比；
- 团队本地开发模型缓存的复用与治理；
- 从 Ollama 原型迁移到生产 Serving 的自动化流程。
