---
title: K8s基础资源 来源批量摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/k8s-basic-resources
date: 2026-10-23
sources:
  - "[[Docker-Kubernetes/k8s-basic-resources/K8s基础-pod调度-亲和力]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/Python调用k8s-api实现资源管理]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-Calico]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-Service]]"
  - "[[Docker-Kubernetes/k8s-configMap-secret/k8s基础-configMap-Secret]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-daemonset]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-deployment]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-ingress]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-job-cronjob]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-kubeadm]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-namespace-资源分配]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-pod]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-statefulset]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-storage]]"
  - "[[k8s基础-yaml-apply]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-临时容器ephemeral]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-容器运行时-containerd]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-自定义CRD资源]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-认证-授权-准入]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s-APIServer深度剖析-请求链路-认证授权-生产调优]]"
  - "[[Docker-Kubernetes/k8s-basic-resources/k8s基础-Finalizer与资源删除]]"
aliases:
  - "K8s 基础资源批量摘要"
  - "k8s-basic-resources 批量摘要"
---

# K8s基础资源 来源批量摘要

## 元信息
- **原始目录**：`Docker-Kubernetes/k8s-basic-resources/`
- **文档数量**：本批次收录 22 篇（`k8s-basic-resources/` 现有 26 篇；另 1 篇 ConfigMap/Secret 已移至 `k8s-configMap-secret/`）
- **领域**：Docker-Kubernetes
- **摄入日期**：2026-04-17（新增文档摄入日期：2026-07-18）

## 摘要
本批次文档系统性地覆盖了 Kubernetes 的核心基础知识，从集群架构与组件（API Server、Scheduler、Controller Manager、etcd）到各类工作负载资源（Pod、Deployment、StatefulSet、DaemonSet、Job/CronJob），再到网络（Service、Ingress、Calico）、存储（Volume、PV/PVC）、配置管理（ConfigMap、Secret）、安全（认证、授权、RBAC）以及扩展机制（CRD、Operator）、资源删除生命周期机制（Finalizer）。文档还涵盖了集群搭建工具 kubeadm、容器运行时 containerd、YAML 编写规范、临时容器调试、Python API 编程等实用主题。整体构成了一套完整的 Kubernetes 基础知识体系。

## 关键知识点
1. API Server 是所有组件通信的中枢，也是唯一与 etcd 交互的组件；请求链路依次为认证 → 授权（RBAC）→ 变更准入 → 校验 → 验证准入 → etcd 持久化 → Watch 通知。
2. 常见 Linux 运行时通过 Pod sandbox 维持共享命名空间；容器共享网络，存储共享需显式挂载同一个 Volume。`containerPort` 不会改变应用监听，requests 参与调度记账与资源保障，不等于资源已被程序实际使用。
3. Liveness 只应检查重启能够修复的进程内部故障并保守重启，外部依赖状态交由 Readiness 谨慎处理（先摘流），慢启动应用使用 Startup Probe 隔离启动阶段。
4. Deployment 仅在 `spec.template` 变化时生成新 RS，滚动更新节奏由 maxSurge 和 maxUnavailable（数字或百分比）控制。
5. StatefulSet 基于 Headless Service 为每个 Pod 分配固定 DNS（`pod-name.svc-name.ns.svc.cluster.local`），并通过 volumeClaimTemplates 为每个 Pod 自动创建独立 PVC。
6. Service 通过标签选择器匹配 Pod 并创建同名 Endpoint；kube-proxy 的 iptables 模式在 Service 数量大时性能下降，IPVS 基于哈希表性能更优；Ingress 流量从 Ingress Controller 直达 Pod，不经过 Service。
7. Client-side Apply 基于 last-applied、live state 与新 manifest 三路合并，多工具共管时可能静默覆盖；Server-side Apply 通过 `managedFields` 追踪字段所有权，把字段争用转化为显式冲突。
8. `metadata.finalizers` 非空时，apiserver 只设置 `deletionTimestamp` 使资源进入 Terminating；需经 Controller 清理并移除 Finalizer 后，对象才会从 etcd 删除。

