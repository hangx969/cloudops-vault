---
title: k8s-scaling 与 k8s-storage 来源批量摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/scaling
  - docker-kubernetes/storage
date: 2026-09-15
sources:
  - "[[Docker-Kubernetes/k8s-scaling/helm部署goldilocks]]"
  - "[[Docker-Kubernetes/k8s-scaling/k8s-基于KEDA的弹性能力]]"
  - "[[Docker-Kubernetes/k8s-scaling/k8s-HPA-VPA]]"
  - "[[开源存储CubeFS，分布式存储]]"
  - "[[Docker-Kubernetes/k8s-storage/helm部署nfs-subdir-external-provisioner]]"
  - "[[Docker-Kubernetes/k8s-storage/开源存储Ceph]]"
  - "[[Docker-Kubernetes/k8s-scaling/k8s成本优化方案-FinOps实战]]"
  - "[[Docker-Kubernetes/k8s-storage/k8s删除PVC后PV数据保护与复用避坑]]"
  - "[[Docker-Kubernetes/k8s-storage/让存储故障现形：Kubernetes Volume Health Monitor 原理与生产接入]]"
aliases:
  - k8s-scaling-storage 批量摘要
  - K8s 扩缩容与存储批量摘要
---

## 元信息

- **原始目录**: `Docker-Kubernetes/k8s-scaling/` 与 `Docker-Kubernetes/k8s-storage/`
- **文档数量**: 9 篇正文（扩缩容 4 篇 + 存储 5 篇；两个目录现有 10 篇）
- **领域**: Kubernetes 自动扩缩容（HPA/VPA/KEDA/KServe）与存储生命周期（PV/PVC/StorageClass）及分布式存储（NFS/Ceph/CubeFS）
- **摄入日期**: 2026-04-17

## 摘要

本批次摘要覆盖了 Kubernetes 集群的两大基础能力：自动扩缩容和持久化存储。扩缩容部分系统性介绍了 HPA（水平扩缩）、VPA（垂直扩缩）、KEDA（事件驱动扩缩）和 KServe 模型服务请求指标扩缩容，以及相关部署工具（Goldilocks 资源推荐），从原生能力到模型推理场景形成完整体系，并补充 Kubernetes 1.37 `HPAScaleToZero` 对异步 Worker 的原生缩零实践。存储部分涵盖了从 PV/PVC/StorageClass 生命周期与数据保护，到简单的 NFS 动态供应、企业级分布式存储（Ceph、CubeFS）以及 CSI 卷健康监控的部署与 K8s 集成，为有状态应用提供可靠的数据持久化和故障可观测能力。

## 关键知识点

