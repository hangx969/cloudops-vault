---
title: K8s基础-自定义CRD资源
tags:
  - kubernetes
  - k8s-basics
aliases:
  - k8s自定义CRD
---

# Kubernetes CRD 与 Operator：从注册资源类型到自动管理应用

`kubectl apply` 可以创建 Deployment、Service，也可以创建 `MongoDBCommunity` 这样的自定义对象。它们使用相似的声明式接口，但背后的职责需要分开理解：CRD 让 API Server 认识新类型，Controller 根据这些对象执行操作，Operator 再把某类应用的运维规则组织进控制循环。

本文先注册一个只保存数据的 CronTab 类型，再通过 MongoDB 的历史安装案例观察 CRD、控制器与存储的配合，最后拆解一个 EtcdCluster 控制器的结构。前两部分需要了解 YAML、Pod、Service 和 PV/PVC；代码部分还需要 Go 与 Kubernetes 客户端基础。所有安装、NFS 配置和删除命令只应在隔离实验环境中使用。

## 一、先分清 CRD、CR 与 Controller

### CRD 定义类型，CR 保存一个实例

CRD（CustomResourceDefinition）是 Kubernetes 提供的 API 扩展机制，无需修改 Kubernetes 源码或编写独立 API Server，即可注册新的资源类型。比如 CRD 定义 `Database` 的字段，用户再创建名为 `orders-db` 的 Database 自定义资源，后者简称 CR（Custom Resource）。

创建 CRD 后，API Server 为启用的版本提供 REST 路径、对象校验、存储和 Watch 等通用能力。`spec.scope` 决定 CR 是 Namespaced 还是 Cluster 范围；CRD 对象本身始终是集群级的。删除命名空间会影响其中的命名空间级 CR，删除 CRD 则会影响该类型的所有实例，实验清理前应先确认数据和外部依赖。

CRD 只定义数据结构。例如定义一个 Backup 类型，并不会自动备份 Redis。需要 Controller 读取 Backup 对象，再调用备份程序或创建 Job。官方[自定义资源说明](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) 也将数据定义与控制逻辑分开讨论。

### Controller 持续调谐，Operator 包含应用运维知识

Controller 观察 CR 及关联资源，比较期望状态与当前状态，执行创建、更新或清理，并把结果写入状态。对象变更只是触发它重新检查的信号；由于通知可能重复、进程可能重启，调谐逻辑应能安全重复执行。

Operator 通常由 CRD 与应用专用 Controller 组成。它可以创建原生 Pod、Service、PVC，也可以操作集群外部系统；能力不限于组合原生对象。数据库备份、恢复、成员扩缩和故障处理都需要实际实现，不能仅因使用了 Operator 就假定自动具备这些能力。定义 CRD 本身也不会改变调度器，调度扩展需要额外实现。

### Helm 与 Operator 如何配合

| 工具 | 主要负责什么 | 使用前需要考虑什么 |
| --- | --- | --- |
| Helm | 渲染、安装和升级一组 Kubernetes 清单 | 适合配置可由模板表达的部署，也能用于安装 Operator |
| Operator | 持续执行领域专用的调谐和运维流程 | 开发与维护成本更高，需核实升级、备份恢复及兼容性 |

管理自己的无状态微服务时，Helm 往往足够；数据库等软件若需要持续运维自动化，可以评估已有 Operator。Operator 常用 Go 开发，也有 Helm、Ansible 等实现方式，并非只能使用 Go。

### 安装一个现成 Operator 的顺序

1. 从项目仓库或 OperatorHub 定位产品，并检查维护状态、支持版本与所需权限。
2. 按该版本说明安装 CRD、ServiceAccount/RBAC 和 Controller。有的安装器会一并处理，不能假定所有项目都使用同一目录布局。
3. 确认 CRD 已 Established，控制器已就绪，再创建符合 schema 的 CR。
4. 检查 CR 的 status、事件和关联资源，确认调谐产生了预期结果。

## 二、注册一个 CronTab 类型



先把类型定义写入 `crontab-crd.yaml`。`group` 与版本组成 CR 的 apiVersion；`plural` 决定 REST 资源名，`kind` 则出现在对象清单中。

~~~sh
tee crontab-crd.yaml<<'EOF'
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  #metadata.name 是用户自定义资源中自己自定义的一个名字。一般我们建议使用“顶级域名.xxx.APIGroup”这样的格式，APIGroup的名称必须与下面的spec.Group字段匹配，格式为: <plural>.<group>
  name: crontabs.stable.example.com
