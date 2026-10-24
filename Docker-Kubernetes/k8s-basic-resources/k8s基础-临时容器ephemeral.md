---
title: K8s基础-临时容器Ephemeral
tags:
  - kubernetes
  - k8s-basics
aliases:
  - k8s临时容器
---

# Kubernetes 临时容器：不用重建 Pod，也能进入现场排障

应用使用精简镜像后，容器里可能没有 shell、curl 或 ps；故障又只在当前 Pod 中出现，重新构建镜像会丢失现场。Ephemeral Container（临时容器）允许向现有 Pod 加入一个带诊断工具的容器，用它检查网络或进程。

本文先说明它与普通容器的区别，再用 `kubectl debug` 调试 Tomcat，并解释直接调用 API 时容易出现的请求格式问题。操作前需要测试 Pod、允许创建临时容器的 RBAC 权限，以及节点可拉取的诊断镜像。本文的命令会修改 Pod，应在获得相应环境授权后使用。

## 临时容器适合解决什么问题

临时容器为现有 Pod 中的诊断任务而设计，通常不需要重启业务容器。前提是 Pod 仍存在且其运行环境支持启动调试容器；它不适用于静态 Pod，也不能代替已经消失的现场。

### 添加方式、字段限制和权限边界

1. 动态添加：通过 `pods/ephemeralcontainers` 子资源更新现有 Pod，适合缺少排障工具或业务容器无法 exec 的情况。调试进程仍会占用资源，不能承诺对业务完全无影响。
2. 字段受限：临时容器最终保存在 `spec.ephemeralContainers`，但不能用普通 Pod 创建、更新或 `kubectl edit` 的方式添加，必须走专用子资源。`ports`、`resources`、存活和就绪探针等字段不允许设置；临时容器不会自动重启。
3. 安全边界仍然有效：网络通常与 Pod 共享，进程可见性取决于目标容器、运行时和权限。它不会自动挂载目标容器的所有卷、继承所有凭据或获得特权。反过来，高权限调试容器可能读取敏感信息并影响业务，因此需要限制镜像和 RBAC，并记录审计。

