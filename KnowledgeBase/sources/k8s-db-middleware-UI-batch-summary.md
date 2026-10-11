---
title: K8s数据库中间件与UI工具 来源批量摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/k8s-db-middleware
  - docker-kubernetes/k8s-UI-tools
date: 2026-10-11
sources:
  - "[[Docker-Kubernetes/k8s-db-middleware/Operator部署Redis集群]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/Operator部署mysql集群]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/helm部署mysql]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/helm部署postgreSQL]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/helm部署strimzi-kafka]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署MongoDB集群]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署httpd服务]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署mysql主从高可用]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署redis集群]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/k8s部署springcloud电商项目]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/helm部署rabbitmq-ha]]"
  - "[[Docker-Kubernetes/k8s-UI-tools/k8s-API检查工具kubent]]"
  - "[[Docker-Kubernetes/k8s-UI-tools/k8s-小工具集合]]"
  - "[[Docker-Kubernetes/k8s-UI-tools/k8s部署-Dashboard-UI]]"
  - "[[Docker-Kubernetes/k8s-UI-tools/k8s部署可视化ui界面kuboard]]"
  - "[[Docker-Kubernetes/k8s-UI-tools/kubectl-UI工具Lens]]"
  - "[[Docker-Kubernetes/k8s-UI-tools/kubectl-可视化插件k9s-stern]]"
  - "[[kuebctl-插件krew]]"
  - "[[Docker-Kubernetes/k8s-UI-tools/rancher(v2.6.4)管理k8s集群]]"
aliases:
  - k8s-db-middleware-UI 批量摘要
  - K8s 中间件与 UI
---

## 元信息

- **原始目录**: `Docker-Kubernetes/k8s-db-middleware/`、`Docker-Kubernetes/k8s-UI-tools/`
- **文档数量**: 19 篇（数据库中间件 11 篇 + UI 工具 8 篇）
- **领域**: Kubernetes 上部署数据库/中间件服务、集群可视化与管理工具
- **摄入日期**: 2026-04-17

## 摘要

本批次文档涵盖两大主题：一是在 Kubernetes 中部署各类数据库（MySQL、PostgreSQL、Redis、MongoDB、Kafka）和中间件服务的实战笔记，涉及原生 YAML、Helm Chart 以及 Operator 三种主流部署方式；二是 Kubernetes 集群的可视化管理工具链，包括 Dashboard、Kuboard、Lens、k9s、Rancher 等多种方案。文档以操作步骤为主，辅以架构说明和生产环境注意事项，是一套完整的 K8s 有状态服务部署与集群管理参考资料。

## 关键知识点

1. Redis Cluster 最少需要 6 个实例（3 主 3 从），通过 16384 个哈希槽实现数据分片；哨兵模式提供监控、通知和自动故障转移。
2. MySQL NDB Cluster 由管理节点、数据节点、SQL 节点三种角色组成，通过 NdbCluster CRD 声明，`redundancyLevel` 控制数据副本数，生产环境建议 >= 2。
3. Bitnami PostgreSQL HA 由 Pgpool（流量接入与读写分离）、repmgr（主从自动切换）和 witness（防脑裂）组成，偶数个节点必须配置 witness；Bitnami 的 MySQL、PostgreSQL Chart 均依赖 `bitnami/common` 子 Chart。
4. Strimzi 部署 Kafka 需先部署 Cluster Operator，再创建 Kafka、Topic、User 等 CRD 资源；Mirror Maker 用于跨集群数据复制和灾备。
5. MongoDB 高可用有主从、副本集、分片三种方案，副本集实现自动故障转移，分片实现水平扩展。
6. MySQL 主从 YAML 实践中，NFS Provisioner 由 ServiceAccount、ClusterRoleBinding、Deployment 组成，配合 StorageClass 动态供给 PV。
7. Dashboard 安装后需将 Service 类型改为 NodePort 并通过 Token 登录；Kuboard v3 以 Docker 容器部署、不依赖 K8s 集群，通过 Service Account 接入集群；Lens 无需在集群中安装组件，内置 Prometheus 集成提供资源可视化。
8. k9s 采用 Vim 风格操作（`:` 输入资源类型，`/` 输入过滤器）；krew 是 kubectl 插件管理工具，rolesum 插件用于可视化查看 RBAC Role 绑定；Rancher 是底层基于 K8s 的企业级多集群管理平台。

## 各文档摘要

### [[Docker-Kubernetes/k8s-db-middleware/Operator部署Redis集群|Operator部署Redis集群]]