spec:
#spec 用于指定该 CRD 的 group、version。比如在创建 Pod 或者 Deployment 时，它的 group 可能为 apps/v1 或者 apps/v1beta1 之类，这里我们也同样需要去定义 CRD 的 API group
  group: stable.example.com
  versions:
  - name: v1
    served: true #每个版本都可以通过服务标志启用/禁用
    storage: true #必须将一个且仅有一个版本标记为存储版本。
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              cronSpec:
                type: string
              image:
                type: string
              replicas:
                type: integer
  scope: Namespaced #指定crd资源作用范围在命名空间或集群
  names: 
  #names 指的是它的 kind 是什么，比如 Deployment 的 kind 就是 Deployment，Pod 的 kind 就是 Pod，这里的 kind 被定义为了CronTab
    plural: crontabs
    singular: crontab
    kind: CronTab
    shortNames:
    - ct
EOF
~~~

然后注册 CRD，并等待 API Server 完成建立：

~~~sh
kubectl apply  -f crontab-crd.yaml
kubectl wait --for=condition=Established crd/crontabs.stable.example.com --timeout=60s
kubectl get crd
kubectl get ct
~~~

接下来创建一个 CronTab 实例。这里的名称与 cron 字段只是自定义数据，不等同于 Kubernetes 内置 CronJob：

~~~sh
tee my-crontab.yaml <<'EOF'
apiVersion: "stable.example.com/v1"
kind: CronTab
metadata:
  name: my-new-cron-object
spec:
  cronSpec: "* * * * * *"
  image: busybox
EOF
kubectl apply -f my-crontab.yaml
kubectl get CronTab
~~~

现在可以通过 `kubectl get ct` 读取这个对象，但不会出现定时任务 Pod，因为尚未部署处理 CronTab 的 Controller。这个实验用于验证“API 能保存自定义数据”这一步，而不是验证定时执行。字段的必填、范围和格式校验可继续通过 schema 或 CEL 规则约束，具体能力见官方[CRD 定义文档](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/)。

## 三、用 MongoDB 案例观察控制器与存储的配合

