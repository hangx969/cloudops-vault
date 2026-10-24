---
title: K8s 容器设计模式
tags:
  - knowledgebase/source
  - docker-kubernetes/basic-resources
date: 2026-10-24
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
1. Sidecar 持续辅助业务容器，典型用途包括代理与日志采集。普通 `containers` 无固定启动顺序；1.33 稳定的原生 Sidecar 位于 `initContainers`，设置 `restartPolicy: Always`，具有专门启动与终止语义。文件共享需显式挂载同一卷。
2. 普通 Init Container 在业务容器启动前按顺序成功结束，适合准备环境和生成配置；多副本数据库迁移还需幂等和锁。进程结束不代表调度时计入的有效 Pod 资源预算自动全部归还。
3. Ambassador 专注出站网络代理，主容器通过 localhost 访问代理。具体能力由代理实现决定：文中 HAProxy TCP 健康检查不会提升 PostgreSQL 副本为主库，也不提供数据库连接池。
4. **Adapter 模式**：Sidecar 的特化——专注数据格式和协议转换（日志标准化/监控指标转 Prometheus/HTTP↔gRPC），使不兼容系统顺利协作
5. **选型核心**：Ambassador 和 Adapter 本质上都是 Sidecar 的特化形式，区别在于关注点不同——Ambassador 管网络通信，Adapter 管数据转换
6. 普通 Init Container 完成后退出；持续辅助容器在运行期提供服务。模式描述职责，实际启动先后与退出顺序仍取决于容器在 Pod 中的声明方式。

## 涉及的概念与实体
- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/entities/Istio]]：Envoy Sidecar 是 Sidecar 模式的最经典实现
- [[KnowledgeBase/entities/Prometheus]]：Adapter 模式的典型消费端
- [[KnowledgeBase/concepts/服务网格]]：Sidecar 模式的最大规模应用

## 值得注意
- 与 [[KnowledgeBase/sources/k8s-basic-resources-batch-summary|K8s 基础资源]] 中的 Pod 基础互补——本文专注 Pod 内多容器协作模式，是从"单容器 Pod"到"多容器 Pod"的进阶
- Istio 的 Sidecar vs Ambient 模式演进（见 [[KnowledgeBase/entities/Istio]]）正是对 Sidecar 模式资源开销问题的回应
- 示例补齐 Fluentd ConfigMap 与 Python 指标转换脚本；业务镜像、数据库可写端点、监控发现和受支持镜像版本仍需按实际环境准备，不能直接视为生产模板。
