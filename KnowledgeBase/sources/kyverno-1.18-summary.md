---
title: Kyverno 部署与策略实践摘要（含 1.18）
tags:
  - knowledgebase/source
  - docker-kubernetes/security
  - kyverno
date: 2026-10-20
sources:
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter]]"
aliases:
  - Kyverno 1.18 Summary
  - Kyverno 1.18 新特性摘要
  - Kyverno 部署与策略实践
---

# Kyverno 部署与策略实践摘要（含 1.18）

## 元信息

- **原始文档**：[[Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter]]
- **领域**：Kubernetes 安全 / 准入控制 / 策略引擎
- **摄入日期**：2026-05-07
- **更新日期**：2026-10-20
- **外部来源**：[CNCF 1.18 公告](https://www.cncf.io/blog/2026/05/05/announcing-kyverno-release-1-18/)、[Kyverno 策略与上线经验](https://mp.weixin.qq.com/s/P07bjN2JFvGnbdtVj-yfQw?scene=1&click_id=49847292)

## 摘要

主文合并了 Kyverno 与 Policy Reporter 的 Helm 部署、八组验证策略、默认配置注入、命名空间资源生成，以及 Artifactory 镜像改写实战。策略按镜像来源、运行权限和工作负载规范组织，配套说明 Audit 到 Enforce 的上线顺序、服务端 dry-run、离线测试、后台扫描和 GitOps 差异处理。文末保留 1.18 的 HTTP 安全、CLI、策略引擎、镜像验证及 CEL 迁移说明，并区分历史 Chart 与新策略 API 的版本范围。

## 关键知识点

1. **部署版本与 HA**：原安装示例的 Kyverno Chart `3.2.7` 对应 `v1.12.6`，不等同于后面的 1.18 实战；HA 应分别设置各控制器副本、PDB 和资源保障。
2. **验证策略**：覆盖 latest、受信任仓库与 Harbor、非 root、privileged/hostPath/主机网络与 PID、资源声明、owner 标签、探针和 Service 类型。各示例明确检查的容器范围，安全规则允许缺省的安全字段。
3. **变更与生成**：注入 `regcred` 引用、设置 Deployment 历史版本上限，以及为新 Namespace 生成 ResourceQuota/LimitRange；`Audit` 不会关闭这些动作，Secret、控制器权限和下游资源就绪需另行确认。
4. **CEL 镜像改写**：以单一 MutatingPolicy 和命名空间 In 列表覆盖目标范围，仅替换有 Smart Remote 缓存的仓库，并处理 containers 与 initContainers。Webhook 故障放行不保证原始镜像源可达；selector 冲突属于原环境的排障记录。
5. **测试与报告**：服务端 dry-run 验证准入链，CLI 测试需要资源样本与预期结果；Audit 模式命令成功不能证明合规。后台扫描关闭后不盘点未再提交的存量对象，报告也不固定为每个命名空间一份。
6. **生产上线**：先审计并整改，再按命名空间逐条强制；将策略和测试纳入 Git，按风险选择 Fail/Ignore，升级前检查 Chart、CRD、可用性及受控例外。
7. **HTTP 调用安全加固**：1.18 增加地址允许/阻止列表和受限 token；命名空间级策略的 HTTP 调用默认禁用，涉及 CVE-2026-4789、CVE-2026-41323。
8. **CLI 扩展**：`kyverno apply` 和 `kyverno test` 支持 Cleanup、HTTP/Envoy 授权策略、MutatingPolicy 的 mutateExisting，以及 `--exceptions-with-policies`。
9. **策略引擎增强**：新增 `successEventActions`，支持 admission controller 基于内存的 HPA 和 `/metrics` TLS，改进并发及稳定性。
10. **CEL 演进**：新增 gzip 库，改进变量与条件的编译求值，以及策略类型和执行引擎的一致性。
11. **镜像验证增强**：`imageRegistryCredentials.secrets` 支持 `namespace/name`，Pod 的 imagePullSecrets 可作为仓库凭证，并修复 ImageValidatingPolicy 的签名、解析及过滤问题。
12. **Policies Helm Chart**：ValidatingPolicies 支持 excludes、`auditAnnotation` 和策略级 annotation 覆盖。
13. **支持与迁移**：1.18 公告提出 N-1 补丁支持及约三个月的支持窗口，并建议由 ClusterPolicy/CleanupPolicy 迁移到对应的新策略类型；实际状态以目标版本说明为准，不能据此推导统一的六个月迁移期限。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kyverno]]：准入策略、变更与生成规则
- [[KnowledgeBase/entities/Kubernetes]]：资源模型与准入链
- [[KnowledgeBase/entities/Helm]]：版本化部署及 values 管理
- [[KnowledgeBase/concepts/RBAC]]：控制器与策略例外的权限边界

## 值得注意

- Policy Reporter 单独部署，负责读取报告、展示和通知；它不执行准入策略。
- 部署清单、CEL 实战与 1.18 发布公告的版本范围需要分别判断；公告中的弃用计划不等于所有版本已经移除旧 API。
- 主文保留 1.18 公告中的 CNCF 毕业背景、AI governance 与多集群策略路线图，路线图内容应按计划理解。
- 容器镜像来源、非 root 配置和探针检查都不等于完整的运行时安全或健康保证。
