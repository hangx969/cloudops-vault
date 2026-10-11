---
title: "开源存储列传第 24 篇 — DeepSeek 3FS，AI原生的并行文件系统"
tags:
  - storage/3fs
  - ai/infrastructure
date: 2026-10-04
author: Aspirer2004
published: 2026-09-25
source_url: "https://mp.weixin.qq.com/s?__biz=Mzg4MjgxNDYwMA==&mid=2247496820&idx=1&sn=57cb683505f97a9b4efac7b5823b533b&chksm=cf524f93f825c685da65fc836abdc4758559466f4dcf258a3ac84ab1c157e4e5a9ce1d8faeec&cur_album_id=4569076918138175489&scene=190#rd"
---

# DeepSeek 3FS，AI原生的并行文件系统

> 原文：Aspirer2004，架构师修仙之路，2026-09-25，开源存储列传第 24 篇。
> 文中性能数字和社区状态来自作者成文时的介绍，其当前适用性需结合目标版本和实际环境判断。

DeepSeek 为什么自己写文件系统，快在哪，复现门槛在哪

2025 年 2 月 28 日，DeepSeek 开源了一个并行文件系统，叫 3FS，全称 Fire-Flyer File System。它是五天开源周的收官项目。原文称，仓库上线几小时后登上 GitHub 趋势榜，是当年关注度最高的存储项目。DeepSeek 以低成本训练大模型出名，外界也关注其集群如何搭建；存储是集群的基础组件之一，开源也让外界有机会了解它的设计。

这个项目的研发顺序与存储领域的常见路径不同。常见路径是先有论文，再有原型，最后进入生产；3FS 则先在 DeepSeek 的训练集群和推理服务里跑了很久，承担 checkpoint 写入、训练数据读取和推理 KVCache 外置，论文和代码一起放出来。设计源头是 2024 年 8 月那篇 Fire-Flyer AI-HPC 的软硬件协同论文（arXiv 2408.14158），3FS 是那套集群设计里的存储层。

本文讨论 DeepSeek 的训练集群到底卡在什么 IO 问题上；3FS 的架构怎么拆；性能数字怎么读，复现要什么条件；它和前面几篇讲过的老一代并行文件系统差在哪；社区拿它做了什么。

## 一、训练集群的三类 IO 难题

大模型训练和推理的存储负载与传统业务明显不同，主要有三类，都会给老式存储带来压力。

**第一类是 checkpoint 写入。** 几千张卡一起训练，必须周期性把模型参数和优化器状态整体存盘，防止故障丢进度。模型越大，一次 checkpoint 越大，几百 GB 到几 TB 是常态。存储写得慢，训练就得停下来等，几千张卡空转，持续产生按小时计费的成本。这类负载要的是突发的大带宽并行写，写完就静默一段时间，过一阵再来一次。

假设一次完整 checkpoint 是 3 TB，存储写速 10 GiB/s，要写五分钟出头。集群每两小时存一次，等待时间占 GPU 时间的比例就有百分之四左右，对几千张卡的集群来说，这百分之四会带来可观的成本。更要紧的是故障恢复：单卡故障后要回滚到上一个 checkpoint 重训，checkpoint 间隔越长，重算浪费越多。因此，在大规模训练中，checkpoint 写速直接影响训练成本。

**第二类是训练数据读取。** 数据加载器要从 PB 级的数据集中随机抽取样本送给 GPU，既要支持高并发随机读，又要避免 GPU 等待数据。数据集放本地盘装不下，放普通网络存储带宽不够，这是训练集群最常见的矛盾。

**第三类是推理的 KVCache 外置。** DeepSeek-V3 用 MLA 结构把 KV 缓存压缩了一个量级，但长上下文、多轮对话累积下来，KVCache 仍会耗尽 GPU 显存。工程上的办法是把不活跃的 KVCache 换出到更便宜的存储层，需要的时候再高速换回来。这是一类高吞吐的读负载，直接决定推理服务能支持多少并发。

![AI 集群的三类 IO 负载](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/04/deepseek-3fs/deepseek-3fs-01-io-workloads.png)

[[Docker-Kubernetes/k8s-storage/assets/deepseek-3fs/deepseek-3fs-01-io-workloads.svg|SVG 矢量源图]]

图：训练与推理的三类 IO 负载，形状各不相同

