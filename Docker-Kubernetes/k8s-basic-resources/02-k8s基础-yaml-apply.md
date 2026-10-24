---
title: K8s基础-YAML
tags:
  - kubernetes
  - k8s-basics
aliases:
  - k8sYAML
---

# 从 YAML 到 kubectl apply：读懂清单，也读懂字段由谁管理

第一次接触 Kubernetes 时，一份 Pod YAML 就能启动应用。等到同一个 Deployment 同时经过 kubectl、Helm、GitOps 和自动扩缩容器管理，问题会变成：清单里的值为什么被覆盖，明明只改了镜像，副本数为什么又变了？

要理解这些现象，需要先读懂 YAML 的层级与 Kubernetes 字段，再看 `apply` 如何把清单合入现有对象。本文从基本语法开始，逐步解释 Client-side Apply（CSA）和 Server-side Apply（SSA）。查询及实验命令需要已经配置好的 kubeconfig；涉及修改的例子应先在独立实验命名空间运行。

## YAML 的层级如何变成对象

YAML 是数据序列化格式。Kubernetes 将 YAML 解码为符合 API schema 的对象，因此“YAML 能解析”与“API 接受这份配置”是两道检查。

缩进使用空格，不能用 Tab；通常每层缩进两个空格。同一层级的字段需要对齐，键名后用 `: ` 分隔值，`#` 表示注释。一个文件可以放多份 YAML 文档，用 `---` 分隔，它表示文档边界，并非另一个磁盘文件。

### 单值、数组与映射

纯量是单个值，例如字符串、布尔值、数字与空值：

```yaml
c1: true
c2: null
```

日期可以用 ISO 8601 风格表示，但 Kubernetes 最终按字段 schema 校验类型。如果目标字段是字符串，建议加引号，尤其是标签、环境变量，以及容易被解释为数字、布尔或日期的值。

数组由多项组成，使用短横线表示每一项：

```yaml
address:
- Beijing
- Shenzhen
```

映射是键值对，可以继续嵌套：

```yaml
heima:
  age: 15
  address: Beijing
```

`labels` 也是映射，但 Kubernetes 要求标签键和值为字符串：

```yaml
labels:
  key1: value1
  key2: value2
```

### 对象列表：以 containers 为例

`kubectl explain pod.spec.containers` 中的 `<[]Object>` 表示“对象组成的数组”。每个容器是一项，每项又含有名称、镜像等字段，`ports` 则是其中嵌套的另一个对象列表。下面是 Pod `spec` 下的片段，使用第三方教学镜像；实验前应确认镜像可访问且符合环境要求：

```yaml
containers:
- name: tomcat-java
  image: xianchao/tomcat-8.5-jre8:v1
  imagePullPolicy: IfNotPresent
  ports:
  - containerPort: 8080
```

普通 Pod 至少需要一个常规容器；Pod 创建后，并非所有模板字段都允许直接修改。实际管理应用时，通常修改 Deployment 等控制器的 Pod 模板，再由控制器创建新 Pod。

## 认识一份 Pod 清单

先用下面的命令查看集群支持的资源和字段：

```sh
kubectl api-versions
kubectl api-resources
kubectl explain pod
kubectl explain pod.spec.containers
```

### 顶层字段分别做什么

| 字段 | 作用 |
| --- | --- |
| `apiVersion` | 资源所在 API 组与版本，例如 Pod 使用 `v1`，Deployment 使用 `apps/v1` |
| `kind` | 对象类型，大小写必须符合 API 定义，例如 `Pod` |
| `metadata` | 对象身份与附加信息，常见字段有 `name`、`namespace`、`labels`、`annotations` |
| `spec` | 希望资源达到的状态，例如使用哪个镜像、多少副本、如何挂载卷 |
| `status` | 组件观察并报告的状态，普通声明式清单通常不手工填写 |

Labels 适合选择和分组对象；Annotations 保存附加信息，例如构建时间、release ID、镜像摘要、日志平台入口、调试工具版本和维护团队信息。两者中的内容都可能被具备读取权限的人看到，不要把密码或敏感联系信息随意放进去。

