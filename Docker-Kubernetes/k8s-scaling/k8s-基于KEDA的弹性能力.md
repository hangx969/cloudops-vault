---
title: "KEDA：事件驱动扩缩容与 KServe 实战"
date: 2026-09-15
tags:
  - kubernetes
  - kubernetes/autoscaling
  - keda
  - hpa
  - scale-to-zero
  - kserve
  - prometheus
  - vllm
aliases:
  - K8s基于KEDA的弹性能力
  - KEDA事件驱动扩缩容
  - KEDA vs HPA 2026 终极对比
  - KEDA vs HPA 2026 终极对比：v1.36 原生缩零后该选谁？
  - KServe + KEDA 实战：基于请求指标实现服务自动扩缩容
  - KServe 集成 KEDA
  - vLLM 请求指标扩缩容
source_urls:
  - https://mp.weixin.qq.com/s/rMLNgv3N9vqkOQ28-833RQ
---

# KEDA：事件驱动扩缩容与 KServe 实战

<div id="kubernetes-keda-事件驱动自动扩缩容原理选型与-kserve-实战" class="legacy-anchor"></div>
<div id="kubernetes-keda-事件驱动自动扩缩容原理选型与-kserve-实战_1" class="legacy-anchor"></div>

Kubernetes 事件驱动自动扩缩容的原理与选型。

KEDA（Kubernetes Event-Driven Autoscaling）把消息积压、请求并发、数据库查询、Prometheus 指标和定时计划等业务信号转换为 Kubernetes 扩缩容决策。使用 KEDA 时，需要理解资源模型、与 HPA 的控制边界和 Scale-to-Zero 行为，再结合常见事件源或 KServe + vLLM 场景选择扩缩容指标。

