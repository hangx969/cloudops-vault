---
title: ArgoCD 同步故障排查
source:
  - "https://mp.weixin.qq.com/s/n4sgO6fcouZ-QyDdulRHaQ"
author:
  - WAKEUP技术
published: 2026-09-20
created: 2026-10-04
date: 2026-10-04
tags:
  - kubernetes
  - argocd
  - gitops
  - troubleshooting
aliases:
  - ArgoCD 同步踩 5 坑
  - ArgoCD 同步与漂移排查
---

# ArgoCD 同步故障排查

ArgoCD 同步时，需要对比 Git 中渲染出的期望状态与集群实际状态。两者出现差异、资源迟迟未就绪、API 拒绝更新或清单移除后触发 prune，都需要先定位原因，再决定怎么处理。排查可从差异比较、资源健康、API 更新、prune 删除和控制面性能五个方面展开。

先阅读 [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础|ArgoCD 基础]]，了解 Application 和同步策略；多集群目录、权限与发布批次设计见 [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD多集群GitOps实战|Argo CD 多集群 GitOps 实战]]。Helm 渲染阶段的 DNS 故障见 [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD部署Helm应用时域名解析失败问题排查与解决|ArgoCD Helm 部署：域名解析故障处理]]。

> [!info] 示例与案例范围
> 三个案例来自 WAKEUP技术《ArgoCD 同步踩 5 坑》，其中的时间、数量和效果为作者描述，尚未复现验证。参数和行为说明依据 2026-10-04 的官方文档与代码。YAML 片段只展示相关字段，需要并入已有配置；示例名称、仓库、资源额度和策略须按实际环境调整。

## 同步、差异和健康状态

先区分三种状态：`OutOfSync` 表示期望状态与 live 状态有差异；同步操作的 `Failed` 表示某次执行失败；`Progressing` 是资源健康状态，表示尚未达到健康检查的条件。应用可以已经 `Synced`，健康状态仍是 `Progressing`。

