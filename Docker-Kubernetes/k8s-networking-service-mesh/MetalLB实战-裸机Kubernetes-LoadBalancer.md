---
title: MetalLB 实战：裸机 Kubernetes 的 LoadBalancer 配置与原理
source: "https://mp.weixin.qq.com/s/lZyjNKiWxTSFE9nWM1pAtg"
author:
  - L WH 泪无痕
published: 2026-09-06
created: 2026-10-20
date: 2026-10-20
description: MetalLB 的安装、Layer2 与 BGP 配置、多地址池选址、组件分工及故障切换边界。
tags:
  - kubernetes/networking
  - kubernetes/loadbalancer
  - metallb
aliases:
  - MetalLB 实战指南：让裸机 Kubernetes 也能像云上一样使用 LoadBalancer
  - MetalLB 简明教程
---

# MetalLB 实战：裸机 Kubernetes 的 LoadBalancer 配置与原理

MetalLB 为裸机 Kubernetes 集群提供 `type: LoadBalancer` Service 的外部 IP 分配和宣告能力。基本流程是：安装组件，用 `IPAddressPool` 定义可用地址，再用 `L2Advertisement` 或 `BGPAdvertisement` 宣告这些地址。

Layer2 通过 ARP（IPv4）或 NDP（IPv6）将流量引向一个入口节点；BGP 则与上游路由器交换路由，在路由器支持并配置 ECMP 时将流量分散到多个节点。本文先完成安装和 nginx 访问验证，再解释两种模式的机制、限制及选型条件。

