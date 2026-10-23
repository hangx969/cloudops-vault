---
title: Kubernetes 健康探针：从配置原理到重启风暴排查
tags:
  - kubernetes
  - k8s-basics
  - kubernetes/probes
date: 2026-10-23
aliases:
  - k8s健康探针
  - Kubernetes健康检查
---

# Kubernetes 健康探针：从配置原理到重启风暴排查

一个 Pod 已经进入 `Running`，应用却可能还在预热缓存；进程仍然存活，也可能已经卡住，无法继续处理请求。面对这些状态，仅检查“容器有没有运行”还不足以决定是否接收流量、是否需要重启。

Kubernetes 的健康探针让应用通过命令、端口或健康接口表达自身状态，再由节点上的 kubelet 执行检查并采取相应动作。检查内容和失败后的处置需要一起设计：把临时的依赖故障写进错误的探针，可能让一次短暂抖动变成更多容器的重启。[^probes]

本文先分清启动、就绪与存活检查的职责，再读懂参数和配置示例，随后讨论发布与恢复边界，最后用一个重启风暴案例检查这些设计为什么会失效。Pod 的容器协作、生命周期与基本操作，可参阅 [[Docker-Kubernetes/k8s-basic-resources/k8s基础-pod|Pod 入门文章]]。

文中的独立 Pod、Service 清单用于演示机制，实验镜像和应用接口需要自行准备；业务由 Deployment 等工作负载管理时，探针配置写在相应的 Pod 模板中。事故数字与时间线按案例来源保留，不作为本文的实测结果。

## 健康探针在检查什么

Kubernetes 提供三种可选探针。它们配置在容器上，由 kubelet 执行，需要使用者在 YAML 中显式声明。探针失败通常影响同一个 Pod 内的目标容器，并不意味着自动删除整个 Pod 或重新调度到其他节点。[^probes]

### 先决定要回答的问题，再选择探测方法

| 探针 | 回答的问题 | 达到失败阈值后的主要动作 |
| --- | --- | --- |
| `startupProbe` | 本轮容器启动是否已经完成？ | 终止该容器，再按重启策略处理。 |
| `readinessProbe` | 当前是否适合接收业务流量？ | 标记未就绪，使 Pod 不再作为通常的 Service 就绪后端；不重启容器。 |
| `livenessProbe` | 是否出现需要重启才能恢复的内部故障？ | 终止该容器，再按重启策略处理。 |

配置了 Startup Probe 时，它成功前，Liveness 和 Readiness 都不会执行；成功后，本轮启动不再执行 Startup Probe。Liveness 与 Readiness 随后各自工作，不能理解为“Readiness 失败后，Liveness 才运行”。未配置的探针按默认成功处理，这不代表 kubelet 已经检查过业务接口。[^probes]

探针类型决定“怎样处置”，探测方法决定“怎样判断”。四种常用方法如下：

- `exec`：在容器内执行命令，退出码为 0 表示成功。所需命令必须存在于镜像中。
- `tcpSocket`：由 kubelet 尝试连接目标端口，连接建立即成功；它不能证明业务逻辑可用。
- `httpGet`：通常向 Pod IP 的指定端口和路径发送 HTTP GET，状态码 200 至 399 表示成功。
- `grpc`：应用实现 gRPC Health Checking Protocol，返回 `SERVING` 表示成功。

每个探针选择一种探测方法。HTTP 或 gRPC 能表达多细的健康语义，取决于应用怎样实现接口；不能仅凭端口能连通，就断言服务已经可以处理请求。[^probe-config]

## 读懂参数：给启动和故障恢复分配时间

先把字段含义分清，再讨论参数“调大还是调小”：

