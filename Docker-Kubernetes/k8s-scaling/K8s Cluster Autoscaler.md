---
title: "K8s Cluster Autoscaler"
source: "https://mp.weixin.qq.com/s/A0QZw99L8ngrvDZV-ocrlQ"
author:
  - "[[LinuxLuMing]]"
published:
created: 2026-10-11
description: "从Pending Pod触发扩容、Node Group选择、缩容阻塞，到HPA联动、参数调优、监控排障和生产回滚，一篇讲清节点自动扩缩容"
tags:
  - "clippings"
---
LinuxLuMing · *2026年8月28日 09:04*

HPA 能自动增加 Pod，但集群没有空闲资源时，新 Pod 会一直处于 Pending。Cluster Autoscaler（简称 CA）负责节点层面的扩缩容：根据 Pod 能否被调度，自动增加或回收 Worker 节点。

CA 不会因为实时 CPU 使用率升高就直接增加节点，也不是通用的虚拟机管理平台。

## 一、Cluster Autoscaler解决什么问题

典型扩容链路：

```
业务流量升高
  ↓
HPA把Deployment从5副本扩到15副本
  ↓
集群剩余资源不足，8个Pod处于Pending
  ↓
Cluster Autoscaler模拟调度
  ↓
发现增加node-group-a的节点可以容纳这些Pod
  ↓
调用云平台或节点组API增加虚拟机
  ↓
新节点加入集群并变为Ready
  ↓
Pending Pod完成调度
```

缩容过程与之相反：HPA 减少 Pod 后，一些节点长期处于低利用状态。CA 确认节点上的 Pod 可以安全迁移后，执行驱逐并删除节点。

CA 只管理预先配置好的 Node Group。在 AWS 上通常对应 Auto Scaling Group，在 Azure 上对应 VMSS，在 GCP 上对应 MIG。裸机或普通 KVM 环境如果没有集成 Cluster API、云平台接口等能力，CA 就无法创建虚拟机。

## 二、它和HPA、VPA有什么区别

| 组件 | 调整对象 | 主要依据 | 解决的问题 |
| --- | --- | --- | --- |
| HPA | Pod副本数 | CPU、内存、QPS等指标 | 业务并发变化 |
| VPA | Pod requests/limits | 历史资源使用 | 单个Pod规格不合适 |
| Cluster Autoscaler | Worker节点数 | 是否存在可通过加节点解决的Pending Pod | 集群容量不足 |

生产环境中最常见的组合是：

```
HPA扩Pod → Pod Pending → CA扩节点
HPA缩Pod → 节点变空 → CA缩节点
```

CA 判断是否扩容时，主要看 Pod 的 `requests` 和调度约束，不直接看实际 CPU 使用率。requests 配置不准确，扩缩容决策也会出现偏差。

```
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: "1"
    memory: 1Gi
```

requests 太低时，CA 可能认为现有节点足以容纳 Pod，实际运行后却出现资源争抢；requests 太高时，CA 会频繁增加节点，成本上升，缩容也更困难。

## 三、扩容决策是怎么做的

CA 定期检查无法调度的 Pod。发现 Pending Pod 后，它会先模拟：如果给某个 Node Group 增加一台同规格节点，这个 Pod 能否调度到新节点上。

模拟时会考虑：

- CPU、内存、临时存储和扩展资源requests
- nodeSelector和nodeAffinity
- taint与toleration
- Pod反亲和、拓扑分布
- PVC所在可用区和Volume限制
- Node Group的标签、污点和实例规格
- Node Group的min/max边界

只有新增节点能够解决调度问题时，CA 才会扩容。

以下 Pending 原因通常无法通过扩容解决：

```
PVC或StorageClass配置错误
Pod要求一个不存在的节点标签
Pod没有容忍节点组的污点
Pod requests超过节点组最大机型
required反亲和条件互相冲突
镜像拉取失败或容器启动失败
节点组已经达到maxSize
云账号配额或IP地址耗尽
```