## 各文档摘要

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源|K8s基础-架构-组件-资源]]
- 核心内容：Kubernetes 的基本概念、发展历程、核心优势，以及集群架构中控制平面（API Server、Scheduler、Controller Manager、etcd）和工作节点（kubelet、kube-proxy）的组件职责。
- 关键知识点：
  - K8s 源自 Google Borg 系统，2014年开源，2018年从 CNCF 毕业
  - API Server 是所有组件通信的中枢，唯一与 etcd 交互的组件
  - Scheduler 监听未绑定节点的 Pod 并执行调度算法
  - K8s 相比纯 Docker 的优势：弹性伸缩、服务发现、自愈、滚动更新、声明式管理

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-pod|K8s基础-Pod]]
- 核心内容：Pod 作为最小可部署单元的容器协作边界，常用字段、调度与初始化、phase 与状态展示、钩子与优雅退出，以及日志和主进程排障。
- 关键知识点：
  - 容器共享 Pod 网络；PID 命名空间默认不共享，文件共享需显式挂载同一 Volume
  - 容器重启通常仍在原 Pod 内，替代 Pod 的 UID 不同
  - `containerPort` 不改变应用监听；requests 用于调度与资源保障，limits 约束运行时使用
  - 普通 Init Container 依次成功结束后，应用容器才启动
  - `PostStart` 与入口程序没有先后保证；`preStop` 与应用退出共用终止宽限期
  - 探针配置与故障复盘见 [[Docker-Kubernetes/k8s-basic-resources/k8s基础-健康探针|健康探针专文]]，来源摘要见 [[KnowledgeBase/sources/k8s-probe-restart-storm-summary]]

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-deployment|K8s基础-Deployment]]
- 核心内容：Deployment 控制器的概念与工作原理，包括 ReplicaSet 管理、滚动更新策略（maxSurge/maxUnavailable）、金丝雀发布与回滚机制。
- 关键知识点：
  - Deployment 管理多个 RS，每次更新生成新 RS 替换旧 RS
  - 仅 `spec.template` 变化才触发更新，产生新 RS
  - maxSurge 和 maxUnavailable 支持数字或百分比，控制滚动更新节奏
  - 相比直接使用 ReplicaSet，Deployment 支持滚动升级、蓝绿部署和回滚

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-statefulset|K8s基础-StatefulSet]]
- 核心内容：StatefulSet 用于部署有状态应用，提供稳定的网络标识符、有序部署/扩缩容、持久化存储（volumeClaimTemplates）。
- 关键知识点：
  - 有状态应用特征：Pod 独立且有序、唯一网络标识、持久存储
  - 基于 Headless Service 为每个 Pod 分配固定 DNS：`pod-name.svc-name.ns.svc.cluster.local`
  - volumeClaimTemplates 自动为每个 Pod 创建独立 PVC
  - 生产环境推荐用 Operator/Helm 部署复杂有状态服务
  - Recreate 在 Kubernetes 1.37 中为 Alpha、默认关闭，需在 API Server 和 Controller Manager 启用 StatefulSetRecreateStrategy
  - rollingUpdate.partition 仅适用于 RollingUpdate，不能与 Recreate 组合；整体重建与分区灰度需要分开评估
  - 区分 StatefulSet 删除/缩容时的 PVC 保留策略与 PVC 删除后的 PV 回收策略，正常 Pod 替换不因 StorageClass 为 Delete 自动删除 PVC
  - [[Docker-Kubernetes/k8s-basic-resources/k8s基础-statefulset#Recreate 更新策略（Kubernetes 1.37 Alpha）|Recreate 更新策略章节]]：包含 4 组代码和 11 个故障案例，并说明版本、配置、存储与案例指标的核验边界

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-daemonset|K8s基础-DaemonSet]]
- 核心内容：DaemonSet 确保集群每个节点运行一个相同的 Pod 副本，常用于日志收集、监控代理、存储守护进程等场景。
- 关键知识点：
  - 节点加入集群自动创建 Pod，节点移除自动删除 Pod
  - 通过 nodeSelector 指定特定节点（如 SSD 磁盘、GPU 节点）
  - 与 Deployment 的 YAML 区别：kind 为 DaemonSet，无 replicas 字段
  - 滚动更新支持 maxUnavailable 控制同时不可用的 Pod 数

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-job-cronjob|K8s基础-Job-CronJob]]
- 核心内容：Job 控制器管理一次性任务（如数据库备份），CronJob 在 Job 基础上增加定时调度能力，支持并行执行与失败重试。
- 关键知识点：
  - Job 相比 shell/docker 的优势：环境隔离、状态追踪、失败重试、并行执行
  - 关键配置：completions（成功数）、parallelism（并行数）、backoffLimit（失败重试上限）
  - CronJob 先创建 Job，再由 Job 创建 Pod 执行任务
  - ttlSecondsAfterFinished 控制 Job 完成后自动清理

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-Service|K8s基础-Service]]
- 核心内容：Service 为一组 Pod 提供稳定的访问入口和负载均衡，详解 Endpoint 机制和 kube-proxy 三种工作模式（Userspace、iptables、IPVS）。
- 关键知识点：
  - Service 通过标签选择器匹配 Pod，创建同名 Endpoint 对象
  - kube-proxy 监听 Service 变动并转换为转发规则（iptables/ipvs）
  - iptables 模式在 Service 数量大时性能下降；IPVS 基于哈希表，性能更优
  - K8s v1.29 引入 nftables 作为 kube-proxy 新后端（Alpha）

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-ingress|K8s基础-Ingress]]
- 核心内容：Ingress 提供七层负载均衡入口，通过 Ingress Controller（如 Nginx）实现基于域名/URL 的流量路由，解决 NodePort 端口管理和四层代理的局限。
- 关键知识点：
  - Ingress 是路由规则资源，Ingress Controller 是实际的反向代理实现
  - 流量直接从 Ingress Controller 到 Pod，不经过 Service（Service 仅用于分组）
  - 生产推荐：独占节点部署 + hostNetwork:true + 前端网关（F5/SLB/LVS）
  - 四层 vs 七层代理的区别与适用场景