| 字段 | 默认值 | 作用 |
| --- | --- | --- |
| `initialDelaySeconds` | 0 秒 | 开始探测前的初始延迟。配置 Startup Probe 后，Liveness、Readiness 的延迟在 Startup 成功后才开始计算。 |
| `periodSeconds` | 10 秒 | 探测周期，最小为 1 秒。Pod 未就绪时，Readiness 可能额外执行，以便更快恢复就绪。 |
| `timeoutSeconds` | 1 秒 | 单次探测的超时时间，最小为 1 秒。 |
| `failureThreshold` | 3 | 连续失败多少次后判定失败，最小为 1。 |
| `successThreshold` | 1 | 失败后需要连续成功多少次才恢复成功；Startup 和 Liveness 必须为 1。 |

可以用 `failureThreshold × periodSeconds` 估算一组配置的容忍量级。例如 Startup 每 5 秒探测、允许连续失败 30 次，可提供约 150 秒的启动预算。但它不是从任意故障发生时刻起精确倒计时的保证，还要考虑初始延迟、探测相位、请求耗时和退出过程。[^probes]

实际调参时，可以按应用特点分别考虑：

- **Startup**：覆盖初始化耗时的合理上界。5 秒周期、30 次失败阈值是一个演示组合；若单次健康请求通常在 1 至 5 秒内完成，可以据此评估超时预算，而不是默认所有应用都适合这个范围。
- **Liveness**：给可恢复抖动留出空间。轻量应用 5 至 10 秒、重型应用 30 至 60 秒的周期，可以作为讨论起点，但周期和失败阈值仍应由正常延迟、故障恢复时间及检测目标决定，不能统一采用“失败两次就重启”。未配置 Startup 时，还需给启动留出足够延迟；配置了 Startup，也要检查运行期初始延迟是否合适。
- **Readiness**：根据摘流速度与抖动容忍要求设置。`successThreshold: 1` 可以较快恢复接流；需要防止反复抖动时，也可以评估增加连续成功次数的影响。

周期太短会增加节点和应用负担，阈值过严可能误杀；周期太长又可能让故障实例继续接流。HTTP 通常能比单纯 TCP 连通提供更多业务信息，例如 Java 应用端口仍在监听、内部却已卡死的情况，但前提是接口确实覆盖了目标故障。没有合适接口时可以选择 TCP，同时接受它只能检查连通性的边界。

## 配置示例：从单项探针到组合使用

示例依次展示启动、接流和重启的判断。这个阅读顺序不代表三类探针在运行时按此顺序执行；Startup 成功后，Readiness 与 Liveness 各自工作。

### Startup Probe：给慢启动应用留出时间

如果应用仍在初始化，Liveness 却已经开始判断失败，容器就可能尚未启动完成便被终止，反复进入重启循环。单纯增大 Liveness 的 `initialDelaySeconds` 可以避开部分问题，但固定等待值很难适应启动耗时的变化，也会延后这一阶段的故障检测。

Startup Probe 为启动阶段设置单独的容忍窗口。只要在窗口内成功，就可以进入运行期探测，不必等满整个窗口；连续失败达到阈值后，才终止容器。

**Exec 示例。** 下面检查 Tomcat 进程是否存在，镜像需要包含 `ps`、`grep`，并根据实际进程调整匹配方式。`[t]omcat` 写法可避免仅匹配到 `grep` 命令自身；进程存在仍不等于应用已经完成业务初始化。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: startupprobe
spec:
  containers:
  - name: startup
    image: tomcat-8.5-jre8:v1
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 8080
    startupProbe:
      exec:
        command:
        - "/bin/sh"
        - "-c"
        - "ps aux | grep '[t]omcat'"
      initialDelaySeconds: 20 #容器启动后多久开始探测
      periodSeconds: 20 #执行探测的时间间隔
      timeoutSeconds: 10 #探针执行检测请求后，等待响应的超时时间
      successThreshold: 1 #成功多少次才算成功
      failureThreshold: 3 #失败多少次才算失败
