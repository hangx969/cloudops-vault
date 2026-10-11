---
title: K8s基础-YAML
tags:
  - kubernetes
  - k8s-basics
aliases:
  - k8sYAML
---

# K8s基础-YAML


## yaml文件

### 语法格式

YAML:标记语言

- --- 表示新的YAML文件的开始,声明两段配置放到一个文件里也用 --- 分隔
- 以空格为缩进,表示层级关系。(不能使用Tab)开头缩进两个空格
- : 后面要加一个空格
- \# 表示注释

### 数据类型

1. 纯量:单个值

```yaml
c1: True
c2: ~
```

- 日期类型:ISO 8601格式

2. 数组

```yaml
address:
- Beijing
- Shenzhen
```

3. 对象:一系列属性

```yaml
heima:
 age: 15
 address: Beijing
```

4. 对象列表

   containers  **`<[]Object>`** -required-
   List of containers belonging to the pod. Containers cannot currently be added or removed. There must be at least one container in a Pod. Cannot be updated.

   - 下级是一个一个的对象,以横线 - 开头,对齐containers。

   ```yaml
   containers:
   - name: tomcat-java
     image: xianchao/tomcat-8.5-jre8:v1
     imagePullPolicy: IfNotPresent
     ports: #ports也是对象列表
     - containerPort: 8080  #容器暴露的端口
   ```

5. map - 键值对

   ```yaml
   labels:
    key1: value1
    key2: value2
   ```

## POD yaml文件

> kubectl explain pod 查看pod的yaml文件写法。

### 一级属性

- apiVersion:k8s内部定义,用kubectl api-versions 查询
- kind:资源类型,查看:kubectl api-resources
- Metadata `<object>`:元数据,描述这个资源,常用的是name,namespace,labels,annotation等。
  - 用Annotation来记录的信息包括:build信息、release信息、Docker镜像信息等,例如时间戳、release id号、镜像hash值、docker registry地址等;日志库、监控库、分析库等资源库的地址信息;程序调试工具信息,例如工具名称、版本号等;团队的联系信息,例如电话号码、负责人名称、网址等。

- Spec `<object>`: specification,描述,是对各种资源配置的详细描述
- Status `<object>`: 内容无需定义,k8s自动生成

### spec子属性

- Containers 数组:容器的详细信息

  ![image-20231026205427484](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310262054540.png)

- imagePullPolicy:
  - Always:总是从远程仓库下载。
  - IfNotExist:本地有就用本地,否则远程仓库下载。
  - Never:只用本地镜像,本地没有就报错。

- Command:启动镜像的时候执行的命令
  - eg:busybox并不是一个程序,而是一个工具类的集合,k8s集群启动管理后,由于没有前台进程阻塞,会自动关闭,解决方法就是让其一直在运行。
  - 解决:用command写一个死循环来执行,就可以一直执行了。
  - 查看:进入容器内部看这个文件:`kubectl exec pod-command -n dev -it -c busybox /bin/sh`

- args:
  - 特别说明:通过上面发现command已经可以完成启动命令和传递参数的功能,为什么这里还要提供一个args选项,用于传递参数呢?这其实跟docker有点关系,kubernetes中的command、args两项其实是实现覆盖Dockerfile中ENTRYPOINT的功能。

 1、如果command和args均没有写,那么用Dockerfile的配置。

 2、如果command写了,但args没有写,那么Dockerfile默认的配置会被忽略,执行输入的command

 3、如果command没写,但args写了,那么Dockerfile中配置的ENTRYPOINT的命令会被执行,使用当前args的参数

 4、如果command和args都写了,那么Dockerfile的配置被忽略,执行command并追加上args参数

- Env: 设置环境变量,但是不推荐,推荐单独放到一个配置文件里面
- port:
  - containerPort:容器监听的端口
  - hostport:容器端口映射到主机上的端口,如果设置,主机上只能运行一个容器的副本(其他的副本映射过来就端口冲突了),所以一般不设置。
  - 访问程序要使用pod ip:container port (集群内部访问)

- resources:资源配额。
  - limits:限制容器运行的最大占用资源,一旦超过就会自动重启
  - requests:规定下限。下限的意思是只有占**用的资源到了下限才能启动**。否则会是pending状态

- nodeSelector 键值对:根据键值对定义的信息,将pod调度到这些label的node上

### 常用字段含义

![image-20240725224115645](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202407252241732.png)

## kubectl apply：Client-side Apply 与 Server-side Apply

> [!summary]
> Client-side Apply（CSA）在客户端基于 last-applied、live state 和新 manifest 做三路合并；Server-side Apply（SSA）由 API Server 计算差异，并通过 `managedFields` 追踪字段所有权，把多工具共管时的静默覆盖转化为显式冲突。

> [!source]
> 参考：《kubectl apply 背后的真相：为什么 Server-side Apply 正在成为标配》。

