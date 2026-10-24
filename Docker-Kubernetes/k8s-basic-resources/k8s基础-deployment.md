---
title: K8s基础-Deployment
tags:
  - kubernetes
  - k8s-basics
aliases:
  - k8sDeployment
---

# Deployment：从副本管理到滚动更新、蓝绿与金丝雀发布

服务需要同时运行三个实例时，手工创建三个 Pod 只解决了第一次启动。之后还会遇到 Pod 故障、扩容和镜像升级：谁补齐副本，怎样逐步替换，失败后又如何退回原版本？Deployment 通过管理 ReplicaSet，把这些动作组织成可观察的发布过程。

本文先说明 ReplicaSet 与 Deployment 的关系，再用完整 YAML 练习扩缩容、更新和回滚，最后把 Service 流量切换接入蓝绿与金丝雀实验。实验需要可用集群、kubectl 和镜像拉取条件；NodePort 示例还需要节点端口可达。文中第三方教学镜像保留原实验用途，实际使用前应检查来源与可用性。

## ReplicaSet 先解决副本数量问题

ReplicaSet 根据选择器匹配 Pod，并在副本不足时创建 Pod、副本过多时缩减 Pod。它的 Pod 模板决定新 Pod 使用什么配置；已有 Pod 不会因为修改 ReplicaSet 的镜像字段就按发布策略全部替换。

### 一个三副本示例

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: rs-ft
  namespace: default
  labels:
    app: guestbook
    tier: frontend
spec:
  replicas: 3
  selector: # 在.spec.selector中定义的标签选择器必须能够匹配到spec.template.metadata.labels里定义的Pod标签
    matchLabels:
      tier1: frontend1
  template:
    metadata:
      labels:
        tier1: frontend1
    spec:
      containers:
      - name: samples-gb-frontend
        image: docker.io/yecc/gcr.io-google_samples-gb-frontend:v3
        imagePullPolicy: IfNotPresent
        ports: 
        - containerPort: 80
```

### 为什么通常在它上面再使用 Deployment

ReplicaSet 适合维持数量，Deployment 则负责新旧 ReplicaSet 之间的更新和历史管理。日常发布通常直接操作 Deployment，不手工修改它拥有的 ReplicaSet。删除 Pod 后能自动补齐副本，只能证明副本控制生效，还不能证明有版本发布与回滚能力。

## Deployment 如何管理新旧 ReplicaSet

Deployment 声明副本数、选择器和 Pod 模板。控制器为对应模板创建或复用 ReplicaSet，再调整各 ReplicaSet 的副本数量，使实际状态逐步接近期望状态。内置策略是 `RollingUpdate` 与 `Recreate`；蓝绿和按流量比例灰度还需要额外的对象与路由配置。基本行为见[Deployment 官方说明](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)。

### 更新期间可以有多个活跃 ReplicaSet

`.spec.template` 发生变化会触发 rollout，通常对应新的 ReplicaSet；如果模板回到已有历史版本，也可能复用已有 ReplicaSet。只改 `.spec.replicas` 不会生成新的模板版本。

滚动过程中，新旧 ReplicaSet 可以同时拥有运行中的 Pod。例如旧 ReplicaSet 原来有三个副本，控制器逐步增加新版本、缩减旧版本，直到旧 ReplicaSet 降为 0。旧 ReplicaSet 保留模板后，才有机会按历史版本回滚。不能把这个过程理解为“任何时候只有一个 ReplicaSet 活跃”。

![image-20231029220956699](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310292209817.png)

### 用更新预算控制替换节奏

`RollingUpdate` 用 `maxSurge` 与 `maxUnavailable` 控制额外副本和允许的不可用数量。两者都可写整数或百分比，默认均为 25%，不能同时为 0。

| 参数 | 百分比计算 | 5 个期望副本、配置 25% 时 |
| --- | --- | --- |
| `maxSurge` | 向上取整 | 可额外创建 2 个副本，常规更新预算为 7 个 |
| `maxUnavailable` | 向下取整 | 允许 1 个不可用，目标是至少 4 个可用副本 |

例如希望更新时仍保持五个可用副本，可以选择 `maxUnavailable: 0`、`maxSurge: 1`，先补一个可用的新 Pod，再缩减旧 Pod。如果允许一个不可用且允许一个额外副本，则控制器可以在四到六个的更新预算内推进，实际动作不保证严格“一次加一个、一次删两个”。

这些预算也不等于操作系统中绝不会超过该数量。正在 Terminating 的 Pod 仍可能占用资源，因此节点容量还要容纳优雅终止期间的额外消耗。应用的 readiness probe 决定能否接流量；liveness probe 用于恢复不健康容器，不能替代 readiness。需要启动缓冲时还可配合 startup probe 与 `minReadySeconds`。

可以直接查询目标集群支持的字段：

```sh
kubectl explain deployment.spec.strategy.rollingUpdate
```

### 先创建一份完整 Deployment

选择器必须匹配 Pod 模板标签，且 Deployment 创建后不能随意修改选择器。下面的 `version: v1` 是这个实验中的分组标签，实际应用不要每次修改镜像时都去修改不可变的 selector。后续示例继续使用 `dep-myapp-blue` 名称：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-myapp-blue
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
      version: v1
  template:
    metadata:
      labels:
        app: myapp
        version: v1
    spec:
      containers:
      - name: myapp
        image: janakiramm/myapp:v1
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
```