### 容器启动参数与环境变量

![image-20231026205427484](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310262054540.png)

`command` 对应覆盖镜像的 `ENTRYPOINT`，`args` 对应覆盖镜像的 `CMD`。两者都是数组，Kubernetes 不会自动把字符串交给 shell 解释。若需要循环、管道或 shell 风格的变量展开，要显式调用 `/bin/sh -c` 等 shell。Kubernetes 本身还支持在 command/args 中用 `$(VAR_NAME)` 引用已定义的容器环境变量，这不需要额外启动 shell。对应关系见[官方命令与参数说明](https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/)。

| 清单中的配置 | 使用的命令与参数 |
| --- | --- |
| 两者都不设置 | 镜像的 ENTRYPOINT 与 CMD |
| 只设置 `command` | 使用新的 command；镜像中默认的命令与参数被覆盖 |
| 只设置 `args` | 保留镜像 ENTRYPOINT，使用新的 args |
| 两者都设置 | 使用新的 command 与 args |

BusyBox 提供一组命令工具，具体容器能运行多久取决于启动命令。若进程立即退出，容器也会结束；需要长期运行的实验可以显式设置循环或 `sleep`，不要把这种等待写成实际业务服务的健康保证。进入运行中的容器时，现代 kubectl 使用 `--` 分隔参数：

```sh
kubectl exec -n dev -it pod-command -c busybox -- /bin/sh
```

`env` 适合传入环境变量，普通配置可以引用 ConfigMap，敏感值可以引用 Secret。使用环境变量或挂载文件应按应用读取方式决定，不必一律改成文件；但应用是否会自动感知配置更新，需要单独确认。

### 镜像、端口与资源

镜像拉取策略有三种，准确拼写与含义见[镜像拉取策略](https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy)：

| `imagePullPolicy` | 含义 |
| --- | --- |
| `Always` | 启动时向仓库解析镜像引用；若对应摘要的镜像层已在本地，可复用缓存，并非每次下载全部镜像 |
| `IfNotPresent` | 本地已有镜像时使用缓存，否则拉取 |
| `Never` | 只使用本地镜像，缺失时启动失败 |

`containerPort` 描述容器预期使用的端口，不会替应用启动监听，也不会自动对外开放 Service。集群内可在网络策略允许时访问 `PodIP:实际监听端口`。`hostPort` 会占用节点上的指定端口，多个 Pod 若争用相同节点、协议和地址上的同一端口，就会限制调度，因此通常通过 Service 暴露应用。

`resources.requests` 是调度时使用的资源请求，调度器据此与节点可分配资源比较；它不是“应用先用到这个数值才允许启动”。`limits` 约束运行中的资源使用，CPU 超限通常受到节流，内存超限可能触发 OOM kill；是否重启还取决于重启策略。更详细的边界见[资源管理说明](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)。

`nodeSelector` 则用键值映射要求节点具备相应标签。节点不匹配、可分配资源不足或其他调度条件不满足，都会使 Pod 留在 Pending。

![image-20240725224115645](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202407252241732.png)

### 先生成骨架，再检查清单

kubectl 可以在客户端生成一个 Deployment 骨架，而不创建资源：

```sh
kubectl create deployment nginx -n nginx --image=nginx:1.27 --dry-run=client -o yaml > nginx.yaml
```

镜像版本这里只用于演示字段，实际应选择仍受维护、经过验证的版本。`--dry-run=client` 适合生成骨架，不能证明目标集群支持全部字段，也不能确认镜像可拉取。需要集群端校验时，可使用 `kubectl apply --dry-run=server -f nginx.yaml`；服务端 dry-run 会访问集群并执行相应校验，但不持久化对象。

## Client-side Apply 如何合并现有资源

普通 `kubectl apply -f deployment.yaml` 使用客户端 apply。对已经存在的 Deployment，可以通过详细日志观察请求过程：

```sh
kubectl apply -f deployment.yaml -v=8 2>&1 | grep -E "PATCH|POST|GET|Content-Type"
```

