---
title: K8s基础-Finalizer与资源删除
tags:
  - kubernetes
  - k8s-basics
aliases:
  - K8s Finalizer
  - Finalizer与资源删除
---

# Kubernetes Finalizer：资源删除为何要等待控制器

执行 `kubectl delete` 后，对象可能仍然存在，并带上 `deletionTimestamp`。PVC 还被 Pod 使用、Operator 正在删除外部数据库，或者负责清理的控制器已停止，都可能让删除过程停下来。

Finalizer 为这类异步清理保留对象。本文先解释删除协议，再按常见阻塞原因排查，最后展示 controller-runtime 中的实现方式。阅读前需要了解资源对象、Controller 和 ownerReferences。诊断命令可以先读取状态；文中的移除 finalizer、批量清理及 `/finalize` 示例会绕过保护，只用于已核实依赖的人工恢复。

## Finalizer是什么？为什么需要它？

DELETE 请求与“对象已经消失”不是同一时刻。Pod 可能需要优雅终止，垃圾回收器可能需要处理依赖对象，控制器也可能需要先释放外部资源。Finalizer 是 API 对象上的删除等待标记，为这些工作保留执行机会。

例如，PVC 的保护 finalizer 用于避免卷仍被 Pod 使用时删除声明；底层云盘是否释放还取决于 PV 回收策略和存储驱动。LoadBalancer Service 则可能需要等待云控制器清理负载均衡器。不能从“删除 PVC”直接推断“云盘一定保留”或“一定释放”。

[Finalizer](https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/) 本身只是字符串，不包含可执行代码。API Server 标记删除并保留对象；观察该标记的 Controller 才负责执行清理并移除自己管理的条目。没有对应 Controller 的自定义字符串，会让对象一直等待。

## Finalizer的工作机制

Finalizer是资源对象 `metadata.finalizers` 字段中的一个字符串列表。当这个列表非空时，K8s不会从etcd中真正删除该对象。

整个删除流程如下：

```
1. 用户执行 kubectl delete pvc my-pvc
2. apiserver收到DELETE请求
3. 检查 metadata.finalizers 是否为空
   ├── 为空 → 按资源的宽限期、删除策略完成后删除对象
   └── 非空 → 进入Terminating状态，不删除对象
4. 设置 deletionTimestamp（标记为正在删除）
5. 对应的Controller观察到deletionTimestamp
6. Controller执行自己的清理逻辑（PVC保护需等待Pod不再使用；外部资源由相应控制器处理）
7. Controller清理完成后，从finalizers列表中移除自己的Finalizer
8. 当finalizers列表变为空 → apiserver从etcd中删除对象
```

下面是正在删除中的 PVC 状态示意。`deletionTimestamp` 由服务端设置，不能把这个片段当作新建 PVC 的 manifest。

```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
  finalizers:
  - kubernetes.io/pvc-protection    # PVC保护Finalizer
  deletionTimestamp: "2026-07-12T10:00:00Z"
  deletionGracePeriodSeconds: 0
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: ceph-block
```

这个PVC有一个 `kubernetes.io/pvc-protection` 的Finalizer。只要这个Finalizer存在，PVC就不会被真正删除。只有当PVC不再被任何Pod使用时，PVC Controller才会移除这个Finalizer，PVC才会被删除。

## 常见的Finalizer

K8s内置了一些常用的Finalizer：

| Finalizer | 作用 | 添加者 |
| --- | --- | --- |
| `kubernetes.io/pvc-protection` | 防止PVC在Pod使用中被删除 | PVC Controller |
| `kubernetes.io/pv-protection` | 防止PV在PVC绑定中被删除 | PV Controller |
| `service.kubernetes.io/load-balancer-cleanup` | 确保Service的负载均衡器被正确清理 | Service Controller |
| `foregroundDeletion` | 前台级联删除时等待阻塞删除的依赖对象 | API Server/垃圾回收控制器 |
| `orphan` | 孤儿删除模式，不自动删除依赖资源 | apiserver |

第三方 Operator 也会添加自己的条目。具体名称依版本和资源类型而变，应读取对象确认；下面保留 Argo CD 和自定义 Operator 的例子。cert-manager 不应把未经核实的 Certificate finalizer 名称当作固定约定。

