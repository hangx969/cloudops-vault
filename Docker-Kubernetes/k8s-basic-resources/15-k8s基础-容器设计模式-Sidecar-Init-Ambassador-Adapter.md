---
title: "K8s 四种容器设计模式"
source:
  - "https://mp.weixin.qq.com/s/LP79kNx9QRdTH44F5s46Kw"
  - "https://mp.weixin.qq.com/s/CHZjuW2hv1b-IaEXM0tM2A"
  - "https://mp.weixin.qq.com/s/35uKYCFWbnyqp9AaH7EyZA"
  - "https://mp.weixin.qq.com/s/MaNQDfrLlcZNaWffSQYF0Q"
created: 2026-06-28
tags:
  - kubernetes
  - container-design-patterns
  - pod
  - sidecar
---

# K8s 四种容器设计模式

<div id="k8s-容器设计模式sidecar-init-container-ambassador-adapter" class="legacy-anchor"></div>
<div id="k8s-容器设计模式" class="legacy-anchor"></div>

一个 Web 服务除了处理请求，可能还需要准备配置、转发日志、连接数据库、输出监控指标。将这些任务放进同一个镜像，会让依赖和发布节奏互相牵制；拆成多个独立 Pod，又要处理额外的网络与数据共享。

Pod 允许多个容器共享网络命名空间，并按需挂载同一组卷。本文围绕这种协作方式，介绍 Sidecar、Init Container、Ambassador 和 Adapter。先看容器何时启动、通过什么交换数据，再看配置示例。示例中的业务镜像与外部服务需要自行准备，这些镜像用于说明配置结构，上线前应选择仍受支持的版本并固定标签或摘要。

## 什么是容器设计模式？

容器设计模式（Container Design Patterns）是一套在 Kubernetes 这样的容器编排平台中合理组合、管理多个容器，以满足复杂应用需求的方法论。这里的“模式”描述职责和协作关系，不全是 Kubernetes API 中独立的容器类型。Ambassador 和 Adapter 通常也是辅助容器；普通 init container 则有明确的启动顺序。

## 为什么需要容器设计模式？

单个容器通常围绕一个主要服务进程组织（它仍可以派生子进程），但实际应用场景往往需要多个进程协作，比如日志收集、数据预处理、服务代理等。如果把所有功能都塞进一个容器，会导致：

- 维护困难：功能耦合，难以独立更新
- 升级复杂：牵一发而动全身
- 耦合度高：组件间依赖关系复杂
- 资源浪费：无法精确控制资源分配

容器设计模式帮助我们将这些功能拆分到不同的容器中，并通过 Pod 这种机制让它们协作。


## 一、Sidecar 模式（边车模式）

### 在同一个 Pod 中补充日志、代理等能力

主容器负责核心业务，辅助容器负责日志、代理或配置同步。两者在同一个 Pod 中运行，可以通过 `localhost` 通信；文件共享需要显式挂载同一个卷，各容器镜像内的根文件系统不会自动共享。