## 日常操作：重启与扩缩容

`rollout restart` 会给 Pod 模板增加重启时间注解，从而触发一次新的 rollout；它不保证重新拉取同一标签下的镜像，也不代表应用配置已正确更新：

```sh
kubectl rollout restart deployment/dep-myapp-blue
```

扩缩容可以修改 YAML 中的 `replicas` 后 apply，也可以临时使用命令：

```sh
kubectl scale deployment/dep-myapp-blue --replicas=5
```

声明式配置、手工 scale 与 HPA 如果同时管理副本数，需要约定字段归属，避免下一次发布又覆盖副本数。扩容前还应确认瓶颈：如果延迟来自数据库慢查询或连接压力，增加应用实例可能继续放大数据库负载。

## 滚动更新与历史版本

滚动更新逐步替换副本，能降低一次性切换全部实例的影响。原生 Deployment 根据副本预算推进，不直接提供“第一批一台、第二批 10%、再观察半小时”这样的完整分批审批流程。固定批次、自动指标判断和审批等待，通常由发布流水线或专门的渐进式交付控制器补充。

### 选择 Recreate 还是 RollingUpdate

| 策略 | 更新时的行为 | 适用前提 |
| --- | --- | --- |
| `Recreate` | rollout 时先终止旧版本，再创建新版本 | 可接受中断，或新旧版本不能同时运行 |
| `RollingUpdate` | 在预算内逐步增减新旧版本 | 应用允许版本共存，有正确的就绪检查和额外容量 |

```sh
kubectl explain deployment.spec.strategy
kubectl describe deployment dep-myapp-blue
```

Recreate 的保证针对控制器组织的版本升级，不能把它当成跨进程、跨故障场景下的全局单实例锁。回滚也只恢复 Pod 模板，不会自动回滚数据库 schema、外部配置或已写入数据。

### 查看发布状态与历史

`kubectl rollout` 提供发布相关命令：

| 子命令 | 用途 |
| --- | --- |
| `status` | 等待并显示当前发布进度 |
| `history` | 查看保留的版本 |
| `pause` / `resume` | 暂停或继续 Deployment 发布 |
| `restart` | 修改模板中的重启注解并触发发布 |
| `undo` | 回到上一版本，或用 `--to-revision` 指定版本 |

```sh
kubectl rollout status deployment/dep-myapp-blue
kubectl rollout history deployment/dep-myapp-blue
kubectl get rs
```

历史输出可能类似：

```text
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

`CHANGE-CAUSE` 来自 `kubernetes.io/change-cause` 注解。旧资料里的 `--record` 方式已经过时，可以显式记录发布原因：

```sh
kubectl annotate deployment dep-myapp-blue kubernetes.io/change-cause="upgrade myapp to v2" --overwrite
```

### 回滚到历史版本

```bash
kubectl rollout undo deploy dep-myapp-blue --to-revision=1 
# 回滚仍按当前部署策略推进，实际替换节奏取决于预算与就绪状态。
```

### 历史保留多少个版本

`.spec.revisionHistoryLimit` 默认保留 10 个旧 ReplicaSet。设为 0 后，旧的零副本 ReplicaSet 会在发布完成后的清理流程中删除，无法再依靠这些对象回滚。发布持续失败或多次更新尚未完成时，实际保留数量可能暂时超过这个值。

### 怎样选择更新预算

百分比适合副本数变化较大的服务，整数则更便于小副本服务控制步长。`maxUnavailable` 越小，主动减少可用副本越谨慎；`maxSurge` 越大，需要的额外容量越多，也可能加快推进。它们不会单独保证业务稳定，仍需配合探针、下游容量与观察指标。

例如十个副本配置 5% 时，`maxUnavailable` 向下取整为 0，`maxSurge` 向上取整为 1。对于需要保留全部可用副本的网关，可以从 `maxUnavailable: 0`、`maxSurge: 1` 开始；副本较多且容量充足时再考虑把 surge 提高到 2 或 3。五副本、十副本没有通用分界，默认的 25% 也需要按业务容错能力评估。

### 修改策略

修改deployment的更新策略:

```bash
#通过kubectl patch改
kubectl patch deployment dep-myapp-blue -p '{"spec":{"strategy":{"rollingUpdate": {"maxSurge":1,"maxUnavailable":0}}}}'
```

下面把策略写入完整清单，更新时使用四个期望副本：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-myapp-blue
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: myapp
      version: v1
  template:
    metadata:
      labels:
        app: myapp
        version: v1
    spec:
      containers:
      - name: myapp
        image: janakiramm/myapp:v2
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
```

