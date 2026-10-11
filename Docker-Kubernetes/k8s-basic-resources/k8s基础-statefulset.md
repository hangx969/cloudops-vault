---
title: K8s基础-StatefulSet
tags:
  - kubernetes
  - k8s-basics
aliases:
  - k8sStatefulSet
---

# K8s基础-StatefulSet


## 应用的状态

- 无状态和有状态应用区别

  - 无状态
    - POD都是一样的
    - 没有顺序要求
    - 不用考虑在哪个node上运行
    - 随意进行伸缩和扩展

  - 有状态
    - 上面的因素都要考虑
    - **每个pod都是独立的，保持启动顺序和唯一性**
    - 每个pod有唯一的网络标识符（有dns名称），pod名称不能随意变化
    - 持久存储的目录也不一样
    - 有序，比如mysql的主从，redis等

## sts介绍

sts是k8s的有状态资源调度器。部署有状态且需要有序启动的服务，比如mysql、zookeeper、eureka、nacos、MongoDB、ES、redis、kafka等。

> [!tip] 提示
> 生产环境部署这些集群，推荐用operator/helm去部署，因为一些复杂集群操作（扩缩容、rebalance等）官方在里面都封装好了，自己手写yaml文件，很难实现。

sts基于headless svc给每一个pod分配一个唯一且固定的网络标识符，各pod之间通过这个标识符来通信。

## statefulSet yaml编写

```yaml
# headless service，用来定义pod网络标识，生成可解析的DNS记录
apiVersion: v1
kind: Service
metadata:
  name: svc-sts-nginx
  labels:
    app: nginx
spec:
  selector:
    app: nginx
  clusterIP: None # 这里才真正标识了svc是headless svc
  ports:
  - name: web
    port: 80
---
apiVersion: apps/v1
kind: StatefulSet
metadata: 
  name: sts-web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  serviceName: svc-sts-nginx # sts由前端headless service管理。这个字段是sts独有的。
  volumeClaimTemplates: # sts的存储配置，自动生成pv和pvc。注意是在sts.spec字段下的
  - metadata:
      name: www
    spec:
      storageClassName: sc-nfs
      accessModes:
      - ReadWriteOnce
      resources:
        requests:
          storage: 1Gi
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        imagePullPolicy: IfNotPresent
        ports:
        - name: web
          containerPort: 80
        volumeMounts:
        - name: www #写volumeClaimTemplates的name
          mountPath: /usr/share/nginx/html
```

## POD主机名

- 每个pod有唯一**主机名**：**pod-name.service名称.名称空间.svc.cluster.local**
  
  例如：sts-web-0.svc-sts-nginx.default.svc.cluster.local

```bash
#查看sts pod主机名
for i in 0 1; do kubectl exec web-$i -- sh -c 'hostname';done
```

## headless service

- 不分配clusterIP怎么访问pod？

  - headless service可以通过解析service的FQDN（`<svc>.<ns>.svc.cluster.local`）, 返回所有Pod的FQDN和ip地址 (statefulSet部署的Pod才有FQDN：`<pod>.<ns>.svc.cluster.local`)

  - 普通的service, 只能通过解析service的DNS返回service的ClusterIP，再通过endpoint找到pod ip。


  ```bash
  #集群内解析headless service的FQDN ==> 直接解析出pod的IP
  nslookup svc-sts-nginx.default.svc.cluster.local
  
  Server:         10.0.0.10
  Address:        10.0.0.10:53
  
  Name:   svc-sts-nginx.default.svc.cluster.local
  Address: 10.244.1.9
  Name:   svc-sts-nginx.default.svc.cluster.local
  Address: 10.244.1.8
  ```

- headless svc和普通svc的区别是headless svc解析svc FQDN会直接返回pod IP；而普通ClusterIP svc，解析svc FQDN会返回的是svc自己的clusterIP
- 注意：
1. sts必须要求先创建svc，但是不一定必须是headless svc，也可以是ClusterIP的svc
     - 如果是headless的svc，对这个service FQDN做dns解析，会找到它所关联的pod ip
     - 如果创建的service有ip，那对这个service做dns解析，会解析到service本身ip，通过ipvs规则再找到pod
  

