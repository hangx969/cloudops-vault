---
title: MetalLB 裸机 LoadBalancer 实战来源摘要
tags:
  - knowledgebase/source
  - kubernetes/networking
  - kubernetes/loadbalancer
date: 2026-10-20
aliases:
  - MetalLB 实战摘要
---

# MetalLB 裸机 LoadBalancer 实战

## 元信息

- **原始文档**：[[Docker-Kubernetes/k8s-networking-service-mesh/MetalLB实战-裸机Kubernetes-LoadBalancer]]
- **外部来源**：[MetalLB 实战指南](https://mp.weixin.qq.com/s/lZyjNKiWxTSFE9nWM1pAtg)，L WH 泪无痕，2026-09-06。
- **领域**：Kubernetes 网络、裸机 LoadBalancer、ARP / NDP、BGP。
- **摄入日期**：2026-10-20。

## 摘要

本文从裸机集群 LoadBalancer Service 长期处于 `<pending>` 的问题出发，介绍 MetalLB 的 IP 分配与网络宣告职责。内容包括 IPVS 的 strictARP 配置、三种安装后端、Layer2 / BGP 配置、nginx 外部访问验证和多地址池选址，并解释单节点入口、故障接管、ECMP 重新哈希及 Calico BGP 共存条件。整理版保留原文的完整配置与操作流程，恢复了剪藏时丢失的代码换行，并按官方文档校正版本和网络边界。

## 关键知识点

1. controller 从 IPAddressPool 分配 VIP，speaker 负责宣告；分配成功和业务流量可达应分别验证。
2. Layer2 对每个 VIP 选择一个宣告节点，应答 ARP / NDP。入口受单节点能力限制，故障切换依赖成员检测和邻居缓存，不能承诺统一的 10 秒上限。
3. BGP 配合上游 ECMP 可以使用多个入口节点，但下一跳变化可能重新映射已有连接，需要评估稳定哈希、变更窗口和上层重试。
4. Native 后端支持基础 BGP；FRR-K8s 支持 BFD、IPv6 和兼容配置合并；直接配置 FRR 的旧后端已被官方标记弃用。
5. IPVS 模式需开启 strictARP；地址池必须避开其他设备和 DHCP 分配范围，MetalLB 不负责探测外部地址冲突。
6. Service 可用 `metallb.io/address-pool` 注解选择地址池；新地址池还要有适用的宣告，默认分配不保证按清单顺序选择。
7. Calico 3.18 起可与 MetalLB 分工：controller 分配 IP，Calico 宣告 LoadBalancer 地址；切换 FRR-K8s 不会自动合并 Calico 的现有会话。
8. Layer2 不建立跨网段路由；客户端经已配置的网关也能访问 VIP。虚拟化端口安全、公有云网络约束和 K3s 内置 ServiceLB 需要分别处理。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kubernetes]]：Service、控制器及节点数据面。
- [[KnowledgeBase/entities/Calico]]：BGP 邻居冲突与路由宣告分工。
- [[KnowledgeBase/concepts/高可用架构]]：VIP 故障接管与连接恢复的区别。

## 值得注意

- 安装清单固定为官方文档列出的 `v0.16.1`；原文的旧版本年份和空版本 URL 已校正，部署前仍需核对所选发行版与集群的兼容性。
- 原文将 Native 写成仅支持 Layer2、将 FRR-K8s 描述为可自动解决 Calico 会话冲突，并把 Layer2 跨子网访问与切换时间写成绝对限制；整理版按官方资料说明了适用条件。
- 原文没有图片，示意图均为文本；本次未使用图床。命令与 YAML 只做文档和静态检查，未在 Kubernetes 集群执行。