1. HPA 默认 15 秒控制循环，按 `ceil(currentReplicas × currentMetric / desiredMetric)` 计算副本数，缩容有 300 秒稳定窗口；HPA 与 VPA 可在不同资源或指标维度共存，但禁止同时控制同一 CPU/内存维度。
2. VPA 由 Recommender、Updater、Admission Controller 组成，模式包括 Off/Initial/Recreate/InPlaceOrRecreate/InPlace，Auto 已被上游弃用；Goldilocks 依赖 VPA Recommender 提供推荐值并以 Dashboard 展示。
3. KEDA 分工为 Operator 负责 `0 ↔ 1`、生成的 HPA 负责 `1 ↔ N`；Kubernetes 1.37 Beta `HPAScaleToZero` 可配合 `minReplicas: 0` 与 Object/External 指标原生缩零，但不替代 KEDA 的事件源、认证和 ScaledJob 能力。
4. KServe + vLLM 扩缩容链路为 Predictor Deployment → vLLM `/metrics` → Prometheus → KEDA → External Metrics API → HPA，以 `vllm:num_requests_running + vllm:num_requests_waiting` 为信号；必须确认 `external.metrics.k8s.io` 可用，仅 CRD 就绪并不够。
5. 动态供给 PV 常见默认回收策略为 `Delete`，删除 PVC 可能销毁底层卷；修改 StorageClass 不回溯已有 PV，需逐个 patch `persistentVolumeReclaimPolicy`，删除前按“确认策略 → 创建并验证快照 → 必要时改为 Retain → 删除后检查 PV 与底层卷”执行。
6. 存储选型：nfs-subdir-external-provisioner 替代已归档的 nfs-client-provisioner，exports 需写宿主机网段而非 Pod 网段；Ceph 提供 RBD/CephFS/RGW 三类存储，高可用常见配置为 3 或 5 MON、2 MGR，并按副本与故障域规划 OSD；CubeFS 轻量、云原生友好但不支持块存储。
7. Volume Health Monitor 通过 4 个 CSI RPC 将卷健康写入 `PVC.status.healthStatus`、`Pod.status.volumeHealth` 与 `CSINode.status.storageHealth`，前提是控制平面与 kubelet 开启 feature gate 且 CSI 驱动实现这 4 个 RPC。
8. FinOps 五层降本路径：Right-Sizing → 节点效率（Karpenter、Spot、Topology Spread）→ 调度策略（非生产环境 CronJob 定时开关投入产出比最高、PriorityClass 抢占）→ FinOps 监控（Prometheus 成本告警 + OpenCost）→ 存储网络（GP3 替代 GP2、WaitForFirstConsumer 减少跨 AZ 费用）。

## 各文档摘要

### [[Docker-Kubernetes/k8s-scaling/helm部署goldilocks|Helm 部署 Goldilocks]]

**核心内容**: Goldilocks 是一个开源工具，通过分析 VPA 推荐值帮助确定工作负载的合理 resource request/limit 设置。

- 依赖 VPA Recommender 组件提供资源推荐数据
- 提供 Web Dashboard 可视化展示推荐值
- 支持 `--on-by-default` 为所有 Namespace 创建 VPA 对象
- 可通过 `--exclude-namespaces` 和 `--ignore-controller-kind` 排除特定资源
- 集成 OAuth2 Proxy 实现访问认证

### [[Docker-Kubernetes/k8s-scaling/k8s-基于KEDA的弹性能力|KEDA：事件驱动扩缩容与 KServe 实战]]

**核心内容**: 说明 KEDA 的事件驱动扩缩容原理、与 HPA/原生 Scale-to-Zero 的选型边界、资源模型、多事件源实践，以及 KServe + vLLM 请求指标实战。

- KEDA Operator 负责 `0 ↔ 1`，生成的 HPA 负责 `1 ↔ N`；Kubernetes 1.37 原生 HPA 缩零并未替代 KEDA 的事件源、认证和 ScaledJob 能力
- 核心 CRD：ScaledObject、ScaledJob、TriggerAuthentication 与 ClusterTriggerAuthentication
- 通用实战覆盖 Cron、RabbitMQ、MySQL、Redis 与 Kafka，并提供完整命令和 YAML
- KServe 实战链路：Predictor Deployment → vLLM `/metrics` → Prometheus → KEDA → External Metrics API → HPA
- 实测 KEDA 2.17.2；必须确认 `external.metrics.k8s.io` 可用，只有 CRD 就绪并不够
- 使用 `vllm:num_requests_running + vllm:num_requests_waiting` 驱动 1→2→1，并通过 HAMi DRA 在单 GPU 节点共享 GPU

### [[Docker-Kubernetes/k8s-scaling/k8s-HPA-VPA|K8s 自动扩缩容：HPA、VPA 与 Scale-to-Zero]]

**核心内容**: 按“选型→指标基础→HPA→Scale-to-Zero→VPA→生产治理”介绍 Kubernetes 扩缩容策略，覆盖 Helm 部署 VPA 与 Kubernetes 1.37 原生 HPA Scale-to-Zero。

