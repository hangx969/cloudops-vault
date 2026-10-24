---
title: K8s基础-namespace-资源分配
tags:
  - kubernetes
  - k8s-basics
aliases:
  - k8sNamespace资源分配
---

# Kubernetes Namespace 与资源分配：给团队划边界，也给资源设预算

同一个集群里，开发环境突然创建大量 Pod，可能影响生产服务；某个应用把内存 requests 写得很小，又可能让节点承受超出预期的负载。Namespace、ResourceQuota 和 LimitRange 分别解决归属、总量和单个对象约束的问题，需要配合使用。

本文从命名空间开始，逐步配置配额、默认资源值与 QoS，最后解释 Namespace 删除为何可能停在 Terminating。阅读示例前，需要了解 Pod、Deployment，以及 CPU 和内存的 requests/limits。配置示例用于测试命名空间，数值应按容量和业务需求调整。

## Namespace 能隔离什么

Namespace 为资源提供名称和管理范围。同一命名空间内同类资源名称需要唯一，不同命名空间可以使用相同名称。它便于分别配置权限、配额与网络策略，但本身不提供独立的节点、网络或安全边界。

Namespace 对象本身是集群级资源；Pod、Deployment、Service、ResourceQuota 等对象则属于某个命名空间。可以按团队、租户、项目或 dev、test、production 环境划分。Node、PersistentVolume 等集群级对象不能靠 Namespace 分组隔离。

是否划分 Namespace 取决于管理边界。即使用户很少，只要需要区分生产与测试权限或资源预算，也可以使用。多租户还应配合 RBAC、NetworkPolicy 和工作负载安全策略。

创建ns:

```bash
kubectl create ns test
```

### 合理的资源划分

资源限制的重要性:如果没有,可能会产生节点资源被异常耗尽的问题。

对象数量配额用于限制异常控制器或自动化任务造成的对象增长。例如，不被节点允许的 sysctl 可能导致 Pod 被 kubelet 拒绝，控制器继续尝试维持副本，失败对象也会增加排障成本。是否反复生成对象取决于控制器和失败状态，不能仅凭 `SysctlForbidden` 推断一定会生成上万个 Pod。

可以为 Namespace 设置 Pod、ReplicaSet、PVC 等对象数量上限。例如 512 个 Pod、1024 个 ReplicaSet 只是容量预算的一个起点，不能直接作为所有集群的生产标准。ReplicaSet 会受 Deployment 的副本和历史版本设置影响，配额需要为发布与回滚保留余量。

#### 以租户为单位

是针对ns去限制的。

1. 基于节点去划分:比如一个团队申请了5台8C16G机器加入集群,可以把 40 CPU、80Gi 作为预算上界的计算起点；还要扣除系统、DaemonSet 和故障冗余，并区分 requests 总量与 limits 总量。配额不会把这些节点自动专用于该团队。
2. 基于现有资源:利用现有资源,直接划分给这个团队固定的cpu和memory

#### 以环境为单位

比如有dev、uat、prod等环境,需要预估每个环境的所有微服务情况,留一些冗余。

## ResourceQuota资源