### [[Docker-Kubernetes/k8s-configMap-secret/k8s基础-configMap-Secret|K8s基础-ConfigMap-Secret]]
- 核心内容：ConfigMap 用于管理非机密配置数据，Secret 用于管理敏感信息，两者均可通过环境变量或存储卷方式注入到 Pod 中。
- 关键知识点：
  - ConfigMap 创建方式：命令行 `--from-literal`、基于文件 `--from-file`、基于目录
  - ConfigMap 大小限制为 1 MiB
  - 两种注入方式：Volume 挂载与 env configMapKeyRef
  - ConfigMap 实现配置与镜像解耦，支持多服务共享配置

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-storage|K8s基础-Storage]]
- 核心内容：Kubernetes 存储体系，从简单存储（EmptyDir、HostPath、NFS）到高级存储（PV/PVC）、配置存储（ConfigMap/Secret）的分层介绍。
- 关键知识点：
  - Volume 生命周期独立于容器，实现数据持久化和容器间数据共享
  - EmptyDir 随 Pod 销毁而删除，适用于临时数据和 sidecar 数据共享
  - PV/PVC 分离存储管理与使用，PV 由管理员创建，PVC 由用户申请
  - 应用场景：用户数据、模型文件、配置文件、共享数据、日志文件

### [[k8s基础-yaml-apply|K8s基础-YAML]]
- 核心内容：YAML 语法基础、Kubernetes 资源字段，以及 Client-side Apply 与 Server-side Apply 的合并机制和字段所有权模型。
- 关键知识点：
  - YAML 数据类型：纯量、数组、对象、对象列表、map
  - Pod YAML 一级属性：apiVersion、kind、metadata、spec、status
  - imagePullPolicy 三种策略：Always、IfNotPresent、Never
  - 使用 `kubectl explain` 逐层查询 YAML 字段定义
  - CSA 依赖 last-applied、live state 与新 manifest 做三路合并，多工具共管时可能静默覆盖
  - SSA 通过 `managedFields` 追踪字段所有权，并把字段争用转化为显式冲突
  - CRD 列表的 map/atomic 合并语义取决于结构化 schema 和 `x-kubernetes-list-*` 注释

