---
title: ArgoCD 同步故障排查 来源摘要
tags:
  - knowledgebase/source
  - kubernetes/argocd
date: 2026-10-04
sources:
  - "[[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD同步故障排查]]"
aliases:
  - ArgoCD 同步踩 5 坑 来源摘要
---

# ArgoCD 同步故障排查 来源摘要

## 元信息
- **原始文档**：[[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD同步故障排查|ArgoCD 同步故障排查]]
- **外部来源**：[WAKEUP技术：ArgoCD 同步踩 5 坑](https://mp.weixin.qq.com/s/n4sgO6fcouZ-QyDdulRHaQ)，原文正文标注 2026-09-20。
- **领域**：Kubernetes / GitOps / ArgoCD
- **摄入日期**：2026-10-04

## 摘要
文章按反复 OutOfSync、资源停在 Progressing、同步执行失败、prune 误删和控制面性能五类问题组织排查，包含 YAML、CLI、Lua 示例、12 条生产注意事项、三个案例和 13 项检查清单。它适合在基础篇之后独立阅读：基础篇已介绍同步选项、Webhook 和健康机制，多集群实战侧重目录、权限和分发；本文把这些配置放到具体故障中解释。配置说明依据官方资料；案例归因和数据来自作者描述，尚未复现验证。

## 关键知识点
1. 同步状态、资源健康状态和最近一次操作结果分别判断；传统三方模型不能解释所有健康、删除和性能问题。
2. 忽略差异应限制到已确认的字段或 manager；`ignoreDifferences` 默认只影响比较，`RespectIgnoreDifferences=true` 才在同步阶段考虑忽略规则，且只对已存在的对象有效。
3. Service、Ingress、Job 和 Certificate 有已有健康检查可核对；Lua 示例要处理真实的状态条件，不能只为消除 Progressing 就覆盖规则。
4. 不可变字段、resourceVersion 错误和缺失的 API 类型分别排查；replace/create 与删除重建不同，force 不是通用重试。
5. 自动 prune、Prune=false、Prune=confirm 和 Application 删除保护用途不同；AppProject 管理范围不能替代删除确认。
6. Webhook 密钥在 argocd-secret；缓存和并发参数在 argocd-cmd-params-cm，默认已有缓存，调参效果须按实际负载验证。

## 涉及的概念与实体
- [[KnowledgeBase/entities/ArgoCD|ArgoCD]]
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/Helm|Helm]]
- [[KnowledgeBase/concepts/CICD|CI/CD]]
- [[KnowledgeBase/concepts/RBAC|RBAC]]
- [[KnowledgeBase/concepts/CRD|CRD]]

## 值得注意
- Application 不支持 `ignoreDifferences.all`，当前 CLI 命令参考没有 `--ignore-differences`；reconciliation 参数及健康、Replace、Webhook 和缓存配置应分别对照对应的 API、命令和官方说明。
- 案例中“只移动文件就被 prune”的完整因果、HPA/admission 的字段归属和性能改进效果均未验证，不能转写为本仓库事故记录。
- 示例命令和配置尚未通过目标 ArgoCD、Kubernetes 环境的部署验证。