- 四层体系：HPA 调整 Pod 副本、VPA 调整资源 requests、KPA 按 Knative 并发缩放、Cluster Autoscaler 调整节点容量
- 指标基础：Metrics Server、Resource/Custom/External Metrics API、Helm 与 Manifest 安装、kubeadm kubelet TLS 排障
- HPA：默认 15 秒控制循环、`ceil(currentReplicas × currentMetric / desiredMetric)` 算法、300 秒缩容稳定窗口，以及 CPU/内存/PHP 压测实战
- Scale-to-Zero：Kubernetes 1.37 Beta `HPAScaleToZero`、Object/External 指标、`minReplicas: 0`、冷启动治理、告警和 KEDA 迁移
- VPA：Recommender/Updater/Admission Controller、Fairwinds Helm 与上游脚本安装、nginx/hamster/MySQL 实战
- VPA 模式：除 Off/Initial/Recreate 外补充 InPlaceOrRecreate/InPlace，并标注 Auto 已被上游弃用
- HPA 与 VPA 可以在不同资源或不同指标维度共存；禁止同时控制同一 CPU/内存维度
- 生产治理：PDB、minAllowed/maxAllowed、OOM/JVM/监控空洞、自定义 Recommender 与渐进式落地

### [[开源存储CubeFS，分布式存储|K8s 分布式存储 CubeFS]]

**核心内容**: 对比单节点存储 vs 分布式存储的优劣，详细比较 Ceph 与 CubeFS 两大平台，阐述在 K8s 上落地分布式存储的优势。

- 单节点存储问题：单点故障、性能瓶颈、扩容复杂、仅支持文件存储
- 分布式存储优势：无限扩容、数据冗余、多副本/纠删码、负载均衡、多存储类型
- Ceph vs CubeFS：Ceph 支持块/对象/文件三种存储但部署复杂；CubeFS 轻量级适合云原生但不支持块存储
- K8s 上部署优势：简化管理（Helm IaC）、自动化运维、一键扩展（DaemonSet）、故障自愈

### [[Docker-Kubernetes/k8s-storage/helm部署nfs-subdir-external-provisioner|Helm 部署 NFS Provisioner]]

**核心内容**: 部署 nfs-subdir-external-provisioner 实现 K8s PV 的动态供应，将现有 NFS 服务器对接 StorageClass。

- NFS 服务端部署：安装 nfs-utils、配置共享目录和 exports
- nfs-subdir-external-provisioner：替代已归档的 nfs-client-provisioner
- 支持通过 StorageClass 动态创建 PV，无需手动创建 PV 资源
- 注意 exports 配置需写宿主机网段（非 Pod 网段），因 PV 先挂载到宿主机再挂载到 Pod

### [[Docker-Kubernetes/k8s-storage/开源存储Ceph|Ceph：架构原理、部署与 Kubernetes 集成]]

**核心内容**：CRUSH、RADOS、PG 与 RBD / RGW / CephFS，硬件、BlueStore、故障恢复、运维成本和完整旧版接入示例。

- MON 维护地图和仲裁，MGR 提供管理模块，OSD 存储和恢复数据，MDS 管理 CephFS 元数据
- PG 数可由 autoscaler 调整，Nautilus 起支持 PG 合并；服务 IO 需结合 min_size 和 PG 状态判断
- 部署可以使用 cephadm 或 Rook；故障隔离与维护能力决定是否独立运行存储集群
- 旧版 RBD / CephFS in-tree 插件在 Kubernetes 1.31 被移除，当前使用 Ceph CSI
- 详细内容见 [[KnowledgeBase/sources/ceph-storage-summary|Ceph 来源摘要]]

### [[Docker-Kubernetes/k8s-storage/k8s删除PVC后PV数据保护与复用避坑|删除 PVC 后 PV 数据保护与复用避坑]]

**核心内容**: 解释 PVC 删除后 PV 的回收策略、`Released` PV 复用风险和有状态服务的安全删除流程。

