---
title: K8s基础-容器运行时-containerd
tags:
  - kubernetes
  - k8s-basics
aliases:
  - k8s容器运行时containerd
---

# containerd 如何在 Kubernetes 节点上运行容器

Pod 已经调度到节点，并不意味着容器已经启动。节点上的 kubelet 还需要准备存储、创建 Pod sandbox、拉取镜像，再把运行容器的工作交给容器运行时。理解这条调用链，可以帮助我们判断故障应该从 Kubernetes API、CRI，还是节点上的运行时查起。

本文以 Linux 节点上的 containerd 和 runc 为例。阅读命令前，先确认命令是在节点主机上执行，且当前用户有访问运行时 socket 的权限；这些权限通常接近节点 root 权限。

## CRI：kubelet 与运行时之间的接口

CRI（Container Runtime Interface，容器运行时接口）定义了 kubelet 调用运行时的 gRPC 协议。接口分为运行时服务和镜像服务，分别处理 sandbox、容器生命周期与镜像操作。containerd、CRI-O 等实现了这套接口，因此 kubelet 可以通过配置端点连接不同运行时。

CRI 是协议，不是接收请求后再转发的独立进程。Kata Containers 等隔离方案通常还需要配合 containerd/CRI-O 的 runtime handler 和 Kubernetes RuntimeClass，不能只把名称填入 CRI socket。Kubernetes 的[容器运行时说明](https://kubernetes.io/docs/setup/production-environment/container-runtimes/)介绍了运行时兼容条件；Kubernetes 1.26 起要求运行时支持 CRI v1。

一次常见的 Pod 启动过程是：

1. 用户将 Pod 或控制器清单提交给 API server，调度器为 Pod 选择节点。
2. 目标节点上的 kubelet 观察到这个 Pod，协调卷挂载，并通过 CRI 请求运行时创建 Pod sandbox。
3. 运行时在 sandbox 阶段协调 CNI 插件配置网络，按需拉取镜像，再创建并启动业务容器。
4. kubelet 持续查询容器状态、执行探针，并把 Pod 状态报告给 API server。

Pod 是 Kubernetes 的管理对象；实际进程由运行时启动。容器在原 Pod 内重启，与控制器重新创建一个 Pod，是两种不同的操作。

## containerd、Docker 与 runc 的分工

containerd 管理镜像传输与存储、快照以及容器生命周期。它最初从 Docker Engine 中独立出来，2017 年加入 CNCF，后来成为 CNCF 毕业项目。Docker Engine 仍可使用 containerd，Kubernetes 也能直接通过 CRI 使用 containerd，无需安装完整 Docker Engine。

Docker 提供镜像构建、CLI、网络等面向用户的完整体验。containerd 更侧重节点运行时能力；在 Linux 上，它通常通过 shim 和 OCI runtime（常见为 runc）创建容器进程。runc 负责使用 namespace、cgroup 等内核机制启动进程，持续的生命周期管理由 containerd 与 shim 配合完成。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202507152134702.png" alt="image-20250715213449459" style="zoom:33%;" />

图中的 Docker 调用链可以读作 Docker Engine → containerd → shim/runc。Kubernetes 使用 containerd 时，入口通常是 kubelet → CRI → containerd。Docker Engine 自身不直接实现 CRI，现代 Kubernetes 如需接入 Docker Engine，要使用 cri-dockerd 适配层。

## 先识别 containerd 配置版本

containerd 的配置文件通常在 `/etc/containerd/config.toml`。发行版可能调整路径或禁用 CRI 插件，因此排查前先查看本机版本与服务启动参数：

```sh
containerd --version
systemctl cat containerd
containerd config dump
```

`containerd config dump` 用于检查有效配置，输出可能包含镜像仓库信息，分享前需检查其中是否有凭据。不要为了套用示例直接覆盖现有配置。

在使用 systemd cgroup 驱动的节点上，kubelet 与运行时应使用一致的驱动。下面两段只展示 runc 对应的配置位置，不是可直接覆盖全文件的完整配置。containerd 1.x 的常见写法为：

```toml
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
  SystemdCgroup = true
```

containerd 2.x 的配置布局有所变化：

```toml
[plugins.'io.containerd.cri.v1.runtime'.containerd.runtimes.runc.options]
  SystemdCgroup = true
```

这两种路径见 Kubernetes 官方的[containerd 配置说明](https://kubernetes.io/docs/setup/production-environment/container-runtimes/#containerd)。需要 CRI 的节点还应确认 `disabled_plugins` 中没有 `cri`。注册表、sandbox 镜像等字段也可能随配置版本改变，应以当前安装版本生成的默认配置和[containerd 配置文档](https://github.com/containerd/containerd/blob/main/docs/cri/config.md)为准。修改驱动或重启运行时会影响节点工作负载，已有集群应按节点维护流程实施。

## 三种命令行工具分别适合做什么

| 工具 | 调用入口 | 常见用途 |
| --- | --- | --- |
| `ctr` | containerd 原生 API | 检查 containerd 的 namespace、镜像、容器等底层对象 |
| `nerdctl` | containerd 原生 API | 使用接近 Docker CLI 的方式运行、查看容器 |
| `crictl` | CRI | 按 kubelet 使用的接口检查 Pod sandbox、容器与镜像 |

排查 Kubernetes 节点时，`crictl` 很有用：它能帮助确认 kubelet 实际连接的 CRI 端点是否正常。`ctr` 和 `nerdctl` 能看到不同层面的信息，但不能替代 Kubernetes 控制器管理 Pod。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202507152141594.png" alt="image-20250715214142382" style="zoom:50%;" />

### ctr：注意 namespace 与镜像仓库配置

containerd 也有 namespace，用于隔离 API 对象。它与 Kubernetes Namespace 是两套概念；同一节点上不同 Kubernetes Namespace 的 Pod，通常都由 CRI 放在 containerd 的 `k8s.io` namespace 中。`ctr` 默认使用 `default`，可先查看实际存在的 namespace：

```sh
ctr ns ls
ctr -n k8s.io images ls
```

手工导入给该节点 Kubernetes 使用的镜像时，需要导入到 `k8s.io`，并确保镜像平台、名称、标签与 Pod 清单匹配：

```sh
ctr -n k8s.io images import image.tar
```

`ctr images pull` 不会自动套用 CRI 插件下的全部仓库配置。若测试环境确实使用明文 HTTP 仓库，可显式指定：

```sh
ctr -n k8s.io images pull --plain-http registry.example.com/team/app:v1
```

`--plain-http` 表示使用 HTTP，不能拿它代替正确的 HTTPS 证书配置。生产私有仓库应按[containerd 仓库配置](https://github.com/containerd/containerd/blob/main/docs/hosts.md)设置主机配置与证书，并区分 CRI 使用的配置和 `ctr --hosts-dir` 指定的配置。

### nerdctl：保留 Docker CLI 的操作习惯

下面保留一个历史版本的安装示例，用于说明二进制安装过程；`1.7.6` 不是通用推荐版本，实际下载前应确认 CPU 架构、containerd 兼容性和[nerdctl 发布说明](https://github.com/containerd/nerdctl/releases)。

~~~sh
# 历史示例：Linux amd64，nerdctl 1.7.6
curl -fLO https://github.com/containerd/nerdctl/releases/download/v1.7.6/nerdctl-1.7.6-linux-amd64.tar.gz
tar xf nerdctl-1.7.6-linux-amd64.tar.gz
sudo mv nerdctl /usr/local/bin/
~~~

如果 API server 不可用，仍可登录节点检查本机容器：

```sh
nerdctl --namespace k8s.io ps -a
crictl pods
crictl ps -a
```

`crictl` 需要通过配置文件或参数连接正确的运行时端点；常见 containerd 端点是 `unix:///run/containerd/containerd.sock`。查看容器和日志后，应继续排查 kubelet、运行时与控制平面的故障原因。直接用底层 CLI 删除或重建受 Kubernetes 管理的容器，可能与 kubelet 的协调动作冲突。
