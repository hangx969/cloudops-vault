---
title: "kubectl 插件指南 来源摘要"
tags:
  - knowledgebase/source
  - kubernetes/cli
  - kubernetes/rbac
date: 2026-10-11
sources:
  - "[[Docker-Kubernetes/k8s-UI-tools/kuebctl-插件krew-rolesum]]"
aliases:
  - Krew 与 kubectl 插件来源摘要
---

# kubectl 插件指南 来源摘要

## 元信息

- **原始文档**：[[Docker-Kubernetes/k8s-UI-tools/kuebctl-插件krew-rolesum|kubectl 插件指南：Krew 安装、常用工具与 RBAC 排查]]
- **外部来源**：[WAKEUP技术：kubectl 不够用？krew 装 10 插件](https://mp.weixin.qq.com/s/H0PCEn6yVjbskCUB7hl94g)，发布于 2026-10-09。
- **领域**：Kubernetes CLI 工具、资源排查与 RBAC。
- **摄入日期**：2026-10-11。

## 摘要

本文将 Krew/rolesum 现有笔记与十组插件场景整合为一篇指南，覆盖插件发现机制、macOS/Linux 与 Windows 安装、内网索引、本地安装包和日常维护。正文按上下文切换、配置清理、资源关系、镜像检查、RBAC、日志、资源分配和 CI 检查组织 13 个插件，保留命令、输出示例、完整 Deployment 配置与检查清单。对照官方索引、文档和代码，校订了无效参数、混淆的工具职责及示例数据，未在实际集群运行这些命令。

## 关键知识点

1. kubectl 从 PATH 发现可执行的插件入口；Krew 管理安装和更新，PATH 仍需手动配置。插件可能是脚本或二进制，kubectl 不提供沙箱。
2. 离线安装要同时处理索引、平台对应的归档及校验信息；跳过索引更新不能替代下载插件包，本地 manifest/archive 是另一条安装路径。
3. ctx/ns 会持久化修改 kubeconfig；neat 清理部分现场字段，但导出清单仍需审查才能复用；tree 只沿 ownerReferences 展示子资源。
4. get-all 的结果受 RBAC、资源排除和 API 可用性约束，导出的清单快照不能当作完整灾备。
5. whoami 确认身份，rolesum 查看角色来源，who-can 反查具有 RBAC 权限的主体；目标身份的授权结果使用 auth can-i 检查，模拟身份需要相应权限。
6. resource-capacity 的 requests/limits 与实际用量要分别解读；--util 依赖 metrics-server，当前版本不支持 --pod-template。
7. score 的警告退出参数为 --exit-one-on-warning，文件使用位置参数；JSON v2 的 grade 位于 checks 数组，CI 管道要保留检查工具的失败退出码。
8. outdated 检查容器镜像更新；废弃 API 检查另见 [[Docker-Kubernetes/k8s-UI-tools/k8s-API检查工具kubent|kubent]]。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kubernetes]]：客户端插件与集群 API 排查。
- [[KnowledgeBase/concepts/RBAC]]：主体、角色来源、权限分析与授权验证。

## 值得注意

- 原文的 images 过滤参数、tree 控制器参数、resource-capacity 模板估算和 outdated 废弃 API 输出不属于核对到的插件能力，完整差异见正文“原文校订说明与来源”。
- 来源文章的版本、输出和 Kubernetes 1.29 metrics 案例只作为来源示例；资源分配表的汇总百分比不自洽，不能用于容量结论。
- 合并正文沿用现有文件路径与原别名，维护已有引用；重复剪藏在内容核对后清理。
