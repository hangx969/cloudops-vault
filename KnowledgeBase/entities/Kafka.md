---
title: Kafka
tags:
  - knowledgebase/entity
  - messaging
date: 2026-10-20
sources:
  - "[[Middlewares/Kafka]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/helm部署strimzi-kafka]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/二进制部署efk+logstash+kafka日志收集平台]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/k8s监控EFK+logstash+kafka]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/基于helm+operator部署ECK日志收集平台]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/k8s日志管理-采集方案与审计日志]]"
  - "[[Docker-Kubernetes/k8s-scaling/k8s-基于KEDA的弹性能力]]"
  - "[[2.1-RAG-Agent环境搭建指南（新人必看）Java 17、MySQL、Elasticsearch、Redis、MinIO、Kafka]]"
aliases:
  - Apache Kafka
---

# Kafka

## 简介

Apache Kafka 是分布式消息队列与事件流平台，常用于日志收集、事件驱动架构和流式数据处理，具备高吞吐、持久化和水平扩展能力。

## 核心功能

- **发布订阅与消费位置**：Producer 向 Topic 发布消息，普通消费组按分区分配消费；当前位置与已提交 Offset 不同，故障恢复和重放都可能再次处理记录
- **重试与幂等**：Producer 幂等性限制会话内重试产生的重复写入，消费端仍需处理重复执行和业务幂等
- **分区与副本**：Topic 拆分为多个 Partition 分布到多个 Broker 以提升并发和扩展性，Partition 以 Leader/Follower 多副本提高可用性
- **元数据管理**：旧集群可能依赖 ZooKeeper；KRaft 通过 Controller 仲裁管理元数据，Kafka 4.0 起移除了 ZooKeeper 模式。元数据仲裁与业务分区复制需分别检查
- **可靠性参数**：分区副本数、`min.insync.replicas`、Producer `acks` 和选主策略共同影响可靠性；`acks=all` 等待当前 ISR，并受 minISR 下限约束，三副本不能单独证明数据已同步
- **集群间复制**：MirrorMaker 从源集群消费并写入目标集群，用于数据备份、迁移和灾备

## 使用场景

- 日志采集链路的缓冲层：Filebeat/Fluentd → Kafka → Logstash → Elasticsearch，日志量大时削峰，避免日志延迟
- 在 Kubernetes 上通过 Strimzi Operator 运行 Kafka 集群，配合 Kafka UI 管理
- 事件驱动扩缩容：KEDA 以 consumer group lag 作为信号扩缩消费者
- 系统间数据交互：数据量大或一方不稳定时，用消息队列替代直接 API 调用

## 相关概念与实体

- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：通过 Strimzi Operator 或 bitnami Chart 在 K8s 上部署 Kafka
- [[KnowledgeBase/concepts/Observability|Observability]]：作为日志采集链路的缓冲层，并通过 JMX Prometheus Exporter 暴露指标
- [[KnowledgeBase/concepts/日志系统|日志系统]]：EFK/ELK 架构中位于采集端与 Logstash 之间的缓冲
- [[KnowledgeBase/concepts/Operator模式|Operator模式]]：Strimzi 以 Kafka、KafkaNodePool、KafkaTopic、KafkaUser 等 CRD 管理集群
- [[KnowledgeBase/entities/Prometheus|Prometheus]]：采集副本与消费指标，分别监控配置偏差、ISR 不足和消费积压；指标名需匹配实际 Exporter
- [[KnowledgeBase/concepts/高可用架构|高可用架构]]：副本确认、故障域分布、持久卷与元数据仲裁需要同时满足
- [[KnowledgeBase/entities/Helm|Helm]]：用 Helm 部署 Strimzi Operator 和 bitnami Kafka Chart

## 在本仓库中的覆盖

- `Docker-Kubernetes/k8s-db-middleware/` 目录中涉及 Kafka 在 Kubernetes 上的部署
- `Docker-Kubernetes/k8s-monitoring-logging/` 目录中作为日志采集管道的组成部分被提及
- [[KnowledgeBase/sources/misc-domains-batch-summary|杂项领域摘要]]：Kafka/RabbitMQ/RocketMQ 中间件概览
- [[Middlewares/Kafka|Kafka：入门、生产配置与 Kubernetes 排障]]：消费组、Offset、重复消费与重试，副本确认及生产基线，ZooKeeper 的存储、身份、I/O、CIDR 和 Listener 排障
- [[KnowledgeBase/sources/kafka-basics-production-summary|Kafka 生产运维来源摘要]]：整合材料、核对结论与未实测边界
- [[Docker-Kubernetes/k8s-db-middleware/helm部署strimzi-kafka|Helm 部署 Strimzi Kafka]]：Strimzi Operator、KRaft 集群与 Broker/Controller NodePool、TLS 与 ACL、指标配置、Kafka UI 及 MirrorMaker 工具介绍；通用生产运维已移到 Kafka 主文
- [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署efk+logstash+kafka日志收集平台|二进制部署efk+logstash+kafka日志收集平台]]：基于 ZooKeeper 部署 Kafka 单节点与三节点集群，用命令行测试 Topic 生产和消费，作为日志缓冲层
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控EFK+logstash+kafka|k8s监控EFK+logstash+kafka]]：Fluentd 通过 kafka 插件写入 Kafka，Logstash 消费后写入 Elasticsearch
- [[Docker-Kubernetes/k8s-monitoring-logging/基于helm+operator部署ECK日志收集平台|基于helm+operator部署ECK日志收集平台]]：用 bitnami Chart 部署 ZooKeeper 与 Kafka，作为 Filebeat 与 Logstash 之间的缓冲
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s日志管理-采集方案与审计日志|K8s 日志：基础机制、六种采集方案与审计日志]]：大规模集群日志架构中以 Kafka 作为削峰缓冲层
- [[Docker-Kubernetes/k8s-scaling/k8s-基于KEDA的弹性能力|KEDA：事件驱动扩缩容与 KServe 实战]]：以 consumer group lag 为信号的 Kafka ScaledObject 示例
- [[2.1-RAG-Agent环境搭建指南（新人必看）Java 17、MySQL、Elasticsearch、Redis、MinIO、Kafka|RAG-Agent环境搭建指南]]：KRaft 模式下生成集群 ID、格式化存储目录并启动单节点 Kafka

## 知识空白

- 仓库中尚无 Kafka Connect、Kafka Streams 等数据集成与流处理组件的实践，现有笔记只在 Strimzi CRD 列表或面试题中提及
- 仓库中尚无分区重分配与扩容后数据均衡（如 KafkaRebalance）的操作
- 已有普通消费组、重复消费和重试的入门说明，仍缺少完整的重试 Topic / 死信、事务消费及恢复演练实操
