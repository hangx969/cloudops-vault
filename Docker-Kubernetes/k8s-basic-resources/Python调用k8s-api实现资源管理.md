---
title: Python调用K8s-API实现资源管理
tags:
  - kubernetes
  - k8s-basics
aliases:
  - Pythonk8sAPI
---

# 用 Python 管理 Kubernetes 资源：从连接集群到增删改查

平时创建 Pod、查询 Service，通常先想到 `kubectl`。当这些操作要进入发布平台、巡检程序或定时任务时，Python 程序也可以直接调用 Kubernetes API。官方 Python 客户端负责请求序列化、身份认证和 API 对象转换，程序仍然受到集群 RBAC 权限约束。

下面从本地连接集群开始，依次完成查询、创建 Deployment、修改 Pod 镜像和删除实验 Pod。示例使用同步客户端；安装版本应先对照[官方兼容性矩阵](https://github.com/kubernetes-client/python#compatibility)选择。运行前需要了解 Pod、Deployment 和 Namespace，并准备有相应权限的实验集群。

## 准备 Python 环境和访问凭据

### 安装依赖

Python 是运行环境，PyCharm 等 IDE 可按习惯选择。在虚拟环境中安装客户端和读取 YAML 所需的 PyYAML：

~~~sh
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows PowerShell 则执行 .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install kubernetes pyyaml
~~~

项目确认可用后，应将实际使用的版本锁定到依赖文件。虚拟环境可以隔离项目依赖，减少与系统 Python 包相互影响。

### 加载 kubeconfig

kubeconfig 包含 API Server 地址、CA 和用户认证信息。向集群管理员申请满足实验权限的凭据，妥善保管；不应为了运行脚本直接复制控制平面的管理员配置。确认其中的 API Server 地址可从本机访问，引用的证书文件路径也可用。

下文统一从 `./config` 加载 kubeconfig，并用 `context` 显式选择实验集群。将两个占位值替换为自己的路径和上下文；不要把凭据提交到代码仓库。Windows 路径可使用原始字符串，例如 `r"E:\work\python-k8s\config"`，避免反斜杠转义。

~~~python
from kubernetes import config

config.load_kube_config(config_file="./config", context="your-lab-context")
~~~

当程序部署到集群内 Pod 时，可以改用 `config.load_incluster_config()`，通过 Pod 的 ServiceAccount 认证；其权限仍需由 Role/RoleBinding 等对象授予。两种入口的使用方式见[官方客户端示例](https://github.com/kubernetes-client/python/tree/master/examples)。不要通过关闭 TLS 校验来绕过证书错误。

下列查询代码会列出集群范围的 Namespace、Service、Pod 和 Deployment，因此需要集群范围的 `list` 权限。若只获准访问一个 Namespace，应改用相应的 `list_namespaced_*` 方法，不必为此申请管理员权限。写入实验分别需要 `deployments` 的 `create`、`pods` 的 `get/patch/delete` 权限。

## 准备两份资源清单

先保存 `pod-nginx.yaml`。它是后面读取、修改和删除操作的对象，使用独立 Pod，避免 Deployment 在删除后立即补建。

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: po-nginx
  namespace: default
spec:
  containers:
  - name: nginx
    image: nginx:stable
    imagePullPolicy: IfNotPresent
~~~

将 Deployment 清单保存为 `nginx-py.yaml`，放在创建脚本所在目录。该文件稍后由 Python 提交，不要提前创建同名 Deployment：

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-nginx
  namespace: default
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
      - name: nginx
        image: nginx:stable
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
~~~

`stable` 仍是可变标签，适合这里说明 API 操作；正式发布应选择已验证的具体版本或镜像摘要。创建前检查当前上下文，再部署实验 Pod：

~~~sh
kubectl --kubeconfig ./config --context your-lab-context config current-context
kubectl --kubeconfig ./config --context your-lab-context apply -f pod-nginx.yaml
kubectl --kubeconfig ./config --context your-lab-context get pod po-nginx -n default
~~~

## 查询资源：先认识 API 分组

`CoreV1Api` 对应核心 `v1` API，管理 Namespace、Service、Pod 等对象；`AppsV1Api` 对应 `apps/v1`，管理 Deployment 等工作负载。方法名中的 `namespaced` 表示需要传入 Namespace，`for_all_namespaces` 表示跨 Namespace 查询。

下面保留全局查询和读取指定 Pod 两种用法。Pod 尚未完成调度或网络初始化时，`pod_ip` 可以是 `None`；Deployment 的 `spec.replicas` 是期望副本数，不能直接视为已就绪副本数。

~~~python
from kubernetes import client, config

config.load_kube_config(config_file="./config", context="your-lab-context")
v1 = client.CoreV1Api()

print("All namespaces:")
for namespace in v1.list_namespace().items:
    print(namespace.metadata.name)

print("All services:")
for svc in v1.list_service_for_all_namespaces().items:
    print(svc.metadata.namespace, svc.metadata.name,
          svc.spec.cluster_ip, svc.spec.ports, sep="\t")

print("All pods:")
for pod in v1.list_pod_for_all_namespaces().items:
    print(pod.status.pod_ip, pod.metadata.namespace, pod.metadata.name, sep="\t")

apps = client.AppsV1Api()
print("All deployments:")
for deployment in apps.list_deployment_for_all_namespaces().items:
    print(deployment.metadata.name, deployment.metadata.namespace,
          deployment.spec.replicas, sep="\t")

print("Read pod:")
resp = v1.read_namespaced_pod(namespace="default", name="po-nginx")
print(resp.spec.containers[0])
print(resp.spec.containers[0].image)
~~~

列表 API 返回的是包含 `items` 的列表对象；读取单个 Pod 返回的是 `V1Pod`。Python 属性使用下划线形式，例如 YAML 中的 `clusterIP` 对应 `cluster_ip`。

## 创建 Deployment：读取 YAML 后提交

`yaml.safe_load()` 将清单解析为字典，客户端把它作为请求体提交给 API Server。这里使用脚本自身所在目录定位文件，避免从不同工作目录启动时找不到 YAML。

~~~python
from pathlib import Path
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException


def main():
    config.load_kube_config(config_file="./config", context="your-lab-context")
    manifest = Path(__file__).resolve().parent / "nginx-py.yaml"
    with manifest.open(encoding="utf-8") as f:
        deployment = yaml.safe_load(f)

    apps = client.AppsV1Api()
    try:
        resp = apps.create_namespaced_deployment(namespace="default", body=deployment)
    except ApiException as exc:
        print(f"创建失败：HTTP {exc.status}，{exc.reason}")
        raise
    print(f"Deployment created: {resp.metadata.name}")


if __name__ == "__main__":
    main()
~~~

返回创建成功表示 API Server 接受了资源，调度、拉取镜像和容器启动仍会异步进行。可以用下面的命令等待发布结果：

~~~sh
kubectl --kubeconfig ./config --context your-lab-context rollout status deployment/dep-nginx -n default
~~~

重复运行 `create_namespaced_deployment()` 不会自动更新已有资源，同名对象存在时通常返回 `409 Conflict`。需要重复执行的工具应明确选择“创建”“更新”或声明式应用的语义，不要吞掉异常后当作成功。方法签名可查[官方 AppsV1Api 文档](https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AppsV1Api.md)。

## 修改 Pod：只提交需要变化的字段

Pod 的大部分规格字段不能直接修改，容器镜像是允许更新的字段之一。本例先读取原镜像，再按容器名称提交局部补丁。将镜像切换为另一条 Nginx 标签，可以在保持 Web 服务用途的同时观察镜像更新。若换为 BusyBox，其默认命令可能很快退出并触发反复重启；这类变更还需要同时设计容器启动命令。

~~~python
from kubernetes import client, config


def main():
    config.load_kube_config(config_file="./config", context="your-lab-context")
    core = client.CoreV1Api()
    old = core.read_namespaced_pod(namespace="default", name="po-nginx")
    print("Old image:", old.spec.containers[0].image)
    patch = {"spec": {"containers": [{"name": "nginx", "image": "nginx:alpine"}]}}
    updated = core.patch_namespaced_pod(
        namespace="default", name="po-nginx", body=patch,
        _content_type="application/strategic-merge-patch+json",
    )
    print("New image:", updated.spec.containers[0].image)


if __name__ == "__main__":
    main()
~~~

这里显式指定 Strategic Merge Patch，使 `containers` 列表按容器 `name` 合并，保留未提交的其他容器和字段。当前客户端支持 `_content_type` 参数，可核对[生成方法源码](https://github.com/kubernetes-client/python/blob/master/kubernetes/client/api/core_v1_api.py)；旧版客户端的参数支持可能不同，应先核对所锁定版本，不能直接套用 JSON Merge Patch 的数组整体替换语义。

补丁返回新镜像字段，不代表新容器已经就绪，还要观察 Pod 状态和事件。如果 Pod 由 Deployment 管理，通常应修改 Deployment 的 Pod 模板，让控制器完成滚动更新；单独修改其下属 Pod 不会改变期望模板，后续重建时还会回到模板指定的镜像。

## 删除实验 Pod

删除操作必须明确资源名称和 Namespace。这里只删除前面创建的独立 Pod `default/po-nginx`，不遍历删除其他对象：

~~~python
from kubernetes import client, config


def main():
    config.load_kube_config(config_file="./config", context="your-lab-context")
    core = client.CoreV1Api()
    core.delete_namespaced_pod(namespace="default", name="po-nginx")
    print("Deletion requested: default/po-nginx")


if __name__ == "__main__":
    main()
~~~

API 请求成功后，Pod 可能先进入 `Terminating`，等待优雅终止和清理。若删除的是 Deployment 管理的 Pod，控制器通常会创建替代副本；停止整个应用应操作对应控制器，不能靠反复删除 Pod 实现。

## 根据错误定位问题

认证、权限和资源校验发生在 API Server 端。排错时先记录方法、资源名称、Namespace 和 HTTP 状态，不要将 kubeconfig 或令牌写入日志。

| 状态或现象 | 优先检查 |
| --- | --- |
| 连接超时、TLS 校验失败 | API Server 网络可达性、CA、证书名称、代理设置 |
| `401 Unauthorized` | 凭据是否有效，是否需要重新登录 |
| `403 Forbidden` | 当前身份是否具备目标资源和 Namespace 所需的 RBAC 权限 |
| `404 Not Found` | 资源名称、Namespace、API 版本是否正确 |
| `409 Conflict` | 创建时是否重名；更新时是否存在资源版本冲突 |
| `422 Unprocessable Entity` | 清单字段、必填项、不可变字段是否违反 API 规则 |

完成这些实验后，同一套“加载配置 → 选择 API 分组 → 提交请求 → 检查资源状态”的流程就可以用于巡检或资源管理程序。批量操作还需要处理分页、超时和重试；写入重试应先确认请求是否已生效，避免重复创建或误报成功。