### 暂停后合并多项模板修改

连续运行多个 `kubectl set` 命令，可能分别触发 rollout。如果希望先改镜像再改资源限制，可以暂停 Deployment，完成修改后统一恢复。一次编辑同一份 YAML 再 apply，通常无需为每个字段单独暂停。

~~~sh
kubectl rollout pause deployment/dep-myapp-blue
# 在暂停期间提交计划中的镜像、资源等模板修改
kubectl rollout resume deployment/dep-myapp-blue
~~~

暂停不撤销已经创建的新 Pod，也不是流量暂停。处于暂停状态的 Deployment 需要先恢复后才能执行回滚。恢复后应继续检查 `rollout status` 与应用指标；发布超时会报告失败进展条件，不会默认替我们完成业务回滚。

## 蓝绿部署：用 Service 选择流量目标

### 两套版本如何切换

蓝绿部署同时保留旧版和新版两套运行环境。这里把当前服务用户的旧版称为绿色，把准备上线的新版称为蓝色；颜色本身没有版本高低之分。蓝色环境先接受验证，确认后把入口切过去，旧版保留一段观察时间以便回退。

![image-20231111095318581](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311110953730.png)

测试环境与线上环境仍可能共享数据库、队列或存储。即使入口没有切换，新版本也可能产生写入或消费，因此测试账号、消息消费和数据兼容都需要设计。新版通过验证后，再修改入口路由：

![image-20231111095615746](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311110956844.png)

切换后需要观察错误率、延迟和业务结果，出现问题时把入口切回旧版。确认新版本稳定后，才按计划释放旧环境资源。切回入口只能恢复流量去向，不能自动撤销新版本已执行的数据写入。

| 方面 | 优点或代价 |
| --- | --- |
| 切换与回退 | 可以通过入口路由快速更换后端，保留旧版便于恢复 |
| 资源容量 | 观察期间需同时容纳两套环境，成本更高 |
| 数据兼容 | 共享数据库与外部依赖时，版本共存和回退都需兼容 |
| 流量状态 | Service、代理、DNS 缓存及已有长连接都会影响实际切换过程 |
| 环境管理 | 需要独立标签、配置和发布操作范围，避免误改另一套环境 |

Deployment 没有名为“蓝绿”的内置策略，但可以用两个 Deployment 加一个 Service 实现基本切换；更复杂的流量与分析流程可以交给专门控制器。

### 实验：先部署绿色 v1

先准备命名空间。离线镜像导入命令在节点主机执行，且只影响当前节点；Pod 可能调度到的其他节点也要有镜像，或能从仓库拉取。

```sh
kubectl create namespace blue-green
ctr -n=k8s.io images import myapp-blue.tar.gz
ctr -n=k8s.io images import myapp-green.tar.gz
```

把下面第一份清单保存为 `dep-green.yaml`：

```yaml
#部署deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-v1
  namespace: blue-green
spec:
  replicas: 3
  selector:
   matchLabels:
    app: myapp
    version: v1
  template:
   metadata:
    labels:
     app: myapp
     version: v1
   spec:
    containers:
    - name: myapp
      image: janakiramm/myapp:v1
      imagePullPolicy: IfNotPresent
      ports:
      - containerPort: 80
```

将 Service 清单保存为 `svc-myapp.yaml`，它初始只选择绿色 v1：

