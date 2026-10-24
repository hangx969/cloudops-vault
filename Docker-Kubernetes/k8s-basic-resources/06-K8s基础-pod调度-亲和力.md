---
title: K8s基础-Pod调度-亲和力
tags:
  - kubernetes
  - k8s-basics
aliases:
  - k8sPod调度亲和力
---

# K8s基础-Pod调度-亲和力

给应用配置多个副本后，还需要确认一件事：这些 Pod 最终运行在哪些节点上？如果副本集中在同一台机器，节点故障时，它们会一起受到影响。对于频繁访问缓存的应用，节点之间的网络距离也可能影响访问延迟。

集群规模变大后，节点之间既有 GPU、SSD 等硬件差异，也可能按用途分成不同节点池。例如，承载入口流量的专用节点，就需要与普通业务区分开。副本数量之外，还需要描述应用对部署位置的要求。

Kubernetes 允许我们把要求写进 Pod 配置：哪些节点必须满足条件，哪些位置可以优先考虑，哪些副本需要分开，以及哪些 Pod 可以使用专用节点。调度器会结合这些规则和资源情况，为尚未绑定节点的 Pod 选择位置。

## 一、调度器怎样为 Pod 选择节点

在默认调度流程中，kube-scheduler 会先过滤掉不满足要求的节点，再对剩余候选节点评分，最后选出节点并完成绑定。资源请求、节点标签、亲和性、污点等条件，都会影响这个过程。

因此，调度结果可以通过声明式配置来控制。常见配置各自回答不同的问题：

| 配置 | 要表达的需求 |
| --- | --- |
| `nodeSelector`、`nodeAffinity` | 节点需要具备什么属性？ |
| `podAffinity`、`podAntiAffinity` | 应当靠近哪些 Pod，或与哪些 Pod 分开？ |
| `topologySpreadConstraints` | 副本在节点、可用区之间应当怎样分布？ |
| 污点与容忍 | 节点是否接受这个 Pod？ |
| `nodeName` | 直接指定节点，并绕过调度器。 |

这些配置可以配合使用。例如，一个 Pod 既要求节点带有 GPU 标签，又需要容忍 GPU 节点上的污点。

一个具体的 Pod 在其生命周期中只会被调度一次。节点故障后的服务恢复，通常由 Deployment、StatefulSet 等控制器创建替代 Pod，再由调度器为新 Pod 选择节点。原来的 Pod 不会被直接搬到另一台机器。[Kubernetes 官方文档：Pod 生命周期](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)

## 二、先用标签描述节点和 Pod

调度规则需要依据具体信息做判断。Kubernetes 中最常用的信息来源就是标签（Label），它以键值对的形式附着在 Node、Pod、Service 等资源上。

### 标签与选择器

标签可以表达版本、环境和应用层次：

| 用途 | 示例 |
| --- | --- |
| 版本 | `version=release`、`version=stable` |
| 环境 | `environment=dev`、`environment=test`、`environment=pro` |
| 应用层次 | `tier=frontend`、`tier=backend` |

选择器（Label Selector）负责根据标签找到对象。等值选择支持 `environment=dev`、`version!=stable`；集合选择支持 `environment in (dev,test)`，还可以判断某个标签是否存在。各配置字段支持的选择器语法并不完全相同，例如 `nodeSelector` 只接受键值相等的条件。

以 `dev` 命名空间中已经存在的 Pod 为例，可以添加、更新、删除标签，也可以按标签查询：

```bash
kubectl label pod pod-test -n dev version=1.0 # 打标签
kubectl label pod nginx -n dev version=2.0 --overwrite=true #更新标签
kubectl label pod nginx -n dev version- # 删掉key为version的标签
kubectl get pod -n dev --show-labels # 看标签
kubectl get pod -l "version=2.0" -n dev --show-labels
kubectl get pods -l version # 列出默认名称空间下标签key是version的pod，不显示标签
kubectl get pod -L version # 为所有列出的Pod增加version列，不按该标签过滤
```

上面最后一条命令中的 `-L version` 只增加输出列。如果还希望过滤出带有该标签的 Pod，需要同时使用 `-l`：

```bash
kubectl get pod -l version -L version
```

节点亲和性检查 Node 的标签，Pod 亲和性检查其他 Pod 的标签。给 Pod 加上 `disk=ceph` 并不会让它自动进入同名标签的节点。

### 拓扑域：怎样描述“同一个位置”

当需求从“找一台带标签的节点”变成“和某组 Pod 放在同一个可用区”时，还需要定义位置的范围。

拓扑键（Topology Key）是节点标签的键。对于某个拓扑键，具有相同标签值的节点属于同一个拓扑域（Topology Domain）。这个域可以是一台主机、一个可用区，也可以是管理员定义的机房或子网。

| 划分方式 | 拓扑键 | 标签值示例 |
| --- | --- | --- |
| 主机 | `kubernetes.io/hostname` | `node-01`、`node-02` |
| 可用区 | `topology.kubernetes.io/zone` | `zone-a`、`zone-b` |
| 地域 | `topology.kubernetes.io/region` | `beijing`、`nanjing` |
| 自定义机房 | `zone` | `chaoyang`、`haidian` |
| 自定义子网 | `subnet` | `subnet-a`、`subnet-b` |