### [[Docker-Kubernetes/k8s-basic-resources/K8s基础-pod调度-亲和力|K8s基础-Pod调度-亲和力]]
- 核心内容：K8s 四种 Pod 调度方式（自动调度、定向调度、亲和性调度、污点调度）及拓扑域概念，通过标签和亲和力规则精确控制 Pod 部署位置。
- 关键知识点：
  - 拓扑域通过节点标签划分（主机、区域、数据中心、子网）
  - 定向调度：nodeName 直接指定节点、nodeSelector 基于标签选择
  - 亲和性调度：NodeAffinity、PodAffinity、PodAntiAffinity
  - 污点与容忍：Taints 标记节点限制、Toleration 允许 Pod 调度到污点节点

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-namespace-资源分配|K8s基础-Namespace-资源分配]]
- 核心内容：Namespace 实现集群资源逻辑隔离，通过 ResourceQuota 和 LimitRange 控制命名空间级别的资源使用与 Pod 资源配置。
- 关键知识点：
  - 生产环境必须对每个 ns 限制 Pod 和 RS 数量，防止异常激增拖垮集群
  - ResourceQuota 限制 ns 的 CPU/内存总量、对象数量（Pod、PVC、Service 等）
  - LimitRange 为未声明 resources 的容器自动添加默认值
  - 资源划分可以租户或环境为单位，需预留冗余

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-Calico|K8s基础-Calico]]
- 核心内容：Calico 开源网络方案的架构、核心组件（Felix、BIRD、etcd）和两种网络模式（IPIP 与 BGP）的对比分析。
- 关键知识点：
  - Felix 负责网络接口管理和路由，BIRD 负责 BGP 路由分发
  - IPIP 模式：隧道封装，配置简单但有性能开销，创建 tunl0 虚拟接口
  - BGP 模式：直接路由，性能更优，物理机作为虚拟路由器
  - IP_AUTODETECTION_METHOD 指定正确的网络接口进行 Pod IP 分配

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-kubeadm|K8s基础-kubeadm]]
- 核心内容：kubeadm 初始化集群的完整流程，包括 16 项预检查内容、安装后配置步骤，以及 K8s 证书体系（集群根证书、etcd 证书分组）。
- 关键知识点：
  - 预检查涵盖：用户权限、版本兼容、端口占用、swap 状态、内核模块等
  - 安装后配置：创建 ConfigMap、打标签、部署 DNS 和 kube-proxy
  - 证书存放路径：`/etc/kubernetes/pki` 和 `/etc/kubernetes/pki/etcd`
  - kubelet 版本需高于 kubeadm 最低要求且不超过待安装 K8s 版本

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-临时容器ephemeral|K8s基础-临时容器Ephemeral]]
- 核心内容：Ephemeral 容器是 K8s 中用于在运行中的 Pod 中动态注入调试容器的机制，无需重启 Pod 即可执行诊断和故障排查。
- 关键知识点：
  - 临时容器不在 Pod 初始规范中定义，通过 `kubectl debug` 动态添加
  - 不支持端口配置、健康检查和资源限制
  - 使用场景：调试崩溃容器、无 shell 镜像的故障排查、安全审查
  - K8s 1.25 起成为 stable 特性，之前需通过 feature-gates 开启

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-容器运行时-containerd|K8s基础-容器运行时-containerd]]
- 核心内容：CRI 接口规范介绍，containerd 作为容器运行时的定位与使用，以及 ctr、nerdctl、crictl 三种命令行工具的对比。
- 关键知识点：
  - CRI 是 K8s 与容器运行时的标准化接口，支持 containerd、CRI-O、Kata 等
  - containerd 从 Docker 引擎中剥离，是 CNCF 毕业项目
  - 调用链：Docker/K8s -> containerd -> RunC（底层容器运行时）
  - ctr namespace 与 K8s namespace 无关，K8s 镜像在 k8s.io namespace 下

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-自定义CRD资源|K8s基础-自定义CRD资源]]
- 核心内容：Operator 模式与 CRD（CustomResourceDefinition）机制，通过自定义资源类型扩展 K8s API，实现复杂应用的声明式管理。
- 关键知识点：
  - Operator = CRD（资源定义）+ Controller（控制逻辑）
  - CRD 自 K8s 1.7 引入，无需修改源码即可扩展 API
  - Operator vs Helm：Operator 适合复杂有状态应用，Helm 适合简单微服务
  - Operator 资源来源：operatorhub.io、GitHub 社区

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-认证-授权-准入|K8s基础-认证-授权-准入]]
- 核心内容：K8s 安全体系中的认证（Authentication）和授权（Authorization）机制，包括 UserAccount、ServiceAccount、Token 管理与 kubeconfig 生成。
- 关键知识点：
  - UserAccount 供集群外部用户使用，ServiceAccount 供应用和用户身份认证
  - K8s 1.24 后不再自动为 SA 创建 Secret，需手动创建 Token
  - Token 创建方式：命令行 `kubectl create token`（有时效）、Secret（永久有效）
  - 基于 SA 生成 kubeconfig 文件供特定用户登录集群