这条命令会实际 apply；只想观察校验过程时应增加 `--dry-run=server`。详细日志也可能包含对象内容和集群地址，分享前需检查。一次典型请求序列可以简化为：

```text
GET /openapi/v3
GET /openapi/v3/apis/apps/v1
GET /apis/apps/v1/namespaces/default/deployments/my-app
PATCH /apis/apps/v1/namespaces/default/deployments/my-app?fieldManager=kubectl-client-side-apply
  Content-Type: application/strategic-merge-patch+json
```

实际请求会受到发现缓存、客户端版本和资源是否存在影响。对内置 Deployment，kubectl 读取当前对象，在本地计算补丁后提交；对象不存在时通常发创建请求。自定义资源不支持 strategic merge patch，不能把上面的 Content-Type 推广到所有资源。

### 三路合并比较哪三份数据

CSA 使用上次提交、当前状态和本次提交：

| 数据 | 从哪里来 | 用来判断什么 |
| --- | --- | --- |
| last-applied | `kubectl.kubernetes.io/last-applied-configuration` 注解 | 上一次通过该流程声明了哪些字段 |
| live state | API server 返回的当前对象 | 集群当前实际保存的值 |
| 新 manifest | 本次提交的清单 | 本次想维持或修改的值，以及相对上次删除的字段 |

补丁的合并语义还与字段类型有关。例如容器列表通常按 `name` 匹配，`tolerations` 则作为整体处理。可以查询 OpenAPI schema：

```sh
kubectl get --raw /openapi/v3/apis/apps/v1 | jq   '.components.schemas["io.k8s.api.core.v1.PodSpec"].properties.containers'
```

其中可能看到两类标记：

```text
"x-kubernetes-list-map-keys": ["name"],
"x-kubernetes-list-type": "map",
"x-kubernetes-patch-merge-key": "name",
"x-kubernetes-patch-strategy": "merge"
```

`x-kubernetes-patch-*` 描述 strategic merge patch 的列表合并规则；`x-kubernetes-list-*` 描述 SSA 使用的列表拓扑。两者有关联，但不能当作同一个机制。atomic 列表常见的拓扑标记是：

```text
"x-kubernetes-list-type": "atomic"
```

### 为什么副本数可能被改回去

假设清单与 last-applied 都声明 `replicas: 3`，随后 HPA 把当前副本改成 5。HPA 不会同步更新 kubectl 的 last-applied 注解。下面可以在实验 Deployment 上模拟对 scale 子资源的修改：

```sh
kubectl patch deployment my-app --subresource='scale' --type='merge' -p '{"spec":{"replicas":5}}'
kubectl get deployment my-app -o yaml
```

再次用仍写着 `replicas: 3` 的清单执行 CSA，可能把当前值重新设为 3，过程不会给出 SSA 式的字段所有权冲突。last-applied 与本次清单相同，并不意味着 live state 中的不同值会自动获得保留。

因此，HPA 接管副本数后，发布配置需要明确交接该字段；移除字段也要考虑默认值和迁移时序，不能在生产中直接删掉就认为没有风险。Helm、GitOps、Operator 与手动命令共同修改资源时，也要对每个字段确定管理来源。

## Server-side Apply 如何追踪字段所有权

