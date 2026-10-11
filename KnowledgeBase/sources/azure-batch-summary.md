---
title: Azure 来源批量摘要
tags:
  - knowledgebase/source
  - azure
date: 2026-04-17
sources:
  - "[[Azure/0_Azure-VM-VMSS]]"
  - "[[Azure/1_Azure-Linux-VM-troubheshooting]]"
  - "[[Azure/2_AKS-basics]]"
  - "[[Azure/3_AKS-workload-identity]]"
  - "[[Azure/4_AKS-SecretProviderClass-KeyVault]]"
  - "[[Azure/5_Azure-Storage]]"
  - "[[Azure/6_Azure-Networking]]"
  - "[[Azure/7_ACR-ACI]]"
  - "[[Azure/8_Azure-devops-basics]]"
  - "[[Azure/9_Azure-devops-self-host-agents]]"
  - "[[Azure/10_Azure-devops-agent-pool-management]]"
  - "[[Azure/11_Azure-Policy]]"
  - "[[Azure/Jfrog-artifactory-Azure]]"
  - "[[14_Kusto Query]]"
  - "[[12_Azure 故障排查工具]]"
  - "[[13_Azure命令行工具]]"
  - "[[Azure/Customer Support/Email Templates]]"
aliases:
  - "Azure 批量摘要"
---

# Azure 来源批量摘要

## 元信息
- **原始目录**：`Azure/`
- **文档数量**：17 篇
- **领域**：Azure
- **摄入日期**：2026-04-17

## 摘要

该 Azure 文档集涵盖了 Azure 云平台的核心基础设施服务与运维实践。内容覆盖计算（VM/VMSS、AKS）、存储、网络、容器服务（ACR/ACI）、DevOps CI/CD 流水线、治理（Azure Policy）等关键领域。此外还包含大量实用的故障排查工具与方法（Fiddler、PerfMon、Browser Trace、KQL 查询等），以及客户支持邮件模板。整体定位为 Azure 技术支持工程师的实战知识库，侧重于中国区（Azure China Cloud）的部署与运维场景。

## 关键知识点

1. Azure China Cloud 需要专门配置：PowerShell 登录使用 `Connect-AzAccount -Environment AzureChinaCloud`，ACR 完全限定 URL 为 `<registry-name>.azurecr.cn`；Azure DevOps 在 Azure China 不支持 MS Managed Agents，只能使用自托管代理。
2. AKS 控制面（apiserver、scheduler、etcd、controller）由 Azure 托管；AKS 1.19+ 的 Linux 节点使用 containerd 作为容器运行时。
3. Workload Identity 需启用 OIDC Issuer 和 Workload Identity 功能，通过 Federated Credential 将 Kubernetes Service Account 与 Azure Managed Identity 关联；SecretProviderClass（CSI 驱动的 AKS 插件）借助预先授权的 User-Assigned Managed Identity，将 Key Vault Secret 同步为同一 namespace 下的 Kubernetes Secret。
4. Azure Policy 在 ARM 层拦截所有 CRUD 请求，位于 RBAC 之后；Policy 针对资源定义，RBAC 针对用户操作；拒绝策略凌驾于所有允许操作之上。
5. 存储冗余有 LRS、GRS、RA-GRS、ZRS、GZRS 五种；Blob 分为 Block、Append、Page 三种类型，访问层中 Cool 最少 30 天、Archive 最少 180 天。
6. Azure DevOps Pipeline 各 Step 之间不共享环境变量，需通过 logging command 传递；自托管 Agent 通过 capability/demand 机制匹配 Pipeline 需求，注册支持 PAT、Device Code、Service Principal 三种认证方式。
7. Linux VM 的 OS 磁盘扩展需在系统内用 fdisk + resize2fs 完成；文件系统损坏时可用 rescue VM 挂载问题磁盘并执行 fsck 修复。
8. 排障工具分工：Browser Trace 导出 HAR，Fiddler Classic 捕获 HTTP/HTTPS 会话，Process Monitor 保存 .PML，PerfMon 与 Diskspd 同步采集性能指标；Diskspd、FIO 分别用于 Windows、Linux 磁盘测试，iotop 用于持续观察 I/O。

## 各文档摘要

