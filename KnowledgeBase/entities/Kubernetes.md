---
title: Kubernetes
tags:
  - knowledgebase/entity
  - docker-kubernetes
date: 2026-10-23
sources:
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/MetalLB实战-裸机Kubernetes-LoadBalancer]]"
  - "[[KnowledgeBase/sources/k8s-node-swap-summary]]"
  - "[[KnowledgeBase/sources/k8s-cluster-autoscaler-summary]]"
  - "[[KnowledgeBase/sources/argocd-sync-troubleshooting-summary]]"
  - "[[KnowledgeBase/sources/k8s-basic-resources-batch-summary]]"
  - "[[KnowledgeBase/sources/kubectl-server-side-apply-summary]]"
  - "[[KnowledgeBase/sources/k8s-installation-management-batch-summary]]"
  - "[[KnowledgeBase/sources/kubectx-kubens-multi-cluster-summary]]"
  - "[[KnowledgeBase/sources/k8s-monitoring-logging-batch-summary]]"
  - "[[KnowledgeBase/sources/k8s-CICD-batch-summary]]"
  - "[[KnowledgeBase/sources/kustomize-base-overlay-summary]]"
  - "[[KnowledgeBase/sources/k8s-networking-service-mesh-batch-summary]]"
  - "[[KnowledgeBase/sources/k8s-security-auth-batch-summary]]"
  - "[[KnowledgeBase/sources/k8s-scaling-storage-batch-summary]]"
  - "[[KnowledgeBase/sources/k8s-volume-health-monitor-summary]]"
  - "[[KnowledgeBase/sources/k8s-db-middleware-UI-batch-summary]]"
  - "[[KnowledgeBase/sources/kubectl-krew-plugins-summary]]"
  - "[[KnowledgeBase/sources/k8s-misc-batch-summary]]"
  - "[[KnowledgeBase/sources/dragonfly-harbor-p2p-distribution-summary]]"
  - "[[KnowledgeBase/sources/k8s-cgroup-v2-summary]]"
  - "[[KnowledgeBase/sources/k8s-backup-dr-summary]]"
  - "[[KnowledgeBase/sources/k8s-pdb-summary]]"
  - "[[KnowledgeBase/sources/k8s-nvidia-device-plugin-summary]]"
  - "[[KnowledgeBase/sources/k8s-probe-restart-storm-summary]]"
  - "[[KnowledgeBase/sources/kserve-vllm-inferenceservice-summary]]"
aliases:
  - "K8s"
---

# Kubernetes

## 简介

Kubernetes（K8s）是容器编排平台，源自 Google Borg 系统，2014 年开源，2018 年从 CNCF 毕业。本仓库 Docker-Kubernetes 目录共 174 篇，其中 Kubernetes 相关 **160 篇**（其余 14 篇为 `docker/`），覆盖了 K8s 全生命周期，包括基础资源、集群安装与管理、监控日志、CI/CD、网络与服务网格、安全认证、扩缩容、存储、数据库中间件、UI 工具、备份恢复、GPU 配置、认证考试等主题。全部源文档的详细摘要见上方 `sources` 中列出的批量与增量摘要页面。下文各小节篇数按对应子目录统计（原统计日期 2026-09-29；总数与 CI/CD 增量于 2026-10-04 按现有文件复核；总数、安装管理与网络目录于 2026-10-20 复核；2026-10-23 新增独立健康探针文章后复核总数与基础资源目录），杂项专题含 helm、配置管理、镜像管理、CKA/CKS、KubeBlocks、容器平台、SpringCloud、GPU 子目录及根目录简历指南。

## 核心功能：核心架构知识