这些限制来自官方[临时容器说明](https://kubernetes.io/docs/concepts/workloads/pods/ephemeral-containers/)。临时容器在 Kubernetes 1.25 已稳定；当前版本无需修改控制平面 feature gate。

### 哪些故障适合临时容器

当业务容器持续崩溃，或镜像里没有 shell、curl 等工具时，`kubectl exec` 可能无法提供足够的信息。临时容器可以携带这些工具，在同一个 Pod 网络环境中检查 DNS、连接和进程状态。

它也可以用于短时性能采样、日志诊断或授权的安全审查。持续监控和日志采集仍应交给正常部署的代理；调试进程会消耗节点资源，运行时间和采集范围需要与故障目标相符。

### 用一条命令加入诊断工具

对于仍在运行的 Pod，可以指定包含诊断工具的镜像。下面的占位值分别是 Pod 名和目标容器名：

```bash
kubectl debug <pod-name> -it --image=busybox:1.36 --target=<container-name>
```

`--target` 指定 Pod 中的容器名，不是 Pod 名。它请求加入目标容器的进程命名空间；如果运行时不支持，调试容器仍可能启动，但 `ps` 看不到业务进程。即使能看到进程，文件和进程访问仍受权限限制。完整操作可对照官方[调试运行中的 Pod](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/#ephemeral-container)。

### 先检查环境和权限

```sh
kubectl version
kubectl auth can-i update pods/ephemeralcontainers -n default
kubectl auth can-i patch pods/ephemeralcontainers -n default
```

`kubectl debug` 的具体更新请求需有对应权限，交互连接还需要 `pods/attach` 等权限。授权应限定到所需命名空间和调试人员，不要为了排障授予 `cluster-admin`。

## 实验：从创建测试 Pod 到调用调试接口

以下实验使用 `default` 命名空间中的独立测试 Pod。示例里的 `tomcat-8.5-jre8:v1` 是自建镜像，需提前提供，或替换为可拉取且包含 Tomcat 的版本。业务容器名为 `tomcat-java`，后面的 `--target` 使用这个名字。

### 1. 创建主 Pod

~~~sh
tee pod-tomcat.yaml <<'EOF' 
apiVersion: v1
kind: Pod
metadata:
  name: tomcat-test
  namespace: default
  labels:
    app:  tomcat
spec:
  containers:
  - name:  tomcat-java
    image: tomcat-8.5-jre8:v1
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 8080
EOF
kubectl apply -f pod-tomcat.yaml
~~~

### 2. 用 kubectl debug 注入临时容器

~~~sh
kubectl debug -it tomcat-test --image=busybox --target=tomcat-java
#通过临时容器查看tomcat主容器信息
ps -ef | grep tomcat
#查看pod yaml中是否注入了临时容器
kubectl describe pods tomcat-test 
Ephemeral Containers:
  debugger-lhdc8:
    Container ID:   docker://e005a0bbd9020107585e8742fb8442c21d32a5365df6fa49bdf2ef48bab6b009
    Image:          busybox
    Image ID:       docker-pullable://busybox@sha256:5acba83a746c7608ed544dc1533b87c737a0b0fb730301639a0179f9344b1678
    Port:           <none>
    Host Port:      <none>
    State:          Running
      Started:      Sun, 19 May 2024 09:23:39 -0400
    Ready:          False
    Restart Count:  0
    Environment:    <none>
    Mounts:         <none>
~~~

### 3. 直接调用 ephemeralcontainers 子资源

日常排障优先使用 `kubectl debug`。若要理解底层请求，可以使用下面的 Pod 格式 JSON。该接口接收 `kind: Pod` 与 `spec.ephemeralContainers`，不是一个独立的 `kind: EphemeralContainers` 对象。删除并重建测试 Pod 的两条命令仅用于隔离本次实验；不要用于保留生产现场。

~~~sh
kubectl delete -f pod-tomcat.yaml
kubectl apply -f pod-tomcat.yaml
tee a.json <<'EOF' 
{
    "apiVersion": "v1",
    "kind": "Pod",
    "metadata": {
            "name": "tomcat-test"
    },
    "spec": {"ephemeralContainers": [{
        "command": [
            "sh"
        ],
        "image": "busybox",
        "imagePullPolicy": "IfNotPresent",
        "name": "debugger",
        "stdin": true,
        "tty": true,
        "targetContainerName": "tomcat-java",
        "terminationMessagePolicy": "File"
    }]}
}

EOF

kubectl replace --raw /api/v1/namespaces/default/pods/tomcat-test/ephemeralcontainers -f a.json
#通过attach连接到临时容器
kubectl attach -it -c debugger tomcat-test
# 调试进程退出后容器不会自动重启，无法再次 attach；条目仍保留在 Pod 中
~~~

如果收到以下错误，先检查请求体，不要把它判断成集群缺少 v1 API：

```text
EphemeralContainers in version "v1" cannot be handled as a Pod:
no kind "EphemeralContainers" is registered for version "v1"
```

下面的发现命令可以帮助区分 API 组与资源，但子资源并不一定作为顶层资源出现在 `kubectl api-resources` 的输出中。

```sh
kubectl get api-versions
kubectl api-resources --api-group=""
kubectl api-resources --api-group=apps
kubectl get --raw /api/v1 | jq '.resources[] | select(.name == "pods/ephemeralcontainers")'
```

对已有临时容器的 Pod，提交更新时需要保留现有条目，只追加新条目；不允许修改或删除旧条目。直接操作前还应读取最新对象，避免与其他调试请求并发冲突。

### 在 AKS 中加入 Azure CLI 调试容器

AKS 中应用与 Azure 服务交互异常时，可以使用包含 Azure CLI 的临时容器检查身份、DNS 和网络。调试容器不会自动继承业务容器的 Azure 登录态或所有挂载；使用工作负载身份时，还需明确配置对应环境变量和投射的 token 卷，避免误用个人高权限身份得出结论。

镜像可从 Microsoft Container Registry 获取。下面使用官方文档给出的固定版本格式 `2.74.0-azurelinux3.0` 演示导入；它用于说明命令，不代表当前最新版本。部署时仍应选择经过验证的受支持版本，详见[Azure CLI 容器说明](https://learn.microsoft.com/zh-cn/cli/azure/run-azure-cli-docker#run-the-docker-container-with-a-specific-version-of-the-azure-cli)。

~~~sh
#镜像上传到ACR
az acr import --name "<acr-name>" --source mcr.microsoft.com/azure-cli:2.74.0-azurelinux3.0 --image azure-cli:2.74.0-azurelinux3.0

#attach debug容器
kubectl debug -it <pod-name> -n <namespace> --image=<acr-login-server>/azure-cli:2.74.0-azurelinux3.0 --target=<container-name>
~~~

## 调试结束后为什么不能删除或重启它

临时容器不能修改、删除或自动重启，是 API 的设计限制，不应笼统称为 bug。退出后仍能在 Pod 的定义和状态中看到记录，但原进程已经结束，不能再次 attach。历史讨论见 [kubernetes#84764](https://github.com/kubernetes/kubernetes/issues/84764)。

要再次调试，可给 `kubectl debug` 指定新容器名，或像下面一样保留 `debugger` 并追加 `debugger1`。Pod 中容器名称必须唯一；反复注入会累积记录，最终通过业务控制器的正常替换流程更新 Pod。

~~~sh
tee a.json <<'EOF'
{
    "apiVersion": "v1",
    "kind": "Pod",
    "metadata": {
            "name": "tomcat-test"
    },
    "spec": {"ephemeralContainers": [
   {
        "command": [
            "sh"
        ],
        "image": "busybox",
        "imagePullPolicy": "IfNotPresent",
        "name": "debugger",
        "stdin": true,
        "tty": true,
        "targetContainerName": "tomcat-java",
        "terminationMessagePolicy": "File"
    },
      {"command": [
            "sh"
        ],
        "image": "busybox",
        "imagePullPolicy": "IfNotPresent",
        "name": "debugger1",
        "stdin": true,
        "tty": true,
        "targetContainerName": "tomcat-java",
        "terminationMessagePolicy": "File"
    }
]}
}
EOF

kubectl replace --raw /api/v1/namespaces/default/pods/tomcat-test/ephemeralcontainers -f a.json
~~~

## 历史版本的启用配置：用于识别旧集群设置

下面的静态 Pod 与 kubelet 配置用于识别旧实验环境，不是当前集群的启用步骤。稳定版本不需要 `EphemeralContainers=true`；已移除的 feature gate 可能使组件启动失败。`RemoveSelfLink` 与临时容器无关，也不应照抄。老集群应优先升级到受支持版本，再按对应版本文档检查可用性。

### API server 中的历史参数

~~~sh
vim /etc/kubernetes/manifests/kube-apiserver.yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    kubeadm.kubernetes.io/kube-apiserver.advertise-address.endpoint: 192.168.40.180:6443
  creationTimestamp: null
  labels:
    component: kube-apiserver
    tier: control-plane
  name: kube-apiserver
  namespace: kube-system
spec:
  containers:
  - command:
    - kube-apiserver
    - --advertise-address=192.168.40.180
    #......
    # 历史参数示意；当前版本不要添加下面的 gate
    # - --feature-gates=EphemeralContainers=true
# 历史启用参数；当前版本不应照抄
~~~

### Scheduler 中出现过的旧配置

~~~sh
vim /etc/kubernetes/manifests/kube-scheduler.yaml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    component: kube-scheduler
    tier: control-plane
  name: kube-scheduler
  namespace: kube-system
spec:
  containers:
  - command:
    - kube-scheduler
    - --authentication-kubeconfig=/etc/kubernetes/scheduler.conf
    - --authorization-kubeconfig=/etc/kubernetes/scheduler.conf
    - --bind-address=192.168.40.180
    - --kubeconfig=/etc/kubernetes/scheduler.conf
    - --leader-elect=true
    # - --feature-gates=EphemeralContainers=true
# 历史启用参数；当前版本不应照抄
~~~

### kubelet 的历史参数与重启操作

~~~sh
#master和node上都要改
vim /etc/sysconfig/kubelet 
KUBELET_EXTRA_ARGS="--feature-gates=EphemeralContainers=true"
~~~

旧实验在修改参数后重启 kubelet，并检查控制平面 Pod：

~~~sh
systemctl restart kubelet
kubectl get pods -n kube-system #检查pod正常工作
~~~

> [!warning] 注意
> 修改静态 Pod manifest 会触发控制平面组件重建，可能中断 API 访问。当前版本不要为了临时容器执行本节的修改或重启；历史环境变更也需要独立的升级与回滚计划。