### [[Azure/0_Azure-VM-VMSS|Azure VM and VMSS]]
- 核心内容：详细介绍 Azure 虚拟机与虚拟机规模集的架构，包括 IaaS/PaaS/SaaS 区别、物理节点架构（Fabric、Host Agent、Guest Agent）及 VMSS 的部署与管理。
- 关键知识点：
  - Fabric Controller 管理数据中心资源分配和服务生命周期
  - Guest Agent (waagent) 负责 VM 内部管理，可手动重装
  - VM 部署在 Windows Server 物理机上，约 1000 台组成集群
  - IaaS/PaaS/SaaS 三层服务模型对比

### [[Azure/1_Azure-Linux-VM-troubheshooting|Azure Linux VM Troubleshooting]]
- 核心内容：Linux 虚拟机常见故障排查指南，涵盖磁盘扩展、文件系统损坏、fstab 问题等场景。
- 关键知识点：
  - OS 磁盘扩展需在 Linux 内部使用 fdisk + resize2fs 完成
  - 文件系统损坏可通过 rescue VM 挂载问题磁盘并使用 fsck 修复
  - fstab 配置错误导致 VM 无法启动的排查方法
  - 常用磁盘命令：df、du、lsblk、fdisk

### [[Azure/2_AKS-basics|AKS Basics]]
- 核心内容：Azure Kubernetes Service 基础架构与核心组件介绍，包括控制面、工作节点、资源预留机制。
- 关键知识点：
  - 控制面由 Azure 托管（apiserver、scheduler、etcd、controller）
  - 工作节点包含 kubelet、kubeproxy、containerd 容器运行时
  - AKS 1.19+ Linux 节点使用 containerd 作为容器运行时
  - 资源预留：CPU 以 millicores 为单位，节点越大预留越多

### [[Azure/3_AKS-workload-identity|AKS Workload Identity]]
- 核心内容：在 AKS 中启用和配置 Workload Identity 的完整步骤，实现 Pod 到 Azure 资源的身份认证。
- 关键知识点：
  - 依赖 OIDC Issuer 和 Workload Identity 功能标志
  - 通过 Federated Credential 将 Kubernetes Service Account 与 Azure Managed Identity 关联
  - 适用于 Azure China Cloud 环境

### [[Azure/4_AKS-SecretProviderClass-KeyVault|AKS SecretProviderClass with KeyVault]]
- 核心内容：使用 SecretProviderClass 将 Azure Key Vault 中的密钥同步为 Kubernetes Secret 的配置方法。
- 关键知识点：
  - SecretProviderClass 是 CSI 驱动的 AKS 插件
  - 需要预先创建 User-Assigned Managed Identity 并授权 Key Vault 访问
  - 支持将 Key Vault Secret 自动转换为 Kubernetes Secret
  - 新创建的 Secret 与 SecretProviderClass 处于同一 namespace

### [[Azure/5_Azure-Storage|Azure Storage]]
- 核心内容：Azure 存储服务全面介绍，涵盖存储类型、冗余策略、Blob 存储、托管磁盘等。
- 关键知识点：
  - 存储冗余：LRS、GRS、RA-GRS、ZRS、GZRS 五种方案
  - Blob 三种类型：Block Blob、Append Blob、Page Blob
  - Blob 访问层：Hot、Cool（最少 30 天）、Archive（最少 180 天）
  - 托管磁盘类型：Premium SSD、Standard SSD、Standard HDD

### [[Azure/6_Azure-Networking|Azure Networking]]
- 核心内容：Azure 网络连接测试与故障排查工具集合，包括 VNet、NSG、负载均衡等网络基础知识。
- 关键知识点：
  - 网络测试工具：psping、telnet、nc、dig、curl、siege
  - dig 用于 DNS 查询与域名解析
  - curl 测试外网连通性，验证出站访问
  - 涵盖 Kubernetes 集群内部 DNS 解析测试

### [[Azure/7_ACR-ACI|Azure ACR and ACI]]
- 核心内容：ACR 容器注册表和 ACI 容器实例的概念、层级结构与操作方法。
- 关键知识点：
  - ACR 层级：容器注册表 > 存储库 > 容器镜像
  - 清单摘要（digest）使用 SHA-256 哈希唯一标识每个镜像
  - ACR 完全限定 URL 格式：`<registry-name>.azurecr.cn`
  - 推送镜像前需先使用 docker tag 标记