> [!note] 三方模型的适用范围
> 三方模型适用于传统 diff 和 Client-side Apply：Git 提供期望状态，live 是当前对象，`kubectl.kubernetes.io/last-applied-configuration` 保存上次应用的配置。ArgoCD 还支持其他 [diff 策略](https://argo-cd.readthedocs.io/en/stable/user-guide/diff-strategies/)，SSA 也使用字段所有权；健康检查、prune 和渲染性能各有机制，不能都归为三方合并失败。

## 一、OutOfSync 反复出现

反复漂移可能来自以下几处：Helm 模板含随机函数，或渲染输入没有固定；API Server、准入 Webhook 为对象补入默认字段，例如 Service 的 `clusterIP`、Pod 的 `securityContext`；HPA 或其他控制器改写 `replicas`、`env` 等字段；聚合 ClusterRole 的 `rules` 随成员角色变化；多种工具管理同一对象后，last-applied 注解也需要核对。这些因素是否真的造成差异，要以 `argocd app diff` 的输出为准。

先修正不确定的渲染输入和错误清单。确认某些字段由其他控制器负责后，再用 `spec.ignoreDifferences` 忽略这些字段。常用方式是 `jsonPointers`、`jqPathExpressions` 和 `managedFieldsManagers`，下面只展示相关 Application 字段。

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  ignoreDifferences:
    # 写法一：jsonPointers，按 JSON 指针精确忽略
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas
      # managedFieldsManagers 让某 manager 写的字段不参与 diff
      managedFieldsManagers:
        - kube-controller-manager
    # 写法二：jqPathExpressions，用 jq 表达式忽略
    - group: ""
      kind: Service
      jqPathExpressions:
        - .spec.clusterIP
        - .spec.healthCheckNodePort
    # 聚合 ClusterRole：只忽略控制器维护的 rules
    - group: rbac.authorization.k8s.io
      kind: ClusterRole
      name: system:aggregated-metrics-reader
      jsonPointers:
        - /rules
  syncPolicy:
    syncOptions:
      - RespectIgnoreDifferences=true
    automated:
      selfHeal: true
      prune: true
```

HPA 接管 Deployment 副本数时，集群里的 `replicas` 可能与 Git 中固定的值不同。可以把忽略规则限制到具体名称和命名空间：

```yaml
spec:
  ignoreDifferences:
    - group: apps
      kind: Deployment
      name: my-app
      namespace: default
      jsonPointers:
        - /spec/replicas
  syncPolicy:
    syncOptions:
      - RespectIgnoreDifferences=true
```

先查看差异和参数，再决定需要哪条忽略规则：

```bash
# 显示 Git 期望与 live 的差异，直接定位漂移字段
argocd app diff my-app

# 查看应用参数；完整渲染结果仍需单独检查
argocd app get my-app --show-params

# 比较两份已保存的 reconciliation 结果（路径需替换）
argocd admin app diff-reconcile-results /path/to/result1 /path/to/result2
```

不同版本和 diff 工具的输出格式可能不同，不应把原文的 `0 files changed, 0 bytes`、`Sync OK` 或 `1 more diffs` 当成固定验收标准。应检查具体字段差异、应用同步状态和最近一次操作结果。

> [!note] 管理命令的参数
> `argocd admin app diff-reconcile-results` 比较的是两份已保存的 reconciliation 结果，参数是 `PATH1 PATH2`，不能直接传一个应用名。普通应用排查先用 `argocd app diff my-app`。见 [命令参考](https://argo-cd.readthedocs.io/en/stable/user-guide/commands/argocd_admin_app_diff-reconcile-results/)。

怀疑字段被其他控制器或人工操作改过时，可以查看 live 对象的 `managedFields`。只列出 manager 名称还不能证明某个字段由谁管理；进一步检查对应的 `fieldsV1`，再判断该忽略差异还是调整管理方式。last-applied 注解则用于核对上次 Client-side Apply 的配置。

```bash
# 列出 managedFields 中的 manager；字段归属还需查看 fieldsV1
kubectl get deployment my-app -n default -o jsonpath='{.metadata.managedFields[*].manager}'

# 看 last-applied 注解里存了什么，对比 Git 差异
kubectl get deployment my-app -n default \
  -o jsonpath='{.metadata.annotations.kubectl\.kubernetes\.io/last-applied-configuration}' | jq .
```

`argocd app set my-app --ignore-differences json:apps/Deployment:default/my-app:/spec/replicas` 不是当前官方命令参考支持的用法，其中 `--ignore-differences` 选项不存在。差异规则应写入前面的 Application YAML。需要确认本地 CLI 支持哪些参数时，先查看帮助：

```bash
argocd app set --help
```

`managedFieldsManagers` 忽略 live 对象中指定 manager 所拥有字段的差异，范围可能比一个 JSON 指针更大。manager 名称应从实际对象读取；HPA、metrics-server 和准入 Webhook 的职责不同，不能把它们都当成 `kube-controller-manager`。如果清单同时由 kubectl 和 ArgoCD 管理，应先厘清字段归属。last-applied 注解需要检查，但不能仅因它存在就删除。

> [!note] 忽略比较与忽略同步
> `ignoreDifferences.all` 不是 Application 支持的字段。上面的示例只忽略聚合 ClusterRole 的 `/rules`。若要在整个 ArgoCD 实例忽略聚合角色的规则变化，可使用 `argocd-cm` 的 `resource.compareoptions.ignoreAggregatedRoles`，见 [差异配置](https://argo-cd.readthedocs.io/en/stable/user-guide/diffing/)。`ignoreDifferences` 默认只影响 diff；同步时也要保留 live 字段，需要 `RespectIgnoreDifferences=true`，且该选项在资源已存在时才生效。

## 二、同步卡住或健康状态停在 Progressing

资源停在 `Progressing` 时，先检查它的就绪条件、事件和控制器日志。例如 Ingress 或 LoadBalancer Service 的地址尚未填入、Job 尚未完成、Certificate 尚未 Ready，都会影响健康状态。

> [!note] 先查已有健康检查
> ArgoCD 对 Service、Ingress、Job 等有内置健康检查，仓库也包含 Certificate 的检查，不能一律视为“不认识这些资源”。先核对所用版本的检查逻辑和对象 `status`，再考虑自定义。见 [Resource Health](https://argo-cd.readthedocs.io/en/stable/operator-manual/health/) 和 [Certificate 检查实现](https://github.com/argoproj/argo-cd/blob/master/resource_customizations/cert-manager.io/Certificate/health.lua)。CRD 定义与由它创建的 CR 也应区分，通常需要判定的是 CR 的就绪状态。

确实需要调整规则时，可以在 `argocd-cm` 中配置 Lua 健康检查。原文的 Certificate 示例在 `Ready=True` 时返回 `Healthy`，其他情况保持 `Progressing`：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  resource.customizations.health.cert-manager.io_Certificate: |
    hs = {}
    hs.status = "Progressing"
    hs.message = "Waiting for certificate"
    if obj.status ~= nil then
      if obj.status.conditions ~= nil then
        for i, condition in ipairs(obj.status.conditions) do
          if condition.type == "Ready" and condition.status == "True" then
            hs.status = "Healthy"
            hs.message = "Certificate is ready"
            return hs
          end
        end
      end
    end
    return hs
```

自定义资源的配置键是 `resource.customizations.health.<group>_<Kind>`。脚本应按控制器实际提供的 `status.phase` 或 `status.conditions` 判断，而不是假定所有 CR 都有同样的状态字段。

> [!note] Lua 标准库与示例范围
> `resource.customizations.useOpenLibs.cert-manager.io_Certificate: "true"` 会开放 Lua 标准库，并非“引入官方 open health 库”。上面的脚本不依赖这些标准库，无需启用。上面的最小示例没有区分 `Ready=False` 等失败条件，不应不经评估就覆盖已有检查。

下面的 Job 自定义检查展示了 Lua 的写法：当 `succeeded >= completions` 时返回 `Healthy`，当 `failed > backoffLimit` 时返回 `Degraded`。

> [!warning] Job 示例的边界
> Job 已有内置检查。这段脚本依赖 `spec.completions` 和 `spec.backoffLimit` 显式存在，也没有完整处理 Job 的 `Complete`、`Failed` 条件和暂停状态。它可能把已结束的 Job 留在 `Progressing`；实际排障应优先使用内置检查，不应直接覆盖。

```yaml
resource.customizations.health.batch_Job: |
  hs = {}
  hs.status = "Progressing"
  hs.message = "Job is running"
  if obj.status ~= nil then
    if obj.spec.completions ~= nil and obj.status.succeeded ~= nil then
      if obj.status.succeeded >= obj.spec.completions then
        hs.status = "Healthy"
        hs.message = "Job completed"
        return hs
      end
    end
    if obj.status.failed ~= nil and obj.spec.backoffLimit ~= nil then
      if obj.status.failed > obj.spec.backoffLimit then
        hs.status = "Degraded"
        hs.message = "Job failed"
        return hs
      end
    end
  end
  return hs
```

更新健康检查后，重新刷新应用并观察资源状态是否变化；仍未生效时，再检查 application-controller 日志。标准安装通常使用 StatefulSet，若部署方式或名称不同，日志命令也要相应调整：

```bash
# 查看同步与健康状态
argocd app get my-app
# 若仍未生效，检查控制器日志（名称与类型按安装方式调整）
kubectl logs -n argocd statefulset/argocd-application-controller | grep -i health
```

CLI 超时、跳过缺失类型的 dry-run、只应用 OutOfSync 资源，是三个不同的控制点。原文列出的命令可以分别使用：

```bash
# 限制本次 CLI 等待时长，不会跳过健康判断
argocd app sync my-app --timeout 300

# 配置缺失类型时跳过 dry-run，以及只应用 OutOfSync 资源
argocd app set my-app --sync-option SkipDryRunOnMissingResource=true
argocd app set my-app --sync-option ApplyOutOfSyncOnly=true
```

后两项也可以写入 Application：

```yaml
spec:
  syncPolicy:
    syncOptions:
      - SkipDryRunOnMissingResource=true
      - ApplyOutOfSyncOnly=true
```

> [!note] 这些选项不会跳过健康等待
> `--timeout 300` 限制 CLI 等待时长，不会把资源变成 Healthy；`SkipDryRunOnMissingResource=true` 只处理缺失资源类型时的 dry-run；`ApplyOutOfSyncOnly=true` 只减少 apply 的资源范围，选择性同步也不执行 hooks。若第三方控制器没有提供可判断的状态，需要明确健康标准，而不是靠这几个选项掩盖问题。

## 三、同步失败：不可变字段、版本冲突与资源缺失

`field is immutable`、`metadata.resourceVersion: Invalid value` 和 `The Kubernetes API could not find` 应分别排查。它们可能涉及不可变字段、更新请求中的版本信息或缺失的资源类型，不能都归为“资源被别人管理”。StatefulSet 的 `volumeClaimTemplates`、Service 的 `clusterIP` 和 Job 的 `spec.template` 都有更新限制，具体允许修改的字段还要对照 Kubernetes 版本和资源类型。

`Replace=true` 适用于选择 replace/create 方式更新资源，例如配置过大、不适合放入 last-applied 注解时；它本身不能绕过 API 对不可变字段的校验。下面的 Application 示例包含 `project` 和应用级同步策略，使用前要评估对整个应用的影响：

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  project: default
  source:
    repoURL: https://github.com/example/repo.git
    path: manifests
    targetRevision: HEAD
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    syncOptions:
      - Replace=true
      - PruneLast=true
      - CreateNamespace=true
    automated:
      selfHeal: false
      prune: true
```

原文还使用了应用级强制同步命令：

```bash
# 强制 apply 可能删除重建；执行前须确认影响范围
argocd app sync my-app --force
```

`PruneLast=true` 将 prune 放到其他资源已部署、健康且前面的波次成功之后；它不保证同名资源重建时没有中断。`CreateNamespace=true` 创建 Application 的目标命名空间。

> [!warning] replace 与删除重建不同
> `Replace=true` 使用 replace/create；明确删除再创建资源的选项是 `Force=true,Replace=true`，通常应限制到已确认可重建的资源。`argocd app sync --force` 也不是普通重试。重建 Service 可能改变 ClusterIP 并造成断连，有状态资源还涉及 PVC 与数据恢复。见 [同步选项](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/)。

`resourceVersion` 报错要结合完整消息判断。版本过旧导致的并发更新通常返回 `409 Conflict`；`Invalid value` 不足以证明只是并发。先检查 Git 或渲染清单是否带入服务端管理的元数据、当前 live 对象和更新请求，再处理重试或字段归属。`--force` 不能被理解为重新 GET 并解除“三方合并锁”，也不应因此直接删除 last-applied 注解。见 [Kubernetes 更新机制](https://kubernetes.io/docs/reference/using-api/api-concepts/#updates-to-existing-resources)。

修改 StatefulSet 的 `volumeClaimTemplates`，例如 `storageClassName` 或 `accessModes`，可能需要重新创建 StatefulSet，并单独规划存储迁移。原文提出“缩容到 0、删除 StatefulSet 时保留 PVC、再用新模板重建”的维护思路；它需要确认 PVC 保留策略和备份，且保留的 PVC 不会因为新模板就自动改变存储类或访问模式。`Replace=true` 不等于直接删除 StatefulSet。

若报错是 API 找不到资源类型，则应检查 CRD 是否安装、版本是否匹配，以及 CRD 与 CR 的同步顺序；强制替换不能补上缺失的 API。

## 四、prune 误删生产资源

开启 `automated.prune: true` 后，应用原来管理的资源若不再出现在渲染出的期望清单中，ArgoCD 可以将其删除。`selfHeal: true` 处理的是 live 偏离 Git 的情况，也可能覆盖人工热修。目录迁移、应用拆分或恢复操作前，需要一起检查这两项设置。

关闭自动 prune 可显式设置 `automated.prune: false`。下面的示例还包含应用级 `Prune=false` 默认选项，并列出 prune 的顺序和传播策略：

```yaml
spec:
  syncPolicy:
    automated:
      prune: false
    syncOptions:
      - Prune=false            # 应用级默认跳过 prune
      - PruneLast=true         # 即使开启也最后再删
      - PrunePropagationPolicy=foreground
```

对关键资源，可以用注解阻止它在同步过程中被 prune；这种保护不等于保护所有删除路径：

```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-options: Prune=false
```

Helm 的资源保留注解示例：

```yaml
metadata:
  annotations:
    "helm.sh/resource-policy": keep
```

> [!note] Helm keep 与 prune 保护的区别
> 当前 ArgoCD 将 `helm.sh/resource-policy: keep` 对应到 `Delete=false`，用于 Application 删除时保留资源；它不能替代同步阶段的 `Prune=false`。需要二次确认 prune 时，可使用资源注解 `argocd.argoproj.io/sync-options: Prune=confirm`。见 [Helm 注解映射](https://argo-cd.readthedocs.io/en/stable/user-guide/helm/) 与 [同步选项](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/)。

AppProject 限制的是来源仓库、目标集群、命名空间和允许管理的资源类型。它能缩小管理范围，但不是对已允许资源的删除确认。下面的示例将 Deployment 列入命名空间级白名单，并明确来源仓库和目标命名空间：

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: prod-project
  namespace: argocd
spec:
  sourceRepos:
    - https://github.com/example/repo.git
  clusterResourceWhitelist:
    - group: ""
      kind: Namespace
  namespaceResourceWhitelist:
    - group: apps
      kind: Deployment
    - group: ""
      kind: Service
    - group: networking.k8s.io
      kind: Ingress
    - group: batch
      kind: Job
  # 明确禁止 ArgoCD 触碰这些高危险资源
  clusterResourceBlacklist:
    - group: "rbac.authorization.k8s.io"
      kind: ClusterRoleBinding
  destinations:
    - server: https://kubernetes.default.svc
      namespace: "prod-*"
```

## 五、同步慢、repo-server 负载高或 Webhook 未配置

同步变慢可能发生在变更发现、清单渲染、状态刷新或同步操作不同阶段。先检查 Git/Webhook、repo-server 和 application-controller 的耗时、队列与 CPU/内存，再决定扩容哪一部分。原文提到“几十个 Application 就打满 CPU”，这是对特定负载的描述，不能当成统一容量上限。

Git Webhook 可以让 push 触发应用刷新，减少等待轮询的时间。GitHub/GitLab 的 Payload URL 使用 `https://<argocd-domain>/api/webhook`；GitHub 的 Content type 选 `application/json`。共享密钥存放在 `argocd-secret`：GitHub 对应 `webhook.github.secret`，GitLab 对应 `webhook.gitlab.secret`，不是原文所写的 `argocd-cm`。具体设置也可参照基础篇的 [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础#配置git webhook|Git Webhook 配置]] 和 [官方说明](https://argo-cd.readthedocs.io/en/stable/operator-manual/webhook/)。

原文给出的 repo-server 扩容与资源请求/上限如下。controller 片段只有 requests，没有 limits；它们都是 Helm values 示例，需按当前 Chart 和实测负载调整：

```yaml
repoServer:
  replicas: 3
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: "1"
      memory: 2Gi
controller:
  resources:
    requests:
      cpu: 250m
      memory: 1Gi
```

可以先查看仓库信息，但 `argocd repo get` 本身不会修改缓存配置：

```bash
# 查看仓库信息（请替换实际仓库 URL）
argocd repo get https://github.com/example/repo.git
```

可用 app-of-apps 或 ApplicationSet 拆分应用，避免一个 Application 渲染上千资源；也可以按业务组织仓库，缩小单次比较的范围。Git 目录生成器为各目录生成独立 Application，便于单独同步。下面的示例设置了生成器的 `revision`，目标命名空间使用 `prod-` 前缀，以匹配前面的 AppProject：

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: services-set
  namespace: argocd
spec:
  generators:
    - git:
        repoURL: https://github.com/example/repo.git
        revision: HEAD
        directories:
          - path: services/*        # 每个子目录生成一个 Application
  template:
    metadata:
      name: "{{path.basename}}"
    spec:
      project: prod-project
      source:
        repoURL: https://github.com/example/repo.git
        path: "{{path}}"
        targetRevision: HEAD
      destination:
        server: https://kubernetes.default.svc
        namespace: "prod-{{path.basename}}"
      syncPolicy:
        syncOptions:
          - CreateNamespace=true
        automated:
          prune: false
          selfHeal: false
```

`status-processors` 和 `operation-processors` 分别控制状态刷新与同步操作队列的并发。所引用的官方配置中，默认值分别为 20 和 10，不能都按 10 理解。缓存与并发参数应配置在 `argocd-cmd-params-cm`：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cmd-params-cm
  namespace: argocd
data:
  controller.status.processors: "30"
  controller.operation.processors: "20"
  reposerver.repo.cache.expiration: "24h"
```

> [!note] 调参位置和效果
> `repo.cache.expiration`、`status.processors` 和 `operation.processors` 不能直接作为 `argocd-cm` 中的键使用；缓存和并发应按上面的 `argocd-cmd-params-cm` 示例配置。官方配置的 manifest 缓存默认已经是 24h，因此显式设为 24h 不代表增加缓存或一定提速；并发提高后也可能增加 API 和 CPU 压力。按安装方式确认参数怎样注入进程，并让相关进程重新加载。见 [参数 ConfigMap](https://argo-cd.readthedocs.io/en/stable/operator-manual/argocd-cmd-params-cm-yaml/) 和 [高可用与扩容](https://argo-cd.readthedocs.io/en/stable/operator-manual/high_availability/)。轮询周期也不是固定 3 分钟；当前配置示例是 `timeout.reconciliation: 120s` 加最多 `timeout.reconciliation.jitter: 60s`，需检查实际配置。Webhook 是加快变更发现的手段，不等于自动禁用轮询。

## 生产环境注意事项

1. 按资源作用域配置 AppProject：集群级和命名空间级规则分别控制。普通业务团队通常不需要管理 ClusterRoleBinding、Node 或 PV。
2. 多集群部署按团队、环境和目标划定 AppProject，再配合 RBAC 限制操作范围。原文建议每个 destination 单独建项目，这是可选隔离方式，不是平台要求。
3. Secret 不以明文进入 Git。可使用 Sealed Secrets 加密，或让 External Secrets 从 Vault、受支持的云端 Secret 服务读取；ArgoCD 编排相应 CR。集群仍会保存解密后的 Kubernetes Secret，不能把“不在 Git 保存明文”理解为集群中没有明文。
4. 开启 selfHeal 后，人工修改可能被恢复。应急热修时先明确同步策略、配置控制来源和回写 Git 的步骤，不要依赖固定几秒的时间窗口。
5. 生产资源按需要关闭自动 prune，或为关键资源设置 `Prune=confirm`。foreground 传播策略依赖 Kubernetes 的 ownerReferences 关系，不保证任意业务依赖的删除顺序。
6. repo-server 和 controller 的资源请求、上限及副本数按负载设置。增加 controller 副本还要配合分片配置，不是简单堆副本。
7. 为关键自定义资源确认有效的健康检查；已有检查满足要求时直接使用，避免仅为消除 Progressing 就无条件判为 Healthy。
8. 备份 ArgoCD 的 Application、AppProject 和必要配置。bootstrap Application 能声明管理配置，但不能替代备份及恢复验证。
9. 按官方高可用方案部署 argocd-server 和 Redis，并配置适当的 PodDisruptionBudget。原文的“所有组件至少 2 副本”不适用于所有 HA 拓扑，Redis 模式和 controller 分片需分别设计。
10. 自动同步变更合并前先渲染清单，再做 schema/策略校验和差异审查。`argocd app diff` 检查差异，kubeconform/kubeval 检查结构，二者不是同一类校验。
11. 用 Application 的 `info` 字段标注负责人和告警入口，便于排障联系。
12. 确保 CRD 在 CR 创建时可用，可以预先安装，或在同次同步中安排顺序；同次同步中存在 CRD 时 ArgoCD 可自动跳过对应 CR 的 dry-run。`SkipDryRunOnMissingResource=true` 不会安装 CRD。

## 原文案例

### 案例一：目录迁移后 Service 被 prune

原文描述：一次周五晚间的目录重构，把 `frontend/service.yaml` 移到 `services/` 后，生产网关出现大量 503，核心下单链路不可用。团队先怀疑网关 Pod，检查 ingress-nginx 和 Endpoint 控制器，花了近二十分钟。

原文归因为：旧 Application 开启 prune 后删掉了 Service；新位置对应的部署又因目标命名空间尚未创建、缺少 `CreateNamespace=true` 而失败，造成服务空窗。作者通过 `kubectl apply` 紧急重建旧 Service 恢复流量，再把迁移改为同一提交内完成、为关键 Service 添加 `Prune=false`，并收窄项目权限。

> [!note] 文件移动不等于资源身份改变
> ArgoCD 跟踪的是资源及其应用归属。仅在同一应用渲染范围内移动文件，且资源的 group/kind/namespace/name 没变，不应仅因 Git 文件路径变化就被 prune。这个案例没有提供清单、Application 路径和操作日志，无法验证完整因果；排查时要检查渲染范围、资源身份或应用归属是否改变。Service、Ingress 和 Gateway 是命名空间级资源，收窄相应权限应使用 namespace 资源规则。

迁移时在同一提交内完成配置变更，可以减少中间态；若迁移跨越多个 Application，还要分别评估它们的同步与 prune 顺序，不能仅凭一个原子提交保证无中断。

### 案例二：HPA 和准入修改造成反复 OutOfSync

原文描述：一个微服务反复 OutOfSync，持续数月。团队先怀疑提交不完整或分支不对，尝试 rebase 和修改 `targetRevision`，仍未解决。

Git 中固定 `replicas: 3`，HPA 按负载把副本扩到 5；准入组件又为 Pod 补入 `securityContext.runAsNonRoot` 和 `runAsUser`。作者在 `ignoreDifferences` 中添加 `/spec/replicas` 与 `managedFieldsManagers: [kube-controller-manager]`，并描述差异随之消失。

> [!note] 不同修改方要分别确认
> 忽略 HPA 相关字段不能自动豁免所有准入修改。准入字段是否出现在应用管理对象的 diff 中、对应什么路径和 manager，都要从 live 对象确认；不能假定它们归属 `kube-controller-manager`。需要同步时也保留已存在对象的副本数，应配合 `RespectIgnoreDifferences=true`。

遇到这类问题，先看具体字段与归属，再决定调整 Git 清单还是设置有限范围的忽略规则。

### 案例三：应用数量增加后 repo-server 排队

原文描述：Application 从 30 个增加到 200 个后，同步延迟从秒级增加到十几分钟，团队先怀疑 Git 服务器或网络。

作者归因为单副本 repo-server 在集中 reconcile 时 CPU 满载、manifest 生成排队，以及轮询带来的变更发现延迟。原文采取了扩到 3 副本、设置资源请求/上限、增加 Webhook、用 ApplicationSet 拆分应用和调整缓存的措施，并描述延迟恢复到秒级。

> [!note] 性能案例的归因边界
> 30、200、3 副本和延迟变化是原文案例数据，未在本仓库验证。原文把缓存设为 24h 的位置写错，且官方配置默认已有 24h 缓存；不能把案例效果归因于这一项。Webhook 加快变更发现，也不等于取代全部轮询。

应用数量增加后，ArgoCD 控制面也需要按实际渲染成本、队列等待和资源使用情况维护。

## 排查清单

- [ ] `argocd app get <app>`：分别查看同步状态、健康状态和最近一次操作结果。
- [ ] `argocd app diff <app>`：逐项定位差异；需要时核对渲染结果、live 对象和 last-applied。
- [ ] 检查 `syncPolicy.automated` 中的 selfHeal/prune，以及应用配置是否由其他声明式资源管理。
- [ ] 对 HPA、准入或控制器修改的字段，确认具体路径、manager 与 `ignoreDifferences` 范围；需要时检查 `RespectIgnoreDifferences`。
- [ ] 资源停在 Progressing 时，先看 `status`、事件及现有健康检查，再判断是否需要 Lua。
- [ ] 同步失败时区分 immutable、resourceVersion、API 类型缺失；确认原因后选择更新、重试、安装 CRD 或计划重建。
- [ ] 怀疑误 prune 时，核对最近的期望清单、同步操作记录、资源注解和 AppProject 的管理范围。
- [ ] 同步慢时检查 Webhook 投递、应用刷新及轮询配置，区分发现延迟与执行延迟。
- [ ] 检查 repo-server/controller 的 CPU、内存、并发和副本；结合 `kubectl top` 判断扩容需求。
- [ ] 多集群场景核对 `destination.server/namespace` 与 AppProject 的 destinations。
- [ ] 检查 Secret 是否明文进入 Git，并确认 Sealed Secrets/External Secrets 的实际解密或同步路径。
- [ ] 需要比较两份 reconciliation 结果时，使用 `argocd admin app diff-reconcile-results PATH1 PATH2`。
- [ ] 确认 Application、AppProject 和必要配置有备份，bootstrap 管理与恢复演练分别落实。

## 同步选项速查

排查时先确定问题属于差异比较、健康判断、API 更新、资源删除还是控制面性能，再对照对应配置。“九成源于三方模型”缺少统计依据，不能作为比例结论。

| 参数 | 作用 | 使用边界 |
| --- | --- | --- |
| `automated.prune: true/false` | 是否自动删除不再出现在期望清单中的资源 | 与同步选项分开；关键资源可以另设 prune 保护 |
| `Prune=false` / `Prune=confirm` | 跳过 prune，或要求删除确认 | 不等于保护所有删除路径；Prune=false 可作为应用默认项或资源注解 |
| `PruneLast=true` | 最后执行隐式 prune 波次 | 前面的资源和波次须成功，不保证同名重建无中断 |
| `PrunePropagationPolicy=foreground` | 前台级联删除 | 按 ownerReferences 清理，不能表示所有业务依赖 |
| `Replace=true` | 使用 replace/create 代替 apply | 仍受不可变字段校验约束，可能需要重建并造成中断 |
| `Force=true,Replace=true` | 明确删除再创建资源 | 通常限制到已评估可重建的资源 |
| `ApplyOutOfSyncOnly=true` | 只应用 OutOfSync 资源 | 减少 apply，但不跳过健康检查，选择性同步不执行 hooks |
| `SkipDryRunOnMissingResource=true` | 缺少类型时跳过相应 dry-run | 不会安装 CRD，也不跳过实际创建失败 |
| `CreateNamespace=true` | 创建 Application 目标命名空间 | 项目权限仍须允许相应操作 |
| `ServerSideApply=true` | 使用服务端 apply 和字段所有权 | 不绕过不可变字段，也不是性能或冲突消失的保证 |
| `RespectIgnoreDifferences=true` | 同步时也考虑 ignoreDifferences | 只有资源已存在时才能使用 live 状态保留字段 |

## 相关笔记与参考资料

- [[KnowledgeBase/entities/ArgoCD|ArgoCD 实体页]]
- [[KnowledgeBase/concepts/CICD|CI/CD]]
- [[KnowledgeBase/sources/argocd-sync-troubleshooting-summary|本文来源摘要]]
- [原文：ArgoCD 同步踩 5 坑](https://mp.weixin.qq.com/s/n4sgO6fcouZ-QyDdulRHaQ)
- [Application 字段定义](https://github.com/argoproj/argo-cd/blob/master/pkg/apis/application/v1alpha1/types.go) 与 [argocd app set 命令参考](https://argo-cd.readthedocs.io/en/stable/user-guide/commands/argocd_app_set/)
- [argocd-cm 配置示例](https://argo-cd.readthedocs.io/en/stable/operator-manual/argocd-cm-yaml/)

示例命令和配置尚未通过目标 ArgoCD/Kubernetes 环境下的运行与部署验证。
