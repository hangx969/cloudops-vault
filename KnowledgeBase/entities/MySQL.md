---
title: MySQL
tags:
  - knowledgebase/entity
  - database
date: 2026-04-17
sources:
  - "[[Database/MySQL入门]]"
  - "[[Database/MGR部署MySQL5.7]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署mysql主从高可用]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/helm部署mysql]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/Operator部署mysql集群]]"
  - "[[Python/python-运维开发/python-mysql]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/09-k8s基础-job-cronjob]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控非云原生应用-主机]]"
---

## 简介

MySQL 是最流行的开源关系型数据库，支持主从复制、读写分离、高可用集群等企业级特性，广泛应用于 Web 应用后端。

## 核心功能

- **关系型存储与 SQL**：以库、表、行和列组织数据，支持单表查询、连接查询、子查询与 UNION 合并查询
- **主从复制**：基于 MySQL Replication（默认异步）把 master 数据复制到一个或多个 slave，master 负责写、slave 负责读
- **组复制（MGR）**：加载 `group_replication` 插件组成复制组，支持单主与多主模式，依赖多数派成员才能继续写入，要求使用 InnoDB 存储引擎
- **NDB Cluster**：基于 NDB 存储引擎，由管理节点、数据节点和 SQL 节点组成，数据在多个数据节点间分区和复制
- **备份与监控**：用 mysqldump 做逻辑备份，用 MySQL Exporter 把指标接入 Prometheus

## 使用场景

- 中小型网站与 Web 应用的后端数据库
- 读多写少的业务：主从复制加读写分离，master 故障时可把应用切换到 slave
- 需要自动故障转移的高可用集群：MGR（配合 Nginx + Keepalived 提供统一入口），或在 K8s 中用 NDB Operator 部署 NDB Cluster
- 在 K8s 学习环境中用 StatefulSet 或 Helm Chart 部署（笔记提示生产环境不推荐主从模式和 NFS 存储）

## 相关概念与实体

- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：在 K8s 中以 StatefulSet、Helm Chart 或 Operator 运行 MySQL
- [[KnowledgeBase/concepts/高可用架构|高可用架构]]：主从复制、MGR、NDB Cluster 等高可用方案，以及 MGR、MMM、MHA 的对比
- [[KnowledgeBase/concepts/Operator模式|Operator模式]]：用官方 NDB Operator 部署 MySQL NDB Cluster
- [[KnowledgeBase/entities/Helm|Helm]]：用 bitnami Chart 部署单节点或主从模式
- [[KnowledgeBase/entities/Nginx|Nginx]]：Nginx stream 四层代理加 Keepalived 为 MGR 集群提供访问入口
- [[KnowledgeBase/entities/Prometheus|Prometheus]]：通过 MySQL Exporter 采集 MySQL 指标

## 在本仓库中的覆盖

- `Docker-Kubernetes/k8s-db-middleware/` 目录中涉及 MySQL 主从集群在 Kubernetes 上的部署
- `Database/` 目录中包含 MySQL 相关基础与进阶笔记
- [[KnowledgeBase/sources/misc-domains-batch-summary|杂项领域摘要]]：MySQL 入门与运维管理
- [[Database/MySQL入门|MySQL入门]]：关系型数据库概念、库表操作，单表、连接、子查询与合并查询，以及 LeetCode SQL 示例
- [[Database/MGR部署MySQL5.7|MGR部署MySQL5.7]]：MGR、MMM、MHA 对比，MGR 单主部署、切换多主与节点故障测试，以及 Nginx + Keepalived 访问入口
- [[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署mysql主从高可用|k8s基于yaml部署mysql主从高可用]]：基于 NFS 动态存储和 StatefulSet 部署一主多从复制，并验证主从同步
- [[Docker-Kubernetes/k8s-db-middleware/helm部署mysql|helm部署mysql]]：bitnami Chart 的单节点与主从（replication）模式配置，以及客户端连接方式
- [[Docker-Kubernetes/k8s-db-middleware/Operator部署mysql集群|Operator部署mysql集群]]：NDB Operator 部署 MySQL NDB Cluster（管理、数据、SQL 节点）及集群外访问
- [[Python/python-运维开发/python-mysql|python-mysql]]：MySQL 安装与增删改查，用 mysql-connector-python 操作数据库
- [[Docker-Kubernetes/k8s-basic-resources/09-k8s基础-job-cronjob|k8s基础-job-cronjob]]：用 CronJob 定时执行 mysqldump 全库备份
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控非云原生应用-主机|Prometheus监控非云原生应用-主机]]：为 MySQL 创建监控账号并部署 MySQL Exporter 接入 Prometheus

## 知识空白

- 仓库中尚无 MySQL 性能调优内容（慢查询日志、EXPLAIN 执行计划、索引设计）
- 仓库中尚无事务隔离级别、MVCC 与锁机制的原理说明（MySQL入门 中的 ACID 详解标注为待补充）
- 仓库中尚无 MySQL Router、ProxySQL 等数据库代理或读写分离中间件的实践
