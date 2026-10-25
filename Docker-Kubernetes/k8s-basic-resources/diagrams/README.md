---
title: K8s 基础资源文章架构图重绘验收记录
tags:
  - kubernetes/diagrams
  - documentation/maintenance
date: 2026-10-25
aliases:
  - K8s 架构图重绘验收
---

# K8s 基础资源文章架构图重绘验收记录

已检查目录中的 26 篇文章，更新 17 篇。使用 Diagram Design skill 和用户选定的 Kubernetes 蓝色主题；三位 GPT 6.1 Sol High agents 分组制作，主 agent 统一验收、上传和替换。

## 交付范围

- 重绘 48 张原有示意图，将 6 处文本流程图转换为图片。
- Pod 创建流程和 kubeadm 历史流程分别拆为 3 张，最终交付 58 张 PNG、58 份可编辑单文件 HTML。
- PNG 均为 2560×1440，已通过 PicGo CLI 的 githubPlus 插件上传到 `hangx969/upload-images-md`，文章使用上传后的图片 URL。
- 保留 4 张非示意图截图：02-01（kubectl explain）、02-02（字段说明表）、12-01（OSI 七层文字列表）、24-02（运行时 CLI 命令对照表）。
- `manifest.json` 保存每个原图 URL、原文本流程、对应图源、上传 URL、SHA-256、排除理由及保真说明。

## 按文章统计

| 文章 | 原图重绘 | 文本图转换 | 新 PNG | 保留截图 |
| --- | ---: | ---: | ---: | ---: |
| [[Docker-Kubernetes/k8s-basic-resources/01-k8s基础-架构-组件-资源|01-k8s基础-架构-组件-资源]] | 2 | 0 | 2 | 0 |
| [[Docker-Kubernetes/k8s-basic-resources/02-k8s基础-yaml-apply|02-k8s基础-yaml-apply]] | 0 | 0 | 0 | 2 |
| [[Docker-Kubernetes/k8s-basic-resources/03-k8s基础-pod基础|03-k8s基础-pod基础]] | 5 | 0 | 7 | 0 |
| [[Docker-Kubernetes/k8s-basic-resources/04-k8s基础-pod-健康探针|04-k8s基础-pod-健康探针]] | 0 | 1 | 1 | 0 |
| [[Docker-Kubernetes/k8s-basic-resources/07-k8s基础-deployment|07-k8s基础-deployment]] | 4 | 0 | 4 | 0 |
| [[Docker-Kubernetes/k8s-basic-resources/09-k8s基础-job-cronjob|09-k8s基础-job-cronjob]] | 1 | 0 | 1 | 0 |
| [[Docker-Kubernetes/k8s-basic-resources/11-k8s基础-Service|11-k8s基础-Service]] | 9 | 0 | 9 | 0 |
| [[Docker-Kubernetes/k8s-basic-resources/12-k8s基础-ingress|12-k8s基础-ingress]] | 7 | 0 | 7 | 1 |
| [[Docker-Kubernetes/k8s-basic-resources/13-k8s基础-storage|13-k8s基础-storage]] | 4 | 0 | 4 | 0 |
| [[Docker-Kubernetes/k8s-basic-resources/14-k8s基础-statefulset|14-k8s基础-statefulset]] | 1 | 0 | 1 | 0 |
| [[Docker-Kubernetes/k8s-basic-resources/15-k8s基础-容器设计模式-Sidecar-Init-Ambassador-Adapter|15-k8s基础-容器设计模式-Sidecar-Init-Ambassador-Adapter]] | 6 | 0 | 6 | 0 |
| [[Docker-Kubernetes/k8s-basic-resources/17-k8s-PodDisruptionBudget实战|17-k8s-PodDisruptionBudget实战]] | 0 | 1 | 1 | 0 |
| [[Docker-Kubernetes/k8s-basic-resources/18-k8s基础-认证-授权-准入|18-k8s基础-认证-授权-准入]] | 6 | 0 | 6 | 0 |
| [[Docker-Kubernetes/k8s-basic-resources/19-k8s-APIServer深度剖析-请求链路-认证授权-生产调优|19-k8s-APIServer深度剖析-请求链路-认证授权-生产调优]] | 0 | 3 | 3 | 0 |
| [[Docker-Kubernetes/k8s-basic-resources/20-k8s基础-Finalizer与资源删除|20-k8s基础-Finalizer与资源删除]] | 0 | 1 | 1 | 0 |
| [[Docker-Kubernetes/k8s-basic-resources/24-k8s基础-容器运行时-containerd|24-k8s基础-容器运行时-containerd]] | 1 | 0 | 1 | 1 |
| [[Docker-Kubernetes/k8s-basic-resources/25-k8s基础-kubeadm|25-k8s基础-kubeadm]] | 1 | 0 | 3 | 0 |
| [[Docker-Kubernetes/k8s-basic-resources/26-k8s基础-Calico|26-k8s基础-Calico]] | 1 | 0 | 1 | 0 |

其余文章未发现需要重绘的现有图。配置片段、命令输出、文件目录树及普通行文中的箭头不作为架构图处理。

## 验收结果

| 检查 | 结果 |
| --- | --- |
| Skill self_check：可访问 SVG 与单文件完整性 | 58/58 通过 |
| Skill export_png：PNG 导出与尺寸 | 58/58 通过，2560×1440 |
| 浏览器几何：文字越界、文字重叠、连线穿非终点节点、斜直线 | 58 张检查，未发现剩余问题 |
| 视觉检查 | 制作 agents 逐图查看；主 agent 检查全部联系图并放大复核复杂图和修正项 |
| 图床访问与文件一致性 | 58/58 HTTP 200，PNG 签名有效，远端 SHA-256 与本地一致 |
| 文章完整性 | 58 个新图链接各出现一次；4 张截图仍在；逐篇还原替换后与 Git HEAD 完全一致，无图替换之外的正文改动 |
| Git 空白检查 | `git diff --check` 通过 |

Geist、Geist Mono、Instrument Serif 已加载。中文在本机通过 PingFang / Songti 字体回退渲染，PNG 已固定最终字形。

## 保真与修正记录

- Service 原文第 3、4 张图与相邻段落颠倒：保留各图语义，调整新图插入位置，使“有注册中心”和“无注册中心”与文字相符。
- Ingress 高可用图使用正文实验中的 VIP `192.168.40.8`、节点 `192.168.40.5/6`。Canary Cookie 示例改为 `foo=always`，并注明 `canary-by-cookie: foo`；Header 仍按注解配置匹配。
- API Watch 图将 `ADDED / MODIFIED / DELETED` 标在 API Server 发往客户端的事件上，保留流式 HTTP 响应及 HTTP/1.1 chunked transfer 说明。参见 [Kubernetes API Concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/#efficient-detection-of-changes)。
- Finalizer 图保留空/非空分支、删除时间标记、控制器清理及移除条目，避免把 Terminating 画成所有资源通用的状态字段。参见 [Finalizers](https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/)。
- Docker、userspace、IPVS、独立 etcd 的 Calico、kubeadm 旧特性等历史内容均保留并标注历史边界。原图与正文示例的 ES/stdout、roundrobin/backup、PVC 命名等差异在对应图注和清单中说明。

原图来源与逐项差异以 `manifest.json` 为准。所有正文改动均为图片或文本流程图替换，未改动实验命令与配置。