> [!info] 示例版本
> 通用示例与 KServe 实测使用 KEDA 2.17.2；KEDA 与 Kubernetes 的字段、兼容矩阵和升级要求会变化，生产使用前应核对目标版本的 [KEDA 文档](https://keda.sh/docs/) 与 [Release Notes](https://github.com/kedacore/keda/releases)。

原示例对应的版本化入口：[KEDA 2.17 Getting Started](https://keda.sh/docs/2.17/) 与 [KEDA 2.17 Scalers](https://keda.sh/docs/2.17/scalers/)。

## 为什么需要事件驱动扩缩容

CPU 和内存能反映资源压力，却不一定等价于业务工作量。CPU 升高可能来自异常循环、依赖故障或运行时抖动；盲目扩容既不一定解决问题，还可能放大故障。队列消费者、批处理 Worker 与模型推理服务更适合使用以下信号：

- 消息队列：Kafka lag、RabbitMQ 队列长度、Redis 列表或 Stream 积压；
- 请求压力：QPS、并发请求数、正在执行与等待中的请求数；
- 数据状态：SQL 查询得到的 pending 记录数；
- 自定义指标：Prometheus、Datadog、New Relic 等观测系统中的业务指标；
- 时间计划：Cron 触发器在固定时段扩缩容；
- 一次性任务：按事件数量创建 Job，处理完成后退出。

KEDA 的核心目标是“有工作时启动并扩展，无工作时缩减，必要时缩到 0”。这尤其适合异步任务和昂贵的 CPU/GPU 工作负载。

## KEDA 架构与工作流

![KEDA 架构](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202508241048999.png)

KEDA 不是 HPA 的替代实现，而是把外部事件源、认证和指标适配封装起来，并管理相应的 HPA。当前架构的职责边界可参考 [KEDA Concepts](https://keda.sh/docs/latest/concepts/)：

1. KEDA Operator 监听 ScaledObject/ScaledJob，轮询事件源并管理扩缩容资源；
2. 对 ScaledObject，Operator 负责 `0 ↔ 1` 的激活与缩零；
3. KEDA Metrics API Server 把外部指标暴露给 Kubernetes External Metrics API；
4. HPA 读取指标并负责 `1 ↔ N` 的副本计算；
5. Admission Webhook 在资源创建或更新时校验常见冲突与非法配置。

```mermaid
flowchart LR
    S[外部事件源] --> O[KEDA Operator]
    O -->|0 ↔ 1| W[Deployment / StatefulSet]
    S --> M[KEDA Metrics API Server]
    M --> A[External Metrics API]
    A --> H[HPA]
    H -->|1 ↔ N| W
```

> [!note] 激活阈值与扩缩容阈值
> KEDA 将缩零/唤醒和 1～N 扩缩容分成两个阶段。支持的 Scaler 可用 `activation*` 参数控制激活阈值，常规阈值则交给 HPA 计算。若 `minReplicaCount >= 1`，激活阈值不会参与决策。

## 核心资源

| 资源 | 用途 |
| --- | --- |
| `ScaledObject` | 为 Deployment、StatefulSet 或支持 `/scale` 子资源的对象配置持续扩缩容，并自动管理 HPA |
| `ScaledJob` | 根据事件积压创建一次性 Job，适合图片、视频、批处理任务 |
| `TriggerAuthentication` | 在命名空间内声明 Scaler 的认证来源 |
| `ClusterTriggerAuthentication` | 跨命名空间复用认证配置 |
| KEDA Operator | 监听 KEDA CRD，轮询 Scaler，并负责 0↔1 |
| KEDA Metrics API Server | 向 HPA 提供 External Metrics |
| Admission Webhook | 校验 KEDA 资源与同一目标的控制冲突 |

KEDA 支持 Kafka、RabbitMQ、AWS SQS、Azure Service Bus、NATS、Redis、PostgreSQL、MySQL、MongoDB、Prometheus、Cron 等多类 Scaler。完整列表以 [KEDA Scalers](https://keda.sh/docs/latest/scalers/) 为准。

认证信息不应直接写进 ScaledObject。TriggerAuthentication 可以引用 Kubernetes Secret、ConfigMap、环境变量或云身份；当前版本还支持从 GCP Secret Manager 等外部 Secret 服务获取认证材料。原对比稿把 GCP Secret Manager 与 ConfigMap 认证误标为 KEDA 2.16 新特性，实际上它们更早已经进入 KEDA，本文不再绑定错误版本。

## HPA、原生 Scale-to-Zero 与 KEDA 的边界

### HPA 的指标与计算

HPA 的基础计算公式是：

```text
期望副本数 = ceil(当前副本数 × 当前指标值 / 目标指标值)
```

`autoscaling/v2` 支持 Resource、Pods、Object、External 等指标。Resource 指标通常来自 Metrics Server；自定义与外部指标需要相应 Adapter。HPA 可以同时配置多个指标，并采用各指标建议副本数中的最大值。

### Kubernetes 1.37 原生 HPA Scale-to-Zero

Kubernetes 1.37 将 `HPAScaleToZero` 提升为 Beta 并默认启用。原生 HPA 使用适合的 Object 或 External 指标时，可以把 `minReplicas` 设为 0，并在指标重新活跃时从 0 拉起。版本状态与升级边界见 [Kubernetes Feature Gates](https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/) 和 [Kubernetes 1.37 Scale-to-Zero 公告](https://kubernetes.io/blog/2026/09/02/kubernetes-v1-37-hpa-scale-to-zero-beta/)。

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: batch-processor
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: batch-processor
  minReplicas: 0
  maxReplicas: 20
  metrics:
    - type: External
      external:
        metric:
          name: queue_depth
        target:
          type: AverageValue
          averageValue: "10"
```

硬性边界：

- `HPAScaleToZero` 必须在 kube-apiserver 和 kube-controller-manager 上同时可用；
- `minReplicas: 0` 至少需要一个 Object 或 External 指标，不能只依赖 CPU/内存 Resource 指标；
- 指标在 Pod 为 0 时仍必须可读取，否则 HPA 没有唤醒信号；
- Kubernetes Service 不会在后端为 0 时缓存 HTTP 请求；同步请求缩零需要网关、队列或 KEDA HTTP Add-on 等缓冲层；
- 指标源故障时，HPA 会报告 `ScalingActive=False`，应监控并准备人工或自动兜底。

### KEDA 仍然解决什么问题

原生 HPA 1.37 解决了“能否缩到 0”，但没有替代事件源连接、认证管理和 Scaler 运维。KEDA 的价值仍在于：

- 对接大量事件源，无需为每个中间件自行开发 External Metrics Adapter；
- 分离激活阈值与扩缩容阈值；
- 在同一 ScaledObject 中组合多个 Trigger；
- 使用 TriggerAuthentication/ClusterTriggerAuthentication 管理认证；
- 通过 ScaledJob 把事件积压映射为一次性 Job；
- 为指标故障提供可配置的 fallback 副本策略。

### 选型矩阵

| 场景 | 推荐 | 原因 |
| --- | --- | --- |
| 标准 HTTP 服务，CPU/内存与负载相关 | HPA | 原生、依赖少、排障链路短 |
| 已有稳定 Object/External Metrics Adapter，集群为 1.37+ | 原生 HPA | 可直接缩零，减少额外组件 |
| Kafka/RabbitMQ/Redis 等队列消费者 | KEDA | 事件源和认证开箱即用 |
| 多事件源组合触发 | KEDA | ScaledObject 支持多个 Trigger 与组合策略 |
| 一次性批处理 | KEDA ScaledJob | 按积压创建 Job，而不是维持常驻 Deployment |
| KServe/vLLM 请求压力 | KServe + Prometheus + KEDA | 直接以运行中和排队请求数驱动副本 |
| 同一系统的不同工作负载 | HPA 与 KEDA 分工 | HTTP Deployment 用 HPA，队列消费者用 KEDA |

> [!warning] 单一控制器原则
> 不要让手工 HPA 与 KEDA ScaledObject 同时管理同一个 Deployment。KEDA 会自行创建并管理 HPA；双重控制会造成副本数争用和震荡。

## KEDA 资源模型

### ScaledObject

~~~yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: video-processing-scaledobject
  namespace: default
spec:
  scaleTargetRef:
    name: order-processor # 目标deployment名称
  pollingInterval: 30 # 每30s检查一次队列
  cooldownPeriod: 300 # 扩缩容后等待5分钟。防止扩缩容抖动
  minReplicaCount: 1
  maxReplicaCount: 10
  triggers:
  - type: rabbitmq
    metadata:
      queueName: "video-processing-queue" # rabbitmq队列名称
      mode: QueueLength # 监听类型
      value: "50" # 当队列中每个实例平均消息50条及以上时触发扩容
  authenticationRef: # 不推荐直接把用户名密码写在这里。都是用一个TriggerAuthentication绑定
    name: keda-trigger-auth-rabbitmq-conn # TriggerAuthentication名称
~~~

### ScaledJob

~~~yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledJob
metadata:
  name: video-processing-scaledjob
  namespace: default
spec:
  jobTargetRef:
    parallelism: 1 # 每次只创建一个job实例
    completions: 1 # 每个Job只运行一次
    template:
      spec:
        restartPolicy: Never
        containers:
        - name: video-processer
          image: busybox:1.28
  pollingInterval: 30 # 每30s检查一次队列
  maxReplicaCount: 10 # 最多同时运行10个job
  successfulJobsHistoryLimit: 3 # 保留3个成功job的历史
  failedJobsHistoryLimit: 1 # 保留1个失败的job历史
  triggers:
  - type: rabbitmq
    metadata:
      queueName: "video-processing-queue" # rabbitmq队列名称
      mode: QueueLength # 监听类型
      value: "50" # 当队列中每个实例平均消息50条及以上时触发扩容
  authenticationRef: # 不推荐直接把用户名密码写在这里。都是用一个TriggerAuthentication绑定
    name: keda-trigger-auth-rabbitmq-conn # TriggerAuthentication名称
~~~

### TriggerAuthentication

连接基础组件的时候需要认证，KEDA设计了单独的资源来保存认证信息。

TriggerAuthentication直接从k8s secret读取认证信息，它本身并不保存认证信息。

~~~yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secrets
  namespace: default
type: Opaque
stringData:
  mysql_conn_str: user:password@tcp(mysql:3306)/status_db

---
apiVersion: keda.sh/v1alpha1
kind: TriggerAuthentication
metadata:
  name: keda-trigger-auth-mysql-conn
  namespace: default
spec:
  secretTargetRef:
  - parameter: connectionString # Scaler参数名字。固定值不能改。应该填啥去keda官网查。
    name: mysql-secret # secret名称
    key: mysql_conn_str # secret的key名称

  # 也支持基于configMap加载
  # configMapTargetRef:
  # - parameter: connectionString # Scaler参数名字。固定值不能改。应该填啥去keda官网查。
  #   name: keda-cm-name # cm名称
  #   key: azure-storage-connectionstring # cm的key名称

  # 也支持基于env加载
  # - parameter: region # Scaler参数名字。固定值不能改。应该填啥去keda官网查。
  #   name: my-env-car # 取哪个环境变量的值
  #   containerName: my-container # 从哪个容器中取（keda管理的deployment中的pod中的某个container）
~~~

## 部署 KEDA

- [官方 Helm 安装说明](https://keda.sh/docs/2.17/deploy/#helm)
- [Artifact Hub：KEDA Chart](https://artifacthub.io/packages/helm/kedacore/keda)
- [GitHub Releases](https://github.com/kedacore/keda/releases)

本文实测版本为 2.17.2。可以直接从仓库安装：

```bash
helm repo add kedacore https://kedacore.github.io/charts
helm repo update

helm upgrade --install keda kedacore/keda \
  -n keda --create-namespace \
  --version 2.17.2 \
  --wait
```

需要离线审阅或自定义 values 时，先下载 Chart：

```bash
helm pull kedacore/keda --version 2.17.2
tar xzf keda-2.17.2.tgz

helm upgrade --install keda ./keda \
  -n keda --create-namespace \
  -f values.yaml \
  --wait
```

安装后同时检查三个组件与聚合 API：

```bash
kubectl get pod -n keda
kubectl get crd | grep keda.sh
kubectl get apiservice v1beta1.external.metrics.k8s.io
```

预期 Operator、Admission Webhook、Metrics API Server 均为 Running，且 `v1beta1.external.metrics.k8s.io` 的 `AVAILABLE=True`。只有 CRD 可见但 External Metrics API 不可用时，ScaledObject 可以创建，HPA 仍然读不到 KEDA 指标。

## 通用场景实战

### 周期性扩缩容

KEDA支持周期性弹性收缩服务，且支持缩容至0。使用场景：

1. 比如有很多任务，占用大量资源，不能在白天跑，需要在晚上跑。
2. 比如有个服务只有每天早上7-9点属于业务高峰，就可以利用KEDA实现在7-9点扩展服务，除此之外的时间缩减副本，以节省资源。

~~~yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: cron-scaledobject
  namespace: default
spec:
  scaleTargetRef:
    name: nginx-hpa # 扩容对象是deployment
  minReplicaCount: 0 # 最低副本数
  cooldownPeriod: 300 # 冷却期：到end时间后，过多久再缩容
  triggers:
  - type: cron
    metadata:
      timezone: Asia/Shanghai
      # 分钟 小时 日 月 星期
      start: 45 10 * * * # 每天北京时间10:45扩容
      end: 55 10 * * * # 每天北京时间10:55缩容
      desiredReplicas: "3" # 扩容后的副本数
~~~

### 基于 RabbitMQ 消息队列扩缩容

KEDA 支持基于 RabbitMQ、Kafka、Redis 等消息队列的积压或消费速率扩缩容，使消费者数量与待处理工作量匹配。

#### 创建测试RabbitMQ

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: rabbitmq
spec:
  type: NodePort
  selector:
    app: rabbitmq
  ports:
  - name: web
    port: 5672
    protocol: TCP
    targetPort: 5672
  - name: http
    port: 15672
    protocol: TCP
    targetPort: 15672
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: rabbitmq
  name: rabbitmq
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rabbitmq
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: rabbitmq
    spec:
      containers:
      - env:
        - name: TZ
          value: Asia/Shanghai
        - name: LANG
          value: C.UTF-8
        - name: RABBITMQ_DEFAULT_USER
          value: user
        - name: RABBITMQ_DEFAULT_PASS
          value: password
        image: registry.cn-beijing.aliyuncs.com/dotbalo/rabbitmq:4.0.5-management-alpine
        imagePullPolicy: IfNotPresent
        livenessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 5672
          timeoutSeconds: 2
        name: rabbitmq
        ports:
        - containerPort: 5672
          name: web
          protocol: TCP
        readinessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 5672
          timeoutSeconds: 2
~~~

通过NodePort访问RabbitMQ UI，注意用的是name为http的端口

#### 模拟消息写入

~~~yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: rabbitmq-publish
spec:
  backoffLimit: 4
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: rabbitmq-client
        image: registry.cn-beijing.aliyuncs.com/dotbalo/rabbitmq-publish:v1.0
        imagePullPolicy: IfNotPresent
        command:
        - "send"
        - "amqp://user:password@rabbitmq.default.svc.cluster.local:5672"
        - "100"
~~~

#### 模拟消费者

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rabbitmq-consumer
  namespace: default
  labels:
    app: rabbitmq-consumer
spec:
  selector:
    matchLabels:
      app: rabbitmq-consumer
  template:
    metadata:
      labels:
        app: rabbitmq-consumer
    spec:
      containers:
        - name: rabbitmq-consumer
          image: registry.cn-beijing.aliyuncs.com/dotbalo/rabbitmq-consumer:v1.0
          imagePullPolicy: IfNotPresent
          command:
          - receive
          args:
          - "amqp://user:password@rabbitmq.default.svc.cluster.local:5672"
~~~

#### 创建 TriggerAuthentication

这里用secret保存连接字符串，也可以直接引用RabbitMQ中的用户名密码env

~~~yaml
apiVersion: v1
kind: Secret
metadata:
  name: keda-rabbitmq-secret
stringData: # stringData 便于直接填写明文；API Server 最终仍会把 Secret 数据编码后存入 data。
  host: amqp://user:password@rabbitmq.default.svc.cluster.local:5672 # amqp地址
---
apiVersion: keda.sh/v1alpha1
kind: TriggerAuthentication
metadata:
  name: keda-trigger-auth-rabbitmq-conn
spec:
  secretTargetRef:
    - parameter: host
      name: keda-rabbitmq-secret
      key: host
~~~

#### 创建 ScaledObject

配置参数参考：[RabbitMQ Queue Scaler](https://keda.sh/docs/2.17/scalers/rabbitmq-queue/)

~~~yaml
---
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: rabbitmq-scaledobject
spec:
  scaleTargetRef:
    name: rabbitmq-consumer
  pollingInterval: 5 # 将默认 30 秒轮询缩短为 5 秒；生产环境按事件延迟和上游压力调整
  cooldownPeriod: 30 # 默认 300 秒；只控制 KEDA 从 1 缩到 0 的等待时间
  minReplicaCount: 1
  maxReplicaCount: 5 # 最大副本数
  triggers:
  - type: rabbitmq
    metadata:
      protocol: amqp # 这是最常用的连接协议
      queueName: hello
      mode: QueueLength # 监听模式，队列长度(QueueLength)或消息速率(MessageRate)。一般用队列长度来做判断
      value: "50" # 消息数或每秒速率
    authenticationRef:
      name: keda-trigger-auth-rabbitmq-conn
~~~

### 基于数据库扩缩容

例如工单系统可查询数据库中的待处理记录数：当 pending 工单达到阈值时扩容处理程序，积压清空后再缩容。

#### 模拟数据库实例

~~~sh
kubectl create deployment mysql --image=registry.cn-beijing.aliyuncs.com/dotbalo/mysql:8.0.20
kubectl set env deploy mysql MYSQL_ROOT_PASSWORD=password
kubectl expose deploy mysql --port 3306

# 进入数据库创建测试的表
kubectl exec -ti mysql-6d8bd866d8-q89nj -- bash
mysql -uroot -hmysql -p
create database dukuan;
use dukuan;
CREATE TABLE orders (
id INT AUTO_INCREMENT PRIMARY KEY,
customer_name VARCHAR(100),
order_amount DECIMAL(10, 2),
status ENUM('pending', 'processed') DEFAULT 'pending',
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
~~~

#### 模拟数据写入程序

~~~sh
kubectl create job insert-orders-job --image=registry.cn-beijing.aliyuncs.com/dotbalo/mysql:insert
~~~

再次进入数据库查看数据

~~~sh
kubectl exec -ti mysql-6d8bd866d8-7qjx9 -- bash
use dukuan;
select * from orders;
~~~

结果会出现工单状态，有一些pending状态的即为未处理完的工单。需要创建数据处理程序。

#### 创建数据处理程序

~~~sh
kubectl create deploy update-orders --image=registry.cn-beijing.aliyuncs.com/dotbalo/mysql:process
~~~

再次进入数据库查看数据：

~~~sh
kubectl exec -ti mysql-6d8bd866d8-7qjx9 -- bash
use dukuan;
select * from orders;
~~~

工单状态会变成processed表示处理完成。

后面我们创建scaledObject，用SQL语句查询数据库中对应未处理的工单数量，当未处理的工单数量大于指定的值时，触发工单处理的deployment的扩容。

#### 创建TriggerAuthentication

~~~yaml
apiVersion: v1
kind: Secret
metadata:
  name: keda-mysql-secret
stringData:
  mysql_conn_str: root:password@tcp(mysql.default.svc.cluster.local:3306)/dukuan
---
apiVersion: keda.sh/v1alpha1
kind: TriggerAuthentication
metadata:
  name: keda-trigger-auth-mysql-conn
spec:
  secretTargetRef:
    - parameter: connectionString
      name: keda-mysql-secret
      key: mysql_conn_str
~~~

#### 创建 ScaledObject

~~~yaml
---
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: mysql-scaledobject
spec:
  scaleTargetRef:
    name: update-orders
  pollingInterval: 5 # 将默认 30 秒轮询缩短为 5 秒
  cooldownPeriod: 30 # 冷却时间，默认300秒
  minReplicaCount: 0
  maxReplicaCount: 5 # 最大副本数
  triggers:
  - type: mysql
    metadata:
      queryValue: "4.4" # 触发扩缩容的平均值
      query: "SELECT COUNT(*) FROM orders WHERE status='pending'"
    authenticationRef:
      name: keda-trigger-auth-mysql-conn
~~~

再次触发数据插入：

~~~sh
kubectl delete job insert-orders-job
kubectl create job insert-orders-job --image=registry.cn-beijing.aliyuncs.com/dotbalo/mysql:insert
~~~

可以观察到在insert-order-jobs完成后，立刻触发了updat-orders deployment的扩容，数据处理得很快，迅速就低于设定值了。30s之后就缩容到0了。

### ScaledJob 任务处理

KEDA可以使用ScaledJob实现单次或者临时的任务处理，用来处理一些数据，比如图片、视频等。

#### 基于 Redis 扩缩容

假设有一个需求，需要从Redis队列获取数据，然后进行处理，就可以使用ScaledJob实现。

首先创建一个Redis实例：

~~~sh
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update bitnami
helm upgrade -i redis bitnami/redis \
--set global.imageRegistry=docker.kubeasy.com \
--set global.redis.password=dukuan \
--set architecture=standalone \
--set master.persistence.enabled=false \
--version 20.1.6
~~~

##### 创建TriggerAuthentication

~~~yaml
apiVersion: v1
kind: Secret
metadata:
  name: redis-so-secret
type: Opaque
stringData:
  redis_username: ""
  redis_password: "dukuan"
---
apiVersion: keda.sh/v1alpha1
kind: TriggerAuthentication
metadata:
  name: redis-so-ta
spec:
  secretTargetRef:
  - parameter: username
    name: redis-so-secret
    key: redis_username
  - parameter: password
    name: redis-so-secret
    key: redis_password
~~~

##### 测试写入数据

~~~sh
kubectl exec -ti redis-master-0 -- bash
redis-cli -h redis-master -a dukuan
# 写入队列数据
LPUSH test_list "t1" "t2" "t3"
LRANGE test_list 0 2
# 读取数据
RPOP test_list
LPOP test_list
~~~

##### 创建 ScaledJob 监听队列

~~~yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledJob
metadata:
  name: redis-queue-scaledjob
spec:
  jobTargetRef:
    parallelism: 1  # 每次只启动一个 Job 实例
    completions: 1  # 每个 Job 只需要完成一次
    backoffLimit: 4  # 最大重试次数
    template:
      spec:
        containers:
        - name: redis-queue-consumer
          image: registry.cn-beijing.aliyuncs.com/dotbalo/redis:process
  pollingInterval: 30  # 每 30 秒检查一次队列中的消息数量
  successfulJobsHistoryLimit: 3  # 保留最近 3 个成功的 Job
  failedJobsHistoryLimit: 3  # 保留最近 3 个失败的 Job
  maxReplicaCount: 5  # 最多同时运行 5 个 Job
  triggers:
  - type: redis
    metadata:
      address: redis-master.default.svc.cluster.local:6379
      listName: test_list
      listLength: "5"
    authenticationRef:
      name: redis-so-ta
~~~

##### 写入测试数据

~~~sh
LPUSH test_list "t1" "t2" "t3"
LPUSH test_list "t1" "t2" "t3"
LPUSH test_list "t1" "t2" "t3"
LRANGE test_list 0 8
~~~

查看redis-queue-scaledjob的日志，就可以看到job扩容出新的pod处理数据。

## Kafka ScaledObject 示例

Kafka 消费者通常以 consumer group lag 作为扩缩容信号：

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: order-consumer
spec:
  scaleTargetRef:
    name: order-consumer
  pollingInterval: 30
  cooldownPeriod: 300
  minReplicaCount: 0
  maxReplicaCount: 50
  triggers:
    - type: kafka
      metadata:
        bootstrapServers: kafka-broker:9092
        consumerGroup: order-processor
        topic: orders
        lagThreshold: "100"
        offsetResetPolicy: latest
```

`lagThreshold` 应按单 Pod 消费吞吐量、消息处理时限和分区数压测确定；副本数还受 Kafka 分区可并行度约束。

## KServe + KEDA：基于请求指标的模型服务实战

模型服务运行后，固定副本数很难同时兼顾突发请求和资源利用率。本文通过一个 Demo，为 KServe 模型服务接入 KEDA，根据 vLLM 的请求指标自动调整副本数，并验证服务从 `1 -> 2 -> 1` 的扩缩容过程。

![KServe 集成 KEDA 的自动扩缩容链路](https://mmbiz.qpic.cn/sz_mmbiz_jpg/TKUQcaFRv0FvqP1P3HoaO2hjaaNSLepQoFzr8MeicVIncdg1uic7Svdu1xBcjfIyDLCsSScNftk59sOLAIiccewGfkOtTyAzibhOB9l2XxerHzI/640?wx_fmt=jpeg&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

### 环境准备

#### 实现思路

需要额外安装 KEDA 和 Prometheus，工作流程如下：

1. KServe 创建 Predictor Deployment 启动模型服务，底层推理引擎 vLLM 通过 `/metrics` 暴露运行指标。
2. Prometheus 采集 `vllm:num_requests_running` 和 `vllm:num_requests_waiting` 等指标。
3. KEDA 查询 Prometheus，并通过 External Metrics API 将查询结果暴露为 HPA 可以使用的外部指标。
4. HPA 比较当前指标值与目标值，计算期望副本数并调整 Predictor Deployment。

#### KEDA 版本与组件前提

本实验实测 KEDA 2.17.2。安装方式见本文前面的“部署 KEDA”；在进入模型服务配置前，应确认 Operator、Admission Webhook 和 Metrics API Server 均正常，尤其是 `v1beta1.external.metrics.k8s.io` 必须处于 `Available=True`。只有 CRD 就绪并不代表 HPA 能读取 KEDA 提供的指标。

#### 部署 Prometheus

使用 `kube-prometheus-stack` 部署 Prometheus 和 Prometheus Operator，关闭 Grafana、Alertmanager、Exporter 和默认告警规则，仅保留指标采集所需组件：

```bash
helm upgrade --install prometheus \
  oci://ghcr.io/prometheus-community/charts/kube-prometheus-stack \
  -n monitoring --create-namespace \
  --version 88.2.0 \
  --set grafana.enabled=false \
  --set alertmanager.enabled=false \
  --set kubeStateMetrics.enabled=false \
  --set nodeExporter.enabled=false \
  --set defaultRules.create=false \
  --set kubeApiServer.enabled=false \
  --set kubelet.enabled=false \
  --set kubeControllerManager.enabled=false \
  --set coreDns.enabled=false \
  --set kubeDns.enabled=false \
  --set kubeEtcd.enabled=false \
  --set kubeScheduler.enabled=false \
  --set kubeProxy.enabled=false \
  --set prometheusOperator.admissionWebhooks.enabled=false \
  --set prometheusOperator.tls.enabled=false \
  --wait
```

先确认 Prometheus Service 已创建。后续 InferenceService 和查询都使用这个 Service；如果没有输出，应先检查 Helm Release 和 Prometheus Pod，不要继续创建 InferenceService：

```bash
kubectl get svc prometheus-kube-prometheus-prometheus -n monitoring
kubectl get pod -n monitoring
kubectl get pod,svc -n monitoring
```

当前配置不创建 PrometheusRule，因此一并关闭了只用于校验规则的 Admission Webhook。安装完成后，集群中应保留 Prometheus Operator 和 Prometheus 两个 Pod。

### 配置自动扩缩容

#### 创建 InferenceService

测试节点只有一张 GPU，而 Demo 需要把服务扩到两个副本，因此使用 HAMi DRA 共享 GPU。创建 ResourceClaimTemplate 和完整的 InferenceService，同时配置每个副本的 GPU 配额、模型和 KEDA 自动扩缩容：

```bash
cat <<'EOF' > qwen-llm.yaml
apiVersion: resource.k8s.io/v1
kind: ResourceClaimTemplate
metadata:
  name: qwen-hami-gpu
  namespace: kserve-test
spec:
  spec:
    devices:
      requests:
        - name: gpu
          exactly:
            deviceClassName: hami-core-gpu.project-hami.io
            allocationMode: ExactCount
            count: 1
            capacity:
              requests:
                memory: 3Gi
                cores: "20"
---
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: qwen-llm
  namespace: kserve-test
  annotations:
    serving.kserve.io/deploymentMode: Standard
    serving.kserve.io/autoscalerClass: keda
spec:
  predictor:
    minReplicas: 1
    maxReplicas: 2
    resourceClaims:
      - name: gpu
        resourceClaimTemplateName: qwen-hami-gpu
    autoScaling:
      metrics:
        - type: External
          external:
            metric:
              backend: prometheus
              serverAddress: http://prometheus-kube-prometheus-prometheus.monitoring.svc:9090
              query: >-
                sum(vllm:num_requests_running{namespace="kserve-test",pod=~"qwen-llm-predictor-.*"})
                +
                sum(vllm:num_requests_waiting{namespace="kserve-test",pod=~"qwen-llm-predictor-.*"})
            target:
              type: Value
              value: "1"
    model:
      modelFormat:
        name: huggingface
      image: docker.m.daocloud.io/kserve/huggingfaceserver:v0.18.0-gpu
      storageUri: pvc://qwen-model
      args:
        - --model_name=qwen
        - --max_model_len=4096
        - --max-num-seqs=32
        - --gpu-memory-utilization=0.8
      resources:
        requests:
          cpu: "1"
          memory: 4Gi
        limits:
          cpu: "2"
          memory: 6Gi
        claims:
          - name: gpu
EOF

kubectl apply -f qwen-llm.yaml

kubectl wait --for=condition=Ready \
  inferenceservice/qwen-llm -n kserve-test --timeout=10m
```

每个 Predictor 副本通过 `qwen-hami-gpu` 申请 3Gi 显存和 20% GPU 核心，因此单 GPU 节点可以同时运行两个副本。KServe 创建 Predictor Deployment 和 ScaledObject，KEDA 再创建 HPA 管理副本数。

#### 扩缩容配置解析

这份 YAML 中的扩缩容配置如下：

```yaml
metadata:
  annotations:
    serving.kserve.io/autoscalerClass: keda
spec:
  predictor:
    minReplicas: 1
    maxReplicas: 2
    autoScaling:
      metrics:
        - type: External
          external:
            metric:
              backend: prometheus
              serverAddress: http://prometheus-kube-prometheus-prometheus.monitoring.svc:9090
              query: >-
                sum(vllm:num_requests_running{namespace="kserve-test",pod=~"qwen-llm-predictor-.*"})
                +
                sum(vllm:num_requests_waiting{namespace="kserve-test",pod=~"qwen-llm-predictor-.*"})
            target:
              type: Value
              value: "1"
```

各参数含义：

- `autoscalerClass: keda`：使用 KEDA 进行扩缩容。
- `minReplicas`、`maxReplicas`：限制最小和最大副本数。
- `serverAddress`：Prometheus 地址。
- `query`：使用 `running + waiting`，同时统计正在执行和已经进入 vLLM 队列的请求。
- `target.value`：每个副本期望承载的目标值。

Prometheus 查询得到的是所有 Predictor Pod 的请求总数：

```text
Query = running 请求数 + waiting 请求数
```

`target.value: 1` 表示希望每个副本平均处理 1 个请求。当前副本范围是 1～2：

- 当前只有 1 个副本时，如果 `Query = 0` 或 `1`，保持 1 个副本。
- 当前只有 1 个副本时，如果 `Query >= 2`，说明请求超过单个副本的目标值，扩到 2 个副本。
- 扩容后即使请求继续增加，也不会超过 `maxReplicas: 2`。
- 负载停止后，`Query` 回到 `0` 或 `1`，等待 300 秒缩容稳定窗口结束，再缩回 1 个副本。

#### 配置 ServiceMonitor

Prometheus Stack 不会自动采集 `qwen-llm`。创建 ServiceMonitor，通过 InferenceService Label 选择 KServe 生成的 Predictor Service：

```bash
cat <<'EOF' > qwen-llm-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: qwen-llm
  namespace: monitoring
  labels:
    release: prometheus
spec:
  namespaceSelector:
    matchNames:
      - kserve-test
  selector:
    matchLabels:
      serving.kserve.io/inferenceservice: qwen-llm
  endpoints:
    - port: qwen-llm-predictor
      path: /metrics
      interval: 5s
EOF

kubectl apply -f qwen-llm-monitor.yaml
```

ServiceMonitor 不会通过 Service 的 ClusterIP 随机抓取一个后端。Prometheus Operator 会读取 Service 对应的 EndpointSlice，并把每个 Predictor Pod 都作为独立 Target。

#### 检查指标和扩缩容资源

通过 Kubernetes Service Proxy 检查 Target。当前只有一个 Predictor，应看到一行 `qwen-llm-predictor-*`，状态为 `up`：

```bash
kubectl get --raw \
  '/api/v1/namespaces/monitoring/services/http:prometheus-kube-prometheus-prometheus:http-web/proxy/api/v1/targets?state=active' | \
  jq -r '.data.activeTargets[] | select(.labels.namespace == "kserve-test") | [.labels.pod, .health, .scrapeUrl] | @tsv'
```

检查空闲时的指标：

```bash
kubectl get --raw \
  '/api/v1/namespaces/monitoring/services/http:prometheus-kube-prometheus-prometheus:http-web/proxy/api/v1/query?query=sum(vllm:num_requests_running%7Bnamespace=%22kserve-test%22,pod=~%22qwen-llm-predictor-.*%22%7D)%2Bsum(vllm:num_requests_waiting%7Bnamespace=%22kserve-test%22,pod=~%22qwen-llm-predictor-.*%22%7D)' | \
  jq -r '[.status, .data.resultType, (.data.result | length), .data.result[0].value[1]] | @tsv'
```

实测输出：

```text
success vector 1 0
```

KServe 创建 Deployment 和 ScaledObject，KEDA 再创建并管理 HPA：

```bash
kubectl get inferenceservice qwen-llm -n kserve-test
kubectl get scaledobject qwen-llm-predictor -n kserve-test
kubectl get hpa keda-hpa-qwen-llm-predictor -n kserve-test
kubectl get deployment qwen-llm-predictor -n kserve-test
kubectl get pod -n kserve-test \
  -l serving.kserve.io/inferenceservice=qwen-llm
```

空闲状态下，各条命令输出中的关键字段如下：

```text
qwen-llm-predictor                  READY=True   ACTIVE=False   MIN=1   MAX=2
keda-hpa-qwen-llm-predictor         TARGETS=0/1                 REPLICAS=1
qwen-llm-predictor                  READY=1/1
```

直接读取 HPA，确认缩容稳定窗口：

```bash
kubectl get hpa keda-hpa-qwen-llm-predictor -n kserve-test \
  -o jsonpath='{.spec.behavior.scaleDown.stabilizationWindowSeconds}{"\n"}'
```

当前结果为 `300`。

### 验证自动扩缩容

#### 验证扩容

先查询 Envoy Gateway 的地址，发送一次推理请求确认服务正常：

```bash
ENVOY_SERVICE=$(kubectl get service -n envoy-gateway-system \
  -l gateway.envoyproxy.io/owning-gateway-name=kserve-ingress-gateway \
  -o jsonpath='{.items[0].metadata.name}')

NODE_PORT=$(kubectl get service -n envoy-gateway-system "$ENVOY_SERVICE" \
  -o jsonpath='{.spec.ports[?(@.port==80)].nodePort}')

NODE_IP=$(kubectl get node \
  -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')

GATEWAY_ADDR="${NODE_IP}:${NODE_PORT}"

curl -H 'Host: qwen-llm-kserve-test.example.com' \
  -H 'Content-Type: application/json' \
  "http://${GATEWAY_ADDR}/openai/v1/chat/completions" \
  -d '{
    "model": "qwen",
    "messages": [{"role": "user", "content": "Answer only with the number: 2+3"}],
    "max_tokens": 8,
    "temperature": 0
  }'
```

##### 产生持续负载

```bash
BODY='{"model":"qwen","messages":[{"role":"user","content":"Write a detailed numbered list from 1 to 300, with a complete sentence for every item."}],"max_tokens":768,"temperature":0.7}'
export BODY GATEWAY_ADDR

seq 12 | xargs -n 1 -P 12 bash -c '
  while true; do
    curl -sS --max-time 180 \
      -H "Host: qwen-llm-kserve-test.example.com" \
      -H "Content-Type: application/json" \
      "http://${GATEWAY_ADDR}/openai/v1/chat/completions" \
      -d "$BODY" >/dev/null
  done
'
```

这条命令会一直占用当前终端，并将并发数保持为 12 持续发送请求。

##### 观察扩容结果

另开两个终端，同时观察 Prometheus 指标以及扩缩容资源：

```bash
watch -n 5 'kubectl get --raw "/api/v1/namespaces/monitoring/services/http:prometheus-kube-prometheus-prometheus:http-web/proxy/api/v1/query?query=sum(vllm:num_requests_running%7Bnamespace=%22kserve-test%22,pod=~%22qwen-llm-predictor-.*%22%7D)%2Bsum(vllm:num_requests_waiting%7Bnamespace=%22kserve-test%22,pod=~%22qwen-llm-predictor-.*%22%7D)" | jq -r ".data.result[0].value[1]"'
```

```bash
watch -n 5 'kubectl get scaledobject,hpa,deployment,pod -n kserve-test'
```

本次实测时间线：

```text
启动负载后  Prometheus 查询值升到 12
              ScaledObject ACTIVE=True
              HPA TARGETS=6/1，Deployment REPLICAS=2
约 250 秒后   第二个 vLLM 完成模型加载，两个 Pod 均为 1/1 Running
```

![KServe 模型服务自动扩缩容时间线](https://mmbiz.qpic.cn/sz_mmbiz_jpg/TKUQcaFRv0ENbjbGGO7fvr9gxOhJYeBLb53lJ4kLT0F8YmO1ggO8KRns50Z4Uw0WUGIbn4IrMXyGB1xpsYhXMfd50rHqRb857ibkNg6cnITE/640?wx_fmt=jpeg&from=appmsg&watermark=1)

指标值是整个 Deployment 的 `running + waiting` 总数。两个副本、总值 12 时，平均每个副本为 6，因此 HPA 的目标列显示约 `6/1`。

扩容期间再次调用 Chat Completions 仍返回正确结果，说明 KEDA 已根据 vLLM 指标把服务从 1 个副本扩到 2 个。

#### 验证缩容

回到运行压测的终端，按 `Ctrl+C` 停止全部请求。

先重复 Prometheus 查询，确认结果回到 0，再检查 ScaledObject 变成 `ACTIVE=False`。Deployment 不会立即缩容，因为当前生成的 HPA 带有 300 秒缩容稳定窗口：

```yaml
behavior:
  scaleDown:
    stabilizationWindowSeconds: 300
```

实际缩容时间还会受到 KEDA 轮询、HPA 同步周期和 Pod 终止时间影响。使用以下命令等待 Deployment 回到一个 Ready 副本：

```bash
kubectl wait deployment/qwen-llm-predictor -n kserve-test \
  --for=jsonpath='{.status.replicas}'=1 --timeout=8m
kubectl wait deployment/qwen-llm-predictor -n kserve-test \
  --for=jsonpath='{.spec.replicas}'=1 --timeout=2m
kubectl wait deployment/qwen-llm-predictor -n kserve-test \
  --for=jsonpath='{.status.readyReplicas}'=1 --timeout=2m

kubectl get hpa keda-hpa-qwen-llm-predictor -n kserve-test
kubectl get deployment qwen-llm-predictor -n kserve-test \
  -o custom-columns=NAME:.metadata.name,SPEC:.spec.replicas,STATUS:.status.replicas,READY:.status.readyReplicas
kubectl get pod -n kserve-test \
  -l serving.kserve.io/inferenceservice=qwen-llm
```

本次停止负载后，Prometheus 查询值回到 `0`，ScaledObject 变成 `ACTIVE=False`；约 299 秒后，HPA 将 Deployment 从 2 缩回 1。最后再次执行 Chat Completions 请求，仍然返回 `5`。

### 总结

1. KServe 创建 Predictor Deployment 启动模型服务，vLLM 通过 `/metrics` 暴露运行指标。
2. Prometheus 采集 `vllm:num_requests_running` 和 `vllm:num_requests_waiting`。
3. KEDA 查询 Prometheus，并通过 External Metrics API 将结果暴露为 HPA 可用的外部指标。
4. HPA 根据指标与目标值计算期望副本数，调整 Predictor Deployment。

这套方案将模型服务的扩缩容信号从 CPU/内存利用率转为请求压力，更接近推理服务的实际容量瓶颈。生产落地前还应根据模型加载时间、GPU 可用性、指标延迟和缩容稳定窗口进行压测与参数校准。

## 生产治理与排障

### 冷启动

从 0 恢复到可处理第一条消息，包含 KEDA 轮询、HPA 同步、调度、镜像拉取和应用初始化。参考资料给出的经验范围为 30～90 秒；模型服务可能因权重加载耗时更久。

- 延迟敏感服务将 `minReplicaCount` 设为 1；
- 预拉镜像并使用本地缓存；
- 在事件源可承受的前提下把 `pollingInterval` 调至 10～15 秒；
- 在 readinessProbe 通过后再接流，并为消息配置重试与死信队列；
- 同步 HTTP 缩零必须配置请求缓冲层。

### 认证与密钥

优先使用云 Workload Identity/IRSA 等短期身份，不把静态密钥直接写入 ScaledObject。必须使用 Secret 时，通过 TriggerAuthentication 引用并定期轮换；跨命名空间复用时使用 ClusterTriggerAuthentication，并严格限制 RBAC。

### 指标故障与 fallback

Prometheus 或云 API 不可用时，默认可能无法给 HPA 提供有效指标。KEDA 的 fallback 属于 ScaledObject 能力，不是所谓“Kubernetes v1.36 External Metrics Fallback”：

```yaml
spec:
  fallback:
    failureThreshold: 3
    replicas: 2
    behavior: static
```

应按目标 KEDA 版本核对 fallback 支持的指标类型和行为，并分别告警“事件源无数据”“Scaler 读取失败”“External Metrics API 不可用”。

### 控制器冲突

每个可伸缩目标只保留一个副本控制入口：

```bash
kubectl get hpa -A
kubectl get scaledobject -A
kubectl describe scaledobject <name> -n <namespace>
kubectl describe hpa <name> -n <namespace>
```

若从 KEDA 迁移到原生 HPA，先用影子 Deployment 验证指标、缩零和冷启动，再切流并删除旧 ScaledObject。

### 升级

KEDA 升级可能包含 CRD、RBAC、API 与生成资源行为变化。升级前应：

1. 阅读目标版本 Release Notes 和 Upgrade Notes；
2. 比较 CRD 与 Helm values 差异；
3. 在 staging 重放 ScaledObject、ScaledJob 和认证配置；
4. 验证 `external.metrics.k8s.io`、Scaler 指标与回退策略；
5. 再按集群逐步升级。

不要假设 `helm upgrade` 会自动完成所有跨版本 CRD 迁移，具体步骤以目标版本说明为准。

### Prometheus 告警示例

```yaml
groups:
  - name: autoscaling
    rules:
      - alert: HPAMetricsUnavailable
        expr: kube_hpa_status_condition{condition="AbleToScale",status="false"} == 1
        for: 5m
        labels:
          severity: warning

      - alert: KEDAScalerErrors
        expr: sum(rate(keda_scaler_errors[5m])) by (scaledObject, scaler) > 0
        for: 5m
        labels:
          severity: warning

      - alert: HPANearMaxReplicas
        expr: kube_hpa_status_current_replicas / kube_hpa_spec_max_replicas > 0.8
        for: 10m
        labels:
          severity: warning
```

指标名和 Label 取决于 kube-state-metrics、KEDA 与监控栈版本，部署前先在 Prometheus 中确认实际时序。

## 总结

- HPA 适合 CPU/内存或已有稳定指标适配链路的标准服务；
- Kubernetes 1.37 原生 HPA 已支持基于 Object/External 指标缩到 0；
- KEDA 的核心优势是事件源连接、认证、0↔1 激活、ScaledJob 与故障回退；
- 队列消费者、批处理和模型推理应优先选择能表达业务压力的指标；
- KServe + vLLM 场景中，`running + waiting` 比 CPU/内存更接近请求容量瓶颈；
- 同一 Deployment 只能由一套扩缩容控制链管理。