- 动态供给 PV 常见默认策略是 `Delete`，删除 PVC 可能触发 CSI 或云厂商 API 销毁底层卷
- 修改 StorageClass 不会回溯已有 PV，存量数据盘必须逐个检查并 patch `persistentVolumeReclaimPolicy`
- `Retain` 后的 PV 可能停留在 `Released`，清理 `claimRef` 前必须确认旧数据可弃或已有备份
- StatefulSet 的 `volumeClaimTemplates` 同样继承 StorageClass 策略，删除前应使用快照或备份保护数据
- 删除前 SOP：确认策略 → 创建并验证快照 → 必要时改为 Retain → 删除后检查 PV 与底层卷状态

### [[Docker-Kubernetes/k8s-storage/让存储故障现形：Kubernetes Volume Health Monitor 原理与生产接入|K8s Volume Health Monitor：原理与生产接入]]

**核心内容**: 介绍 Kubernetes 1.37 Alpha Volume Health Monitor 如何通过 4 个 CSI RPC 将卷健康状态写入 PVC、Pod 和 CSINode，并接入 Prometheus 告警与谨慎的故障切换流程。

- 控制器侧写入 `PVC.status.healthStatus`，节点侧写入 `Pod.status.volumeHealth` 和 `CSINode.status.storageHealth`
- 前提是控制平面、kubelet 开启 feature gate，且 CSI 驱动实现 4 个健康 RPC
- `Degraded` 与 `Inaccessible` 分级处理，remediation 需要冷却、重试上限和人工确认

## 涉及的概念与实体

- [[KnowledgeBase/concepts/HPA]]: 水平 Pod 自动扩缩容
- [[KnowledgeBase/concepts/VPA]]: 垂直 Pod 自动扩缩容
- [[KnowledgeBase/concepts/KEDA]]: 事件驱动自动扩缩容
- [[KnowledgeBase/concepts/Cluster-Autoscaler]]: 节点级别弹性伸缩
- [[KnowledgeBase/concepts/分布式存储]]: 多节点数据冗余存储架构
- [[KnowledgeBase/concepts/StorageClass]]: K8s 动态存储供应
- [[KnowledgeBase/concepts/PV-PVC]]: 持久卷与持久卷声明
- [[KnowledgeBase/entities/Goldilocks]]: 资源推荐可视化工具
- [[KnowledgeBase/entities/VPA]]: 垂直扩缩容组件
- [[KnowledgeBase/entities/KEDA]]: 事件驱动扩缩器
- [[KnowledgeBase/entities/Metrics-Server]]: K8s 资源指标服务
- [[KnowledgeBase/entities/CubeFS]]: 云原生分布式存储（OPPO 开源）
- [[KnowledgeBase/entities/Ceph]]: 企业级分布式存储系统
- [[KnowledgeBase/entities/NFS]]: 网络文件系统
- [[KnowledgeBase/entities/Knative]]: Serverless 框架（KPA 来源）
- [[KnowledgeBase/concepts/Finalizer]]: PVC/PV 删除过程中的保护钩子
- [[KnowledgeBase/concepts/Observability|Observability]]: CSI 卷健康状态的可观测性入口
- [[KnowledgeBase/entities/Prometheus]]: 采集 vLLM 指标并提供 PromQL 查询

### [[Docker-Kubernetes/k8s-scaling/k8s成本优化方案-FinOps实战|K8s 集群成本优化]]

**核心内容**: K8s 集群成本优化五层体系（Right-Sizing → 节点效率 → 调度策略 → FinOps 监控 → 存储网络），含完整配置和 4 周落地路线图，预期降低 40%-60% 云账单。