例如，`node-01` 和 `node-02` 的可用区标签都是 `zone-a`。按主机划分时，它们属于两个域；按可用区划分时，它们属于同一个域。

`kubernetes.io/hostname` 是常见的节点标签，但它的值不保证等于 Node 对象的名称。云环境通常会填充标准地域、可用区标签，自建集群则需要检查或维护这些信息。标签也不会自动发现真实的机房、子网关系，使用自定义键时，要确保它们与实际环境一致。

自定义的 `zone` 与标准标签 `topology.kubernetes.io/zone` 是不同的键，配置和节点上的标签必须对应。尤其使用 Pod 反亲和性时，相关节点应一致地具备所选拓扑键，避免缺失标签造成非预期结果。

## 三、从简单的节点选择开始

如果只是要求 Pod 运行在带有某个标签的节点上，`nodeSelector` 就能满足需求。

### nodeSelector：匹配节点标签

先查看节点标签，再给目标节点添加一个自定义标签：

```bash
kubectl get nodes --show-labels #看node标签
kubectl label nodes node-01 disk=ceph #给node打标签
```

然后在 Pod 的 `spec.nodeSelector` 中声明相同的键值对：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo-pod
  namespace: default
  labels:
    app: tomcat
    env: dev
spec:
  nodeSelector:
    disk: ceph
  containers:
  - name:  tomcat-pod-java
    ports:
    - containerPort: 8080
    image: tomcat:8.5-jre8-alpine
    imagePullPolicy: IfNotPresent
  - name: busybox
    image: busybox:latest
    command:
    - "/bin/sh"
    - "-c"
    - "while true; do echo hello; sleep 10; done"
```

这里的 `disk=ceph` 只是一条由管理员维护的标签。它用于筛选节点，并不会为 Pod 挂载 Ceph 存储。

`nodeSelector` 是硬约束。若写了多个键值对，节点必须全部满足；若没有符合条件且满足其他调度要求的节点，Pod 就会保持未调度状态，通常表现为 `Pending`。即使标签匹配，节点上的资源、污点等条件仍然需要通过检查。

### nodeName：直接指定节点

`spec.nodeName` 可以直接填写 Node 对象的名称：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo-pod
  namespace: default
  labels:
    app: tomcat
    env: dev
spec:
  nodeName: node-01
  containers:
  - name:  tomcat-pod-java
    ports:
    - containerPort: 8080
    image: tomcat:8.5-jre8-alpine
    imagePullPolicy: IfNotPresent
  - name: busybox
    image: busybox:latest
    command:
    - "/bin/sh"
    - "-c"
    - "while true; do echo hello; sleep 10; done"
```

这份配置指定了 `node-01`。`nodeName` 非空时，调度器会跳过这个 Pod，由目标节点上的 kubelet 尝试接纳它。这会绕过正常的调度选择，不能把 `nodeName` 与 `nodeSelector`、亲和性叠加后，期待调度器继续验证这些组合条件。节点不存在或无法接纳 Pod 时，Pod 仍然可能无法运行。

它还会绕过调度器对 `NoSchedule` 污点的过滤；若节点上存在不被容忍的 `NoExecute` 污点，Pod 仍会被驱逐。普通业务部署通常使用 `nodeSelector` 或节点亲和性来选择节点，`nodeName` 更适合需要直接绑定的特定场景。[Kubernetes 官方文档：为 Pod 指定节点](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodename)

## 四、节点亲和性：表达“必须”与“尽量”

`nodeSelector` 很适合简单的等值匹配。如果需要表达“SSD 或 NVMe 节点都可以”，或者“优先放在某类节点，没有合适的也可以运行”，就需要 `nodeAffinity`。

Pod 的亲和性配置位于 `spec.affinity`，包含 `nodeAffinity`、`podAffinity` 和 `podAntiAffinity`。可以用以下命令查看字段说明：

```bash
kubectl explain pods.spec.affinity
```

```bash
kubectl explain pods.spec.affinity.nodeAffinity
# preferredDuringSchedulingIgnoredDuringExecution <[]Object>
# requiredDuringSchedulingIgnoredDuringExecution <Object>
```

### 先读懂两种规则类型

亲和性规则中最常见的两个字段虽然很长，但可以拆开理解：

| 字段 | 调度时的含义 |
| --- | --- |
| `requiredDuringSchedulingIgnoredDuringExecution` | 必须满足，属于硬约束。没有合适节点时无法调度。 |
| `preferredDuringSchedulingIgnoredDuringExecution` | 尽量满足，属于软偏好。不满足这一偏好也可以继续考虑其他节点。 |

`DuringScheduling` 表示在调度时判断，`IgnoredDuringExecution` 表示 Pod 运行后，即使相关标签变化导致规则不再满足，也不会仅因此驱逐已经运行的 Pod。

软偏好只影响候选节点的评分，无法绕过资源不足、硬亲和性不匹配、未容忍污点等限制。

### 硬亲和性：节点必须满足条件

假设节点已经带有自定义的 `zone=foo` 或 `zone=bar` 标签，下面的 Pod 只允许进入这两类节点：

