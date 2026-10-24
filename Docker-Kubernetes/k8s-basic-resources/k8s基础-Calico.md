---
title: K8s基础-Calico
tags:
  - kubernetes
  - k8s-basics
aliases:
  - k8sCalico
---

# K8s基础-Calico

同一节点上的两个 Pod 通了，并不代表跨节点网络已经配置正确。跨节点通信需要回答几个问题：Pod 地址由谁分配，节点如何知道目标 Pod 在哪里，底层网络是否能转发这个地址，以及哪些连接应被策略阻止。Calico 将地址管理、路由和网络策略结合起来，负责处理这些问题。

理解 Calico 前，建议先熟悉 Pod IP、节点 IP、CIDR、路由表和 CNI。本文先介绍组件分工，再解释 BGP、IPIP、VXLAN 的关系，最后给出安装配置的阅读方法。所有配置都应在实验集群中验证，现有集群切换封装方式可能中断连接。

## Calico 解决什么问题

Calico 是开源的网络和安全方案，可用于 Kubernetes、容器、虚拟机和主机。在 Kubernetes 中，它可以为 Pod 分配 IP，建立跨节点通信，并实现 NetworkPolicy 等网络访问控制。

“网络连通”和“允许访问”要分开检查：路由、封装和 MTU 决定数据包能否送达；网络策略决定某类流量是否被允许。多租户隔离也需要显式配置策略，安装插件本身不会自动生成符合业务要求的隔离规则。

### 组件及其分工

![image-20231023152017200](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310241222817.png)

这张图描述传统的 Calico 架构。部署方式和数据平面不同，实际启用的组件也会变化：

| 组件 | 主要职责 | 阅读配置时需要注意 |
| --- | --- | --- |
| Felix | 在每个节点配置接口、路由和策略，维护本机数据平面并上报状态 | 具体实现与所选 Linux 或 eBPF 数据平面有关 |
| 数据存储 | 保存 Calico 的配置、IP 地址分配等网络状态 | Kubernetes datastore 通过 Kubernetes API 保存资源；etcd datastore 才直接连接独立 etcd，二者不要混用 |
| BGP 客户端 / BIRD | 与其他节点或网络设备交换路由 | 使用传统 BGP 路由方案时启用；VXLAN-only 方案可以不运行 BGP |
| Route Reflector | 向 BGP 客户端反射路由，减少全互联会话数量 | 全互联的无向会话数是 N(N−1)/2，大规模时可采用一个或多个反射器 |