2. headless svc一般只用作集群内部通信。要给集群外部通信，可以再创建新的svc，NodePort类型来暴露sts的pod。


> Dig工具使用：
>
> - @来指定域名服务器
> - -t 指定要解析的类型
>
> - A 为解析类型 ，A记录：解析域名到IP
>
> ```bash
> dig -t A svc-sts-nginx.default.svc.cluster.local @10.0.0.10
> ```

## 存储模板

- 对于有状态应用都会用到持久化存储，比如mysql主从，由于主从数据库的数据是不能存放在一个目录下的，每个mysql节点都需要有自己**独立的存储空间**。

- 而在deployment中创建的存储卷是一个共享的存储卷，多个pod使用同一个存储卷，它们数据是同步的；而statefulset定义中的每一个pod都不能使用同一个存储卷，这就需要使用`volumeClainTemplate`。

- 当在使用statefulset创建pod时，`volumeClainTemplate`会自动生成一个PVC，从而请求绑定一个PV，每一个pod都有自己专用的存储卷。Pod、PVC和PV对应的关系图如下：

  ![image-20240324095254313](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202403240952473.png)

## 扩缩容

sts启动的时候默认是从小到大一个一个启动，上一个没起来，下一个不会启动。（也可以改成并发启动的策略）

注意删除的时候也是一起全删除的

- 可以直接修改yaml文件扩缩容
  - 扩容：pod name从小到大扩。
  - 缩容：pod name从大到小删。

## 滚动更新

两种模式：OnDelete（必须手动删掉旧的才能创建新的）、RollingUpdate。现在默认是RollingUpdate

默认是序号从大到小一个一个更新。而且更新时由于pod持久存储不能重复冲突挂载，所以必须完全释放了这个pod，才会创建新的出来。

- 定义字段

  ```bash
  kubectl explain sts.spec.updateStrategy
  ```

- yaml文件

  ```yaml
  apiVersion: apps/v1
  kind: StatefulSet
  metadata: 
    name: sts-web
  spec:
    replicas: 2
    selector:
      matchLabels:
        app: nginx
    serviceName: svc-sts-nginx #sts由前端headless service管理
    updateStrategy: 
      type: RollingUpdate #type还有OnDelete，OnDelete不会让pod自动更新，只有手动删除pod，才会自动创建新的pod
      rollingUpdate:
        maxUnavailable: 0 # 与deployment的更新策略类似，这里写0，就代表replicas规定的数量一个也不能少。
        partition: 2 # 更新的时候只更新pod序号 >= 2。即分段更新。可以实现灰度发布。确认完再设成0
    template:
      metadata:
        labels:
          app: nginx
      spec:
        containers:
        - name: nginx
          image: nginx
          imagePullPolicy: IfNotPresent
          ports:
          - name: web
            containerPort: 80
          volumeMounts:
          - name: www # 写volumeClaimTemplates的name
            mountPath: /usr/share/nginx/html
  ```


## 回滚

~~~sh
# 查看更新状态
kubectl rollout status sts/<daemonset-name>
# 列出所有修订版本
kubectl rollout history sts <daemonset-name>
# 回滚到指定 revision
kubectl rollout undo sts <statefulset-name> --to-revision=<revision>
#StatefulSet 的更新和回滚与 Deployment 类似，唯一的区别是历史版本在 ControllerRevision 中保存。
~~~

生产不推荐回滚，哪里配置错了直接改就行。回滚可能会造成有状态服务的异常。

## 并发pod管理

StatefulSet 可以通过`.spec.podManagementPolicy` 字段配置 Pod 的管理策略。比如有些sts服务我们只是需要有唯一标识符，并不需要按序创建，那就可以调整这个字段为Parallel。

