---
title: Kubernetes NodeSwap：原理、k3s 配置与验证
source: "https://mp.weixin.qq.com/s/Njofe86YyLc3gMcNVHHLEQ?scene=1"
author:
  - 东风微鸣
published: 2026-10-17
created: 2026-10-20
date: 2026-10-20
description: 在 k3s 集群中通过 kubelet drop-in 启用 LimitedSwap，说明适用条件、QoS 边界、逐节点上线顺序及四项验证。
tags:
  - kubernetes
  - k3s
  - linux/swap
aliases:
  - K8s 最佳实践已更新：请使用 Node Swap！
  - Node Swap
---

# Kubernetes NodeSwap：原理、k3s 配置与验证

NodeSwap 允许 Kubernetes 工作负载在受控范围内使用节点的 swap。它在 Kubernetes v1.34 进入稳定阶段，但 kubelet 默认仍使用 `NoSwap`，需要显式配置才能让符合条件的容器使用 swap。

本文基于东风微鸣的 Homelab 实践整理。环境信息和命令输出均来自原作者；文末“官方资料核对”单独说明实验经验的适用边界。

## 适用条件与收益

原文建议在满足以下条件时启用 NodeSwap：

- Kubernetes v1.34 及以上版本。
- 节点系统盘使用本地 SSD 或 NVMe 高速存储。
- 节点使用 cgroup v2。

kubelet 的核心配置如下：

```yaml
failSwapOn: false
memorySwap:
  swapBehavior: LimitedSwap
```

作者将启用 swap 的收益归纳为：

- 降低内存成本：符合条件的工作负载可以在内存压力下换出空闲匿名页，提高 Pod 密度。
- 缓冲内存尖峰：为工作负载提供额外的缓冲，减少因内存压力触发 OOM 的机会。
- 配置改动少：本次实验的宿主机已启用 swap，swap 文件、分区和 `/etc/fstab` 均未改动，主要调整 kubelet 的 `swapBehavior`。
- 可以观测：通过 `node.status.nodeInfo.swap.capacity` 和 `kubectl top nodes --show-swap` 查看容量与使用量。

这些收益有明确边界：

- 只有符合条件的 Burstable Pod 中、内存 request 小于 limit 的容器能使用 swap；Guaranteed 工作负载不会因此获得 swap 额度。
- 调度器不感知 swap，容量规划仍以节点物理内存为准，不能将 swap 计入可调度内存。
- 匿名页换出会产生磁盘 I/O。原文不建议在系统盘不具备本地 SSD 或 NVMe 性能条件时启用。

原文将社区的常见建议概括为：用 swap 缓冲内存尖峰，容量规划仍按物理 RAM 计算。

## 实验环境与前置检查

作者使用的 Homelab 环境如下：

| 项目 | 配置 |
| --- | --- |
| 节点 | 4 台 N100 小主机 |
| 集群 | k3s `v1.36.5+k3s1` |
| cgroup | v2 |
| 宿主机 swap | `/swap.img`，实验前已通过 `swapon` 启用 |

开始前，逐项确认：

1. 检查 cgroup 版本：`stat -fc %T /sys/fs/cgroup` 应返回 `cgroup2fs`。
2. 检查宿主机 swap：`swapon --show` 应有输出。作者的环境使用 `/swap.img`；尚未启用 swap 的节点需要先完成宿主机配置。
3. 确认 k3s 对应的 Kubernetes 版本为 v1.34 或更高，包含稳定版 NodeSwap。

前置条件不满足时，仅修改 kubelet 配置无法完成启用。

## 两个 kubelet 配置项的区别

`memorySwap.swapBehavior` 的默认值是 `NoSwap`。在此模式下，即使宿主机启用了 swap，并设置了 `failSwapOn: false`，容器 cgroup 的 `memory.swap.max` 仍为 `0`。

| 配置项 | 控制内容 |
| --- | --- |
| `failSwapOn: false` | 允许 kubelet 在宿主机已启用 swap 时启动 |
| `memorySwap.swapBehavior: LimitedSwap` | 允许符合条件的容器使用受限的 swap 额度 |

> [!note] 两项配置分别控制启动与容器用量
> 仅设置 `failSwapOn: false` 不会给容器分配 swap。作者的宿主机 swap、分区和 `/etc/fstab` 已配置好，本次需要补上的是 kubelet 的 `LimitedSwap` 策略。

## LimitedSwap 的适用范围与额度

`LimitedSwap` 会按 Pod QoS、容器内存配置以及是否为关键 Pod 限制 swap 的使用范围：

- Pod 必须属于 Burstable QoS。
- 容器的 memory request 与 limit 必须不相等。
- Guaranteed 和 BestEffort Pod 不能使用 swap。
- 关键 Pod（`IsCriticalPod`）不能使用 swap，与 QoS 类别无关。

