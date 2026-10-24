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
- [[Docker-Kubernetes/k8s-basic-resources/01-k8s基础-架构-组件-资源]] — K8s 架构总览
- [[Docker-Kubernetes/k8s-basic-resources/03-k8s基础-pod基础|Pod 入门]] — 容器协作、配置、生命周期与优雅退出
- [[Docker-Kubernetes/k8s-basic-resources/04-k8s基础-pod-健康探针|健康探针]] — Startup/Readiness/Liveness 配置、参数与重启风暴排查
- [[Docker-Kubernetes/k8s-configMap-secret/k8s基础-configMap-Secret]] — ConfigMap 与 Secret 配置管理
- [[Docker-Kubernetes/k8s-installation-management/k8s多集群kubeconfig管理]] — 多集群 kubeconfig、kubectx/kubens 与生产防误操作
- [[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤]] — 最新版安装
- [[Docker-Kubernetes/k8s-monitoring-logging/Kubernetes原生部署Prometheus与Grafana]] — 原生部署 Prometheus 与 Grafana
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶|Prometheus-Stack：生产部署与运维]] — 监控全家桶
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础]] — GitOps 入门
- [[Docker-Kubernetes/k8s-image-management/Dragonfly与Harbor-P2P镜像分发|Dragonfly + Harbor：P2P 分发]] — Harbor 源站卸载与 AI 集群 P2P 镜像/大文件分发

## Kubernetes 基础资源系列：建议发布顺序

26 篇按同一条学习路线编号。先使用已有实验集群，理解 API 对象、工作负载、访问和存储，再处理运维与扩展开发；最后三篇回到运行时、集群引导和网络实现。Namespace 一篇包含配额与 QoS，因此放在 Pod 和工作负载之后。

