---
title: 分布式存储全景来源摘要
tags:
  - knowledgebase/source
  - storage/distributed
date: 2026-10-11
aliases:
  - 开源存储发展路线摘要
---

# 分布式存储全景来源摘要

## 元信息

- 原始文档：[[Docker-Kubernetes/k8s-storage/分布式存储全景-架构与发展路线|分布式存储全景：架构、发展路线与选型]]
- 领域：分布式存储、Kubernetes 存储
- 摄入日期：2026-10-11
- 外部来源：Aspirer2004，2026-08-29，[开源存储列传 00](https://mp.weixin.qq.com/s/wyBSMexbZolx71soYnXcLA)

## 摘要

文章用数据放置、冗余、一致性和故障恢复四个问题解释分布式存储，再比较文件、对象和块接口。发展路线覆盖 HPC、大数据、统一扩展和云原生，并讨论互联网、容器化、AI 三类负载推动的变化。保留原系列 00—28 的完整目录、按阅读目标划分的路径及讨论边界。

## 关键知识点

1. 横向扩展把单机容量、吞吐和可靠性限制转化为数据分布与协调问题。
2. 文件、对象和块是对外接口差异；Ceph 共用 RADOS 底座，JuiceFS 则用对象存储承载文件数据。
3. HPC 强调并行 IO，大数据强调海量批处理，统一存储强调接口复用，云原生强调声明式卷生命周期。
4. AI 负载至少需要区分 checkpoint 写入、训练数据读取和 KV Cache 分层。
5. 选型应把接口、负载、故障域、社区维护和支持服务放在一起评估，不能只比较容量或吞吐表。
6. Alluxio 的研究、开源和更名是不同节点：2012 年研究起步，2013 年开源，2016 年更名与 1.0 发布。

## 涉及的概念与实体

- [[KnowledgeBase/concepts/分布式存储]]
- [[KnowledgeBase/concepts/StorageClass]]
- [[KnowledgeBase/concepts/高可用架构]]
- [[KnowledgeBase/entities/Ceph]]
- [[KnowledgeBase/entities/Kubernetes]]

## 值得注意

- 时间线和原系列目录用于理解发展背景，不表示所有篇目已收录，也不表示表中的容量量级是接口硬限制。
- 8 张原图已上传图床。Alluxio 更名时间按创始人资料核对，正文注明了与原文的差别。