- 四大浪费黑洞：过度配置（40%）、空闲资源（30%）、僵尸资源（15%）、碎片化（15%）
- L1 Right-Sizing：VPA 四种模式 + VPA/HPA 黄金组合（VPA 管资源，HPA 管业务指标）+ 集群资源审计脚本
- L2 节点效率：Karpenter vs Cluster Autoscaler 六维对比（5-15 秒扩容/主动 Consolidation/Pod 粒度 Bin-Packing）+ Spot 实例策略（砍 60-70%）+ Topology Spread 多 AZ 分散
- L3 调度策略：非生产环境 CronJob 定时开关（投入产出比最高）+ PriorityClass 资源抢占（关键服务 Never 抢占/批处理可抢占）
- L4 FinOps 监控：Prometheus 5 条成本告警规则（CPU 低利用率/Request 3x 偏差/僵尸 Pod/未绑定 PVC/内存低利用率）+ OpenCost 成本分摊部署
- L5 存储网络：GP3 替代 GP2（便宜 20%）、HDD 替代 SSD（便宜 75%）、WaitForFirstConsumer 减少跨 AZ 费用
- 5 大生产避坑：VPA/HPA 冲突、Karpenter Consolidation 误杀、Spot 雪崩、ResourceQuota 阻止 VPA、监控盲区
- 4 周落地路线图：Week1 VPA Off+OpenCost → Week2 VPA Auto+Karpenter+Spot → Week3 PriorityClass+PDB → Week4 存储网络优化

## 交叉主题发现

1. **扩缩容层次体系**: HPA（Pod 水平） -> VPA（Pod 垂直） -> KEDA（事件驱动） -> Cluster Autoscaler（节点级别），四层扩缩能力从应用层到基础设施层逐步递进。
2. **存储与 CI/CD 依赖**: Jenkins、GitLab 等 CI/CD 工具（k8s-CICD 目录）大量使用 NFS PV/PVC 做持久化存储，NFS Provisioner 的动态供应能力直接支撑了 DevOps 工具链的部署。
3. **Metrics Server 枢纽角色**: HPA 和 VPA 均依赖 Metrics Server 提供资源指标，是扩缩容体系的基础组件。
4. **资源优化闭环**: VPA Recommender 提供推荐值 -> Goldilocks 可视化展示 -> 运维人员调整 request/limit -> HPA 基于 request 计算扩缩比例，形成资源优化闭环。
5. **存储选型权衡**: NFS（简单但非高可用） -> CubeFS（云原生友好但无块存储） -> Ceph（功能全面但运维复杂），三种方案适用于不同规模和复杂度的场景。
6. **存储删除安全边界**: StorageClass 提供供给模板，PV 的 `persistentVolumeReclaimPolicy` 决定具体删除行为；`Retain`、快照和备份共同构成有状态数据的恢复边界。
7. **KEDA 与 Serverless**: KEDA 的缩容到 0 能力与 Knative/KPA 的 Serverless 模式理念一致，反映了事件驱动架构在 K8s 中的深入应用。
8. **推理服务扩缩容信号**: 对 KServe/vLLM 模型服务，`running + waiting` 请求数比 CPU/内存利用率更直接反映推理排队压力，但仍需结合模型加载时间、GPU 调度和 HPA 稳定窗口压测。

## 值得注意

- 版本边界：`HPAScaleToZero` 为 Kubernetes 1.37 Beta（原文注明默认启用），Volume Health Monitor 为 1.37 Alpha，字段与行为仍可能变化，原文建议与存储厂商监控互补、不作为唯一故障判定依据；KEDA 结论基于 2.17.2 实测。
- 文档间不一致：[[Docker-Kubernetes/k8s-scaling/k8s成本优化方案-FinOps实战|K8s 集群成本优化]]仍按 VPA 四种模式讲解，并在第 2 周路线图启用 `Auto`；[[Docker-Kubernetes/k8s-scaling/k8s-HPA-VPA|K8s 自动扩缩容：HPA、VPA 与 Scale-to-Zero]]则标注 `Auto` 已被上游弃用、新配置应改用显式模式。
- 数据安全红线：`Released` PV 清理 `claimRef` 前必须确认旧数据可弃或已有备份；Ceph 需按故障域、恢复窗口和维护能力选择 cephadm 或 Rook，旧版接入示例不能直接用于当前 Kubernetes；卷健康 remediation 需要冷却、重试上限和人工确认。