| Pod QoS | request vs limit | 能否用 swap |
| --- | --- | --- |
| Burstable | request != limit | 可以，使用 LimitedSwap |
| Burstable | request == limit | 不可以，使用 NoSwap |
| Guaranteed | request == limit | 不可以，使用 NoSwap |
| BestEffort | 都没设 | 不可以，使用 NoSwap |
| 任意 | IsCriticalPod | 不可以，使用 NoSwap |

容器可使用的 swap 额度按以下公式计算：

```text
containerSwapLimit = (containerMemoryRequest / nodeTotalMemory) × totalPodsSwapAvailable
```

request 越小，分配到的 swap 额度越小。这里的 `totalPodsSwapAvailable` 指节点上可供 Pod 使用的 swap 总量。

> [!important] swap 不参与调度容量计算
> 调度器仍按节点物理 RAM 和工作负载的 memory requests 调度。将 swap 当作额外 RAM 超卖，可能导致频繁换页和节点抖动。

## 在 k3s 中配置 kubelet

### 使用独立的 drop-in 文件

k3s 管理默认配置文件：

`/var/lib/rancher/k3s/agent/etc/kubelet.conf.d/00-k3s-defaults.conf`

原文说明该文件会在 k3s 启动时重写，因此自定义配置应放在同一目录的独立文件中。

drop-in 文件需要满足两个条件：

- 文件名以 `.conf` 结尾。
- 文件按字典序加载；覆盖默认值的文件应排在 `00-k3s-defaults.conf` 之后。

本例使用 `90-swap.conf`，完整路径为：

`/var/lib/rancher/k3s/agent/etc/kubelet.conf.d/90-swap.conf`

文件内容如下：

```yaml
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
failSwapOn: false
memorySwap:
  swapBehavior: LimitedSwap
```

显式写入 `failSwapOn: false`，避免依赖已有配置。保留 k3s 自己维护的 `00-k3s-defaults.conf`，不要覆盖或删除。

### 配置文件支持范围

