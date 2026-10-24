---
title: "Kubebuilder：从零开发 K8s Operator"
source: "https://mp.weixin.qq.com/s/Ts9MxQOpQVaUtw6YbHXogw"
created: 2026-06-28
tags:
  - kubernetes
  - operator
  - kubebuilder
  - crd
  - go
---

# Kubebuilder：从零开发 K8s Operator

<div id="从零开发-kubernetes-operatorkubebuilder-实战教程" class="legacy-anchor"></div>
<div id="从零开发-kubernetes-operator" class="legacy-anchor"></div>

一个自定义对象能通过 API 保存配置，却不会自动执行任务。要让配置变化转成实际行为，需要一个控制器反复检查对象，并把观察结果或执行结果写回。Kubebuilder 会生成 API 类型、控制器入口和部署文件，开发者再补上领域逻辑。

本文实现一个较小的例子：Foo 对象在同一命名空间寻找指定名称的 Pod，存在时将 `status.happy` 设为 true，不存在时设为 false。这个控制器只观察对象，不创建数据库或业务 Pod，适合先学会资源注册、事件映射和状态更新。阅读前需要 Go 基础、CRD 概念和一个可丢弃的测试集群。

## 什么是 Operator？

Operator 将应用的部署、升级或恢复规则编码到控制循环中。它既可以管理内置工作负载，也可以通过自定义 API 表达领域需求；执行能力取决于具体实现。

例如，Operator 可以在 Kubernetes 中部署和维护 MySQL、Elasticsearch 或 GitLab Runner 等工具，自动配置这些工具，根据事件调整系统状态，并对故障做出反应。

Operator 由两个组件组成：

- CRD（Custom Resource Definition）：Kubernetes 自定义类型的资源蓝图，用于描述其规范（Spec）和状态（Status）。CRD 的实例称为自定义资源（CR）
- Controller（控制器）：持续监视集群状态，并根据事件做出变更，目标是将资源的当前状态变为用户在 CR Spec 中定义的期望状态

Reconcile 每次都以对象的当前状态为依据。事件只负责把对象键加入队列，控制器不能假定收到一次事件就只运行一次；重复事件、失败重试和进程重启都要求调谐逻辑保持幂等。

Manager 负责组织缓存、客户端、控制器和进程生命周期。一个 Manager 可以注册多个控制器；同一进程中的控制器通常共享缓存，不需要各自全量拉取资源。

## 构建 Operator

可以直接使用 controller-runtime，也可以使用 Kubebuilder 或 Operator SDK 生成项目。本文按 Kubebuilder 的 Go 项目结构编写；工具版本与 Go、Kubernetes 客户端依赖需要配套，不能把不同年代的脚手架和代码片段混用。

### 开发环境准备

```bash
# 必备工具
# Go：按选定Kubebuilder发布版与生成go.mod的要求安装；当前快速开始要求v1.24.6+
# Docker 17.03+
# kubectl：与测试集群版本兼容
# Kubernetes：使用选定controller-runtime支持的测试版本，可用kind搭建

# 安装 kubebuilder
curl -L -o kubebuilder https://go.kubebuilder.io/dl/latest/$(go env GOOS)/$(go env GOARCH) \
  && chmod +x kubebuilder \
  && mv kubebuilder /usr/local/bin/

# 验证
kubebuilder version
```

