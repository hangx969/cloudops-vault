---
title: K8s基础-DaemonSet
tags:
  - kubernetes
  - k8s-basics
aliases:
  - k8sDaemonSet
---

# DaemonSet：让指定节点各运行一份后台组件

日志采集器需要读取本机日志，节点监控程序需要读取本机指标。即使我们知道集群有十个节点，也不能简单创建十个 Deployment 副本：调度器可能把多个副本放在同一节点，新节点加入时也不会自动增加副本。

DaemonSet 按符合条件的节点维护 Pod，适合这类与节点绑定的后台工作。本文先部署一个日志采集示例，再说明节点选择、滚动更新和回滚。实验需要一个可用的 Kubernetes 集群、能够创建 DaemonSet 的权限，以及可拉取示例镜像的节点。涉及宿主机目录挂载时，还需要集群安全策略允许使用 `hostPath`。

## DaemonSet 控制器怎样维护节点副本

### 它如何确定副本数量

DaemonSet 确保每个符合条件的节点运行一份 Pod。这里的“符合条件”取决于节点选择器、节点亲和性、污点与容忍等配置。新节点满足条件时，控制器为其创建 Pod；节点标签变化后不再匹配时，相应 Pod 会被删除。删除 DaemonSet 时，默认也会级联清理其 Pod。

控制器通过 API server 观察 DaemonSet、Pod 和 Node 的变化，为目标节点创建带节点亲和性约束的 Pod，再由调度器完成绑定。节点资源不足、镜像拉取失败或容忍条件不满足时，Pod 仍可能无法正常运行。详细行为见[DaemonSet 官方说明](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)。

### 常见用途

| 节点上的工作 | 常见组件 | 为什么适合 DaemonSet |
| --- | --- | --- |
| 提供节点存储服务 | Ceph 等存储守护进程 | 需要使用目标节点的磁盘或存储接口 |
| 采集日志 | Fluentd、Filebeat、Logstash 等 | 需要读取本节点日志文件 |
| 采集节点指标 | Node Exporter、collectd 等 | 需要读取节点 CPU、内存和文件系统指标 |

Prometheus 服务端通常作为集中式采集与查询服务部署；按节点运行的常见组件是 Node Exporter。存储系统也可能由 Operator 再管理底层 DaemonSet，实际应遵循对应项目的部署方式。

## 示例：使用 DaemonSet 部署 Fluentd

下面保留日志采集器的完整 Pod 模板，镜像使用 Kubernetes 官方示例中的固定版本。它演示节点部署与目录挂载，真正接入日志平台时还需要匹配日志格式、Fluentd 配置与输出目的地。`/var/log` 常用于读取 CRI 日志；`/var/lib/docker/containers` 是历史 Docker 日志目录，纯 containerd 节点通常不依赖它。不要据此假定所有运行时都把日志写到相同路径。

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: ds-test
  namespace: default
  labels:
    app: fluentd-logging
spec:
  selector:
    matchLabels:
      name: fluentd-elasticsearch
  template:
    metadata:
      labels:
        name: fluentd-elasticsearch
    spec:
      tolerations:
      - key: node-role.kubernetes.io/control-plane # 容忍master的污点
        operator: Exists
        effect: NoSchedule
      containers:
      - name: fluentd-elasticsearch
        image: quay.io/fluentd_elasticsearch/fluentd:v5.0.1
        imagePullPolicy: IfNotPresent
        resources: 
          requests: 
            cpu: 100m
            memory: 200Mi
          limits: 
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
      volumes:
      - name: varlog # 挂载系统日志
        hostPath:
          path: /var/log
      - name: varlibdockercontainers # 挂载容器日志
        hostPath:
          path: /var/lib/docker/containers
