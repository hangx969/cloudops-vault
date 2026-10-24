---
title: K8s 标签与选择器实战
tags:
  - knowledgebase/source
  - docker-kubernetes/basic-resources
date: 2026-06-28
sources:
  - "[[Docker-Kubernetes/k8s-basic-resources/05-k8s基础-pod调度-标签与选择器实战]]"
aliases:
  - 标签选择器摘要
---

# K8s 标签与选择器实战

## 元信息
- **原始文档**：[[Docker-Kubernetes/k8s-basic-resources/05-k8s基础-pod调度-标签与选择器实战|K8s 标签与选择器避坑：5 条规则与生产案例]]
- **领域**：Docker-Kubernetes / 基础资源
- **摄入日期**：2026-06-28

## 摘要
K8s 标签（Labels）与选择器（Selectors）的生产级实战指南。覆盖标签与注解的区别、`app.kubernetes.io/*` 官方推荐命名规范、两种选择器（等值/集合）的用法与限制、5 条 SRE 核心铁律（selector 匹配、节点调度、成本归因、版本标签陷阱、单值原则）、4 个真实翻车案例（含 kubectl v1.33.0 Null 值修复）。

## 关键知识点
1. **Labels vs Annotations**：标签被系统消费（调度器/Service/HPA），注解仅给人看（构建信息/联系人）
2. **官方推荐标签**：`app.kubernetes.io/name|instance|version|component|part-of|managed-by` 六件套，所有工具互认
3. **Deployment selector 不可变**：创建后无法修改，改了直接卡死，只能删除重建
4. **版本标签陷阱**：`app.kubernetes.io/version` 只做展示（查询/监控/审计），**绝对不放 selector**——selector 不可变，版本会变
5. **节点调度选型**：`nodeSelector` 管"定向调度"，Taints/Tolerations 管"节点拒绝"，两者互补不强绑
6. **成本归因标签**：team/cost-center/environment/project 四维度，AWS EKS 支持导入为成本分配标签（每 Pod 最多 50 个）
7. **标签值不支持数组**：`"prod,staging,dev"` 是字符串不是数组，无法用 `In` 操作符匹配单个元素
8. **kubectl Null 值 Bug**：v1.30.5 及更早版本对 Helm 渲染出的 null 标签值处理异常，v1.33.0 修复

## 涉及的概念与实体
- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/entities/Helm]]
- [[KnowledgeBase/entities/Kyverno]]：策略引擎可强制标签规范
- [[KnowledgeBase/concepts/CICD]]：CI/CD 系统打标签需带前缀

## 值得注意
- 与现有 [[KnowledgeBase/sources/k8s-basic-resources-batch-summary|K8s 基础资源]] 互补——该批量摘要覆盖 Pod/Deployment/Service 等 22 篇，但**没有 Labels/Selectors 专题**，本文填补了这个空白
- "Deployment selector 不可变"是高频翻车点，与 [[KnowledgeBase/sources/k8s-release-strategy-summary|K8s 发布策略]] 中的蓝绿/金丝雀部署直接相关
- 成本归因标签体系与 [[KnowledgeBase/sources/k8s-scaling-storage-batch-summary|K8s 扩缩容与存储]] 中的 FinOps 内容形成完整闭环
