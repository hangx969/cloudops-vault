---
title: K8s基础-Pod
tags:
  - kubernetes
  - k8s-basics
aliases:
  - k8sPod
---

# Kubernetes Pod 入门：从容器协作到健康探针与优雅终止

把应用做成镜像之后，我们已经能用容器启动一个进程。但把它交给 Kubernetes 管理，还要回答几个问题：应用要运行在哪台节点上？日志收集容器怎样与业务容器配合？进程启动了，是否就能接收流量？更新版本时，旧实例怎样处理完手里的请求再退出？

这些问题都绕不开 Pod。它是 Kubernetes 创建和管理的最小可部署单元，也是调度、网络共享和应用生命周期管理的基础。理解了 Pod，再看 Deployment 的滚动更新、Service 的流量转发和容器重启，许多分散的配置才会连起来。

本文按应用运行的过程展开：先理解 Pod 与容器的关系，再读懂配置、启动和状态，接着区分三种健康探针，最后讨论退出、发布和排障。文末保留了一次探针配置失当引发级联重启的案例，用来说明这些机制在故障中怎样相互影响。

文中的独立 Pod 清单主要用于演示；持续运行的业务通常由 Deployment、StatefulSet 等工作负载管理，批处理任务则可以使用 Job。示例中的实验镜像、应用接口和网络条件需要自行准备；生产部署应选择经过验证的镜像版本。[^pods]

## 为什么 Kubernetes 需要 Pod

### 一个运行单元，可以包含一个或多个容器

单容器 Pod 是常见的用法。需要多个副本时，通常增加 Pod 数量，而不是把多个相同的业务容器塞进一个 Pod。

多容器 Pod 适合需要紧密协作的进程，例如业务容器与日志收集容器、Web 服务与文件同步容器，或应用与服务网格代理。这些容器作为一个单元调度到同一节点，共享 Pod 的部分运行环境，但不代表它们必须同时启动。[^pods]

这种组织方式也给应用管理提供了统一的边界：Kubernetes 可以综合容器状态和就绪条件判断整个 Pod 能否提供服务。底层运行时则由 kubelet 通过 CRI 对接，例如 containerd；Pod 的使用并不以 Docker 为前提。[^cri]

### 同一个 Pod 内，哪些资源可以共享

理解共享范围，比记住“Pod 里有多个容器”更有用：

- **网络**：容器共享 Pod 的 IP 地址和端口空间，可以用 `localhost:port` 互相访问。同一地址、同一传输协议下的监听端口不能冲突。
- **存储**：Pod 可以声明多个 Volume，容器再通过各自的 `volumeMounts` 选择挂载哪些卷、挂载到哪里。只有挂载同一个卷，才会看到相应的共享文件；容器的整个根文件系统不会自动共享。
- **进程与 IPC**：常见 Linux Pod 可以通过共享的 IPC 环境通信，但 PID 命名空间默认不共享。需要跨容器查看进程时，可显式设置 `spec.shareProcessNamespace: true`。[^process]

Pod 中的容器可以独立退出和重启。容器重启时，Pod 对象通常仍是原来的对象；Pod 被删除或替换后，新 Pod 才拥有新的 UID。即使控制器创建的替代 Pod 沿用了相同名称，也不能把它当作原来的实例。[^lifecycle]

### Pause 容器：为共享运行环境提供基础

在常见的 Linux 容器运行时实现中，创建 Pod sandbox 时会先创建一个基础设施容器，通常称为 pause 或 infra 容器。它维持共享的命名空间环境，应用容器随后加入其中。[^cri]

`kubectl get pods` 中的 `READY 1/1` 通常表示该行统计的一个容器已经就绪，pause 容器不计入其中。pause 也不负责检测业务健康；健康探针由 kubelet 执行，存储共享则依赖 Volume 的声明和挂载。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310252236935.png" alt="image-20231025223642872" style="zoom:50%;" />

### 用两个场景理解容器协作

**文件同步。** 如果应用需要消费 Git 仓库中的文件，可以让一个 sidecar 定期同步仓库，业务容器读取共享卷中的内容。Kubernetes 社区的 git-sync 就提供了这类能力。[^gitsync]

需要区分“文件已更新”和“程序已升级”：同步源码或配置，并不会自动让正在运行的 Go 二进制或 Java 进程加载新代码。是否能直接生效，要看应用的加载方式；应用版本发布仍需相应的构建、替换和重启机制。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310261900543.png" alt="image-20231026190044415" style="zoom:50%;" />

