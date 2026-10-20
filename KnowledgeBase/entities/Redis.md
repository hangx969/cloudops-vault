---
title: Redis
tags:
  - knowledgebase/entity
  - database
date: 2026-04-17
sources:
  - "[[Database/源码安装redis-6.2.6-centos7]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署redis集群]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/Operator部署Redis集群]]"
  - "[[Docker-Kubernetes/docker/docker部署UI工具portainer-部署redis-sentinel]]"
  - "[[Docker-Kubernetes/kubeblocks/kubeblocks部署高可用harbor集群]]"
  - "[[AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/Kubernetes原生部署Prometheus与Grafana]]"
  - "[[7.5-RAG-Agent架构设计面试题预测]]"
---

## 简介

Redis 是高性能键值数据库，常用于缓存、消息队列、分布式锁等场景。支持多种数据结构，并提供 Sentinel 高可用和 Cluster 集群模式。

## 核心功能

- **内存键值存储**：支持字符串、List、Sorted Set 等数据结构，以 SET、GET、DEL、RPUSH 等简单命令读写，适合高并发访问
- **主从复制**：一主多从复制数据，支持读写分离与故障迁移
- **Sentinel 高可用**：哨兵监控主节点，多个哨兵确认主节点失效后自动故障转移
- **Cluster 分片**：通过分片和复制把数据分布到多个节点，节点故障时自动恢复
- **持久化**：支持 RDB 快照（SAVE、BGSAVE）和 AOF 日志（多种写入策略、AOF 重写与文件修复）

## 使用场景

- 高并发缓存：电商商品类目、推荐系统、秒杀抢购
- 排行榜与消息列表：用 Sorted Set 实现直播弹幕、游戏排行榜，用 List 缓存最新评论
- 平台组件的缓存与限流：作为 Harbor 的外部 Redis、LiteLLM 的缓存与路由限流
- 缓存问题治理：用缓存空值、TTL 随机化和分布式锁应对缓存穿透、雪崩与击穿
- 在 K8s 中用 StatefulSet、Redis Operator 或 KubeBlocks 运行高可用 Redis（Operator 笔记推荐 Cluster 模式，不推荐主从模式）

## 相关概念与实体

- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：在 K8s 中以 StatefulSet、Redis Operator 或 KubeBlocks 部署 Redis
- [[KnowledgeBase/entities/Docker|Docker]]：以容器方式部署 Redis 主从与哨兵
- [[KnowledgeBase/concepts/高可用架构|高可用架构]]：主从复制、Sentinel、Cluster 三种高可用模式
- [[KnowledgeBase/concepts/Operator模式|Operator模式]]：Redis Operator 通过 RedisCluster 资源部署集群
- [[KnowledgeBase/entities/Harbor|Harbor]]：KubeBlocks 创建的 Redis 集群作为 Harbor 外部 Redis
- [[KnowledgeBase/entities/Prometheus|Prometheus]]：通过 redis_exporter 采集 Redis 指标

## 在本仓库中的覆盖

- `Docker-Kubernetes/k8s-db-middleware/` 目录中涉及 Redis Sentinel 与 Cluster 在 Kubernetes 上的部署
- `Docker-Kubernetes/docker/` 目录中包含 Redis 容器化部署相关笔记
- [[KnowledgeBase/sources/misc-domains-batch-summary|杂项领域摘要]]：Redis 数据库入门与集群部署
- [[Database/源码安装redis-6.2.6-centos7|源码安装redis-6.2.6-centos7]]：使用场景，源码安装单节点，主从复制与故障迁移测试，Sentinel 与 Cluster 部署，RDB/AOF 持久化
- [[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署redis集群|k8s基于yaml部署redis集群]]：主从、哨兵、Cluster 模式对比，基于 NFS PV 和 StatefulSet 部署并用 redis-trib 初始化集群，测试主从切换
- [[Docker-Kubernetes/k8s-db-middleware/Operator部署Redis集群|Operator部署Redis集群]]：用 Helm 安装 Redis Operator 部署 Cluster 模式集群，配置密码认证并测试集群内外连接
- [[Docker-Kubernetes/docker/docker部署UI工具portainer-部署redis-sentinel|docker部署UI工具portainer-部署redis-sentinel]]：用 Compose 部署 Redis 主从与哨兵，并测试高可用
- [[Docker-Kubernetes/kubeblocks/kubeblocks部署高可用harbor集群|kubeblocks部署高可用harbor集群]]：KubeBlocks 创建 Sentinel 主备 Redis 集群，作为 Harbor 的外部 Redis
- [[AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM|基于K8s部署vLLM和LiteLLM]]：Redis Sentinel 作为 LiteLLM 缓存，单节点 Redis 用于路由限流
- [[Docker-Kubernetes/k8s-monitoring-logging/Kubernetes原生部署Prometheus与Grafana|Kubernetes原生部署Prometheus与Grafana]]：Redis 与 redis_exporter 在同一 Pod 部署，由 Prometheus 采集指标
- [[7.5-RAG-Agent架构设计面试题预测|RAG-Agent架构设计面试题预测]]：用缓存空值、TTL 随机化、Redisson 分布式锁应对缓存穿透、雪崩与击穿

## 知识空白

- 仓库中尚无 Redis 数据结构与常用命令的系统讲解
- 仓库中尚无 Redis 内存上限与淘汰策略（maxmemory、maxmemory-policy）的配置说明
- 仓库中尚无 Redis 慢查询（slowlog）与大 Key 排查等性能诊断实践