排查 CA 不扩容时，应先检查 Pod：

```
kubectl describe pod <pending-pod>
```

先看 `FailedScheduling` 的具体原因，再查 CA 日志。仅凭 Pending 状态，无法判断问题是否出在节点容量上。

## 四、多个Node Group时怎么选

集群中经常同时存在不同类型的节点组：

```
general：通用计算节点
memory：大内存节点，带workload=memory污点
spot：低成本抢占式节点
system：专门运行系统组件
```

CA 通过 expander 选择要扩容的节点组，常见策略包括：

| Expander | 选择逻辑 | 适用场景 |
| --- | --- | --- |
| random | 随机选择 | 测试或无明显差异的节点组 |
| least-waste | 扩容后剩余资源最少 | 降低资源浪费 |
| most-pods | 能容纳最多待调度Pod | 优先提高调度吞吐 |
| priority | 按配置的节点组优先级 | 优先Spot、失败后回退按需实例 |

同一个 Node Group 内的节点应具有近似一致的调度属性，包括资源规格、标签和污点。如果混合实例组中的规格差异很大，CA 基于模板得到的模拟结果可能与实际启动的节点不一致。

## 五、缩容为什么比扩容谨慎

扩容要尽快为 Pending Pod 提供运行空间；缩容则需要确认节点上的 Pod 可以安全迁移。因此，CA 会检查两件事：

1. 节点利用率是否持续低于阈值。
2. 节点上的重要Pod能否被重新调度到其他节点。

常见的默认设置是：节点的 requests 利用率低于约 50%，并持续一段时间后，才成为缩容候选。具体值由参数控制，不同版本和云平台的托管实现可能有差异。

以下情况经常阻止缩容：

- PodDisruptionBudget不允许再中断副本
- 没有Deployment、StatefulSet等控制器管理的裸Pod
- 使用hostPath、local PV或不安全的本地临时数据
- Pod带有 `safe-to-evict: "false"`
- nodeSelector、亲和性或资源条件导致Pod无处可迁
- kube-system关键Pod缺少足够的PDB保护
- 节点被标记为禁止缩容

```
# 禁止CA缩容指定节点
kubectl annotate node worker-1 \
  cluster-autoscaler.kubernetes.io/scale-down-disabled=true

# 允许安全驱逐指定Pod（确认数据可丢或可恢复后再用）
kubectl annotate pod <pod-name> \
  cluster-autoscaler.kubernetes.io/safe-to-evict=true
```

不要为了让缩容成功，批量给所有 Pod 添加 `safe-to-evict=true`。这会绕过本地数据等保护条件，可能造成数据丢失。

## 六、PDB和优雅终止怎么影响缩容

CA 删除非空节点时，会通过 Eviction API 驱逐 Pod，并遵守 PodDisruptionBudget 的约束。

```
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: web
```

如果业务只有 2 个 Ready 副本，且设置了 `minAvailable: 2`，允许中断数就是 0，所在节点无法安全缩容。

检查：

```
kubectl get pdb -A
kubectl describe pdb web-pdb
```

Pod 还需要正确处理 SIGTERM：

```
spec:
  terminationGracePeriodSeconds: 30
  containers:
  - name: web
    lifecycle:
      preStop:
        exec:
          command: ["sh", "-c", "sleep 10"]
```

CA 发起驱逐后，应用仍需要完成终止流程：先停止接收新请求，处理完在途请求，再退出进程。不能把驱逐当成可以立即断电的信号。

## 七、生产部署的关键配置

CA 通常以 Deployment 运行在集群内，通过 leader election 保证多副本部署时只有一个实例执行扩缩容。增加 CA 副本不会提升扩缩容处理吞吐。

**版本必须与 Kubernetes 小版本匹配。** 例如，Kubernetes 1.30 优先使用 CA 1.30.x。跨版本兼容没有官方测试保证。

Helm 部署的通用形式：

