---
title: K8s基础-kubeadm
tags:
  - kubernetes
  - k8s-basics
aliases:
  - k8skubeadm
---

# kubeadm 做了什么：初始化流程、证书和集群升级

运行 `kubeadm init` 后，控制平面组件会陆续启动，终端最后给出节点加入命令。第一次安装时，我们很容易只关注这条命令是否成功；真正需要排错或升级时，才发现证书、静态 Pod、kubeconfig 和节点配置分别由不同步骤生成。

kubeadm 是集群引导与生命周期工具，负责把 Kubernetes 组件按一套约定组织起来。它不会代替我们准备全部主机条件，也不会自动提供业务高可用、CNI 网络、持久存储和监控。本文解释默认 Linux 控制平面的初始化过程，随后梳理证书用途与升级顺序。外部 etcd、外部 CA 或定制发行版会有不同配置，应以本机版本对应文档和实际文件为准。

## 先认识初始化流程

![kubeadm init：历史流程总览](https://raw.githubusercontent.com/hangx969/upload-images-md/main/k8s-basic-resources/2026-10-25/k8s-25-01-kubeadm-historical-overview-17e77702d5e9.png)

![kubeadm 历史流程：配置、预检与本地启动](https://raw.githubusercontent.com/hangx969/upload-images-md/main/k8s-basic-resources/2026-10-25/k8s-25-01-kubeadm-historical-bootstrap-7efe0ba6199f.png)

![kubeadm 历史流程：清单与收尾配置](https://raw.githubusercontent.com/hangx969/upload-images-md/main/k8s-basic-resources/2026-10-25/k8s-25-01-kubeadm-historical-completion-2b573f15dba9.png)

这张历史流程图可用于理解各阶段的关系，部分名称和特性已经改变。按当前的常见默认配置，`init` 会先检查环境，再准备证书、kubeconfig 和静态 Pod 清单，等待控制平面健康，最后写入引导配置并安装基础插件。各阶段也可以用 `kubeadm init phase` 单独调用，具体职责见[kubeadm 实现说明](https://kubernetes.io/docs/reference/setup-tools/kubeadm/implementation-details/)。

### 预检查在检查什么

预检查用于尽早发现主机条件冲突，检查项、严重级别和默认值会随版本改变。可以按身份、网络、运行时和既有配置几类理解检查结果，实际检查集合以目标版本为准。

| 检查范围 | 常见检查内容 | 出现问题时应如何理解 |
| --- | --- | --- |
| 执行身份与版本 | 是否有 root 权限，kubeadm、kubelet 与目标控制平面版本是否兼容 | 版本兼容不是简单的 `kubeadm >= Kubernetes`，应遵循版本偏差策略 |
| 主机网络 | 主机名解析、本机地址、路由、代理与 `NO_PROXY` | 使用代理本身并非禁止，应让控制平面、节点与 Pod/Service 网段正确绕过代理 |
| 防火墙与端口 | API server、kubelet、scheduler、controller manager，以及 etcd 端口是否可用 | 不必一律关闭防火墙；应按角色开放必要端口，常见端口包括 6443、10250、10257、10259、2379、2380 |
| 既有文件与数据 | `/etc/kubernetes/manifests` 中是否已有清单，本地 etcd 数据目录是否可用于初始化 | 可能是残留安装，也可能是已有集群，必须先确认，不要直接删除 |
| 容器运行时 | CRI socket、运行时服务、CRI 版本及 cgroup 驱动是否可用 | 现代集群检查的是 CRI 运行时；Docker Engine 需要 cri-dockerd 适配层 |
| kubelet 服务 | 是否安装、版本是否受支持、服务是否启用 | kubelet 不能新于与之通信的 API server，允许的旧版本范围随版本策略确定 |
| 系统内核与资源控制 | 内核、操作系统、cgroup 支持及 swap 配置 | swap 需要结合 kubelet 的 `failSwapOn` 与 NodeSwap 配置判断，初学实验通常按安装文档禁用 |
| 系统工具 | `crictl`、`ip`、`iptables`、`mount`、`nsenter`，以及旧实验中涉及的 `ebtables`、`ethtool`、`socat`、`tc`、`touch` | 依赖与具体检查集合随版本和网络方案变化，不要机械补装全部历史工具 |
| 网络转发 | IPv4/IPv6 forwarding；桥接流量是否需经过 netfilter | `ip_forward`、`bridge-nf-call-iptables` 等需结合 CNI 模式设置，不是所有模式都相同 |
| IPVS 模式 | 选择 IPVS 时所需模块是否可用 | 只在使用相应 kube-proxy 模式时有意义 |
| etcd | 本地成员端口与数据目录，或外部 etcd 的连通性、版本与证书 | 外部 etcd 由独立生命周期管理，不能假设 kubeadm 会自动维护全部成员 |

较早的实验资料会检查 Docker 的 GraphDriver，或要求加载特定桥接模块。这些记录能解释旧环境故障，但不能直接套用到 containerd 和所有 CNI 方案。不要通过 `--ignore-preflight-errors=all` 绕过尚未理解的失败；先根据检查名称定位原因。所需网络端口可对照[官方端口与协议](https://kubernetes.io/docs/reference/networking/ports-and-protocols/)。

### 检查通过后生成哪些内容

控制平面需要先具备身份和本地启动配置，才能接收其他节点加入。默认流程可以按下面的顺序理解：

1. 在 `/etc/kubernetes/pki` 生成或复用 CA、组件证书和 ServiceAccount 签名密钥，为组件之间的 TLS 通信准备身份。
2. 生成 kubelet、scheduler、controller manager 以及管理员使用的 kubeconfig，并为 kubelet 写入本地配置。
3. 在 `/etc/kubernetes/manifests` 写入 API server、controller manager、scheduler 和本地 etcd 的静态 Pod 清单，由 kubelet 负责启动。
4. 等待控制平面健康，把集群配置保存到 `kube-system/kubeadm-config`，把 kubelet 的公共配置保存到 `kube-system/kubelet-config`。旧版本可能使用 `kubelet-config-<version>` 形式的名称。
5. 给当前节点添加 `node-role.kubernetes.io/control-plane` 标签和默认 `NoSchedule` 污点，写入必要的节点信息。旧版 `master` 名称属于历史约定。
6. 创建 bootstrap token Secret 和相应 RBAC，准备 `kube-public/cluster-info`，用于节点发现与 TLS bootstrapping。
7. 通过 API 安装 CoreDNS 和 kube-proxy 等默认插件，输出 `kubeadm join` 命令。CNI 仍需另外安装，插件未准备好时节点或 DNS Pod 可能尚未就绪。

历史流程中出现过 DynamicKubeletConfig，以及把控制平面转换成 DaemonSet 的 self-hosted 实验方案。它们不属于现代 kubeadm 的标准初始化步骤；阅读旧日志或旧图时可以保留这个背景，但不要据此启用旧特性或寻找不存在的默认配置。

`admin.conf` 是高权限管理员配置。现代 kubeadm 还可能生成 `super-admin.conf`，其中的超级用户身份可以绕过 RBAC，应作为应急凭据妥善保管，不能分发给日常用户。集群初始创建后，应另外配置职责明确的用户访问方式。

## 三组 CA 与组件证书如何对应

默认证书目录分为 `/etc/kubernetes/pki` 与其中的 `etcd` 子目录。`.crt` 是证书，`.key` 是私钥；私钥能用于冒用相应身份或签发新证书，必须限制读取权限。证书文件存在也不表示有效，需要同时检查有效期、用途与访问地址。

### Kubernetes 根 CA

`/etc/kubernetes/pki/ca.crt` 与 `ca.key` 是 Kubernetes 根 CA 的证书和私钥。它签发的证书包括：

| 证书与私钥 | 通信中的用途 |
| --- | --- |
| `/etc/kubernetes/pki/apiserver.crt`、`apiserver.key` | API server 向客户端证明自己的服务端身份 |
| `/etc/kubernetes/pki/apiserver-kubelet-client.crt`、`apiserver-kubelet-client.key` | API server 主动连接 kubelet 时使用的客户端身份，例如日志和 exec 相关请求 |

这些用途由 TLS 通信方向决定，不能把 `apiserver-kubelet-client` 误认为 kubelet 访问 API server 的证书。kubelet 自身的客户端证书与 kubeconfig 是另一条认证路径。

### front-proxy 根 CA

聚合 API 场景中，代理会把已认证的用户身份传给扩展 API server。`front-proxy-ca.crt`、`front-proxy-ca.key` 是这条信任链使用的 CA；`front-proxy-client.crt`、`front-proxy-client.key` 是 API server 作为代理访问扩展服务时使用的客户端证书。它们均位于 `/etc/kubernetes/pki`。

`--requestheader-client-ca-file` 指定用于校验受信任代理客户端证书的 CA，配合允许的客户端名称与请求头配置，防止普通客户端伪造用户身份。不要把 front-proxy CA 与普通客户端认证 CA 混用。具体信任关系见[聚合层配置](https://kubernetes.io/docs/tasks/extend-kubernetes/configure-aggregation-layer/)。

### etcd 根 CA

etcd 使用独立的 CA。`/etc/kubernetes/pki/etcd/ca.crt` 与 `ca.key` 签发 etcd 服务端、成员互联与健康检查相关证书：

| 证书与私钥 | 用途 |
| --- | --- |
| `/etc/kubernetes/pki/etcd/server.crt`、`server.key` | etcd 对客户端提供服务时的 TLS 身份 |
| `/etc/kubernetes/pki/etcd/peer.crt`、`peer.key` | etcd 成员之间通信，peer 指同一集群中的其他成员 |
| `/etc/kubernetes/pki/etcd/healthcheck-client.crt`、`healthcheck-client.key` | 具备 etcd 客户端身份的健康检查或诊断工具 |
| `/etc/kubernetes/pki/apiserver-etcd-client.crt`、`apiserver-etcd-client.key` | API server 访问 etcd 使用的客户端身份；文件位于上一级 pki 目录 |

旧版 etcd 静态 Pod 的 `describe` 输出可能含有下面的 exec 探针，它使用健康检查证书运行 `etcdctl`：

```text
Liveness: exec [/bin/sh -ec ETCDCTL_API=3 etcdctl --endpoints=https://[127.0.0.1]:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get foo] delay=15s timeout=15s period=10s #success=1 #failure=8
```

这是一段历史输出，现代清单可能使用不同探针或健康端点。诊断时应读取当前 `/etc/kubernetes/manifests/etcd.yaml`，不能假定探针仍执行 `get foo`。证书布局与轮换操作可对照[kubeadm 证书管理](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-certs/)。

在有权限的控制平面节点上，可以先只查看到期情况：

```sh
sudo kubeadm certs check-expiration
```

该命令用于检查，不能代替证书轮换、外部 CA 管理或 CA 私钥备份。外部签发的证书需要遵循外部 CA 的更新流程。

## kubeadm 集群升级要遵循什么顺序

升级不是只更新 kubeadm 二进制。它还涉及控制平面清单、kubelet 配置、节点软件包、网络插件以及可能的 etcd 版本变化。开始前要阅读目标版本发布说明，备份 etcd 与业务状态，并确认备份能够恢复。

官方[kubeadm 升级流程](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/)按版本更新，操作时要选择与源版本、目标版本对应的页面。跨次版本升级不能跳级，应先升级第一个控制平面节点，再逐个处理其余控制平面节点，最后处理工作节点。

| 阶段 | 核心动作 | 容易漏掉的边界 |
| --- | --- | --- |
| 规划版本 | 确认软件源、目标补丁版本和插件兼容性 | `pkgs.k8s.io` 按次版本分仓库，旧软件源可能已经冻结 |
| 首个控制平面 | 先安装目标版本 kubeadm，运行 `kubeadm upgrade plan`，确认后运行 `kubeadm upgrade apply <目标版本>` | plan 是评估，apply 才修改控制平面；不要多节点同时执行首节点步骤 |
| 其他控制平面 | 升级本机 kubeadm，再运行 `kubeadm upgrade node` | 每次处理一个节点，保留控制平面与 etcd 多数派 |
| 每个节点的 kubelet | 按要求 drain，升级 kubelet/kubectl，重启 kubelet并检查状态，再 uncordon | 次版本 kubelet 升级前必须排空节点，PDB、容量和本地数据可能影响排空 |
| 工作节点 | 升级 kubeadm，运行 `kubeadm upgrade node`，再按维护流程处理 kubelet | 不能假定控制平面升级会自动升级所有节点软件 |
| 收尾验证 | 检查节点、系统 Pod、CNI、DNS 与业务访问 | 节点 Ready 不能代替业务读写与备份验证 |

版本偏差也不是所有组件统一允许相差一个版本。一般规则包括 kubelet 不能新于 API server，kubectl 应在 API server 前后一个次版本范围内；多 API server 版本混用会进一步缩小兼容交集。精确限制应查[版本偏差策略](https://kubernetes.io/releases/version-skew-policy/)，并优先让 kubeadm、kubelet 与计划版本保持一致。

`kubeadm upgrade` 默认会更新它管理的部分证书，但这不等于自动更新所有外部证书，也不负责业务数据库的数据升级。把控制平面升级、节点维护、插件升级与业务验证分清，才能判断当前处于哪一步、还缺哪些确认。
