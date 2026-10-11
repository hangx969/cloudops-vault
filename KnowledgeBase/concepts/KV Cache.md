---
title: KV Cache
tags:
  - knowledgebase/concept
  - AI/企业级私有化大模型
date: 2026-10-04
sources:
  - "[[开源存储DeepSeek 3FS，AI原生的并行文件系统]]"
  - "[[基于docker部署vLLM和LiteLLM私有化大模型]]"
  - "[[AI/企业级私有化大模型/KV Cache-从原理到集群调度]]"
  - "[[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]]"
aliases:
  - Key-Value Cache
  - KV 缓存
---

# KV Cache

## 定义

KV Cache 是 Transformer Attention 在处理上下文时保存的 Key 和 Value 张量缓存。自回归生成新 token 时，推理引擎复用历史 K/V，只计算新增 token 的 K/V，从而减少重复计算；代价是缓存会随上下文和并发增长，占用大量显存并带来带宽压力。

## 核心要点

- **缓存内容**：每层 Attention 都会产生 K（用于匹配）和 V（用于聚合），KV Cache 保存已处理 token 的这些中间结果。
- **Prefill 与 Decode**：Prefill 批量处理输入、生成初始缓存，主要关注计算吞吐和 TTFT；Decode 逐 token 生成、读取历史缓存并追加新 K/V，主要关注显存带宽、TPOT 和调度效率。
- **生命周期**：请求到达后分配并写入缓存，Decode 期间持续增长，达到上下文上限或请求结束后释放。
- **容量估算**：缓存规模与层数、KV 头数、头维度、上下文长度、KV 数据类型和并发请求数相关；总显存还要叠加模型权重、激活、框架运行时、通信缓冲区和系统开销。
- **内存管理**：PagedAttention 将 KV Cache 切成固定大小的块，支持非连续存储、动态分配和复用，降低连续显存分配导致的碎片与浪费。
- **集群调度**：Prefix Cache 可以复用共享系统 Prompt；Prefill/Decode 分离让节点按计算或显存特性分工；负载均衡则需要在迁移请求时考虑缓存搬运成本。
- **工程瓶颈**：Decode 常处于 memory/IO-bound 状态，GPU 计算单元的峰值算力不等于端到端生成速度；长上下文、高并发和跨节点传输会放大这一问题。

- **磁盘外置**：不活跃的 KV Cache 可放到 3FS 这类分布式存储层，利用较大的容量与读取吞吐；实际收益取决于缓存命中、换入换出开销和适配组件，不能仅由聚合带宽推断推理延迟。

## 与其他概念的关系

- [[KnowledgeBase/concepts/混合精度与模型量化]]：KV Cache 的精度字节数直接影响单请求显存；量化可减少占用，但需要验证质量和框架支持。
- [[基于docker部署vLLM和LiteLLM私有化大模型]]：从 PagedAttention、KV Cache 显存公式和并发容量角度介绍私有化推理。
- [[AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM]]：提供 Kubernetes GPU 服务部署背景，可用于承接 KV Cache 的资源调度设计。

## 在本仓库中的覆盖

- [[AI/企业级私有化大模型/KV Cache-从原理到集群调度]]：覆盖 KV Cache 定义、Prefill/Decode、生命周期、单节点带宽瓶颈与集群调度。
- [[基于docker部署vLLM和LiteLLM私有化大模型]]：覆盖 PagedAttention、KV Cache 显存估算和 vLLM 服务部署。
- [[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]]：把 KV Cache 放入 vLLM/SGLang 选型、上下文长度、显存比例、并发和 PD 分离的工程权衡中。

- [[开源存储DeepSeek 3FS，AI原生的并行文件系统|DeepSeek 3FS 并行文件系统]]：介绍 GPU 显存、CPU 内存、磁盘的多级缓存，以及原文据公开报道提及的实验性适配路径。

## 知识空白

- GQA/MQA、不同 KV 头数与实际模型配置下的精确显存公式和容量规划。
- Prefix Cache 的哈希、块复用、淘汰策略以及跨请求/跨租户的隔离边界。
- Prefill/Decode 分离的网络协议、KV Cache 传输压缩、拓扑感知调度和故障恢复。
- KV Cache 量化、稀疏化、压缩对长上下文质量与吞吐的端到端影响。