```

**TCP 示例。** 如果应用的启动完成条件确实可以用“开始监听端口”表达，可以在容器配置下使用：

```yaml
startupProbe:
  tcpSocket:
    port: 8080
  initialDelaySeconds: 10 #容器启动后多久开始探测
  periodSeconds: 5 #执行探测的时间间隔
  timeoutSeconds: 2 #探针执行检测请求后，等待响应的超时时间
  successThreshold: 1 #成功多少次才算成功
  failureThreshold: 30 #失败多少次才算失败
```

**HTTP 示例。** 如果应用能提供反映初始化结果的接口，可以使用 HTTP：

```yaml
startupProbe:
  httpGet:
    path: /health # 检查路径
    port: 8080
    scheme: HTTP
    # httpHeaders: # 可选，请求头。可以传入一个token做一个简单认证。
    # - name: end-user
      # value: Jason
    # 默认请求 Pod IP:8080，而不是节点的 localhost:8080
  initialDelaySeconds: 20 # 容器启动后多久开始探测。
  periodSeconds: 20 #执行探测的时间间隔
  timeoutSeconds: 10 #探针执行检测请求后，等待响应的超时时间
  successThreshold: 1 # 探测成功多少次才算成功
  failureThreshold: 3 # 探测失败多少次才算失败
```

### Readiness Probe：进程还活着，也可能暂时不能接请求

应用可能正在预热缓存、等待关键依赖，或因负载过高而暂时无法接收新请求。Readiness 失败时，容器继续运行，Pod 的就绪状态则发生变化。

对于常规 Service 流量，控制平面会相应更新后端就绪信息。现代 Kubernetes 通常通过 EndpointSlice 表达这些状态；“摘流”不一定意味着立即删除整个端点记录，也不代表网络层禁止任何客户端直接访问 Pod IP。`publishNotReadyAddresses` 等配置还会改变相关行为。[^endpoints]

下面的示例通过 8081 端口探测 Spring Boot 的健康接口，并声明一个 NodePort Service：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: springboot
  labels:
    app: springboot
spec:
  containers:
  - name: springboot
    image: docker.io/mydlqclub/springboot-helloworld:0.0.1
    imagePullPolicy: IfNotPresent
    ports:
    - name: server
      containerPort: 8080
    - name: management
      containerPort: 8081
    readinessProbe:
      initialDelaySeconds: 20
      periodSeconds: 5
      timeoutSeconds: 10
      httpGet:
        scheme: HTTP
        port: 8081
        path: /actuator/health
---
apiVersion: v1
kind: Service
metadata:
  name: springboot
  labels:
    app: springboot
spec:
  selector:
    app: springboot
  type: NodePort
  ports:
  - name: server
    port: 8080
    targetPort: 8080
    nodePort: 31180
  - name: management
    port: 8081
    targetPort: 8081
    nodePort: 31181
```

探测成功后，Pod 才能成为通常的就绪后端；探测失败则停止通过这条常规 Service 路径接收新流量，等待后续恢复。接口也应按“是否能处理请求”设计，而不是简单复用一个包含所有依赖的总健康状态。

### Liveness Probe：只对重启有帮助的故障采取动作

Liveness 适合识别主循环卡死、不可恢复的死锁等进程内部故障。外部数据库暂时不可用，通常不应直接判定本进程需要重启；重启并不能修好数据库，还可能加重连接和流量压力。

连续失败达到阈值后，kubelet 终止对应容器，再根据重启策略处理。它通常不会因此删除 Pod 对象、重新调度整个 Pod。[^probes]

**Exec 示例。** 容器先创建 `/tmp/healthy`，30 秒后删除它；探针用 `cat` 检查文件是否存在。前 30 秒命令成功，文件删除后命令失败，连续失败达到默认阈值后触发后续动作。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness-exec
  labels:
    app: liveness
