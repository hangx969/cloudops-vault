---
title: K8s 容器设计模式
tags:
  - knowledgebase/source
  - docker-kubernetes/basic-resources
date: 2026-06-28
sources:
  - "[[k8s基础-容器设计模式-Sidecar-Init-Ambassador-Adapter]]"
aliases:
  - 容器设计模式摘要
---

# K8s 容器设计模式

## 元信息
- **原始文档**：[[k8s基础-容器设计模式-Sidecar-Init-Ambassador-Adapter|K8s 四种容器设计模式]]
- **领域**：Docker-Kubernetes / 基础资源
- **摄入日期**：2026-06-28
- **覆盖模式**：Sidecar、Init Container、Ambassador、Adapter

## 摘要
K8s 四大容器设计模式指南。覆盖每种模式的核心理念、典型场景、完整 YAML 配置示例和选型指南。解决"把所有功能塞进一个容器"导致的维护困难、升级复杂、耦合度高问题。

## 关键知识点
1. **Sidecar 模式**：主容器 + 辅助容器同时运行，典型用例是 Istio Envoy 代理和 Fluentd 日志采集；通过 emptyDir 共享卷交换数据
2. **Init Container 模式**：主容器启动前串行执行初始化任务（环境准备/DB迁移/配置生成/权限设置），执行完毕后退出释放资源
3. **Ambassador 模式**：Sidecar 的特化——专注出站网络代理（数据库连接池/服务发现/TLS认证/API网关），主容器通过 localhost 访问外部服务
4. **Adapter 模式**：Sidecar 的特化——专注数据格式和协议转换（日志标准化/监控指标转 Prometheus/HTTP↔gRPC），使不兼容系统顺利协作
5. **选型核心**：Ambassador 和 Adapter 本质上都是 Sidecar 的特化形式，区别在于关注点不同——Ambassador 管网络通信，Adapter 管数据转换
6. **Init vs 其他三者的根本区别**：Init Container 在主容器启动**前**运行并退出，其他三种与主容器**同时**运行

## 涉及的概念与实体
- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/entities/Istio]]：Envoy Sidecar 是 Sidecar 模式的最经典实现
- [[KnowledgeBase/entities/Prometheus]]：Adapter 模式的典型消费端
- [[KnowledgeBase/concepts/服务网格]]：Sidecar 模式的最大规模应用

## 值得注意
- 与 [[KnowledgeBase/sources/k8s-basic-resources-batch-summary|K8s 基础资源]] 中的 Pod 基础互补——本文专注 Pod 内多容器协作模式，是从"单容器 Pod"到"多容器 Pod"的进阶
- Istio 的 Sidecar vs Ambient 模式演进（见 [[KnowledgeBase/entities/Istio]]）正是对 Sidecar 模式资源开销问题的回应
- Ambassador 模式中 HAProxy 做 DB 代理的配置可直接复用到生产环境