- **核心内容**: 使用 OT-Redis-Operator 在 K8s 上部署 Redis 集群模式（3主3从），介绍了 Helm 和 YAML 两种安装方式。
- **关键知识点**:
  - 推荐 Cluster 模式部署 Redis，不推荐主从 replication 模式（在 K8s 中主从切换不及时）
  - Redis 集群最少 6 个实例（3 主 3 从）
  - Operator 安装后会注册 RedisCluster CRD 资源
  - 通过简单的 YAML 即可声明式创建集群

### [[Docker-Kubernetes/k8s-db-middleware/Operator部署mysql集群|Operator部署MySQL集群]]

- **核心内容**: 使用 MySQL 官方维护的 NDB Operator 部署 MySQL NDB Cluster 分布式数据库集群。
- **关键知识点**:
  - NDB Cluster 由管理节点、数据节点、SQL 节点三种角色组成
  - 支持 Helm、YAML、克隆仓库三种安装方式
  - `redundancyLevel` 控制数据副本数量，生产环境建议 >= 2
  - 使用 NdbCluster CRD 资源声明集群

### [[Docker-Kubernetes/k8s-db-middleware/helm部署mysql|Helm部署MySQL]]

- **核心内容**: 使用 Bitnami Helm Chart 部署单节点 MySQL（standalone 模式），通过 NodePort 暴露服务。
- **关键知识点**:
  - 使用 `bitnami/mysql` Chart，支持 standalone 和 replication 架构
  - 生产环境不推荐 NFS 作为存储后端
  - 需要将 `charts/bitnami/common` 作为子 Chart 放入 `mysql/charts/` 目录

### [[Docker-Kubernetes/k8s-db-middleware/helm部署postgreSQL|Helm部署PostgreSQL]]

- **核心内容**: 使用 Bitnami Helm Chart 部署 PostgreSQL HA 高可用集群，包含 Pgpool、repmgr 和 witness 组件。
- **关键知识点**:
  - HA 模式包含 Pgpool（流量接入与读写分离）、repmgr（主从自动切换）、witness（防脑裂）
  - 偶数个节点必须配置 witness
  - 同样需要 bitnami/common 子 Chart

### [[Docker-Kubernetes/k8s-db-middleware/helm部署strimzi-kafka|Helm部署Strimzi Kafka]]

- **核心内容**: 使用 Strimzi Operator 部署生产级 Kafka 集群，并介绍 Kafka UI 和 Mirror Maker 数据复制工具。
- **关键知识点**:
  - Strimzi 是最主流的 Kafka on K8s Operator 方案
  - 先部署 Cluster Operator，再创建 Kafka、Topic、User 等 CRD 资源
  - Kafka 核心概念：Broker、Topic、Partition、Producer、Consumer、Offset
  - Mirror Maker 用于跨集群数据复制和灾备

### [[Docker-Kubernetes/k8s-db-middleware/helm部署rabbitmq-ha|Helm部署RabbitMQ HA]]

- **核心内容**: 使用 aliyun/rabbitmq-ha Helm Chart 在 K8s 上部署 RabbitMQ 高可用集群（StatefulSet 模式），包含 Chart 配置修改和 API 版本兼容性修复。
- **关键知识点**:
  - 使用 `aliyun/rabbitmq-ha` Chart（版本 1.0.0），基于 rabbitmq:3.7-alpine 镜像
  - 旧版 Chart 需手动修改 API 版本：`rbac.authorization.k8s.io/v1beta1` → `v1`、`apps/v1beta1` → `apps/v1`
  - StatefulSet 需补充 `spec.selector.matchLabels` 字段
  - 通过 NodePort 暴露管理界面，默认关闭持久化存储
  - Chart 版本较旧，生产环境建议评估 Bitnami 维护的 `bitnami/rabbitmq`

### [[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署MongoDB集群|K8s基于YAML部署MongoDB集群]]

- **核心内容**: 通过原生 YAML 文件在 K8s 上部署 MongoDB 集群，涉及 NFS 存储和 ConfigMap 配置。
- **关键知识点**:
  - MongoDB 三种高可用方案：主从、副本集、分片
  - 副本集实现自动故障转移，分片实现水平扩展
  - 使用 NFS 作为持久化存储，手动创建数据目录

### [[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署httpd服务|K8s基于YAML部署httpd服务]]

- **核心内容**: 从 Dockerfile 构建 Apache httpd 镜像，并在 K8s 上通过 YAML 部署 Pod 和 Service。
- **关键知识点**:
  - 从源码编译 httpd 并打包为 Docker 镜像
  - 使用 `docker save/load` 在节点间分发镜像
  - 基础的 Pod YAML 编写示例

### [[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署mysql主从高可用|K8s基于YAML部署MySQL主从高可用]]

