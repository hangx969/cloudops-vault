---
title: K8s健康探针配置与重启风暴复盘
tags:
  - knowledgebase/source
  - docker-kubernetes/k8s-probe
date: 2026-10-24
aliases:
  - Pod探针重启风暴摘要
  - K8s健康探针重启风暴复盘
  - Kubernetes健康探针配置摘要
---

# K8s 健康探针配置与重启风暴复盘

## 元信息

- **原始文档**：[[Docker-Kubernetes/k8s-basic-resources/04-k8s基础-pod-健康探针]]
- **领域**：Kubernetes / Pod / 健康探针
- **摄入日期**：2026-09-06
- **最近更新**：2026-10-24（补充公众号导入背景并重排技术内容）

## 摘要

文章从发布后 Pod 显示 Running 却无法处理请求的场景切入，解释运行状态、就绪状态与三类探针的职责，再介绍四种探测方式、默认参数、时间预算和完整 YAML 示例。健康端点设计提前到案例之前，说明共享依赖、管理端口和轻量 Liveness 的检查边界。案例保留原来源记述的配置、数字和时间线，串起依赖抖动、摘流窗口与级联重启的关系；随后给出有序排查步骤、监控查询、发布与恢复边界及上线检查清单，原有 19 个代码块保持完整。

## 关键知识点

1. Startup 成功前不执行 Liveness 与 Readiness；成功后两者各自工作，没有固定的先后顺序。
2. Exec、TCP、HTTP、gRPC 分别表达命令结果、连通性或应用健康语义，端口可连接不等于业务可用。
3. Liveness 应围绕重启能修复的内部故障设计；Readiness 控制常规 Service 的就绪后端，失败不重启容器。
4. `failureThreshold × periodSeconds` 只估算容忍量级，不能当作故障发生后精确计时的保证；参数要结合启动耗时、请求延迟和退出过程验证。
5. 健康端点需轻量、限时；共享依赖检查可能让全部副本同时未就绪，须结合降级与流量策略判断。
6. sidecar 脚本退出不会自动成为业务容器的探针结果，也不会自动重启业务容器；管理端口健康也不必然代表业务端口健康。
7. 探针批量变更需要灰度、回滚、重启率告警和依赖变慢故障演练，PDB 与 HPA 不能直接阻止探针误杀。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/concepts/高可用架构]]
- [[KnowledgeBase/sources/k8s-pdb-summary|K8s PDB 实战]]
- [[KnowledgeBase/sources/k8s-basic-resources-batch-summary|K8s 基础资源]]

## 值得注意

- 事故数字与时间线是原案例记述，不是官方文档结论或本次实测；现有材料只有来源标题，未补造作者或发布链接。
- 三种探针共用一个 Actuator 路径的例子用于说明配置位置，生产环境仍需按职责选择端点。
- Liveness 与 Readiness 的容忍窗口倍数属于经验建议；Prometheus 查询使用示意指标名，实际指标、标签与类型需核对采集系统。
- Pod 基础、退出和调试内容保留在 [[Docker-Kubernetes/k8s-basic-resources/03-k8s基础-pod基础]]。