### [[Docker-Kubernetes/k8s-basic-resources/Python调用k8s-api实现资源管理|Python调用K8s-API实现资源管理]]
- 核心内容：使用 Python kubernetes 库编程操作 K8s 集群，实现 Pod、Service、Deployment 等资源的查询、创建和管理。
- 关键知识点：
  - 使用 `client.CoreV1Api()` 操作 Pod、Service、Namespace 等核心资源
  - 使用 `client.AppsV1Api()` 操作 Deployment 等控制器资源
  - 需加载 kubeconfig 文件（master 节点的 `~/.kube/config`）进行认证
  - 支持列举、查询、创建等 CRUD 操作

### [[Docker-Kubernetes/k8s-basic-resources/k8s-APIServer深度剖析-请求链路-认证授权-生产调优|K8s API Server：请求链路、认证授权与生产调优]]
- 核心内容：kube-apiserver 内部工作原理全面剖析——请求完整生命周期（认证→授权→准入→持久化→Watch）、Watch/Informer 机制、API 扩展（CRD/聚合 API）、生产调优、故障排查。
- 关键知识点：
  - 请求链路 7 步：认证（X.509/SA Token/OIDC/Webhook）→ 授权（RBAC）→ 变更准入（Mutating）→ 校验 → 验证准入（Validating）→ etcd 持久化 → Watch 通知
  - Watch 机制：基于 ResourceVersion 增量推送，Watchcache 内存缓存减少 etcd 压力，Bookmark 事件防止 RV 过期
  - SharedInformer 三组件：Reflector（List+Watch）→ DeltaFIFO Queue → Indexer（本地缓存）
  - 准入 Webhook 危险点：`failurePolicy: Fail` + Webhook 不可用 = 所有 Pod 创建失败，必须排除 kube-system
  - CRD 注册后自动提供 REST CRUD + Watch + RBAC + etcd 持久化
  - 聚合 API Server（APIService）：kubectl top pods 背后调用 metrics-server 的机制
  - 生产调优参数：max-requests-inflight/max-mutating-requests-inflight/target-ram-mb，资源规划表（50→3000+ 节点）
  - 审计日志完整 Policy 配置（分级：None/Metadata/Request）
  - 3 条 Prometheus 告警规则（错误率/P99 延迟/并发请求上限）
  - 故障排查手册：API Server 无响应（etcd 健康检查/证书过期）、Webhook 死锁紧急恢复、Watch 泄漏定位

### [[Docker-Kubernetes/k8s-basic-resources/k8s基础-Finalizer与资源删除|K8s基础-Finalizer与资源删除]]
- 核心内容：Finalizer 机制的完整解析——`metadata.finalizers` 字段如何阻止资源被真正删除、资源删除的完整流程（deletionTimestamp → Controller 清理 → 移除 Finalizer → etcd 删除）、内置与第三方常见 Finalizer、资源"删不掉"的五大场景及诊断修复方法、Operator 中编写 Finalizer 的完整代码示例。
- 关键知识点：
  - `metadata.finalizers` 列表非空时，apiserver 只设置 `deletionTimestamp` 进入 Terminating，不会真正删除对象
  - 五大"删不掉"场景：Controller 已卸载、Controller 清理逻辑报错、Namespace 内资源卡住、Finalizer 与 ownerReferences 循环依赖、apiserver 无法到达 Controller
  - 手动移除 Finalizer（`kubectl patch --type=merge -p '{"metadata":{"finalizers":null}}'`）会跳过清理逻辑，可能导致外部资源（云盘、负载均衡器）泄漏
  - 编写 Finalizer 四原则：清理逻辑幂等、失败时不移除 Finalizer（RequeueAfter 重试）、命名用 `域名/功能` 格式、记录部分清理进度
  - Finalizer（资源对象级别，apiserver 层拦截）与 preStop/terminationGracePeriodSeconds（Pod 级别）作用层次不同，Finalizer 更早触发、更难绕过