这个字段目前支持如下的两种方式：

1. OrderdReady：有序管理，默认方式。Pod创建和更新按照正序和倒序进行操作。删除是同时删除。
2. Parallel：并发管理，Pod 创建和删除同时并行启动和删除。（更新还是倒序更新）。

## 案例-部署web站点

~~~yaml
#sts
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: sts-web
  namespace: default
  labels:
    app: web
spec:
  replicas: 2
  selector:
    matchLabels:
       app: nginx
  serviceName: svc-sts-web
  template:
    metadata:
      namespace: default
      labels:
        app: nginx
    spec:
      containers:
        name: nginx
        image: nginx
        imagePullPolicy: IfNotPresent
        ports:
        - name: www
          containerPort: 80
          protool: TCP
        volumeMounts:
        - name: storage-web
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: storage-web
      namespace: default
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: sc-web
      resources:
        requests: 
          storage: 1Gi
          
#svc
---
apiVersion: v1
kind: Service
metadata:
  name: svc-sts-web
  namespace: default
spec:
  clusterIP: None
  selector:
    app: nginx
  ports:
  - name: www
    port: 80
    protocol: TCP

#sc
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-web
provisioner: example.com/nfs
~~~


## Recreate 更新策略（Kubernetes 1.37 Alpha）

本节根据 WAKEUP技术的 StatefulSet Recreate 策略文章整理。原文发表于 2026 年 8 月 24 日；下文保留其配置、命令和案例，并将官方资料核验说明与作者经验分开。

