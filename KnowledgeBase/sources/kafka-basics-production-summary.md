---
title: Kafka 入门、生产配置与 Kubernetes 排障来源摘要
tags:
  - knowledgebase/source
  - messaging/kafka
date: 2026-10-20
sources:
  - "[[Middlewares/Kafka]]"
aliases:
  - Kafka 生产运维来源摘要
---

# Kafka 入门、生产配置与 Kubernetes 排障

## 元信息

- **原始文档**：[[Middlewares/Kafka]]
- **领域**：消息系统、Kafka、Kubernetes 有状态服务
- **摄入日期**：2026-10-20
- **资料组成**：现有 Kafka 入门笔记、WAKEUP 技术的 ZooKeeper 迁移故障案例，以及从 [[Docker-Kubernetes/k8s-db-middleware/helm部署strimzi-kafka]] 迁出的副本同步与生产配置章节；关键边界按正文所列官方资料核对。

## 摘要

文档按入门概念、副本可靠性、生产配置、Kubernetes 迁移排障和上线审查组织。介绍 Topic、Partition、Consumer Group、Offset、重复消费与重试，并区分 ZooKeeper 与 KRaft。生产部分解释副本数、ISR、minISR 与 Producer 确认之间的关系，保留配置、Java Producer、Topic 命令和监控示例。排障部分覆盖临时卷生命周期、成员身份、独立持久卷、磁盘 I/O、CIDR、DNS 和 Listener，并补齐 ZooKeeper 示例中的成员映射与服务配置。

## 关键知识点

1. 普通消费组的并行度受分区分配约束，消费者数量与 Broker 副本数没有一一对应关系。
2. 成功处理后未成功提交 Offset、重平衡或主动重放都可能导致重复消费；Producer 幂等性不能替代消费端业务幂等。
3. 三副本、minISR 为 2、Producer 使用 `acks=all` 是常见基线；`all` 等待当前 ISR，minISR 是确认下限，不是固定等待数量。
4. 副本不足、低于 minISR 和 Consumer Lag 需要分别监控；Prometheus 名称取决于实际 Exporter 和配置采集链路。
5. Kafka 2.8 的 KRaft 是早期模式，3.3 起对新集群达到生产可用阶段，4.0 起移除了 ZooKeeper 模式。
6. `emptyDir` 在同一 Pod 内的容器重启期间保留，Pod 删除或重建后丢失；PVC 是否真实挂载到状态目录需要另外核对。
7. ZooKeeper 的 `myid` 必须对应 `server.N`；稳定 DNS、每成员持久卷及底层 I/O 隔离需要同时满足。
8. StatefulSet 的 PVC 保留策略控制何时删除 PVC，PV 回收策略控制 PVC 删除后的存储处理；`Session Expired` 也不等于服务进程必然重启。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kafka]]
- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/entities/Prometheus]]
- [[KnowledgeBase/concepts/高可用架构]]
- [[KnowledgeBase/concepts/StorageClass]]
- [[KnowledgeBase/concepts/Operator模式]]

## 值得注意

- 原文事故缺少完整 ISR、选主、消费组分配和数据核对证据，正文将原记录与可推导的故障模式分开说明，未将其当作独立验证的事故结论。
- 原示意图经 PicGo GitHub Plus 上传并核对文件哈希；图中 minISR 的部分标记保留了历史错误，正文已明确阅读边界。
- ZooKeeper 3.8 清单展示持久化与身份配置；生产还需补齐资源、探针、分布、访问控制和恢复方案。本次未执行集群部署、生产消费或故障切换测试。