1. [[Docker-Kubernetes/k8s-basic-resources/01-k8s基础-架构-组件-资源|Kubernetes 架构入门：从一次应用部署认识组件与资源]]：先认识控制平面、工作节点，以及一次部署请求经过的组件。
2. [[Docker-Kubernetes/k8s-basic-resources/02-k8s基础-yaml-apply|从 YAML 到 kubectl apply：读懂清单，也读懂字段由谁管理]]：读懂资源清单、常见字段，以及 apply 的合并与字段管理方式。
3. [[Docker-Kubernetes/k8s-basic-resources/03-k8s基础-pod基础|Kubernetes Pod 入门：从容器协作到生命周期管理]]：理解容器协作边界、启动过程、生命周期与优雅退出。
4. [[Docker-Kubernetes/k8s-basic-resources/04-k8s基础-pod-健康探针|Kubernetes 健康探针：从配置原理到重启风暴排查]]：区分启动、就绪和存活，理解探针参数与重启风暴。
5. [[Docker-Kubernetes/k8s-basic-resources/05-k8s基础-pod调度-标签与选择器实战|K8s 标签与选择器避坑：5 条规则与生产案例]]：用标签描述资源，再用选择器建立资源之间的对应关系。
6. [[Docker-Kubernetes/k8s-basic-resources/06-K8s基础-pod调度-亲和力|K8s基础-Pod调度-亲和力]]：理解节点选择、亲和性、污点与容忍，排查调度约束。
7. [[Docker-Kubernetes/k8s-basic-resources/07-k8s基础-deployment|Deployment：从副本管理到滚动更新、蓝绿与金丝雀发布]]：从副本数量进入滚动更新、回滚、蓝绿和金丝雀发布。
8. [[Docker-Kubernetes/k8s-basic-resources/08-k8s基础-daemonset|DaemonSet：让指定节点各运行一份后台组件]]：让每个符合条件的节点运行一份日志或监控代理。
9. [[Docker-Kubernetes/k8s-basic-resources/09-k8s基础-job-cronjob|Job 与 CronJob：在 Kubernetes 中运行一次性和定时任务]]：组织一次性与定时任务，处理重试、并发、备份和权限。
10. [[Docker-Kubernetes/k8s-basic-resources/10-k8s基础-namespace-资源分配|Kubernetes Namespace 与资源分配：给团队划边界，也给资源设预算]]：在理解工作负载后，再设置团队边界、配额、默认值和 QoS。
11. [[Docker-Kubernetes/k8s-basic-resources/11-k8s基础-Service|Kubernetes Service：从稳定入口到服务发现与流量转发]]：为应用建立稳定访问入口，理解 DNS、端口与 EndpointSlice。
12. [[Docker-Kubernetes/k8s-basic-resources/12-k8s基础-ingress|Kubernetes Ingress：从 HTTP 路由到灰度发布与故障排查]]：把 HTTP 路由、TLS、认证和灰度放到入口链路中；旧 ingress-nginx 案例带维护边界。
13. [[Docker-Kubernetes/k8s-basic-resources/13-k8s基础-storage|Kubernetes 存储入门：从 Volume 到 PV、PVC、CSI 与扩容]]：从临时目录、节点磁盘到 PV/PVC、CSI、动态供应与扩容。
14. [[Docker-Kubernetes/k8s-basic-resources/14-k8s基础-statefulset|StatefulSet：为有状态应用保留身份、存储和更新顺序]]：在已有网络与存储知识上，理解稳定身份、独立卷与有状态更新。
15. [[Docker-Kubernetes/k8s-basic-resources/15-k8s基础-容器设计模式-Sidecar-Init-Ambassador-Adapter|K8s 四种容器设计模式]]：按启动时机和数据路径组合 Init、Sidecar、Ambassador 与 Adapter。
16. [[Docker-Kubernetes/k8s-basic-resources/16-k8s基础-临时容器ephemeral|Kubernetes 临时容器：不用重建 Pod，也能进入现场排障]]：为缺少工具的运行中 Pod 加入诊断容器，保留故障现场。
17. [[Docker-Kubernetes/k8s-basic-resources/17-k8s-PodDisruptionBudget实战|Kubernetes PDB 实战：让节点维护留出可用副本]]：为节点维护配置 Eviction 预算，并区分维护与发布策略。
18. [[Docker-Kubernetes/k8s-basic-resources/18-k8s基础-认证-授权-准入|Kubernetes 认证、授权与准入：一次 API 请求如何获得许可]]：串起身份、凭据、RBAC 与准入，按实际运维动作配置权限。
19. [[Docker-Kubernetes/k8s-basic-resources/19-k8s-APIServer深度剖析-请求链路-认证授权-生产调优|K8s API Server：请求链路、认证授权与生产调优]]：深入写入、Watch、APF、审计和控制平面故障定位。
20. [[Docker-Kubernetes/k8s-basic-resources/20-k8s基础-Finalizer与资源删除|Kubernetes Finalizer：资源删除为何要等待控制器]]：理解资源删除等待、外部清理，以及人工恢复的边界。
21. [[Docker-Kubernetes/k8s-basic-resources/21-k8s基础-自定义CRD资源|Kubernetes CRD 与 Operator：从注册资源类型到自动管理应用]]：区分 CRD、CR 与 Controller，观察自定义 API 和运维逻辑。
22. [[Docker-Kubernetes/k8s-basic-resources/22-Python调用k8s-api实现资源管理|用 Python 管理 Kubernetes 资源：从连接集群到增删改查]]：通过 Python 客户端完成查询、创建、修改和定名删除实验。
23. [[Docker-Kubernetes/k8s-basic-resources/23-k8s基础-Operator开发实战-Kubebuilder|Kubebuilder：从零开发 K8s Operator]]：实现一个小型 Operator，练习事件映射、调谐与状态回写。
24. [[Docker-Kubernetes/k8s-basic-resources/24-k8s基础-容器运行时-containerd|containerd 如何在 Kubernetes 节点上运行容器]]：回到节点，理解 CRI、containerd、shim/runc 和排障工具。
25. [[Docker-Kubernetes/k8s-basic-resources/25-k8s基础-kubeadm|kubeadm 做了什么：初始化流程、证书和集群升级]]：梳理初始化、证书与升级流程，连接前面学到的控制平面机制。
26. [[Docker-Kubernetes/k8s-basic-resources/26-k8s基础-Calico|Calico 入门：Pod 跨节点通信、BGP 与隧道封装]]：从 Pod 跨节点通信继续深入 BGP、IPIP/VXLAN、地址池与网络策略。

## 知识库导航

→ [[KnowledgeBase/maps/kubernetes-map]] — K8s 专题地图


---