```

> [!info] 说明
> 与 Deployment 相比，`kind` 为 `DaemonSet`，且没有 `.spec.replicas` 字段。副本数由符合条件的节点数决定；`replicaCount` 常见于 Helm Chart 的 values，并非 Deployment API 字段。选择器仍需匹配 Pod 模板标签，且创建后不能随意修改。

## 指定节点部署

如果采集器只应运行在某类节点上，可以在 `.spec.template.spec` 中加入 `nodeSelector`。下面是两个可替换使用的片段，不应在同一 YAML 层级重复定义两个 `nodeSelector`：

~~~yaml
# 如果指定了.spec.template.spec.nodeSelector，DaemonSet Controller 将在与 Node Selector 匹配的节点上创建 Pod
# 比如部署在磁盘类型为 ssd 的节点上（需要提前给节点定义标签 Label）：
nodeSelector:
  disktype: ssd
~~~

GPU 节点可以使用另一组标签选择条件：

~~~yaml
# 比如调度到GPU节点上
nodeSelector:
  gpu: "true" # 注意布尔值需要设成字符串
~~~

节点新增或标签变化后，控制器会重新计算目标集合：给新匹配的节点补建 Pod，并删除不再匹配节点上的 Pod。这个过程异步完成，实际运行还要满足资源与调度条件。

## 滚动更新时如何控制节点可用性

```bash
kubectl explain ds.spec.updateStrategy.rollingUpdate
```

DaemonSet 默认使用 `RollingUpdate`，模板修改后逐步替换旧 Pod；也可以选择 `OnDelete`，由操作者删除旧 Pod 后再创建新版本。滚动更新的两个参数需要一起理解：

| 字段 | 默认值 | 作用 |
| --- | --- | --- |
| `maxUnavailable` | `1` | 更新过程中允许不可用的目标节点数量，可用整数或百分比表示 |
| `maxSurge` | `0` | 允许在已有可用旧 Pod 的节点上额外启动新 Pod 的数量，可用整数或百分比表示 |

两者不能同时为 `0`，也不能同时大于 `0`。默认配置通常先删除一部分旧 Pod，再创建新 Pod；只有启用 surge 的配置，才会在旧 Pod 仍可用时先启动替代 Pod。官方[更新 DaemonSet](https://kubernetes.io/docs/tasks/manage-daemon/update-daemon-set/)介绍了这些参数。

下面使用 `maxSurge: 1`、`maxUnavailable: 0`，允许在一个节点上先增加新版本 Pod，待其可用后删除旧 Pod。节点需要有同时容纳两份 Pod 的资源；使用同一 `hostPort`、独占设备或不可并发写入的宿主机目录时，还要确认两个版本能否共存。此示例没有配置 readiness probe，实际发布应加入能反映采集器就绪情况的探针。

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: ds-test
  namespace: default
  labels:
    app: fluentd-logging
spec:
  selector:
    matchLabels:
      name: fluentd-elasticsearch
  updateStrategy:
    type: RollingUpdate
    rollingUpdate: 
      maxSurge: 1 # 最多在1个已有可用旧Pod的节点上额外启动新Pod
      maxUnavailable: 0 # 不主动以停止旧Pod的方式制造不可用节点
  template:
    metadata:
      labels:
        name: fluentd-elasticsearch
    spec:
      tolerations:
      - key: node-role.kubernetes.io/control-plane #容忍控制节点的污点
        operator: Exists
        effect: NoSchedule
      containers:
      - name: fluentd-elasticsearch
        image: quay.io/fluentd_elasticsearch/fluentd:v5.0.1
        imagePullPolicy: IfNotPresent
        resources: 
          requests: 
            cpu: 100m
            memory: 200Mi
          limits: 
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
      volumes:
      - name: varlog # 挂载系统日志
        hostPath:
          path: /var/log
      - name: varlibdockercontainers # 挂载容器日志
        hostPath:
          path: /var/lib/docker/containers
```

## 查看更新状态与回滚

修改镜像或 Pod 模板后，先查看发布状态和历史版本。下面的回滚命令会修改 DaemonSet，只应在确认目标历史版本存在且需要回退时执行：

```bash
# 查看更新状态
kubectl rollout status ds/ds-test
# 查看更新历史版本
kubectl rollout history ds ds-test
# 回滚到历史版本
kubectl rollout undo ds ds-test --to-revision=1 
```