## 涉及的概念与实体
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/concepts/Finalizer|Finalizer]]
- [[KnowledgeBase/entities/Pod|Pod]]
- [[KnowledgeBase/entities/Deployment|Deployment]]
- [[KnowledgeBase/entities/StatefulSet|StatefulSet]]
- [[KnowledgeBase/entities/DaemonSet|DaemonSet]]
- [[KnowledgeBase/entities/Service|Service]]
- [[KnowledgeBase/entities/Ingress|Ingress]]
- [[KnowledgeBase/entities/ConfigMap|ConfigMap]]
- [[KnowledgeBase/entities/Calico|Calico]]
- [[KnowledgeBase/entities/containerd|containerd]]
- [[KnowledgeBase/entities/kubeadm|kubeadm]]
- [[KnowledgeBase/entities/CRD|CRD]]
- [[KnowledgeBase/entities/Operator|Operator]]
- [[KnowledgeBase/entities/RBAC|RBAC]]
- [[KnowledgeBase/entities/PV-PVC|PV/PVC]]

## 交叉主题发现
- **声明式管理贯穿始终**：从 Pod YAML 编写、Deployment 滚动更新到 CRD 自定义资源，所有资源都通过声明式 YAML 定义期望状态，由 K8s 控制器自动实现。
- **网络层次分明**：Service 提供四层负载均衡（iptables/IPVS），Ingress 提供七层负载均衡（域名/URL 路由），Calico 提供底层网络连通性（IPIP/BGP），三层协同构成完整的 K8s 网络体系。
- **安全与资源管控紧密关联**：认证-授权-准入控制保障集群访问安全，ResourceQuota 和 LimitRange 保障资源使用安全，两者共同防止集群被滥用或拖垮。
- **有状态与无状态的对比设计**：Deployment（无状态）vs StatefulSet（有状态）的设计理念贯穿多篇文档，体现了 K8s 对不同应用类型的差异化支持。
- **从容器到编排的演进**：containerd 文档连接了 Docker 与 K8s 的技术演进线索，展示了容器运行时从 Docker 独占到 CRI 标准化的技术变革。
- **生产环境最佳实践**：多篇文档强调了生产环境的注意事项，如 ns 级别 Pod/RS 数量限制、Ingress 独占节点 + hostNetwork、Operator 部署有状态服务等。
- **删除生命周期与扩展机制交织**：Finalizer 机制解释了 namespace-资源分配 文档中 Namespace 卡在 Terminating 的根本原因，也与 CRD/Operator 文档中"删除命名空间级联删除自定义资源实例"直接相关——CRD 实例若带 Finalizer 且 Controller 异常，会导致整条级联删除链路卡死。

## 值得注意
- **版本边界**：CRD 自 K8s 1.7 引入；1.24 起不再自动为 ServiceAccount 创建 Secret，需手动创建 Token（`kubectl create token` 有时效，Secret 方式永久有效）；临时容器自 1.25 起为 stable，此前需通过 feature-gates 开启；nftables 作为 kube-proxy 新后端于 v1.29 引入，文中标注为 Alpha。
- **探针误配的放大效应**：Pod 文档复盘了 Liveness/Readiness 配置不当引发 300+ Pod 连锁重启的生产事故；PDB 和 HPA 不能直接阻止 Liveness 误杀，探针变更仍需灰度、监控和快速回滚。
- **高风险操作**：准入 Webhook 配置 `failurePolicy: Fail` 且 Webhook 不可用时，所有 Pod 创建都会失败，必须排除 kube-system；手动移除 Finalizer 会跳过清理逻辑，可能导致云盘、负载均衡器等外部资源泄漏。
