---
title: vLLM
tags:
  - knowledgebase/entity
  - ai/inference-serving
date: 2026-10-04
sources:
  - "[[开源存储DeepSeek 3FS，AI原生的并行文件系统]]"
  - "[[基于docker部署vLLM和LiteLLM私有化大模型]]"
  - "[[AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM]]"
  - "[[AI/企业级私有化大模型/一个 Deployment 就能跑 vLLM，为什么还需要 KServe？]]"
  - "[[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]]"
aliases:
  - vLLM Serving
---

# vLLM

## 简介

vLLM 是面向大语言模型的高吞吐推理与服务引擎，提供高效 KV Cache 管理、Continuous Batching、分布式并行和 OpenAI 兼容 API。它适合把 DeepSeek、Qwen、Llama 等模型部署为生产级在线服务。

## 核心功能

- **高吞吐调度**：动态批处理不同生成阶段的请求，提高 GPU 利用率。
- **KV Cache 管理**：通过块式管理降低碎片，并在上下文长度、并发与显存之间做资源规划。
- **并行推理**：支持 Tensor、Pipeline、Data 等并行方式，部署方式需匹配 GPU 与网络拓扑。
- **服务接口**：通过 `vllm serve` 暴露 OpenAI 兼容 API，并可用 `--served-model-name` 隔离业务名与模型路径。
- **平台集成**：可直接容器化，也可由 [[KnowledgeBase/entities/Kubernetes|Kubernetes]]、KServe 和网关管理生命周期与弹性。

## 使用场景

- 通用 LLM/VLM 的高吞吐在线 Serving；
- 单机多 GPU 或多节点模型推理；
- 需要 OpenAI 兼容 API 的私有化部署；
- 通过 KServe、Gateway API 和自动扩缩容构建模型平台。

## 关键工程边界

- `--gpu-memory-utilization` 是当前实例的显存使用目标，不是跨进程硬隔离。
- `--max-model-len` 增大会推高 KV Cache 占用并压缩并发容量。
- `--trust-remote-code` 允许执行模型仓库代码，只应对可信且固定 Revision 的模型启用。
- 性能结论必须基于真实模型、请求分布、精度、GPU 和版本压测。

## 相关概念与实体

- [[KnowledgeBase/concepts/KV Cache]]：生成阶段复用注意力 K/V 状态的核心显存资源。
- [[KnowledgeBase/concepts/混合精度与模型量化]]：影响权重显存、吞吐和硬件兼容性。
- [[KnowledgeBase/entities/CUDA]]：GPU 执行环境与版本兼容基础。
- [[KnowledgeBase/entities/Docker]]：隔离 PyTorch/CUDA Runtime 并支持离线复制。
- [[KnowledgeBase/entities/Kubernetes]]：编排 Worker、GPU 资源、网关和弹性。
- [[KnowledgeBase/entities/Ollama]]：更偏向本地体验与模型管理的替代入口。

## 在本仓库中的覆盖

- [[基于docker部署vLLM和LiteLLM私有化大模型]]：权重、KV Cache、显存估算和 LiteLLM 网关。
- [[AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM]]：Kubernetes GPU 服务部署。
- [[AI/企业级私有化大模型/一个 Deployment 就能跑 vLLM，为什么还需要 KServe？|为何用 KServe 管理 vLLM 推理服务？]]：InferenceService、Gateway API、PVC 与自动扩缩容。
- [[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]]：与 Ollama、SGLang、vLLM-Omni 的选型及离线交付。

- [[开源存储DeepSeek 3FS，AI原生的并行文件系统|DeepSeek 3FS 并行文件系统]]：原文据公开报道介绍通过 Mooncake 等多级缓存组件间接接入 3FS 的路径，未提供本仓库的接入配置或实测结果。

## 知识空白

- 不同模型和 GPU 上 vLLM 与 SGLang 的可复现实测基线；
- 多节点并行、KV Cache 传输和故障恢复实践；
- vLLM 版本升级兼容矩阵与灰度回滚案例。
