---
title: "K8s PodDisruptionBudget 实战：优雅中断保护"
source: "https://mp.weixin.qq.com/s/lXl9ZvAdJ7mTbwsdpwSPig"
created: 2026-06-06
tags:
  - kubernetes
  - pdb
  - high-availability
  - deployment
---

# K8s PodDisruptionBudget 实战

节点维护时，`kubectl drain` 会把节点上的应用迁走。如果同一服务的多个副本同时被驱逐，服务可能在新副本就绪前失去处理请求的能力。PodDisruptionBudget（PDB，中断预算）让应用声明：通过 Eviction API 驱逐 Pod 时，需要保留多少健康副本。

本文先解释预算如何计算，再区分节点排空与滚动发布，最后给出配置和排障示例。阅读前应了解 Deployment、Pod 标签选择器和 readinessProbe；所有维护实验应放在测试节点，文中的生产命名空间和镜像只是示例。

## 一、什么是 PDB

Pod 中断分两种：

- 非自愿中断（Involuntary）：节点宕机、内核 panic、节点压力驱逐等，不会先向 PDB 申请预算。容器 OOMKill 也不能靠 PDB 阻止，但不一定意味着整个 Pod 被删除。
- 自愿中断（Voluntary）：节点维护、集群升级中的主动迁移、应用发布等人为触发的操作。其中只有使用 Eviction API 的驱逐会执行 PDB 检查。

[PDB 的作用边界](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/) 是约束 Eviction API。`kubectl drain` 默认使用该接口；直接删除 Pod、控制器滚动更新和不可抗故障不会被 PDB 阻止。这些原因造成的不健康副本仍会减少可用预算。

没有 PDB 时，drain 缺少这项应用级可用副本检查。有 PDB 时，不满足预算的驱逐会被拒绝，drain 通常会重试，直到预算恢复或命令超时。PDB 不负责增加副本，也不保证其他节点有调度容量。

## 二、两种配置方式（二选一）

### minAvailable：最少保持可用

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payment-service-pdb
  namespace: production
spec:
  minAvailable: 2        # 始终保持至少2个Pod可用
  selector:
    matchLabels:
      app: payment-service
```

### maxUnavailable：最多允许不可用

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: order-service-pdb
  namespace: production
spec:
  maxUnavailable: 1      # 最多允许1个Pod同时不可用
  selector:
    matchLabels:
      app: order-service
```

两者都支持百分比（副本数动态变化时更实用）：

```yaml
spec:
  minAvailable: "80%"    # 始终保持80%的副本可用
  # 或
  maxUnavailable: "20%"  # 最多允许20%不可用
```

> 百分比向上取整。3 副本配置 `minAvailable: "80%"` 时，2.4 向上取为 3，健康副本齐全时也不允许驱逐。`maxUnavailable: "20%"` 在 3 副本时向上取为 1，实际允许比例达到约 33%。应按最小副本数检查结果，详见官方[预算计算说明](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)。

## 三、PDB 与 Drain / 滚动更新的配合

### 场景一：kubectl drain 节点维护

drain 过程中，K8s 的 eviction API 会检查目标 Pod 对应的 PDB：

```
检查 PDB → 驱逐 pod-A 是否会违反 minAvailable?
  当前可用: 3/3
  驱逐后剩余: 2/3
  minAvailable: 2 → 满足 → 允许驱逐
  
等待 pod-A 在其他节点就绪后，再尝试驱逐 pod-B...
```

如果服务只有 2 个健康副本且 `minAvailable: 2`，第一个副本的驱逐就会被阻止。即使只维护一个节点也一样；需要先增加并确认额外副本就绪，或由应用负责人接受中断并调整预算。

### 场景二：Deployment 滚动更新

Deployment 的滚动更新由它自己的 `maxUnavailable` 和 `maxSurge` 控制，控制器删除旧 Pod 时不通过 Eviction API，因此不受 PDB 阻止。发布期间的不健康副本会影响 PDB 的统计，可能让同时进行的节点维护没有驱逐预算。发布策略和 PDB 需要分别设计，并避免维护与发布争抢可用副本。

## 四、生产配置模式

### 模式一：高可用服务（3副本+）

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-gateway-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: api-gateway
      tier: frontend
```

### 模式二：数据库 StatefulSet（严格保护）

```yaml
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: mysql
      role: replica  # 只保护 replica，primary 单独配置
```

### 模式三：长期运行的批处理 Worker

以下假设 Worker 由 Deployment 等支持 scale 的控制器管理。普通 Job 的完成语义和副本模型不同，通常依靠 Job 重试或检查点恢复，不能照搬这个百分比 PDB。对于任意控制器或无控制器 Pod，只能按官方限制采用整数 `minAvailable`，并自行处理可用性。

```yaml
spec:
  maxUnavailable: "30%"
  selector:
    matchLabels:
      app: batch-worker