**日志收集。** 假设业务已经把日志写入某个目录，包含 `error.log`、`access.log`、`warning.log`、`info.log`。为了把它们发送到统一的日志服务，可以让业务容器和日志收集容器挂载同一个卷，由后者读取并发送文件。

这样可以把日志采集逻辑从业务代码中分离出来，也便于在遵循同一日志规范的服务之间复用采集配置。业务容器仍需把日志写入约定的共享目录；仅仅把两个容器放进同一个 Pod，并不会让它们自动看到对方的文件。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310261902236.png" alt="image-20231026190227168" style="zoom:50%;" />

## 写一个 Pod：从最小清单理解常用字段

理解了运行边界，就可以把它写进配置。下面的清单描述一个运行 Nginx 的 Pod，可保存为 `pod-demo.yaml`：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-demo
  labels:
    run: pod-demo
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
```

`apiVersion` 和 `kind` 确定资源类型，`metadata` 描述名称和标签，`spec` 描述期望运行的容器。创建后，可以先观察列表，再查看详细状态与事件：

```bash
kubectl apply -f pod-demo.yaml
kubectl get pod pod-demo -o wide
kubectl describe pod pod-demo
```

下面几组字段决定了容器怎样启动，以及 Kubernetes 怎样管理它。

### 端口：声明不会替应用启动监听

`spec.containers[].ports[].containerPort` 描述容器使用的端口，也可通过端口名称供 Service 等配置引用。它不会让应用自动监听这个端口，也不等于把端口映射到了宿主机。实际监听哪个地址和端口，仍由容器中的程序决定。[^api]

例如，程序实际监听 80，把 `containerPort` 改成 81 不会改变程序行为。同一个 Pod 的两个容器如果都要监听同一地址的 TCP 80 端口，也不能靠在 YAML 中填写不同数字来避免冲突。

### 启动命令：区分 command 与 args

`spec.containers[].command` 对应镜像的 `ENTRYPOINT`，`args` 对应 `CMD`。未指定时使用镜像中的默认值；只设置 `args` 时，可以保留镜像入口并替换参数。它们不会自动经过 Shell，使用管道、重定向等语法时，需要显式调用 `/bin/sh -c`。[^command]

这一点也会影响后文的 Tini 示例：如果镜像入口已经用 Tini 包装主进程，在 Pod 中重新指定 `command` 就可能绕过它。

### 资源：requests 参与调度，limits 约束运行

`requests` 是调度器判断节点能否容纳 Pod 的重要依据，并不表示对应内存已经全部被程序占用。因此，节点上运行 `free -m` 看起来还有空闲内存，新 Pod 仍可能因为可分配资源已被其他 Pod 的 requests 占用而处于 Pending。

`limits` 约束容器运行时的资源使用：CPU 超限通常表现为节流，内存压力下则可能触发 OOM 终止。只填写某项资源的 limit、没有填写 request，且准入阶段没有设置默认 request 时，Kubernetes 会把该 limit 复制为 request。排查调度失败时，应检查最终生效的配置。[^resources]

### 环境变量：把 Pod 自身的信息交给应用

普通环境变量用 `value` 指定；Pod 名称、IP、标签等信息可以通过 Downward API 的 `valueFrom.fieldRef` 注入。下面是放在容器配置下的片段：

```yaml
env:
- name: path
  value: test
- name: POD_NAME
  valueFrom:
    fieldRef:
      fieldPath: metadata.name
- name: POD_IP
  valueFrom:
    fieldRef:
      fieldPath: status.podIP
- name: LABEL_APP
  valueFrom:
    fieldRef:
      fieldPath: metadata.labels['run']
