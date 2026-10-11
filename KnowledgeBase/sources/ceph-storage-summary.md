---
title: Ceph 架构、部署与 Kubernetes 集成来源摘要
tags:
  - knowledgebase/source
  - storage/ceph
date: 2026-10-11
aliases:
  - Ceph 存储来源摘要
  - Ceph 原理与运维摘要
---

# Ceph 架构、部署与 Kubernetes 集成来源摘要

## 元信息

- 原始文档：[[Docker-Kubernetes/k8s-storage/开源存储Ceph|Ceph：架构原理、部署与 Kubernetes 集成]]
- 领域：分布式存储、Kubernetes 存储
- 摄入日期：2026-10-11
- 外部来源：Aspirer2004，[Ceph 上篇](https://mp.weixin.qq.com/s/upPqxdnsyFAaaIuFldfStQ)（2026-09-08）、[Ceph 下篇](https://mp.weixin.qq.com/s/TCW5uLLR7K6wxw6O_lN5JQ)（2026-09-09）

## 摘要

文章从 Ceph 的起源、CRUSH 放置和 RADOS 对象层展开，说明 PG、MON/MGR/OSD/MDS/RGW 分工以及 RBD、对象和文件接口。工程部分覆盖硬件、BlueStore、故障恢复、容量、人力、升级、发行版和 AI 负载分工。旧版部署部分保留 ceph-deploy、RBD、CephFS、Provisioner 与 Rook 示例的完整操作和配置，并标明适用版本及已知配置问题。

## 关键知识点

1. CRUSH 根据 PG 标识、拓扑、权重和规则计算 OSD 集合；分散的是数据放置查询，CephFS 目录元数据仍由 MDS 管理。
2. 对象先映射到 PG，再映射到 OSD；现代 Ceph 的 PG autoscaler 和 PG 合并允许调整、减少 PG 数量。
3. size 是期望副本数，min_size 是服务 IO 所需的最少副本数；undersized 本身不等于停止写入。
4. recovery 通常利用操作日志做恢复，backfill 扫描和同步 PG 全部内容，不表示健康副本已经丢失。
5. 三副本和 4+2 纠删码的理论空间开销分别约为 3 倍、1.5 倍，实际选择还取决于写入大小、延迟和恢复成本。
6. 网络可以按需求分离，容量需要检查各 OSD；生产规划应考虑业务与恢复流量竞争。
7. cephadm 和非 cephadm 的升级顺序不同，跨版本路径及维护日期应查目标发行说明。
8. Kubernetes 1.31 已移除 in-tree RBD / CephFS；当前应使用 Ceph CSI，旧示例不能当作当前生产配置。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Ceph]]
- [[KnowledgeBase/concepts/分布式存储]]
- [[KnowledgeBase/concepts/StorageClass]]
- [[KnowledgeBase/concepts/高可用架构]]
- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/entities/Prometheus]]
- [[KnowledgeBase/entities/Grafana]]

## 值得注意

- 原笔记 52 个代码块完整保留；18 张架构和运维原图已上传图床。原图中 PG 状态、恢复区别、流量及升级的简化表述以正文核对说明为准。
- 网络速率、规模门槛、人力和恢复时长是原作者经验，不是官方硬性要求。
- 正文中的版本维护列表核对日期为 2026-10-11；没有执行 Ceph 或 Kubernetes 部署测试。