### 控制平面与数据平面
- **API Server**：所有组件通信的中枢，唯一与 etcd 交互的组件
- **Scheduler**：监听未绑定节点的 Pod 并执行调度算法，支持 NodeResourceFit 插件的三种评分策略（LeastAllocated、MostAllocated、RequestedToCapacityRatio）
- **Controller Manager**：运行控制器循环，管理 Deployment、StatefulSet、DaemonSet 等工作负载的期望状态
- **etcd**：分布式键值存储，高可用需至少 3 节点，故障恢复通过 `etcdctl member remove/add` 实现
- **kubelet**：节点代理，管理 Pod 生命周期，默认日志限制 containerLogMaxSize 10Mi / containerLogMaxFiles 5
- **kube-proxy**：三种模式（Userspace、iptables、IPVS），IPVS 基于哈希表性能更优；v1.29 引入 nftables（Alpha）

### 声明式资源模型
- 所有资源通过 YAML 定义期望状态，由控制器自动实现：apiVersion、kind、metadata、spec、status
- **Server-side Apply**：API Server 通过 `managedFields` 记录字段所有权；相比依赖 last-applied 三路合并的 Client-side Apply，它会把 kubectl、Helm、Argo CD、Operator 等多管理器之间的字段争用显式报告为冲突，详见 [[k8s基础-yaml-apply#kubectl apply：Client-side Apply 与 Server-side Apply]]
- **Pause 容器**：常见 Linux 运行时借助 Pod sandbox 维持共享命名空间，容器可通过 localhost 互访；存储共享依赖显式挂载同一个 Volume
- **Operator = CRD + Controller**：无需修改 K8s 源码即可扩展 API，适合复杂有状态应用管理
- **PodDisruptionBudget（PDB）**：自愿中断（drain/滚动更新/升级）时的可用性保护，通过 `minAvailable` 或 `maxUnavailable` 约束同时不可用的 Pod 数量，详见 [[Docker-Kubernetes/k8s-basic-resources/k8s-PodDisruptionBudget实战]]
- **健康探针分工**：Startup 隔离启动阶段，Readiness 控制摘流，Liveness 仅处理重启能够修复的进程内部故障；外部依赖抖动不应直接触发容器重启，详见 [[Docker-Kubernetes/k8s-basic-resources/k8s基础-健康探针]]
- **多集群上下文管理**：context 绑定 cluster、user 和 namespace；kubectx/kubens 简化切换，kube-ps1 暴露当前位置，但真正的生产权限边界仍是独立凭证和 RBAC，详见 [[Docker-Kubernetes/k8s-installation-management/k8s多集群kubeconfig管理#kubectx 与 kubens：多集群快速切换]]

### 网络体系三层协同
- **裸机 LoadBalancer**：MetalLB 将 VIP 分配与宣告分开；Layer2 为单 VIP 提供单节点入口和故障接管，BGP 配合路由器 ECMP 提供多节点入口，两者的接管时间与连接恢复都需要实际验证
- **Calico**（底层网络连通性）：IPIP 模式隧道封装配置简单，BGP 模式直接路由性能更优
- **Service**（四层负载均衡）：通过标签选择器匹配 Pod，iptables/IPVS 转发规则
- **Ingress**（七层负载均衡）：流量直接从 Ingress Controller 到 Pod，不经过 Service；生产推荐独占节点 + hostNetwork:true + 前端网关

### 容器运行时演进
- CRI 标准化接口支持 containerd、CRI-O、Kata 等运行时
- 调用链：K8s -> containerd -> RunC
- K8s 1.24+ 全面转向 containerd，从 Docker 迁移步骤：cordon/drain -> 卸载 Docker -> 安装 containerd -> 修改 kubelet 配置

### cgroup v2 资源隔离（详见 [[KnowledgeBase/sources/k8s-cgroup-v2-summary|cgroup v2 摘要]]）
- K8s v1.25 GA 支持 cgroup v2，v1.27 MemoryQoS 特性 Beta 默认开启
- cgroup v2 采用统一层次树，kubelet + containerd 必须同时使用 `systemd` cgroupDriver
- CPU Burst（内核 5.14+）解决 v1 固定窗口 throttle 问题，P99 延迟降低 30%-50%
- memory.high 双层限制：`memory.min = requests`、`memory.high = requests * 0.9`、`memory.max = limits`
- 生产迁移：先在非核心节点验证，通过 NodeAffinity 标签隔离 v1/v2 节点，逐步扩大

## 使用场景

- **生产级集群建设与容灾**：用 kubeadm 或二进制方式部署高可用集群，配置 etcd 高可用与故障恢复，跨地域采用两地三中心或异地多活（Karmada、智能 DNS/GTM）；etcd 快照、Velero 与应用数据备份构成三层容灾
- **云原生应用交付**：GitLab 提交 → Jenkins/Tekton 构建 → Harbor 推送镜像 → K8s 部署，或由 ArgoCD 以 GitOps Pull 模式交付，Kustomize Base + Overlay 管理环境差异
- **可观测性平台**：Prometheus、Grafana、Alertmanager 负责指标与告警，EFK 或 Loki 收集日志，SkyWalking、Jaeger 做链路追踪
- **有状态中间件托管**：用原生 YAML、Helm Chart 或 Operator 部署 MySQL、PostgreSQL、Redis、MongoDB、Kafka
- **AI 推理服务**：在 GPU 节点上用 KServe InferenceService 部署 vLLM，并通过 KEDA 按请求指标扩缩容

## 在本仓库中的覆盖：知识覆盖地图

### 基础资源（26 篇）
详见 [[KnowledgeBase/sources/k8s-basic-resources-batch-summary|k8s-basic-resources 批量摘要]]

覆盖 Pod、Deployment（滚动更新 maxSurge/maxUnavailable）、StatefulSet（Headless Service + volumeClaimTemplates）、DaemonSet、Job/CronJob、Service、Ingress、ConfigMap/Secret、Storage（EmptyDir/HostPath/NFS/PV/PVC）、Namespace 资源分配（ResourceQuota/LimitRange）、Calico 网络、kubeadm 集群搭建、容器运行时 containerd、CRD/Operator、认证授权 RBAC、临时容器 Ephemeral、YAML 编写规范、Python K8s API 编程、Finalizer 资源删除生命周期机制。

**核心要点**：
- Deployment 仅 `spec.template` 变化才触发更新，产生新 ReplicaSet
- StatefulSet 基于 Headless Service 为 Pod 分配固定 DNS：`pod-name.svc-name.ns.svc.cluster.local`
- 生产环境必须对每个 Namespace 限制 Pod/RS 数量，防止异常激增拖垮集群
- K8s 1.24 后不再自动为 ServiceAccount 创建 Secret，需手动创建 Token

### 安装与管理（21 篇）
详见 [[KnowledgeBase/sources/k8s-installation-management-batch-summary|k8s-installation-management 批量摘要]]

覆盖 k8s 1.20 至 1.35 多版本 kubeadm 安装（CentOS -> Rocky Linux 迁移路径）、二进制安装高可用集群（keepalived + nginx）、企业级高可用集群规划、etcd 高可用配置与故障恢复、两地三中心与异地多活架构（Karmada、智能 DNS/GTM）、生产环境优化最佳实践、容器运行时迁移与版本升级、故障排查指南，以及 kubectx/kubens、kube-ps1、OIDC 登录和多文件合并等多集群 kubeconfig 管理实践。

**核心要点**：
- 生产环境控制节点资源：0-100 节点用 8C+32G，100-250 用 16C+32G，250-500 需 etcd 分离
- 3 master 可管理约 900 个 worker 节点
- Pod 状态排查：Pending（资源/调度问题）、ImagePullBackOff（镜像问题）、CrashLoopBackOff（代码/权限问题）、Evicted（资源不足）
- kubeadm 配置 API 演进：v1beta2 -> v1beta3 -> v1beta4
- NodeSwap 自 Kubernetes v1.34 稳定，默认仍为 `NoSwap`；`failSwapOn: false` 仅放行 kubelet 启动，符合条件的 Burstable 容器使用 swap 还需 `memorySwap.swapBehavior: LimitedSwap`。调度器不将 swap 计入可调度内存。
- [[Docker-Kubernetes/k8s-installation-management/k8s-NodeSwap-配置与验证|NodeSwap 配置与验证]]：k3s drop-in、QoS 与 request/limit 边界、逐节点上线，以及 configz、节点容量、使用量和容器 cgroup 四项检查；区分 Homelab 操作与官方控制平面建议。

### 监控与日志（20 篇）
详见 [[KnowledgeBase/sources/k8s-monitoring-logging-batch-summary|k8s-monitoring-logging 批量摘要]]

**监控**：[[KnowledgeBase/entities/Prometheus|Prometheus]] 基础与多版本部署、联邦集群、Helm 部署 kube-prometheus-stack 全家桶、Alertmanager 告警、监控 K8s 系统组件/外部集群/非云原生应用、[[KnowledgeBase/entities/Grafana|Grafana]] 可视化。

**日志**：EFK/ELK 多种部署形态（K8s 容器化、二进制、ECK Operator）、Loki+Promtail 轻量方案、K8s Events 持久化。

**链路追踪**：SkyWalking（低侵入字节码注入）和 Jaeger（CNCF 项目，Uber 开源）。

**核心要点**：
- Prometheus 存储效率：每采样 3.5 bytes，300 万时间序列 30s 间隔 60 天约 200G
- 日志收集器轻量化趋势：Logstash -> Fluentd -> Filebeat/Fluent-bit
- EFK 适合 TB 级大规模日志，Loki 适合轻量级场景
- Kafka 作为缓冲层解决高吞吐日志延迟：Fluentd -> Kafka -> Logstash -> ES

### CI/CD（25 篇）
详见 [[KnowledgeBase/sources/k8s-CICD-batch-summary|k8s-CICD 批量摘要]] 与 [[KnowledgeBase/sources/argocd-sync-troubleshooting-summary|同步故障排查增量摘要]]

覆盖 [[KnowledgeBase/entities/ArgoCD|ArgoCD]]（GitOps 持续交付、Image Updater、DNS 与同步故障排查）、[[KnowledgeBase/entities/Jenkins|Jenkins]]（多版本部署、Pipeline 语法、DevOps 平台落地）、Tekton（云原生 Pipeline）、[[KnowledgeBase/entities/Kustomize|Kustomize]]（Base+Overlay 配置定制）、GitHub Actions（Self-hosted Runner）、多语言应用发布（Go/Python/Java）。

**核心要点**：
- GitOps（ArgoCD Pull 模式）vs 传统 CI/CD（Jenkins Push 模式）两种部署哲学
- 通用发版流程：GitLab 提交 -> Jenkins 构建 -> Docker 镜像 -> Harbor 推送 -> K8s 部署
- Tekton 核心优势：云原生、标准化 CRD、事件驱动，Pipeline 直接映射为 K8s Pod
- Kustomize 通过 Base 复用公共资源、Overlay 描述环境差异；部署前应依次渲染、比较并应用最终清单
- 云原生演进：Jenkins（VM 时代）-> Tekton（K8s 原生）-> ArgoCD（GitOps）

### 网络与服务网格（8 篇）
详见 [[KnowledgeBase/sources/k8s-networking-service-mesh-batch-summary|k8s-networking-service-mesh 批量摘要]] 与 [[KnowledgeBase/sources/metallb-loadbalancer-summary|MetalLB LoadBalancer 实战摘要]]

覆盖 Ingress-Nginx 部署（hostNetwork + ClusterFirstWithHostNet）、External-DNS 域名自动同步、[[KnowledgeBase/entities/Istio|Istio]] 多版本部署与流量管理（熔断/超时/重试）、企业项目接入 Istio 实战、集群网络安全工具（kube-bench、kube-hunter、kubeaudit、Polaris）。

**核心要点**：
- 南北流量（Ingress-Nginx）vs 东西流量（Istio）协同工作
- [[Docker-Kubernetes/k8s-networking-service-mesh/MetalLB实战-裸机Kubernetes-LoadBalancer]]：安装、地址池、Layer2 / BGP 宣告、nginx 外部验证、多地址池及 Calico BGP 共存；仅有 EXTERNAL-IP 不代表服务已经可达
- Istio 1.5+ 将 Pilot/Mixer/Citadel 整合为 istiod 单体
- 服务网格 vs SpringCloud/Nacos：语言无关、无需侵入业务代码
- CVE-2019-5736：Docker 18.09.2 以下 runC 漏洞可提权

### 安全与认证（9 篇）
详见 [[KnowledgeBase/sources/k8s-security-auth-batch-summary|k8s-security-auth 批量摘要]]

覆盖 Capsule 多租户管理、Cert-Manager 证书自动化（ACME/Let's Encrypt）、External Secrets（Azure Key Vault 同步）、Kyverno 策略引擎、OAuth2 Proxy 身份认证、SonarQube 代码质量扫描、Trivy Operator 镜像漏洞扫描、Security Context 容器安全上下文。

**核心要点**：
- 安全工具链：Kyverno（准入控制）+ Trivy（镜像扫描）+ SonarQube（代码扫描）构成从代码到运行时的完整安全防线
- [[KnowledgeBase/entities/Cert-Manager|Cert-Manager]] 核心资源：Issuer/ClusterIssuer → Certificate/CertificateRequest → Order/Challenge → TLS Secret；覆盖 HTTP01/DNS01 与自动续期
- Capsule Tenant：一组 Namespace 的逻辑分组，RBAC + ResourceQuota + NetworkPolicy 策略隔离
- Security Context：UID/GID 管理 + Capabilities（drop ALL + 按需 add）+ 特权模式禁止 + sysctl + seccomp + Pod 安全标准三级策略

### 扩缩容与存储（13 篇）
详见 [[KnowledgeBase/sources/k8s-scaling-storage-batch-summary|k8s-scaling-storage 批量摘要]] 与 [[KnowledgeBase/sources/k8s-cluster-autoscaler-summary|Cluster Autoscaler 节点扩缩容摘要]]

**扩缩容四层体系**：HPA（Pod 水平，基于 CPU/内存）-> VPA（Pod 垂直，调整 request/limit）-> KEDA（事件驱动，支持缩容到 0）-> Cluster Autoscaler（节点级别弹性）。Goldilocks 提供 VPA 推荐值可视化。

**存储基础与方案**：PV/PVC/StorageClass 负责持久化资源的声明与供给；NFS（简单但非高可用）-> CubeFS（云原生友好但无块存储）-> Ceph（功能全面但运维复杂，支持 RBD/CephFS/RADOS Gateway 三种类型）。

**核心要点**：
- HPA 基础算法：`ceil(currentReplicas × currentMetricValue / desiredMetricValue)`；默认同步周期 15 秒、缩容稳定窗口 300 秒，扩容默认无稳定窗口
- KEDA 支持数十种外部事件源（Kafka、RabbitMQ、HTTP、Cron 等），独特优势是缩容到 0
- Ceph 生产环境强烈建议二进制安装在服务器上，不要装在 K8s 中
- NFS exports 配置需写宿主机网段（非 Pod 网段），因 PV 先挂载到宿主机再挂载到 Pod
- 动态供给 PV 的 `Delete` 策略可能在删除 PVC 时销毁底层云盘；重要数据应使用 `Retain` 并在删除前确认快照或备份
- 修改 StorageClass 不会回溯修改存量 PV；`Released` PV 复用前要审查 `claimRef` 和旧数据，StatefulSet 也要审查级联删除行为
- KServe 可将 vLLM `running + waiting` 请求数交给 KEDA，再通过 External Metrics API 驱动 HPA，示例验证了模型服务 `1 -> 2 -> 1` 的请求指标扩缩容
- KServe InferenceService Standard 将模型来源、Runtime、GPU 资源与 Gateway API 入口收敛为声明式服务；完整部署见 [[AI/企业级私有化大模型/一个 Deployment 就能跑 vLLM，为什么还需要 KServe？|为何用 KServe 管理 vLLM 推理服务？]]
- Kubernetes 1.37 的 `HPAScaleToZero` 允许原生 HPA 基于 External/Object 指标将异步 Worker 缩到 0；从 0 拉起的冷启动、指标源可用性和就绪探针决定生产边界
- KEDA 与原生 HPA 不能同时管理同一个 Deployment；KEDA 适合直接连接事件源，原生 HPA 适合已有 External 指标链路的场景
- Volume Health Monitor 通过 4 个 CSI RPC 将卷健康写入 `PVC.status.healthStatus`、`Pod.status.volumeHealth` 和 `CSINode.status.storageHealth`，补足 PVC 长期 `Bound` 但底层已降级的可观测性盲区
- 该特性以 Kubernetes 1.37 Alpha 为前提，必须同时验证 feature gate 与 CSI 驱动版本，并把 `Degraded`/`Inaccessible` 分级接入告警和 remediation

- [[KnowledgeBase/entities/Cluster Autoscaler|Cluster Autoscaler]] 基于 requests 和调度约束判断新增节点能否解决 Pending；回收节点前检查 PDB、本地存储和迁移条件。部署、排障与上线回滚见 [[Docker-Kubernetes/k8s-scaling/K8s Cluster Autoscaler|节点自动扩缩容实践]]。

### 数据库中间件与 UI 工具（19 篇）
详见 [[KnowledgeBase/sources/k8s-db-middleware-UI-batch-summary|k8s-db-middleware-UI 批量摘要]]

**数据库部署**（三种范式对比）：原生 YAML（学习底层）、Helm Chart（标准化配置）、Operator（自动化运维）。覆盖 MySQL（NDB Operator/Helm/YAML 主从）、PostgreSQL HA（Pgpool+repmgr）、Redis（Cluster 模式 3主3从）、MongoDB（副本集/分片）、Kafka（Strimzi Operator）。

**UI 工具链**：Dashboard（Web 原生）、Kuboard（国产增强）、Lens（桌面 IDE，内置 Prometheus）、k9s（终端 TUI，Vim 风格）、Rancher（企业级多集群管理平台）、Krew 插件管理器。

**kubectl 插件排查**：[[kuebctl-插件krew|Krew 与 kubectl 插件指南]] 列出本机 14 个 Krew 业务插件及安装版本，说明上下文、资源、字段归属、镜像、日志、容量、卷用量与 CI 查询；whoami、rolesum、who-can 和 auth can-i 分别处理身份、角色来源、主体反查与授权查询。Stern、df-pv、blame、view-allocations 的用法与 ACK D7 实测限制见正文及 [[KnowledgeBase/sources/kubectl-krew-plugins-summary|来源摘要]]。

### 杂项专题（18 篇）
详见 [[KnowledgeBase/sources/k8s-misc-batch-summary|k8s-misc 批量摘要]]

覆盖 [[KnowledgeBase/entities/Helm|Helm]] v3 安装与使用、Config Syncer 跨 Namespace 同步、[[KnowledgeBase/entities/Dragonfly|Dragonfly]] P2P 镜像与 AI 大文件分发、Reloader 配置变更自动重启、CKA/CKS 认证备考、KubeBlocks 统一数据库管理、[[KnowledgeBase/entities/Harbor|Harbor]] 镜像仓库（docker-compose/Helm/KubeBlocks 三种部署方式）与 P2P Preheat、OpenShift、K3S、SpringCloud 迁移、Velero 备份恢复，以及 NVIDIA GPU 配置实践。Dragonfly 的 Scheduler 属于控制面，Peer、Seed Peer 与 Harbor 源站构成主要数据路径；P2P 的收益应以并发规模、对象大小、网络拓扑和运维成本共同评估。

### 备份与灾备（2 篇）
详见 [[KnowledgeBase/sources/k8s-backup-dr-summary|K8s 备份与灾备摘要]]

三层容灾架构：L1 etcd 快照（保命，`etcdctl snapshot`，全集群分钟级恢复）→ L2 [[KnowledgeBase/entities/Velero|Velero]] 应用备份（后悔药，Namespace/Label 粒度精确恢复）→ L3 应用数据备份（终极保险，数据库原生工具）。生产六大避坑：恢复验证必须定期演练、etcd 快照含 Secret 明文须加密、跨版本快照仅向前兼容、Velero 不含 Node 状态/Webhook 配置等隐形状态。

## 相关概念与实体

| 领域 | 核心实体 |
|------|----------|
| 容器基础 | [[KnowledgeBase/entities/Docker|Docker]]、[[KnowledgeBase/entities/containerd|containerd]] |
| 包管理与配置 | [[KnowledgeBase/entities/Helm|Helm]]、[[KnowledgeBase/entities/Kustomize|Kustomize]] |
| 网络与代理 | [[KnowledgeBase/entities/Ingress|Ingress]]、[[KnowledgeBase/entities/Istio|Istio]]、[[KnowledgeBase/entities/Calico|Calico]] |
| 监控与日志 | [[KnowledgeBase/entities/Prometheus|Prometheus]]、[[KnowledgeBase/entities/Grafana|Grafana]]、[[KnowledgeBase/entities/Loki|Loki]]、[[KnowledgeBase/entities/Alertmanager|Alertmanager]] |
| CI/CD | [[KnowledgeBase/entities/ArgoCD|ArgoCD]]、[[KnowledgeBase/entities/Jenkins|Jenkins]]、[[KnowledgeBase/entities/Tekton|Tekton]]、[[KnowledgeBase/entities/GitLab|GitLab]] |
| 安全 | [[KnowledgeBase/entities/Kyverno|Kyverno]]、[[KnowledgeBase/entities/Cert-Manager|Cert-Manager]]、[[KnowledgeBase/entities/Trivy|Trivy]] |
| 存储 | [[KnowledgeBase/entities/Ceph|Ceph]]、[[KnowledgeBase/entities/CubeFS|CubeFS]]、[[KnowledgeBase/entities/NFS|NFS]] |
| 数据库 | [[KnowledgeBase/entities/MySQL|MySQL]]、[[KnowledgeBase/entities/Redis|Redis]]、[[KnowledgeBase/entities/PostgreSQL|PostgreSQL]]、[[KnowledgeBase/entities/Kafka|Kafka]] |
| 集群管理 | [[KnowledgeBase/entities/Rancher|Rancher]]、[[KnowledgeBase/entities/K3S|K3S]]、[[KnowledgeBase/entities/Velero|Velero]]、[[KnowledgeBase/entities/KubeBlocks|KubeBlocks]] |

## 知识空白

- **Gateway API**：K8s 新一代入口 API，将逐步替代 Ingress 资源
- **多集群管理与联邦**：Karmada 已提及但未深入实践，Liqo、Submariner 等方案未覆盖
- ~~**FinOps 成本优化**~~（已有 K8s 成本优化方案文章覆盖 OpenCost 部署 + VPA/Karpenter/Spot + Prometheus 成本告警）
- **GitOps 进阶**：Flux CD 未覆盖，ArgoCD ApplicationSet 和多租户 GitOps 实践不足
- **eBPF 网络方案**：Cilium 作为下一代 CNI 未涉及
- **Serverless**：Knative 仅在 KPA 扩缩容中提及，完整 Serverless 方案缺失
- **混沌工程**：Chaos Mesh、Litmus 等故障注入工具未覆盖
- **Service Mesh 新方案**：Ambient Mesh（无 Sidecar 的 Istio）、Linkerd 未深入
