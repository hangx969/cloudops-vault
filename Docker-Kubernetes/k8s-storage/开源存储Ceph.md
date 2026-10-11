---
title: Ceph：架构原理、部署与 Kubernetes 集成
tags:
  - kubernetes
  - storage/ceph
  - storage/distributed
date: 2026-10-11
source:
  - https://mp.weixin.qq.com/s/upPqxdnsyFAaaIuFldfStQ
  - https://mp.weixin.qq.com/s/TCW5uLLR7K6wxw6O_lN5JQ
aliases:
  - K8s Ceph部署
  - K8s Ceph部署与集成
  - Ceph 分布式存储
  - 开源存储列传第 07 篇 — Ceph（上），一套集群三种存储
  - 开源存储列传第 08 篇 — Ceph（下），算算工程与运维这笔账
---

# Ceph：架构原理、部署与 Kubernetes 集成

Ceph 在同一套集群中提供 RBD 块设备、RGW 对象接口和 CephFS 文件系统。三者共享 RADOS 对象存储底座，通过 CRUSH 计算数据放置位置，由 PG 组织复制、恢复和一致性状态。

这套设计适合需要统一存储能力的私有云与大规模平台，也把硬件规划、故障处理和升级的复杂度集中到运维团队。下面先说明架构和工程取舍，再保留旧版部署及 Kubernetes 接入流程。网络、规模、人力和恢复时间等经验值用于参考，不是官方配置标准。

分布式存储的接口与发展路线可先看 [[Docker-Kubernetes/k8s-storage/分布式存储全景-架构与发展路线|分布式存储全景]]。

## 起源与项目概况

2004 年，加州大学圣克鲁兹分校（UC Santa Cruz）存储系统研究中心，博士生 Sage Weil 开始写一个叫 Ceph 的项目。2006 年，两篇论文先后发表：一篇是 OSDI 上的《Ceph: A Scalable, High-Performance Distributed File System》，讲一个分布式文件系统；另一篇是超算大会 SC'06 上的《CRUSH: Controlled, Scalable, Decentralized Placement of Replicated Data》，讲一个数据放置算法。2007 年，Weil 的博士论文完成，题目就叫 Ceph，副题是可靠、可扩展、高性能的分布式存储。Ceph 后来从文件系统扩展为统一存储平台。

两篇论文分别讨论文件系统与数据放置。Ceph 最初提供文件存储，后来在同一底座上增加块和对象接口。理解这三种接口，可以先看底层的数据放置机制。

Weil 在读博之前参与创办过一家网络托管公司 DreamHost。毕业之后，Ceph 的开发在 DreamHost 继续，并且直接跑进了生产环境。DreamHost 提供了真实的生产存储需求。和 Google 的 GFS、Yahoo 推动的 HDFS 一样，Ceph 的发展也与在通用服务器上承载生产数据的需求有关。