老一代并行文件系统是为 HPC 的规整读写设计的，对象存储的随机读和 POSIX 语义都弱，本地盘又不能共享。这三种方案都难以满足需求，DeepSeek 因而选择自研文件系统。这也延续了他们的工程传统：DeepSeek 的团队和幻方一脉相承，一直做软硬件协同设计。2024 年 8 月，他们在 arXiv 上发布 Fire-Flyer AI-HPC 论文，公开了整个集群的设计：一万张 GPU 的计算集群，配 180 个存储节点，每个存储节点配 16 块 NVMe SSD 和两块 200Gbps 的 InfiniBand 网卡。3FS 就是这套设计里的存储层，先确定硬件配置，再设计文件系统。

Fire-Flyer 集群有两代演进。第一代集群建于 2021 年前后，第二代扩到万张 GPU 规模。论文里，DeepSeek 逐项说明了集群的设计取舍：如何搭建网络拓扑、为何坚持全闪、为何自研文件系统。其中一个核心结论是，这种软硬件协同设计能明显压低训练集群的总体拥有成本。存储也采用同样的方法：先确定 16 块 SSD、两块 200Gbps 网卡的硬件配置，再据此设计软件，尽量用足带宽。从硬件配置反推软件设计，而不是先写软件再挑硬件，这是 3FS 和市面上多数存储项目的根本差别。

## 二、开源周收官

2025 年 2 月 24 日到 28 日，DeepSeek 连续五天，每天开源一个生产级组件，官方叫 Open Source Week。按顺序：第一天 FlashMLA，Hopper GPU 上的解码注意力内核；第二天 DeepEP，MoE 模型的专家并行通信库；第三天 DeepGEMM，FP8 矩阵乘库；第四天 DualPipe 和 EFLB，双向流水线并行算法和专家负载均衡；第五天就是 3FS，同一天还有个小项目 Smallpond，分布式数据处理框架。

![DeepSeek 开源周（2025 年 2 月）](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/04/deepseek-3fs/deepseek-3fs-02-open-source-week.png)

[[Docker-Kubernetes/k8s-storage/assets/deepseek-3fs/deepseek-3fs-02-open-source-week.svg|SVG 矢量源图]]

图：开源周五天发布顺序，3FS 是收官项目