[官方 k3s 配置文档](https://docs.k3s.io/installation/configuration#kubelet-configuration-files)说明，kubelet drop-in 配置文件的支持从 k3s v1.32 开始；本文 v1.34 及以上的适用范围已覆盖这一前提。配置文件和命令行参数混用时，还需要考虑参数优先级，最终以 kubelet 实际生效的配置为准。

## 逐节点上线

在 k3s 中，重启 kubelet 对应重启所在节点的 k3s 服务。作者的 Homelab 按以下顺序上线：

1. 先处理 worker 节点。
2. 再逐台处理 master（控制平面）节点。
3. 每处理一台，都确认 `kubectl get nodes` 显示全部节点 Ready，且 etcd 成员健康，再继续下一台。

避免同时重启多台 master，导致 etcd 失去维持 quorum 所需的成员数量。作者记录的操作过程没有重启节点，也没有主动驱逐 Pod。

> [!note] 控制平面的适用边界
> 上述顺序保留了作者的实验过程。官方建议控制平面不配置 swap，详见 [[#官方资料核对]]。

## 验证清单

验证应覆盖实际配置、节点容量、使用量和容器 cgroup 额度四个方面。以下输出为作者的实验记录。

### 1. 确认 kubelet 的实际配置

查询目标节点的 `configz`：

```bash
kubectl get --raw "/api/v1/nodes/<node>/proxy/configz" \
  | jq '.kubeletconfig | {failSwapOn, memorySwap}'
```

期望看到 `failSwapOn: false`，且 `memorySwap.swapBehavior == "LimitedSwap"`。

作者的输出：

```console
❯ kubectl get --raw "/api/v1/nodes/n100-cheshi-0/proxy/configz" | jq '.kubeletconfig | {failSwapOn, memorySwap}'
{
  "failSwapOn": false,
  "memorySwap": {
    "swapBehavior": "LimitedSwap"
  }
}
```

### 2. 确认节点上报 swap 容量

检查 `.status.nodeInfo.swap.capacity`：

```console
❯ kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.nodeInfo.swap.capacity}{"\n"}{end}'
n100-cheshi-0    8589930496
n100-jumper-0    4294963200
n100-jumper-1    4294963200
n100-jumper-2    4294963200
```

实验中的 4 台节点均有容量值。该字段缺失时需要进一步检查；在相关工具输出中，它可能表现为 `unknown`。

### 3. 确认 swap 使用量可见

检查最后两列 `SWAP(bytes)` 和 `SWAP(%)`：

```console
❯ kubectl top nodes --show-swap
NAME            CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)   SWAP(bytes)   SWAP(%)
n100-cheshi-0   671m         16%      11088Mi         35%         0Mi           0%
n100-jumper-0   853m         21%      8065Mi          53%         0Mi           0%
n100-jumper-1   759m         18%      6317Mi          41%         0Mi           0%
n100-jumper-2   466m         11%      7270Mi          47%         0Mi           0%
```

这里的 `0Mi` 是作者记录的当时使用量；容器是否获得 swap 额度，还需要检查下一项。

### 4. 确认容器 cgroup 的 swap 额度

进入容器查看 `memory.swap.max`：

```bash
kubectl exec <pod> -- cat /sys/fs/cgroup/memory.swap.max
```

对比以下情况：

- request 为 `64Mi`、limit 为 `256Mi` 的 Burstable Pod，预期 `memory.swap.max > 0`。
- memory request 等于 limit 的容器，以及 request/limit 均未设置的 BestEffort Pod，预期 `memory.swap.max == 0`。

作者记录的 Burstable Pod：

```console
cat /sys/fs/cgroup/memory.swap.max
36200448
```

作者记录的 request/limit 均未设置的 Pod：

```console
cat /sys/fs/cgroup/memory.swap.max
0
```

作者当时没有找到 memory request 等于 limit 的 Pod，因此原文未提供这类 Pod 的实测输出。上述记录验证了已展示的两类情况，不能视为所有边界条件都已实测。

## 官方资料核对

以下内容于 2026-10-20 对照官方资料补充，与上文的作者实验记录区分：

- **稳定版本与默认策略**：Kubernetes v1.34 发布说明确认 Linux 节点 swap 支持进入稳定阶段，默认仍为 `NoSwap`。[Kubernetes v1.34 发布说明](https://kubernetes.io/blog/2025/08/27/kubernetes-v1-34-release/#linux-node-swap-support)
- **控制平面**：官方建议控制平面不配置 swap，避免关键服务换页影响性能。原文对 master 的操作顺序属于 Homelab 经验，不应直接作为生产控制平面的启用建议。[控制平面与 swap](https://kubernetes.io/docs/concepts/cluster-administration/swap-memory-management/#swap-and-control-plane-nodes)
- **存储条件**：官方关注实际承载 swap 的存储性能及其与系统进程的 I/O 竞争；本地 SSD 或 NVMe 是原文提出的部署建议，并非 NodeSwap API 的硬性限定。官方同时建议使用加密 swap，并考虑独立设备或 I/O 优先级隔离。[swap 存储实践](https://kubernetes.io/docs/concepts/cluster-administration/swap-memory-management/#use-of-a-dedicated-disk-for-swap)
- **收益与验证范围**：原文没有提供成本、Pod 密度或性能的前后对比数据，也未展示 memory request 等于 limit 的实测结果。收益描述保留为作者的启用理由，命令输出保留为该实验环境的观测结果。

## 要点回顾

1. NodeSwap 在 Kubernetes v1.34 进入稳定阶段，但默认 `swapBehavior` 仍是 `NoSwap`；单独设置 `failSwapOn: false` 不会给容器分配 swap。
2. 宿主机 swap 和 kubelet 启动条件已满足时，启用容器 swap 的关键配置是 `memorySwap.swapBehavior: LimitedSwap`。
3. `LimitedSwap` 受 Burstable QoS、内存 request/limit 和关键 Pod 条件限制，额度按 request 占节点物理内存的比例计算。
4. k3s 可以通过 `.conf` drop-in 文件覆盖默认配置，文件名需排在 `00-k3s-defaults.conf` 之后；上线后仍需核对实际配置和容器额度。

## 参考资料

- [原文：K8s 最佳实践已更新：请使用 Node Swap！](https://mp.weixin.qq.com/s/Njofe86YyLc3gMcNVHHLEQ?scene=1)，东风微鸣，2026-10-17。
- [Kubernetes：Swap memory management](https://kubernetes.io/docs/concepts/cluster-administration/swap-memory-management/)
- [Kubernetes v1.34 发布说明：Linux node swap support](https://kubernetes.io/blog/2025/08/27/kubernetes-v1-34-release/#linux-node-swap-support)
- [k3s：Kubelet Configuration Files](https://docs.k3s.io/installation/configuration#kubelet-configuration-files)
- [Kubernetes：通过配置文件设置 kubelet 参数](https://kubernetes.io/docs/tasks/administer-cluster/kubelet-config-file/)
- [KEP-2400：Node memory swap support](https://github.com/kubernetes/enhancements/tree/master/keps/sig-node/2400-node-swap)
- [Kubelet 配置 API：memorySwap](https://kubernetes.io/docs/reference/config-api/kubelet-config.v1/)

## 相关笔记

- [[Docker-Kubernetes/k8s-installation-management/k8s-cgroup-v2深度解析-迁移实战与避坑指南|cgroup v2 原理与迁移]]
- [[Docker-Kubernetes/k8s-installation-management/k8s生产环境优化与最佳实践|Kubernetes 生产环境优化]]
- [[KnowledgeBase/sources/k8s-node-swap-summary|NodeSwap 来源摘要]]
- [[KnowledgeBase/maps/kubernetes-map|Kubernetes 专题地图]]
