---
title: CRD
tags:
  - knowledgebase/concept
  - kubernetes/extensibility
date: 2026-05-04
sources:
  - "[[Docker-Kubernetes/k8s-basic-resources/21-k8s基础-自定义CRD资源]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/Operator部署Redis集群]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/Operator部署mysql集群]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/helm部署strimzi-kafka]]"
aliases:
  - Custom Resource Definition
  - CustomResourceDefinition
  - 自定义资源定义
---

# CRD

## 定义

CRD（CustomResourceDefinition）是 Kubernetes 提供的 API 扩展机制，允许用户在不修改 K8s 源码的前提下向 API Server 注册全新的资源类型。创建 CRD 后，K8s 会自动为其生成 RESTful API 路径，用户可以像操作原生资源（Pod、Service）一样对自定义资源进行 CRUD 操作。

## 核心要点

- CRD 自 Kubernetes 1.7 引入，取代了此前的 ThirdPartyResource，是 K8s 声明式 API 扩展的标准方式
- CRD 本身是集群级资源（无命名空间），但通过 `scope` 字段可指定其自定义资源是 Namespaced 还是 Cluster 级别
- 删除命名空间时会级联删除该命名空间下的所有自定义资源实例
- CRD 的 `metadata.name` 格式约定为 `<plural>.<group>`，例如 `crontabs.stable.example.com`
- CRD 单独存在仅定义了数据模型，需要配合 Controller 才能实现业务逻辑（CRD + Controller = Operator）

## 与其他概念的关系

- [[KnowledgeBase/concepts/Operator模式]]：CRD 是 Operator 模式的基础组件，CRD 定义资源模型，Controller 实现控制逻辑
- [[KnowledgeBase/entities/Kubernetes]]：CRD 是 K8s 原生的 API 扩展机制
- [[KnowledgeBase/concepts/StorageClass]]：StorageClass 本身也是通过类似的扩展机制注册到 K8s API 的
- [[KnowledgeBase/concepts/Finalizer]]：自定义资源实例可携带 Finalizer，Namespace 级联删除该资源时若对应 Controller 未移除 Finalizer，会导致删除卡住

## 在本仓库中的覆盖

- [[Docker-Kubernetes/k8s-basic-resources/21-k8s基础-自定义CRD资源]]：CRD 的完整定义、创建步骤和 crontab 自定义资源示例
- [[Docker-Kubernetes/k8s-db-middleware/Operator部署Redis集群]]：RedisCluster CRD 的实际使用
- [[Docker-Kubernetes/k8s-db-middleware/Operator部署mysql集群]]：NdbCluster CRD 的实际使用
- [[Docker-Kubernetes/k8s-db-middleware/helm部署strimzi-kafka]]：Kafka、Topic、User 等 CRD 资源的创建

## 知识空白

- CRD 的版本管理（多版本共存、Conversion Webhook）
- CRD 的校验机制（OpenAPI v3 Schema、Admission Webhook）
- CRD 开发工具链（kubebuilder、Operator SDK 的 CRD 生成）
- CRD 的性能与规模限制