跑 `kubectl apply -f deployment.yaml` 是每个 K8s 工程师的肌肉记忆。但你有没有想过：这一条命令在 API Server 那一侧到底做了什么？为什么同一个 Deployment，被 kubectl、Helm、Argo CD、HPA 同时管理的时候，会出现「副本数莫名其妙被改回去」「手动修复被覆盖」这类灵异事件？

答案都藏在 apply 的实现方式里——客户端算 diff（Client-side Apply，CSA） vs 服务端算 diff 并追踪字段所有权（Server-side Apply，SSA）。这篇文章把整个过程拆开讲清楚。

### 一、Client-side Apply：默认模式下的「三路合并」

`kubectl apply` 默认走的是客户端 apply。别被名字骗了，它并不是完全在客户端完成——先看它到底发了哪些 HTTP 请求：

```
kubectl apply -f deployment.yaml -v=8 2>&1 | grep -E "PATCH|POST|GET|Content-Type"
```

对一个已存在的资源，你会看到：

```
GET /openapi/v3
GET /openapi/v3/apis/apps/v1
GET /apis/apps/v1/namespaces/default/deployments/my-app
PATCH /apis/apps/v1/namespaces/default/deployments/my-app?fieldManager=kubectl-client-side-apply
  Content-Type: application/strategic-merge-patch+json
```

关键点： **先 GET 拉取 live state，再本地算 diff，最后发 PATCH**。补丁用的是 Kubernetes 特有的 `application/strategic-merge-patch+json` （strategic merge patch，SMP）。

SMP 和普通 JSON merge patch 的区别在于：它理解列表（list）字段该如何合并。比如 `spec.containers` 是「按 name 合并」的，而 `spec.tolerations` 是「整体替换」的。这些规则不是硬编码在 kubectl 里，而是从 OpenAPI schema 里读出来的：

```
kubectl get --raw /openapi/v3/apis/apps/v1 | jq \
  '.components.schemas["io.k8s.api.core.v1.PodSpec"].properties.containers'
```

返回值里有几个关键注释：

```
"x-kubernetes-list-map-keys": ["name"],
"x-kubernetes-list-type": "map",
"x-kubernetes-patch-merge-key": "name",
"x-kubernetes-patch-strategy": "merge"
```

而 `tolerations` 则是：

```
"x-kubernetes-list-type": "atomic"
```

atomic 意味着整个列表要整体替换，没有 merge key。

### 二、三路合并的致命盲区：静默覆盖

客户端 apply 的核心是「三路合并」，比较三个信息源：

1. 1\. **last-applied 注解**： `kubectl.kubernetes.io/last-applied-configuration`，记录 kubectl 上次 apply 的内容
2. 2\. **live state**：集群里资源的当前状态
3. 3\. **新 manifest**：你这次要 apply 的内容

通过对比「上次 apply 的内容」和「新 manifest」，kubectl 判断你 **故意改了哪些字段**，然后生成一个 patch。

问题出在这里： **last-applied 注解只在 `kubectl apply` 时更新**。如果 HPA 用 `/scale` 子资源把 replicas 从 3 改成 5，它是直接发 PATCH，完全绕过三路合并，也不会更新 annotation：

```
# 模拟 HPA 扩容到 5 副本
kubectl patch deployment my-app --subresource='scale' --type='merge' -p '{"spec":{"replicas":5}}'

# 此时 annotation 里仍然是 replicas: 3
kubectl get deployment my-app -o yaml
```

于是下一次你 `kubectl apply -f deployment.yaml` （manifest 里写的是 replicas: 3），kubectl 会认为「上次是 3，现在还是 3，没变」，HPA 扩上去的 5 个副本就 **被静默改回 3** ——没有任何警告、没有报错。这就是成熟平台里最常见的「副本数莫名回退」事故根源。

在只有 kubectl 一个工具管资源的小集群里，这没问题。但在 Helm、Argo CD、operator、admission webhook 同时写同一个对象的大集群里，静默覆盖会层出不穷，而且几乎无法排查。

### 三、Server-side Apply：把所有权追踪挪到服务端

加上 `--server-side` 就切换到 SSA：

```
kubectl apply --server-side -f deployment.yaml -v=8 2>&1 | grep -E "PATCH|POST|GET|Content-Type"
```
```
GET /openapi/v3
GET /openapi/v3/apis/apps/v1
PATCH /apis/apps/v1/namespaces/default/deployments/my-app?fieldManager=kubectl
  Content-Type: application/apply-patch+yaml
```

和 CSA 的三个区别：

1. 1\. **没有 GET 拉取 live state** ——diff 在服务端做，kubectl 不需要
2. 2\. **永远发 PATCH 而不是 POST** ——不管资源存不存在，API Server 内部处理 create-or-update
3. 3\. **Content-Type 是 `application/apply-patch+yaml`** ——SSA 专属，告诉 API Server 要追踪字段所有权并检测冲突

SSA 最核心的概念是 **field ownership（字段所有权）**。API Server 记录「哪个 manager 拥有每个字段」，存在对象的 `managedFields` 里。每个工具都有自己的 manager 名：