spec:
  containers:
  - name: liveness
    image: busybox:1.28
    imagePullPolicy: IfNotPresent
    args:                       #创建测试探针探测的文件
    - /bin/sh
    - -c
    - touch /tmp/healthy; sleep 30; rm -rf /tmp/healthy; sleep 600
    livenessProbe:
      initialDelaySeconds: 10   #延迟检测时间
      periodSeconds: 5          #检测时间间隔
      exec:
        command:
        - cat
        - /tmp/healthy
```

**HTTP 示例。** 下面的 Spring Boot 应用在 8081 端口提供 Actuator 健康接口，通过 HTTP 返回码判断探测结果：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness-http
  labels:
    test: liveness
spec:
  containers:
  - name: liveness
    image: docker.io/mydlqclub/springboot-helloworld:0.0.1 #ctr -n=k8s.io images import springboot.tar.gz解压
    imagePullPolicy: IfNotPresent
    livenessProbe:
      initialDelaySeconds: 20   #延迟加载时间
      periodSeconds: 5          #重试时间间隔
      timeoutSeconds: 10        #超时时间设置
      httpGet:
        scheme: HTTP
        port: 8081
        path: /actuator/health
```

该例使用 `/actuator/health` 演示语法。生产环境应先检查该接口包含哪些检查项，避免把数据库等共享依赖的故障引入 Liveness。支持相应功能的 Spring Boot 版本可以分别使用 `/actuator/health/liveness` 和 `/actuator/health/readiness`。[^springboot]

**TCP 示例。** 下面只检查 Nginx 的 80 端口能否建立连接：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness-tcp
  labels:
    app: liveness-tcp
spec:
  containers:
  - name: liveness
    image: nginx:latest
    imagePullPolicy: IfNotPresent
    livenessProbe:
      initialDelaySeconds: 15
      periodSeconds: 20
      tcpSocket:
        port: 80
#探测80端口起来没起来
#停掉nginx
#kubectl exec -it liveness-tcp -- /bin/bash
# nginx -s stop 会停止主进程；此后的重启也可能由 restartPolicy 直接触发。
```

示例中的 `nginx -s stop` 会停止主进程，容器随后可能直接按 `restartPolicy` 重启，因此不能仅凭“重启了”就证明 Liveness 生效。要验证探针，应结合 Events 中的探针失败记录与容器终止原因。

### 三种探针一起配置时，各自仍需有明确职责

下面的完整示例展示三种探针可以怎样放在同一个容器配置中。为便于对照，它们都请求同一个 Actuator 路径；这只演示配置位置，不是生产端点设计模板。后文案例会给出分离 `/startup`、`/live`、`/ready` 的写法。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: springboot-live
  labels:
    app: springboot
spec:
  containers:
  - name: springboot
    image: docker.io/mydlqclub/springboot-helloworld:0.0.1
    imagePullPolicy: IfNotPresent
    ports:
    - name: server
      containerPort: 8080
    - name: management
      containerPort: 8081
    readinessProbe:
      initialDelaySeconds: 20
      periodSeconds: 5
      timeoutSeconds: 10
      httpGet:
        scheme: HTTP
        port: 8081
        path: /actuator/health
    livenessProbe:
      initialDelaySeconds: 20
      periodSeconds: 5
      timeoutSeconds: 10
      httpGet:
        scheme: HTTP
        port: 8081
        path: /actuator/health
    startupProbe:
      initialDelaySeconds: 20
      periodSeconds: 5
      timeoutSeconds: 2
      httpGet:
        scheme: HTTP
        port: 8081
        path: /actuator/health
---
apiVersion: v1
kind: Service
metadata:
  name: springboot-live
  labels:
    app: springboot
spec:
  selector:
    app: springboot
  type: NodePort
  ports:
  - name: server
    port: 8080
    targetPort: 8080
    nodePort: 31180
  - name: management
    port: 8081
    targetPort: 8081
    nodePort: 31181
```

这份 Service 与前面的 Readiness 示例都使用 NodePort 31180、31181，两个实验应分别运行；如果需要并存，必须改用未占用的 NodePort，并区分用于选择后端的标签，避免两个 Service 同时选中两组 Pod。