```

## 五、四大配置陷阱

### 陷阱一：单副本服务配 minAvailable: 1

```yaml
# ❌ 会导致节点永远无法被 drain！
spec:
  replicas: 1
---
spec:
  minAvailable: 1  # 只有1个副本，drain时永远无法满足
```

预算不变时，drain 会持续被拒绝或等待到超时。`--force` 只允许处理没有控制器的 Pod，不绕过 PDB。`--disable-eviction` 会改用直接删除并绕过预算，只能在明确接受中断的恢复流程中使用。单副本应用需要接受停机，或先扩容并验证应用支持多副本。

### 陷阱二：minAvailable 等于副本总数

```yaml
# ❌ 等同于"不允许任何中断"
spec:
  replicas: 3
---
spec:
  minAvailable: 3  # 节点维护永远无法进行
```

正确做法：`minAvailable: replicas - 1` 或用百分比留出余量。

### 陷阱三：混淆空 selector 与未设置 selector

```yaml
# policy/v1 中 selector: {} 匹配命名空间内所有 Pod
spec:
  minAvailable: 2
  selector: {}  # 误保护命名空间内所有 Pod
```

`policy/v1` 中，未设置 selector 或设为 null 不选择任何 Pod；显式的 `{}` 才选择命名空间内全部 Pod。应始终写明确的标签条件，避免不同服务共用预算。

### 陷阱四：PDB 和 HPA 配合时的计算失误

HPA 动态调整副本数，PDB 百分比需考虑最小副本场景：

```yaml
# HPA: minReplicas: 2, maxReplicas: 10
# PDB: maxUnavailable: "50%"
# 当副本是2时，50%=1，可能对高可用服务太激进

# 如果业务允许至少保留 1 个副本，可使用绝对数；这不是通用高可用标准
spec:
  minAvailable: 1  # 无论 HPA 如何扩缩，至少保证1个可用
```

### 不健康 Pod 的驱逐策略

`unhealthyPodEvictionPolicy` 在 Kubernetes 1.31 稳定。默认 `IfHealthyBudget` 可能让不健康 Pod 在预算不足时阻塞排空；`AlwaysAllow` 允许驱逐 Running 但未 Ready 的 Pod，健康 Pod 仍受预算保护。可以在 `spec` 中设置：

```yaml
unhealthyPodEvictionPolicy: AlwaysAllow
```

这有助于处理 CrashLoopBackOff 阻塞维护的情况，但应先确认应用能够在其他节点恢复。

## 六、验证 PDB 是否生效

```bash
# 查看 PDB 状态
kubectl get pdb -n production
# NAME                   MIN AVAILABLE   MAX UNAVAILABLE   ALLOWED DISRUPTIONS   AGE
# payment-service-pdb    2               N/A               1                     3d

# 查看预算的健康统计和条件
kubectl describe pdb payment-service-pdb -n production
kubectl get events -n production --sort-by=.lastTimestamp
# 同时检查 drain 的错误输出；并非所有驱逐拒绝都会留下相同 reason 的 Event

# 调用 eviction API 测试（被 PDB 阻止会返回 429 Too Many Requests）
```

`ALLOWED DISRUPTIONS` 是当前允许通过预算检查的驱逐数，取决于健康副本、期望副本和在途驱逐等状态。值为 0 时，继续检查 selector 是否匹配、Pod 是否 Ready、`status.observedGeneration` 是否追上配置，以及新 Pod 是否因容量或挂载问题无法就绪。

## 七、完整生产示例（支付服务）

```yaml
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: payment-service
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0      # 发布时先扩再缩；实际可用性仍取决于探针和优雅终止
      maxSurge: 1
  template:
    metadata:
      labels:
        app: payment-service
    spec:
      terminationGracePeriodSeconds: 60
      containers:
      - name: payment
        image: payment-service:v2.3.1
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
---
# PDB
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payment-service-pdb
  namespace: production
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: payment-service
```

该示例使用业务镜像 `payment-service:v2.3.1`，需替换为自己的仓库地址，并实现 `/health/ready`。Deployment 的 selector、Pod 标签与 PDB selector 必须一致。

`maxUnavailable: 0` 与 `minAvailable: 2` 分别约束两类操作：

- 滚动更新时先启动新 Pod（surge），确认就绪后再删除旧 Pod
- 节点维护通过 Eviction API 时，在 3 个副本均健康的前提下，当前允许驱逐 1 个 Pod；新副本恢复健康后预算才会补回。