```
# cert-manager：请从实际对象读取 metadata.finalizers，不假定固定 Certificate 条目

# ArgoCD的Application
metadata:
  finalizers:
  - resources-finalizer.argocd.argoproj.io

# 自定义Operator
metadata:
  finalizers:
  - my-operator.example.com/cleanup
```

## 资源"删不掉"的五大场景

### 场景一：Controller已不存在

这是最常见的情况。某个Operator创建了一堆Custom Resource，每个都带着它的Finalizer。后来Operator被卸载了，但Custom Resource还在。现在你删除这些CR，它们的Finalizer永远不会被移除，因为负责移除Finalizer的Controller已经不在了。

```
# 删除CR卡住
kubectl delete mysqlcluster my-db
# 等待...等待...一直等待...

# 查看状态
kubectl get mysqlcluster my-db -o yaml | grep finalizers
# finalizers:
# - mysql.operator.example.com/finalizer
```

### 场景二：Controller清理逻辑报错

Controller存在，但清理逻辑执行失败。比如一个Operator的Finalizer逻辑需要调用外部API删除一个云资源，但API凭证过期了，清理逻辑一直报错，Finalizer一直无法被移除。

```
# 查看Controller日志
kubectl logs -n operator-system deploy/mysql-operator

# 常见报错
ERROR: failed to delete cloud resource: Unauthorized
ERROR: Reconciler error: failed to cleanup: timeout calling API
```

### 场景三：Namespace卡在Terminating

删除Namespace时，Namespace内的所有资源都需要先被删除。如果其中任何一个资源因为Finalizer卡住，整个Namespace都会卡在Terminating状态。

```
kubectl get namespace old-project
NAME          STATUS        AGE
old-project   Terminating   120d

# 检查Namespace内残留资源
kubectl api-resources --verbs=list --namespaced -o name | \
  xargs -n 1 kubectl get -n old-project --ignore-not-found
```

### 场景四：级联删除等待带 finalizer 的子资源

在前台级联删除中，父对象可能等待子对象完成删除，而子对象的 finalizer 尚未移除。这通常是删除依赖链，不是仅因同时存在 ownerReferences 与 finalizer 就形成循环。只有清理代码反过来等待父对象消失等情况下，才可能产生实际死锁。先定位最下游阻塞对象及其 Controller。

### 场景五：Controller 无法访问 API Server

Controller 通常主动 watch API Server，而不是 API Server 回调 Controller。Controller Pod 所在节点异常、凭据失效、RBAC 不足或网络不通，都可能让它收不到事件或无法更新 finalizers。Webhook 的回调链路则是另一类问题，需要单独排查。

## 诊断与解决

### 诊断步骤

```
# 第一步：查看资源的Finalizer
kubectl get <resource> <name> -o jsonpath='{.metadata.finalizers}'
echo

# 第二步：查看deletionTimestamp
kubectl get <resource> <name> -o jsonpath='{.metadata.deletionTimestamp}'
echo

# 第三步：查看关联的Controller是否在运行
kubectl get pods -n <controller-namespace> -l app=<controller-name>

# 第四步：查看Controller日志中的错误
kubectl logs -n <controller-namespace> deploy/<controller-name> | \
  grep -i "finalizer\|cleanup\|error"

# 第五步：读取完整对象，确认 finalizer、ownerReferences 和删除状态
kubectl get <resource> <name> -o yaml
# 是否建立 watch 需要结合 Controller 配置、日志和实现判断，不能靠这一输出证明
```

### 何时才考虑人工移除 Finalizer

优先恢复 Controller 或修复外部依赖。Controller 不存在只解释了为什么卡住，不能证明可以跳过清理。人工移除前，应保存完整对象、识别每个条目对应的责任，并确认外部资源已处理，或者明确接受数据丢失、费用残留及孤立对象风险。

下面前两种方式会移除所有条目，影响其他控制器的保护；通常应只移除已经核实的那一个。

```
# 方法一：kubectl patch
kubectl patch <resource> <name> --type=merge -p '{"metadata":{"finalizers":null}}'

# 方法二：kubectl edit
kubectl edit <resource> <name>
# 手动删除 finalizers 列表中的所有条目

# 方法三：JSON Patch（精确移除特定Finalizer）
kubectl patch <resource> <name> --type=json \
  -p='[{"op":"test","path":"/metadata/finalizers/0","value":"my-operator.example.com/cleanup"},{"op":"remove","path":"/metadata/finalizers/0"}]'
```