还要确认管理端口能否代表业务端口的实际状态。单独的管理 HTTP 服务正常，并不一定说明业务 HTTP 服务也能接收请求。[^springboot]

### gRPC：应用需要实现健康检查协议

原生 gRPC 探针在 Kubernetes 1.24 进入 Beta，在 1.27 成为稳定功能。下面以 etcd 为例，演示 `grpc.port` 的配置位置：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: etcd-with-grpc
spec:
  containers:
  - name: etcd
    image: registry.cn-hangzhou.aliyuncs.com/google_containers/etcd:3.5.1-0
    command: [ "/usr/local/bin/etcd", "--data-dir", "/var/lib/etcd", "--listen-client-urls", "http://0.0.0.0:2379", "--advertise-client-urls", "http://127.0.0.1:2379", "--log-level", "debug"]
    ports:
    - containerPort: 2379
    livenessProbe:
      grpc:
        port: 2379 # 目标端口需要实现 gRPC 健康检查协议。
      initialDelaySeconds: 10
```

目标必须实现 gRPC 健康检查协议，不能把任意开放的 gRPC 端口都当作健康接口。这里使用数字端口；实际镜像、协议支持和集群版本需要对应。[^probe-config]

## 让探针参与发布与故障恢复

单个字段写对，并不等于滚动发布时一定没有中断。新实例的启动和接流、旧实例的流量摘除和退出，需要一起考虑。

对于启动慢的服务，用 Startup Probe 覆盖初始化阶段；用 Readiness 明确表达什么时候可以接流。没有合适的 Readiness 时，新容器可能在进程刚启动、业务尚未准备好时就被视为就绪，从而增加滚动更新期间的请求失败风险。Liveness 则应根据可识别的内部故障配置，不必为了“配齐三种探针”而添加一个会误杀的检查。

旧实例退出时，应用仍要处理停止信号，并在宽限期内完成存量工作。探针不代替 `preStop`、终止宽限期和应用自身的优雅关闭逻辑；这些机制见 [[Docker-Kubernetes/k8s-basic-resources/k8s基础-pod#Pod 如何退出：钩子与宽限期|Pod 的终止过程]]。同时还要验证多副本、滚动更新策略与实际负载均衡路径，不能仅凭探针通过就承诺发布没有中断。

### 自定义高频检查，不能直接替代 kubelet 探针

原生 `periodSeconds` 最小为 1 秒。如果有更细粒度的观测需求，可以编写应用监控逻辑。下面的 sidecar 轮询脚本可以说明自定义检查与 Kubernetes 探针的区别：

```bash
#!/bin/bash
while true; do
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)
  if [ "$response" != "200" ]; then
    echo "Tomcat is not healthy. Exiting..."
    exit 1
  fi

  sleep 0.001  # 两轮请求之间暂停 1 ms；实际周期还包含 curl 请求耗时