```bash
kubectl explain pods.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-node-affinity-demo
  namespace: default
  labels:
    app: bb
    tier: ft
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: zone # 硬亲和性 - 必须调度到label是zone=foo或zone=bar的node
            operator: In
            values:
            - foo
            - bar
  containers:
  - name: busybox
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    command:
    - "/bin/sh"
    - "-c"
    - "while true; do echo hello; sleep 10; done"
```

`operator: In` 表示标签值在 `values` 中。这里同一条表达式中的 `foo`、`bar` 是可选值，匹配任意一个即可。

### 软亲和性：给符合偏好的节点加分

软亲和性为每条规则设置 `weight`，取值为 1 到 100。下面分别为 `zone1` 和 `zone2` 两组标签设置了偏好：

```bash
kubectl explain pods.spec.affinity.nodeAffinity.preferredDuringSchedulingIgnoredDuringExecution
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-node-affinity-demo
  namespace: default
  labels:
    app: bb
    tier: ft
spec:
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - preference:
          matchExpressions:
          - key: zone1
            operator: In
            values:
            - foo1
            - bar1
        weight: 10
      - preference:
          matchExpressions:
          - key: zone2
            operator: In
            values:
            - foo2
            - bar2
        weight: 20 # 匹配该规则时贡献权重，最终位置还取决于综合评分。
  containers:
  - name: busybox
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    command:
    - "/bin/sh"
    - "-c"
    - "while true; do echo hello; sleep 10; done"
```

节点匹配多条偏好时，相应权重会累计，并参与调度器的综合评分。因此，权重较高能增强这条偏好的影响，但不能保证某个节点一定胜出。

上面的两个节点亲和性 Pod 示例使用相同名称，用于对照硬规则与软规则。实际复现时可选择其一；若要同时观察，应使用不同的 Pod 名称。已经创建的 Pod 通常不能直接修改这些调度字段来触发重新调度。

### 多个条件怎样组合

阅读节点亲和性配置时，可以按以下层次判断：

- `nodeSelector` 与节点亲和性中的硬约束需要同时满足；软规则继续参与评分。
- 多个 `nodeSelectorTerms` 之间是“或”，满足其中一个 term 即可。
- 同一个 term 中的多个 `matchExpressions` 之间是“且”，节点必须全部满足。

节点亲和性支持 `In`、`NotIn`、`Exists`、`DoesNotExist`、`Gt`、`Lt` 等操作符。其中，`NotIn`、`DoesNotExist` 可以表达排除某类节点的需求。Kubernetes 没有名为 `nodeAntiAffinity` 的 Pod 配置字段。

### 把计算服务放到指定硬件上

如果应用要求使用 SSD 或 NVMe，可以用节点标签描述磁盘类型，再用硬亲和性限制节点范围：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: compute
spec:
  replicas: 2
  selector:
    matchLabels:
      app: compute
  template:
    metadata:
      labels:
        app: compute
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: disktype
                operator: In
                values:
                - ssd
                - nvme
      containers:
      - name: compute
        image: nginx:1.15.12
```

这里的 `disktype` 只描述磁盘类型。CPU、内存等计算能力需要另外评估，标签本身不会分配或预留资源。

如果磁盘类型只是偏好，可以把上例 `spec.template.spec.affinity` 下的 `nodeAffinity` 替换为：

```yaml
nodeAffinity:
  preferredDuringSchedulingIgnoredDuringExecution:
  - weight: 100
    preference:
      matchExpressions:
      - key: disktype
        operator: In
        values:
        - ssd
        - nvme
```

若希望 SSD 的偏好强于 NVMe，可以为两条规则设置不同权重。下面是放在 `spec.template.spec` 下的配置片段：

```yaml
affinity:
  nodeAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      preference:
        matchExpressions:
        - key: disktype
          operator: In
          values:
          - ssd
    - weight: 50
      preference:
        matchExpressions:
        - key: disktype
          operator: In
          values:
          - nvme
```

### 尽量避开低性能节点

如果已用 `performance=low` 标识不希望优先使用的节点，可以使用 `NotIn`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: compute-intensive-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: compute-intensive
  template:
    metadata:
      labels:
        app: compute-intensive
    spec:
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - key: performance
                operator: NotIn
                values:
                - low
      containers:
      - name: compute-intensive
        image: nginx:1.15.12
```

这条软规则会提高“不带 `performance=low`”这一条件的偏好。没有 `performance` 标签的节点也能匹配 `NotIn`，所以如果希望只选择已确认性能等级的节点，还需要配合 `Exists` 或明确的 `In` 条件。

## 五、Pod 亲和性：决定和谁靠近、和谁分开

节点亲和性依据节点属性选择位置。有些需求还取决于其他应用的位置：访问频繁的应用与缓存希望靠近，同一应用的副本则希望分开，以降低单个故障域同时影响多个副本的风险。

这时需要把 Pod 选择器和拓扑域结合起来：`labelSelector` 选择要参照的 Pod，`topologyKey` 定义“同一个位置”的范围。

### podAffinity：靠近匹配的 Pod

先创建一个带有 `app=bb` 标签的 Pod：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-pod-affinity-1
  namespace: default
  labels:
    app: bb
    tier: ft
spec:
  containers:
  - name: busybox
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    command:
    - "/bin/sh"
    - "-c"
    - "while true; do echo hello; sleep 10; done"