BGP 全互联让各节点直接交换 Pod 网段路由，但节点越多，会话数增长越快。Route Reflector 集中传播路由，业务数据包通常仍按路由直接发送，不需要经过反射器转发。`calico/node` 中 Felix、BIRD 和 confd 的职责可对照[官方组件配置说明](https://docs.tigera.io/calico/latest/reference/configure-calico-node)。

## 先分清路由与封装

BGP 是交换路由的协议，用来告诉节点“去哪个网段应走哪个下一跳”；IPIP 和 VXLAN 则是数据包封装方式，用来让底层网络只需识别节点地址。它们处在不同层面，因此可以组合。传统 Calico 的 IPIP 方案通常仍通过 BGP 分发路由。

BGP 是路径向量路由协议，既可以在自治系统之间运行，也可以用于集群内部的路由分发。运营商的多线路接入只是 BGP 的一种应用，不能用“多线单 IP”概括 Calico 中的作用。

| 方案 | 路由与传输方式 | 对底层网络的要求 |
| --- | --- | --- |
| 无封装路由 | Pod 数据包不额外封装；可用 BGP 向节点或上游分发 Pod 网段 | 底层网络和回程路径必须能正确路由 Pod 地址 |
| IPIP | 在原始 IPv4 包外再加 IPv4 头；传统方案通常结合 BGP | 节点间允许 IP 协议号 4，正确设置 MTU；仅支持 IPv4 |
| VXLAN | 通过 VXLAN 封装跨节点数据，Felix 可维护集群路由 | 节点间允许对应 UDP 端口；默认常用 4789，并检查 MTU |

封装的价值是减少底层对 Pod 网段的感知要求，不代表可以绕过节点间的防火墙或路由问题。VXLAN 的包头通常比 IPIP 更大，不能笼统断言其性能一定更好。选择时要结合云平台限制、网络可控程度、MTU 和实际负载，[官方封装说明](https://docs.tigera.io/calico/latest/networking/configuring/vxlan-ipip)也列出了 IPv4/IPv6 支持边界。

### 无封装是否要求节点二层互通

同一子网中的节点常可以直接将包交给目标节点，但“Calico 无封装只能在二层互通时使用”不成立。如果底层路由器学习了 Pod 网段，并具有正确的下一跳和回程路由，跨三层网络同样可以无封装通信。

BGP 会话建立只证明路由控制连接可用，不能证明业务数据面已经可达。遇到“路由看起来存在，Pod 却不通”，需要继续检查下一跳、底层路由、回程路径、源地址检查、安全组和网络策略。

### Always、CrossSubnet 和 Never

封装可以对所有跨节点流量启用，也可以只对跨子网流量启用：

- `Always`：跨节点的对应地址池流量使用封装。
- `CrossSubnet`：节点位于不同子网时封装，同一子网内可直接路由，减少封装开销。
- `Never`：不使用该类封装，需要由底层提供 Pod 地址路由能力。

这里的子网是节点网络的子网。跨子网封装同时要求 Calico 检测到正确的节点地址和子网掩码。IPIP 中常见的 `tunl0` 是隧道设备，不应据此推导“每节点必须额外申请一个虚拟节点 IP”。VXLAN 也会使用相应的隧道接口和地址，其具体分配由 Calico 管理。

## 读懂安装清单中的参数

本文沿用 manifest 安装方式解释参数。Operator 安装通过 `Installation` 等 API 管理配置，不应直接修改其生成的 DaemonSet。下面是 `calico-node` 容器的环境变量片段，不是可独立部署的完整资源：

```yaml
# 位于 DaemonSet.spec.template.spec.containers 中的 calico-node 容器下
# 镜像版本应来自与目标 Kubernetes 版本兼容的完整安装清单
name: calico-node
env:
- name: DATASTORE_TYPE
  value: "kubernetes"
- name: CLUSTER_TYPE
  value: "k8s,bgp"
- name: IP
  value: "autodetect"
- name: CALICO_IPV4POOL_CIDR
  value: "10.244.0.0/16"
- name: CALICO_IPV4POOL_IPIP
  value: "Always"
```

`DATASTORE_TYPE=kubernetes` 表示通过 Kubernetes API 保存配置；`CALICO_IPV4POOL_CIDR` 是默认 Pod 地址池，不能与节点、Service 或其他现有网络重叠。`CLUSTER_TYPE` 中的 `bgp` 是部署类型标识，不应把它当作单独的 BGP 开关。

这些 `CALICO_IPV4POOL_*` 环境变量主要控制首次创建的默认地址池。地址池已经存在后，仅修改环境变量或重启 DaemonSet 通常不会重配现有 IPPool，应检查实际 IPPool；参见[官方安装配置选项](https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/config-options)。

### 多网卡节点如何选择地址

`IP_AUTODETECTION_METHOD` 用于自动检测 Calico 使用的节点 IPv4 地址。多网卡主机上，可以按接口名称筛选：

```yaml
- name: IP_AUTODETECTION_METHOD
  value: "interface=ens33"
```

`interface=eth.*` 表示匹配名称符合该正则表达式的接口。接口名必须结合节点实际情况填写，不能把虚拟隧道或仅用于管理的接口误选成业务网络。

该参数选择的是节点地址，不是从 `ens33` 网卡给 Pod 分配 IP。Pod 地址通常由运行时调用 CNI 后，由 Calico IPAM 等地址管理插件分配。默认自动检测可用时无需手动指定，但多网卡、VPN 或复杂路由环境应按[节点地址自动检测说明](https://docs.tigera.io/calico/latest/networking/ipam/ip-autodetection)检查选择结果。

## 配置不同的封装方案

以下片段用于说明新安装的配置差异。不要在同一地址池同时开启 IPIP 和 VXLAN，也不要将它们未经评估应用到现有业务集群。manifest 与 Operator 的字段不同，例如环境变量关闭封装常用 `Never`，IPPool 则通过 `ipipMode` 和 `vxlanMode` 表达；不要照搬未经当前版本支持的 `Off` 值。

### IPIP：所有跨节点流量或只跨子网

在 manifest 的 `calico-node` 环境变量中设置：

~~~yaml
- name: CALICO_IPV4POOL_IPIP
  value: "CrossSubnet"
- name: CALICO_IPV4POOL_VXLAN
  value: "Never"
~~~

要让所有跨节点流量使用 IPIP，将 `CrossSubnet` 改为 `Always`。传统使用 BIRD 的安装还需保持 BGP 组件和相应探针有效。Azure 等不支持 IPIP 的环境应选择平台支持的封装方式。

现有地址池应检查 IPPool 的实际字段。以下是 IPIP 跨子网地址池的完整示例，CIDR 只是实验值，已有池不要重复创建或与之重叠：

~~~yaml
apiVersion: projectcalico.org/v3
kind: IPPool
metadata:
  name: ippool-ipip-cross-subnet
spec:
  cidr: 10.244.0.0/16
  ipipMode: CrossSubnet
  vxlanMode: Never
  natOutgoing: true
~~~

`natOutgoing` 控制离开 Calico 地址池的流量是否做出站 NAT，与跨节点是否封装是不同的配置。

### BGP 路由与无封装

如果计划使用传统 BGP 分发路由且不做封装，manifest 初始配置可写为：

~~~yaml
- name: CALICO_IPV4POOL_CIDR
  value: "10.244.0.0/16"
- name: CALICO_IPV4POOL_IPIP
  value: "Never"
- name: CALICO_IPV4POOL_VXLAN
  value: "Never"
- name: CALICO_NETWORKING_BACKEND
  value: "bird"
~~~

这只是选择后端与默认池行为，不能替代上游路由配置。还需要确认节点 BGP mesh 或显式 BGPPeer，以及底层对 Pod 网段的可达性。如果 IPIP 使用 `CrossSubnet`，它依然可以同时使用 BGP，只是数据面跨子网时会封装。

### VXLAN

VXLAN 必须配置 `CALICO_IPV4POOL_VXLAN`，不能只把 IPIP 参数改成 `CrossSubnet` 就宣称已启用 VXLAN：

~~~yaml
- name: CALICO_IPV4POOL_IPIP
  value: "Never"
- name: CALICO_IPV4POOL_VXLAN
  value: "CrossSubnet"
- name: CALICO_NETWORKING_BACKEND
  value: "vxlan"
~~~

`vxlan` 后端用于只需 VXLAN 的方案，会禁用 BIRD/BGP。如果原 manifest 的存活或就绪探针还检查 `-bird-live`、`-bird-ready`，需要按当前版本官方清单同步调整；否则关闭 BIRD 后探针仍会报错。只用 VXLAN 地址池时可以不运行 BGP，需要向外部通告路由时则另行设计。

Operator 安装可通过下面的 `Installation` 片段表达跨子网 VXLAN；它需要合并到与目标版本匹配的安装配置，不能当作现有集群的无影响切换命令：

~~~yaml
apiVersion: operator.tigera.io/v1
kind: Installation
metadata:
  name: default
spec:
  calicoNetwork:
    bgp: Disabled
    ipPools:
    - cidr: 10.244.0.0/16
      encapsulation: VXLANCrossSubnet
~~~

### 关于 host-gw

`host-gw` 是 Flannel 中常见的后端名称。Calico 的 `CALICO_NETWORKING_BACKEND` 支持的值包括 `bird`、`vxlan`、`none`，不存在可按 `hostgw` 启用的对应模式。若想让 Calico 使用节点作为下一跳直接路由，应评估前面的无封装方案，不要填写虚构的后端值。`none` 常用于只做策略等特定部署，也不是 host-gw 的替代写法。

## 安装与验证顺序

从[自管理集群安装文档](https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises#install-calico)选择与 Kubernetes、操作系统、内核匹配的版本，确定使用 Operator 还是 manifest。原先常见的 `calico/node:v3.18.0` 属于历史学习配置，不应作为新集群安装版本。

安装前，先确认 Pod CIDR、封装协议、防火墙、MTU 和多网卡地址选择；再下载固定版本的完整清单，核对镜像与权限后在实验环境部署。Calico 的节点组件通常由 DaemonSet 运行，不是单独创建一个普通 Deployment 就能完成网络安装。

验证应从本机到跨节点逐步扩大：

1. 检查 Calico Pod 是否就绪，节点地址和 IPPool 是否符合预期。
2. 检查同一节点的 Pod 通信，再验证不同节点、不同子网的 Pod 通信。
3. 验证 Service、DNS 和必要的出站访问，区分 CNI 问题与 Service 转发问题。
4. 对受策略保护的流量验证“应放行”和“应拒绝”两类结果。

若看到 `tunl0` 仍存在，不要立即卸载 `ipip` 模块。原本用于清理残留设备的 `rmmod ipip` 会影响仍依赖该模块的网络，只能在确认 Calico 已卸载、没有其他使用者且已安排网络维护时处理。

## 与其他网络插件对照

CNI 定义容器网络插件接口，不同插件的数据平面、策略能力和运维要求差异很大。不要只按“小集群用某插件、大集群用另一插件”选择。

| 插件 | 理解其定位时可关注的方面 |
| --- | --- |
| Flannel | 聚焦 Pod 网络连通，提供 VXLAN、host-gw 等后端；网络策略通常需要额外实现 |
| Calico | Pod 网络、地址管理与网络策略，可选择不同封装方式和数据平面 |
| Weave Net | 使用虚拟网络连接节点；评估前需另行确认项目维护状态和目标 Kubernetes 版本兼容性 |
| Cilium | 以 eBPF 为基础，提供网络、策略与可观测性能力，需核对内核和部署要求 |

排查 Calico 时，先明确自己选了什么数据平面、如何分发路由、是否封装，再沿着节点地址、路由、封装协议和策略逐项检查。相同的“Pod 不通”，在这几层对应的处理方法并不相同。
