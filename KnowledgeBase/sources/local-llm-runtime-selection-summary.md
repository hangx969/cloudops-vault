---
title: 大模型本地部署选型来源摘要
tags:
  - knowledgebase/source
  - ai/inference-serving
  - ai/private-deployment
date: 2026-09-13
aliases:
  - Ollama vLLM SGLang vLLM-Omni 选型来源摘要
---

# 大模型本地部署选型来源摘要

## 元信息

- **原始文档**：[[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]]
- **领域**：AI 推理服务、私有化部署
- **摄入日期**：2026-09-13

## 摘要

本文从模型资产、离线交付、推理 Runtime、GPU 显存和容器化部署五个层面比较 Ollama、vLLM、SGLang 与 vLLM-Omni。核心结论是：Ollama 适合本地体验，vLLM 适合通用高吞吐 LLM Serving，SGLang 适合复杂生成与高级调度，vLLM-Omni 面向受支持的图像、视频、音频和 Omni 模型。生产架构应通过 Model Gateway 向业务暴露稳定能力接口，并将模型版本、GPU 调度和 Worker 生命周期解耦。

## 关键知识点

1. 模型权重、推理 Runtime 与 Model Gateway 是三个独立层次；业务不应绑定真实模型目录或具体引擎。
2. 模型离线交付需同时搬运权重与 Runtime 镜像，并记录 Revision、Digest、校验和、许可证及驱动/CUDA 边界。
3. `--gpu-memory-utilization` 是 vLLM 单实例的显存目标比例，不是跨进程硬隔离；上下文长度、KV Cache 与并发存在直接取舍。
4. SGLang 的 Prefix Cache、RadixAttention 和 Prefill/Decode 分离适合复杂、高规模 Serving，但会增加部署复杂度。
5. vLLM-Omni 的模型支持与 API 依赖具体版本；ComfyUI 零散组件目录不能直接视为完整可服务仓库。
6. 测试环境可在单容器中运行多个独立进程；生产环境更适合一个模型 Worker 一个容器，以获得故障隔离与独立扩缩容。
7. Docker 的主要收益是依赖隔离、离线复制和回滚；正确配置时 GPU 计算性能通常接近宿主机。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Ollama]]
- [[KnowledgeBase/entities/vLLM]]
- [[KnowledgeBase/entities/ModelScope]]
- [[KnowledgeBase/entities/Docker]]
- [[KnowledgeBase/entities/CUDA]]
- [[KnowledgeBase/entities/NVIDIA]]
- [[KnowledgeBase/concepts/KV Cache]]
- SGLang
- vLLM-Omni

## 值得注意

- 运行时性能不能只看峰值 tokens/s，应结合 TTFT、TPOT、P95/P99、显存、错误率和运维复杂度压测。