- **核心内容**: 使用原生 YAML 部署 MySQL 主从高可用集群，包含 NFS Provisioner 的完整搭建流程。
- **关键知识点**:
  - 完整的 NFS Provisioner 搭建：ServiceAccount、ClusterRoleBinding、Deployment
  - 生产环境中 MySQL 对性能要求高时不建议部署在 K8s 中
  - StorageClass 动态供给 PV

### [[Docker-Kubernetes/k8s-db-middleware/k8s基于yaml部署redis集群|K8s基于YAML部署Redis集群]]

- **核心内容**: 详解 Redis 高可用架构（主从、哨兵、Cluster 模式），并通过原生 YAML 在 K8s 上部署 Redis 集群。
- **关键知识点**:
  - Redis 主从复制支持全同步和部分同步
  - 哨兵模式提供监控、通知和自动故障转移
  - Redis Cluster 通过 16384 个哈希槽实现数据分片
  - 一致性模型：单节点强一致，主从复制弱一致

### [[Docker-Kubernetes/k8s-db-middleware/k8s部署springcloud电商项目|K8s部署SpringCloud电商项目]]

- **核心内容**: 将 SpringCloud 电商项目部署到 K8s，涵盖 Harbor 搭建、Docker 环境准备、系统初始化等全流程。
- **关键知识点**:
  - 完整的 CentOS 系统初始化步骤（防火墙、selinux、时间同步、内核参数）
  - Harbor 镜像仓库搭建
  - Docker 安装与配置

### [[Docker-Kubernetes/k8s-UI-tools/k8s-API检查工具kubent|K8s API检查工具kubent]]

- **核心内容**: kube-no-trouble (kubent) 工具简介，用于检查 K8s 集群中已废弃 API 版本。
- **关键知识点**:
  - 用于 K8s 升级前检查废弃 API 的兼容性工具

### [[Docker-Kubernetes/k8s-UI-tools/k8s-小工具集合|K8s小工具集合]]

- **核心内容**: K8s 相关小工具的索引页面，指向 Lens 等工具文档。
- **关键知识点**:
  - 作为工具索引入口

### [[Docker-Kubernetes/k8s-UI-tools/k8s部署-Dashboard-UI|K8s部署Dashboard UI]]

- **核心内容**: 部署 Kubernetes Dashboard 并配置 Token 登录方式，包含常见问题的解决。
- **关键知识点**:
  - 安装后需将 Service 类型改为 NodePort 以便外部访问
  - 浏览器安全限制可通过键入 `thisisunsafe` 跳过
  - K8s 1.24+ 版本需手动创建 SA 和 Secret 绑定

### [[Docker-Kubernetes/k8s-UI-tools/k8s部署可视化ui界面kuboard|K8s部署Kuboard]]

- **核心内容**: 使用 Docker 部署 Kuboard v3 可视化管理界面，并添加 K8s 集群。
- **关键知识点**:
  - Kuboard 通过 Docker 容器方式部署，不依赖 K8s 集群
  - 支持通过 Service Account 认证方式接入集群
  - 提供 Web 界面创建 Deployment 和 Service

### [[Docker-Kubernetes/k8s-UI-tools/kubectl-UI工具Lens|kubectl UI工具Lens]]

- **核心内容**: Lens IDE 功能介绍，包括内置可视化、智能终端、Helm 管理、插件系统等。
- **关键知识点**:
  - 支持 MacOS/Windows/Linux，无需在集群中安装组件
  - 内置 Prometheus 集成，提供 CPU/内存/网络/磁盘可视化
  - 插件：lens-certificate-info（证书查看）、lens-debug-tools（Debug Sidecar）、kube-resource-map（资源拓扑图）
  - 智能终端自动同步 kubectl 版本

### [[Docker-Kubernetes/k8s-UI-tools/kubectl-可视化插件k9s-stern|kubectl可视化插件k9s和stern]]

- **核心内容**: k9s 终端 UI 工具的安装、使用和快捷键说明。
- **关键知识点**:
  - Vim 风格操作，`:` 输入资源类型，`/` 输入过滤器
  - 支持上下文切换、标签过滤、正则过滤、模糊查找
  - 多种安装方式：webi、deb 包、snap

### [[kuebctl-插件krew|kubectl 插件指南：Krew 与 RBAC 排查]]

- **核心内容**：Krew 安装、内网与离线分发、13 个常用插件，以及 whoami/rolesum/who-can/auth can-i 的权限排查分工。
- **关键知识点**：
  - PATH 需要手动配置；插件平台支持与客户端 API 兼容性分别核对
  - rolesum 默认查询 ServiceAccount，也可查询 User/Group；who-can 静态分析需要读取角色和绑定
  - 资源清单快照不能代替完整灾备；outdated 检查镜像，废弃 API 检查使用相应工具
  - Windows 可参考现有 Scoop 笔记；插件参数、资源统计和版本限制见正文