> [!note] 版本与示例范围
> 本文根据原文整理，安装示例固定为官方安装文档列出的 `v0.16.1`，核对日期为 2026-10-20。原文采用的 `v0.13.2+` CRD 配置方式继续保留；原文的“最新版本为 0.16.x（2025 年）”不作为版本依据。以下命令和 YAML 已恢复剪藏时丢失的换行，尚未在实际集群部署验证。升级或更换版本前应阅读对应的 [Release Notes](https://metallb.io/release-notes/)。

## 一、背景：裸机集群为什么缺少 LoadBalancer

在接入云负载均衡控制器的 Kubernetes 集群中，创建 `type: LoadBalancer` Service 后，控制器会调用云平台的接口分配外部 IP 并配置负载均衡器。自建机房或本地虚拟机中的集群，如果没有相应实现，Service 的 `EXTERNAL-IP` 就会一直显示 `<pending>`。

常见的替代方式有：

- NodePort：通过 `节点IP:NodePort` 访问服务，通常使用高位端口；域名、TLS 和外部入口还需另行配置。
- `externalIPs`：手工规划外部 IP，并自行保证流量能够到达节点；Kubernetes 不会为这些地址自动提供分配和故障转移机制。

MetalLB 使用标准网络协议宣告虚拟 IP（VIP）：Layer2 模式使用 ARP / NDP，BGP 模式使用边界网关协议（Border Gateway Protocol）。地址分配与对外宣告结合后，裸机集群也能通过 LoadBalancer Service 暴露应用。

> [!warning] 地址池必须提前规划
> 地址池应使用所属网络中未被 DHCP 或静态配置占用的地址，并避免与其他地址池、节点及其他设备冲突。MetalLB 不会替你探测外部 IP 冲突；重复分配可能造成间歇性丢包，且难以仅从 MetalLB 日志定位。

## 二、快速开始：安装与配置

### 2.1 前置条件

| 条件 | 要求与说明 |
| --- | --- |
| Kubernetes | 官方主页仍列出 `1.13.0+` 这一通用前提；它不能替代所选 MetalLB 发行版的兼容性核查，不能据此认定本文 `v0.16.1` 示例可直接用于所有旧集群。 |
| MetalLB 配置方式 | 本文使用 `v0.13.2+` 的 CRD 配置；旧的 `metallb-system/config` ConfigMap 不再是本文的配置入口。 |
| CNI | Flannel、Cilium 等在官方兼容列表中；Calico 大部分场景可用，但需要检查 BGP 会话冲突，见 7.3。 |
| 可用地址段 | 为 MetalLB 预留空闲 IPv4 / IPv6 地址。Layer2 的 VIP 应在入口节点可响应 ARP / NDP 的二层网络中；BGP 地址池需要上游路由可达，不必与节点处于同一子网。 |
| Layer2 节点通信 | 节点间允许 `7946/TCP` 和 `7946/UDP`，供 memberlist 交换成员状态与故障检测信息。 |
| BGP 网络设备 | 需要可管理且支持 BGP 的路由器或交换机，并配置与节点的 BGP 邻居；多路径分流还需要设备支持并启用 ECMP。 |

版本和网络要求参见 [官方前置条件](https://metallb.io/#requirements)及 [Network Addon Compatibility](https://metallb.io/installation/network-addons/)。CRD 配置的发布边界参见 [v0.13.2 发布说明](https://metallb.io/release-notes/#version-0132)。

### 2.2 仅在 kube-proxy IPVS 模式下开启 strictARP

如果 kube-proxy 运行在 IPVS 模式，需要开启 `strictARP: true`。IPVS 使用的 `kube-ipvs0` 虚拟接口可能影响节点的 ARP 应答；严格 ARP 配置可避免节点错误响应由 MetalLB 管理的 VIP。

iptables / nftables 模式不需要为此修改 IPVS 配置。`strictARP` 属于 IPVS 配置项，不能把原文“其他模式没有这个参数”理解为整个 kube-proxy 配置 API 中不存在该字段。官方步骤见 [安装准备](https://metallb.io/installation/#preparation)。

1. 在能够管理集群的终端编辑 kube-proxy ConfigMap，无需在每个控制平面节点重复编辑：

   ```bash
   kubectl edit configmap -n kube-system kube-proxy
   ```

2. 在 ConfigMap 内的 `KubeProxyConfiguration` 中修改相应字段。下面是配置内容片段，不是独立的 ConfigMap 清单：

   ```yaml
   apiVersion: kubeproxy.config.k8s.io/v1alpha1
   kind: KubeProxyConfiguration
   mode: "ipvs"
   ipvs:
     strictARP: true
   ```

3. 保存后滚动重启 kube-proxy，使配置生效：

   ```bash
   kubectl rollout restart -n kube-system daemonset kube-proxy
   ```

### 2.3 安装 MetalLB

官方提供 manifest、Kustomize 和 Helm 三种安装方式，下面沿用 manifest 方式。按所需后端选择一条安装命令，三种 manifest 不要重复安装。

| 后端 | 能力与适用情况 |
| --- | --- |
| Native | 内置原生 BGP 实现，适用于仅 Layer2 或基础 BGP 场景；不支持 BFD 和 IPv6 BGP。 |
| FRR-K8s | 官方推荐的 BGP 后端，支持 BFD、IPv6，以及合并兼容的额外 FRR 配置；也可使用 Layer2。 |
| FRR | 直接配置 FRR 的旧后端，官方已标记弃用，应规划迁移到 FRR-K8s。 |

原文将 Native 写成“仅支持 L2”，这里按 [官方安装文档](https://metallb.io/installation/)校正，同时补齐缺失的版本路径。

```bash
# 选择一：Native 后端
kubectl apply -f \
  https://raw.githubusercontent.com/metallb/metallb/v0.16.1/config/manifests/metallb-native.yaml

# 选择二：FRR-K8s 后端
kubectl apply -f \
  https://raw.githubusercontent.com/metallb/metallb/v0.16.1/config/manifests/metallb-frr-k8s.yaml

# 选择三：FRR 旧后端，仅供识别既有部署
kubectl apply -f \
  https://raw.githubusercontent.com/metallb/metallb/v0.16.1/config/manifests/metallb-frr.yaml
```

安装后会创建 `metallb-system` 命名空间，核心组件包括 controller Deployment 和 speaker DaemonSet。FRR-K8s 后端还会部署相应的 FRR-K8s 组件。

创建自定义资源前，先等待组件就绪。验证 webhook 由 controller 提供，组件启动期间立即提交配置可能报 `Failed calling webhook`。

```bash
kubectl wait --for=condition=Ready -n metallb-system pod --all
```

该命令可作为启动检查；若创建 CR 时仍出现 webhook 错误，还应检查 controller 和 webhook 的实际状态，不能只凭一次 Pod Ready 判断配置已可用。

### 2.4 Layer2 配置：地址池与二层宣告

首次验证可以从不依赖 BGP 路由器的 Layer2 开始。以下 Layer2、生产地址池和 BGP 地址池示例用于说明不同配置，地址范围有重叠，不能全部同时应用。

#### 第 1 步：创建 IPAddressPool

多个 `IPAddressPool` 可以共存，地址支持 CIDR、起止范围或单个 IP，IPv4 / IPv6 均可。将下面的最小地址池保存为 `ipaddresspool.yaml`：

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: first-pool
  namespace: metallb-system
spec:
  addresses:
    - 192.168.1.240-192.168.1.250 # 替换为实际网段中的空闲 IP
```

生产规划也可以使用带注释的 CIDR 配置。以下 `prod-pool` 是上面地址池的替代示例：

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: prod-pool
  namespace: metallb-system
spec:
  addresses:
    - 192.168.1.240/29 # 记录网段归属，便于审计
  avoidBuggyIPs: true # 跳过以 .0 和 .255 结尾的地址，兼容部分旧设备
```

`avoidBuggyIPs` 针对部分旧设备的 smurf 防护误拦，不负责检测地址冲突。参见 [Advanced AddressPool Configuration](https://metallb.io/configuration/_advanced_ipaddresspool_configuration/)。

#### 第 2 步：创建 L2Advertisement

将下面的宣告配置保存为 `l2advertisement.yaml`，关联 `first-pool`：

```yaml
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: l2-advert
  namespace: metallb-system
spec:
  ipAddressPools:
    - first-pool
```

```bash
kubectl apply -f ipaddresspool.yaml -f l2advertisement.yaml
```

如果使用 `prod-pool`，应将 `ipAddressPools` 中的名称一并改为 `prod-pool`。不指定 `ipAddressPools` 时，L2Advertisement 默认适用于所有地址池。

Layer2 不需要把 VIP 真正绑定到节点网卡上；speaker 通过应答局域网中的 ARP / NDP 请求，让发往 VIP 的流量到达对应节点。

### 2.5 BGP 配置：邻居、地址池与路由宣告

BGP 模式需要与路由器或交换机建立邻居会话。下面三个对象可用 `---` 分隔，保存为同一个 `metallb-bgp.yaml` 后应用。

#### 第 1 步：创建 BGPPeer

每个需要对接的路由器配置一个 `BGPPeer`。注意区分本集群 ASN 和路由器 ASN：

```yaml
apiVersion: metallb.io/v1beta2
kind: BGPPeer
metadata:
  name: my-router
  namespace: metallb-system
spec:
  myASN: 64500 # 本集群 ASN
  peerASN: 64501 # 路由器 ASN
  peerAddress: 10.0.0.1 # 路由器 IP
```

#### 第 2 步：创建 IPAddressPool

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: bgp-pool
  namespace: metallb-system
spec:
  addresses:
    - 192.168.1.240-192.168.1.250
```

#### 第 3 步：创建 BGPAdvertisement

```yaml
apiVersion: metallb.io/v1beta1
kind: BGPAdvertisement
metadata:
  name: bgp-advert
  namespace: metallb-system
spec:
  ipAddressPools:
    - bgp-pool
```

```bash
kubectl apply -f metallb-bgp.yaml
```

BGP 宣告使用 `BGPAdvertisement`，不是 `L2Advertisement`。不指定 `ipAddressPools` 时，默认关联所有地址池；也可以通过标签选择器筛选地址池。配置结构参见 [官方配置说明](https://metallb.io/configuration/)。

使用 FRR-K8s 后端完成这类基础宣告时，不需要额外手写 FRR 配置文件。BFD、community 等高级功能分别通过 `BFDProfile`、`Community` 等 CR 配置。

## 三、实战验证：部署 nginx 并通过 VIP 访问

下面按“部署应用 → 创建 Service → 检查地址分配 → 从外部访问”的顺序验证。清单中的 nginx 镜像沿用原文的 `nginx:1.25`，实际部署时应按自己的镜像维护策略选择版本。

### 3.1 创建 nginx Deployment

保存为 `nginx-deploy.yaml`，在 `default` 命名空间应用：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.25
          ports:
            - containerPort: 80
```

```bash
kubectl apply -n default -f nginx-deploy.yaml
```

### 3.2 创建 LoadBalancer Service

保存为 `nginx-svc.yaml`：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
```

```bash
kubectl apply -n default -f nginx-svc.yaml
```

### 3.3 确认 EXTERNAL-IP 已分配

```bash
kubectl get svc nginx -n default
```

原文给出的示例输出如下，实际分配地址和 NodePort 可能不同：

```text
NAME    TYPE           CLUSTER-IP       EXTERNAL-IP     PORT(S)        AGE
nginx   LoadBalancer   10.103.240.239   192.168.1.241   80:30164/TCP   5s
```

`EXTERNAL-IP` 从 `<pending>` 变成地址池中的 IP，说明地址已经分配；它还不能单独证明外部网络和后端应用均可用。

### 3.4 从集群外部访问

先在与入口节点处于同一二层网络的主机上验证，避免把跨网段路由问题混入首次测试：

```bash
curl http://192.168.1.241
```

返回 nginx 默认欢迎页，才说明这一访问路径上的入口和后端应用能够工作。在使用 kube-proxy 的 Layer2 示例中，流量路径为：

```text
客户端通过 ARP 找到 VIP 对应的节点 MAC
    → 流量到达宣告 VIP 的节点
    → kube-proxy 转发
    → nginx Pod
```

> [!note] 跨网段访问的条件
> ARP / NDP 的解析发生在 VIP 所在的二层网络内，但客户端可以经过已配置的三层网关到达该网络。Layer2 本身不会向上游发布路由，跨网段访问需要网络中已有或额外配置的路由；不能把它概括成“Layer2 完全不支持跨子网”或“客户端必须与节点同网段”。这是根据 [Layer2 工作机制](https://metallb.io/concepts/layer2/)作出的网络路径判断。

## 四、多地址池：按 Service 选择地址段

不同业务可以使用不同地址池，例如内部地址使用 `10.0.x`，外部入口地址使用 `192.168.x`。地址池名称用于分配策略，实际可达范围仍取决于网络配置。

### 4.1 创建内部和外部地址池

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: internal-pool
  namespace: metallb-system
spec:
  addresses:
    - 10.0.0.100-10.0.0.200
---
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: external-pool
  namespace: metallb-system
spec:
  addresses:
    - 192.168.1.100-192.168.1.150
```

这些地址池还需要适用的 L2Advertisement 或 BGPAdvertisement 才会被宣告。如果沿用前面只关联 `first-pool` 的 L2Advertisement，应按实际网络调整关联范围；仅创建新地址池不会自动扩展它。

### 4.2 通过 Service 注解指定地址池

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-external
  annotations:
    metallb.io/address-pool: external-pool
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
```

`nginx-external` 会请求从 `external-pool` 分配地址。未指定池的 Service 则按地址池的自动分配条件、选择器和优先级选择，不能依赖 YAML 顺序或所谓“第一个可用池”；同优先级池之间的选择可以是随机的。参见 [地址池分配规则](https://metallb.io/configuration/_advanced_ipaddresspool_configuration/)。

## 五、组件分工：controller 分配 IP，speaker 宣告 IP

```text
创建 type: LoadBalancer Service
              │
              ▼
        Kubernetes API
          │         │
          ▼         ▼
     controller    speaker
     Deployment    DaemonSet
          │         │
     分配/回收 VIP   对外宣告 VIP
          │         ├─ Layer2：ARP / NDP
          ▼         └─ BGP：路由更新
写入 Service status       │
                          ▼
                    流量到达节点
                          │
                          ▼
                    kube-proxy → Pod
```

- controller：负责集群级 IP 地址管理（IPAM）。它监听 LoadBalancer Service，从 IPAddressPool 分配地址，写入 `.status.loadBalancer.ingress[].ip`；Service 删除时回收相应分配。
- speaker：通常以 DaemonSet 部署在节点上，负责 VIP 的网络宣告。Layer2 模式下应答 ARP / NDP，BGP 模式下由所选后端向邻居发布路由。使用 FRR-K8s 时，BGP 会话由 FRR-K8s / FRR 承载。
- 节点数据面：收到业务流量后，由 kube-proxy 或相应 Service 数据面送往后端 Pod。controller 和 speaker 的分工也是排障边界：先分清是“没有分到 IP”，还是“已分 IP 但流量未到达”。

ARP（Address Resolution Protocol）在 IPv4 网络中根据 IP 解析 MAC 地址；NDP（Neighbor Discovery Protocol）是 IPv6 的邻居发现协议，基于 ICMPv6。

## 六、Layer2 模式：工作原理与局限

### 6.1 每个 VIP 由一个节点宣告

Layer2 下，同一时刻，一个 Service VIP 由一个候选节点上的 speaker 宣告。该节点应答 VIP 的 ARP / NDP 请求，让网络设备把发往 VIP 的流量交给它，再由节点上的 Service 数据面转发到后端 Pod。

```text
客户端：“192.168.1.241 对应哪个 MAC？”
                 │
                 │ ARP 广播
                 ▼
        node-A       node-B       node-C
        leader       speaker      speaker
                 ▲
         仅 node-A 为该 VIP 应答
                 │
                 ▼
    发往该 VIP 的流量进入 node-A
                 │
                 ▼
           kube-proxy → Pod
```

这里的 leader 是针对某个 VIP 而言，不代表所有 Service VIP 都必须由同一节点宣告。

memberlist 用于获知成员状态和检测故障；宣告节点的选择是无状态计算：speaker 根据候选节点与 VIP 的哈希排序，决定由谁宣告。原文“通过 memberlist 选主”省略了这一层分工。参见 [Layer2 选举机制](https://metallb.io/concepts/layer2/#how-the-l2-leader-election-works)。

### 6.2 单节点入口带宽

一个 VIP 的外部流量先进入同一节点，所以其入口吞吐受该节点网卡和处理能力限制。增加后端 Pod 不会自动增加这个 VIP 的入口带宽。

Layer2 的入口机制提供的是故障接管能力；节点收到流量后的 Pod 分流仍由 Kubernetes 的 Service 数据面完成。

### 6.3 故障接管与邻居缓存

宣告节点故障后，其余 speaker 通过 memberlist 检测成员变化，按新的候选集合决定宣告节点。新节点发送 gratuitous ARP 或 unsolicited NDP，促使邻居缓存更新。

```text
原宣告节点故障
    ↓
memberlist 检测成员变化
    ↓
按新的候选集合确定宣告节点
    ↓
新节点发送 gratuitous ARP / unsolicited NDP
    ↓
网络设备和客户端更新邻居缓存
    ↓
后续流量到达新节点
```

多数系统能正确处理主动邻居通告，通常在数秒内切换；不正确处理通告的旧系统可能等待缓存自然过期，时间更长。原文写的“通常不超过 10 秒”“≤ 10 秒”不是官方保证，不能作为可用性承诺。

在有计划的切换中，可在更换宣告节点后让旧节点继续运行几分钟，继续转发仍使用旧缓存的流量。这不适用于已经宕机的节点。参见 [Layer2 限制与缓解方式](https://metallb.io/concepts/layer2/#limitations)。

## 七、BGP 模式：多节点宣告与 ECMP

### 7.1 路由器按连接选择入口节点

BGP 模式下，符合宣告条件的节点通过 BGP 向上游路由器发布 VIP 路由。路由器学到通往同一 VIP 的多条等价路径后，可以通过 ECMP（Equal-Cost Multi-Path，等价多路径）分散流量。

```text
             上游路由器 / 交换机
                 BGP peer
              │      │      │
         BGP 会话 BGP 会话 BGP 会话
              │      │      │
              ▼      ▼      ▼
           node-A  node-B  node-C
              └──────┼──────┘
                     │
              路由器按 ECMP 哈希
              将连接分到不同节点
```

具体策略由路由器决定，常见的 per-flow 哈希字段包括：

- 三元组：协议、源 IP、目的 IP。
- 五元组：协议、源 IP、目的 IP、源端口、目的端口。

在路径集合稳定时，同一连接通常进入同一节点，减少包乱序。相比单 VIP 的 Layer2 单节点入口，BGP 配合 ECMP 可以利用多个节点的入口能力。

### 7.2 节点变动可能中断已有连接

节点故障或缩容会撤回相应路径，该路径上的连接可能中断。ECMP 的路径集合变化还可能触发重新哈希，把其他已有连接映射到不持有原连接状态的节点。

例如，一个连接原先发往 node-A。增加或移除一个下一跳后，后续报文可能被分到 node-B；node-B 不掌握原有连接状态，客户端就可能遇到请求失败或 `Connection reset by peer`。BGP 的多节点分流能力不保证扩缩容过程中的连接无损迁移。

可以采取以下缓解措施：

1. 在路由器支持时使用 resilient ECMP / resilient LAG 等更稳定的哈希算法，减少受影响连接。
2. 减少不必要的入口节点变动。
3. 将必要变更安排在低峰期。
4. 由上层 Ingress 或应用按业务条件提供重试。

这些措施只能降低影响，不能消除所有断连。节点下线和重新哈希的具体行为参见 [BGP 模式限制](https://metallb.io/concepts/bgp/#limitations)。

### 7.3 Calico BGP 共存：明确由谁宣告 LoadBalancer 路由

Calico 与 MetalLB 如果从同一节点向同一个上游邻居各自建立冲突的 BGP 会话，就可能无法同时正常工作。不能把问题简化为“Calico 使用 BGP 就一定不能装 MetalLB”。

[官方 Calico 集成说明](https://metallb.io/configuration/calico/)给出了一种分工方式：Calico 3.18 起支持宣告 LoadBalancer 地址，MetalLB controller 负责分配 IP；此时创建 IPAddressPool，但不创建 MetalLB 的 BGPAdvertisement，由 Calico 通过 `serviceLoadBalancerIPs` 宣告规划的地址范围。

FRR-K8s 可以合并遵循其兼容规则的 FRRConfiguration，但不会自动接管 Calico 的既有 BGP 会话。原文“换成 FRR-K8s 即可合并 Calico 会话”的建议不能直接照用。参见 [FRR-K8s 配置合并说明](https://metallb.io/configuration/_advanced_bgp_configuration/#configuring-with-frr-k8s)。

其他选择包括按网络设计拆分邻居或使用 VRF；若考虑将 Calico 改为非 BGP 模式，也需要先评估 Pod 网络和路由的影响，不能只为安装 MetalLB 直接切换现有 CNI。

## 八、模式选型与环境适配

### 8.1 选型步骤

1. 确认是否有可管理的 BGP 路由器，以及多节点入口和 ECMP 分流的需求。条件具备时评估 BGP。
2. 如果先做本地验证、规模较小，或不准备改动上游 BGP，可从 Layer2 开始。
3. 如果 Calico 已向上游宣告路由，先确定由 Calico 还是 MetalLB 宣告 LoadBalancer 地址，再处理邻居关系。

```text
需要为裸机 Service 提供 LoadBalancer
    │
    ├─ 有可管理的 BGP 网络，并需要多节点入口？
    │    ├─ 是 → 评估 BGP + ECMP
    │    └─ 否 → 评估 Layer2 单 VIP 单节点入口
    │
    └─ Calico 已运行 BGP？
         └─ 先确定路由宣告职责与邻居关系
              ├─ MetalLB 分配 IP，Calico 宣告
              └─ 或按网络设计拆分 BGP 会话
```

Layer2 部署简单，但需要接受单 VIP 的入口带宽和故障接管限制；BGP 能利用多节点入口，但增加了路由配置和连接变动的管理成本。生产环境应按这些条件选择，不能仅凭“能用 BGP 就用 BGP”判断。

### 8.2 能力与故障表现对比

| 维度 | Layer2 | BGP |
| --- | --- | --- |
| 单 VIP 入口 | 同一时刻由一个节点宣告并接收流量 | 可由多个符合条件的节点宣告，路由器用 ECMP 分流 |
| 网络配置 | 不要求配置 BGP；需要可用的二层网络与正常的 ARP / NDP | 需要 BGP 邻居、路由传播和相应的 ECMP 配置 |
| 故障切换 | 通常数秒，受故障检测及邻居缓存影响，没有统一的 10 秒上限 | 路由收敛和 ECMP 重新哈希可能中断已有连接 |
| 跨网段访问 | 需由已有或额外配置的三层路由到达 VIP 所在网络 | 通过 BGP 发布路由实现可达，仍取决于上游网络配置 |
| 常见场景 | 测试、小规模集群，或能够接受单节点入口的环境 | 需要多节点入口、能够管理 BGP 网络的环境 |

| 条件变化 | 可能出现的退化 | 判断与处理方向 |
| --- | --- | --- |
| 单 Service 带宽持续上升 | Layer2 入口达到单节点网卡或处理能力上限 | 仅扩 Pod 无法增加入口带宽，可评估 BGP + ECMP |
| Layer2 宣告节点故障 | 检测和邻居缓存更新期间 VIP 短暂不可达 | 验证实际接管时间及客户端缓存行为 |
| 增加或移除 BGP 下一跳 | ECMP 重新哈希，已有连接可能中断 | 评估 resilient ECMP、低峰变更和上层重试 |
| BGP 节点下线或缩容 | 对应路径消失，相关连接受影响 | 同时检查路由收敛和连接恢复 |
| 客户端位于其他子网，且没有通往 VIP 的路由 | Layer2 宣告无法替代缺失的三层路由，访问失败 | 检查网关路由；按网络设计补路由或使用 BGP |

### 8.3 跨环境适配

| 环境 | 适用情况 | 差异与处理 |
| --- | --- | --- |
| 自建机房物理网络 | 可使用 Layer2 或 BGP | 根据地址规划、二层范围和上游设备能力选择。 |
| OpenStack 等虚拟化平台 | 取决于虚拟网络配置 | 端口安全或防欺骗规则可能拦截 VIP 流量，需要按平台配置允许的地址或端口策略。 |
| 公有云 VPC | 多数不能直接套用裸机方案 | 底层网络通常不接受来宾自行宣告的 ARP / BGP；先核对平台支持情况，通常使用云厂商的负载均衡服务。 |
| K3s | 需处理内置 ServiceLB | 按官方集成方式，用 `--disable servicelb` 禁用内置 ServiceLB，避免两个实现同时管理 LoadBalancer Service。 |

环境边界参见 [Cloud Compatibility](https://metallb.io/installation/clouds/)及 [Issues with K3s](https://metallb.io/configuration/k3s/)。

### 8.4 替代或互补方案

- kube-vip：提供 VIP 和 LoadBalancer 能力，支持 ARP / BGP，也常用于 Kubernetes 控制面高可用。
- Cilium LB-IPAM：如果已经使用 Cilium，可用其 IPAM 能力分配 LoadBalancer 地址。地址分配与宣告是不同职责，还需配合 L2 Announcements 或 BGP Control Plane 等能力使地址可达，不能仅创建地址池就认定入口已经可用。参见 [Cilium LB-IPAM](https://docs.cilium.io/en/stable/network/lb-ipam/)。

## 相关笔记与参考资料

- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-Service|Kubernetes Service]]：Service 类型、端口和后端选择。
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-Calico|Calico 网络]]：Pod 网络、BGP 与网络模式。
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx|Ingress-Nginx]]：七层入口部署。
- [[KnowledgeBase/concepts/高可用架构|高可用架构]]：冗余、故障检测与接管。
- [[KnowledgeBase/sources/metallb-loadbalancer-summary|本文来源摘要]]。
- [原文：MetalLB 实战指南](https://mp.weixin.qq.com/s/lZyjNKiWxTSFE9nWM1pAtg)，L WH 泪无痕，2026-09-06。
- [MetalLB Installation](https://metallb.io/installation/)。
- [MetalLB Configuration](https://metallb.io/configuration/)。
- [MetalLB Layer2 Concepts](https://metallb.io/concepts/layer2/)。
- [MetalLB BGP Concepts](https://metallb.io/concepts/bgp/)。
- [MetalLB Release Notes](https://metallb.io/release-notes/)。