![Sidecar：业务与日志采集分工](https://raw.githubusercontent.com/hangx969/upload-images-md/main/k8s-basic-resources/2026-10-25/k8s-15-01-sidecar-logging-pattern-02dcaa9d5a82.png)

### 日志与配置同步等常见用途

- 日志收集和转发：Fluentd 等日志代理作为 Sidecar 采集主容器日志
- 配置文件同步：从配置中心拉取最新配置并写入共享卷
- 服务网格代理：Istio Envoy 作为 Sidecar 代理服务间流量
- 监控数据收集：Prometheus exporter 采集业务指标

### 实战配置：Web 应用 + 日志收集

![日志 Sidecar：共享日志与独立配置](https://raw.githubusercontent.com/hangx969/upload-images-md/main/k8s-basic-resources/2026-10-25/k8s-15-02-sidecar-nginx-fluentd-dccd4360e7a3.png)


```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-app-with-logging
spec:
  containers:
  # 主容器：Web 应用
  - name: web-app
    image: nginx:1.20
    ports:
    - containerPort: 80
    volumeMounts:
    - name: log-volume
      mountPath: /var/log/nginx

  # Sidecar 容器：日志收集
  - name: log-collector
    image: fluentd:v1.14
    volumeMounts:
    - name: log-volume
      mountPath: /var/log/nginx
    - name: fluentd-config
      mountPath: /fluentd/etc

  volumes:
  - name: log-volume
    emptyDir: {}
  - name: fluentd-config
    configMap:
      name: fluentd-config
```

主容器和辅助容器通过 `emptyDir` 共享日志目录；该卷随 Pod 消失，不适合承担日志持久化。下面补齐 `fluentd-config`，演示把 Nginx access log 送到 Fluentd 标准输出；生产中需要配置实际日志后端、缓冲和轮转策略。

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/nginx/access.log
      pos_file /tmp/nginx-access.pos
      tag nginx.access
      read_from_head true
      <parse>
        @type nginx
      </parse>
    </source>
    <match nginx.access>
      @type stdout
    </match>
```

### 普通辅助容器与原生 Sidecar 的生命周期

上例把两个容器都写在 `containers` 中，它们没有确定的启动先后顺序，也没有专门的反向终止保证。日志代理要能等待日志文件出现，应用也不能假定代理已就绪。

Kubernetes 的[原生 Sidecar](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/) 在 1.28 以 alpha 引入、1.29 默认启用，并在 1.33 稳定。它写在 `initContainers` 中，配置容器级 `restartPolicy: Always`，启动后持续运行。kubelet 在确认该容器已启动后继续后续初始化；若依赖实际服务就绪，应使用合适的 `startupProbe`。

```yaml
# Pod spec 片段：将日志容器移至这里，原 containers 中保留 web-app
initContainers:
- name: log-collector
  image: fluentd:v1.14
  restartPolicy: Always
  volumeMounts:
  - name: log-volume
    mountPath: /var/log/nginx
  - name: fluentd-config
    mountPath: /fluentd/etc
```

原生 Sidecar 可独立重启；Pod 终止时，kubelet 在应用容器停止后按相反顺序终止这些 Sidecar。Job 的主任务完成也不会被这种 Sidecar 永久阻塞。它仍使用 Pod 的终止宽限期，不能保证日志一定来得及全部发送。


## 二、Init Container 模式（初始化容器模式）

### 先完成初始化，再启动应用

普通 Init Container 在应用容器启动前执行准备任务，必须成功结束后才能继续下一个初始化步骤。它退出后不再消耗运行时 CPU，但调度时仍会计入有效资源需求；不能把高配 Init Container 理解为调度结束后自动归还全部 Pod 资源预算。具体计算见官方[初始化容器资源说明](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/#resource-sharing-within-containers)。

![Init Container：初始化完成后启动应用](https://raw.githubusercontent.com/hangx969/upload-images-md/main/k8s-basic-resources/2026-10-25/k8s-15-03-init-container-sequence-f5a04ac35491.png)

### 初始化任务需要能重复执行

- 环境准备与依赖检查：验证外部服务可用性、检查网络连接
- 数据库迁移：执行数据库 schema 更新、数据初始化。多副本可能并发执行，迁移必须支持幂等和锁；复杂迁移更适合独立 Job 或发布流程。
- 配置文件生成：动态生成应用配置文件、密钥注入
- 权限与安全设置：设置文件权限、挂载密钥、安全扫描

初始化逻辑可以使用独立镜像和依赖，不必打进业务镜像。多个普通 Init Container 串行执行，前一步失败时应用不会启动，排障也能区分准备阶段与业务阶段。容器失败可能重试，所以创建目录、写配置和数据初始化等操作都应能够重复执行。

### 实战配置：应用初始化

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-init
spec:
  # 初始化容器
  initContainers:
  - name: init-setup
    image: busybox:1.35
    command: ['sh', '-c']
    args:
    - |
      echo "初始化应用环境..."
      mkdir -p /shared
      echo "app.env=production" > /shared/app.properties
      echo "初始化完成"
    volumeMounts:
    - name: shared-data
      mountPath: /shared

  # 主容器
  containers:
  - name: main-app
    image: openjdk:11-jre
    command: ['java', '-jar', '/app/app.jar']
    volumeMounts:
    - name: shared-data
      mountPath: /app/config

  volumes:
  - name: shared-data
    emptyDir: {}
```

这个例子展示配置写入与挂载关系：初始化容器写入 `/shared/app.properties`，主容器会在 `/app/config/app.properties` 看到它。`openjdk:11-jre` 本身不包含 `/app/app.jar`，需要替换成打包了该 JAR 的业务镜像。

另一种用法是在 Init Container 中从 Git 拉取静态文件到共享卷，再由 Nginx 提供服务。应固定提交版本，避免同一部署的不同副本因“拉取最新代码”而运行不同内容。


## 三、Ambassador 模式（大使模式）

### 通过 localhost 代理外部连接

Ambassador 为主应用提供本地网络入口，把远端地址、连接策略和认证配置放到代理容器中。应用只需连接本地端口，代理再访问外部系统。

![Ambassador：通过本地代理访问外部系统](https://raw.githubusercontent.com/hangx969/upload-images-md/main/k8s-basic-resources/2026-10-25/k8s-15-04-ambassador-outbound-proxy-31a95f0e5dbe.png)

### 数据库与外部 API 的代理用途

- 数据库连接代理：统一管理数据库连接、连接池和故障转移
- 服务发现与负载均衡：动态发现后端服务并实现负载均衡
- 网络安全与认证：集中处理 TLS 加密、身份验证和授权
- API 网关功能：作为 API 网关，处理路由、限流和监控

### 实战配置：数据库代理

![Ambassador：数据库代理的职责与选择](https://raw.githubusercontent.com/hangx969/upload-images-md/main/k8s-basic-resources/2026-10-25/k8s-15-05-ambassador-database-concept-ea6128697fb8.png)

Deployment：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-with-db-proxy
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web-service
  template:
    metadata:
      labels:
        app: web-service
    spec:
      containers:
      # 主应用容器
      - name: web-service
        image: myapp:latest
        ports:
        - containerPort: 8080
        env:
        - name: DB_HOST
          value: "localhost"    # 通过 Ambassador 访问
        - name: DB_PORT
          value: "5432"

      # Ambassador 数据库代理容器
      - name: db-proxy
        image: haproxy:2.4
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: haproxy-config
          mountPath: /usr/local/etc/haproxy
        command: ["haproxy", "-db", "-f", "/usr/local/etc/haproxy/haproxy.cfg"]

      volumes:
      - name: haproxy-config
        configMap:
          name: haproxy-config
```

HAProxy ConfigMap：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: haproxy-config
data:
  haproxy.cfg: |
    global
        daemon
    defaults
        mode tcp
        timeout connect 5000ms
        timeout client 50000ms
        timeout server 50000ms

    frontend db_frontend
        bind *:5432
        default_backend db_servers

    backend db_servers
        balance roundrobin
        server db1 postgres-primary.default.svc.cluster.local:5432 check
        server db2 postgres-replica.default.svc.cluster.local:5432 check backup
```

主容器通过 `localhost:5432` 访问 HAProxy，再由它连接数据库。`-db` 强制前台运行，避免配置中的 `daemon` 使容器主进程退出。此处 `check` 仅检测 TCP 连通性，`backup` 只是主后端不可达时的备用目标：它不会提升 PostgreSQL 副本为主库，也不提供数据库连接池。写流量必须接到角色正确的可写端点；实际主从切换应由数据库高可用系统完成，连接池可另用 PgBouncer 等组件。


## 四、Adapter 模式（适配器模式）

### 在应用输出与采集系统之间转换格式

Adapter 读取主应用输出，并转换成外部系统可以接受的格式或协议。遗留应用无法直接修改时，这种方式允许在保持其接口的前提下接入新的监控或日志系统。

### 指标、日志与协议的转换用途

- 日志格式标准化：将不同格式的日志统一转换为标准格式（如 JSON）
- 监控指标转换：将各种监控指标转换为统一的数据格式（如 Prometheus 格式）
- 协议转换：实现不同协议间的转换，如 HTTP 到 gRPC
- 数据格式适配：调整数据格式以满足不同系统的需求
![Adapter：把应用输出转换为监控格式](https://raw.githubusercontent.com/hangx969/upload-images-md/main/k8s-basic-resources/2026-10-25/k8s-15-06-adapter-metrics-pattern-117853ea532e.png)

### 实战配置：遗留系统监控数据转 Prometheus

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legacy-app-with-adapter
spec:
  replicas: 1
  selector:
    matchLabels:
      app: legacy-service
  template:
    metadata:
      labels:
        app: legacy-service
    spec:
      containers:
      # 主应用容器（遗留系统）
      - name: legacy-app
        image: legacy-service:1.0
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: metrics-volume
          mountPath: /var/metrics

      # Adapter 监控适配器容器
      - name: metrics-adapter
        image: python:3.12-alpine
        ports:
        - containerPort: 9100
        volumeMounts:
        - name: metrics-volume
          mountPath: /host/metrics
        - name: adapter-script
          mountPath: /scripts
        command: ["python", "/scripts/convert_metrics.py"]
        env:
        - name: LEGACY_METRICS_PATH
          value: "/host/metrics"
        - name: PROMETHEUS_PORT
          value: "9100"

      volumes:
      - name: metrics-volume
        emptyDir: {}
      - name: adapter-script
        configMap:
          name: metrics-adapter-script
          defaultMode: 0755
```

主容器将原始指标写入共享卷，Adapter 读取并转换后，在 Pod 的 9100 端口暴露 `/metrics`。这里使用 Python 解释器运行自定义转换程序；node-exporter 镜像不会自动理解遗留业务格式，也不能假定其中存在 shell 或转换脚本。若选用 node-exporter 的 textfile collector，还需另一个程序生成合法的 `.prom` 文件。

下面补齐脚本 ConfigMap。约定遗留应用以原子替换方式写入 `/var/metrics/requests_total.txt`，内容为一行 `requests_total=123`；转换器据此输出一个 counter。实际格式不同，需要修改解析器。

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: metrics-adapter-script
data:
  convert_metrics.py: |
    import os
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from pathlib import Path

    source = Path(os.environ["LEGACY_METRICS_PATH"]) / "requests_total.txt"

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/metrics":
                self.send_error(404)
                return
            try:
                key, raw = source.read_text().strip().split("=", 1)
                if key != "requests_total":
                    raise ValueError("unexpected metric")
                value = int(raw)
                if value < 0:
                    raise ValueError("negative counter")
                body = ("# HELP legacy_requests_total Requests processed by the legacy app.\n"
                        "# TYPE legacy_requests_total counter\n"
                        f"legacy_requests_total {value}\n").encode()
            except (OSError, ValueError):
                self.send_error(503, "source metrics unavailable")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    HTTPServer(("0.0.0.0", int(os.environ["PROMETHEUS_PORT"])), Handler).serve_forever()
```

这个最小实现没有认证、TLS 或并发优化，适合解释数据转换路径。还需为采集端配置 Service 或 Pod 发现规则；只声明 `containerPort` 不会让 Prometheus 自动采集。业务镜像 `legacy-service:1.0` 也需要自行提供。


## 四种模式对比

| 维度 | Sidecar | Init Container | Ambassador | Adapter |
|------|---------|----------------|------------|---------|
| 运行时机 | 在 Pod 运行期间持续辅助；启动语义取决于声明方式 | 主容器启动前运行 | 在主容器运行期间提供代理 | 在主容器运行期间转换数据 |
| 生命周期 | 与 Pod 关联，可独立重启 | 执行完毕后退出 | 通常与 Pod 关联 | 通常与 Pod 关联 |
| 核心职责 | 辅助增强 | 环境初始化 | 外部通信代理 | 数据/协议转换 |
| 数据流方向 | 主→Sidecar（采集） | Init→共享卷→主 | 主→Ambassador→外部 | 主→Adapter→外部系统 |
| 典型代表 | Istio Envoy、Fluentd | DB migration、Git pull | HAProxy、Cloud SQL Proxy | Prometheus exporter |
| 与 Sidecar 的区别 | 通用辅助模式 | 运行时机不同 | 专注出站代理 | 专注格式转换 |

### 从启动顺序和数据路径选择

先判断任务是否只需要在启动前完成。准备配置、检查依赖等一次性任务适合普通 Init Container；需要在应用运行期间持续工作的日志或代理进程，适合辅助容器，并根据集群版本选择普通声明或原生 Sidecar。

持续运行的辅助容器还可以按职责细分：主应用通过它访问外部系统时属于 Ambassador；它把应用的输出转换成另一种格式时属于 Adapter。这两种模式通常都是 Sidecar 的具体用途，不必把名称当作互斥的 Kubernetes 资源类型。最终应能说明每个容器何时就绪、如何交换数据，以及故障和终止时其他容器如何应对。
