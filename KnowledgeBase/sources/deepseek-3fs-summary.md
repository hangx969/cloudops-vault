---
title: DeepSeek 3FS 并行文件系统来源摘要
tags:
  - knowledgebase/source
  - storage/3fs
  - ai/infrastructure
date: 2026-10-04
sources:
  - "[[开源存储DeepSeek 3FS，AI原生的并行文件系统]]"
aliases:
  - DeepSeek 3FS 来源摘要
  - Fire-Flyer File System 来源摘要
---

# DeepSeek 3FS 并行文件系统来源摘要

## 元信息

- **原始文档**：[[开源存储DeepSeek 3FS，AI原生的并行文件系统|开源存储DeepSeek 3FS，AI原生的并行文件系统]]
- **作者与原文日期**：Aspirer2004，2026-09-25
- **领域**：并行文件系统、AI 集群存储、KV Cache 外置
- **摄入日期**：2026-10-04

## 摘要

文章从 checkpoint 写入、训练样本随机读取、推理 KVCache 外置三类负载，解释 DeepSeek 自研 3FS 的背景。它介绍管理、元数据、存储和客户端四个组件，以及 FoundationDB 元数据、USRBIO 原生接口、RDMA、CRAQ 链复制和数据放置设计。性能部分区分聚合读吞吐、单节点 checkpoint 写入、KVCache 读取与 GraySort 排序的配置和口径，并与 Lustre、BeeGFS、DAOS 对照。最后讨论社区的缓存后端集成，以及硬件条件、运维资料和生产采用的限制。

## 关键知识点

1. checkpoint 的突发并行写、训练数据的高并发随机读和推理缓存外置，对带宽、容量与故障恢复提出不同要求。
2. 3FS 的元数据服务无状态，使用 FoundationDB 保存文件元数据并提供事务；存储服务管理 SSD 上的 chunk，元数据与数据可分别扩展。
3. FUSE 提供文件接口兼容路径，USRBIO 提供基于共享内存和环形队列的异步数据接口；原生客户端的元数据操作仍由 FUSE 处理。
4. CRAQ 采用 write-all/read-any。官方实现遇到 committed 与 pending 版本并存时，可让客户端等待后重试；显式 relaxed read 的语义不同，不能概括为自动转向链尾读取已提交版本。
5. 原文列出的 6.6 TiB/s 聚合读吞吐依赖 180 个存储节点、500 多个客户端和高速 RDMA 网络；单客户端、单节点、聚合吞吐及 GraySort 结果应分别解读。
6. 原文据公开报道介绍 Mooncake 的实验性 USRBIO 适配器、LMCache 后端及 vLLM/SGLang 的间接接入路径；相关集成和性能描述尚未经过独立验证。

## 涉及的概念与实体

- [[KnowledgeBase/concepts/KV Cache]]：GPU、CPU 与磁盘层之间的缓存放置和换入换出。
- [[KnowledgeBase/entities/vLLM]]：原文讨论经多级缓存组件间接使用 3FS 的推理场景。

## 值得注意

- 正文提供 9 张图示，独立 SVG 可从对应链接打开。
- 原生 IO 路径、CRAQ 读路径、权限、轻量数据集快照和 MIT 许可条件需要结合官方资料理解。
- 性能数字和仓库成熟度反映作者成文时的情况；相关基准尚未独立复现，全部社区集成的当前状态也尚未核实。
- 文章未提供 Kubernetes CSI 驱动、挂载清单或部署步骤，相关 Kubernetes 集成尚未验证。
