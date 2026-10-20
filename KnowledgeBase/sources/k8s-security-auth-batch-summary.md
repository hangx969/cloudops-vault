---
title: k8s-security-auth 来源批量摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/security
date: 2026-10-20
sources:
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署capsule]]"
  - "[[cert-manager 实战：Helm 部署、TLS 自动签发与续期]]"
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署external-secrets]]"
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter]]"
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署oauth2proxy]]"
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署sonarqube]]"
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署trivy-operator]]"
  - "[[k8s容器安全上下文-SecurityContext]]"
aliases:
  - "k8s-security-auth 批量摘要"
  - "K8s 安全认证批量摘要"
---

## 元信息

- **原始目录**: `Docker-Kubernetes/k8s-security-auth/`
- **文档数量**: 本批次收录 8 篇（`k8s-security-auth/` 目录现有 9 篇）
- **领域**: Kubernetes 安全、认证授权、证书管理、策略引擎、代码质量与镜像扫描、容器安全上下文
- **摄入日期**: 2026-04-17

## 摘要

本目录涵盖 Kubernetes 集群安全与认证授权领域的核心工具，包括多租户管理（Capsule）、证书自动化管理（Cert-Manager）、外部密钥同步（External Secrets）、策略引擎（Kyverno）、身份认证代理（OAuth2 Proxy）、代码质量扫描（SonarQube）以及容器镜像漏洞扫描（Trivy Operator）。所有工具均通过 Helm Chart 方式部署，文档覆盖了从下载配置到企业级使用的完整流程。

## 关键知识点

1. Capsule 以 Tenant CRD 将一组 Namespace 逻辑分组并统一施加 RBAC、Resource Quota、Network Policy；Tenant Owner 必须属于 Capsule User Group（`capsuleUserGroups`），可通过证书 O 字段、外部 IdP 组或 ServiceAccount 配置。
2. Cert-Manager 签发链路为 Issuer/ClusterIssuer → Certificate/CertificateRequest → Order/Challenge → TLS Secret → Ingress/Pod；ACME 覆盖 HTTP01 与 DNS01，生产流程包括 Staging 验证、自动续期、到期监控与 Webhook/Challenge 排障。
3. External Secrets Operator 由 SecretStore/ClusterSecretStore 指定外部密钥源与认证方式、ExternalSecret 定义同步映射，`refreshInterval` 控制拉取频率；对接 Azure Key Vault 支持 Managed Identity 与 Workload Identity。
4. Kyverno 作为 Admission Controller 拦截 API 请求，支持 validate/mutate/generate 三类策略，Policy Reporter 提供策略执行结果的 GUI。
5. OAuth2 Proxy 可作为独立反向代理或 Ingress-Nginx Middleware 运行，链路为 Nginx 路由 → OAuth2 Proxy 认证 → Redis 会话存储。
6. Trivy Operator 采用 Client-Server 模式（trivy-operator 执行扫描、trivy-server 提供漏洞库），产出 VulnerabilityReport 与 ConfigAuditReport；漏洞库是 OCI Image，需用 oras 下载而非 docker pull。
7. SecurityContext 分 Pod 级与容器级，容器级覆盖 Pod 级；推荐基线为 `drop: ALL` + 按需 `add: NET_BIND_SERVICE`、`allowPrivilegeEscalation: false`、`readOnlyRootFilesystem: true`，seccomp 使用 RuntimeDefault，fsGroupChangePolicy 使用 `OnRootMismatch`。
8. Pod 安全标准分 Privileged/Baseline/Restricted 三级：Baseline 允许 13 种 capabilities，Restricted 仅允许 NET_BIND_SERVICE。

## 各文档摘要

### [[Docker-Kubernetes/k8s-security-auth/helm部署capsule|Helm 部署 Capsule]]

**核心内容**: Capsule 是 K8s 多租户管理工具，通过 Tenant CRD 将一组 Namespace 逻辑分组，并对其实施 RBAC、Resource Quota、Network Policy 等策略。

- Tenant：一组 Namespace 的逻辑分组，支持权限分配与隔离
- capsuleUserGroups 配置可操作 Capsule 的用户组
- Tenant Owner 需属于 Capsule User Group（通过证书 O 字段、外部 IdP 组或 ServiceAccount 配置）
- 用户认证通过 OpenSSL 证书（CN/O 字段）+ kubeconfig 实现

### [[cert-manager 实战：Helm 部署、TLS 自动签发与续期|Helm 部署 Cert-Manager]]

**核心内容**: Cert-Manager 是 K8s 全能证书管理工具，支持基于 ACME 协议与 Let's Encrypt 签发免费证书并自动续期。

