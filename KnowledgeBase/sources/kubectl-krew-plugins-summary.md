---
title: kubectl 插件指南 来源摘要
tags:
  - knowledgebase/source
  - kubernetes/cli
  - kubernetes/rbac
date: 2026-10-11
sources:
  - "[[kuebctl-插件krew]]"
aliases:
  - Krew 与 kubectl 插件来源摘要
---

# kubectl 插件指南 来源摘要

## 元信息

- **原始文档**：[[kuebctl-插件krew|kubectl 插件指南：Krew 安装、常用工具与 RBAC 排查]]
- **外部来源**：[WAKEUP技术：kubectl 不够用？krew 装 10 插件](https://mp.weixin.qq.com/s/H0PCEn6yVjbskCUB7hl94g)，发布于 2026-10-09。
- **领域**：Kubernetes CLI 工具、资源排查与 RBAC。
- **摄入日期**：2026-10-11。

## 摘要

指南介绍 kubectl 插件发现机制、Krew 在 macOS/Linux 与 Windows 上的安装、内网索引、本地安装包和日常维护。当前本机通过 Krew 管理 14 个业务插件及 Krew 管理器，ctx/ns 由 Homebrew 提供，outdated 已卸载。正文按用途说明常用命令，补充 Stern、df-pv、blame、view-allocations 的用法，以及 ACK D7 的只读实测结果；原有演示输出、完整 Deployment 配置和检查清单继续保留，不能将演示命令都视为已经执行。

## 关键知识点

1. kubectl 从 PATH 发现可执行的插件入口；Krew 管理安装和更新，PATH 仍需手动配置。插件可能是脚本或二进制，kubectl 不提供沙箱。
2. 离线安装要同时处理索引、平台对应的归档及校验信息；跳过索引更新不能替代下载插件包，本地 manifest/archive 是另一条安装路径。
3. ctx/ns 会持久化修改 kubeconfig；neat 清理部分现场字段，但导出清单仍需审查才能复用；tree 只沿 ownerReferences 展示子资源。
4. get-all 的结果受 RBAC、资源排除和 API 可用性约束，导出的清单快照不能当作完整灾备。
5. whoami 确认身份，rolesum 查看角色来源，who-can 反查具有 RBAC 权限的主体；目标身份的授权结果使用 auth can-i 检查，模拟身份需要相应权限。
6. resource-capacity 的 requests/limits 与实际用量要分别解读；`--util` 依赖 metrics-server，当前版本不支持 `--pod-template`。本机 v0.8.0 在 `-n forgeops --util` 查询中出现集群总 Utilization 为 0 的情况，节点/Pod 行有值，全局查询正常。
7. score 的警告退出参数为 `--exit-one-on-warning`，文件使用位置参数；JSON v2 的 grade 位于 checks 数组，CI 管道要保留检查工具的失败退出码。本机 v1.20.0 默认检查 Kubernetes `v1.18`，应显式设置目标集群版本；对导出清单返回 1 表示发现问题，不等于插件无法运行。
8. outdated 检查容器镜像更新；本机在 Artifactory 镜像查询中得到多个 `Unable to get image data`，未取得可靠完整结果，已卸载。废弃 API 检查另见 [[Docker-Kubernetes/k8s-UI-tools/k8s-API检查工具kubent|kubent]]。
9. Stern 支持 Pod/容器名正则、标签和日志内容筛选；`--no-follow` 读取历史日志后退出，`--max-log-requests` 控制并发。本机从 6 个 DS Pod 读取 18 行日志后正常退出。
10. blame 根据 managedFields 标注字段 manager；manager 标识客户端或控制器工作流，不等于认证用户名或完整修改历史。管道输入应保留 `--show-managed-fields`，本地文件使用 `-i`。
11. df-pv 读取挂载卷的 SIZE、USED、AVAILABLE 和 %USED，依赖节点卷统计权限与兼容的存储驱动；PVC 容量和文件系统统计是不同字段。本机读取到 6 个 DS PVC。
12. view-allocations 按资源、节点、命名空间和 Pod 汇总分配；`-u` 读取现场 CPU/内存用量，Free 默认依据 requests/limits 计算。v3.1.0 的 `-n forgeops -u` 汇总仍包含其他命名空间用量，比较总量应使用全局查询。
13. `krew list` 只显示 Krew 管理的安装记录，其他来源的 kubectl 入口用 `kubectl plugin list` 核对；本机 ctx/ns 的切换会写入 kubeconfig。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kubernetes]]：客户端插件与集群 API 排查。
- [[KnowledgeBase/concepts/RBAC]]：主体、角色来源、权限分析与授权验证。

## 值得注意

- images 的过滤、tree 的 ownerReferences 关系、资源插件的命名空间汇总、blame 的字段归属和 df-pv 的卷统计各有范围或前提，详见正文对应章节及“使用边界与参考资料”。
- 原文的历史版本、演示输出和 Kubernetes 1.29 metrics 案例仍是示例；资源分配表的汇总百分比不自洽，不能用于容量结论。本机安装版本与 ACK D7 实测记录单独列出，版本和数值对应 2026-10-11 的检查快照。