安装前可核对 [Kubebuilder 快速开始](https://book.kubebuilder.io/quick-start.html) 的版本要求。上面的 `latest` 下载方式用于首次体验；团队项目应记录并固定 Kubebuilder 发布版，同时以提交的 `go.mod`、`go.sum` 锁定依赖。下面的控制器使用当前 `Watches(object, handler)` 接口，不能配合旧版 `source.Kind{Type: ...}` 写法。

### 初始化项目

```bash
# 在空目录中初始化项目；生成Go模块、Makefile、配置与入口
mkdir foo-operator
cd foo-operator
kubebuilder init --domain my.domain --repo my.domain/tutorial

# 创建新的 API（CRD）和 Controller
kubebuilder create api --group tutorial --version v1 --kind Foo
# 提示创建 CRD 和 Controller 时均按 yes
```

生成的项目结构（Go 项目）：

```
├── cmd/main.go      # 项目入口，设置并运行管理器
├── config/          # K8s 部署 Operator 的 manifest
├── Dockerfile       # 构建管理器镜像的容器文件
├── api/v1/          # Foo CRD 定义
└── internal/controller/  # Foo 控制器
```

### 自定义 CRD

`spec.name` 表示要寻找的 Pod 名称。查找范围限定在 Foo 所在命名空间；这里的“找到”仅表示 Pod 对象存在，不表示它处于 Ready 或 Running。`status.observedGeneration` 则记录控制器已经处理到哪一代配置。保留脚手架生成的 group/version 注册文件，并将 `foo_types.go` 中的 API 类型补为以下内容：

```go
// api/v1/foo_types.go
package v1

import (
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// FooSpec defines the desired state of Foo
type FooSpec struct {
    // Name of the friend Foo is looking for
    // +kubebuilder:validation:MinLength=1
    Name string `json:"name"`
}

// FooStatus defines the observed state of Foo
type FooStatus struct {
    // Happy will be set to true if Foo found a friend
    Happy bool `json:"happy"`
    ObservedGeneration int64 `json:"observedGeneration,omitempty"`
}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status

// Foo is the Schema for the foos API
type Foo struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`

    Spec   FooSpec   `json:"spec"`
    Status FooStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true
// FooList contains a list of Foo.
type FooList struct {
    metav1.TypeMeta `json:",inline"`
    metav1.ListMeta `json:"metadata,omitempty"`
    Items []Foo `json:"items"`
}

func init() {
    SchemeBuilder.Register(&Foo{}, &FooList{})
}
```

### 实现 Controller

控制器先读取 Foo，再按同一命名空间和名称 Get Pod。读取出错时返回错误重试；只有明确 NotFound 才认为不存在，避免把 API 连接或权限故障写成 `happy=false`。状态没有变化时不重复写回，减少无意义的自身事件。

控制器还监听 Pod 事件，把发生变化的 Pod 映射到引用它的 Foo。这样创建或删除 jack Pod 时，相关 Foo 都会重新检查。下面使用当前[资源 Watch 的事件映射方式](https://book.kubebuilder.io/reference/watching-resources/predicates-with-watch.html)。

```go
// internal/controller/foo_controller.go
package controller

import (
    "context"
    "time"

    corev1 "k8s.io/api/core/v1"
    apierrors "k8s.io/apimachinery/pkg/api/errors"
    "k8s.io/apimachinery/pkg/runtime"
    "k8s.io/apimachinery/pkg/types"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
    "sigs.k8s.io/controller-runtime/pkg/handler"
    "sigs.k8s.io/controller-runtime/pkg/log"
    "sigs.k8s.io/controller-runtime/pkg/reconcile"

    tutorialv1 "my.domain/tutorial/api/v1"
)

type FooReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

// 此控制器只读Foo和Pod，只写Foo状态，不需要对象创建/删除权限。
// +kubebuilder:rbac:groups=tutorial.my.domain,resources=foos,verbs=get;list;watch
// +kubebuilder:rbac:groups=tutorial.my.domain,resources=foos/status,verbs=get;update;patch
// +kubebuilder:rbac:groups="",resources=pods,verbs=get;list;watch

func (r *FooReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    logger := log.FromContext(ctx)
    var foo tutorialv1.Foo
    if err := r.Get(ctx, req.NamespacedName, &foo); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    if !foo.DeletionTimestamp.IsZero() {
        return ctrl.Result{}, nil
    }

    var friend corev1.Pod
    err := r.Get(ctx, types.NamespacedName{
        Namespace: foo.Namespace,
        Name: foo.Spec.Name,
    }, &friend)
    if err != nil && !apierrors.IsNotFound(err) {
        return ctrl.Result{}, err
    }
    friendFound := err == nil

    if foo.Status.Happy != friendFound || foo.Status.ObservedGeneration != foo.Generation {
        foo.Status.Happy = friendFound
        foo.Status.ObservedGeneration = foo.Generation
        if err := r.Status().Update(ctx, &foo); err != nil {
            return ctrl.Result{}, err
        }
        logger.Info("updated Foo status", "happy", friendFound)
    }

    // 周期复查作为事件映射失败等情况的恢复路径。
    return ctrl.Result{RequeueAfter: time.Minute}, nil
}

func (r *FooReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&tutorialv1.Foo{}).
        Watches(&corev1.Pod{}, handler.EnqueueRequestsFromMapFunc(r.mapPodsReqToFooReq)).
        Complete(r)
}

