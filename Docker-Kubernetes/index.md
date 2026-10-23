# Docker-Kubernetes/ — 容器与编排

174 篇文档，覆盖 Docker 基础到 K8s 生产级全栈。

## 子目录结构

| 子目录 | 篇数 | 核心内容 |
|--------|------|----------|
| docker/ | 13 | Docker 基础、镜像离线分发、GPU 配置与服务部署实战 |
| k8s-basic-resources/ | 26 | Pod/健康探针/Deployment/Service/Ingress/Storage/RBAC/CRD |
| k8s-configMap-secret/ | 3 | ConfigMap/Secret 基础、跨 Namespace 同步与变更重载 |
| k8s-installation-management/ | 16 | v1.20→v1.35 安装演进、企业高可用、etcd HA |
| k8s-monitoring-logging/ | 20 | Prometheus 全栈、EFK/Loki 日志、Jaeger/SkyWalking 链路追踪 |
| k8s-CICD/ | 24 | Jenkins/ArgoCD/GitLab CI/Tekton/GitHub Actions/Pact Broker |
| k8s-networking-service-mesh/ | 7 | Ingress-Nginx/Calico/Istio 流量管理 |
| k8s-security-auth/ | 7 | Cert-Manager/External Secrets/Kyverno/OAuth2 Proxy |
| k8s-scaling/ | 6 | HPA/VPA/KEDA/KServe/Karpenter 弹性扩缩容、原生 HPA Scale-to-Zero |
| k8s-storage/ | 5 | Ceph/CubeFS/NFS 分布式存储、PV/PVC 数据保护、CSI 卷健康监控 |
| k8s-db-middleware/ | 11 | Redis/MySQL/PostgreSQL/Kafka/RabbitMQ 集群部署 |
| k8s-UI-tools/ | 8 | Dashboard/Rancher/k9s/Lens 管理工具 |
| helm-operator/ | 1 | Helm v3 工具链 |
| k8s-image-management/ | 3 | Harbor 镜像仓库与 Dragonfly P2P 分发 |
| CKA-CKS/ | 3 | 认证考试备考 |
| 其他 | 7 | K3S/KubeBlocks/Velero/GPU/SpringCloud 迁移 |

## 关键入口

- [[Docker-Kubernetes/docker/docker基础]] — Docker 入门
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源]] — K8s 架构总览
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-pod|Pod 入门]] — 容器协作、配置、生命周期与优雅退出
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-健康探针|健康探针]] — Startup/Readiness/Liveness 配置、参数与重启风暴排查
- [[Docker-Kubernetes/k8s-configMap-secret/k8s基础-configMap-Secret]] — ConfigMap 与 Secret 配置管理
- [[Docker-Kubernetes/k8s-installation-management/k8s多集群kubeconfig管理]] — 多集群 kubeconfig、kubectx/kubens 与生产防误操作
- [[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤]] — 最新版安装
- [[Docker-Kubernetes/k8s-monitoring-logging/Kubernetes原生部署Prometheus与Grafana]] — 原生部署 Prometheus 与 Grafana
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶|Prometheus-Stack：生产部署与运维]] — 监控全家桶
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础]] — GitOps 入门
- [[Docker-Kubernetes/k8s-image-management/Dragonfly与Harbor-P2P镜像分发|Dragonfly + Harbor：P2P 分发]] — Harbor 源站卸载与 AI 集群 P2P 镜像/大文件分发

## 知识库导航

→ [[KnowledgeBase/maps/kubernetes-map]] — K8s 专题地图


---