- • Helm → `helm`
- • Argo CD → `argocd`
- • kubectl → `kubectl`
- • 自定义 → 用 `--field-manager` 指定

API Server 用一个专门的 Go 库 `sigs.k8s.io/structured-merge-diff` 做结构化 diff，它理解 K8s 资源的结构（container 列表按 name 合并、tolerations 是 atomic、replicas 是标量）。

合并规则变成 **基于所有权** 而不是基于值：

这才是关键区别： **SMP 靠值来合并（看什么变了），SSA 靠所有权来合并（看谁声明了什么）**。冲突不再是「静默覆盖」，而是显式抛错：「这个字段是 helm 管的，你想改，先跟它协商」。

### 四、CRD 的坑：没有 schema 就是 atomic

SSA 对 CRD 的行为，取决于这个 CRD 有没有定义 schema、schema 怎么写的：

- • **没有 schema 信息**：SSA 不知道该 merge 列表，就采取最保守的默认—— **所有列表都按 atomic 整体替换**。每次 apply 都会整个列表覆盖，不留意就丢数据。
- • **CRD 作者可以控制**：在 schema 里加 `x-kubernetes-list-type` 和 `x-kubernetes-list-map-keys` 注释，和内置资源用的是同一套。

检查某个 CRD 的 SSA 注释：

```
kubectl get crd <crd-name> -o yaml | grep -A 3 "x-kubernetes-list"
```

如果输出为空，说明这个 CRD 的所有列表都会按 atomic 处理。值得注意的是，像 cert-manager 这类用 Kubebuilder 生成的 CRD， `status.conditions` 通常带 `x-kubernetes-list-type: map` + `x-kubernetes-list-map-keys: ["type"]`，这样不同 controller 可以各自管理不同 condition 而不互相覆盖。

写 operator 或 CRD 的人一定要记得加对注释——好在 Kubebuilder 等现代框架会自动生成，主流 operator 基本都是合规的。

### 五、Helm 4 的迁移

Helm 4 对 **新部署的 release 默认启用 SSA**，但对已有的 Helm 3 release 保持向后兼容，不会自动切换。要迁移，需要显式加 flag：

```
helm4 upgrade my-app my-chart --server-side=true
```

迁移后可以用 `--show-managed-fields` 验证：

```
kubectl get deployment my-app -o yaml --show-managed-fields
```

在 `managedFields` 里， `operation: Apply` 说明 Helm 已经在用 SSA； `operation: Update` 则还是旧的客户端 apply。

一个值得注意的点：Helm 3 会「认领」一堆 chart 里根本没声明的 Kubernetes 默认值（比如 `progressDeadlineSeconds` 、 `revisionHistoryLimit` 等）。迁移到 SSA 后，这些默认值不再由 Helm 拥有，因此不会产生冲突。但如果在生产环境里，其他工具（kubectl、Argo CD、operator）已经碰过同一批资源，升级 **一定会冒出冲突** ——每个冲突都会明确告诉你「哪个字段有争议、谁拥有它」。

还有两个坑要记住：

1. 1\. **Helm 3 / Helm 4 混用**：一个用 Helm 4 + server-side 升级过的 release，如果再用 Helm 3 回滚，那次回滚会退回到客户端 apply。
2. 2\. **Helm 的 release Secret**：Helm 4 用 SSA 后，Secret 不再用来算 diff，但 `helm rollback` 和 `helm history` 仍然依赖它，别乱删。

### 收尾

回到最初的问题： `kubectl apply` 到底做了什么？在默认的 CSA 下，它是在客户端做三路合并再发 patch，本质上是「值对值」的合并，多个工具同时写同一个对象时必然产生静默覆盖。

SSA 把所有权追踪挪到 API Server，通过 `managedFields` 记录「谁拥有哪个字段」，把「静默覆盖」变成了「显式冲突」。冲突不是 bug，而是特性—— **每一个 SSA 暴露出来的冲突，都是 CSA 会悄悄埋掉的雷**。

实用建议：

- 新项目直接上 `kubectl apply --server-side`，或用 Argo CD / Helm 4 这些默认支持 SSA 的工具链
- 多工具共管同一资源的团队，尽快迁移，别再被「副本数莫名回退」折磨
- 写 CRD/operator 时务必加对 `x-kubernetes-list-type` 注释，否则 SSA 会按 atomic 替你「整体替换」列表
- 排查字段冲突时，先 `kubectl get <obj> -o yaml --show-managed-fields` 看所有权归属

Kubernetes 从 1.22 就支持了 SSA，Helm 4 的默认启用终于让生态跟上了节奏。是时候把 `--server-side` 变成你的默认肌肉记忆了。

### 延伸阅读

- [Server-Side Apply 官方文档](https://kubernetes.io/docs/reference/using-api/server-side-apply/)
- [Server Side Apply 详解](https://juejin.cn/post/7173328614644006942)

## kubectl create -f --dry-run=client

- 快速生成yaml文件:`kubectl create deploy nginx -n nginx --image=xxx:xxx --dry-run=client -o yaml > nginx.yaml`