```

然后创建第二个 Pod，让它与 `default` 命名空间中匹配 `app=bb` 的 Pod 位于同一台主机：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-pod-affinity-2
  namespace: default
  labels:
    app: bb
    tier: ft
spec:
  affinity:
    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution: # 硬亲和性：目标拓扑域中必须存在匹配的Pod
      - labelSelector: # 这个pod要跟app=bb的pod做亲和性
          matchExpressions:
          - {key: app, operator: In, values: ["bb"]}
        topologyKey: kubernetes.io/hostname # 怎么定义同一个位置？对于key=kubernetes.io/hostname的node，value相同就算同一位置 ==> 也就是跟匹配的pod在相同的node上算相同的位置。
  containers:
  - name: busybox
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    command:
    - "/bin/sh"
    - "-c"
    - "while true; do echo hello; sleep 10; done"
```

`topologyKey: kubernetes.io/hostname` 将“同一个位置”限定为主机。在这个例子中，第二个 Pod 会尝试进入第一个 Pod 所在的节点；该节点还必须满足资源和其他调度条件。如果把拓扑键换成可用区标签，位置范围就会变成同一个可用区。

`podAffinity` 同样有硬、软两种规则，可以通过命令查看：

```bash
kubectl explain pods.spec.affinity.podAffinity
# 同样分为硬亲和性和软亲和性：
# preferredDuringSchedulingIgnoredDuringExecution <[]Object>
# requiredDuringSchedulingIgnoredDuringExecution <[]Object>
```

### podAntiAffinity：避开匹配的 Pod

反亲和性使用相同的选择方式，但要求或倾向于避开已有匹配 Pod 的拓扑域。下面这份完整配置表达“尽量不要与 `default` 命名空间中 `app=bb` 的 Pod 放在同一台主机”：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-pod-anti-affinity-demo
  namespace: default
  labels:
    app: bb
    tier: ft
spec:
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values: ["bb"]
          namespaces:
          - default
          topologyKey: kubernetes.io/hostname
  containers:
  - name: busybox
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    command:
    - "/bin/sh"
    - "-c"
    - "while true; do echo hello; sleep 10; done"
```

这里使用软反亲和性。只有一个可用节点时，这条偏好本身不会阻止调度。若使用硬反亲和性，找不到满足要求的拓扑域就会等待。

### 命名空间决定匹配范围

Pod 标签属于各自的命名空间，因此 Pod 亲和性还需要明确在哪些命名空间中寻找参照对象：

- 不设置 `namespaces` 和 `namespaceSelector`，或者 `namespaces: []` 且不设置 `namespaceSelector` 时，默认匹配规则所属 Pod 的命名空间。
- 设置 `namespaces: [default]` 时，显式指定 `default` 命名空间。
- `namespaceSelector` 根据命名空间自身的标签选择命名空间；`namespaceSelector: {}` 会匹配所有命名空间。
- 同时设置 `namespaces` 和 `namespaceSelector` 时，匹配范围取两者的并集。已经指定 `namespaces: [default]`，再加上空选择器 `{}`，范围仍然会扩大到所有命名空间。

`namespaces`、`namespaceSelector` 和 `topologyKey` 都应放在对应的 Pod affinity term 内。软规则中，它们位于 `podAffinityTerm` 下，不能与 `weight` 同级。

Pod 亲和性需要考虑已有 Pod 的分布，大范围匹配会增加调度计算量。能限定应用标签和命名空间时，应尽量限定，特别是在节点、Pod 数量较多的集群中。[Kubernetes 官方文档：Pod 间亲和性与反亲和性](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#inter-pod-affinity-and-anti-affinity)

## 六、把规则用于副本分布和服务协同

理解了“选哪些 Pod”和“按什么范围判断位置”，就可以把反亲和性用于副本隔离，把亲和性用于服务协同。

### 同一个应用必须部署在不同主机

下面的 Deployment 有两个副本，通过硬反亲和性禁止相同应用的 Pod 位于同一个主机拓扑域：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: diff-nodes
spec:
  selector:
    matchLabels:
      app: diff-nodes
  replicas: 2
  template:
    metadata:
      labels:
        app: diff-nodes
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchExpressions:
                  - key: app
                    operator: In
                    values:
                      - diff-nodes # 当前ns中具有app=diff-nodes标签的pod不允许被调度到hostname相同的节点上
              topologyKey: kubernetes.io/hostname
              namespaces: [] # 空表示当前namespace
      containers:
        - name: diff-nodes
          image: nginx:1.15.12
```

在没有其他冲突的前提下，这两个副本至少需要两台可用节点。如果集群只有一台符合要求的节点，第二个副本会保持未调度。把“必须分开”写成硬规则之前，需要同时考虑扩容、节点故障和滚动更新时是否有足够的候选位置。