```

其中 `LABEL_APP` 读取 `run` 标签。常见的 `fieldRef` 字段包括：

- 标识：`metadata.name`、`metadata.namespace`、`metadata.uid`。
- 标签和注解：`metadata.labels['<KEY>']`、`metadata.annotations['<KEY>']`。
- 调度与身份：`spec.nodeName`、`spec.serviceAccountName`。
- 地址：`status.hostIP`、`status.hostIPs`、`status.podIP`、`status.podIPs`。

这些字段可用作环境变量，但不代表所有字段都能通过 Downward API Volume 暴露，具体支持范围应查官方列表。[^downward]

### 重启策略：决定容器退出之后怎么办

Pod 级别的 `spec.restartPolicy` 有三个常见取值：

| 取值 | 容器退出后的行为 |
| --- | --- |
| `Always` | 无论退出码是否为 0，都重启；这是默认值。 |
| `OnFailure` | 退出码非 0 时重启，正常退出时不重启。 |
| `Never` | 不自动重启已退出的容器。 |

这里讨论的是常规应用容器的 Pod 级策略；原生 sidecar 和较新版本的容器级重启规则还存在单独的配置。Deployment 的 Pod 模板使用 `Always`，Job 则通常按任务需要选择 `OnFailure` 或 `Never`，不能把“始终保持 Always”当作所有工作负载的通用规则。[^lifecycle]

下面的实验让 BusyBox 等待 10 秒后以非零状态退出，便于观察容器重启次数：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: bb-rp
  labels:
    app: busybox
spec:
  containers:
  - name: busybox
    image: busybox:latest
    command: ["/bin/sh"]
    args: ["-c", "sleep 10; exit 1"]
  restartPolicy: Always
```

## Pod 如何启动：调度、初始化与状态

提交清单成功，只表示 Kubernetes 接收了资源定义。镜像是否拉取成功、初始化是否完成、应用能否提供服务，还要继续观察。

### 从 API 请求到节点上的容器

一个普通 Pod 的创建过程可以按下面的顺序理解：

1. 用户通过 `kubectl` 或其他 API 客户端向 API Server 提交 Pod 定义。
2. API Server 完成校验、准入等处理，把对象持久化到 etcd，并返回请求结果。
3. 调度器发现尚未分配节点的 Pod，结合资源与调度约束选择节点，把绑定结果写回 API Server。
4. 目标节点上的 kubelet 发现分配给自己的 Pod，协调网络、存储和容器运行时准备运行环境并启动容器。
5. kubelet 持续上报状态，API Server 保存更新后的对象信息。

组件通过 API Server 的 watch 等机制观察变化，而不是由 API Server 逐条向所有组件下发执行命令。

![image-20231026203326085](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310262033218.png)

把视角切到 Pod 内部，启动主线则是：准备 sandbox 和卷，执行普通 Init Container，再启动应用容器；如果配置了 Startup Probe，等待它成功后才执行 Liveness 和 Readiness。只有满足就绪条件，Pod 才能作为通常意义上的 Service 就绪后端。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310252254552.png" alt="image-20231025225409474" style="zoom:50%;" />

图示适合帮助理解各阶段，但不是所有事件的严格时序图。例如，`PostStart` 与容器入口程序之间没有先后保证，Liveness 与 Readiness 也没有固定的执行顺序。

### Init Container：把必须先完成的工作放在启动之前

普通初始化容器定义在 `spec.initContainers` 中。多个 Init Container 按定义顺序执行，前一个成功结束后才运行下一个；全部成功后，应用容器才开始运行。失败后是重试还是让 Pod 失败，还受重启策略影响。

它适合下载文件、生成初始配置或等待启动前置条件。初始化容器与应用容器可以使用不同镜像，通过显式挂载的共享卷传递结果。在 Deployment、DaemonSet、StatefulSet、Job 等资源中，也是在各自的 Pod 模板内配置它。

普通 Init Container 不支持 `lifecycle`、`livenessProbe`、`readinessProbe`、`startupProbe`，因为它应当执行完成后退出。这里要与使用 `initContainers` 声明、设置容器级 `restartPolicy: Always` 的原生 sidecar 区分。[^init]

下面的示例先下载页面，再由 Nginx 提供访问。下载成功依赖镜像中的工具、DNS 和外部站点连通性：

```yaml
#主容器运行nginx服务，初始化容器用来给主容器生成index.html文件
apiVersion: v1
kind: Pod
metadata:
  name: init-nginx
spec:
  volumes:
  - name: pod-workdir
    emptyDir: {} # Pod 级临时卷，供两个容器共享
  initContainers:
  - name: install
    image: docker.io/library/busybox:1.28
    imagePullPolicy: IfNotPresent
    command:
    - wget
    - "-O"
    - "/work-dir/index.html"
    - "https://www.baidu.com" #把百度主页下下来存到这个目录
    volumeMounts:
    - name: pod-workdir
      mountPath: /work-dir
  containers:
  - name: nginx
    image: nginx:latest
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80
    volumeMounts:
    - name: pod-workdir
      mountPath: /usr/share/nginx/html # 两个容器显式挂载同一个卷，在不同路径看到同一份文件。
```