done
```

这段脚本每轮请求后暂停 1 毫秒，实际周期还包含 HTTP 请求耗时，并不保证每毫秒执行一次。如此密集的请求也会增加负载，应先评估是否必要。

更关键的是，脚本 `exit 1` 退出的是它所在的 sidecar，并不会把结果自动变成业务容器的 Readiness 或 Liveness，也不会自动重启业务容器。要把自定义观测接入流量控制或恢复动作，还需要另外设计应用或控制逻辑。

## 探针失效真实案例

> [!info] 案例来源
> 本案例整理自《一场由健康探针引发的Pod重启风暴——K8s LivenessReadiness Probe配置不当的深度复盘》，事故数字与时间线沿用该文记述。下面结合前文的探针语义，分析其配置、修复思路与 PDB、HPA 的保护边界。

### 事故概况

一次旨在“更快发现不健康 Pod”的 Liveness Probe 参数调整，在数据库慢查询和连接池争用期间放大了瞬时抖动。订单服务的健康接口从约 50 ms 增长到 3.2 秒，刚好超过 3 秒超时阈值。按案例记述，Liveness 在约 10 秒量级的窗口内连续失败两次，开始重启 Pod 内的业务容器，剩余副本承担更多流量，进一步压垮数据库连接池，最终形成级联重启。

事故期间：

- 订单服务的 40 个 Pod 中，可用副本快速下降到约 6 个；
- 支付服务的 20 个 Pod 中，可用副本下降到约 3 个；
- 300 多个 Pod 中的容器在约 5 分钟内发生连锁重启；
- 上游订单服务故障继续通过 RPC 超时传播到支付服务；
- 核心业务最终出现大面积 502 和不可用。

### 触发事故的配置变化

变更前：

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

变更后：

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

这组参数意味着：

- 探针每 5 秒执行一次；
- 一次请求超过 3 秒即记为失败；
- 连续失败 2 次便触发容器重启；
- 按探测周期与失败阈值相乘估算，容忍量级约为 10 秒。

这里的 10 秒是量级估算，不是从首次失败结果起固定等待 10 秒；实际动作时间还受探测相位、超时和终止过程影响。

更严重的是，`/healthz` 不只是检查进程是否存活，还同步检查数据库、Redis 和消息队列。外部依赖的瞬时抖动因此被错误解释为“进程已经无法恢复，必须重启”。

### 故障时间线

| 时间 | 事件 |
|---|---|
| 15:12 | 慢查询触发，订单服务数据库连接池开始紧张 |
| 15:13 | /healthz 响应达到 3.2 秒，第一次超过 3 秒超时 |
| 15:13 | 5 秒后第二次超时，Liveness 判定失败 |
| 15:13 | kubelet 开始重启订单服务 Pod 内的容器 |
| 15:14 | 多个 Pod 内的业务容器被终止，剩余可用 Pod 承担更多流量 |
| 15:14 | 剩余 Pod 的连接池进一步过载，健康检查普遍超时 |
| 15:15 | 订单服务 Pod 大量进入 CrashLoopBackOff |
| 15:16 | 支付服务因依赖订单服务而发生 RPC 超时，其健康检查也开始失败 |
| 15:17 | 支付服务 Pod 内的容器被连续重启 |
| 15:18 | 核心业务大面积不可用 |

故障形成了正反馈：

```text
数据库短暂抖动
  → Liveness 超时
  → Pod 内的容器被重启
  → 剩余 Pod 流量和连接压力上升
  → 更多健康检查超时
  → 更多 Pod 内的容器被重启
```

### 为什么 Readiness 没有阻止重启风暴

当时的 Readiness 配置为：

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 3
  successThreshold: 1
```

Readiness 的周期为 10 秒、失败阈值为 3，容忍量级约为 30 秒；Liveness 的对应量级却只有约 10 秒。两组数字都不是精确计时，但说明原配置倾向于更早触发重启动作，而没有给摘流后的恢复留出足够空间。按案例的故障过程，结果是：

1. Liveness 先达到失败阈值，触发终止容器；
2. 业务容器还没来得及通过摘流获得恢复窗口，就被 kubelet 重启；
3. 新容器启动后再次承受流量和依赖压力；
4. 健康检查再次超时，进入循环。

对于这类希望先摘流、再等待自愈的服务，Readiness 通常应比 Liveness 更敏感，Liveness 则应更保守。这是配置目标，不是 Kubernetes 保证的探针执行顺序。

### 三个根因

#### Liveness 检查了外部依赖

Liveness 连续失败达到阈值后，会终止容器并按策略处理，因此应检测重启能够修复的进程内部故障，例如主循环卡死或不可恢复的死锁。

数据库、缓存、消息队列和下游 RPC 的失败通常不应直接导致 Liveness 失败。重启应用不会修复外部依赖，反而可能制造连接风暴和流量转移。