- 证书分类：Root CA、中间 CA、终端实体证书
- 核心链路：Issuer/ClusterIssuer → Certificate/CertificateRequest → Order/Challenge → TLS Secret → Ingress/Pod
- 支持 Self-signed、ACME（Let's Encrypt）、内部 CA、Vault、Venafi 等 Issuer 类型
- ACME 同时覆盖 HTTP01 与 DNS01，并保留 Cloudflare、Azure DNS Workload Identity 和通配符证书实战
- 生产流程包括 Staging 验证、自动续期、到期监控、Webhook/Challenge 排障、验收与回滚
- Helm 同时保留 OCI Chart 和本地 Chart 两种安装路径；版本固定并按实际环境核对兼容矩阵
- 详见 [[KnowledgeBase/sources/cert-manager-tls-automation-summary|cert-manager TLS 自动化来源摘要]]

### [[Docker-Kubernetes/k8s-security-auth/helm部署external-secrets|Helm 部署 External Secrets]]

**核心内容**: External Secrets Operator 从外部密钥提供商（如 Azure Key Vault）读取 Secrets 并同步写入 K8s Secrets。

- 核心资源：ClusterSecretStore/SecretStore（指定外部密钥源和认证方式）、ExternalSecret（定义同步映射）
- 集成 Azure Key Vault：支持 Managed Identity 和 Workload Identity 认证
- refreshInterval 控制拉取频率（如 1h）
- 支持 ChinaCloud 环境配置

### [[Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter|Helm 部署 Kyverno 和 Policy Reporter]]

Kyverno 在准入阶段验证或变更资源，也可以按触发事件生成配套资源；Policy Reporter 单独读取报告，提供 UI 与通知。

- Helm 配置区分历史 Chart 与应用版本；HA 按控制器设置副本、PDB 和资源保障。
- 十组策略覆盖镜像、运行权限、资源、标签、探针、Service、默认配置注入及命名空间资源生成；Harbor 限制与通用仓库校验合并说明。
- CEL MutatingPolicy 按命名空间与仓库允许列表改写 Artifactory 镜像地址，覆盖普通容器和初始化容器。
- 策略按 common 和 region 管理；先 Audit，再按业务范围切换 Enforce，明确后台扫描、服务端 dry-run、CLI 测试与 GitOps 差异的边界。
- 1.18 公告包含 HTTP 安全加固、CLI 扩展、策略引擎与镜像验证改进、Policies Chart 配置、N-1 支持及 CEL 迁移方向。

### [[Docker-Kubernetes/k8s-security-auth/helm部署oauth2proxy|Helm 部署 OAuth2 Proxy]]

**核心内容**: OAuth2 Proxy 是 K8s 应用的身份认证反向代理，支持 Middleware 模式作用于 Ingress-Nginx，集成 GitHub 等 OAuth 提供商。

- 两种工作模式：独立反向代理 / Ingress-Nginx Middleware
- sessionStorage 使用 Redis 存储用户会话状态
- 集成 GitHub OAuth App：配置 Client ID/Secret、Cookie Secret
- 架构：Nginx 路由 -> OAuth2 Proxy 认证 -> Redis 会话存储

### [[Docker-Kubernetes/k8s-security-auth/helm部署sonarqube|Helm 部署 SonarQube]]

**核心内容**: SonarQube 是开源代码质量管理系统，支持多语言（Java、C#、JavaScript、Python 等）的自动化代码质量检测。

- 检测能力：错误、漏洞、代码异味（Code Smell）
- 可集成到 CI/CD 流程中实现持续代码质量改进
- 通过 Cert-Manager 创建 HTTPS 证书
- 配置 Ingress（nginx-default）暴露服务

### [[Docker-Kubernetes/k8s-security-auth/helm部署trivy-operator|Helm 部署 Trivy Operator]]

**核心内容**: Trivy Operator 是容器镜像漏洞扫描器，以 Client-Server 模式在集群中运行，自动扫描工作负载的镜像安全漏洞。

- Client-Server 模式：trivy-operator（扫描执行）+ trivy-server（漏洞数据库）
- 报告类型：VulnerabilityReport（镜像漏洞）、ConfigAuditReport（配置安全）
- Vulnerability DB 是 OCI Image，需使用 oras 工具下载（非 docker pull）
- 支持离线环境的漏洞数据库部署

### [[k8s容器安全上下文-SecurityContext|K8s 容器安全上下文：从入门到生产避坑]]

**核心内容**: Security Context 生产实战完全指南，覆盖 UID/GID 管理、Linux Capabilities、特权模式、sysctl、seccomp、Pod 安全标准（PSS）三级策略。