func (r *FooReconciler) mapPodsReqToFooReq(ctx context.Context, obj client.Object) []reconcile.Request {
    var list tutorialv1.FooList
    if err := r.List(ctx, &list, client.InNamespace(obj.GetNamespace())); err != nil {
        log.FromContext(ctx).Error(err, "unable to list Foo for Pod event")
        return nil
    }

    requests := make([]reconcile.Request, 0)
    for _, foo := range list.Items {
        if foo.Spec.Name == obj.GetName() {
            requests = append(requests, reconcile.Request{
                NamespacedName: types.NamespacedName{
                    Namespace: foo.Namespace,
                    Name: foo.Name,
                },
            })
        }
    }
    return requests
}
```

### 生成清单并运行

API 类型变化后先生成 DeepCopy 代码，再生成 CRD 与 RBAC。`make install` 会修改当前 kubeconfig 指向的集群，只能对测试集群执行；`make run` 则在本机运行控制器，并使用本机凭据，不代表已经验证集群内 ServiceAccount 权限。


```bash
# 1. 更新生成代码与清单
make generate
make manifests
go test ./...

# 2. 安装 CRD 到集群
make install
kubectl get crds
# foos.tutorial.my.domain

# 3. 运行控制器（也可部署为集群中的 Deployment）
make run
```

### 用两个 Foo 检查状态变化

将下面清单保存为 `foo-samples.yaml`。Foo 与测试 Pod 都放在当前命名空间；如改用其他命名空间，后续命令统一加 `-n`。

```yaml
# 创建两个 Foo 自定义资源
apiVersion: tutorial.my.domain/v1
kind: Foo
metadata:
  name: foo-01
spec:
  name: jack    # 寻找名为 jack 的 Pod
---
apiVersion: tutorial.my.domain/v1
kind: Foo
metadata:
  name: foo-02
spec:
  name: joe     # 寻找名为 joe 的 Pod
```

```bash
kubectl apply -f foo-samples.yaml
# 此时两个 Foo 的 happy 状态都为 false（没有同名 Pod）

# 将下文的测试Pod保存为jack-pod.yaml后部署
kubectl apply -f jack-pod.yaml
# 控制器检测到 Pod 创建事件 → 触发 foo-01 的 reconciliation → happy 变为 true
# foo-02 不受影响（它的朋友是 joe）

# 修改 foo-02 的 spec.name 为 jack
kubectl patch foo foo-02 --type=merge -p '{"spec":{"name":"jack"}}'
# 控制器触发 reconciliation → foo-02 的 happy 也变为 true

# 测试资源可丢弃时删除jack Pod，两个Foo最终都会回到false
kubectl delete pod jack
kubectl get foos -o custom-columns=NAME:.metadata.name,FRIEND:.spec.name,HAPPY:.status.happy,OBSERVED:.status.observedGeneration
```

测试 Pod 的清单如下。它只为创建和删除事件提供一个可观察对象，不需要进入容器执行命令。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: jack
spec:
  containers:
  - name: web
    image: nginx:1.28
```

启动控制器后，先确认两个 Foo 的 `observedGeneration` 已追上 `metadata.generation`。创建 jack 后只有 foo-01 变为 true，修改 foo-02 后两者均为 true，删除 jack 后均为 false。状态是异步更新的，应等待下一次调谐，不能要求 apply 返回时已经完成。

## 从教学控制器走向应用管理

- 为 `spec.name` 建立字段索引，避免每次 Pod 事件遍历命名空间内所有 Foo；不要依赖事件不会重复。
- 在集群内使用专用 ServiceAccount，并按需要设置 namespace-scoped cache、Role 和 RoleBinding；生成的 ClusterRole 不代表必须全局绑定。
- 在日志中记录 Foo 的命名空间、名称、generation 和查找结果，便于区分 Pod 不存在与 API 读取失败。
- 为无法读取目标 Pod 等持续故障定义 status condition；如产生 Kubernetes Event，避免每轮重试都重复发送。
- 添加 `additionalPrinterColumns`，让 `kubectl get foos` 直接显示目标 Pod、happy 和 observedGeneration。
- 测试 Pod 与 Foo 同名但不同命名空间、读取错误、Pod 删除及状态未变化时不写回等分支，再用测试集群检查 watch 链路。

## Operator 开发工具对比

| 工具 | 定位 | 语言 | 说明 |
|------|------|------|------|
| Kubebuilder | API与控制器项目脚手架 | Go | 生成类型、控制器和部署文件 |
| OperatorSDK | Red Hat 主导 | Go/Ansible/Helm | 支持多种方式构建 Operator |
| controller-runtime | 底层库 | Go | Kubebuilder/OperatorSDK 的底层依赖，可从头构建 |
| Metacontroller | 轻量级 | 任意语言 | 通过 Webhook 方式，用任意语言实现控制器逻辑 |

选择框架后，先固定生成器和依赖版本，再保存可重复的生成、构建与测试流程。这个 Foo 示例验证的是读取、事件映射和状态回写；真正管理外部应用时，还需要补充 ownerReferences、finalizer、错误条件、升级和恢复流程。