| 探针 | 要回答的问题 | 失败结果 | 推荐检查内容 |
|---|---|---|---|
| Startup | 应用是否已完成启动 | 超过启动容忍期后重启 | 初始化、迁移、缓存预热等启动条件 |
| Liveness | 进程是否已无法自愈 | 重启容器 | 进程内部状态，不依赖外部系统 |
| Readiness | 当前是否能安全接收请求 | 从 Service 后端摘除 | 处理请求所需的关键依赖和容量 |

#### Readiness 比 Liveness 更慢

原配置没有为“先摘流、后恢复，必要时再重启”提供足够的时间差。修复时需要同时调整检查内容与参数，不能只把某一个超时值调大。

修复后的示例：

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
  successThreshold: 1

livenessProbe:
  httpGet:
    path: /live
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 20
  timeoutSeconds: 5
  failureThreshold: 5
```

按相同的量级估算法，Readiness 的失败窗口约为 10 秒，Liveness 约为 100 秒，给应用自愈和外部依赖恢复留下更大空间。实际摘流与重启时间仍需通过故障演练验证。

> [!warning] 不要机械套用倍数
> “Liveness 容忍窗口至少是 Readiness 的两倍”可以作为保守启发式，但不是 Kubernetes 的通用公式。参数应根据应用启动时间、正常延迟分布、依赖恢复时间、错误预算和可接受故障发现时间，通过压测与故障演练确定。

#### 慢启动应用没有 Startup Probe

只靠 `initialDelaySeconds` 很难同时兼顾慢启动与运行期故障发现。Startup Probe 成功之前，Liveness 和 Readiness 不会开始执行，可把启动阶段与运行阶段分离。

```yaml
startupProbe:
  httpGet:
    path: /startup
    port: 8080
  periodSeconds: 5
  failureThreshold: 30

livenessProbe:
  httpGet:
    path: /live
    port: 8080
  periodSeconds: 20
  timeoutSeconds: 5
  failureThreshold: 5

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

这里为启动阶段提供约 150 秒的探测预算。一旦 Startup 成功，运行期探针才接管。

### 健康检查端点设计

建议把三个端点按语义拆开。下面是处理函数示意，`dbPool`、`cache` 等需要替换为应用中的实际实现：

```go
// /startup：检查初始化工作是否完成
func startupHandler(w http.ResponseWriter, r *http.Request) {
    if !dbPool.IsInitialized() || !cache.IsWarmed() {
        w.WriteHeader(http.StatusServiceUnavailable)
        return
    }
    w.WriteHeader(http.StatusOK)
}

// /live：极轻量，只证明进程仍能响应
func liveHandler(w http.ResponseWriter, r *http.Request) {
    // 不检查数据库、缓存、消息队列等外部依赖
    w.WriteHeader(http.StatusOK)
}

// /ready：检查当前是否可以接收业务流量
func readyHandler(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), time.Second)
    defer cancel()

    if err := dbPool.Ping(ctx); err != nil {
        w.WriteHeader(http.StatusServiceUnavailable)
        return
    }
    w.WriteHeader(http.StatusOK)
}
```

设计原则：

- /live 不因外部依赖失败而返回非 200。外部系统抖动通常不能通过重启当前容器修复。
- /ready 可以检查关键依赖，但必须有严格超时。多个依赖最好分别设置超时，避免一个依赖拖住整个端点。
- 健康端点本身不能成为瓶颈。避免复杂计算、长链路调用和大量 I/O。
- 谨慎决定 Readiness 是否检查共享依赖。如果数据库整体故障导致所有 Pod 同时 NotReady，Service 可能失去全部后端；需要结合降级能力、故障模式和流量策略设计。
- 探针路径应有明确语义。使用 /startup、/live、/ready 比笼统的 /healthz 更容易避免职责混淆。

### 监控与诊断