`emptyDir` 是随 Pod 创建的临时卷，不是把某个指定宿主机目录直接挂入容器。它可以跨容器重启保留数据，但 Pod 从节点移除后，其中的数据会丢失。两个容器分别挂载到 `/work-dir` 和 `/usr/share/nginx/html`，因此访问的是同一份文件。[^volumes]

如果另一个 Pod 定义了两个初始化容器，列表中可能看到这样的输出：

```text
pod-init   0/1     Init:0/2   0          7s
#Init: 0/2，表示两个初始化容器未完成
```

`Init:0/2` 表示两个初始化容器中还没有一个完成，需要继续查看初始化容器的日志和事件，而不是先排查尚未启动的主容器。

### 状态：先区分 Pod phase 与列表中的 STATUS

`kubectl get pods` 的 `STATUS` 列会展示便于排障的信息，它不总是 Pod 的 `status.phase`。例如 `CrashLoopBackOff` 和 `Terminating` 都不属于 Pod phase。[^lifecycle]

Pod phase 只有下面五类：

| Phase | 含义与排查入口 |
| --- | --- |
| `Pending` | 对象已被接收，但一个或多个容器尚未准备好；可能还在等待调度、镜像或运行环境。先看 `describe` 与 Events。 |
| `Running` | Pod 已绑定节点，容器已创建，至少一个容器仍在运行、启动或重启。它不保证应用已经就绪。 |
| `Succeeded` | 所有容器均成功终止，且不会再重启。可查看任务日志确认结果。 |
| `Failed` | 所有容器均已终止，且至少一个以失败结束。结合退出码、日志和 Events 判断原因。 |
| `Unknown` | 无法获取 Pod 状态，通常涉及节点通信等问题。 |

日常排障中还会看到这些状态、原因或展示值：

| 展示值或原因 | 通常说明什么 |
| --- | --- |
| `ContainerCreating` | 容器运行环境仍在准备，可能涉及镜像、网络、卷挂载或配置问题。 |
| `ErrImagePull` / `ImagePullBackOff` | 镜像拉取失败或正在退避重试，检查镜像地址、网络和认证。 |
| `CrashLoopBackOff` | 容器反复退出，kubelet 正在延迟下一次重启；检查启动命令、上一轮日志、退出原因和探针事件。 |
| `OOMKilled` | 容器进程被 OOM 机制终止，检查内存 limit、实际使用、内存泄漏及节点压力。 |
| `Terminating` | Pod 已进入删除流程，检查钩子、宽限期、节点状态及其他删除阻塞原因。 |
| `SysctlForbidden` | 请求的内核参数未获允许或不受支持，检查 sysctl 配置与节点策略。 |
| `Completed` | 常用于展示容器正常完成的终止原因，任务执行结束时可以看到。 |
| `Error` | 容器失败终止时的常见展示值，需要进一步检查具体原因。 |
| `Evicted` | Pod 被驱逐，常见原因包括节点内存、磁盘等资源压力。 |

默认情况下，反复失败的容器重启采用指数退避，例如 10、20、40 秒，最长到 300 秒；持续正常运行一段时间后会重置。较新版本可调整退避行为，因此这些数字应结合节点配置理解。`CrashLoopBackOff` 描述的是“正在等待重试”，真正的故障原因仍要从日志和事件中找。[^lifecycle]

## 健康探针：把启动、就绪与存活分开

到这里，我们已经知道容器能否启动，却还没有回答两个运行期问题：它现在能接流量吗？如果接不了，是应该暂时摘流，还是重启进程？

Kubernetes 用三种可选探针分别表达这些判断。它们配置在容器上，由 kubelet 执行，需要使用者在 YAML 中显式声明。[^probes]

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

这份 Service 与上一份示例都使用 NodePort 31180、31181，两个实验应分别运行；如果需要并存，必须改用未占用的 NodePort，并区分用于选择后端的标签，避免两个 Service 同时选中两组 Pod。

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

### 参数怎样取值：先有预算，再调频率

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

## Pod 如何退出：钩子与宽限期