JSON Patch 示例先用 `test` 验证索引 0 的值，防止并发修改后删错条目；应替换成对象中的真实值与索引。删除正在使用的卷相关保护，除了泄漏外还可能带来数据风险。

### 批量盘点与受控清理

批量移除会跳过多个控制器的清理流程。下面保留循环处理方式，默认只列出候选对象；只有逐项核对后，才在隔离恢复环境中显式设置 `ALLOW_REMOVE_FINALIZERS=true`。它不是日常清理脚本。

```
#!/bin/bash
# 批量清理某个Namespace中所有卡在Terminating的资源

set -euo pipefail
NAMESPACE="old-project"
ALLOW_REMOVE_FINALIZERS="${ALLOW_REMOVE_FINALIZERS:-false}"

# 获取所有带Finalizer的Terminating资源
kubectl api-resources --verbs=list --namespaced -o name | while read -r resource; do
  kubectl get "$resource" -n "$NAMESPACE" -o json | \
    jq -r '.items[] | select(.metadata.deletionTimestamp != null) | "\(.kind)/\(.metadata.name)"' | \
    while read -r item; do
      echo "候选对象：$item"
      if [ "$ALLOW_REMOVE_FINALIZERS" = "true" ]; then
        kubectl patch "$item" -n "$NAMESPACE" --type=merge \
          -p '{"metadata":{"finalizers":null}}'
      fi
    done
done
```

### Namespace 的特殊 finalize 接口

Namespace 还可能因 API 发现失败或 APIService 不可用而卡住，先查看 Namespace 的 Conditions、残留资源和对应控制器。它的 `spec.finalizers` 通过 `/finalize` 接口处理；强行清空可能留下命名空间内的孤立对象。仅在这些风险已核实并接受后使用下列恢复方式。

```
# 方法一：保留对象结构，仅清空 Namespace 的 spec.finalizers
kubectl get namespace <name> -o json | \
  jq '.spec.finalizers = []' | \
  kubectl replace --raw "/api/v1/namespaces/<name>/finalize" -f -

# 方法二：如使用第三方 Krew 插件，先确认名称、来源和实现
kubectl krew search finalizer
# 旧笔记中的 ns-remove-finalizer 不是 Kubernetes 内置命令，
# 不能假定当前 Krew 索引一定提供它；核实后才安装和使用
```

## 编写自己的Finalizer