应监控探针成功率、延迟、容器重启和可用副本变化。下面使用自定义指标的示意名称：第一条统计成功事件的每秒速率，第二条假定延迟使用 classic Histogram，计算最近 5 分钟的 P99。成功事件速率不是成功率；成功率还需要对应的总探测次数。实际指标名、标签和类型必须按采集系统核对，不能当作 kubelet 默认指标。[^prometheus]

```promql
# 成功事件的每秒速率，假设该指标是自定义 Counter
rate(probe_success_total{probe="liveness"}[5m])

# 延迟 P99，假设该指标是 classic Histogram
histogram_quantile(
  0.99,
  sum by (le) (
    rate(probe_duration_seconds_bucket{probe="liveness"}[5m])
  )
)
```

现场排查至少包括：

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name> --previous
kubectl get events --field-selector involvedObject.name=<pod-name>
kubectl get pod <pod-name> -o yaml
```

重点确认：

- Last State 和容器退出原因；
- Events 中是否出现 Liveness probe failed；
- Restart Count 的增长速度；
- 探针实际超时、失败阈值与周期；
- 依赖延迟是否在重启前已经升高；
- 可用副本下降是否导致剩余 Pod 负载增加。

### 事故后的工程治理

- 建立 Probe 配置标准，生产探针变更必须经过 Code Review。
- 在 CI/CD 中检查高风险配置，例如 Liveness 引用外部依赖、过短容忍窗口、缺少 Startup Probe。
- 为 Pod 重启率、探针失败率和可用副本骤降设置告警。
- 探针参数变更先灰度到少量副本，并观察完整故障窗口。
- 定期进行依赖变慢、连接池耗尽和探针超时的故障演练。
- 结合滚动更新策略、拓扑分布、反亲和性和足够副本数降低同时失效风险。

> [!danger] PDB 与 HPA 的保护边界
> PodDisruptionBudget 主要约束自愿中断，例如节点排空；它不能阻止 kubelet 因 Liveness 失败而重启容器，也不能直接阻止应用自身崩溃。HPA 的 `minReplicas` 只约束期望副本下限，不能保证这些副本在探针误杀期间保持 Ready。二者可以增强整体可用性，但不能代替正确的探针语义、参数和故障隔离。PDB 的约束主要通过 Eviction API 生效，直接删除 Pod 也可能绕过它。[^pdb][^hpa]

### 复盘结论

- 瞬时依赖故障不等于进程死亡。
- 只有“重启能够修复”的故障才适合由 Liveness 处理。
- 对适合摘流后自愈的服务，应为 Readiness 留出先行动作的窗口，Liveness 谨慎触发重启。
- 慢启动应用应使用 Startup Probe 隔离启动阶段。
- 探针参数不是越敏感越好，必须根据真实延迟和恢复时间验证。
- 批量修改核心服务探针属于高风险变更，应灰度发布并准备快速回滚。

## 参考文档

探针类型、参数和运行机制参考 Kubernetes 官方文档；Spring Boot 的端点设计参考项目官方说明。事故数字与时间线沿用案例来源的记述。

[^probes]: [Kubernetes：三种健康探针及参数](https://kubernetes.io/docs/concepts/workloads/pods/probes/)。
[^probe-config]: [Kubernetes：配置 Liveness、Readiness 与 Startup Probe](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)。
[^endpoints]: [Kubernetes：EndpointSlice conditions](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/#conditions)。
[^springboot]: [Spring Boot：Kubernetes Probes 与外部依赖检查](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html#actuator.endpoints.kubernetes-probes)。
[^prometheus]: [Prometheus：histogram_quantile](https://prometheus.io/docs/prometheus/latest/querying/functions/#histogram_quantile)。
[^pdb]: [Kubernetes：Disruptions 与 PDB](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)。
[^hpa]: [Kubernetes：Horizontal Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)。

补充阅读：[Kubernetes 详细教程：容器探测](https://gitee.com/hangxu969/golang/blob/main/k8s详细教程/Kubernetes详细教程.md#534-容器探测)。