Namespace 建好以后，还需要为它设置资源预算。[ResourceQuota](https://kubernetes.io/docs/concepts/policy/resource-quotas/) 在 API 准入时检查声明的资源总量与对象数量，不根据监控中的实时 CPU 使用率扣减配额。它可以：

- 限制资源使用量
- 限制对象数量

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: customer1-quota
  namespace: customer1
spec:
  hard:
    # 示例预算；应用前先创建 customer1 命名空间
    count/pods: "100"
    requests.cpu: "2"
    requests.memory: 4Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    count/replicasets.apps: "1000"
    count/persistentvolumeclaims: "10"
    requests.storage: 400Gi
    count/services: "40"
```

> CPU的单位解释:[为 Pod 和容器管理资源 | Kubernetes](https://kubernetes.io/zh-cn/docs/concepts/configuration/manage-resources-containers/)
>
> CPU 资源的限制和请求以 "cpu" 为单位。 在 Kubernetes 中,一个 CPU 等于 **1 个物理 CPU 核** 或者 **1 个虚拟核**, 取决于节点是一台物理主机还是运行在某物理主机上的虚拟机。
>
> - 如果是request.cpu: 0.5 --> 那就是请求0.5个核
> - 如果是request.cpu: 500m --> 那是500毫核 --> 也就是0.5核

> [!warning] 注意
>
> - 如果配额限制了 CPU/内存 requests 或 limits，对应容器必须具有这些声明；可由 LimitRange 补默认值。否则 Deployment 对象可能创建成功，但 ReplicaSet 创建 Pod 时被拒绝。通过 `kubectl describe rs` 和 `kubectl get events` 查看准入错误。仅限制对象数量的配额不会自动要求所有 CPU/内存字段。
> - 新配额不会为了满足上限而自动驱逐已运行 Pod；后续创建、扩容或更新资源会受到检查。删除对象通常用于释放预算，不是“超额后禁止删除”。

## LimitRange资源

ResourceQuota 控制命名空间总量，无法单独保证每个容器的声明合理。一个只申请 `1m` CPU、`1Mi` 内存的容器可能被调度到剩余可分配 requests 很少的节点，实际运行却消耗更多内存。LimitRange 可以约束单个容器或 Pod 的资源范围，也能给缺失字段补默认值。

这样是不行的,需要:

1. 对requests和limits的值也进行合理性的约束,不符合约束的就禁止创建;
2. 对于没有显式声明requests和limits的资源,添加上一个默认值。

在Kubernetes集群中部署任何的服务,都建议添加resources参数,也就是配置内存和CPU资源的请求和限制。如果不想给每个容器都手动添加资源配置,此时可以使用limitRange实现给每个容器自动添加资源配置(不会覆盖已经配置的值)。

~~~yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: cpu-mem-limit-range
spec:
  limits:
  - type: Container # 类型名区分大小写；Pod 类型可约束 Pod 总量
    default: # default就是limit的默认值
      cpu: 1
      memory: 512Mi
    defaultRequest: # request的默认值
      cpu: 0.5
      memory: 256Mi
    min: # 容器资源声明的下限
      memory: 32Mi
      cpu: 100m
    max: # 容器资源声明的上限
      memory: 1Gi
      cpu: 1
  - type: PersistentVolumeClaim # 限制PVC的存储大小范围(创建太多很小的PVC,可能会产生过多的存储碎片)
    max:
      storage: 3Gi
    min:
      storage: 1Gi
~~~

> [!warning] 注意
>
> 1. limitRange是针对pod去修改的,deployment的yaml不会被修改。

## QoS

资源声明还会影响 Pod 的 QoS（Quality of Service，服务质量）分类。节点内存紧张时，需要区分 kubelet 的节点压力驱逐与内核 OOM killer：前者会终止 Pod，后者通常终止容器中的进程，两者的决策机制不同。

[Pod QoS](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/) 依据 CPU/内存资源配置分类。QoS 会影响 OOM 分数等行为，但节点压力驱逐还会考虑是否超过 requests、Pod Priority 和使用量等因素。QoS 不是 Pod 优先级，也不能保证关键服务永远不被终止。以下按常规的容器级资源声明说明。

### Guaranteed

Guaranteed 要求容器的 CPU 和内存 requests 与 limits 相等。调度器根据 requests 判断节点是否有足够的可分配资源；该分类不会提高 `priorityClassName`，也无法避免节点故障或应用超过自身内存限制导致的 OOM。

配置Guaranteed级别的Pod,需要满足如下条件:

1. Pod中的每个容器必须指定limits.memory和requests.memory,并且两者需要相等
2. Pod中的每个容器必须指定limits.cpu和requests.cpu,并且两者需要相等

~~~yaml
limits:
  cpu: 200m
  memory: 512Mi
requests:
  cpu: 200m
  memory: 512Mi
~~~

> MySQL、Redis 等有状态服务可以按压测结果考虑 Guaranteed。资源值需要覆盖数据库缓存、连接和后台任务；配置相等本身不能替代容量评估。

### Burstable

Burstable 的资源配置介于 Guaranteed 与 BestEffort 之间。调度按 requests 计算，运行中可以在 limits 和节点实际资源允许的范围内使用超过 requests 的资源。超过 requests 的部分在节点压力下更容易受到影响。

配置Burstable级别的Pod,需要满足如下条件:

1. Pod不符合Guaranteed的配置要求
2. Pod 中至少一个容器具有 CPU 或内存 request/limit；只设置 limit 时，缺失的 request 可能在准入阶段被补成同值。分类应以 API 中最终保存的配置为准。

~~~yaml
requests:
  memory: 128Mi
  cpu: 100m
~~~

> - 一般自己开发的无状态微服务,允许漂移的,可以设置成Burstable。
> - 而且一般微服务CPU使用量低,所以CPU一般设置成小requests,可变得更大,这种模式就是Burstable。
> - Java 容器不能用固定的 `Xmx+128Mi` 作为通用内存预算。还需计入 Metaspace、线程栈、直接内存、JVM 本身及应用的堆外占用，再结合负载测量配置 requests/limits。

### BestEffort

BestEffort Pod 的所有容器均未声明 CPU/内存 requests 和 limits。调度时缺少这部分资源预算，节点压力下通常很脆弱；实际驱逐顺序仍受压力类型、使用量和 Pod Priority 等因素影响。

配置BestEffort级别的Pod,不配置resources字段即可。

> 生产环境不推荐使用,因为没有配置任何资源声明,可能会被调度到资源紧张的节点上,造成一些问题。

## ns删除后卡在Terminating状态

删除命名空间时，可能因为残留资源或 finalizer 未完成，导致 namespace 一直卡在 Terminating 状态，重启 K8s 或节点都无效。

> [!warning] 注意
> 强制删除前建议先排查并清理 namespace 中的残留资源，确认无法自然释放后再使用强制手段。

### 原理

Namespace 控制器需要先发现并删除命名空间中的对象。APIService 不可用、资源发现失败、残留对象的 finalizer 无法完成，都会阻塞这个过程。先查看 `kubectl describe namespace "$NAMESPACE"` 的 Conditions，再枚举残留对象并修复对应控制器。Namespace 使用的 `spec.finalizers` 与普通对象的 `metadata.finalizers` 需要区分。

下面保留 `/finalize` 接口的人工恢复示例。只有确认遗留资源及外部依赖已处理，并明确接受残留对象风险后才使用；强行置空可能留下不可见或孤立资源，不等于完成清理。

### 手动方式

```sh
# 1. 开启 API 代理（新窗口保持运行）
kubectl proxy
# Starting to serve on 127.0.0.1:8001

# 2. 新开终端，导出 namespace JSON 并清空 finalizers
kubectl get namespace $NAMESPACE -o json | jq '.spec.finalizers = []' > temp.json

# 3. 发送 PUT 请求完成删除
curl --fail --show-error -H "Content-Type: application/json" -X PUT --data-binary @temp.json \
  127.0.0.1:8001/api/v1/namespaces/$NAMESPACE/finalize
```

### 将人工恢复步骤写成脚本

> 来源：[实用脚本：强制删除K8s命名空间（Terminating状态）](https://mp.weixin.qq.com/s/ERIZaE08tGUtd5fs9YvR5Q)

前置条件：需要先在另一个终端执行 `kubectl proxy` 保持运行，且需安装 `jq`。

```sh
#!/bin/bash
set -euo pipefail
# deleteNameSpace.sh - 强制删除 Terminating 状态的 namespace
# 用法: bash deleteNameSpace.sh <namespace-name>

NAMESPACE="${1:-}"

if [ -z "$NAMESPACE" ]; then
    echo "请传入要删除的 namespace 名称："
    read -r NAMESPACE
fi

echo "您将要删除的 namespace 名称是：$NAMESPACE"

# 导出 JSON 并清空 finalizers
kubectl get namespace "$NAMESPACE" -o json | jq '.spec.finalizers = []' > temp.json

# 通过 API 发送 PUT 请求完成删除
curl --fail --show-error -H "Content-Type: application/json" -X PUT \
  --data-binary @temp.json \
  "127.0.0.1:8001/api/v1/namespaces/$NAMESPACE/finalize"

# 验证结果；连接、权限等查询错误必须单独报告
if ! REMAINING=$(kubectl get namespace "$NAMESPACE" --ignore-not-found -o name); then
    echo "查询失败，请检查 API 连接和权限，不能据此判断已删除"
    exit 1
fi
if [ -n "$REMAINING" ]; then
    echo "命名空间仍然存在：$NAMESPACE"
    exit 1
fi
echo "命名空间对象已不存在：$NAMESPACE"
# 仍需按事先记录核对外部资源及孤立对象
```

使用：

```sh
# 终端 1：开启代理
kubectl proxy

# 终端 2：执行脚本
bash deleteNameSpace.sh knative-eventing
```

## 特殊namespace

### kube-node-lease

- 每个节点在其中维护 Lease 对象作为轻量心跳；kubelet 续约 Lease，控制平面的节点生命周期控制器结合心跳与 Node 状态判断节点健康。API Server 提供存取接口，不自行运行节点健康判定循环。