### [[Azure/8_Azure-devops-basics|Azure DevOps Basics]]
- 核心内容：Azure DevOps 流水线基础概念，包括 Pipeline、Stage、Job、Step 的层级关系与配置方法。
- 关键知识点：
  - Pipeline 通过 azure-pipelines.yml 定义 CI/CD 流程
  - 分为 YAML Pipeline（常用）和 Classic Pipeline 两种
  - Steps 之间不共享环境变量，需通过 logging command 传递
  - 触发方式：代码推送、定时、其他构建完成

### [[Azure/9_Azure-devops-self-host-agents|Azure DevOps Self-Hosted Agents]]
- 核心内容：Azure DevOps 自托管代理的部署、注册、认证与自定义镜像制作。
- 关键知识点：
  - Azure China 不支持 MS Managed Agents，只能使用自托管代理
  - Agent 通过 capability/demand 机制匹配 pipeline 需求
  - Agent 注册支持 PAT、Device Code、Service Principal 三种认证方式
  - Agent 与 Pipeline 之间使用 OAuth Token 和非对称加密通信

### [[Azure/10_Azure-devops-agent-pool-management|Azure DevOps Agent Pool Management]]
- 核心内容：使用 Az CLI 和 REST API 管理 DevOps Agent Pool 与 Agent 的操作方法。
- 关键知识点：
  - 通过 PAT 登录 DevOps CLI
  - 使用 az pipelines pool/agent 命令管理池和代理
  - Agent 删除只能通过 REST API 操作
  - 可通过 assignedRequest 字段检测 agent 是否正在执行 job

### [[Azure/11_Azure-Policy|Azure Policy]]
- 核心内容：Azure Policy 的工作原理、调用流程、与 RBAC 的区别，以及 Policy Definition 的编写方法。
- 关键知识点：
  - Policy 在 ARM 层拦截所有 CRUD 请求，位于 RBAC 之后
  - Explicit Deny System：拒绝策略凌驾于所有允许操作之上
  - Policy 针对资源定义，RBAC 针对用户操作
  - 支持 Audit 和 Enforcement 两大用途

### [[Azure/Jfrog-artifactory-Azure|JFrog Artifactory on Azure]]
- 核心内容：在 Azure 上部署 JFrog Artifactory 的架构和步骤，包括 ACI 和 AKS 两种部署方式。
- 关键知识点：
  - Artifactory 目录结构：app（程序）和 var（数据，需持久化）
  - 支持部署到 ACI（需 VNet 配置）和 AKS
  - 需要准备 VNet、子网和容器镜像
  - 与 ACR、Azure Storage 集成

### [[14_Kusto Query|Kusto Query Language (KQL) Reference]]
- 核心内容：用于 Azure 诊断和故障排查的 KQL 查询语句集合，覆盖 VM、AKS、存储、ACR/ACI 等多种服务。
- 关键知识点：
  - 关键表：LogContainerSnapshot、LogNodeSnapshot、LogContainerHealthSnapshot
  - 可查询 VM 的 Node ID、Container ID、可用性集等信息
  - 支持节点状态、容器健康状态、租户事件等多维度查询
  - 面向 Azure 内部诊断平台（Azurecm）

### [[13_Azure命令行工具|Command Line Tools]]
- 核心内容：Azure 命令行工具集合，包括 Azure PowerShell、Az CLI 和 AzCopy 的安装、配置与使用。
- 关键知识点：
  - Azure PowerShell 基于 .NET 对象，使用 cmdlet 管理资源
  - Azure China Cloud 需使用 `Connect-AzAccount -Environment AzureChinaCloud`
  - 可使用 AAD App + Client Secret 实现自动登录
  - 清除登录缓存优先使用 `Clear-AzContext -Scope CurrentUser` 或 `az account clear`，不要不加区分地批量删除缓存文件