> [!warning] 版本与配置核验（2026-10-11）
> 原文称 Recreate 在 Kubernetes 1.37 中已 GA，但官方将它标为 **Alpha、默认关闭**。使用前需在 `kube-apiserver` 和 `kube-controller-manager` 启用 `StatefulSetRecreateStrategy`。版本号本身不能证明集群已启用该功能。见[官方特性门控列表](https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/#feature-gates)。
>
> 原文的 `Recreate + rollingUpdate.partition` 配置不符合当前 API：`rollingUpdate` 只允许用于 `RollingUpdate`，切换为 `Recreate` 时必须移除该字段。见 [StatefulSet API 校验代码](https://raw.githubusercontent.com/kubernetes/kubernetes/master/pkg/apis/apps/validation/validation.go)。

### 为什么需要整体重建

有状态应用升级时，除了 Pod 能否启动，还要检查集群成员关系、数据格式和客户端连接。逐个替换 Pod 会让不同序号的副本暂时运行不同版本；如果应用不支持这种混合运行，升级就可能出现兼容性问题。

作者记录过一个三节点 etcd 类共识集群的故障：序号 1 的新 Pod 已启动但尚未加入集群，序号 0 的旧 Pod 随后被删除，短暂只剩一个健康节点，发生重新选主和快照重建，P99 写入延迟升至秒级。这是原文的事故描述，未提供配置和探针信息，不能据此判断所有共识集群都应改用整体重建。

三种更新策略的区别如下。`Recreate` 为可选功能，默认更新策略仍是 `RollingUpdate`。参见 [StatefulSet API](https://kubernetes.io/docs/reference/kubernetes-api/apps/stateful-set-v1/#StatefulSetUpdateStrategy)。

| 策略 | 修改 Pod 模板后的行为 | 适用条件 |
| --- | --- | --- |
| `RollingUpdate` | 自动逐个删除并重建 Pod；默认从高序号向低序号更新 | 应用允许新旧版本在不同副本上短暂共存；可用 `partition` 分阶段更新 |
| `OnDelete` | 不主动更新已有 Pod；删除 Pod 后，控制器才按更新后的模板重建 | 更新节奏由人工或外部自动化控制 |
| `Recreate` | 删除全部 Pod，等它们完全终止后，再创建新版本 Pod | 应用不能同时运行两个版本，并能接受整体停机；需启用 Alpha 特性门控 |

`Recreate` 的删除阶段不受 `podManagementPolicy` 影响，全部 Pod 会一起进入删除流程。创建阶段则遵循该字段：`OrderedReady` 从序号 0 开始，逐个等待 Running 和 Ready；`Parallel` 并行创建全部 Pod。它不能保证所有 Pod 在同一瞬间退出，也不保证应用数据格式自动兼容。见[官方 Recreate 说明](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/#recreate)。

这里的重建会替换 Pod 实例，保留的是 StatefulSet 的稳定身份与存储映射。是否接受停机，应由应用的升级要求和业务恢复目标决定。原文认为“一致性优于可用性”，并主张共识或主从服务默认采用 Recreate；这是作者的取舍，不能直接作为所有有状态应用的默认配置。

### 配置示例与启用条件

原文给出以下示例。代码保留供对照；其中 `Recreate` 与 `rollingUpdate.partition` 的组合会被当前 StatefulSet API 校验拒绝。它还省略了 Service、selector、Pod 标签、存储和 Redis 集群配置，不能作为完整部署清单使用。

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
spec:
  replicas: 3
  podManagementPolicy: OrderedReady
  updateStrategy:
    type: Recreate
    rollingUpdate:
      partition: 0   # 灰度时先设为 2，只重建序号 2 的 Pod 试水
  template:
    spec:
      containers:
      - name: redis
        image: redis:7.4
```

> [!info] 按官方资料补充的配置
> 下列片段用于说明当前 API 的字段组合，不是完整 StatefulSet 清单；原文示例保持原样。启用特性门控后，`Recreate` 不配置 `rollingUpdate`。

```yaml
spec:
  podManagementPolicy: OrderedReady
  updateStrategy:
    type: Recreate
  persistentVolumeClaimRetentionPolicy:
    whenDeleted: Retain
    whenScaled: Retain
```

两个控制面组件都需要启用以下参数；配置方式按集群安装方式处理：

```text
--feature-gates=StatefulSetRecreateStrategy=true
```

从已有 `RollingUpdate` 配置切换时，需要同时清除 `rollingUpdate`。以下是根据 API 约束补充的策略切换命令，前提是集群已经支持并启用该特性，且 StatefulSet 没有被 Operator 回写策略：

```bash
kubectl patch sts redis-cluster --type=merge -p '{"spec":{"updateStrategy":{"type":"Recreate","rollingUpdate":null}}}'
```

随后通过现有清单修改 `spec.template` 中的镜像或配置，观察旧 Pod 是否全部终止后才创建新 Pod。仅切换策略或调整分区，不等于提交了新的 Pod 模板。首次使用应在非核心环境演练；API 接受配置之后，还要核对控制器实际执行的删除、创建顺序。启用条件参见 [KEP-3541](https://www.kubernetes.dev/resources/keps/3541/#upgrade--downgrade-strategy)。

### Pod、PVC 与 PV 的生命周期

通过 `volumeClaimTemplates` 创建的 PVC，名称为 `<模板名>-<sts名>-<序号>`，例如 `data-redis-cluster-0`。同一序号的 Pod 重建后，使用原有 PVC 是 StatefulSet 的预期行为；删除 Pod 并不等于删除 PVC，也不等于清空历史数据。

需要分清两层策略：

| 配置 | 控制的对象和时机 | `Retain` 的含义 |
| --- | --- | --- |
| StatefulSet 的 `persistentVolumeClaimRetentionPolicy.whenDeleted / whenScaled` | 删除 StatefulSet 或缩容时，是否删除模板生成的 PVC | 保留 PVC；两项默认均为 `Retain` |
| PV 的 `persistentVolumeReclaimPolicy`，动态创建时继承 StorageClass 的 `reclaimPolicy` | PVC 删除、PV 被释放后的底层存储处置 | 保留 PV 与底层数据，供后续人工处理 |

第一层用于 StatefulSet 删除和缩容，不把正常更新时的 Pod 替换变成 PVC 删除。第二层在 PVC 被删除后才涉及卷回收；StorageClass 为 `Delete` 不能单独解释“删 Pod 导致 PVC 被回收”。检查已有卷时，应检查实际 PV 的回收策略。参见[官方 PVC 保留策略](https://kubernetes.io/docs/reference/kubernetes-api/apps/stateful-set-v1/#StatefulSetPersistentVolumeClaimRetentionPolicy)和[官方 PV 回收说明](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#reclaiming)。

原文建议核心数据使用 `Retain` 并定期快照。可将它作为数据保护方案评估，但 `Retain` 不能阻止 PVC 对象被删除，也不能替代备份或恢复演练。删除 StatefulSet 前仍需核对 PVC 保留策略、ownerReferences 和级联删除方式。

原文还把 Deployment 的存储概括为临时卷，这个说法过于绝对：Deployment 也可以挂载 PVC。StatefulSet 的特点是为各序号维持稳定身份，并通过存储模板管理相应 PVC。

### 分区灰度：原文命令适用于 RollingUpdate

`partition` 以序号为阈值划分更新范围，不能按业务指标自动放行。以下保留原文操作步骤，但它们应在 `type: RollingUpdate` 下使用；Recreate 没有分区灰度入口。默认从 0 编号时，3 副本的 `partition: 2` 会把更新限制在序号 2，较低序号仍运行旧版本。

#### 第一步：先更新最高序号 Pod

在提交新 Pod 模板前设定分区。原文使用 `replicas-1`，即 3 副本设为 2，然后观察新 Pod 能否加入集群、数据是否符合预期：

```bash
kubectl patch sts redis-cluster -p '{"spec":{"updateStrategy":{"rollingUpdate":{"partition":2}}}}'
kubectl rollout status sts/redis-cluster --timeout=120s
```

这些命令设置分区并等待 rollout，不包含镜像或模板更新；需要配合实际的模板变更。rollout 成功也不等于应用数据一致性验证完成。

#### 第二步：检查后逐步放开

原文基础流程是在检查通过后把 `partition` 降为 0：

```bash
kubectl patch sts redis-cluster -p '{"spec":{"updateStrategy":{"rollingUpdate":{"partition":0}}}}'
kubectl rollout status sts/redis-cluster --timeout=300s
```

作者还描述了一种三阶段流程：先更新最高序号，执行自动化校验，包括按应用的数据布局比对数据哈希、检查集群成员；人工确认后降到中间序号；最后降为 0。各阶段之间至少观察 10 分钟，监控 P99 延迟和错误率。原文称采用该流程后半年没有事故，这一效果尚未复现验证。对默认编号的 3 副本而言，分区可以依次为 2、1、0；这仍然允许不同副本暂时运行不同版本。

#### 第三步：检查 PVC 与应用状态

原文的检查命令如下，同样可用于重建后的检查：

```bash
# 检查 PVC 是否还在（Recreate 不应删卷）
kubectl get pvc -l app=redis-cluster
# 检查集群成员与数据
kubectl exec redis-cluster-0 -- redis-cli cluster info
```

`kubectl get pvc -l app=redis-cluster` 只会列出带该标签的 PVC，需确认存储模板实际设置了标签。`redis-cli cluster info` 可以检查集群状态，不能单独证明全部数据完整；还应按应用需要核对成员、持久化恢复和数据校验结果。

如果应用要求整个 StatefulSet 内的新旧版本完全不共存，应评估 Recreate 的停机窗口、Operator 提供的维护流程，或独立 StatefulSet 的切换方案。不能同时把同一更新过程描述为“分区逐个更新”和“全程没有新旧版本并存”。

### 原文的 11 个故障案例

以下保留作者报告的故障和处理方式。案例未提供完整环境、事件和日志；涉及 Recreate、存储删除或流量行为的结论，需要结合前面的核验说明阅读。

1. **未灰度就整体停机。** 作者称首次直接设置 `type: Recreate`，3 个 Pod 同时被删除，服务中断，恢复用了 5 分钟；之后要求先用 `partition` 灰度。核验说明：Recreate 本来就是全量重建，`partition` 不能限制它的更新范围。先灰度需要选择 RollingUpdate 或另行设计验证环境，整体重建则要预留停机窗口。

2. **PVC 丢失。** 作者将一次重建后的 PVC 清理和历史数据丢失归因于 StorageClass 设置了 `Delete`，处理方式是改为 `Retain` 并定期快照。核验说明：这个原因链缺少 PVC 如何被删除的证据；需检查 PVC 保留策略、ownerReferences 和其他删除操作，不能只凭 StorageClass 的回收策略归因。

3. **并行启动破坏依赖顺序。** 作者称使用 `podManagementPolicy: Parallel` 后，从节点先于主节点启动，出现选主异常，改回 `OrderedReady` 后稳定。存在启动依赖时，应保留适合该应用的顺序；Parallel 不保证节点按序就绪。

4. **进程已启动，数据尚未就绪。** 容器进程启动后，数据仍在加载。原文称 readiness 探针缺失导致流量过早进入，补充探针后才解决。探针需要反映应用可接收请求的状态，而不仅是进程存活。

5. **初始化依赖失败。** 原文把这一项称为“有状态 sidecar 顺序依赖”，实际描述的是 init 容器拉取配置失败，并称主容器持续 CrashLoop；作者将配置加载改成异步重试后恢复。核验说明：普通 init 容器需成功完成后，应用容器才会启动。应根据容器状态和日志区分初始化失败与应用启动失败，不能由这段描述确认主容器的失败路径。见[官方 init 容器说明](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)。

6. **客户端仍使用旧地址。** 作者称 DNS 缓存使客户端短期内继续连接旧 Endpoint，处理方式是配合 readiness 控制服务端就绪状态，并在客户端增加连接重试。整体重建也不能替代客户端的断线恢复逻辑。

7. **Operator 覆盖手工配置。** 作者称数据库 Operator 固定使用 RollingUpdate，手工修改的策略被回写。最后采用该 Operator 自身的维护窗口和暂停副本流程。由 Operator 管理的 StatefulSet，应先确认其支持的升级方式。

8. **回滚再次停机。** 原文称新版本出现问题后，回滚又触发了一次整体重建；后续为关键服务建立独立 StatefulSet 的蓝绿切换方案，减少对重建回滚的依赖。这是作者的处理方案，仍需按应用核对数据同步、切换和恢复条件。

9. **误删 StatefulSet 后丢失 PVC。** 作者称执行 `kubectl delete sts` 时未加 `--cascade=false`，PVC 随之回收，并建议使用 `--cascade=orphan` 或确认卷回收策略。核验说明：删除 StatefulSet 并不必然删除 PVC，默认 PVC 保留策略为 Retain；是否回收需检查实际保留策略和 ownerReferences。`--cascade=orphan` 与 PV 的 Retain 控制不同对象，不能把其中一项当成完整的数据保护保证。

10. **把重建当成清空节点。** 作者称手动删除序号 2 的 Pod 后，新 Pod 复用了序号和旧 PVC，出现其所称的“数据串台”。核验说明：复用同序号的 PVC 是正常行为，删除 Pod 不会自动改变序号或重置数据。若目标是清空节点或重新分配数据，应走应用明确支持的流程。

11. **未就绪 Pod 收到请求。** 原文称新 Pod 已 Running、readiness 尚未通过，EndpointSlice 已更新并收到流量，建议加强 readiness、客户端连接重试和控制器同步检查。核验说明：EndpointSlice 中出现地址不等于它已是可接收流量的后端，需检查 `conditions.ready`、实际流量路径以及 Service 的 `publishNotReadyAddresses`；该字段为 true 时，端点的 ready 会被视为 true。见[官方 EndpointSlice 条件说明](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/#conditions)。

### 原文 Redis Cluster 迁移案例与适用边界

作者给出一个包含 `redis-cluster-0/1/2` 的三节点 Redis Cluster 案例。原文称默认更新按 0→1→2 进行，混合版本期间因槽位迁移出现 MOVED 重定向增多，客户端错误率短时翻倍。核验说明：默认 RollingUpdate 的顺序是从高序号到低序号，3 副本对应 2→1→0。

案例的流程如下：

1. 把策略改为 Recreate，并将 `partition` 设为 2。作者称只有 2 号 Pod 重建，随后用 `redis-cli cluster nodes` 检查拓扑、比对数据哈希，再观察 5 分钟客户端错误率；同时称离线节点的槽位由 0、1 号节点接管。

2. 将分区降为 1，重建 1 号并重复校验。作者称这一阶段短暂只有 0、2 号在线，且没有新旧版本并存带来的槽位冲突。

3. 将分区降为 0，最后重建 0 号。作者称迁移在低峰完成，全程没有新旧混跑，客户端报错峰值比过去低约 70%。

> [!warning] 案例不能作为当前 Recreate 的操作依据
> 上述分区过程不符合 Recreate 的 API 约束和全量重建语义；若实际使用的是 RollingUpdate 分区灰度，低序号旧版本与高序号新版本会暂时共存。原文未提供主从角色、replica 布局、槽位分配和测量依据，无法据此确认槽位接管过程或约 70% 的改善。Redis Cluster 的自动故障转移依赖可提升的 replica 及多数 master 的投票，不能仅凭“三节点”推定另外两个节点会自动接管槽位。见 [Redis Cluster 官方规范](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/#replica-election-and-promotion)。

作者列出的迁移前准备仍可作为检查线索：核对卷回收策略并准备最近快照；确认 readiness 反映数据已加载、应用可以工作；在预发环境用相同拓扑演练，记录各阶段耗时。案例中的 5 分钟观察和前面三阶段流程中的至少 10 分钟，是原文不同流程的观察时间，不能作为通用发布阈值。

原文的回滚方案是把镜像 tag 改回旧版，再走分区灰度，并指出整体重建可能再次中断服务；核心服务则考虑独立 StatefulSet 的蓝绿切换。需要分清：修改模板、分区灰度和整体重建是不同步骤，Recreate 不能依靠 `partition` 完成回滚。

### 上线前检查

整体重建避免的是同一 StatefulSet 内新旧 Pod 修订版本并存，不能修复应用的数据格式不兼容。按原文建议，应先在预发验证新版本能否读取旧版本写入的数据；必要时先迁移数据格式，再升级应用。

- [ ] 确认 Kubernetes 版本及两个控制面组件的 `StatefulSetRecreateStrategy` 配置，先在非核心环境验证实际更新行为。
- [ ] 根据应用的混合版本兼容性选择策略：需要分区灰度时使用 RollingUpdate；整体重建时安排业务低峰、停机窗口、前端降级或重试。
- [ ] 检查实际 PVC/PV、StorageClass、PVC 保留策略和卷回收策略，准备快照或备份；日常更新通过 Pod 模板变更完成，避免把删除整个 StatefulSet 当作普通升级。
- [ ] 验证启动依赖、init/sidecar 的配置加载、readiness 和客户端重试；强依赖顺序的应用应评估 OrderedReady。
- [ ] 确认 Operator 不会回写更新策略，核对其维护窗口或暂停副本流程。
- [ ] 校验集群成员、持久化恢复和应用数据；灰度流程监控 P99 与错误率，并保留人工放行步骤。
- [ ] 演练数据格式迁移和回滚，明确是否需要独立 StatefulSet 的切换方案。
- [ ] 对 Pod 删除/创建事件配置告警，持续监控 PVC 状态，确认存储仍在位。

本节完成的是文章整理和官方资料核验，未执行 Kubernetes/Redis 命令、部署或复现作者案例。
