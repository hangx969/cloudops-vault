---
title: Kubernetes NodeSwap 配置与验证来源摘要
tags:
  - knowledgebase/source
  - kubernetes/memory
date: 2026-10-20
sources:
  - "[[Docker-Kubernetes/k8s-installation-management/k8s-NodeSwap-配置与验证]]"
aliases:
  - NodeSwap 来源摘要
  - Node Swap 来源摘要
---

# Kubernetes NodeSwap 配置与验证来源摘要

## 元信息

- **原始文档**：[[Docker-Kubernetes/k8s-installation-management/k8s-NodeSwap-配置与验证|Kubernetes NodeSwap：原理、k3s 配置与验证]]
- **外部来源**：[K8s 最佳实践已更新：请使用 Node Swap！](https://mp.weixin.qq.com/s/Njofe86YyLc3gMcNVHHLEQ?scene=1)
- **作者与发布日期**：东风微鸣，2026-10-17
- **领域**：Kubernetes 节点管理、Linux 内存与 cgroup v2
- **摄入日期**：2026-10-20

## 摘要

文章记录了作者在 4 台 N100、k3s `v1.36.5+k3s1` 的 Homelab 中，通过 kubelet drop-in 将 `NoSwap` 调整为 `LimitedSwap` 的过程。内容覆盖宿主机前置条件、两个 kubelet 配置项的职责、QoS 与 request/limit 边界、额度公式、逐节点上线和四项验证。整理稿保留原文 10 个代码块及全部实验输出，并单独补充官方资料核对，说明控制平面与存储建议的适用边界。

## 关键知识点

1. NodeSwap 在 Kubernetes v1.34 进入稳定阶段；默认 `NoSwap` 不允许容器使用 swap。
2. `failSwapOn: false` 允许 kubelet 在宿主机启用 swap 时启动；`memorySwap.swapBehavior: LimitedSwap` 才控制符合条件的容器是否获得 swap 额度。
3. 本文启用前提包括 cgroup v2 和已配置的宿主机 swap。原文建议本地 SSD 或 NVMe；官方关注实际承载 swap 的设备性能与 I/O 隔离。
4. `LimitedSwap` 面向 Burstable Pod，memory request 等于 limit 的容器可退出 swap；Guaranteed、BestEffort 和关键 Pod 不获得 swap 额度。
5. swap 额度按 `(containerMemoryRequest / nodeTotalMemory) × totalPodsSwapAvailable` 分配；调度器不将 swap 计入内存容量。
6. k3s 使用 `/var/lib/rancher/k3s/agent/etc/kubelet.conf.d/90-swap.conf` 覆盖默认值；保留 `00-k3s-defaults.conf`，文件后缀为 `.conf`，按字典序加载。
7. 验证需要分别检查 kubelet `configz`、节点 `.status.nodeInfo.swap.capacity`、`kubectl top nodes --show-swap` 和容器 `memory.swap.max`。
8. 官方建议控制平面不配置 swap，并建议使用加密 swap。作者逐台重启 master 的顺序是实验记录，不能直接推广为生产启用建议。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：kubelet 配置、QoS、节点内存与调度边界。
- [[KnowledgeBase/concepts/容器运行时|容器运行时]]：将 kubelet 的 swap 限制落实到容器 cgroup。
- [[KnowledgeBase/maps/kubernetes-map|Kubernetes 专题地图]]：安装与运维管理的阅读入口。

## 值得注意

- 单独设置 `failSwapOn: false`、节点已上报 swap 容量，或某次采样显示 `0Mi`，均不能替代容器额度检查。
- 原文提供 Burstable Pod 的 `memory.swap.max = 36200448` 和未设置 request/limit 的 Pod 的 `0` 两组输出，未展示 memory request 等于 limit 的实测结果。
- 原文没有成本、Pod 密度或性能的前后对比数据；相关收益保留为作者判断。
- 原始剪藏描述提到 Ansible，但正文没有提供 playbook 或自动化步骤；整理稿未据此补造实现。