```
helm repo add autoscaler https://kubernetes.github.io/autoscaler
helm repo update

helm upgrade --install cluster-autoscaler \
  autoscaler/cluster-autoscaler \
  -n kube-system \
  --set cloudProvider=<aws|azure|gce|clusterapi> \
  --set autoDiscovery.clusterName=<cluster-name> \
  --set image.tag=v<与K8s匹配的版本>
```

上述命令是通用部署骨架。要让 CA 能够扩容节点，还需要满足三项前置条件：

1. 云平台已经创建Node Group，并配置min/max范围。
2. CA的ServiceAccount拥有读取和修改节点组容量的最小权限。
3. 节点组设置了正确的自动发现标签、节点标签和污点模板。

以 AWS 自动发现为例，节点组通常需要以下标签：

```
k8s.io/cluster-autoscaler/enabled
k8s.io/cluster-autoscaler/<cluster-name>
```

权限必须限定到当前集群的节点组，避免 CA 误操作其他集群的 Auto Scaling Group。

## 八、常用参数怎么调

生产环境中常用的参数如下：

| 参数 | 作用 | 调整风险 |
| --- | --- | --- |
| `--scan-interval` | 检查集群状态的周期 | 太短会增加API调用和云平台压力 |
| `--scale-down-utilization-threshold` | 缩容利用率阈值 | 太高会频繁迁移Pod |
| `--scale-down-unneeded-time` | 节点持续闲置多久才缩容 | 太短容易抖动 |
| `--scale-down-delay-after-add` | 扩容后暂停缩容的时间 | 太短可能刚扩就缩 |
| `--max-node-provision-time` | 等待新节点就绪的最长时间 | 应覆盖云平台实际启动时长 |
| `--expander` | 多节点组选择策略 | 会影响成本和容量利用率 |
| `--balance-similar-node-groups` | 在相似节点组间平衡 | 多可用区节点组常用 |

建议从默认值开始，根据实际日志和监控调整。不要为了加快扩容而一味缩短等待时间：云平台创建虚拟机、安装组件和拉取镜像都需要时间。

## 九、为什么业务高峰还是扩容不及时

CA 做出扩容决策只是第一步。完整的扩容延迟包括：

```
发现Pending Pod
+ CA扫描周期
+ 云平台创建虚拟机
+ 节点启动和加入集群
+ CNI/CSI/DaemonSet初始化
+ 业务镜像拉取
+ 应用启动并通过readiness
```

整个过程可能需要数分钟，应对突发流量不能完全依赖临时增加节点。

常用优化：

### 1\. 资源预留

运行一批低优先级 Pause Pod，为业务预留缓冲资源。高优先级业务 Pod 到来时，会抢占 Pause Pod 占用的资源，先完成调度；进入 Pending 状态的 Pause Pod 随后触发 CA 补充节点。

### 2\. 镜像预热

大镜像在新节点上首次拉取可能需要几分钟。可以用 DaemonSet 预拉取核心镜像，或制作包含常用镜像层的节点模板。

### 3\. 定时预扩容

如果每天有固定的业务高峰，提前增加节点组的最小容量，比高峰到来后临时扩容更可靠。

### 4\. 准确配置requests

CA 根据调度信息作出决策。requests 偏离实际需求时，仅靠调整扩容参数无法解决问题。

## 十、故障排查：为什么不扩、为什么不缩

### 不扩容

```
kubectl get pods -A --field-selector=status.phase=Pending
kubectl describe pod <pending-pod>
kubectl logs -n kube-system \
  deployment/cluster-autoscaler --tail=300
kubectl get configmap cluster-autoscaler-status \
  -n kube-system -o yaml
```

重点搜索：

```
NotTriggerScaleUp
No expansion options
max node group size reached
Failed to increase node group size
Insufficient cpu / memory
node affinity / taint mismatch
```

### 不缩容