商业化经历了几个阶段：2012 年，团队成立 Inktank 公司，专门做 Ceph 的商业支持，同年发布第一个稳定版本系列 Argonaut。2014 年 4 月，Red Hat 以约 1.75 亿美元现金收购 Inktank。2018 年 11 月，Ceph 基金会成立，隶属于 Linux 基金会，项目治理从单一公司主导变成多家共管。2019 年 IBM 收购 Red Hat，2022 年 IBM 把 Red Hat 的存储产品线整合进 IBM Storage，Ceph 的商业发行版改名 IBM Storage Ceph。发行版的分工见 [[#发行版与厂商生态]]。

![Ceph 的二十年](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-architecture-01-ceph-history.svg)

图：从博士论文到基金会项目，Ceph 的关键节点

项目的基本信息如下。

| 条目 | 内容 |
| --- | --- |
| 起点 | 2004 年 UC Santa Cruz 研究项目，2006 年两篇论文发表并开源 |
| 创始人 | Sage Weil，DreamHost 联合创始人 |
| 许可证 | 核心代码 LGPL 2.1 或 LGPL 3，个别文件采用其他许可证 |
| 治理 | Ceph 基金会（2018 年成立，Linux 基金会下属） |
| 商业脉络 | Inktank（2012）→ Red Hat 收购（2014）→ IBM 整合（2022） |
| 三种形态 | 块（RBD）、对象（RGW）、文件（CephFS） |
| 原文介绍的版本 | Tentacle v20（2025 年 11 月发布）、Squid v19；当前维护状态见 [[#运维成本与版本升级]] |

原文把 Weil 的设计目标概括为自适应、分散数据放置和自愈。当时许多分布式存储使用中心元数据服务器记录和分配数据位置。Ceph 希望集群能够自行计算位置、发现故障并重建数据，减少管理员在这些环节的干预。硬件维护和容量规划仍需要人工完成。

关键问题是：没有集中放置表，客户端如何找到数据？Ceph 通过共享的拓扑和放置规则计算位置。

## 数据放置：查表、一致性哈希与 CRUSH

先看问题本身。分布式存储首先需要决定数据放在哪里。写入的时候要知道写去哪台机器，读取的时候要知道去哪台机器找。常见思路可以分成三类。

### 集中维护放置表

HDFS 采用集中放置表，NameNode 记录每个数据块在哪些 DataNode 上，客户端每次读写都先去 NameNode 查。好处是直观、可控，管理员想看什么都清清楚楚。代价是表本身成了中心：它的内存要装下全部元数据，它的可用性决定整个集群的可用性。因此，NameNode 的内存容量与高可用设计是 HDFS 的重要运维问题。

### 一致性哈希

把存储节点和数据都哈希到同一个环上，数据落在顺时针方向最近的节点。没有中心，节点增减时只有相邻区间的数据要移动。问题是这个环是平的：机架、机房这些层级关系在环上表达不出来，虚拟节点有助于均衡分布，但故障域仍需要额外的放置规则。

### 根据拓扑和规则计算

不维护集中放置表，只分发一份集群地图，所有参与者用同一个算法，拿数据的标识当场算出位置。相同输入得到相同输出，不必逐次查询集中服务。Ceph 选的就是这条。

![数据放在哪：三类答案](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-architecture-02-data-placement-options.svg)

图：数据放置的三类答案与各自代价

Ceph 的集群地图包含两部分：一棵描述集群结构的树，加一组放置规则。原文以 MB 级地图说明这一设计；地图大小仍取决于集群规模。客户端启动时从 MON 获取地图，数据 IO 通常不需要再经过集中放置表：拿对象标识和手里的地图，跑一遍 CRUSH 算法，算出数据该在哪几个 OSD 上，直接发请求过去。

这个设计换来两个直接的好处。第一，数据放置查询没有集中表的瓶颈，数据读写路径少一次位置查询，集群规模涨上去之后这一跳的差距会越来越大。第二，扩容缩容只改地图：新节点加进树里，所有参与者拿到新地图重新计算，只有落在新节点上的那部分数据需要搬家，其他数据原地不动。

代价也要说清楚。算法放置意味着位置是算出来的，不是登记出来的，排查时需要理解映射过程。要把特定数据限制在指定磁盘上，也需要通过池、规则和设备分组表达。这要求运维人员理解地图、规则和 PG 映射；CephFS 的目录元数据仍由 MDS 管理。

## CRUSH：拓扑、权重与故障域

CRUSH 的全称是 Controlled Replication Under Scalable Hashing，可控的、可规模化的哈希复制。它的职责是：给一个数据的标识，返回一组存储节点，整个过程不需要查任何表。输入有三样：集群地图、放置规则、数据的标识。

### 集群地图是一棵树

集群地图描述的是物理拓扑。根节点下面是若干层级，常见的是机房、机架、主机，叶子节点是 OSD，也就是每块盘对应的存储进程。每个节点都有一个权重，权重通常和容量成正比：一台插了 12 块大盘的机器，权重通常高于插 6 块小盘的机器，数据自然多往它那里放。拓扑树表达层级，权重表达容量，共同构成计算放置位置的输入。

### 规则规定打散到什么粒度

规则（CRUSH rule）声明冗余策略的边界。比如一条典型的规则写：三副本，故障域为主机。意思是三份副本必须落在三台不同的主机上——一台整机掉电，数据仍然有两份活着。要求更高的场景可以把故障域提到机架，代价是同样的副本数，机器之间要隔得更开，可选的落点变少。纠删码池的规则也是在这里定义的，硬件规划也需要按这些故障域配置节点。

### 确定性的伪随机放置

算法本体是一组伪随机哈希。计算使用 PG 标识、CRUSH 地图和规则，输出一组 OSD，例如 osd.3、osd.7、osd.14。地图的 epoch 标识配置版本，不应理解成每次都重新扰动全部数据的随机种子。伪随机保证了分布均匀，确定性保证了可复现：客户端和每个 OSD 拿同一份地图算同一道题，答案必然一致。所以写入方知道往哪写，存储方知道自己该不该有这份数据，双方不需要对答案。

地图变化的时候怎么办？每份地图有一个版本号，叫 epoch。加一块盘、撤一台机器，epoch 加一，新地图分发下去。重新计算之后，绝大多数数据的落点不变，只有和变化节点相关的那部分数据得到新的落点，需要迁移。迁移量大致等于新增容量占集群总容量的比例——这个性质和一致性哈希的优点是同一个，但 CRUSH 是靠树结构和权重做到的，不需要虚拟节点。

![CRUSH 的计算过程](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-architecture-03-crush-map-rules.svg)

图：地图加规则加标识，算出一组目标 OSD

### 和一致性哈希的分野

两者经常被放在一起比，这里把差别说透。一致性哈希把节点和数据映射到同一个环上，数据找顺时针最近的节点，节点增减只影响相邻的一段区间，迁移量小，这是它的核心贡献。但环是一维的、平的，物理世界的层级关系——哪些机器在同一个机架，哪些机架共用一个交换机——在环上没有位置。一个机架整体掉电，环不知道这回事，副本可能恰好都落在同一批节点上。

CRUSH 把层级直接做进结构里：树形地图天然有层级，规则明确声明副本打散到哪一层，权重精确控制分布比例。迁移量小这个优点两者都有，实现路径不同。工程上的区别在于：基础的一致性哈希环主要表达节点位置，CRUSH 直接表达拓扑层级和故障域规则。后者可以按主机、机架或机房表达放置边界。

![一致性哈希与 CRUSH 的分野](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-architecture-04-hash-ring-vs-crush.svg)

图：平的环与带层级的树

还有一个工程细节值得交代：客户端手里的地图可能是旧的。刚扩容、地图还没同步过来，客户端算出的落点就是错的。Ceph 的处理办法是把 epoch 带在每次请求里，OSD 收到请求发现版本对不上，会告诉客户端新地图在哪，客户端更新后重算再发。epoch 帮助参与者识别地图是否过期；数据一致性还依赖写入协议和 peering。故障恢复也依赖地图版本和 PG 状态协商。

## RADOS：统一的对象存储底座

CRUSH 解决的是算法问题，RADOS 是承载这个算法的存储层。RADOS 全称 Reliable Autonomic Distributed Object Store，可靠的、自治的分布式对象存储，是 Ceph 的底层存储。不管上层要的是块、对象还是文件，最后落到最底下，都是 RADOS 对象。

RADOS 对象很简单，三样东西：一个名字，一段字节，一组键值属性。它不直接提供 POSIX 目录树；对象 API 本身支持字节读写和追加，不能把它等同于 S3 的整对象接口。上层接口分别映射自己的数据模型：RBD 把一块虚拟磁盘切成一个个对象；RGW 把上传的文件存成对象，大文件自动切片；CephFS 把文件数据按块切成对象。上层负责把各自的数据模型映射成对象，RADOS 负责存储和冗余，三种接口由此共用底座。

服务对象的进程叫 OSD，Object Storage Daemon，一块盘对应一个。一台 12 盘位的服务器就跑 12 个 OSD，每个 OSD 管自己那块盘上的所有对象。对象读写、副本同步、故障重建和周期性完整性检查都由 OSD 完成。客户端的 IO 最终都是发给 OSD 的网络请求。

名字里的 Autonomic（自治）指的是：故障检测、数据重建和负载均衡由集群自动执行。一块盘坏了，OSD 之间的心跳发现它不响应，MON 确认后更新地图，相关数据开始往别处补，全程自动。具体流程见 [[#故障恢复与巡检]]。

![RADOS：上层三种形态，底层一种对象](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-architecture-05-rados-layers.svg)

图：三种接口最终都落到 RADOS 对象

## PG：对象分组、映射与数量规划

如果 CRUSH 直接拿每个对象算落点，会有个问题：一个集群里对象动辄几十亿个，每个对象的放置、副本状态、恢复进度都要单独跟踪的话，跟踪表本身就把系统压垮了。Ceph 在对象和 OSD 之间加了一层分组，叫 PG，Placement Group，放置组。

映射链是这样的：对象标识先经过哈希和池的 PG 映射，得到所属 PG；教学上常把这一步简化为对 PG 数量取模；PG 再作为一个整体走 CRUSH，算出一组 OSD。同一个 PG 里的对象共同管理：放在同一组 OSD 上，用同一套冗余策略，处于同一个状态。系统要跟踪的单位从几十亿个对象变成了几千个 PG，管理成本直接降了几个数量级。

![从对象到盘的映射链](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-architecture-06-object-pg-osd.svg)

图：对象先归入 PG，PG 再整体映射到一组 OSD

每个副本池PG 有一个主 OSD（primary），其他 OSD 保存副本。客户端通常向主 OSD 发请求，由它处理请求、给写入定序并转发复制操作。PG 数量则需要在分布均衡、恢复并行度和管理开销之间取舍。

PG 太少，数据堆在少数 PG 里，分布不均，单 PG 容量膨胀，故障恢复和再平衡的时候能并行的单位少，速度慢。PG 太多，每个 PG 都有自己的状态机和心跳报文，MON 和 OSD 的内存开销涨上去，集群出故障时要重新协商状态的 PG 数量也多，恢复启动本身就慢。

原文给出的经验关系是：每个 OSD 承载的 PG 副本数 ≈ PG 总数 × 副本数 ÷ OSD 数量，参考量级为每 OSD 约 100 个，全闪场景约 200 个。以 100 个 OSD、三副本、目标 100 计算，PG 总数约为 3333；原文用“3000 上下”作数量级示例。这只是规划起点，实际还需考虑多个池的分配和容量比例。

现代版本可用 pg_autoscaler 根据池的使用量和预期容量给出建议或调整 PG 数。原文“PG 数基本只能增不能减”的说法适用于早期版本；自 Nautilus 起支持 PG 合并和减少 pg_num。增减仍会引起重映射、数据迁移或短暂的 IO 协调，应留出资源。参见 [PG 数量规划](https://docs.ceph.com/en/tentacle/rados/operations/placement-groups/) 和 [Nautilus 的 PG 合并说明](https://ceph.io/en/news/blog/2019/new-in-nautilus-pg-merging-and-autotuning/)。

## 组件分工：MON、MGR、OSD、MDS 与 RGW

Ceph 集群由几种角色组成，各自职责清楚。各组件在控制面、数据面和文件元数据路径上承担不同职责。

MON（Monitor）维护集群的权威状态。它维护各种地图：集群地图、OSD 地图、PG 地图、MDS 地图，还管认证。多个 MON 之间用 Paxos 类共识协议保持一致，通常部署 3 个或 5 个，在多数派可用时维持 quorum，3 个 MON 可容忍 1 个失效，5 个可容忍 2 个失效。MON 不经手存储数据，流量很小，但对稳定性要求高——地图对不上，全集群都得等它。前面讲的集群地图版本号对账，对的就是 MON 手里这份权威版本。

MGR（Manager）提供监控和管理功能。指标采集、Web 仪表盘、容量告警、自动化模块（比如 pg_autoscaler）都挂在 MGR 上。早期这些功能塞在 MON 里，2017 年的 Luminous 版本把 MGR 独立出来。常见部署是两个，一主一备。

OSD 负责实际数据服务。一块盘一个进程，前面已经讲过。一个集群里 OSD 的数量最多，故障也最多，磁盘故障、慢请求和数据恢复通常都需要检查 OSD。

MDS（Metadata Server）只管 CephFS。目录树、inode、权限这些文件系统元数据由 MDS 管理，元数据本身也存在 RADOS 里。MDS 可以多活，用多个实例分担元数据压力，也可以配热备。只用 RBD 或 RGW 的集群不需要 MDS。

还有一个角色严格说属于三种形态那一层：RGW（RADOS Gateway），对象存储的 HTTP 网关，下一节讲。

![一个 Ceph 集群的组件拓扑](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-architecture-07-components.svg)

图：MON 管地图，MGR 管仪表盘，OSD 管数据，MDS 只管 CephFS

| 组件 | 职责 | 是否经手数据 | 典型数量 |
| --- | --- | --- | --- |
| MON | 维护集群地图，Paxos 共识，认证 | 否 | 3 或 5 |
| MGR | 指标、仪表盘、自动化模块 | 否 | 2 |
| OSD | 对象读写、副本同步、恢复、完整性校验 | 是 | 每盘一个 |
| MDS | CephFS 元数据：目录树、inode、权限 | 只管元数据 | 按需，可多活 |
| RGW | 对象存储 HTTP 网关，S3 兼容 | 是 | 按流量，至少 2 |

## RBD、RGW 与 CephFS

> [!note] 共享语义与性能
> 常见 RBD 文件系统卷按单节点读写使用，CephFS 提供跨客户端共享文件语义。ReadWriteOnce 限定节点，不一定限定单个 Pod；接口之间也没有脱离负载和配置的固定性能排序。RGW 解决的是 HTTP 对象访问模型，不能简单理解为块与文件性能的折中。

三种接口以不同方式把应用数据映射到 RADOS。三者的共同点是：数据最终都是 RADOS 对象，放置都走 CRUSH，冗余都靠 RADOS 的池（pool）配置。差异在上层怎么切数据、怎么给接口。

RBD 提供块设备。Linux 中 /dev/sda 等设备通常对应本地磁盘，rbd 设备则通过网络连接到 Ceph 集群中的存储区域，写入最终落在集群中。块设备既可直接使用，也可格式化后使用。一个 RBD 镜像就是一块虚拟磁盘，默认对象大小通常为 4 MiB，散布在池里。客户端有两条路：Linux 内核的 rbd 模块，或者用户态库（给 QEMU 这类程序用）。RBD 常用于虚拟机磁盘：OpenStack 的 Cinder 和 Nova、Proxmox、oVirt 都拿它当虚拟机的磁盘。RBD 支持快照，基于写时复制，快照无需立即复制全部数据；快照之上还能开可写克隆，做黄金镜像批量开虚拟机。

RGW 提供对象接口。RGW 进程对外提供 HTTP 服务，兼容 S3 接口（也兼容一部分早期的 OpenStack Swift 接口）。桶和对象的元数据也存在 RADOS 池里，大文件自动分片成多个对象。RGW 可以横向扩，前面挂负载均衡；支持多站点同步，做跨机房的数据复制。应用侧通过 S3 端点访问，但仍应核对所需 API 的兼容范围。

CephFS 提供文件系统接口。这是 Ceph 出生时的第一个形态。MDS 维护目录树和 inode，文件数据按块切成对象存进 RADOS。客户端用内核挂载或者 FUSE 挂载，多台机器可以同时挂同一个文件系统，标准 POSIX 语义。NFS 导出也支持，走 Ganesha。CephFS 的快照同样是写时复制。

![一套底座，三种形态](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-architecture-08-three-interfaces.svg)

图：三种形态共用同一个 RADOS 底座

| 形态 | 对外接口 | 必需组件 | 典型用途 |
| --- | --- | --- | --- |
| RBD 块 | 内核 rbd 模块、用户态库、iSCSI 网关 | MON + OSD | 虚拟机磁盘、数据库卷 |
| RGW 对象 | HTTP，S3 兼容，部分 Swift 兼容 | MON + OSD + RGW | 备份、图片视频、数据湖底座 |
| CephFS 文件 | 内核或 FUSE 挂载、NFS 导出 | MON + OSD + MDS | 共享数据集、家目录、媒体制作 |

这套结构的好处是：加一种存储形态，不用另起一套集群。硬件、运维工具、监控、备件都是同一套，容量也能在不同形态之间调配。相应的代价是：三种形态的 IO 跑在同一批盘上，互相竞争；任何一层出问题，三种形态一起受影响。 资源和监控可以复用，性能竞争、故障影响及运维复杂度也会集中到同一套平台，需要按池和故障域规划隔离。

## 副本、纠删码与写入流程

RADOS 的池在创建时就要定冗余策略，二选一：副本（replicated）或纠删码（erasure coded）。这个选择决定了空间成本、写入性能和恢复行为，需要结合负载选择。

副本池保存多份完整数据。健康的三副本池（size=3）在正常写入路径中等待副本确认；故障时能否继续 IO 还取决于 min_size 和 PG 状态，不能仅凭“还有一份副本”判断。空间开销三倍，换来的是低延迟、支持任意随机写、恢复速度快。RBD 常用副本池，尤其是随机小写负载；纠删码能否用于 RBD 数据池还取决于版本和覆盖写配置，不能把它当作接口上的禁止条件。

纠删码池把数据切成 k 个数据块，算出 m 个校验块，分散存放。典型配置 4+2：4 个数据块加 2 个校验块，任意坏两块都能恢复，空间开销只有 1.5 倍。省空间的代价是：写入要凑齐一个条带才能编码，覆盖写要先读旧块再算新校验（读改写），CPU 有额外开销，延迟也比副本高。原文建议优先把纠删码用于冷数据、大对象和 RGW 归档负载；具体取舍需看写入大小和延迟要求。

![三副本与纠删码 4+2](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-architecture-09-replicas-vs-ec.svg)

图：三副本与纠删码的容量和性能取舍

| 维度 | 三副本池 | 纠删码池（4+2） |
| --- | --- | --- |
| 空间开销 | ×3 | ×1.5 |
| 随机小写 | 直接支持 | 读改写，慢 |
| 写入延迟 | 低 | 较高，要凑条带 |
| 恢复速度 | 快，拷贝即可 | 慢，要读块重算 |
| 典型选择 | RBD、CephFS 元数据、热数据 | RGW 冷数据、备份归档 |

### 写入路径

以健康的三副本池为例，写入路径如下：

1. 客户端根据对象标识和池配置计算目标 PG，再通过 CRUSH 映射获得 OSD 集合和主 OSD。
2. 请求直接发送给主 OSD，数据路径不经过 MON。
3. 主 OSD 给写入定序，把操作转发给另外两个副本 OSD，同时完成本地持久化。
4. 参与本次写入的副本确认完成后，主 OSD 向客户端返回成功。健康状态下，这表示三份副本已确认写入。

如果写入过程中某个副本 OSD 没了，主 OSD 会报告，MON 更新地图，这个 PG 进入重新协商状态（peering），选出新的主，核对各副本的操作日志，把不一致的地方补齐，然后继续服务。这套流程保证了一件事：副本写入由主 OSD 定序，恢复时核对副本历史，以维持一致性。这里描述的是通常的主 OSD 路径，并不覆盖所有版本的副本读优化。常见 RBD 文件系统卷以单节点读写方式使用；CephFS 多客户端共享，还要由 MDS 协调文件元数据、锁和访问能力。

![一次写入的完整路径](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-architecture-10-replicated-write.svg)

图：写入直达主 OSD，全副本确认后返回

数据的完整性还有一道保险：OSD 会定期做 scrub（副本间比对校验）和 deep scrub（读全部数据算校验和），这些检查用于发现静默损坏。发现不一致后，还需要判断损坏类型和修复方式，不应假定所有不一致都会自动修复。


> [!note] 对象 API 与故障时 IO
> RADOS 提供 rados_append 等字节级接口；size 是期望副本数，min_size 是服务 IO 所需的最少副本数。原文图中的“全副本确认”描述健康三副本写入路径。参见 [Librados API](https://docs.ceph.com/en/tentacle/rados/api/librados/#rados_append) 和 [副本数与 min_size](https://docs.ceph.com/en/tentacle/rados/operations/pools/#setting-the-number-of-rados-object-replicas)。

## 部署方式与硬件规划

Ceph 的部署工具经历过几代变化。cephadm 从 2020 年的 Octopus 开始成为主要部署方式，用于引导集群及后续扩容、升级；Kubernetes 环境通常使用 Rook，以 Operator 和声明式资源管理 Ceph。早期手工脚本、ceph-deploy 和 Ansible 的流程适合研究旧环境，新部署应优先选择受支持的编排工具。后面的 [[#旧版部署与 Kubernetes 接入示例]] 保留旧环境的操作细节。

网络需要同时承载客户端 IO、副本同步和故障恢复。public 网络面向客户端，单独配置的 cluster 网络承载 OSD 心跳、复制和恢复。三副本写入包含主 OSD 的本地写和向另外两个 OSD 的复制，不能把它简化为“cluster 网络传三份数据”。是否分离两张网取决于流量和成本；官方说明许多部署只使用 public 网络也能正常工作，尤其是 25GbE 及更快的网络。

原文给出的社区经验是：10GbE 作为起步参考，全闪集群参考 25GbE，NVMe 高性能集群考虑 100GbE。它们不是固定最低规格，应按每节点磁盘吞吐、客户端并发和恢复窗口计算。参见 [Ceph 网络配置](https://docs.ceph.com/en/tentacle/rados/configuration/network-config-ref/)。

盘的组织方式是"一块盘一个 OSD"。常见混合介质配置是大容量 HDD 做数据盘，SSD 切出一部分给 BlueStore 的元数据（db 和 wal），元数据操作走 SSD，顺序写走 HDD。预算充足就全闪，性能上限高得多。原文特别提醒避开 SMR（叠瓦式磁记录）机械盘。这类盘写入特性差，重写放大严重，放进 Ceph 会拖慢恢复、放大抖动，社区和盘厂都反复提示过。

![OSD 磁盘的三种常见配置](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-operations-01-disk-tiers.svg)

图：三档磁盘配置，按预算和延迟要求选

OSD 数据盘通常不再叠加 RAID。RAID 卡会引入自己的缓存、日志和重建逻辑，和 Ceph 的冗余机制叠在一起，两套重建会竞争资源，也会增加故障定位的难度。标准做法是 HBA 直通或 JBOD 模式，裸盘直接交给 OSD，数据保护完全由 Ceph 的副本或纠删码负责。应让 Ceph 能直接观察和管理每块数据盘的故障与恢复。

MON 和 MGR 可以放在管理节点上，避免与高 IO 业务争用资源。MON 通常为 3 或 5 个，MGR 常见一主一备；时钟同步需要可靠配置，时钟漂移会影响 MON 的稳定性和仲裁，不能把它直接等同于脑裂。

监控可以使用 MGR 的 Prometheus 模块和 Grafana 仪表盘。容量常见默认水位为 nearfull 85%、backfillfull 90%、full 95%。这些水位需要检查每个 OSD 的使用率和实际配置：backfillfull 会阻止向过满目标 OSD 回填，full 会限制相关 PG 的写入；整体容量还有空闲也可能出现局部满盘。

![一个典型的 Ceph 部署](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-operations-02-deployment-layout.svg)

图：两张网、三种节点，一个典型部署的形状

| 项目 | 社区常见做法（非官方标准） |
| --- | --- |
| 网络 | 按负载决定是否分离 public / cluster；原文参考 10GbE、全闪 25GbE |
| 数据盘 | HDD 加 SSD 混部或全闪，SMR 盘避开 |
| OSD 组织 | 一块盘一个 OSD，db 与 wal 放 SSD |
| MON / MGR | MON 3 或 5 个，MGR 2 个，独立节点或管理节点，可靠的时间同步 |
| 监控 | MGR Prometheus 模块 + Grafana，容量水位进告警 |
| 起步规模 | 原作者的经验判断：三节点以下、百 TB 以下优先评估轻量方案 |

规模建议是成本判断，不是 Ceph 的容量下限。管理组件和日常维护存在固定开销，集群越大，通常越容易摊薄。原文倾向于把没有增长预期、总量不足百 TB 的小规模对象或文件需求交给轻量方案，例如 MinIO、MooseFS 或 NFS；把几百 TB 起步、将向 PB 增长的需求作为 Ceph 的主要候选场景。是否适用仍取决于接口、可用性目标和团队已有能力。

## FileStore 与 BlueStore

OSD 通过本地存储引擎写入磁盘。Ceph 曾从 FileStore 迁移到 BlueStore。两者的写入路径和本地元数据组织方式差别很大。

FileStore 复用本地文件系统：每块盘先格式化成 XFS，对象当成文件存进去。写入路径是日志优先：数据先写 journal（通常放在单独一块 SSD 上），fsync 确认，再进入主存储。这套设计的主要成本是数据和日志的重复写入。数据先写 journal 一遍，再由文件系统写主存储一遍；XFS 自己还有一套元数据日志。一次对象写入，盘上实际落了远不止一份。fsync 延迟会影响整条路径，小写、覆盖写尤其难受。另外，通用文件系统的事务语义和 Ceph 想要的不完全一致，很多操作要在文件系统之上再拼一层逻辑，代码复杂，行为也难预测。

BlueStore 的思路是反过来：让对象存储直接控制本地数据布局，减少通用文件系统带来的额外日志和语义适配。BlueStore 直接管理裸盘，元数据放进内嵌的 RocksDB，数据块用写时复制的方式分配，每个数据块带校验和。2017 年的 Luminous 版本（v12）里 BlueStore 成为默认引擎，FileStore 后来退出主要部署路径，Reef 起不再受支持。

![FileStore 与 BlueStore 的层次对比](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-operations-03-filestore-vs-bluestore.svg)

图：去掉中间的 XFS，是这次演进的核心动作

| 维度 | FileStore | BlueStore |
| --- | --- | --- |
| 盘的管理 | 先建 XFS，对象存成文件 | 直接管理裸盘 |
| 写入路径 | journal 加主存储，写两遍 | 写时复制，大块写无双写 |
| 元数据 | 文件系统 inode 加日志 | 内嵌 RocksDB |
| 数据校验 | 依赖文件系统 | 每个数据块带校验和 |
| 状态 | Reef 起不再受支持 | 2017 年 Luminous 起默认 |

2019 年，Ceph 团队把这段经历写成论文发表在 SOSP 上，题目很直白：《File systems unfit as distributed storage backends》，文件系统不适合作为分布式存储的后端。论文回顾了十年的演进，结论是：通用本地文件系统的设计假设（单机、单用户、层次化命名）和分布式存储的需求（批量对象、自带冗余、需要精确控制落盘）对不上，这会增加适配成本。是否复用本地文件系统也是其他分布式存储项目需要权衡的问题。

## 故障恢复与巡检

OSD 掉线是理解自愈过程的常见场景。故障检测、地图变化和 PG 恢复相互衔接。

1. OSD 通过秒级心跳检测彼此状态；某个 OSD 不响应时，其他 OSD 上报，MON 将其标记为 down。
2. 相关 PG 可能进入 degraded 或 undersized 等状态。是否继续服务取决于剩余副本、min_size 和 peering，不能只看一个状态词。
3. 在通常配置下，OSD 持续 down 超过 mon_osd_down_out_interval 后会被标记 out，常见默认值为 600 秒。noout 等配置和故障域策略可能改变这一行为。
4. 地图变化后，Ceph 选择新的放置目标，执行恢复或回填，最终回到 active+clean。运维人员需要确认告警、观察进度并判断硬件是否应更换。

恢复与回填的区别在于需要怎样同步数据：

- recovery：通常依据近期操作日志恢复缺失或过期的对象，避免扫描整个 PG。
- backfill：扫描和同步 PG 的全部内容，常见于新放置目标或日志不足以做增量同步的情况。它是 recovery 的一种特殊情况，不意味着健康副本已经丢失；如果数据本身无法找到，可能出现 unfound 或 incomplete，需要人工判断。

![一块盘掉线后的自愈时间线](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-operations-04-osd-failure-recovery.svg)

图：OSD 掉线后的恢复过程；图中 recovery / backfill 的区别以正文定义为准

巡检重点是 PG 状态及其持续时间：

| 状态 | 含义 | IO 判断 |
| --- | --- | --- |
| active+clean | PG 可服务且数据达到配置的冗余水平 | 正常目标状态 |
| degraded | 部分对象尚未达到期望冗余数 | 结合 active、min_size 等状态判断 |
| undersized | PG 副本数低于池的 size | 不等于已经低于 min_size |
| recovering / backfilling | 数据同步或回填进行中 | 关注进度及对业务 IO 的竞争 |
| peering | 副本协商历史和权威状态 | 完成协商后才能决定服务状态 |

PG 可以同时带多个状态。长时间未回到 active+clean 的 PG 是排查信号，但原因可能是空间、限速、未找到对象或故障尚未处理。参见 [PG 状态定义](https://docs.ceph.com/en/tentacle/rados/operations/pg-states/) 和 [min_size](https://docs.ceph.com/en/tentacle/rados/operations/pools/#setting-the-number-of-rados-object-replicas)。

![PG 的几个关键状态](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-operations-05-pg-states.svg)

图：常见 PG 状态；图中的 undersized 不等于低于 min_size

数据重建会占用集群的网络、磁盘和 CPU，与业务 IO 竞争资源。几百块盘的集群里换一台整机，backfill 跑上一两天不稀奇，期间业务 IO 会感到变慢。所以运维手里有一组限速参数，社区经验是业务高峰期限速慢跑，夜间窗口放开让它跑完。机器永久退役时，需要先完成数据迁移并确认可安全移除，再清理 OSD 和拓扑记录，避免数据尚未恢复就删除必要信息。

再往上一层的故障——MON 少数派失效、整机房网络分区——靠的还是同一套机制：多数派维持地图权威，少数派恢复后重新对账。集群规模越大，单点故障越频繁，自愈能力的意义就越从"功能"变成"日常"。运维人员需要理解恢复过程和资源竞争，才能安排干预时机。

还有一种比掉盘更麻烦的情况：盘没坏，但是变慢了。机械盘老化、固件缺陷、接口降速，都会让某块盘的响应时间从毫秒级劣化到秒级。这块盘上的 PG 是主副本的时候，整条写入链都被它拖住，客户端看到的是间歇性卡顿，监控上表现为 slow request（慢请求）告警。掉线的盘系统会自动绕开，慢盘却要等人发现。BlueStore 和 OSD 层对慢请求有统计和告警，巡检时看到 slow request 持续出现，就要动手定位是哪块盘，该换就换。慢盘往往仍在线，不能只依赖掉线后的自愈。

容量打满会使相关 PG 拒绝写入，虚拟机可能出现文件系统只读、数据库日志无法继续写入等业务现象。原文认为这类事故往往已有持续容量告警，因此需要提前扩容、清理冷数据，或把适合的冷数据迁入纠删码池。告警到满盘的时间取决于增长速度，不能把原文“一般有几周”的经验当作固定缓冲期。

## 运维成本与版本升级

Ceph 的学习成本来自相互关联的 PG、CRUSH、pool、flag 和 peering。掌握命令之外，还需要理解状态和干预前提。原文给出“生产集群至少有一名专职维护人员”的经验建议，并明确它不是官方要求。

以下保留原作者的人力估算，用于预算讨论，不作为规模门槛或配置标准：

| 集群规模 | 人力参考（社区经验） | 主要风险点 |
| --- | --- | --- |
| 50 块盘以下 | 原文建议优先评估其他方案 | 固定开销摊不薄，选轻量方案 |
| 50 到 300 块盘 | 1 名专职 | 容量规划、PG 数量、首次升级 |
| 300 到 1500 块盘 | 2 到 3 人小组 | 故障窗口、恢复限速、性能调优 |
| 1500 块盘以上 | 专职团队 | 架构演进、多集群拆分、自动化 |

版本升级需要读取目标版本发行说明、确认集群健康、演练并观察升级后的指标。原文用“一天演练加一天执行”说明投入，但实际窗口取决于节点数、升级路径和故障余量。

升级顺序取决于部署工具：cephadm 从 MGR、MON 开始，之后按其编排顺序升级其他守护进程；非 cephadm 的包升级流程可以是 MON → MGR → OSD，再处理 MDS、RGW 等组件。不能把其中一种顺序套到所有部署上。大版本是否允许跨级，也必须查目标版本说明，例如 Tentacle 支持从 Reef 或 Squid 升级。参见 [cephadm 升级](https://docs.ceph.com/en/tentacle/cephadm/upgrade/) 和 [Tentacle 发行说明](https://docs.ceph.com/en/latest/releases/tentacle/)。

原文讨论了 Reef v18（2023）、Squid v19（2024）和 Tentacle v20（2025）。它把前两者称为 LTS、Tentacle 称为常规版，并预计 Squid 于 2026 年 9 月停止维护；当前应以官方维护列表为准。截至 2026-10-11：

| 系列 | 当前列表中的版本 | 维护状态 | 官方结束日期 |
| --- | --- | --- | --- |
| Tentacle v20 | 20.2.4 | 活跃维护 | 预计 2027-06-01 |
| Squid v19 | 19.2.6 | 活跃维护 | 预计 2026-10-31 |
| Reef v18 | 18.2.8 | 已归档 | 2026-03-20 |

这些日期会调整，选型和升级前应再次查阅 [Ceph 发布与维护列表](https://docs.ceph.com/en/latest/releases/)。

![近年的版本节奏](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-operations-06-releases-upgrades.svg)

图：原文版本时间线；图中的 LTS 分类、固定不跳级和升级顺序请按正文及目标版本说明理解

社区里反复出现的坑也值得列一列：时钟没同步，MON 集群来回抖动；容量没人看，一路涨到 full 线，集群直接拒绝写入；出问题慌了手脚，手动删 MON 的数据目录，地图没了，集群瘫了；backfill 跑到一半嫌慢，手动停 OSD，越帮越忙。这些坑都有同一个根源：Ceph 的自动化程度很高，但它要求操作者也理解这套自动化的前提。不理解前提的手动操作，比故障本身更危险。

原文建议按下面的顺序学习，故障演练应在独立实验集群中进行：

1. 用三台闲置机器或虚拟机搭建实验集群，走一遍 cephadm 部署流程。
2. 学会读 ceph status，识别健康状态、PG 状态和容量水位。
3. 在实验环境停止一个 OSD，观察降级、peering 和恢复，把状态变化与原理对应起来。

理解“对象 → PG → OSD”这条映射，以及地图变化后的重映射，是继续学习其他概念的基础。

## 发行版与厂商生态

Ceph 的生态包括上游社区、商业发行版和部署编排工具。上游由 ceph.io 社区开发，2018 年成立的 Ceph 基金会隶属于 Linux 基金会，多家公司共同投入。核心代码采用 LGPL 2.1 或 LGPL 3，其他文件的许可需按 [COPYING 清单](https://github.com/ceph/ceph/blob/main/COPYING) 核对。

商业线的变迁很快：2014 年 Red Hat 收购 Inktank，做出 Red Hat Ceph Storage；2019 年 IBM 收购 Red Hat；2022 年，IBM 把 Red Hat 的存储产品线整合进 IBM Storage，发行版改名 IBM Storage Ceph。同期，Red Hat 自己的存储重心转向 OpenShift Data Foundation（ODF）——跑在 OpenShift 上的存储层，底座同样是 Ceph。SUSE Enterprise Storage 已不向新客户销售，既有客户支持取决于合同；官方生命周期页给出的 SES 6 通用支持结束日期为 2022-05-30，不能用原文的 2022 年 1 月概括整个产品线。Ubuntu 阵营有 Canonical 的 Charmed Ceph。Kubernetes 场景常用 Rook 编排 Ceph。

![Ceph 的发行版与生态](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-operations-07-distributions.svg)

图：上游一棵树，商业分支各有去向

| 形态 | 背景 | 现状 |
| --- | --- | --- |
| 上游社区 | Ceph 基金会，核心代码 LGPL 2.1 / 3 | 主干，年度发布，多家共建 |
| IBM Storage Ceph | 原 Red Hat Ceph Storage | 2022 年并入 IBM，商业主力 |
| OpenShift Data Foundation | Red Hat，OpenShift 上的存储层 | 底座是 Ceph，持续迭代 |
| Charmed Ceph | Canonical / Ubuntu | 持续维护 |
| Rook | CNCF 毕业项目 | K8s 场景事实标准 |
| SUSE Enterprise Storage | SUSE 的 Ceph 发行版 | 不再向新客户销售；既有客户按合同与版本核对支持 |

国内的情况，概括地说：多家云厂商和存储厂商都有基于 Ceph 的商业发行版，也有公开的 EB 级部署实践，私有云和公有云的存储底座里 Ceph 系产品占相当比例。具体厂商不逐一点评，选型时的判断标准对所有发行版都一样：基于上游哪个版本、对上游有没有持续贡献、出了问题响应能力如何。评估发行版应重点看支持能力、上游跟进和定制修改的维护成本。

## 公开部署与规模口径

原文引用 Linux 基金会 2024 年 12 月新闻稿中的用户自报规模：用户自行报告的 Ceph 存储总量超过 1 EB，分布在超过 3000 个集群里。这是用户自报的采用规模，不能等同于审计后的完整装机统计。

知名用户挑几个有公开资料的。CERN（欧洲核子研究中心）从 2013 年开始评估 Ceph，用来承接实验产生的海量数据，据公开报道有世界上规模最大的 Ceph 集群之一。DigitalOcean 用 Ceph 做云平台的块存储底座，其官方博客披露过数十个生产集群的规模，后来还加入了 Ceph 基金会。Bloomberg 的内部云存储平台也建在 Ceph 上，多次在 Ceph 社区会议上分享大规模运维经验。电信行业的采用也很多，多家运营商用它承载内部云和边缘节点。

这些公开案例说明 Ceph 可以支持大规模部署，但具体结果仍依赖硬件、负载、维护团队和流程，不能直接用作本集群的性能承诺。

## 选型判断

可以依次检查四个条件。

### 块存储需求

私有云、虚拟化平台要给虚拟机供盘，OpenStack、Proxmox、oVirt 这类场景，RBD 是 Ceph 的主要能力之一，这个需求单独就能撑起上 Ceph 的理由。纯对象存储需求，不构成这个理由。

### 多种接口与资源复用

块、对象、文件都要，还想共用一套硬件和运维班子，Ceph 是常见的统一存储候选。只要一种形态，就有更轻的选择。

### 规模与增长预期

几百 TB 起步、有增长预期，Ceph 的固定开销才摊得薄。一百来 TB 以内，轻量项目或者云托管更划算。

### 团队与支持服务

原文建议至少预留一名专职人员，规模扩大后配置团队。没有这个人力预算，前面的理由再多也别自建，去买发行版的支持服务，或者直接用云厂商的托管存储。

![选型判断树](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/11/storage/ceph-operations-08-selection.svg)

图：从接口、规模和团队能力判断是否适合自建

| 维度 | Ceph | MinIO 等对象项目 | GlusterFS 等文件项目 | 云厂商托管 |
| --- | --- | --- | --- | --- |
| 接口 | 块 + 对象 + 文件 | 对象 | 文件 | 按服务 |
| 运维成本 | 高，需专门能力 | 通常较低 | 中 | 底层由厂商维护 |
| 合适规模 | 数百 TB 起 | 小到中 | 小到中 | 弹性 |
| 典型场景 | 私有云底座 | S3 端点、备份 | 共享文件 | 公有云业务 |

还应比较自建和云托管的成本。公有云上的云盘和对象存储服务，不少在底层用的正是 Ceph 或类似架构的系统，DigitalOcean 就是公开的例子。但这不意味着用户要自己跑 Ceph——能用托管服务就用托管服务，自建是给"没有托管可用、又有规模、又有人"的场景准备的。需要把这三个条件放在一起评估。

其他开源项目提供了不同的取舍。纯对象存储，《MinIO，S3兼容存储的兴起与转折》（第 13 篇）讲的 MinIO 和《SeaweedFS，小文件哲学的长跑者》（第 14 篇）部署简单、资源占用小，中小规模下体验更好；只要共享文件，MooseFS 开箱即用，JuiceFS 用对象存储加独立元数据引擎，运维模型都简单得多，两者分别是《MooseFS，开箱即用的轻量选手》和《JuiceFS，元数据与数据分家》的主角；GlusterFS 也是原文讨论的共享文件候选。原作者更倾向于在多接口、大规模需求下选择 Ceph，而在单一需求下先评估轻量方案。选型时需要把满足需求所需的功能与后续维护成本一起比较。

## AI 负载中的分工

在 AI 基础设施中，Ceph 常用于三个位置：RBD 给 GPU 云的虚拟机当系统盘和数据盘；RGW 提供 S3 兼容接口，训练框架、数据湖工具链直接对接；CephFS 作为共享数据集和模型仓库，多台训练机同时读。原文把这些位置作为 Ceph 参与 AI 平台的典型方式。

但要说清楚边界。训练主链路上的极端负载——万卡集群的 checkpoint 洪峰、海量小文件的高吞吐随机读——有更对口的选择：Lustre、DAOS 和 [[Docker-Kubernetes/k8s-storage/开源存储DeepSeek 3FS，AI原生的并行文件系统|DeepSeek 3FS]] 等并行存储。Ceph 能跑这些负载，但论极致吞吐和延迟，它不是为此设计的。checkpoint 这种大顺序写场景，Ceph 用大容量盘加纠删码池接得住，但对时延敏感的场景要专门调优。

原文还介绍了 Ceph 与缓存或文件访问层配合的方式：数据放 Ceph，前面挂 Alluxio 或 JuiceFS 做缓存和加速，计算节点读缓存，冷数据沉在 Ceph。这是一种存算分离的搭法，需要同时规划底层容量和访问层性能。从分工上看，Ceph 常承担长期数据底座：长期保存数据集、模型、产物是它的强项，喂数据的最后一公里交给专门的加速层或者并行文件系统。


> [!note] 经验值与原图的适用范围
> 网络速率、容量规模、人力数量和恢复时长均为原文经验参考。原图保留了来源的表述：10 分钟内重新上线的 OSD 仍可能需要同步缺失写入；backfill 不表示健康副本已丢失；undersized 不等于低于 min_size；升级顺序取决于编排方式。图中的“三副本传三份”和容量水位也应按正文解释。
>
> SUSE 状态参见 [产品说明](https://www.suse.com/download/ses/) 和 [生命周期](https://www.suse.com/lifecycle/)；FileStore 状态参见 [BlueStore 迁移](https://docs.ceph.com/en/squid/rados/operations/bluestore-migration/)。

## 旧版部署与 Kubernetes 接入示例

> [!warning] 适用版本
> 以下示例涉及 EL7、Ceph Jewel、ceph-deploy、旧版 in-tree RBD / CephFS、旧 external-storage Provisioner 和 Rook 1.12。Kubernetes 1.31 已移除 in-tree RBD / CephFS 插件，当前接入应使用 Ceph CSI；示例中的 API、镜像和配置不能当作当前生产部署清单。参见 [Kubernetes 1.31 移除说明](https://kubernetes.io/blog/2024/08/13/kubernetes-v1-31-release/)。
>
> 实验记录包含关闭防火墙 / SELinux、使用 client.admin、chmod 777 和 Recycle 等做法。生产环境需要按权限、认证、网络隔离和回收策略重新设计，存储副本也不能替代备份。Ceph 可以由 cephadm 管理，也可以由 Rook 运行在 Kubernetes 中；是否独立部署取决于故障隔离和维护能力。

### 主机准备（EL7 实验环境）

#### 配置三台主机的静态 IP

| 主机 | 实验角色 | IP |
| --- | --- | --- |
| master1-admin | 管理节点 | 192.168.40.7 |
| node1-monitor | MON 节点 | 192.168.40.8 |
| node2-osd | OSD 节点 | 192.168.40.9 |

~~~ini
#修改/etc/sysconfig/network-scripts/ifcfg-ens33文件，变成如下：
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static
IPADDR=192.168.40.200
NETMASK=255.255.255.0
GATEWAY=192.168.40.2
DNS1=192.168.40.2
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_FAILURE_FATAL=no
IPV6_ADDR_GEN_MODE=stable-privacy
NAME=ens33
DEVICE=ens33
ONBOOT=yes

#修改配置文件之后需要重启网络服务才能使配置生效，重启网络服务命令如下：
service network restart
~~~

#### 配置主机名

~~~sh
hostnamectl set-hostname master1-admin && bash
hostnamectl set-hostname node1-monitor && bash
hostnamectl set-hostname node2-osd && bash
~~~

#### 配置 hosts

~~~sh
#3台机器上/etc/hosts中增加：
192.168.40.7   master1-admin  
192.168.40.8   node1-monitor  
192.168.40.9   node2-osd  
~~~

#### 配置 SSH 互信

~~~sh
#设置root密码
passwd root
Aa111111111
#以master1-admin为例
ssh-keygen -t rsa
ssh-copy-id master1-admin
ssh-copy-id node1-monitor
ssh-copy-id node2-osd 
~~~

#### 实验环境关闭防火墙

~~~sh
#3台都执行
systemctl stop firewalld && systemctl disable firewalld
~~~

#### 实验环境关闭 SELinux

~~~sh
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
~~~

#### 配置 Ceph 软件源

~~~sh
#3台都执行
yum install -y yum-utils 
yum-config-manager --add-repo https://dl.fedoraproject.org/pub/epel/7/x86_64/ 
yum install --nogpgcheck -y epel-release
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7 
rm /etc/yum.repos.d/dl.fedoraproject.org*
~~~

~~~ini
vim /etc/yum.repos.d/ceph.repo

[Ceph]
name=Ceph packages for $basearch
baseurl=http://mirrors.aliyun.com/ceph/rpm-jewel/el7/x86_64/ 
enabled=1 
gpgcheck=0 
type=rpm-md 
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc 
priority=1
[Ceph-noarch] 
name=Ceph noarch packages 
baseurl=http://mirrors.aliyun.com/ceph/rpm-jewel/el7/noarch/ 
enabled=1 
gpgcheck=0 
type=rpm-md 
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc 
priority=1 
[ceph-source]
name=Ceph source packages 
baseurl=http://mirrors.aliyun.com/ceph/rpm-jewel/el7/SRPMS/ 
enabled=1 
gpgcheck=0 
type=rpm-md 
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc 
priority=1
~~~

#### 配置时间同步

~~~sh
service ntpd stop
ntpdate cn.pool.ntp.org

crontab -e
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org

service crond restart
~~~

#### 安装基础软件包

~~~sh
yum install -y yum-utils device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat  ipvsadm conntrack ntpdate telnet deltarpm
~~~

### 用 ceph-deploy 部署集群

> [!note] 旧环境配置
> 下文 ceph.conf 实际设置 size=2，注释中的“从 3 改成 1”与配置不一致，应以数值为准；这是实验配置。时钟漂移阈值不应代替时间同步。

#### 安装 Ceph

~~~sh
#master1-admin上执行，安装ceph-deploy
yum install python-setuptools ceph-deploy -y
#3台上都执行，安装ceph
yum install ceph ceph-radosgw  -y
#确认ceph版本
ceph --version
~~~

#### 生成 MON 节点配置

~~~sh
#master1-admin上创建一个目录，用于保存 ceph-deploy 生成的配置文件信息
cd /etc/ceph
ceph-deploy new master1-admin node1-monitor node2-osd
ls
#生成了如下配置文件，Ceph配置文件、一个monitor密钥环和一个日志文件
#ceph.conf  ceph-deploy-ceph.log  ceph.mon.keyring
~~~

#### 初始化 MON

~~~sh
#把ceph.conf配置文件里的默认副本数从3改成1 。把osd_pool_default_size = 2 加入[global]段，这样只有2个osd也能达到active+clean状态：
vim /etc/ceph/ceph.conf
[global]
fsid = c617a513-0b8e-40a4-ba5a-741bbc9a13d8
mon_initial_members = master1-admin, node1-monitor, node2-osd
mon_host = 192.168.40.7,192.168.40.8,192.168.40.9
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
osd_pool_default_size = 2
mon clock drift allowed = 0.500 
mon clock drift warn backoff = 10

#mon clock drift allowed ，监视器间允许的时钟漂移量，默认值0.05
#这个设置定义了在发出警告之前，监视器的时间漂移必须超过 mon clock drift allowed 的多少倍。这意味着，如果 mon clock drift allowed 是0.500秒，那么只有当监视器的时间漂移超过5秒时，才会发出警告。
~~~

~~~sh
#初始化monitor，收集所有密钥
#master1-admin上
cd /etc/ceph
ceph-deploy mon create-initial
ls *.keyring
~~~

#### 部署 OSD

~~~sh
#准备osd，在master1-admin上
cd /etc/ceph/
ceph-deploy osd prepare master1-admin:/dev/sdc
ceph-deploy osd prepare node1-monitor:/dev/sdc 
ceph-deploy osd prepare node2-osd:/dev/sdc

#激活osd，在master1-admin上
ceph-deploy osd activate master1-admin:/dev/sdc1
ceph-deploy osd activate node1-monitor:/dev/sdc1
ceph-deploy osd activate node2-osd:/dev/sdc1

#查看状态：
ceph-deploy osd list master1-admin node1-monitor node2-osd
~~~

#### 创建 CephFS

使用 CephFS 至少需要一个 MDS，为客户端提供文件元数据服务。

##### 创建 MDS

~~~sh
#master1-admin上
ceph-deploy mds create master1-admin node1-monitor node2-osd
#查看ceph当前文件系统
ceph fs ls   
~~~

> 一个cephfs至少要求两个librados存储池，一个为data，一个为metadata。当配置这两个存储池时，注意：
>
> 1. 为metadata pool设置较高级别的副本级别，因为metadata的损坏可能导致整个文件系统不可用。
> 2. 建议metadata pool使用低延时存储，比如SSD，因为metadata会直接影响客户端的响应速度。

##### 创建 OSD 存储池

> [!note] PG 参数的版本差异
> 下文 128 / 512 / 4096 是旧笔记的静态参考值。现代 Ceph 已有 PG autoscaler 和 PG 合并能力，不能把“无法自动计算”或这组值套到当前集群，参见 [[#PG：对象分组、映射与数量规划]]。

~~~sh
#master1-admin上
ceph osd pool create cephfs_data 128
ceph osd pool create cephfs_metadata 128
~~~

> 上面的128是pg_num的值，确定 pg_num 取值是强制性的，因为不能自动计算。下面是几个常用的值：
>
> - 少于 5 个 OSD 时可把 pg_num 设置为 128
>
> - OSD 数量在 5 到 10 个时，可把 pg_num 设置为 512
>
> - OSD 数量在 10 到 50 个时，可把 pg_num 设置为 4096
>
> - OSD 数量大于 50 时，你得理解权衡方法、以及如何自己计算 pg_num 取值
>
> 自己计算 pg_num 取值时可借助 pgcalc 工具：随着 OSD 数量的增加，正确的 pg_num 取值变得更加重要，因为它显著地影响着集群的行为、以及出错时的数据持久性（即灾难性事件导致数据丢失的概率）。

##### 创建文件系统

~~~sh
ceph fs new hangtestfs cephfs_metadata cephfs_data
#查看创建后的cephfs
ceph fs ls
#查看mds节点状态
ceph mds stat 
#查看存储集群状态信息
ceph -s
~~~

### Pod 直接挂载 RBD（旧版 in-tree 插件）

#### 安装节点客户端

~~~sh
# kubernetes要想使用ceph，需要在k8s的每个node节点安装ceph-common的驱动  。
#把ceph节点上的ceph.repo文件拷贝到k8s各个节点/etc/yum.repos.d/目录下，然后在k8s的各个节点yum install ceph-common -y
scp /etc/yum.repos.d/ceph.repo 192.168.40.4:/etc/yum.repos.d/
scp /etc/yum.repos.d/ceph.repo 192.168.40.5:/etc/yum.repos.d/
scp /etc/yum.repos.d/ceph.repo 192.168.40.6:/etc/yum.repos.d/
#每个k8s节点上安装
yum install ceph-common -y
#在ceph的master1-admin上把ceph配置文件拷贝到k8s node上
scp /etc/ceph/* 192.168.40.4:/etc/ceph/
scp /etc/ceph/* 192.168.40.5:/etc/ceph/
scp /etc/ceph/* 192.168.40.6/etc/ceph/
~~~

#### 创建 RBD 镜像

~~~sh
#master1-admin上
#创建ceph rbd
ceph osd pool create k8srbd1 6 #创建pool，pgnum是6
rbd create rbda -s 1024 -p k8srbd1 #创建1G大小的块设备
rbd feature disable k8srbd1/rbda object-map fast-diff deep-flatten
~~~

#### 创建 Pod 直接挂载 RBD

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: po-testrbd
spec:
  containers:
    - name: nginx
      image: nginx
      imagePullPolicy: IfNotPresent
      volumeMounts:
      - name: testrbd
        mountPath: /mnt
  volumes:
    - name: testrbd #注意： k8srbd1下的rbda被pod挂载了，那其他pod就不能占用这个k8srbd1下的rbda了
      rbd:
        monitors:
        - '192.168.40.7:6789'
        - '192.168.40.8:6789'
        - '192.168.40.9:6789'
        pool: k8srbd1
        image: rbda
        fsType: xfs
        readOnly: false
        user: admin
        keyring: /etc/ceph/ceph.client.admin.keyring
~~~

下面记录旧版 Pod 直接挂载同一个 RBD 镜像的失败案例。它不同于通过 PVC 在单节点共享同一卷的行为。

  ~~~yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: dep-cephrbd
  spec:
    replicas: 2
    selector:
      matchLabels:
        storage: ceph
    template:
      metadata:
        labels:
          storage: ceph
      spec:
        containers:
        - name: nginx
          image: nginx
          imagePullPolicy: IfNotPresent
          volumeMounts:
          - name: testrbd
            mountPath: /mnt/
        volumes:
        - name: testrbd #注意： k8srbd1下的rbda被pod挂载了，那其他pod就不能占用这个k8srbd1下的rbda了
          rbd:
            monitors:
            - '192.168.40.7:6789'
            - '192.168.40.8:6789'
            - '192.168.40.9:6789'
            pool: k8srbd1
            image: rbda
            fsType: xfs
            readOnly: false
            user: admin
            keyring: /etc/ceph/ceph.client.admin.keyring
  ~~~

原实验中，两个 Pod 直接使用同一个 RBD 镜像时，只有一个能启动，另一个提示 `MountVolume.WaitForAttach failed for volume "testrbd" : rbd image k8srbd1/rbda is still being used`。是否支持共享，还需核对节点、访问模式和插件实现。

### 用 RBD 创建静态 PV

#### 创建 Secret

~~~sh
#创建ceph-secret这个k8s secret对象，这个secret对象用于k8s volume插件访问ceph集群，获取client.admin的keyring值，并用base64编码，在master1-admin（ceph管理节点）操作
ceph auth get-key client.admin | base64
#创建ceph的secret，在k8s的控制节点操作：
cat secret-ceph.yaml 
apiVersion: v1
kind: Secret
metadata:
  name: ceph-secret
data:
  key: QVFCVFJwdGx4Z2VoTFJBQW9QVkpsb3NvZDl1ZFBTYXRZbThDUGc9PQ== #<上一步生成的key>

kubectl apply -f ceph-secret.yaml
~~~

#### 创建 Pool 与镜像

~~~sh
#创建ceph rbd
ceph osd pool create k8srbd1 6 #创建pool，pgnum是6
rbd create rbda -s 1024 -p k8srbd1 #创建1G大小的块设备
rbd feature disable k8srbd1/rbda object-map fast-diff deep-flatten
~~~

#### 创建 PV

~~~yaml
apiVersion: v1 
kind: PersistentVolume 
metadata: 
  name: ceph-pv 
spec:   
   capacity:     
     storage: 1Gi   
   accessModes:     
   - ReadWriteOnce   
   rbd:     
         monitors:       
         - '192.168.40.7:6789'
         - '192.168.40.8:6789'
         - '192.168.40.9:6789'    
         pool: k8srbd1     
         image: rbda     
         user: admin     
         secretRef:       
           name: ceph-secret     
         fsType: xfs     
         readOnly: false   
   persistentVolumeReclaimPolicy: Recycle
~~~

#### 创建 PVC

~~~yaml
kind: PersistentVolumeClaim 
apiVersion: v1 
metadata:   
  name: ceph-pvc 
spec:   
  accessModes:     
  - ReadWriteOnce   
  resources:     
   requests:       
    storage: 1Gi
~~~

#### 挂载 PVC

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  selector:
    matchLabels:
     app: nginx
  replicas: 2 # tells deployment to run 2 pods matching the template
  template: # create pods using pod definition in this template
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
        volumeMounts:
          - name: ceph-data
            mountPath: "/ceph-data"
      volumes:
      - name: ceph-data
        persistentVolumeClaim:
          claimName: ceph-pvc
~~~

- 通过 PV/PVC 使用 RBD 时，ReadWriteOnce 允许同一节点上的多个 Pod 使用卷，也允许同一 Pod 的多个容器使用。
- ReadWriteOnce 不支持跨节点同时读写同一卷。
- 原实验记录了节点失联后，新节点上的 Pod 因旧挂载未解除而无法启动。恢复取决于驱动的解绑、故障节点隔离和卷锁处理，不能把它理解为所有 RBD 卷都无法自动恢复。

对应的处理思路：

1. 需要跨节点共享写入时，使用具备相应语义的文件存储，例如 CephFS。
2. 用节点标签把 Deployment 固定到某个节点。原笔记不建议这样做，因为该节点故障时会影响服务。

访问模式与卷呈现方式参见 [Kubernetes PV 文档](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#volume-mode)。

### 用旧版 RBD Provisioner 动态供应 PV

> [!note] selfLink 兼容处理
> 这一节的 RemoveSelfLink=false 只对应旧 Provisioner 和 Kubernetes 1.20 时期的故障记录，不是当前 Kubernetes 的通用修复方式。新部署应改用受支持的 Ceph CSI 驱动。

#### 旧版 Provisioner 的配置文件准备

~~~sh
#3台ceph节点和3台k8s节点都执行。sc需要用到。
chmod 777  -R  /etc/ceph/*
mkdir /root/.ceph/
cp -ar /etc/ceph/ /root/.ceph/
~~~

#### 安装旧版 RBD Provisioner

~~~sh
#事先上传镜像
docker load -i 
~~~

~~~yaml
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: rbd-provisioner
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: rbd-provisioner
rules:
  - apiGroups: [""]
    resources: ["persistentvolumes"]
    verbs: ["get", "list", "watch", "create", "delete"]
  - apiGroups: [""]
    resources: ["persistentvolumeclaims"]
    verbs: ["get", "list", "watch", "update"]
  - apiGroups: ["storage.k8s.io"]
    resources: ["storageclasses"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["create", "update", "patch"]
  - apiGroups: [""]
    resources: ["services"]
    resourceNames: ["kube-dns","coredns"]
    verbs: ["list", "get"]
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: rbd-provisioner
subjects:
  - kind: ServiceAccount
    name: rbd-provisioner
    namespace: default
roleRef:
  kind: ClusterRole
  name: rbd-provisioner
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: rbd-provisioner
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
- apiGroups: [""]
  resources: ["endpoints"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: rbd-provisioner
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: rbd-provisioner
subjects:
- kind: ServiceAccount
  name: rbd-provisioner
  namespace: default
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rbd-provisioner
spec:
  selector:
    matchLabels:
      app: rbd-provisioner
  replicas: 1
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: rbd-provisioner
    spec:
      containers:
      - name: rbd-provisioner
        image: quay.io/xianchao/external_storage/rbd-provisioner:v1
        imagePullPolicy: IfNotPresent
        env:
        - name: PROVISIONER_NAME
          value: ceph.com/rbd
      serviceAccount: rbd-provisioner
~~~

#### 创建 Ceph Secret

~~~sh
#创建ceph-secret这个k8s secret对象，这个secret对象用于k8s volume插件访问ceph集群，获取client.admin的keyring值，并用base64编码，在master1-admin（ceph管理节点）操作
ceph auth get-key client.admin | base64
~~~

~~~yaml
#创建ceph的secret，在k8s的控制节点操作：
apiVersion: v1
kind: Secret
metadata:
  name: ceph-secret-sc
type: "ceph.com/rbd" #secret的type除了可以用内置的，也可以自定义一个string。
data:
  key: QVFCVFJwdGx4Z2VoTFJBQW9QVkpsb3NvZDl1ZFBTYXRZbThDUGc9PQ== #<上一步生成的key>
~~~

~~~sh
#创建ceph pool，只需要创建pool即可，rbd设备会被sc来自动创建
ceph osd pool create k8stest1 6 #创建pool，pgnum是6
~~~

#### 创建 StorageClass

~~~yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: k8s-rbd
provisioner: ceph.com/rbd #要用provisioner里面env定义的name
parameters:
  monitors: 192.168.40.8:6789,192.168.40.7:6789,192.168.40.9:6789
  adminId: admin
  adminSecretName: ceph-secret-sc
  pool: k8stest1
  userId: admin
  userSecretName: ceph-secret-sc
  fsType: xfs
  imageFormat: "2" #指定了RBD镜像的格式。"2"表示使用第二版的RBD镜像格式，这是一种新的、更加灵活的格式，支持更多的特性，如快照、克隆和层次化存储等
  imageFeatures: "layering" #这个参数指定了RBD镜像的特性。"layering"表示启用了层次化存储特性。层次化存储允许镜像共享相同的数据块，可以节省存储空间，并且可以更快地创建新的镜像和快照。
~~~

> [!warning] K8s 1.20版本兼容问题
> k8s1.20版本通过rbd provisioner动态生成pv会报错:
>
> ```sh
> kubectl logs rbd-provisioner-685746688f-8mbz
> ```
>
> E0418 15:50:09.610071    1 controller.go:1004] provision "default/rbd-pvc" class "k8s-rbd": unexpected error getting claim reference: selfLink was empty, can't make reference
>
> - 报错原因是1.20版本禁用了selfLink，解决方法如下；
>
> - 编辑/etc/kubernetes/manifests/kube-apiserver.yaml，在这里：
>
> ```yaml
> spec:
>  containers:
>  - command:
>    - kube-apiserver
> ```
>
> 添加这一行：
>
> ```yaml
> - --feature-gates=RemoveSelfLink=false
> ```
>
> 重启kubelet
>
> ~~~sh
> systemctl restart kubelet
> ~~~

#### 创建 PVC

~~~yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: rbd-pvc
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  resources:
    requests:
      storage: 1Gi
  storageClassName: k8s-rbd
~~~

> 在 PVC 定义中，`spec.volumeMode` 指定卷以文件系统还是裸块设备的方式提供给容器；读写和共享访问模式由 `accessModes` 表达。
>
> `volumeMode`字段有两个可能的取值：
>
> 1. `Filesystem`：默认模式，由卷插件准备或使用已有文件系统，再挂载给容器。
> 2. `Block`：以裸块设备提供给容器，不由 Kubernetes 格式化或挂载文件系统。
>
> 按应用需求选择：普通文件读写使用 `Filesystem`；需要直接管理块设备或文件系统的应用可以使用 `Block`。性能差异需要按负载测试。

#### 创建 Pod 挂载 PVC

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    test: rbd-pod
  name: ceph-rbd-pod
spec:
  containers:
  - name: ceph-rbd-nginx
    image: nginx:latest
    imagePullPolicy: IfNotPresent
    volumeMounts:
    - name: ceph-rbd
      mountPath: /mnt
      readOnly: false
  volumes:
  - name: ceph-rbd
    persistentVolumeClaim:
      claimName: rbd-pvc
~~~

### CephFS 静态 PV 与共享挂载

> [!warning] Secret 的值
> 下文实验记录把整个 keyring 文件做 Base64 编码。CephFS Secret 的 key 应是密钥值，而不是带 [client.admin] 和 key = 的完整文件。按对应插件的文档提取实际 key；不要直接复用下文的示例编码。

#### 创建 CephFS 子目录

~~~sh
ceph fs ls
#为了别的地方能挂载cephfs，先创建一个secretfile，在master1-admin上
cat /etc/ceph/ceph.client.admin.keyring |grep key|awk -F" " '{print $3}' > /etc/ceph/admin.secret

#挂载cephfs的根目录(192.168.40.8:6789:/)到集群mon节点下的一个目录，比如/mnt/k8s_data/，因为挂载后，我们就可以直接在k8s_data下面用Linux命令创建子目录了。
mkdir /mnt/k8s_data/
mount -t ceph 192.168.40.8:6789:/ /mnt/k8s_data -o name=admin,secretfile=/etc/ceph/admin.secret
df -h

#在cephfs的根目录里面创建了一个子目录podtest，k8s以后就可以挂载这个目录 
cd /mnt/k8s_data/
mkdir podtest -p
chmod 0777 podtest/ 
~~~

#### 创建 Secret

~~~sh
#将/etc/ceph/ceph.client.admin.keyring里面的key的值转换为base64
cat /etc/ceph/ceph.client.admin.keyring | base64
W2NsaWVudC5hZG1pbl0KCWtleSA9IEFRQlRScHRseGdlaExSQUFvUFZKbG9zb2Q5dWRQU2F0WW04Q1BnPT0K
~~~

~~~yaml
#创建secret
apiVersion: v1
kind: Secret
metadata:
  name: cephfs-secret
data:
  key: W2NsaWVudC5hZG1pbl0KCWtleSA9IEFRQlRScHRseGdlaExSQUFvUFZKbG9zb2Q5dWRQU2F0WW04Q1BnPT0K
~~~

#### 创建 PV

~~~yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: cephfs-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteMany
  cephfs:
    monitors:
      - 192.168.40.8:6789
    path: /podtest
    user: admin
    readOnly: false
    secretRef:
        name: cephfs-secret
  persistentVolumeReclaimPolicy: Recycle  
~~~

#### 创建 PVC

~~~yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: cephfs-pvc
spec:
  accessModes:
    - ReadWriteMany
  volumeName: cephfs-pv
  resources:
    requests:
      storage: 1Gi
~~~

#### 创建 Pod 挂载 PVC

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: cephfs-pod-1
spec:
  containers:
    - image: nginx
      name: nginx
      imagePullPolicy: IfNotPresent
      volumeMounts:
      - name: test-v1
        mountPath: /mnt
  volumes:
  - name: test-v1
    persistentVolumeClaim:
      claimName: cephfs-pvc
~~~

### Rook 1.12 环境示例

> [!warning] 配置片段的结构
> 下文镜像替换片段有重复 ROOK_CSI_CEPH_IMAGE、两项挤在一行，以及中文冒号；storage.nodes 也不应嵌到 storage.config 下。这些是旧记录中的配置问题，不能直接复制后 apply。应按目标版本的 operator.yaml 和 CephCluster 模板放置字段；Dashboard 的协议与端口也以该版本生成的 Service 为准。

#### 安装 Ceph

参考：[Rook Quickstart Guide](https://rook.github.io/docs/rook/v1.12/Getting-Started/quickstart/#cluster-environments)

- 获取 Rook 部署文件：[rook/rook - GitHub](https://github.com/rook/rook)

~~~sh
unzip rook-master.zip
cd rook-master/deploy/examples/
vim operator.yaml
#修改镜像地址：registry.k8s.io访问速度慢。可以使用阿里云的镜像源：registry.cn-hangzhou.aliyuncs.com/google_containers。
##把下面的镜像地址修改成阿里云的##
# ROOK_CSI_CEPH_IMAGE: "quay.io/cephcsi/cephcsi:v3.7.2"
# ROOK_CSI_REGISTRAR_IMAGE: "registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.7.0"
# ROOK_CSI_RESIZER_IMAGE: "registry.k8s.io/sig-storage/csi-resizer:v1.7.0"
# ROOK_CSI_PROVISIONER_IMAGE: "registry.k8s.io/sig-storage/csi-provisioner:v3.4.0"
# ROOK_CSI_SNAPSHOTTER_IMAGE: "registry.k8s.io/sig-storage/csi-snapshotter:v6.2.1"
# ROOK_CSI_ATTACHER_IMAGE: "registry.k8s.io/sig-storage/csi-attacher:v4.1.0"
##改完之后变成如下##
ROOK_CSI_CEPH_IMAGE: "quay.io/cephcsi/cephcsi:v3.7.2"
ROOK_CSI_CEPH_IMAGE: "registry.cn-hangzhou.aliyuncs.com/google_containers/cephcsi:v3.7.2"   ROOK_CSI_REGISTRAR_IMAGE: "registry.cn-hangzhou.aliyuncs.com/google_containers/csi-node-driver-registrar:v2.7.0"
ROOK_CSI_RESIZER_IMAGE: "registry.cn-hangzhou.aliyuncs.com/google_containers/csi-resizer:v1.7.0"
ROOK_CSI_PROVISIONER_IMAGE: "registry.cn-hangzhou.aliyuncs.com/google_containers/csi-provisioner:v3.4.0"
ROOK_CSI_SNAPSHOTTER_IMAGE: "registry.cn-hangzhou.aliyuncs.com/google_containers/csi-snapshotter:v6.2.1"
ROOK_CSI_ATTACHER_IMAGE: "registry.cn-hangzhou.aliyuncs.com/google_containers/csi-attacher:v4.1.0"
#修改以下字段：
ROOK_ENABLE_DISCOVERY_DAEMON： "true"
#Rook的一个环境变量，用于控制是否启用发现守护程序。发现守护程序是Rook集群中的一个组件，用于检测新的存储设备并将其添加到Rook集群中。
~~~

- 安装 Rook Operator：

~~~sh
kubectl apply -f crds.yaml -f common.yaml -f operator.yaml
kubectl get pods -n rook-ceph
~~~

#### 指定 Ceph 存储节点与磁盘

在 Rook 源码的 `deploy/examples/cluster.yaml` 中选择存储节点和磁盘：

~~~yaml
storage:
  useAllNodes: false
  useAllDevices: false
  #deviceFilter:
  config:
    nodes:
      - name: "master1"
        devices:
        - name: "sdb"
      - name: "node1"
        devices:
        - name: "sdb"
      - name: "node2"
        devices:
        - name: "sdb"
#部署
kubectl apply -f cluster.yaml
~~~

字段说明：

| 字段 | `true` | `false` |
| --- | --- | --- |
| `useAllNodes` | 在所有符合条件的节点上使用存储设备 | 仅使用 `storage.nodes` 指定的节点 |
| `useAllDevices` | 使用所选节点上符合条件的可用设备 | 通过 `devices`、过滤器等显式选择设备 |

这些字段控制 OSD 存储选择，MON、MGR 等组件的放置另行配置。`devices` 中的 `name: sdb` 指定裸盘；原实验为 master1、node1、node2 各增加一块未格式化的 sdb，并建议至少三个节点。生产规划还需要核对副本数和故障域，参见 [Rook 1.12 存储选择](https://rook.io/docs/rook/v1.12/CRDs/Cluster/ceph-cluster-crd/#storage-selection-settings)。

#### 部署 Toolbox

~~~sh
kubectl apply -f toolbox.yaml -n rook-ceph
#等待pod running
kubectl -n rook-ceph exec -it rook-ceph-tools-6adffg7qzsvg-adv -- bash
ceph status
ceph osd status
ceph df
~~~

#### 访问 Dashboard

Rook 默认创建 Dashboard；原实验用 NodePort Service 暴露 MGR 的 Dashboard 端口。

~~~yaml
tee dashboard.yaml <<'EOF'
apiVersion: v1
kind: Service
metadata:
  labels:
    app: rook-ceph-mgr
    ceph_daemon_id: a
    rook_cluster: rook-ceph
  name: rook-ceph-mgr-dashboard
  namespace: rook-ceph
spec:
  ports:
  - name: http-dashboard
    port: 7000
    protocol: TCP
    targetPort: 7000
  selector:
    app: rook-ceph-mgr
    ceph_daemon_id: a
    rook_cluster: rook-ceph
  sessionAffinity: None
  type: NodePort
EOF
~~~

通过 `节点 IP:NodePort` 访问 Dashboard。

- 用户名：`admin`
- 密码：用下面的命令读取实验集群中的 Secret。

    ```sh
    kubectl -n rook-ceph get secret rook-ceph-dashboard-password -o jsonpath="{['data']['password']}" | base64 --decode && echo
    ```

## 来源与相关笔记

- Aspirer2004，2026-09-08：[Ceph 上篇：一套集群三种存储](https://mp.weixin.qq.com/s/upPqxdnsyFAaaIuFldfStQ)。
- Aspirer2004，2026-09-09：[Ceph 下篇：工程与运维成本](https://mp.weixin.qq.com/s/TCW5uLLR7K6wxw6O_lN5JQ)。
- [Ceph 架构文档](https://docs.ceph.com/en/tentacle/architecture/)、[PG 修复说明](https://docs.ceph.com/en/pacific/rados/operations/pg-repair/)。
- [Rook 1.12 Quickstart](https://rook.github.io/docs/rook/v1.12/Getting-Started/quickstart/#cluster-environments)：旧版 Rook 示例的版本参考。
- [[Docker-Kubernetes/k8s-storage/分布式存储全景-架构与发展路线|分布式存储全景]]
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-storage|Kubernetes 存储基础]]
- [[Docker-Kubernetes/k8s-storage/k8s删除PVC后PV数据保护与复用避坑|PV/PVC 数据保护与复用]]
- [[Docker-Kubernetes/k8s-storage/开源存储Longhorn，K8s的轻量块存储|Longhorn]]
- [[Docker-Kubernetes/k8s-storage/开源存储DeepSeek 3FS，AI原生的并行文件系统|DeepSeek 3FS]]