```yaml
#创建前端service
apiVersion: v1
kind: Service
metadata:
  name: myapp-lan-lv
  namespace: blue-green
  labels:
    app: myapp
spec:
  type: NodePort
  ports:
  - port: 80
    nodePort: 30062
    name: http
  selector:
    app: myapp
    version: v1
```

### 再部署蓝色 v2

把下面清单保存为 `dep-blue.yaml`，确认两套版本分别就绪后，再进行流量切换：

  ```yaml
  #创建deployment
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: myapp-v2
    namespace: blue-green
  spec:
    replicas: 3
    selector:
     matchLabels:
      app: myapp
      version: v2
    template:
     metadata:
      labels:
       app: myapp
       version: v2
     spec:
      containers:
      - name: myapp
        image: janakiramm/myapp:v2
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
  ```

Service 初始选择 `version: v1`，因此流量进入绿色版本。验证蓝色版本后，将 Service 的选择器切到 `v2`：

```sh
kubectl apply -f dep-green.yaml
kubectl apply -f dep-blue.yaml
kubectl apply -f svc-myapp.yaml
kubectl rollout status deployment/myapp-v1 -n blue-green
kubectl rollout status deployment/myapp-v2 -n blue-green
# 确认验证完成后再切流量；也可修改Service清单后apply
kubectl patch service myapp-lan-lv -n blue-green --type=merge -p '{"spec":{"selector":{"app":"myapp","version":"v2"}}}'
```

Service 清单也需要在使用前提交；NodePort `30062` 应未被其他 Service 占用。切换主要影响后续连接，已有连接、应用会话和下游数据不会因此瞬间迁移。回退时将选择器改回 `v1`，并保留两套版本的数据兼容性。

## 金丝雀发布：先让一部分请求接触新版

金丝雀发布先把少量实例或流量交给新版本，观察错误率、延迟和业务指标，再决定继续放量或回退。名称源自矿井中用金丝雀预警有害气体的做法；在发布中，承担预警作用的是可观测的运行结果。

![image-20231111103236653](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311111032729.png)

### 暂停 rollout 可以观察，但不能精确锁定一份新副本

原实验尝试在更新镜像后立即暂停 Deployment：

```sh
kubectl apply -f dep-green.yaml
kubectl set image deployment myapp-v1 myapp=nginx:latest -n blue-green
kubectl rollout pause deployment myapp-v1 -n blue-green
# 观察完成且决定继续后恢复
kubectl rollout resume deployment myapp-v1 -n blue-green
```

这组命令用于观察控制器如何响应更新与暂停，不适合保证“恰好一个新 Pod”。两次 API 操作之间存在竞争，控制器可能还未创建新副本，也可能已经推进多个副本；暂停也不会撤回已发出的操作。`nginx:latest` 在这里只是改变模板的实验值，不代表业务兼容的升级目标，生产应使用经过验证的固定版本或摘要。

### 让新旧 Deployment 独立伸缩

更容易控制的基本方式，是复用前面的两个 Deployment：旧版保持多个副本，新版先保留一个副本，让 Service 只选择共同的 `app: myapp`，同时包含两个版本。选择器去掉版本字段的 merge patch 示例为：

```sh
# 若做过上面的暂停实验，先重新提交绿色清单以恢复原应用镜像
kubectl apply -f dep-green.yaml
kubectl rollout status deployment/myapp-v1 -n blue-green
kubectl scale deployment/myapp-v2 -n blue-green --replicas=1
kubectl patch service myapp-lan-lv -n blue-green --type=merge -p '{"spec":{"selector":{"app":"myapp","version":null}}}'
```

这只是按可用后端数量近似分摊连接，不能保证每个请求严格按某个百分比分配。长连接、会话亲和与负载差异都会改变观察到的比例。若需要 2% 流量、指定用户或请求头规则，可使用具备加权路由能力的网关或 Istio 等方案，并配合发布控制器组织放量与回退。Kubernetes 官方的[金丝雀模式说明](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#canary-deployments)也建议用多个 Deployment 承载不同版本。

## 迁移应用前先整理运行条件

把已有服务迁入 Kubernetes 前，先确认镜像来源、固定版本与架构，记录实际监听端口；再列出环境变量、配置文件和启动参数，例如 MySQL 初始化时需要的密码配置。最后检查数据目录：哪些只是缓存，哪些必须持久化，是否需要 PVC、备份和恢复验证。

这些信息决定 Pod 模板如何编写，也决定滚动、蓝绿或金丝雀是否可行。若应用无法与旧版本同时读写同一份数据，应先解决数据兼容和迁移流程，再选择发布策略。