```
kubectl logs -n kube-system \
  deployment/cluster-autoscaler --tail=500 | \
  grep -iE 'scale.down|unneeded|unremovable'

kubectl get pdb -A
kubectl get pods -A -o wide --field-selector spec.nodeName=<node>
kubectl describe node <node>
```

重点检查 PDB、本地存储、裸 Pod、亲和性和禁止缩容注解，以及其他节点是否有足够空间满足 Pod 的 requests。

## 十一、监控和告警

CA 提供 Prometheus 格式的指标，至少应监控以下内容：

- 当前是否存在未调度Pod
- 最近一次扩容或缩容是否成功
- Node Group是否达到最大容量
- CA自身是否正常运行并完成循环
- 新节点从创建到Ready的耗时
- 不可移除节点数量及原因

日志中长期出现“达到 maxSize”却没有告警，是最常见的容量治理漏洞。如果等到业务 Pod 进入 Pending 才发现节点组上限太小，就错过了提前处理容量问题的时机。

## 十二、Cluster Autoscaler还是Karpenter

| 维度 | Cluster Autoscaler | Karpenter |
| --- | --- | --- |
| 节点来源 | 预先配置的Node Group | 根据约束动态选择节点规格 |
| 云平台覆盖 | 更广 | 取决于对应Provider实现 |
| 使用方式 | 调整节点组容量 | 直接管理更完整的节点生命周期 |
| 适合场景 | 已有成熟节点组体系、需要稳妥接入 | 机型多、Spot多、希望快速选型和整合 |

如果公司已经围绕 ASG、VMSS 等节点组建立了权限、网络和成本体系，CA 通常更容易落地。如果需要根据 Pending Pod 动态选择实例规格，快速替换和整合节点，可以进一步评估 Karpenter。

## 十三、上线、验证与回滚

### 上线前

```
1. 确认CA版本与K8s小版本匹配
2. Node Group的min/max和自动发现标签正确
3. 云权限遵循最小权限
4. 核心业务有合理PDB和优雅终止
5. requests经过真实数据校准
```

### 验证扩容

创建一个测试 Deployment，其 requests 超过当前剩余容量，但能被新节点容纳。确认以下过程：

```
Pod出现FailedScheduling
→ CA日志出现扩容决策
→ Node Group desired增加
→ 新节点Ready
→ Pod完成调度
```

### 验证缩容

删除测试负载后观察：

```
节点进入unneeded候选
→ CA执行Pod驱逐
→ PDB保持满足
→ 节点从集群和云平台节点组删除
```

### 回滚

```
# 暂停CA，不再执行新的扩缩容决策
kubectl scale deployment cluster-autoscaler \
  -n kube-system --replicas=0

# 将Node Group的期望容量恢复到固定值
# 具体命令由云平台决定

# 删除或回滚Helm Release
helm rollback cluster-autoscaler <revision> -n kube-system
```

回滚 CA 不会自动恢复已经删除的节点。关闭 CA 前，应确认当前节点容量足以承载业务，并把 Node Group 的最小值和期望值恢复到安全水平。

## 总结

Cluster Autoscaler 的核心逻辑很直观：为所有可调度的 Pod 提供可用节点，同时回收长期不需要的节点。生产环境能否稳定扩缩容，取决于 requests 是否准确、Node Group 模板是否一致、PDB 是否合理、本地存储能否迁移，以及云权限和配额是否正确。

生产使用时，需要注意以下三点：

```
扩容看Pending Pod，不看实时CPU。
缩容看Pod能否安全迁移，不只看节点空不空。
突发流量不能只靠临时加节点，必须保留容量缓冲。
```

## 参考资料

- [Kubernetes 官方文档：Node Autoscaling](https://kubernetes.io/docs/concepts/cluster-administration/node-autoscaling/)
- [Kubernetes Autoscaler 官方 FAQ](https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/FAQ.md)
- [Cluster Autoscaler 官方 Helm Chart](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler/charts/cluster-autoscaler)