> [!note] 许可证说明
> 原文和图示将 MIT 概括为“商用无限制”。MIT 允许商业使用，但仍要求在软件副本或实质部分中保留版权声明和许可声明。参见 [3FS LICENSE](https://github.com/deepseek-ai/3FS/blob/main/LICENSE)。

这五个组件覆盖了 DeepSeek 训练和推理链路的各个环节：算子、通信、矩阵乘、流水线、存储，都在生产环境中使用过。许可证也宽松，3FS 用的是 MIT，原文将其概括为“商用没有任何附加条件”。对存储圈来说，这是第一次有一家 AI 实验室把自研的并行文件系统完整开源出来，同时提供代码、设计文档和性能数据。

发布后也引起了广泛关注。仓库当天登上 GitHub 趋势榜，Hacker News 上连挂好几天，随后出现了源码走读、架构拆解和基准复现等技术分析。存储项目很少有这样的热度，平时一个新存储开源，关注者通常以存储领域的工程师为主。3FS 的关注度很大程度上来自 DeepSeek，外界希望从它的文件系统设计中了解低成本训练的原因。开源内容也超出了概念验证：这是一个有设计文档、性能数据和生产使用记录的完整组件。

## 三、架构拆解

3FS 的官方设计文档把系统分成四块：管理服务（mgmt）、元数据服务（meta）、存储服务（storage）、客户端（client）。整体是解耦的：元数据和数据分开扩展，控制面和数据面分开。

![3FS 总体架构](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/04/deepseek-3fs/deepseek-3fs-03-architecture.png)

[[Docker-Kubernetes/k8s-storage/assets/deepseek-3fs/deepseek-3fs-03-architecture.svg|SVG 矢量源图]]

图：3FS 四组件架构，元数据与数据分离

### 元数据：无状态服务加事务数据库

3FS 的元数据服务自己不存状态，目录树、文件属性、chunk 到存储节点的映射，全部以 KV 形式存在 FoundationDB 里。FoundationDB 是苹果的开源分布式事务数据库，提供跨键的强一致事务。这个选型的好处很直接：元数据服务可以随时加实例、随时替换，坏了重启就行，一致性由底下的事务数据库保证。对比老一代系统，Lustre 的 MDS 是有状态的元数据服务器，扩展和故障切换都围绕它做了一整套机制，3FS 则把这一层交给了成熟组件。

选择 FoundationDB 而非自研轻量元数据服务，源于 3FS 的一个基本判断：元数据的一致性是最难做对的部分，目录改名、文件删除、空间回收这些操作天然需要跨多个键的原子事务。自研一套能扛住这些场景的分布式事务层，工作量不小，出错概率还不低。FoundationDB 是被苹果大规模生产验证过的事务数据库，由它处理分布式事务，3FS 专注于把文件系统语义转换为 KV 操作。代价是多了一个外部依赖，运维时也要维护 FoundationDB。这一取舍把事务一致性交给外部组件，将文件系统特有的逻辑留在 3FS 中。

### 数据面：用户态加 RDMA 加 io\_uring 思路

客户端有两条路径。一条是 FUSE 挂载，走内核，兼容性最好，但有内存拷贝开销，官方测试吞吐约每秒 40 万个 4KiB 读请求，折合 1.6 GB/s 左右，可以满足普通文件系统用法，但难以满足高性能场景。另一条是原生客户端，应用通过一个叫 USRBIO 的用户态接口直接发起 IO。

USRBIO 是 3FS 自定义的用户态块 IO 接口，官方设计文档的原话是设计受 Linux io\_uring 启发。应用注册一段共享内存和一个环形队列，IO 请求进入队列，数据在应用内存和存储节点之间直接传输，不经过内核缓冲区，没有多余拷贝。网络层走 RDMA，存储节点访问 NVMe 盘也是用户态异步 IO（据社区源码分析走 io\_uring，项目没有用 SPDK）。从应用到盘，整条数据路径都在用户态和网卡硬件里完成，内核只负责控制面和 FUSE 兼容路径。这就是它快的结构性原因。

![原生客户端的数据路径](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/04/deepseek-3fs/deepseek-3fs-04-native-io-path.png)

[[Docker-Kubernetes/k8s-storage/assets/deepseek-3fs/deepseek-3fs-04-native-io-path.svg|SVG 矢量源图]]

图：原生客户端路径，从应用内存到 NVMe 盘的直通

> [!note] 客户端 IO 路径（截至 2026-10-04）
> 官方文档说明，原生客户端位于 FUSE daemon 内，`open/close/stat` 等元数据操作仍经 FUSE；USRBIO 受 `io_uring` 启发，不等于从应用到磁盘完全绕过内核。当前存储读取代码可在 `libaio` 与 `io_uring` 之间选择，不能把“用户态接口”直接等同于“内核不参与磁盘 IO”。参见 [官方设计文档](https://github.com/deepseek-ai/3FS/blob/main/docs/design_notes.md#asynchronous-zero-copy-api) 与 [AioReadWorker 配置](https://github.com/deepseek-ai/3FS/blob/main/src/storage/aio/AioReadWorker.h)。

### 副本：CRAQ 链复制

数据切成固定大小的 chunk，每个 chunk 放在一条复制链上，链由若干个存储节点组成。3FS 用的是 CRAQ，Chain Replication with Apportioned Queries，链式复制的改进版。写入从链头进，沿链传播到链尾，所有节点都写成功才算提交，这是 write-all；读取可以从链上任意节点读，这是 read-any，用于分散读压力。难点在并发读写：某个节点上有还没传播完的脏版本怎么办？CRAQ 的办法是，读到未提交版本时返回一个特殊状态码，客户端转而去链尾读已提交的版本。这样既保持强一致，也不牺牲读吞吐。

![CRAQ 链复制：写全链，读任意点](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/04/deepseek-3fs/deepseek-3fs-05-craq-replication.png)

[[Docker-Kubernetes/k8s-storage/assets/deepseek-3fs/deepseek-3fs-05-craq-replication.svg|SVG 矢量源图]]

图：CRAQ 的写路径与读路径，强一致下摊开读压力

> [!note] 读路径核对（2026-10-04）
> 上文和图示中的“转向链尾读取”与官方实现说明不同。官方文档明确写到，3FS 不向链尾查询版本；节点同时持有 committed 和 pending 版本时返回特殊状态，客户端可以等待后重试，或显式发起 relaxed read 获取 pending 版本。后者与读取已提交版本的语义不同。参见 [官方数据复制说明](https://github.com/deepseek-ai/3FS/blob/main/docs/design_notes.md#data-replication)。

### 数据放置：链与组合设计

chunk 映射到 target，target 组成 chain，一张链表（chain table）定义整个集群的数据分布。放置算法用了一个组合数学里的设计，叫平衡不完全区组设计（balanced incomplete block design），作用是保证任意一块盘挂掉之后，重建流量能均匀摊到剩下的盘上，避免少数磁盘被重建流量占满。物理规模上，180 个存储节点、2880 块 NVMe SSD，含副本的有效容量在 20 PiB 以上。

关于副本开销，作者认为 3FS 并非依靠大量副本堆叠磁盘：链复制里一个 chunk 通常只有两三个副本，空间效率比全副本高，恢复速度也比传统的整盘重建快。这一设计依赖磁盘不会大面积同时故障，单盘故障后可快速从复制链补齐数据。对于全闪集群，盘的平均无故障时间相对稳定，这种细粒度的链式冗余比整盘镜像更划算。这也是它和传统 HPC 文件系统的一个区别：老系统多半依赖底下的 RAID 保证盘坏了数据不丢，文件系统自己不管冗余，3FS 则在自身数据面处理冗余。

![数据放置：从文件到盘](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/04/deepseek-3fs/deepseek-3fs-06-data-placement.png)

[[Docker-Kubernetes/k8s-storage/assets/deepseek-3fs/deepseek-3fs-06-data-placement.svg|SVG 矢量源图]]

图：文件到盘的放置链路，放置算法保证故障时流量均衡

## 四、性能数字怎么读

3FS 公开的性能数字不少，读的时候要把口径分清楚：哪个测试、什么配置、有没有背景流量。下面这张表把官方口径列全。

| 测试项 | 集群配置 | 官方宣称 | 出处 |
| --- | --- | --- | --- |
| 聚合读吞吐 | 180 存储节点（2×200Gbps IB，16×14TiB NVMe）+ 500 多个客户端，带训练背景流量 | 约 6.6 TiB/s | GitHub README |
| 集群读吞吐实测 | Fire-Flyer 2 集群（网络出口 9 TB/s） | 实测读 8 TB/s | arXiv 2408.14158 |
| checkpoint 写 | 单个存储节点 | 10 GiB/s | arXiv 2408.14158 |
| KVCache 峰值读 | 单客户端（1×400Gbps 网卡） | 最高 40 GiB/s | GitHub README |
| GraySort 排序 | 25 存储节点（2×400Gbps）+ 50 计算节点，110.5 TiB 数据 | 30 分 14 秒，平均 3.66 TiB/min | GitHub README |

![带宽怎么堆到 6.6 TiB/s](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/04/deepseek-3fs/deepseek-3fs-07-bandwidth.png)

[[Docker-Kubernetes/k8s-storage/assets/deepseek-3fs/deepseek-3fs-07-bandwidth.svg|SVG 矢量源图]]

图：从单盘到集群的带宽堆叠，配比是关键

高吞吐的原理并不复杂：NVMe 盘的单盘带宽早就过了 GB/s 级别，16 块盘并起来，单机网络会先达到带宽上限。瓶颈从盘移到了网络，3FS 的目标是充分利用网络带宽：用户态去掉内核拷贝，RDMA 绕过 TCP/IP 协议栈，通过批量并发充分利用队列。表中第一行的 6.6 TiB/s 是带训练背景流量测出来的聚合读，不是空集群压测的峰值。

原文提到，有工程师按硬件规格核算过这些数据：180 节点的双 200Gbps 网卡，网络出口总带宽可以计算，6.6 TiB/s 大约用了可用带宽的七成多，峰值工况约八成多。作者据此认为，这些数字接近硬件理论上限，没有明显夸大的迹象。

复现也有较高的硬件门槛。要复现 README 里的基准测试，需要约 500 个客户端节点（各配 200Gbps 网卡）和 180 个存储节点（各配 16 块 14TB NVMe 和两块 200Gbps 网卡），外加全套 InfiniBand 交换网络。全球能凑出这套环境的机构屈指可数。另外，官方基准没有公布延迟数据，KVCache 测试也没写全硬件配置。对多数团队来说，阅读架构、学习设计比复现整套集群更现实。

GraySort 是另一种测试口径。它是大数据领域的经典基准：把一大堆随机数据排好序，过程中数据要全量读入、打散、再全量写回，同时考察读写带宽。3FS 用的不是那套 180 节点集群，而是 25 个存储节点加 50 个计算节点，110.5 TiB 数据 30 分 14 秒排完，平均 3.66 TiB/min。这一结果也说明 3FS 能支持通用大数据处理负载。作者认为，它在传统基准上的表现，说明底层数据面具有通用性，并非只靠 AI 场景的特殊优化。

## 五、与老一代并行文件系统的差异

本系列第 01 篇《Lustre，HPC并行文件系统的元老》、第 02 篇《BeeGFS，走易用路线的并行文件系统》、第 03 篇《DAOS，为NVMe和RDMA重做一套存储》讲过上一代。将 3FS 加入对照，可以看到几种设计的差异。

| 维度 | Lustre（1999） | DAOS（2019 开源） | 3FS（2025） |
| --- | --- | --- | --- |
| 设计年代背景 | HDD 集群，聚合盘带宽 | NVMe + Optane + RDMA | 全闪 + 200Gbps RDMA + AI 负载 |
| 客户端形态 | 内核模块 | 用户态 SDK | 用户态原生 + FUSE 兼容 |
| 元数据 | 有状态 MDS | 分布式对象索引 | 无状态服务 + FoundationDB |
| 数据冗余 | 依赖 RAID 等外部手段 | 副本与纠删码 | CRAQ 链复制 |
| 主要场景 | HPC 仿真、超算 | HPC、AI 集群 | AI 训练与推理 |
| 演进方式 | 在老架构上打补丁 | 重写，但依赖的介质（Optane）退场 | 无包袱，直接为 AI 负载新建 |

![并行文件系统的三代](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/04/deepseek-3fs/deepseek-3fs-08-filesystem-generations.png)

[[Docker-Kubernetes/k8s-storage/assets/deepseek-3fs/deepseek-3fs-08-filesystem-generations.svg|SVG 矢量源图]]

图：三代并行文件系统，介质换代驱动架构重做

Lustre 和 BeeGFS 出生时，盘是机械硬盘，单盘一百多 MB/s，系统设计的核心命题是把成百上千块盘聚合成大带宽，客户端做成内核模块是当时的合理选择。到了全闪时代，单盘几个 GB/s，老架构的内核路径、元数据单点、TCP 传输，都成为瓶颈，需要逐步改进。DAOS 是 Intel 为 NVMe 加 RDMA 做的第一次重写，作者认可这一思路，但认为 Optane 持久内存停产削弱了它的硬件基础。3FS 是第二次重写，这次没有押特殊介质，就是普通 NVMe 加 InfiniBand，负载目标也收窄到 AI 训练推理这一件事上。收窄负载目标，也让每一层都能围绕这一场景简化设计。

3FS 有两个值得关注的技术决策。一是元数据引擎外置。老系统通常自行管理元数据，3FS 证明外置反而降低了造新系统的门槛，事务层换一家供应商就能适配。二是数据路径只做一种形态：高性能路径只有 USRBIO 加 RDMA，FUSE 明确定位为兼容附件。两条路径分工明确，便于集中工程投入。作者认为，不少老系统的性能负担来自同时兼顾过多场景。

## 六、落地情况与社区动作

DeepSeek 是 3FS 的首个用户。官方给出的四个使用场景，正好对应前面说的负载：数据准备（分析流水线的中间产物，按层级目录组织）、数据加载器（训练样本随机读，不再需要预取和预洗牌）、checkpoint（大模型并行存盘，论文里写单节点写入 10 GiB/s，一次存盘几秒完成）、推理 KVCache 外置（比 DRAM 缓存便宜，容量大，吞吐能够满足需求）。DeepSeek-V3 的推理服务在显存紧张时把 KVCache 换出到这套磁盘存储，需要时再换回，这一用法在开源前就已用于生产。

![KVCache 的多级放置](https://raw.githubusercontent.com/hangx969/upload-images-md/main/2026/10/04/deepseek-3fs/deepseek-3fs-09-kv-cache-tiers.png)

[[Docker-Kubernetes/k8s-storage/assets/deepseek-3fs/deepseek-3fs-09-kv-cache-tiers.svg|SVG 矢量源图]]

图：KVCache 多级缓存，3FS 接磁盘层

社区的集成工作主要集中在推理框架的 KVCache 外置上。据公开报道：月之暗面（Moonshot AI）的推理服务平台 Mooncake 给自家的 Mooncake Store 做了一个实验性的 3FS USRBIO 适配器，把 3FS 当作 GPU 显存、CPU 内存之后的第三级磁盘层；KVCache 管理组件 LMCache 的存储后端列表里也有 3FS；vLLM 和 SGLang 的使用者可以通过 Mooncake 这类多级缓存间接用上 3FS。这些集成都利用了 3FS 的大吞吐读取能力，将它用作推理侧的冷数据存储。国内也有存储厂商公开宣布对 3FS 的兼容或复现实践，同样按公开报道对待。

截至原文成文时，仓库还没有正式的版本号发布，提交数在一百多这个量级，设计文档齐备但运维资料偏薄，社区的实操经验集中在拥有全闪 RDMA 集群的团队。中小规模团队尝试部署时，首先需要具备适用的 InfiniBand 网络和 NVMe 磁盘，软件本身并非第一道门槛。

## 七、意义与局限

作者认为，3FS 的意义主要有三点。

第一，它证明 AI 实验室可以从算子、通信、调度一路自研到存储，然后把整条链路开源。存储开源的玩家名单里，以前是存储厂商和基金会项目，现在多了 AI 实验室。提出需求与开发软件的是同一团队，作者认为这会改变迭代速度。

第二，它给全闪加 RDMA 时代的并行文件系统提供了一个参考实现。无状态元数据服务加事务数据库、链复制、用户态零拷贝数据面，这三项设计都可以分别借鉴，用到其他系统中。

第三，它把 KVCache 外置从论文里的概念变成了有真实生产数据的工程件。推理侧的存储需求从这一年开始被认真对待。

放在整个系列的脉络里看，3FS 是年份最晚的一篇，却是第三波浪潮逻辑最清楚的样本：新负载逼出新架构。HPC 逼出了 Lustre，大数据逼出了 HDFS，AI 训练逼出了 3FS。介质、网络与负载变化，推动了文件系统的重新设计。作者据此判断，AI 负载将定义存储的下一个十年，并将 3FS 视为这一判断的首个实证。

选型时也需要考虑以下局限。

- **不是通用文件系统。**
	POSIX 支持有限，权限、快照、配额这类通用功能不在它的设计清单里，它面向 AI 负载设计。
- **场景绑定 AI。**
	它擅长大吞吐读写，元数据密集的小文件负载不是强项，元数据操作要走 FoundationDB 事务，延迟特性和本地缓存型方案不在一个量级。
- **硬件绑定。**
	没有 200Gbps 级别的 RDMA 网络和大规模 NVMe 盘阵，性能优势出不来，退化成一套普通的分布式文件系统，还多了运维成本。
- **社区还年轻。**
	没有版本发布节奏，生态薄，生产采用前需要自行验证故障场景。

> [!note] 功能边界核对（2026-10-04）
> 原文把权限列为不在设计清单中的功能，但官方 inode 结构包含 ownership 与 permissions；官方还描述了用软链接、硬链接构造轻量数据集快照的用法。这不能替代对完整 POSIX 语义、快照和配额能力的逐项检查，也不能据此概括为“完全没有权限或快照”。参见 [文件接口](https://github.com/deepseek-ai/3FS/blob/main/docs/design_notes.md#file-system-interfaces) 与 [元数据结构](https://github.com/deepseek-ai/3FS/blob/main/docs/design_notes.md#file-metadata-on-transactional-key-value-store)。

作者将 3FS 视为 AI 时代首个经过生产验证的开源并行文件系统，认为它集中解决了存储如何跟上万卡集群 IO 需求的问题。上一篇《Fluid，K8s上的数据加速编排》讲的是站在计算和存储中间做加速，3FS 则按 AI 负载重新设计存储底座，专注于这一场景。

IPFS 和 Filecoin 关注另一个问题：如何让数据不归任何单一方管理，并按内容本身查找。