下面给出 controller-runtime 的控制流程。`examplev1.MyResource` 是项目生成的 API 类型（Spec 需要有 `DatabaseName string`），`DatabaseClient` 是需要由项目实现并注入的外部数据库接口；因此这是一份带明确依赖的控制器骨架，不是独立可运行程序。实现顺序可对照 [Kubebuilder 的 finalizer 示例](https://book.kubebuilder.io/reference/using-finalizers.html)。

```
package controllers

import (
    "context"
    "fmt"
    "errors"
    "time"

    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
    "sigs.k8s.io/controller-runtime/pkg/log"
    "sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
    apierrors "k8s.io/apimachinery/pkg/api/errors"

    examplev1 "example.com/api/v1"
)

const myFinalizerName = "my-operator.example.com/finalizer"

// 实际 SDK 适配层应把外部“数据库不存在”转换成这个错误。
var ErrDatabaseNotFound = errors.New("database not found")

type DatabaseClient interface {
    DeleteDatabase(ctx context.Context, name string) error
}

type MyResourceReconciler struct {
    client.Client
    DB DatabaseClient
}

// +kubebuilder:rbac:groups=example.com,resources=myresources,verbs=get;list;watch;update;patch
// +kubebuilder:rbac:groups=example.com,resources=myresources/finalizers,verbs=update
// markers 的 API group/resource 请替换成项目实际定义。

func (r *MyResourceReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var resource examplev1.MyResource
    if err := r.Get(ctx, req.NamespacedName, &resource); err != nil {
        if apierrors.IsNotFound(err) {
            return ctrl.Result{}, nil
        }
        return ctrl.Result{}, err
    }

    // 检查是否正在删除
    if !resource.DeletionTimestamp.IsZero() {
        // 资源正在被删除，执行清理逻辑
        return r.reconcileDelete(ctx, &resource)
    }

    // 资源正常存在，确保Finalizer已添加
    if !controllerutil.ContainsFinalizer(&resource, myFinalizerName) {
        controllerutil.AddFinalizer(&resource, myFinalizerName)
        if err := r.Update(ctx, &resource); err != nil {
            return ctrl.Result{}, err
        }
    }

    // 正常调谐逻辑...
    return ctrl.Result{}, nil
}

func (r *MyResourceReconciler) reconcileDelete(ctx context.Context, resource *examplev1.MyResource) (ctrl.Result, error) {
    if !controllerutil.ContainsFinalizer(resource, myFinalizerName) {
        return ctrl.Result{}, nil
    }

    // 1. 执行外部资源清理
    if err := r.cleanupExternalResources(ctx, resource); err != nil {
        // 清理失败，不移除Finalizer，等待下次调谐重试
        log.FromContext(ctx).Error(err, "failed to cleanup external resources")
        return ctrl.Result{RequeueAfter: 30 * time.Second}, nil  // 30秒后重试
    }

    // 2. 清理成功，移除Finalizer
    controllerutil.RemoveFinalizer(resource, myFinalizerName)
    if err := r.Update(ctx, resource); err != nil {
        return ctrl.Result{}, err
    }

    log.FromContext(ctx).Info("resource cleaned up successfully", "name", resource.Name)
    return ctrl.Result{}, nil
}

func (r *MyResourceReconciler) cleanupExternalResources(ctx context.Context, resource *examplev1.MyResource) error {
    // 清理外部资源，例如删除云盘、释放负载均衡器等
    // 必须是幂等的！因为可能被多次调用
    
    // 示例：删除外部数据库
    if r.DB == nil {
        return fmt.Errorf("database client is not configured")
    }
    err := r.DB.DeleteDatabase(ctx, resource.Spec.DatabaseName)
    if err != nil && !errors.Is(err, ErrDatabaseNotFound) {
        return fmt.Errorf("delete database: %w", err)
    }
    
    return nil
}
```

编写Finalizer时的关键原则：

第一，清理逻辑必须幂等。 Controller可能在清理失败后多次重试，清理逻辑必须能安全地执行多次。

第二，清理失败时不要移除Finalizer。 只有在确认所有外部资源都已清理完毕后，才移除Finalizer。失败时返回 `RequeueAfter` ，让Controller稍后重试。

第三，给Finalizer起一个唯一的名字。 使用 `域名/功能` 的格式，避免与其他Operator的Finalizer冲突。

第四，处理部分清理的情况。 如果有多个外部资源需要清理，记录清理进度，下次重试时跳过已清理的资源。

## Finalizer与Graceful Shutdown的关系

Finalizer和 `preStop` 钩子、 `terminationGracePeriodSeconds` 经常被混淆，它们的作用层次不同：

| 机制                          | 作用层级         | 触发时机              |
|-------------------------------|-----------------|----------------------|
| preStop hook                  | Pod级别         | Pod被删除时           |
| terminationGracePeriodSeconds | Pod级别         | Pod删除超时强制杀死    |
| Finalizer                     | 资源对象级别      | 资源对象被删除时       |
| OwnerReference + Garbage Collection | 资源关系级别 | 父资源删除级联子资源    |

Finalizer 保留 API 对象供 Controller 完成清理，`preStop` 和终止宽限期控制容器退出。带 finalizer 的 Pod 在被标记删除后也可能开始终止，不能把两者理解为严格串行的“先 finalizer、后停进程”。`kubectl delete --force` 也不等于自动清空 finalizers。

## 从删除状态定位下一步

看到 `deletionTimestamp` 后，先记录 finalizers 和 ownerReferences，再找到负责该条目的 Controller。Controller 正常时检查其权限与外部 API；Controller 已卸载时，优先恢复同一版本并完成清理。只有外部依赖已核对、正常路径无法恢复时，才考虑精确移除已确认的条目。

开发控制器时则要反向检查这条链路：先持久化自己的 finalizer，再创建外部依赖；清理必须可重试，失败保留条目，成功后只移除自己管理的条目。这样即使 Controller 在中途重启，也能从 API 状态继续处理。