### [[12_Azure 故障排查工具|12_Azure 故障排查工具]]
- 核心内容：按浏览器和 HTTP 请求、Azure API、Windows 进程与性能、磁盘 I/O 的顺序介绍排障工具和操作方法。
- 关键知识点：
  - Browser Trace 导出 HAR；Fiddler Classic 捕获并过滤 HTTP/HTTPS 会话
  - Postman 调试 Entra ID（AAD）与 ARM API 时需使用对应目标资源的令牌
  - Process Monitor 保存 .PML；PerfMon 与 Diskspd 同步采集性能指标
  - Diskspd、FIO 和 iotop 分别用于 Windows/Linux 磁盘测试与持续 I/O 观察

### [[Azure/Customer Support/Email Templates|Email Templates]]
- 核心内容：微软技术支持工程师使用的中英文邮件模板集合，覆盖初次联系、追踪进展、问题调查等场景。
- 关键知识点：
  - 初次邮件需收集资源 ID、错误信息、事件时间
  - 中英文双语模板
  - 涵盖初次联系、追踪、进展更新等工单生命周期
  - 面向 Azure 全球技术中心（GTC）支持流程

## 涉及的概念与实体
- [[KnowledgeBase/entities/Azure|Azure]]
- [[KnowledgeBase/entities/AKS|AKS]]
- [[KnowledgeBase/entities/Azure VM|Azure VM]]
- [[KnowledgeBase/entities/VMSS|VMSS]]
- [[KnowledgeBase/entities/Azure Storage|Azure Storage]]
- [[KnowledgeBase/entities/Azure Networking|Azure Networking]]
- [[KnowledgeBase/entities/ACR|ACR]]
- [[KnowledgeBase/entities/ACI|ACI]]
- [[KnowledgeBase/entities/Azure DevOps|Azure DevOps]]
- [[KnowledgeBase/entities/Azure Policy|Azure Policy]]
- [[KnowledgeBase/entities/Key Vault|Key Vault]]
- [[KnowledgeBase/entities/Workload Identity|Workload Identity]]
- [[KnowledgeBase/entities/KQL|KQL]]
- [[KnowledgeBase/entities/JFrog Artifactory|JFrog Artifactory]]
- [[KnowledgeBase/entities/Fiddler|Fiddler]]
- [[KnowledgeBase/entities/PerfMon|PerfMon]]

## 交叉主题发现
- **Azure China Cloud 专注**：多篇文档专门针对中国区 Azure 的特殊配置（如 AzureChinaCloud 环境、azurecr.cn 域名、自托管 DevOps Agent 的必要性），说明该知识库主要服务于中国区 Azure 运维。
- **AKS 安全体系**：Workload Identity、SecretProviderClass、Key Vault 三篇文档构成完整的 AKS 身份认证与密钥管理链路，从 Pod 身份到密钥注入形成闭环。
- **工具链与故障排查**：诊断与排障工具自成一类（Fiddler、PerfMon、Browser Trace、Postman、IO Monitor 已合并为故障排查工具专文，另有 KQL 与命令行工具），体现了知识库的技术支持工程师视角。
- **DevOps 全链路**：从 Pipeline 基础、自托管 Agent 到 Agent Pool 管理，覆盖了 Azure DevOps CI/CD 的完整运维流程。
- **存储与计算交叉**：Azure Storage 与 VM、AKS 存在紧密关联，磁盘类型、IO 测试、存储冗余等知识点跨多篇文档互相引用。

## 值得注意
- **Policy 显式拒绝无法被子级放宽**：原笔记举例，若对管理组施加拒绝策略，再给下层 child 分配更宽松的策略是行不通的，需先把 child 排除在外再分配宽松策略。
- **令牌与抓包数据的敏感性**：Entra ID（AAD）与 ARM 接口需使用各自目标资源对应的令牌，两者不能互换；HAR、Fiddler 会话和令牌可能包含身份验证信息，共享前应移除敏感字段。
- **登录缓存的清理方式**：原笔记建议先用 `Clear-AzContext -Scope CurrentUser`（PowerShell）或 `az account clear`（Az CLI）清除后重新登录；列出的 msal.cache 等缓存文件仅供排查旧环境参考，不要不加区分地批量删除。
- **Agent 删除只能走 REST API**：Az CLI 没有删除 agent 的命令；可通过 assignedRequest 字段判断 agent 是否正在执行 job。
