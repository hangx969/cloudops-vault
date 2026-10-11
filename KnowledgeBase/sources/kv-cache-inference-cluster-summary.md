---
title: KV Cache：从诞生到集群调度 来源摘要
tags:
  - knowledgebase/source
  - AI/企业级私有化大模型
date: 2026-09-06
aliases:
  - KV Cache 来源摘要
---

# KV Cache：从诞生到集群调度 来源摘要

## 元信息

- **原始文档**：[[AI/企业级私有化大模型/KV Cache-从原理到集群调度]]
- **原始来源**：[微信公众号原文](https://mp.weixin.qq.com/s/RajIT1Ozh-qhDkDmvIPD9A)
- **领域**：AI / 企业级私有化大模型
- **摄入日期**：2026-09-06

## 摘要

本文用餐厅服务员和“小本本”的类比解释 KV Cache：模型在 Prefill 阶段批量计算输入的 Key/Value，在 Decode 阶段复用历史缓存并追加新 token，从而避免反复计算上下文。文章进一步梳理 KV Cache 的生命周期、显存占用、GPU 内部的 HBM/SRAM 带宽瓶颈，以及 Prefix Cache、Prefill/Decode 分离和负载均衡等集群调度思路。

## 关键知识点

1. KV Cache 保存 Attention 已计算出的 Key 和 Value；自回归生成时，新 token 只需计算新增 K/V，并读取历史缓存。
2. 没有缓存时，逐 token 生成会反复处理历史上下文，文章用简化模型说明计算量从 O(n²) 降到 O(n)；实际收益取决于实现、上下文长度和批处理方式。
3. Prefill 一次性处理输入，通常受计算吞吐影响并决定 TTFT；Decode 逐 token 生成，主要受历史 KV Cache 读取、显存带宽和调度效率影响，并关注 TPOT。
4. KV Cache 会随对话增长，在请求结束或达到上下文上限后释放；其规模与层数、KV 头数、头维度、上下文长度、精度字节数和并发请求数相关。
5. 单节点瓶颈通常不是计算单元本身，而是 HBM→SRAM→计算单元之间的数据搬运；长上下文和高并发会显著放大显存及带宽压力。
6. 集群层面可复用系统 Prompt 的 Prefix Cache，将 Prefill 与 Decode 分配到不同节点，并在节点接近容量上限时迁移请求和缓存。
7. 文章给出的 70B、128K、64 并发约 640 GB 等数字用于直观展示容量压力；生产估算还应结合 GQA/MQA、实际模型配置、KV 精度、框架块管理、运行时和通信开销。

## 涉及的概念与实体

- [[KnowledgeBase/concepts/KV Cache]]
- [[KnowledgeBase/concepts/混合精度与模型量化]]
- [[基于docker部署vLLM和LiteLLM私有化大模型]]
- [[AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM]]

## 值得注意

- 原文的 O(n²)→O(n) 和显存数字是面向入门理解的简化表达，不应替代针对具体模型和推理框架的压测、容量规划。
- “Prefill 是计算瓶颈、Decode 是搬运瓶颈”是常见工程抽象；实际瓶颈会随 batch、硬件、量化、并行策略和框架实现变化。