下面是 MongoDB Community Operator 0.5.0 的历史实验。其[原项目仓库](https://github.com/mongodb/mongodb-kubernetes-operator)已经归档，示例用来解释安装结构和 PVC 绑定过程；新部署需另行核查当前 MongoDB Operator 产品、版本和存储要求，不能把这个旧版本作为生产推荐。

先下载 `mongodb-kubernetes-operator-0.5.0.zip` 并解压。以下相对路径都以该版本源码目录为基准，创建 `mongodb` 命名空间后注册 CRD：

~~~sh
kubectl create ns mongodb
cd mongodb-kubernetes-operator-0.5.0
kubectl apply -f deploy/crds/mongodb.com_mongodbcommunity_crd.yaml
#查看mongodb是否创建成功
kubectl get crd/mongodbcommunity.mongodb.com
~~~

CRD 只提供类型，接着安装运行调谐逻辑的 Controller：

~~~sh
kubectl apply -f deploy/operator/ -n mongodb
#mongodb-kubernetes-operator这个项目是将自定义控制器和自定义资源类型分开实现的；其operator只负责创建和监听对应资源类型的变化，在资源有变化时，实例化为对应资源对象，并保持对应资源对象状态吻合用户期望状态；上述四个清单中主要是创建了一个sa账户，并对对应的sa用户授权
#operator也是以pod形式运行
kubectl get pods -n mongodb
~~~

Controller 就绪后，先检查 CR 的存储模板，再创建实例。0.5.0 的默认 PVC 使用 `ReadWriteOnce`，申请量为 `10G`，可从该版本的[StatefulSet 构建代码](https://github.com/mongodb/mongodb-kubernetes-operator/blob/v0.5.0/pkg/controller/mongodb/replica_set_controller.go)及[默认资源定义](https://github.com/mongodb/mongodb-kubernetes-operator/blob/v0.5.0/pkg/kube/resourcerequirements/resource_requirements.go)核对。后文 1Gi NFS PV 不能满足这个默认申请。

为了使用后文的静态存储实验，首次 apply 之前，在 `deploy/crds/mongodb.com_v1_mongodbcommunity_cr.yaml` 中 MongoDBCommunity 对象现有的 `spec` 下加入以下 `statefulSet` 字段，保留原来的 members、security、users 等配置和同文件中的密码 Secret。该版本会把自定义 StatefulSet 配置合并到生成结果中。

```yaml
# 加入 MongoDBCommunity.spec 的片段，不是独立资源
statefulSet:
  spec:
    volumeClaimTemplates:
    - metadata:
        name: data-volume
      spec:
        storageClassName: ""
        accessModes: [ReadWriteMany]
        resources:
          requests:
            storage: 500Mi
```

这一步必须发生在首次创建该 MongoDB CR 之前。如果已经有生成的 PVC，不要把它们改成下面的示例规格，更不要删除已有数据库卷；先读取实际的 StorageClass、容量和 accessModes，再提供匹配的 PV，或在新的空白实验环境从头运行。PVC 的这些字段通常不能事后改写，也不能用 apply 缩小存储申请。

然后创建 CR，观察控制器生成的 Pod 和 PVC：

~~~sh
cat deploy/crds/mongodb.com_v1_mongodbcommunity_cr.yaml
kubectl apply -f deploy/crds/mongodb.com_v1_mongodbcommunity_cr.yaml -n mongodb
kubectl get pods -n mongodb
# 若Pod Pending，查看PVC是否已由StatefulSet生成、是否在等待匹配PV
kubectl get pvc -n mongodb
# 只有在可丢弃的初次安装实验中才考虑重建PVC，不能用于已有数据库
# kubectl delete pvc --all -n mongodb
~~~

### 为隔离实验提供静态 PV

如果 PVC 一直 Pending，先 `describe pvc` 检查 StorageClass、容量和访问模式，不要先删除卷。本节使用 NFS 演示静态 PV 绑定。前提是服务端已安装并启动 NFS 服务，所有工作节点都安装了 NFS 客户端挂载工具，且节点到服务端的 NFS 网络已放通。RHEL/Rocky 一类系统使用 `nfs-utils` 包，Debian/Ubuntu 的客户端通常使用 `nfs-common`；下面服务命令按 RHEL 系示例，其他发行版需使用对应包和服务名。NFS 服务地址、目录和权限都应替换为实验环境配置。生产数据库需要评估文件系统语义、延迟、持久性与故障域；`no_root_squash` 会扩大客户端 root 的访问权限，不应直接使用到共享生产存储。

~~~sh
# 在专用实验NFS服务端以管理员身份准备；工作节点也需安装NFS客户端工具
dnf install -y nfs-utils
systemctl enable --now nfs-server
mkdir -p /data/p1 /data/p2 /data/p3
tee /etc/exports.d/mongodb-demo.exports <<'EOF'
/data/p1  *(rw,no_root_squash)
/data/p2  *(rw,no_root_squash)
/data/p3  *(rw,no_root_squash)
EOF
exportfs -arv
~~~

~~~sh
tee pv-demo.yaml <<'EOF'
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv-v1
  labels:
    app: example-mongodb-svc
spec:
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  storageClassName: ""
  accessModes: ["ReadWriteOnce","ReadWriteMany","ReadOnlyMany"]
  persistentVolumeReclaimPolicy: Retain
  mountOptions:
  - hard
  - nfsvers=4.1
  nfs:
    path: /data/p1
    server: 192.168.40.180
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv-v2
  labels:
    app: example-mongodb-svc
spec:
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  storageClassName: ""
  accessModes: ["ReadWriteOnce","ReadWriteMany","ReadOnlyMany"]
  persistentVolumeReclaimPolicy: Retain
  mountOptions:
  - hard
  - nfsvers=4.1
  nfs:
    path: /data/p2
    server: 192.168.40.180
---
 
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv-v3
  labels:
    app: example-mongodb-svc
spec:
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  storageClassName: ""
  accessModes: ["ReadWriteOnce","ReadWriteMany","ReadOnlyMany"]
  persistentVolumeReclaimPolicy: Retain
  mountOptions:
  - hard
  - nfsvers=4.1
  nfs:
    path: /data/p3
    server: 192.168.40.180
EOF
~~~

### 让 PVC 与静态 PV 的条件一致

PVC 的名称需要与 StatefulSet 的卷模板名、实例名和序号对应。首次创建 CR 前已配置空 StorageClass、ReadWriteMany 与 500Mi，因此后文 1Gi PV 能满足容量条件。`500M` 是十进制，`500Mi` 是二进制，此处统一使用后者。

下面展示三个 PVC 的完整清单，便于核对，也可用于在控制器创建前预绑定的独立实验。如果当前 StatefulSet 已生成同名 PVC，先读取它们并比较 spec，跳过手工 apply PVC 的命令，只创建匹配 PV；不要尝试覆盖不可变字段。

~~~sh
tee pvc-demo.yaml <<'EOF' 
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-volume-example-mongodb-0
  namespace: mongodb
spec:
  storageClassName: ""
  accessModes:
    - ReadWriteMany
  volumeMode: Filesystem
  resources:
    requests:
      storage: 500Mi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-volume-example-mongodb-1
  namespace: mongodb
spec:
  storageClassName: ""
  accessModes:
    - ReadWriteMany
  volumeMode: Filesystem
  resources:
    requests:
      storage: 500Mi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-volume-example-mongodb-2
  namespace: mongodb
spec:
  storageClassName: ""
  accessModes:
    - ReadWriteMany
  volumeMode: Filesystem
  resources:
    requests:
      storage: 500Mi
EOF
kubectl apply -f pv-demo.yaml
# 仅在这些PVC尚不存在且规格已与卷模板完全一致时使用
# kubectl apply -f pvc-demo.yaml
kubectl get pv
kubectl get pvc,pods -n mongodb
~~~



## 四、拆解 EtcdCluster 的 API 与事件处理结构

Etcd 是分布式键值存储。完整的 Etcd Operator 可以把成员创建、替换、备份与恢复组织成调谐流程，但成员扩容并不等于按 CPU 指标水平扩容普通 Web 服务；仲裁、成员变更顺序和数据恢复都需要领域逻辑。

[CoreOS etcd-operator 仓库](https://github.com/coreos/etcd-operator)已归档。本节拆解 EtcdCluster 的 CRD、镜像和事件回调结构，用于理解各部分接口；它还不是可安装的数据库产品。示意代码中引用的旧依赖 API 未形成可构建项目，也没有真正的成员管理实现；想动手开发完整控制器，可继续阅读 [[Docker-Kubernetes/k8s-basic-resources/k8s基础-Operator开发实战-Kubebuilder]]。

### 1. 定义 EtcdCluster 的数据结构

`apiextensions.k8s.io/v1` 要求结构化 schema。下面为 `replicas` 和 `storage` 添加类型与基本范围，API Server 才知道哪些字段有效。它仍然不负责启动 etcd。

~~~sh
tee etcdcluster-crd.yaml <<'EOF'
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: etcdclusters.etcd.database.coreos.com
spec:
  group: etcd.database.coreos.com
  versions:
    - name: v1alpha1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              required: [replicas, storage]
              properties:
                replicas:
                  type: integer
                  minimum: 1
                storage:
                  type: string
                  pattern: '^[1-9][0-9]*(Mi|Gi|Ti)$'
  scope: Namespaced
  names:
    plural: etcdclusters
    singular: etcdcluster
    kind: EtcdCluster
    shortNames:
      - etcd
EOF
~~~

### 2. 准备控制器的运行环境

下面 Deployment 是部署结构片段，`your-etcd-operator-image` 与 kubeconfig 路径都是占位符；示例未提供挂载、ServiceAccount/RBAC 和可运行镜像，不能直接 apply 后期望数据库出现。真正部署时应使用专用 ServiceAccount 的集群内配置，并只授予所需命名空间和资源权限。

~~~sh
tee etcd-operator.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: etcd-operator
spec:
  selector:
    matchLabels:
      app: etcd-operator
  replicas: 1
  template:
    metadata:
      labels:
        app: etcd-operator
    spec:
      containers:
        - name: etcd-operator
          image: your-etcd-operator-image
          # 添加你的Etcd Operator镜像信息
          args: ["--kubeconfig", "/path/to/kubeconfig"]
          # 根据需要添加额外的参数
EOF
~~~

构建镜像时，需要把实际控制器项目放在构建目录内，锁定兼容的 Go 模块与基础镜像。下面展示多阶段构建结构；`golang:1.16` 是旧实验版本，不能直接用于当前 controller-runtime 项目。

  ~~~dockerfile
  FROM golang:1.16 as builder
  
  WORKDIR /app
  
  # 复制Etcd Operator的代码到容器中
  COPY . .
  
  # 编译Etcd Operator
  RUN go build -o etcd-operator .
  
  # 创建最终的镜像
  FROM alpine:latest
  RUN apk --no-cache add ca-certificates
  WORKDIR /root/
  COPY --from=builder /app/etcd-operator .
  CMD ["./etcd-operator"]
  ~~~

  ~~~sh
  docker build -t your-etcd-operator-image .
  ~~~

### 3. 阅读事件回调与控制器依赖

下面的架构代码展示客户端初始化、控制器配置与 Add/Update/Delete 回调的连接方式。它不是可编译示例：`controller.NewEtcdOperator`、`controller.Operator` 及 `OnAddEtcdCluster` 等接口需要由项目实现，不能假定归档仓库提供同名 API；imports 也包含尚未使用的备份与工具包。缺少 `rest` 的导入、错误类型与实际库版本不一致都需要在真实项目中处理。

回调现在只打印事件，并不会创建 etcd Pod、PVC 或执行扩容。完整实现还需要把事件转成工作队列中的对象键，重新读取状态，幂等地执行调谐，并处理删除 tombstone、重试和退出信号。这里不使用这一骨架来验证数据库管理行为。

  ~~~go
  package main
  
  import (
  	"context"
  	"flag"
  	"fmt"
  	"log"
  	"os"
  	"path/filepath"
  	"time"
  
  	"github.com/coreos/etcd-operator/pkg/backup"
  	"github.com/coreos/etcd-operator/pkg/controller"
  	"github.com/coreos/etcd-operator/pkg/etcdapi"
  	"github.com/coreos/etcd-operator/pkg/util/constants"
  	"github.com/coreos/etcd-operator/pkg/util/k8sutil"
  	"github.com/spf13/pflag"
  	"k8s.io/apimachinery/pkg/util/wait"
  	"k8s.io/client-go/kubernetes"
  	"k8s.io/client-go/tools/clientcmd"
  )
  
  func main() {
  	kubeconfig := flag.String("kubeconfig", "", "Path to a kubeconfig file")
  	flag.Parse()
  
  	// 初始化Kubernetes客户端
  	config, err := clientcmd.BuildConfigFromFlags("", *kubeconfig)
  	if err != nil {
  		log.Fatal(err)
  	}
  	clientset, err := kubernetes.NewForConfig(config)
  	if err != nil {
  		log.Fatal(err)
  	}
  
  	// 创建EtcdOperator控制器
  	operator, err := createEtcdOperator(clientset, config)
  	if err != nil {
  		log.Fatal(err)
  	}
  
  	// 启动EtcdOperator控制器
  	err = operator.Run()
  	if err != nil {
  		log.Fatal(err)
  	}
  }
  
  func createEtcdOperator(clientset kubernetes.Interface, config *rest.Config) (*controller.Operator, error) {
  	operator := controller.NewEtcdOperator(clientset, config)
  
  	// 设置EtcdOperator的参数和配置
  	operator.Config.EtcdVolumeProvisioner = constants.DefaultEtcdVolumeProvisioner
  	operator.Config.PVProvisioner = constants.DefaultPVProvisioner
  	operator.Config.PodPolicy = constants.DefaultPodPolicy
  
  	// 设置处理EtcdCluster资源事件的回调函数
  	operator.OnAddEtcdCluster = handleEtcdClusterAdd
  	operator.OnUpdateEtcdCluster = handleEtcdClusterUpdate
  	operator.OnDeleteEtcdCluster = handleEtcdClusterDelete
  
  	return operator, nil
  }
  
  // 处理EtcdCluster资源的添加事件
  func handleEtcdClusterAdd(ctx context.Context, cluster *etcdapi.EtcdCluster) {
  	// 执行EtcdCluster资源添加事件的逻辑操作
  	fmt.Println("EtcdCluster added:", cluster.Name)
  }
  
  // 处理EtcdCluster资源的更新事件
  func handleEtcdClusterUpdate(ctx context.Context, oldCluster, newCluster *etcdapi.EtcdCluster) {
  	// 执行EtcdCluster资源更新事件的逻辑操作
  	fmt.Println("EtcdCluster updated:", newCluster.Name)
  }
  
  // 处理EtcdCluster资源的删除事件
  func handleEtcdClusterDelete(ctx context.Context, cluster *etcdapi.EtcdCluster) {
  	// 执行EtcdCluster资源删除事件的逻辑操作
  	fmt.Println("EtcdCluster deleted:", cluster.Name)
  }
  ~~~

### 4. 提交 CR 并区分 API 成功与应用成功

在完成自己的控制器实现、镜像、权限和部署后，可以提交下面的 EtcdCluster 实例。只安装 schema 也能保存这个对象，但没有调谐逻辑就不会得到 etcd 集群。先观察 CR 的创建，再分别检查控制器日志和关联工作负载，不要把两者当作同一项验证。

~~~sh
tee etcd-cluster.yaml <<'EOF'
apiVersion: etcd.database.coreos.com/v1alpha1
kind: EtcdCluster
metadata:
  name: my-etcd-cluster
spec:
  replicas: 3
  storage: 10Gi
EOF
~~~

大多数常规部署可以组合内置资源完成。需要新的声明式接口，且有人维护调谐、升级和故障恢复行为时，再考虑 CRD 与 Controller。修改 CoreDNS 或 kube-proxy 并不是开发自定义业务控制器的前提。