启动和健康检查解决了“什么时候接流”和“什么时候恢复”，退出则要解决相反的问题：如何停止接收新请求，并尽量处理完正在进行的工作。

### PostStart 与 PreStop 分别在什么时机执行

容器生命周期钩子定义在 `spec.containers[].lifecycle` 下：

- `postStart` 在容器创建后触发，与容器入口程序之间没有先后保证。可以处理不要求先于主程序完成的轻量动作；必须完成后才能启动业务的准备工作，应放进 Init Container。它不接收 Kubernetes 额外传入的事件参数，但处理器自身可以定义命令和参数。
- `preStop` 在 kubelet 发出停止信号前执行，可用于通知下线、触发清理或给流量摘除留出传播时间。它会占用终止宽限期，不能无限阻塞，也不会因为主进程已自行退出而补做清理。

钩子失败可能导致容器被终止，后续行为再由重启策略等机制决定。Kubernetes 没有这里可以替代 `postStart` 的通用 `preStart` 钩子。[^hooks]

下面的示例在 `postStart` 中生成页面，在 `preStop` 中等待 10 秒：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: life-demo
spec:
  containers:
  - name: lifecycle-demo-container
    image: nginx:latest
    imagePullPolicy: IfNotPresent
    lifecycle:
      postStart:
        exec:
          command: ["/bin/sh", "-c","echo 'lifecycle hookshandler' > /usr/share/nginx/html/test.html"]
      preStop:
        exec:
          command: ["/bin/sh", "-c", "sleep 10"] # 为流量摘除的传播留出等待时间
        # 支持 Sleep handler 的集群也可使用以下写法，与 exec 二选一
        # sleep:
          # seconds: 60