- **独立摘要**：[[KnowledgeBase/sources/kubectl-krew-plugins-summary|kubectl 插件指南 来源摘要]]。

### [[Docker-Kubernetes/k8s-UI-tools/rancher(v2.6.4)管理k8s集群|Rancher管理K8s集群]]

- **核心内容**: Rancher v2.6.4 的介绍、部署和配置，用于企业级多集群 Kubernetes 管理。
- **关键知识点**:
  - Rancher 是企业级多集群 K8s 管理平台，底层基于 K8s
  - 提供容器管理、多云支持、高可用、安全性、应用商店等功能
  - 部署包含完整的系统初始化和 Docker 安装流程

## 涉及的概念与实体

- [[KnowledgeBase/entities/Redis]] / [[KnowledgeBase/entities/MySQL]] / [[KnowledgeBase/entities/PostgreSQL]] / [[KnowledgeBase/entities/MongoDB]] / [[KnowledgeBase/entities/Kafka]]
- [[KnowledgeBase/entities/Helm]] / [[KnowledgeBase/entities/Operator]]
- [[KnowledgeBase/entities/Strimzi]] / [[KnowledgeBase/entities/Bitnami]]
- [[KnowledgeBase/entities/Rancher]] / [[KnowledgeBase/entities/Lens]] / [[KnowledgeBase/entities/k9s]] / [[KnowledgeBase/entities/Kuboard]]
- [[KnowledgeBase/entities/Harbor]]
- [[KnowledgeBase/concepts/StatefulSet]] / [[KnowledgeBase/concepts/CRD]] / [[KnowledgeBase/concepts/Operator模式]]
- [[KnowledgeBase/concepts/NFS-Provisioner]] / [[KnowledgeBase/concepts/StorageClass]]
- [[KnowledgeBase/concepts/高可用架构]] / [[KnowledgeBase/concepts/主从复制]] / [[KnowledgeBase/concepts/数据分片]]
- [[KnowledgeBase/concepts/RBAC]] / [[KnowledgeBase/concepts/NodePort]]

## 交叉主题发现

1. **三种部署范式对比**: 原生 YAML（学习理解底层）、Helm Chart（标准化配置管理）、Operator（自动化运维），三者在复杂度和自动化程度上递进，文档覆盖了同一数据库（如 MySQL、Redis）的不同部署方式，可进行横向对比。
2. **存储后端选择**: 多篇文档反复强调生产环境不推荐 NFS，建议使用 Ceph 等分布式存储，这是 K8s 有状态服务部署的核心考量。
3. **Helm Chart 依赖管理**: Bitnami 系列 Chart（MySQL、PostgreSQL、Tomcat）都需要 `common` 子 Chart，这是 Helm 依赖管理的通用模式。
4. **可视化工具互补**: Dashboard（Web 原生）、Kuboard（国产增强）、Lens（桌面 IDE）、k9s（终端 TUI）、Rancher（多集群管理平台）各有定位，形成从轻量到重量级的工具链。
5. **Operator 生态**: Redis Operator (OT)、NDB Operator (MySQL 官方)、Strimzi Operator (Kafka) 均采用 CRD + Controller 模式，体现了 K8s 声明式 API 扩展的统一范式。

## 值得注意

- **NFS 仅适合学习环境**: Helm 部署 MySQL 文档指出生产环境不推荐 NFS（单点无高可用、性能也有问题），MySQL 主从文档也提示性能要求高的 MySQL 不建议部署在 K8s 中；而 MongoDB、MySQL 主从等 YAML 实践均以 NFS 作为持久化存储，引用其存储配置时需注意这一前提。
- **Redis 部署模式取舍**: Operator 文档推荐 Cluster 模式，不推荐主从 replication 模式（在 K8s 中主从切换不及时）；主从复制属于弱一致模型。
- **旧版 Chart 与 API 兼容**: aliyun/rabbitmq-ha Chart（1.0.0，基于 rabbitmq:3.7-alpine）需手动将 `rbac.authorization.k8s.io/v1beta1` 改为 `v1`、`apps/v1beta1` 改为 `apps/v1`，并为 StatefulSet 补充 `spec.selector.matchLabels`，生产环境建议评估 Bitnami 维护的 `bitnami/rabbitmq`；K8s 1.24+ 部署 Dashboard 需手动创建 SA 和 Secret 绑定；集群升级前可用 kubent 检查废弃 API。
