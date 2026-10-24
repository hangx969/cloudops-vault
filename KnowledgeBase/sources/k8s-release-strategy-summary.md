---
title: K8s 发布策略实战（蓝绿/金丝雀）
tags:
  - knowledgebase/source
  - docker-kubernetes/CICD
  - release-strategy
date: 2026-06-06
sources:
  - "[[Docker-Kubernetes/k8s-CICD/k8s发布策略-蓝绿部署与金丝雀发布]]"
aliases:
  - 蓝绿金丝雀摘要
---

# K8s 发布策略实战（蓝绿/金丝雀）

## 元信息
- **原始文档**：[[Docker-Kubernetes/k8s-CICD/k8s发布策略-蓝绿部署与金丝雀发布]]
- **领域**：Kubernetes / CI/CD / 发布策略
- **摄入日期**：2026-06-06

## 摘要
系统对比 K8s 四种发布策略（Recreate/RollingUpdate/蓝绿/金丝雀），深入讲解蓝绿部署（Service selector 秒级切换）和金丝雀发布的三种实现方案（K8s 原生副本比例、Nginx Ingress Annotation 精细流量控制、Argo Rollouts 企业级自动分析）。覆盖数据库 Schema 兼容性、健康检查配合、Prometheus 告警规则、选型决策树。

## 关键知识点
1. **蓝绿部署核心**：两套完整环境 + Service selector 切换，秒级切换/回滚，但资源消耗翻倍
2. **金丝雀三种实现**：① K8s 原生副本比例（粗粒度）② Nginx Ingress `canary-weight`/`canary-by-header`/`canary-by-cookie` Annotation（精细流量控制，推荐）③ Argo Rollouts CRD（steps + AnalysisTemplate + Prometheus 自动判断，企业级）
3. **Argo Rollouts**：`setWeight` + `pause` 分步渐进，AnalysisTemplate 绑定 Prometheus 指标（成功率 < 99% 自动回滚），操作命令 `promote`/`abort`
4. **数据库 Schema 兼容性**：expand/contract 三步法——新版本兼容旧列 → 只读新列 → 删除旧列，推荐 Flyway/Liquibase
5. **选型决策树**：回滚 < 1 分钟 → 蓝绿；高风险/A/B 测试 → 金丝雀；大型团队自动化 → Argo Rollouts；资源受限 → RollingUpdate
6. **金丝雀发布前置检查清单**：readinessProbe + 资源限制 + PDB + 监控面板 + 回滚命令就绪

## 涉及的概念与实体
- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/entities/ArgoCD]]
- [[KnowledgeBase/entities/Ingress]]
- [[KnowledgeBase/concepts/CICD]]

## 值得注意
- 与已有 [[Docker-Kubernetes/k8s-basic-resources/07-k8s基础-deployment]] 中的蓝绿/金丝雀基础原理互补——已有文章讲原理和简单 YAML，本文提供 **Nginx Ingress 和 Argo Rollouts 两种生产级方案**
- 与已有 [[Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio#灰度发布|Istio 灰度发布]] 互补——Istio 方案需要服务网格，本文的 Nginx Ingress 方案更轻量
- 渐进式流量调整脚本（canary-progress.sh）可直接用于生产环境的半自动金丝雀发布