```

`preStop` 的等待只是给流量切换留出时间，不会自动让应用处理完请求。镜像中的主进程仍需正确处理停止信号。示例注释中的 Sleep handler 在 Kubernetes 1.30 进入 Beta 并默认启用，1.34 成为稳定功能；旧集群应确认支持情况。[^feature-gates]

### 一次普通删除，会发生哪些事

对于正常运行、没有其他删除阻塞的 Pod，可以这样理解终止过程：

1. 客户端提交删除请求，API Server 给 Pod 记录删除时间和宽限期，列表中通常显示 `Terminating`。
2. kubelet 看到终止请求，开始本地关闭流程；如果容器定义了 `preStop` 且宽限期不为 0，先执行钩子。
3. 钩子完成后，kubelet 请求容器运行时向容器主进程发送停止信号，通常为 `SIGTERM`；镜像或受支持的配置可以指定其他停止信号。应用应停止接收新任务并完成必要清理。
4. 宽限期到期仍未退出的剩余进程，会被运行时强制终止，通常涉及 `SIGKILL`。本地终止完成后，kubelet 推进 API 对象的删除。

与节点关闭过程并行，控制平面也在更新 EndpointSlice：终止中的端点通常标记为 `terminating`，并不再作为常规就绪后端。传播到代理和客户端需要时间，不应假定“端点已更新”和“所有流量都已停止”是同一瞬间。[^endpoints]

普通容器的停止顺序没有统一保证；原生 sidecar 有相应的终止顺序机制。上述行为通过 kubelet 和容器运行时完成，不能统一理解为 Kubernetes 在节点上执行 `docker stop`。[^lifecycle]

### 宽限期包含 preStop，也包含应用自己的退出时间

`spec.terminationGracePeriodSeconds` 默认是 30 秒。如果 `preStop` 在期限结束时仍未完成，kubelet 会请求一次很短的 2 秒扩展；这不是给应用额外保留的一整段正常退出时间。[^lifecycle]

因此，在默认 30 秒宽限期下写一个 90 秒的 `preStop`，不会自动获得 90 秒等待。如果业务确实需要更长时间处理长连接，应设置合适的 `spec.terminationGracePeriodSeconds`，例如 90，并让“钩子耗时 + 应用退出耗时”落在预算内。若钩子本身就等待 90 秒，仅把总宽限期设成 90 秒仍不足以给后续清理留出空间。

删除命令也可以用 `--grace-period=<秒数>` 指定宽限期。强制删除的示例如下：

```bash
# 强制删除pod
kubectl delete pod <pod-name> --force --grace-period=0
```

`--force --grace-period=0` 会绕过正常优雅终止，并使 API 对象立即删除，但不保证节点上的进程已经停止。尤其在节点失联时，不能把“列表里看不到 Pod”当作业务进程已退出的证据。[^lifecycle]

## 生产发布：把流量切换与应用生命周期对齐

单个字段写对，并不等于滚动发布时一定没有中断。需要把新实例启动、接流和旧实例退出放在同一条流程中考虑。

对于启动慢的服务，用 Startup Probe 覆盖初始化阶段；用 Readiness 明确表达什么时候可以接流。没有合适的 Readiness 时，新容器可能在进程刚启动、业务尚未准备好时就被视为就绪，从而增加滚动更新期间的请求失败风险。Liveness 则应根据可识别的内部故障配置，不必为了“配齐三种探针”而添加一个会误杀的检查。

旧实例退出时，应用应处理停止信号、停止接收新工作，并在宽限期内完成存量请求。`preStop` 可以承载必要的下线动作或等待传播，但仅仅 `sleep` 一段时间，不能保证长连接和未完成请求都已结束。多副本、滚动更新策略和负载均衡行为也需要一起验证。

### 如果流量经过 Eureka 或 Nacos，摘流链路也要一起检查

有些 Spring Cloud 应用把 Pod IP 注册到 Eureka、Nacos，调用方直接根据注册表访问实例。这时，请求可能并不经过 Kubernetes Service，不能只检查 Service 后端是否更新。

更新过程中，即使旧 Pod 已经开始退出，注册中心或客户端缓存中的旧地址仍可能继续被使用。可以结合实际框架选择以下做法：

- 在下线前调用注销或状态更新接口，并确认客户端如何刷新地址；这一方案需要应用与调用方配合。
- 先向应用发出下线信号，再通过合适的 `preStop` 等待时间覆盖地址传播，且将整个过程计入终止宽限期。
- 在架构允许时，使用 Kubernetes Service 统一服务发现，并验证 EndpointSlice、代理和调用方连接的更新过程。

Kubernetes 的服务发现不能概括为“替代整个 Spring Cloud”。Spring Cloud 还包括配置管理、熔断、路由等能力，迁移应逐项判断功能与调用路径。[^springcloud]

## 日常调试：让容器运行并找到故障线索

到这里，Pod 从启动到退出的主线已经完整。实际排障时，还需要分清主进程是否存活、应用是否可用，以及日志来自当前实例还是上一轮实例。

### 进入指定容器

多容器 Pod 可以通过 `-c` 选择目标容器：

```bash
kubectl exec -it <pod-name> -c <container-name> -- /bin/bash
```

命令中既要有 Pod 名，也要有容器名。镜像不包含 Bash 时，可以尝试 `/bin/sh`；精简镜像也可能没有 Shell。

### 长时运行：先确认主进程应该做什么

持续运行的业务通常让服务进程在前台运行。任务完成后本来就应该退出的程序，则更适合按任务语义选择 Job 等资源，不需要为了保持 Pod 的 Running 状态再加一个无限等待进程。

在临时调试场景中，下面两种写法可以让容器保持运行，方便进入环境检查。

**使用 `tail` 等待。**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: tail-pod
spec:
  containers:
  - name: nginx
    image: nginx:latest
    command: ["tail", "-f", "/dev/null"]
```

它会持续等待，并不提供业务服务。尤其要注意，这里覆盖了 Nginx 镜像的默认入口，因此并没有启动 Nginx。

**使用 `sleep` 暂停。**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sleep-pod
spec:
  containers:
  - name: alpine
    image: alpine:latest
    command: ["sleep", "infinity"]
```

`sleep infinity` 通常开销很低，但仍需镜像中的 `sleep` 实现支持该参数。这同样只适合需要保留调试环境等场景。

### Tini 解决 PID 1 问题，不负责业务自动拉起

Tini 是轻量级容器 init，主要处理信号转发和僵尸子进程回收。它启动的主子进程退出后，Tini 也会退出，并沿用子进程的退出码；它不是让业务永久运行、失败后自动拉起的进程监督器。[^tini]

下面的镜像包装方式示意如何让 Tini 作为入口。`your-main-process` 是占位名称，实际构建还要把应用及其依赖放进镜像，并选择与目标平台匹配的 Tini 二进制：

```dockerfile
FROM ubuntu:latest
ADD https://github.com/krallin/tini/releases/download/v0.19.0/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]
CMD ["your-main-process"]
```

构建命令与 Dockerfile 分开执行：

```bash
docker build -t your-image-with-tini .
```

Pod 可以通过 `args` 传入要运行的程序，保留镜像里的 Tini `ENTRYPOINT`：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: tini-pod
spec:
  containers:
  - name: my-container
    image: your-image-with-tini
    args: ["your-main-process"] # 保留镜像中的 Tini ENTRYPOINT
```