如果使用 `requiredDuringSchedulingIgnoredDuringExecution` 表达跨可用区反亲和性，还要检查集群的准入配置：启用 `LimitPodHardAntiAffinityTopology` 时，硬反亲和性的拓扑键被限制为 `kubernetes.io/hostname`。该准入插件默认未启用，实际限制以集群配置为准。[Kubernetes 官方文档：LimitPodHardAntiAffinityTopology](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#limitpodhardantiaffinitytopology)

### 同一个应用尽量部署在不同主机

如果节点不足时更希望副本先运行起来，可以改用软反亲和性：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: diff-nodes
spec:
  selector:
    matchLabels:
      app: diff-nodes
  replicas: 2
  template:
    metadata:
      labels:
        app: diff-nodes
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - diff-nodes
                topologyKey: kubernetes.io/hostname
                namespaces: []
              weight: 100
      containers:
      - name: diff-nodes
        image: nginx:1.15.12
```

这份配置优先考虑没有同应用副本的节点，但在其他调度条件都满足时，允许多个副本运行在同一节点。它降低了硬约束带来的阻塞风险，也意味着需要接受故障域可能重叠的结果。

### 同一个应用尽量分布在不同机房

如果节点上已经用自定义的 `zone` 标签区分机房，把拓扑键改为 `zone`，就可以表达机房级别的分散偏好：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: diff-zone
spec:
  selector:
    matchLabels:
      app: diff-zone
  replicas: 3
  template:
    metadata:
      labels:
        app: diff-zone
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - diff-zone
                topologyKey: zone
                namespaces: []
              weight: 100
      containers:
        - name: diff-nodes
          image: nginx:1.15.12
```

若集群使用标准可用区标签，应将这里的拓扑键改为 `topology.kubernetes.io/zone`，并检查候选节点是否具备该标签。

### 应用和缓存尽量放在同一个可用区

对于频繁访问缓存的应用，可以让应用 Pod 优先靠近已运行的缓存 Pod。假设缓存带有 `app=cache` 标签，节点上的 `zone` 标签表示可用区：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      affinity:
        podAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions: # 这个deployment的pod尽量和app=cache的pod分布在zone标签和值相同的节点上
                - key: app
                  operator: In
                  values:
                  - cache
              topologyKey: zone
      containers:
      - name: my-app
        image: nginx:1.15.12
```

该规则会让 `my-app` 的新 Pod 优先考虑同一命名空间中存在缓存 Pod 的可用区。若希望缓存的新 Pod 也考虑应用位置，可以在缓存的 Pod 模板中增加对应的软亲和性；是否需要双向配置，取决于两者的部署顺序和扩缩容方式。

位置接近只影响 Pod 的部署关系。若一个 Service 同时选中了多个可用区的缓存 Pod，调度亲和性不会自动保证应用请求命中本可用区的缓存，访问路径还需要结合 Service 或客户端的路由方式设计。

### 需要控制数量差时，使用拓扑分布约束

反亲和性适合表达“与谁分开”。当需求是“让多个副本在节点或可用区之间尽量均衡”时，`topologySpreadConstraints` 能直接表达各域中的数量偏差。它与 `affinity` 是 PodSpec 中的独立字段，也可以配合使用。

下面的 Deployment 按主机划分拓扑域，限制新增副本带来的数量偏差：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: example-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: example
  template:
    metadata:
      labels:
        app: example
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        whenUnsatisfiable: DoNotSchedule
        topologyKey: kubernetes.io/hostname
        labelSelector:
          matchLabels:
            app: example
      containers:
      - name: example
        image: nginx:1.15.12
```

理解这份配置，需要关注以下字段：

| 字段 | 含义 |
| --- | --- |
| `topologyKey` | 按哪个节点标签划分拓扑域。 |
| `labelSelector` | 哪些 Pod 参与各域中的数量统计，通常匹配当前应用的 Pod 标签；统计范围为当前 Pod 的命名空间。 |
| `maxSkew` | `DoNotSchedule` 模式下，限制放入新 Pod 后，目标域的匹配 Pod 数与全局最小值的差。 |
| `whenUnsatisfiable` | `DoNotSchedule` 会拒绝违反该约束的调度；`ScheduleAnyway` 则作为偏好，优先选择有助于降低偏差的位置。 |

全局最小值会受符合条件的拓扑域及 `minDomains` 等配置影响。在上例中，如果三台节点都属于符合条件的域、资源也足够，三个副本可以逐步形成每台一个的分布。但 `maxSkew: 1` 本身不要求必须存在三台节点：只有一个符合条件的域且未设置更高的 `minDomains` 时，也可能容纳所有副本。

配置多条约束时，调度器会综合考虑它们，并同时满足其中的硬约束。这些规则作用于新 Pod 的调度，不会主动迁移已有 Pod 来重新平衡分布。[Kubernetes 官方文档：Pod 拓扑分布约束](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)

## 七、污点与容忍：控制节点是否接受 Pod

前面的规则主要由 Pod 声明要选择什么位置。有时还需要从节点一侧限制进入的工作负载。例如，给 GPU 节点保留容量，暂时隔离尚未验收的新节点，或在维护前停止接收普通业务 Pod。

污点（Taint）添加在节点上，容忍（Toleration）写在 Pod 中。调度器会检查 Pod 是否容忍节点上的相关污点，再结合其他条件决定能否调度。

容忍只解除对应污点的限制。一个 Pod 容忍 GPU 污点后，也可能进入没有该污点的普通节点；要指定节点范围，仍需节点选择器、节点亲和性或相应的资源请求。

### 三种 effect 分别做什么

污点通常写成 `key=value:effect`，其中 value 可以省略。污点保存在 Node 的 `spec.taints` 中，与 `metadata.labels` 是两套独立数据；添加污点不会自动添加同名标签。

| effect | 未容忍该污点的新 Pod | 节点上已存在且未容忍的 Pod |
| --- | --- | --- |
| `PreferNoSchedule` | 尽量避免进入，属于软限制。 | 不因该污点被驱逐。 |
| `NoSchedule` | 正常调度流程不允许进入。 | 不因该污点被驱逐。 |
| `NoExecute` | 不允许进入。 | 会被驱逐。 |

一个节点可以有多个污点。只容忍其中一个，并不会消除其他未被容忍的限制。三种 effect 也不存在“容忍更强的就自动兼容更弱的”这样的匹配关系。

### 添加、查看和移除污点

污点可以带 value，也可以不带。以单个节点为例：

```bash
kubectl taint node node-01 ssd=true:PreferNoSchedule
kubectl taint node node-01 ssd:PreferNoSchedule
```

如果需要对所有节点操作，可以使用 `--all`。它会扩大操作范围：

```bash
kubectl taint node ssd=true:PreferNoSchedule --all
```

查看一个节点或所有节点的污点：

```bash
kubectl get node master-01 -o=jsonpath='{.spec.taints}'
kubectl describe node master-01 | grep Taint -A 10
# 看所有节点的污点
kubectl describe node | grep Taint -A 10
```

在污点表达式后加 `-` 可以移除指定污点：

```sh
kubectl taint node node-01 ssd=true:PreferNoSchedule-
```

如果 key 和 effect 保持不变，只更新 value，可以使用 `--overwrite`：

```bash
kubectl taint node node-01 ssd=false:PreferNoSchedule --overwrite
```

例如，将 `node-02` 标记为生产专用节点，并在需要时移除该 key 对应的污点：

```bash
kubectl taint node node-02 node-type=production:NoExecute
kubectl taint node node-02 node-type-
```

这里使用了 `NoExecute`，会影响节点上未容忍该污点的已有 Pod。如果只希望阻止新的 Pod 进入，应使用 `NoSchedule`。

### 容忍怎样与污点匹配

常用的两种操作符是 `Equal` 和 `Exists`：

- `Equal` 要求 key、value 匹配；不写 operator 时，默认也是 `Equal`。
- `Exists` 只按 key 判断，不比较 value，配置中不应填写 value。
- effect 非空时，需要与污点的 effect 相同；不填写 effect 时，匹配该 key 下的所有 effect。
- key 为空时，operator 必须为 `Exists`，表示匹配所有 key。此时 effect 若非空，仍然只匹配指定 effect。

完全匹配某个污点的配置片段，放在 Pod 的 `spec` 下：

```yaml
tolerations:
- key: "taintKey"
  operator: "Equal"
  value: "taintValue"
  effect: "NoSchedule"
```

如果只关心 key 和 effect，忽略 value，应使用 `Exists`：

```yaml
tolerations:
- key: "taintKey"
  operator: "Exists"
  effect: "NoSchedule"
```

如果省略 effect，就会容忍该 key 下所有 effect 的污点：

```yaml
tolerations:
- key: "taintKey"
  operator: "Exists"
```

`Equal` 中省略 value 只表示匹配空值，不能当作忽略 value 使用。像下面这样同时省略 key 和 effect，则会容忍所有污点，范围很宽，应按工作负载的实际需要配置：

```yaml
tolerations:
- operator: "Exists"
```

### 用 tolerationSeconds 控制 NoExecute 的容忍时长

`tolerationSeconds` 用于 `NoExecute` 容忍。未设置时，这条匹配的容忍不会因时间到期而失效；设置为 3600 时，表示在匹配的污点存在期间，允许 Pod 继续绑定一段时间：

```yaml
tolerations:
- key: "taintKey"
  operator: "Equal"
  value: "taintValue"
  effect: "NoExecute"
  tolerationSeconds: 3600
```

如果污点在期限到达前被移除，Pod 不会因这次污点而被驱逐。不要将该字段用于 `NoSchedule` 来表达延迟调度。

下面是一个完整 Pod 示例，容忍 `node-type=production:NoExecute`，并将容忍时长设为 10 秒：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-toleration-demo
  namespace: default
  labels:
    app: bb
    tier: ft
spec:
  containers:
  - name: busybox
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    command:
    - "/bin/sh"
    - "-c"
    - "while true; do echo hello; sleep 10; done"
  tolerations:
  - key: "node-type"
    operator: "Equal"
    value: "production"
    effect: "NoExecute"
    tolerationSeconds: 10
```

时间到期后，这个裸 Pod 可以被驱逐，但不会由 Deployment 自动补出替代实例，因为它没有对应的工作负载控制器。需要自动恢复副本时，应在控制器的 Pod 模板中配置容忍。[Kubernetes 官方文档：污点与容忍](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)

### 常见的内置污点

Kubernetes 会根据节点状态管理一些内置污点，常见的包括：

| 污点 key | 对应状态或用途 |
| --- | --- |
| `node.kubernetes.io/not-ready` | Node 的 Ready 状态为 `False`。 |
| `node.kubernetes.io/unreachable` | Node 的 Ready 状态为 `Unknown`，控制面无法确认节点状态。 |
| `node.kubernetes.io/memory-pressure` | 内存压力。 |
| `node.kubernetes.io/disk-pressure` | 磁盘压力。 |
| `node.kubernetes.io/pid-pressure` | PID 压力。 |
| `node.kubernetes.io/network-unavailable` | 节点网络尚不可用。 |
| `node.kubernetes.io/unschedulable` | 节点被标记为不可调度。 |

节点失联或未就绪时，常见的驱逐行为与前两种状态对应的 `NoExecute` 污点有关。其他压力类污点通常通过 `NoSchedule` 影响新 Pod 的调度，但磁盘、内存压力仍可能触发 kubelet 的节点压力驱逐，不能据此认为已有 Pod 一定不受影响。

## 八、把污点与容忍用于节点管理

有了 effect 和匹配规则的基础，就可以区分几类实际需求：阻止新 Pod 进入、保留特殊节点，以及让已有 Pod 离开。选择前应先判断，操作是否需要影响当前正在运行的业务。

### 控制平面节点和待验收的新节点

控制平面节点通常承担集群管理组件，不希望普通业务进入时，可以设置 `NoSchedule` 污点。部分安装工具已经默认添加，应先检查现有配置：

```bash
kubectl taint node k8s-master01 node-role.kubernetes.io/control-plane:NoSchedule
```

如果确实需要驱逐节点上未容忍该污点的已有 Pod，才考虑 `NoExecute`：

```bash
kubectl taint node k8s-master01 node-role.kubernetes.io/control-plane:NoExecute
```

这会影响正在运行的 Pod，不能将同时添加两种 effect 作为所有集群的常规要求。

对于新节点，如果要求验收完成前不接收业务 Pod，可以预先设置临时污点：

```bash
kubectl taint node k8s-master01 new-node=true:NoSchedule
```

这里的节点名仅作示例，实际应替换为待验收节点。如果节点接入后再添加污点，需要考虑添加前已经发生调度的窗口。确实需要让未容忍的已有 Pod 离开时，可单独使用下面的操作：

```bash
kubectl taint node k8s-master01 new-node=true:NoExecute
```

验收完成后移除对应临时污点，再让节点承载业务。

### 给 GPU 等特殊节点保留容量

如果普通业务先占满 GPU 节点的 CPU 和内存，后来的 GPU 任务也可能无法运行。可以先用污点限制普通 Pod 进入：

```sh
kubectl taint node k8s-node02 gpu=true:NoSchedule
```

对于 SSD 等节点，若只需要软限制，可以使用：

```sh
kubectl taint node k8s-node02 ssd=true:PreferNoSchedule
```

需要进入 GPU 节点的 Pod，应在 `spec` 下添加匹配容忍：

```yaml
tolerations:
- key: "gpu"
  operator: "Exists"
  effect: "NoSchedule"
```

若还要求这个工作负载只运行在 GPU 节点，需同时维护节点标签：

```bash
kubectl label node k8s-node02 gpu=true
```

在 Deployment 中组合节点选择器和容忍：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpu-example
spec:
  replicas: 1
  selector:
    matchLabels:
      app: gpu-example
  template:
    metadata:
      labels:
        app: gpu-example
    spec:
      nodeSelector: # 根据标签限定节点范围；这里尚未申请GPU设备
        gpu: "true"
      tolerations: # 容忍解除污点限制，节点选择器限定目标节点
      - key: "gpu"
        operator: "Exists"
        effect: "NoSchedule"
      containers:
      - name: gpu-example
        image: nginx:1.15.12
```

这里解决的是位置和准入问题，示例中的 Nginx 容器并没有申请 GPU 设备。真正使用 GPU 时，需要部署相应驱动和设备插件，并在实际业务容器下申请 GPU 扩展资源。以暴露 `nvidia.com/gpu` 的环境为例：

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

GPU 扩展资源请求可以让调度器依据节点可分配的设备数量选择位置；若节点有污点，仍需匹配容忍。是否还要添加节点选择器，取决于是否需要进一步限定设备型号或节点池。[Kubernetes 官方文档：调度 GPU](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)

### 把入口组件放到专用节点

Ingress Controller、Gateway、存储组件等工作负载，有时需要使用专用节点。可以用标签选择节点，用污点阻止其他未容忍的 Pod 进入。

例如，将 `k8s-node02` 标记为入口节点：

```sh
kubectl label node k8s-node02 ingress=true
# 添加一个污点，不让其他服务部署
kubectl taint node k8s-node02 ingress=true:NoSchedule
```

假设 Ingress Controller 以 DaemonSet 部署，资源名为 `ingress-nginx-controller`，可以编辑它的 Pod 模板：

```bash
kubectl edit daemonset ingress-nginx-controller -n ingress-nginx
```

在 `spec.template.spec` 下配置：

```yaml
nodeSelector:
  ingress: "true"
  kubernetes.io/os: linux
tolerations:
- key: ingress
  operator: Exists
  effect: NoSchedule
```

同样的组合也能用于租户专用节点。但污点和标签只控制调度位置；若租户能够自行添加容忍或修改节点选择条件，还需要相应的权限和准入策略约束，才能维持预期的节点使用范围。

### 计划维护：停止接收，再有序迁出

节点需要升级或下线时，要先确认应用是否有足够副本、其他节点是否有容量，以及存储是否允许迁移。单副本服务不能仅靠驱逐就保证维护期间持续可用。

使用自定义污点时，可以先阻止新的未容忍 Pod 进入维护节点：

```sh
kubectl taint node k8s-node02 maintain:NoSchedule
```

然后对受控制器管理的应用触发滚动更新。例如：

```sh
kubectl rollout restart deploy redis -n basic-component-dev
```

新的 Pod 会按照现有调度规则选择位置。需要等待替代副本就绪，再处理下一批工作负载；滚动更新本身并不保证所有服务都没有中断。

原有工作负载处理完成后，如果已经确认剩余 Pod 可以被驱逐，也可以使用 `NoExecute`：

```sh
kubectl taint node k8s-node02 maintain:NoExecute
```

直接添加 `NoExecute` 不能替代按 PodDisruptionBudget 控制的维护驱逐流程。维护完成后移除自定义污点：

```sh
kubectl taint node k8s-node02 maintain-
```

对于常规计划维护，更适合使用 Kubernetes 提供的 `cordon`、`drain`、`uncordon` 流程。[Kubernetes 官方文档：安全地腾空节点](https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/)

先禁止节点接收普通的新调度：

```sh
kubectl cordon k8s-node01
```

`cordon` 将 Node 的 `spec.unschedulable` 设为 `true`，节点列表中通常显示 `SchedulingDisabled`，已有 Pod 不会仅因此被驱逐。它与手工添加一个自定义污点是不同的操作。

然后迁出节点上的工作负载：

```sh
kubectl drain k8s-node01 --ignore-daemonsets --delete-emptydir-data
```

`drain` 通常通过 Eviction API 驱逐 Pod，并遵守适用的 PodDisruptionBudget。这里的 `--ignore-daemonsets` 会跳过 DaemonSet 管理的 Pod；`--delete-emptydir-data` 允许删除使用 `emptyDir` 的 Pod，其本地临时数据会丢失，应先确认数据可以舍弃。没有控制器管理的 Pod 也不会因为迁出操作自动补建到其他节点。

维护并确认节点恢复后，重新允许调度：

```sh
kubectl uncordon k8s-node01
```

### 节点故障：调整容忍与驱逐时机

节点故障时，控制面需要先识别节点异常。Ready 为 `False` 或 `Unknown` 时，可能分别关联 `node.kubernetes.io/not-ready` 或 `node.kubernetes.io/unreachable` 污点，相关 `NoExecute` 污点用于触发基于污点的驱逐。

对于没有显式覆盖这些容忍的普通 Pod，Kubernetes 默认会添加 300 秒的相应容忍。因此，常见的“五分钟”描述的是异常被识别并添加相关污点后的容忍等待，不能直接当作从机器故障到服务恢复的固定时间。DaemonSet Pod 对这两类污点通常有不设到期时长的容忍，行为也不同。

希望缩短等待时，可以在工作负载的 Pod 模板中显式设置两条容忍：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tolerations-second
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tolerations-second
  template:
    metadata:
      labels:
        app: tolerations-second
    spec:
      tolerations:
      - key: node.kubernetes.io/unreachable
        operator: Exists
        effect: NoExecute
        tolerationSeconds: 10
      - key: node.kubernetes.io/not-ready
        operator: Exists
        effect: NoExecute
        tolerationSeconds: 10
      containers:
      - name: nginx
        image: nginx:1.15.12
```

这里的 10 秒只调整匹配污点的容忍时长。故障检测、驱逐处理、控制器补建、重新调度、镜像拉取和应用就绪，都还需要时间。有状态应用还要考虑旧实例隔离及存储卷的卸载、重新挂载，不能照搬“10 秒恢复”的预期。

短容忍有助于更早开始恢复，也可能在短暂网络抖动时触发不必要的重建。应结合应用的状态、启动耗时和可用性要求选择时长。[Kubernetes 官方文档：基于污点的驱逐](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/#taint-based-evictions)

## 九、配置之后，怎样确认规则生效

复现前，先让示例中的节点名称、标签和命名空间与实际环境对应，并选用环境中可拉取的镜像版本。上面的完整资源清单用于分别演示不同场景；同名资源和同名标签不应不加区分地混在一起运行。

验证调度结果时，可以按以下顺序检查：

1. 查看候选节点的标签和污点，确认规则引用的 key、value 确实存在。
2. 查看 Pod 实际绑定的节点；涉及 Pod 亲和性时，也查看被选择 Pod 的标签、命名空间和位置。
3. 如果 Pod 没有成功调度，读取 Events 中的 `FailedScheduling` 原因，检查硬约束、资源和未容忍污点。
4. 修改 Deployment 等控制器的 Pod 模板后，观察新副本的分布与就绪状态。

常用的只读命令如下，执行时替换相应资源名和命名空间：

```bash
kubectl get nodes --show-labels
kubectl describe node node-01
kubectl get pods -n default -o wide --show-labels
kubectl describe pod pod-node-affinity-demo -n default
kubectl rollout status deployment/diff-nodes -n default
```

如果 Pod 已经绑定节点，却仍未运行，应继续检查容器状态和事件。镜像拉取失败、存储挂载失败等问题，也可能让 Pod 停留在 `Pending`；只有确认尚未完成节点绑定，才应继续沿调度规则排查。