SSA 在 Kubernetes 1.22 达到稳定。显式增加 `--server-side` 后，客户端把声明交给 API server，由服务端做结构化合并并记录字段管理者。完整规则见[Server-Side Apply 官方说明](https://kubernetes.io/docs/reference/using-api/server-side-apply/)。

```sh
kubectl apply --server-side -f deployment.yaml -v=8 2>&1 | grep -E "PATCH|POST|GET|Content-Type"
```

核心写入请求的形式是：

```text
PATCH /apis/apps/v1/namespaces/default/deployments/my-app?fieldManager=kubectl
  Content-Type: application/apply-patch+yaml
```

SSA 通过 apply PATCH 实现创建或更新，不需要为了计算三路补丁先读取 live state；客户端仍可能进行 API 发现、校验或迁移相关请求，因此不能把“整个命令一定没有 GET”当成判断依据。

### managedFields 记录什么

服务端把字段管理信息放在 `metadata.managedFields` 中。kubectl 的 SSA 默认 manager 是 `kubectl`，也可用 `--field-manager` 指定稳定的工作流名称。其他工具使用什么 manager，取决于其版本与实现，应查看实际对象，不要只按工具名称猜测。

```sh
kubectl get deployment my-app -o yaml --show-managed-fields
```

字段记录中的 `operation: Apply` 表示 SSA，`operation: Update` 表示其他创建、更新或非 apply patch 操作。看到 Update 不能直接断定某个工具使用了哪一种客户端补丁算法，还需要结合 `manager`、具体字段和工具配置判断。

当 SSA 想把其他 manager 管理的字段改成不同值时，会出现冲突。如果多个 manager 声明相同值，可以共享所有权。处理冲突通常有三种选择：移除自己不该管理的字段、把值调整为与现状一致，或在明确交接后使用 `--force-conflicts` 接管。强制接管会覆盖值并转移所有权，不能作为所有冲突的默认处理。

SSA 也不能拦住所有外部修改。普通 Update 或非 apply PATCH 仍可改变字段，并调整管理记录。它提供的是 apply 工作流之间可检查的协作规则，仍需要配置和团队约定配合。

## CRD 的列表如何合并

自定义资源同样可以使用 SSA，其合并粒度取决于 CRD 的结构化 schema。没有指定列表拓扑时，列表通常按 atomic 处理，也就是整张列表作为一个管理单元。现代 `apiextensions.k8s.io/v1` CRD 要求结构化 schema，因此“没有列表拓扑标记”与“完全没有 schema”需要区分。

CRD 作者可以用 `x-kubernetes-list-type: map` 加上 `x-kubernetes-list-map-keys` 指定按键合并，也可以用 `set` 表达集合。以 condition 列表为例，按 `type` 匹配可以让不同控制器管理各自条目，但前提是 CRD 实际声明了这样的结构。

```sh
kubectl get crd <crd-name> -o yaml | grep -A 3 "x-kubernetes-list"
```

这个命令便于快速查找，输出为空只说明没有查到该字符串；对指定字段的行为仍应检查其完整 schema。使用 Kubebuilder 生成 CRD 时，也要正确声明 marker 并检查生成结果，框架不会自动猜出每个业务列表的语义。

## Helm 4 的 SSA 迁移

Helm 4 的新安装默认使用 SSA；升级与回滚的 `--server-side` 默认值是 `auto`，沿用上一 release 的 apply 方式，因此从 Helm 3 升级已有 release 时，不会仅因为换了二进制就自动迁移。行为可对照[Helm SSA 设计](https://docs.helm.sh/community/hips/hip-0023/)和[helm upgrade 参数](https://docs.helm.sh/docs/helm/helm_upgrade/)。

若已经检查字段归属并决定迁移，可以显式指定：

```sh
# 需要 Helm 4；若本机二进制名为 helm4，请相应替换
helm upgrade my-app my-chart --server-side=true
```

随后检查对应对象的 `managedFields`，结合 Helm 的 manager 与 `operation: Apply` 确认相关字段的操作方式。不要因为对象中某个其他 manager 出现 Apply 就认为 Helm 已经完成迁移。

迁移时，历史客户端更新可能对默认字段留下管理记录，其他工具也可能已经管理部分字段。是否冲突取决于真实所有权与本次声明，不能断言一定冲突，或认为默认字段一定没有冲突。先在测试环境检查 dry-run 与真实升级结果，再安排生产迁移。

还要注意版本混用与 release 历史：旧 Helm 再次执行更新或回滚可能采用客户端更新方式，不能假定后续操作始终保持 SSA。Helm 的 release 记录仍用于历史与回滚；默认 Secret 存储后端中的 release Secret 不能因为“不再依靠它计算对象 diff”而删除。

当多个工具共享对象时，可以从一个具体字段开始检查：它现在是什么值，由哪个 manager 管理，下一次发布是否还会声明这个值。明确管理边界，再选择迁移或交接，比单独增加一个 apply 参数更能解释后续行为。
