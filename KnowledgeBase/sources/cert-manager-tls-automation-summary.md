---
title: cert-manager Helm 部署与 TLS 自动化来源摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/security
  - kubernetes/tls
date: 2026-09-15
sources:
  - "[[cert-manager 实战：Helm 部署、TLS 自动签发与续期]]"
aliases:
  - cert-manager TLS 自动化摘要
---

# cert-manager Helm 部署与 TLS 自动化

## 元信息

- **原始文档**：[[cert-manager 实战：Helm 部署、TLS 自动签发与续期|cert-manager 实战：Helm 部署、TLS 自动签发与续期]]
- **领域**：Kubernetes 安全、TLS、证书自动化
- **摄入日期**：2026-09-15

## 摘要

文章按 Helm 部署、声明式证书生命周期和场景实战介绍 cert-manager 的使用方法。内容覆盖 Issuer/ClusterIssuer、Certificate/CertificateRequest、Order/Challenge、Secret 与 Ingress 的资源关系，HTTP01/DNS01 选型、Staging 到 Production 的验证路径，以及自动续期、生产安全、验收和回滚。实战部分介绍自签名 Pod TLS、Cloudflare DNS01、Azure DNS Workload Identity、通配符证书、PKCS#12 和 Helm 管理配置。

## 关键知识点

1. cert-manager 将证书申请、域名校验、Secret 写入、状态跟踪和续期转化为声明式控制循环。
2. Issuer 仅在所在 Namespace 生效，ClusterIssuer 可被全局引用；Certificate 生成的 Secret 仍位于 Certificate 所在 Namespace。
3. HTTP01 适合可公开访问 80 端口的普通域名；DNS01 支持通配符和私网入口，但必须控制 DNS API 权限与传播延迟。
4. Production 申请前应先用 Staging 验证 DNS、Ingress 与 Challenge 全链路，避免触发 CA 速率限制。
5. 续期成功后 cert-manager 更新原 Secret；生产还需监控 Certificate、CertificateRequest、Order、Challenge 和 webhook 状态。
6. 自签名、Cloudflare 和 Azure DNS 是不同信任与校验场景，不能混用其 Issuer/Solver 配置。

## 涉及的概念与实体

- [[KnowledgeBase/concepts/证书管理]]
- [[KnowledgeBase/entities/Cert-Manager]]
- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/entities/Ingress]]
- [[KnowledgeBase/entities/Helm]]

## 值得注意

- 文中的 `v1.21.1` 与 `v1.16.1` 分别来自 OCI 安装示例和既有本地 Chart 环境记录；部署时应固定并按官方兼容矩阵核对版本。
- TLS Secret 含私钥，DNS01 凭据可修改 DNS 记录，两者都应实施最小权限、审计和加密备份。
- 删除 cert-manager CRD 会连带删除对应自定义资源；升级和卸载前必须核对当前版本行为并备份。