- Security Context 两级配置：Pod 级通用身份 + 容器级特殊权限，容器级覆盖 Pod 级
- UID/GID 6 个核心字段：runAsUser/runAsGroup/runAsNonRoot/fsGroup/fsGroupChangePolicy/supplementalGroups
- fsGroupChangePolicy 生产用 `OnRootMismatch`（减少递归、提升启动速度）
- v1.35 GA：`supplementalGroupsPolicy: Strict` 消除镜像 `/etc/group` 隐式组安全隐患
- Capabilities 最佳实践：`drop: ALL` + 按需 `add: NET_BIND_SERVICE`，配合 `allowPrivilegeEscalation: false` + `readOnlyRootFilesystem: true`
- 特权模式三条铁律：默认禁止、99% 场景用 capabilities 替代、privileged 会让 seccomp 失效
- allowPrivilegeEscalation 陷阱：hostPath/CSI 卷可能隐式授予 CAP_SYS_ADMIN 导致该字段不生效
- sysctl 安全列表（v1.32，13 个参数含内核版本要求）、不安全 sysctl 三步启用流程
- seccomp 三种 Profile（Unconfined/RuntimeDefault/Localhost）、生产用 RuntimeDefault 即可
- Pod 安全标准三级策略：Privileged/Baseline/Restricted，Baseline 允许 13 种 capabilities，Restricted 仅允许 NET_BIND_SERVICE
- 6 个常见故障排查（runAsNonRoot 冲突、fsGroup 卷权限、不安全 sysctl、特权端口绑定、只读文件系统、seccomp 与特权互斥）

## 涉及的概念与实体

- [[KnowledgeBase/concepts/多租户]]: Capsule Tenant 实现 Namespace 级别的多租户隔离
- [[KnowledgeBase/concepts/证书管理]]: Cert-Manager 自动化 TLS 证书签发与续期
- [[KnowledgeBase/concepts/Secrets管理]]: External Secrets 外部密钥同步到 K8s
- [[KnowledgeBase/concepts/策略即代码]]: Kyverno 以 CRD 方式定义集群策略
- [[KnowledgeBase/concepts/身份认证]]: OAuth2 Proxy 统一身份认证代理
- [[KnowledgeBase/concepts/镜像安全]]: Trivy 容器镜像漏洞扫描
- [[KnowledgeBase/entities/Capsule]]: K8s 多租户管理工具
- [[KnowledgeBase/entities/Cert-Manager]]: 证书管理工具
- [[KnowledgeBase/entities/External-Secrets]]: 外部密钥同步工具
- [[KnowledgeBase/entities/Kyverno]]: K8s 策略引擎
- [[KnowledgeBase/entities/OAuth2-Proxy]]: 身份认证反向代理
- [[KnowledgeBase/entities/SonarQube]]: 代码质量管理平台
- [[KnowledgeBase/entities/Trivy]]: 镜像漏洞扫描器
- [[KnowledgeBase/entities/Azure-Key-Vault]]: 外部密钥提供商

## 交叉主题发现

1. **安全工具链协同**: Kyverno（准入控制）+ Trivy（镜像扫描）+ SonarQube（代码扫描）构成了从代码到运行时的完整安全防线。
2. **证书与 Ingress 联动**: Cert-Manager 为 SonarQube、Goldilocks 等工具生成 TLS 证书，与 `k8s-networking-service-mesh` 目录的 Ingress-Nginx 紧密配合。
3. **认证与 Ingress 集成**: OAuth2 Proxy 通过 Ingress-Nginx 的 auth-url/auth-signin annotation 实现统一认证，`k8s-scaling` 目录的 Goldilocks 也使用了同样的认证集成模式。
4. **密钥管理闭环**: External Secrets 从 Azure Key Vault 同步密钥到 K8s，CI/CD 工具（Jenkins Credentials）和应用（Helm values）均可引用这些 K8s Secrets。
5. **多租户与 RBAC**: Capsule 的多租户隔离与 K8s 原生 RBAC 配合，为企业级集群的团队协作提供了安全边界。

## 值得注意

- 安全字段可能失效：特权模式或拥有 `CAP_SYS_ADMIN` 时 `allowPrivilegeEscalation` 始终为 true，而 hostPath/CSI 卷可能隐式授予该权能；`privileged: true` 会让 seccomp 失效，二者不应同时使用。
- 版本边界：`supplementalGroupsPolicy` 于 v1.35 GA，v1.33 Beta 阶段的行为变更会让 kubelet 拒绝在无法确保该策略的节点上运行 Pod，从 v1.32 及更早版本升级前需查阅官方升级注意事项；sysctl 安全列表按 v1.32 整理。
- Kyverno 迁移：1.18 无破坏性变更，但 ClusterPolicy 弃用计划仍在推进，应开始迁移到新的策略类型；命名空间级策略发起的 HTTP 调用默认被禁用。
- Cert-Manager 上线顺序：先用 Let's Encrypt Staging 验证再切 Production，且两者使用不同名称的 Issuer；文中 `v1.21.1` 为写作时的示例版本，部署前需确认稳定版本并核对 Kubernetes 兼容矩阵。