### 看日志时，先确定是哪个容器、哪一轮运行

`kubectl logs` 默认读取容器标准输出、标准错误对应的日志。多容器 Pod 应明确选择容器，反复退出的容器则可以用 `--previous` 读取上一次已终止实例的日志。默认情况下，kubelet 保留一个已终止容器及其日志，不代表能够回看任意多轮历史；需要长期留存时，应依赖集中日志系统。[^logging]

```bash
kubectl logs <pod-name>
# 读取指定容器上一次已终止实例的日志
kubectl logs --previous <pod-name>

# 查看 Pod 内所有应用容器的日志
kubectl logs mypod --all-containers=true
# 查看指定容器的日志
kubectl logs mypod -c container-name

# 查看当前命名空间中的事件
kubectl get events
kubectl get events --field-selector involvedObject.name=podName
```

遇到问题，可以先沿着“Events → 容器状态与退出原因 → 当前及上一轮日志 → 实际生效配置”排查。下面的案例就需要把探针失败与重启前的依赖延迟放在一起，才能看清因果关系。

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

正文涉及的 Kubernetes 机制以官方文档为依据；案例中的事故数字与时间线沿用原文记述。下面列出核对入口，便于按主题继续阅读。

[^pods]: [Kubernetes：Pods](https://kubernetes.io/docs/concepts/workloads/pods/)。
[^process]: [Kubernetes：共享进程命名空间](https://kubernetes.io/docs/tasks/configure-pod-container/share-process-namespace/)。
[^cri]: [containerd：CRI 插件架构](https://github.com/containerd/containerd/blob/main/docs/cri/architecture.md)。
[^gitsync]: [Kubernetes git-sync 项目说明](https://github.com/kubernetes/git-sync)。
[^api]: [Kubernetes Core API 类型定义](https://github.com/kubernetes/api/blob/master/core/v1/types.go)。
[^command]: [Kubernetes：定义容器命令与参数](https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/)。
[^resources]: [Kubernetes：Pod 与容器的资源管理](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)。
[^downward]: [Kubernetes：Downward API](https://kubernetes.io/docs/concepts/workloads/pods/downward-api/)。
[^lifecycle]: [Kubernetes：Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)；[中文版](https://kubernetes.io/zh-cn/docs/concepts/workloads/pods/pod-lifecycle/)。
[^init]: [Kubernetes：Init Containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)。
[^volumes]: [Kubernetes：Volumes / emptyDir](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir)。
[^probes]: [Kubernetes：三种健康探针及参数](https://kubernetes.io/docs/concepts/workloads/pods/probes/)。
[^probe-config]: [Kubernetes：配置 Liveness、Readiness 与 Startup Probe](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)。
[^endpoints]: [Kubernetes：EndpointSlice conditions](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/#conditions)。
[^hooks]: [Kubernetes：容器生命周期钩子](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)。
[^feature-gates]: [Kubernetes：Feature Gates，PodLifecycleSleepAction](https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/)。
[^springboot]: [Spring Boot：Kubernetes Probes 与外部依赖检查](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html#actuator.endpoints.kubernetes-probes)。
[^springcloud]: [Spring Cloud：功能与项目说明](https://spring.io/projects/spring-cloud/)。
[^tini]: [Tini：使用方式与退出行为](https://github.com/krallin/tini)。
[^logging]: [Kubernetes：日志架构](https://kubernetes.io/docs/concepts/cluster-administration/logging/)。
[^prometheus]: [Prometheus：histogram_quantile](https://prometheus.io/docs/prometheus/latest/querying/functions/#histogram_quantile)。
[^pdb]: [Kubernetes：Disruptions 与 PDB](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)。
[^hpa]: [Kubernetes：Horizontal Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)。

补充阅读：[Kubernetes 详细教程：容器探测](https://gitee.com/hangxu969/golang/blob/main/k8s详细教程/Kubernetes详细教程.md#534-容器探测)。
