---
title: Helm部署Kyverno和Policy-Reporter
tags:
  - kubernetes
  - security
  - auth
aliases:
  - kyverno策略引擎
---

# Helm 部署 Kyverno 和 Policy Reporter

Kyverno 用策略约束 Kubernetes 资源：验证镜像来源、运行权限和资源声明，也可以补充默认配置，或为新命名空间生成配套资源。

> [!note] 版本范围
> 安装章节保留原笔记的 Kyverno Chart `3.2.7`，其 `appVersion` 为 `v1.12.6`；Policy Reporter Chart 为 `2.24.2`，均为历史配置示例。后面的 CEL `MutatingPolicy` 实战和 1.18 新特性属于较新的版本范围，不能直接套用到这套旧 Chart。部署前应核对目标 Chart、Kyverno 与 Kubernetes 的兼容性。

## Kyverno 的工作方式

Kyverno 是 Kubernetes 原生策略引擎，名称来自希腊语中的“govern”。它作为动态准入控制器运行，通过 Mutating 和 Validating Webhook 处理 API Server 发来的请求，在资源持久化前执行匹配的规则。

![Kyverno 准入控制架构](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202411221003152.png)

常用动作的职责不同：

| 动作 | 作用 | 示例 |
| --- | --- | --- |
| `validate` | 检查对象；`Audit` 记录违规，`Enforce` 拒绝不合规请求 | 限制镜像仓库、要求资源声明 |
| `mutate` | 修改请求中的对象，或按专门配置修改已有对象 | 注入 `imagePullSecrets`、改写镜像地址 |
| `generate` | 根据触发资源创建配套资源 | 新建 Namespace 后生成 ResourceQuota、LimitRange |

Kyverno 还支持镜像验证和资源清理。传统 `ClusterPolicy` 用 YAML 描述规则，也会用到 JMESPath；较新的策略类型使用 CEL。相比 OPA Gatekeeper 的 Rego 规则，简单的 YAML 模式校验更贴近 Kubernetes 清单，但复杂逻辑仍需要理解相应的表达式和执行边界。

## 通过 Helm 部署 Kyverno

### 下载与版本检查

```bash
helm repo add --force-update kyverno https://kyverno.github.io/kyverno
helm repo update kyverno
helm pull kyverno/kyverno --version 3.2.7
tar -xzf kyverno-3.2.7.tgz
cd kyverno
helm show chart .
```

测试环境可以直接安装仓库中的 Chart：

```bash
helm install kyverno kyverno/kyverno -n kyverno --create-namespace
```

上面的简装命令未固定版本；需要可重复部署时，应像下载示例一样固定版本并提交经过评审的 values。

### 生产环境配置高可用

单副本中断可能影响匹配策略的资源发布。Kyverno 的不同控制器各自运行在 Deployment 中，应分别设置副本数，不能只设置顶层 `replicaCount=3`。以下 values 可用于原笔记的 Chart `3.2.7`：

```yaml
# values-ha.yaml
admissionController:
  replicas: 3
  podDisruptionBudget:
    enabled: true
    minAvailable: 2
backgroundController:
  replicas: 2
  podDisruptionBudget:
    enabled: true
    minAvailable: 1
cleanupController:
  replicas: 2
  podDisruptionBudget:
    enabled: true
    minAvailable: 1
reportsController:
  replicas: 2
  podDisruptionBudget:
    enabled: true
    minAvailable: 1
```

将高可用配置与环境的 `values.yaml` 一起维护，并配置资源保障、跨节点分布和系统命名空间排除。若使用 PolicyException，还需按目标版本确认 `features.policyExceptions.enabled`、例外所在命名空间及管理权限；启用此功能不等于已经定义了例外。

### 安装与基础检查

在解压后的 Kyverno Chart 目录执行：

```bash
helm upgrade -i kyverno -n kyverno --create-namespace . \
  -f values.yaml -f values-ha.yaml

kubectl -n kyverno get deployment,pod,pdb
kubectl get clusterpolicy
kubectl get mutatingwebhookconfigurations,validatingwebhookconfigurations | grep kyverno
```

尚未创建策略时，`clusterpolicy` 为空是正常现象。生产环境还应检查 Webhook 的选择器与排除范围，确保 Kyverno 自身及必要的系统组件能够恢复。高可用配置见 [Kyverno 安装文档](https://kyverno.io/docs/installation/installation/#high-availability-installation)。

## 部署 Policy Reporter 查看报告

Policy Reporter 是单独安装的报告与通知组件，可读取 Kyverno 生成的 PolicyReport，并通过 UI 展示结果。它不负责执行准入策略，也不是安装 Kyverno 后自动出现的内置界面。

相关入口：[Policy Reporter 文档](https://kyverno.github.io/policy-reporter/)、[Releases](https://github.com/kyverno/policy-reporter/releases)、[Artifact Hub](https://artifacthub.io/packages/helm/policy-reporter/policy-reporter)。

### 下载 Chart

```bash
helm repo add --force-update policy-reporter https://kyverno.github.io/policy-reporter
helm repo update policy-reporter
helm pull policy-reporter/policy-reporter --version 2.24.2
tar -xzf policy-reporter-2.24.2.tgz
```

### 配置证书、Ingress 与 OAuth

以下示例沿用原环境的域名与组件名称，依赖已经安装的 cert-manager、`selfsigned` ClusterIssuer、Ingress-Nginx 和 OAuth2 Proxy。

先创建 Policy Reporter 命名空间和 Certificate：

```bash
kubectl create ns policy-reporter

tee certificate-policy-reporter.yaml <<'EOF'
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: cert-policy-reporter
  namespace: policy-reporter
spec:
  secretName: policy-reporter-tls-cert-secret
  privateKey:
    rotationPolicy: Always
  commonName: kyverno.hanxux.local
  dnsNames:
    - kyverno.hanxux.local
  usages:
    - digital signature
    - key encipherment
    - server auth
  issuerRef:
    name: selfsigned
    kind: ClusterIssuer
EOF

kubectl apply -f certificate-policy-reporter.yaml
```

在 Policy Reporter 的 `values.yaml` 中配置 UI、HTTPS 和 OAuth 认证：

```yaml
# Settings for the Policy Reporter UI subchart (see subchart's values.yaml)
ui:
  enabled: true
  create: true
  plugins:
    kyverno: true
  resources:
    limits:
      memory: 256Mi
      cpu: 300m
    requests:
      memory: 50Mi
      cpu: 100m
  ingress:
    enabled: true
    ingressClassName: nginx-default
    annotations:
      nginx.ingress.kubernetes.io/auth-url: "http://oauth2-proxy.oauth2-proxy.svc.cluster.local/oauth2/auth"
      nginx.ingress.kubernetes.io/auth-signin: "https://oauth2proxy.hanxux.local/oauth2/start?rd=https%3A%2F%2Fkyverno.hanxux.local"
    hosts:
    - host: kyverno.hanxux.local
      paths:
      - path: /
        pathType: Prefix
    tls:
      - secretName: policy-reporter-tls-cert-secret
        hosts:
          - kyverno.hanxux.local
```

### 安装、通知与访问

在解压后的 Policy Reporter Chart 目录执行：

```bash
helm upgrade -i policy-reporter -n policy-reporter . -f values.yaml
```

访问 [Policy Reporter UI](https://kyverno.hanxux.local)。需要向 Loki、Slack 等目标发送通知时，参照 [Enable Targets Notification](https://kyverno.github.io/policy-reporter/guide/helm-chart-core#enable-targets-notification) 配置。

## 策略编写与目录管理

### 匹配、排除与模式语法

- `match.any`：任意一个匹配项成立即可；`match.all`：所有匹配项都成立。
- `exclude`：排除不应受本策略影响的资源。业务策略通常排除 `kube-system` 和 `kyverno`；其他系统命名空间按环境补充。
- `preconditions`：匹配后进一步判断请求条件，例如跳过 `DELETE`。
- `?*`：要求存在且非空；`!*:latest`：不匹配以 `:latest` 结尾的镜像。
- `=(字段)`：字段可以不存在；存在时校验其值。`X(字段)`：要求该字段不存在。
- `foreach`：逐项检查容器等列表；`anyPattern`：接受若干模式中的任意一种。

更多语法可查 [Validate Rules](https://kyverno.io/docs/policy-types/cluster-policy/validate/)；原笔记参考的 [Kyverno Policy 语法文章](https://mp.weixin.qq.com/s/5tANwfzp8C0O2GS8fkXErA) 也予以保留。

下面八组验证策略使用 `validationFailureAction: Audit` 和 `background: false`，便于先观察新请求。`validationFailureAction` 是旧版策略字段；较新版本推荐在各条 `validate` 下使用 `failureAction`。本文保留旧写法以对应历史 Chart，迁移时应依据目标版本的 CRD 调整。

> [!important] 审计与变更的边界
> `Audit` 不会拒绝违规请求；`background: false` 不会扫描已经存在且没有再提交的对象。两者都不会把 mutate 或 generate 变成“只预览”：这两类规则仍可能修改或生成资源。

### 按 common 与 region 管理策略

每个策略放在独立文件中，便于评审、版本控制与回滚；同一目录也可以整体应用：

```bash
kubectl apply -f ./policies/
```

原笔记的 Azure DevOps 流水线按 common 和 region 分目录应用。以下是流水线 `script` 片段，包含 Azure DevOps 的变量及模板表达式：

```bash
export DIRECTORY="$(System.DefaultWorkingDirectory)/${{parameters.folder}}"
kubectl apply -f $DIRECTORY/external/kyverno/policies/common --recursive

if test -d "$DIRECTORY/external/kyverno/policies/${{parameters.region}}"; then
  kubectl apply -f $DIRECTORY/external/kyverno/policies/${{parameters.region}} --recursive
fi
```

## 验证策略：镜像、权限与工作负载规范

### 禁止 latest 标签

`latest` 标签难以标识具体发布版本，也不利于回滚。以下规则用 `!*:latest` 检查镜像后缀；它本身不是完整的“必须显式写版本标签”规则。未写标签、带仓库端口及使用 digest 的镜像，都应加入测试样本，再决定是否补充显式标签或 digest 校验。

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-latest-tag
spec:
  validationFailureAction: Audit
  background: false
  rules:
    - name: require-image-tag
      match:
        any:
          - resources:
              kinds: ["Pod"]
      exclude:
        any:
          - resources:
              namespaces: ["kube-system", "kyverno"]
      validate:
        message: "禁止使用 latest 镜像标签。"
        pattern:
          spec:
            containers:
              - image: "!*:latest"
```

此例只检查普通容器；若要覆盖 initContainers 和 ephemeralContainers，需要为这些列表补充同样的校验，不能把普通容器通过当作整个 Pod 的镜像检查通过。

### 限制受信任镜像仓库（Harbor）

仓库限制既可以统一要求 `registry.example.com/*`，也可以只约束业务命名空间。下面沿用原文的 Harbor 场景：`app-namespace` 中普通容器和初始化容器的镜像必须来自 `registry.local.harbor`。发布初期先审计，整改后再切换为 `Enforce`；原有强制拦截效果对应后者。

`foreach` 分别遍历两个容器列表；初始化容器不存在时，用 `|| []` 返回空列表。仓库地址应使用稳定域名，并通过 Git 管理配置，避免把某台 Registry 的 IP 固定在策略中。

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: check-images
spec:
  validationFailureAction: Audit
  background: false
  rules:
    - name: check-registry
      match:
        any:
          - resources:
              kinds: ["Pod"]
              namespaces: ["app-namespace"]
      exclude:
        any:
          - resources:
              namespaces: ["kube-system", "kyverno"]
      preconditions:
        any:
          - key: "{{ request.operation }}"
            operator: NotEquals
            value: DELETE
      validate:
        message: "镜像必须来自 registry.local.harbor。"
        foreach:
          - list: "request.object.spec.initContainers || []"
            pattern:
              image: "registry.local.harbor/*"
          - list: "request.object.spec.containers"
            pattern:
              image: "registry.local.harbor/*"
```

改为通用仓库限制时，将两处前缀替换为 `registry.example.com/*`，并按实际范围调整 `namespaces`。必要的例外通过受控的 `exclude` 或 PolicyException 管理。此例未覆盖 ephemeralContainers。

### 要求容器以非 root 身份运行

以 root 运行会增加容器被入侵后的风险，但容器内 root 不直接等于获得宿主机 root。该策略允许 Pod 级统一设置，也允许每个容器分别设置 `runAsNonRoot: true`。容器级配置会覆盖 Pod 级配置，因此 Pod 级分支还必须检查容器没有显式关闭此限制。

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-run-as-non-root
spec:
  validationFailureAction: Audit
  background: false
  rules:
    - name: run-as-non-root
      match:
        any:
          - resources:
              kinds: ["Pod"]
      exclude:
        any:
          - resources:
              namespaces: ["kube-system", "kyverno"]
      validate:
        message: "Pod 级或每个容器必须设置 runAsNonRoot: true，容器不得覆盖为 false。"
        anyPattern:
          - spec:
              securityContext:
                runAsNonRoot: "true"
              containers:
                - =(securityContext):
                    =(runAsNonRoot): "true"
              =(initContainers):
                - =(securityContext):
                    =(runAsNonRoot): "true"
              =(ephemeralContainers):
                - =(securityContext):
                    =(runAsNonRoot): "true"
          - spec:
              containers:
                - securityContext:
                    runAsNonRoot: "true"
              =(initContainers):
                - securityContext:
                    runAsNonRoot: "true"
              =(ephemeralContainers):
                - securityContext:
                    runAsNonRoot: "true"
```

模式参考 [Require runAsNonRoot](https://kyverno.io/policies/pod-security/restricted/require-run-as-nonroot/require-run-as-nonroot/)。这样可以兼容两种声明位置，也覆盖初始化容器和临时容器；不必强制在 Pod 与每个容器上重复填写相同配置。

### 禁止 privileged、hostPath 和主机命名空间共享

这些配置会扩大工作负载访问宿主机的能力，应作为安全基线管理。仍先确认系统组件和特殊业务的依赖，再决定强制范围。以下策略在三条规则中都排除系统命名空间，并允许安全字段缺省。

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-dangerous-security
spec:
  validationFailureAction: Audit
  background: false
  rules:
    - name: disallow-privileged
      match:
        any:
          - resources:
              kinds: ["Pod"]
      exclude:
        any:
          - resources:
              namespaces: ["kube-system", "kyverno"]
      validate:
        message: "禁止 privileged 容器。"
        pattern:
          spec:
            containers:
              - =(securityContext):
                  =(privileged): "false"
            =(initContainers):
              - =(securityContext):
                  =(privileged): "false"
            =(ephemeralContainers):
              - =(securityContext):
                  =(privileged): "false"
    - name: disallow-host-path
      match:
        any:
          - resources:
              kinds: ["Pod"]
      exclude:
        any:
          - resources:
              namespaces: ["kube-system", "kyverno"]
      validate:
        message: "禁止挂载 hostPath。"
        pattern:
          spec:
            =(volumes):
              - X(hostPath): "null"
    - name: disallow-host-network
      match:
        any:
          - resources:
              kinds: ["Pod"]
      exclude:
        any:
          - resources:
              namespaces: ["kube-system", "kyverno"]
      validate:
        message: "禁止 hostNetwork 和 hostPID。"
        pattern:
          spec:
            =(hostNetwork): "false"
            =(hostPID): "false"
```

`=(volumes)` 表示可以不声明卷；[官方 hostPath 示例](https://kyverno.io/policies/pod-security/baseline/disallow-host-path/disallow-host-path/) 用 `X(hostPath)` 禁止字段出现。`=(hostNetwork)`、`=(hostPID)` 和可选 `privileged` 则允许字段不存在，避免要求用户显式填写已经默认关闭的字段。

### 要求声明 requests 和 limits

缺少资源声明会影响调度和资源隔离。先检查业务 Chart 是否暴露了资源参数，审计并整改已有工作负载，再引入强制策略和 ResourceQuota。配额要求资源声明时，不合规的新 Pod 可能在准入阶段被拒绝，不能简单归为调度 Pending。

`?*` 表示字段必须存在且非空。此例沿用原文要求普通容器同时声明 CPU、内存的 requests 和 limits；是否强制 CPU limit，应由团队按业务决定。

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-resources
spec:
  validationFailureAction: Audit
  background: false
  rules:
    - name: require-requests-limits
      match:
        any:
          - resources:
              kinds: ["Pod"]
      exclude:
        any:
          - resources:
              namespaces: ["kube-system", "kyverno"]
      validate:
        message: "每个普通容器都必须声明 CPU、内存的 requests 与 limits。"
        pattern:
          spec:
            containers:
              - resources:
                  requests:
                    memory: "?*"
                    cpu: "?*"
                  limits:
                    memory: "?*"
                    cpu: "?*"
```

本例只检查普通容器；需要覆盖 initContainers 时另行补充规则。启用 LimitRange 后，应验证默认值与本规则是否一致。

### 要求 owner 标签

owner 标签便于故障定位、责任归属和成本分摊。下面保留原文的 `app.kubernetes.io/owner` 作为团队自定义键；它不属于 [Kubernetes 官方推荐标签清单](https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/)，实际可换成团队域名前缀。

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-owner-label
spec:
  validationFailureAction: Audit
  background: false
  rules:
    - name: require-owner-label
      match:
        any:
          - resources:
              kinds: ["Deployment", "StatefulSet", "Service"]
      exclude:
        any:
          - resources:
              namespaces: ["kube-system", "kyverno"]
      validate:
        message: "必须带 app.kubernetes.io/owner 标签。"
        pattern:
          metadata:
            labels:
              app.kubernetes.io/owner: "?*"
```

此规则检查资源自身的 `metadata.labels`，不等于自动给 Pod 模板加标签。若 Prometheus、Grafana 或成本系统需要使用该标签，还需确认其采集和映射配置。

### 要求 readinessProbe 和 livenessProbe

readinessProbe 决定容器是否准备好接收流量，livenessProbe 用于判断是否需要重启。下面的规则同时要求两种探针，并检查探测周期大于 0；应按业务范围使用，避免把同样的探针要求套到一次性任务上。

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-probes
spec:
  validationFailureAction: Audit
  background: false
  rules:
    - name: require-readiness-probe
      match:
        any:
          - resources:
              kinds: ["Pod"]
      exclude:
        any:
          - resources:
              namespaces: ["kube-system", "kyverno"]
      validate:
        message: "普通容器必须配置 readinessProbe 和 livenessProbe。"
        pattern:
          spec:
            containers:
              - readinessProbe:
                  periodSeconds: ">0"
                livenessProbe:
                  periodSeconds: ">0"
```

Kubernetes 会为探针参数提供默认值，使用默认周期并不等于探针无效；这条规则也不能证明探针端点能正确反映应用健康。探针本身还需要配置有效的检查动作，并在运行时验证。参见 [Kubernetes 探针配置](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)。

### 限制 NodePort 和 LoadBalancer

若业务统一经 Ingress 暴露 HTTP 服务，可以限制自行创建 NodePort 或 LoadBalancer。LoadBalancer 在云环境中还可能产生费用；确需这些 Service 类型的基础设施应使用明确的例外。

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: restrict-service-types
spec:
  validationFailureAction: Audit
  background: false
  rules:
    - name: disallow-nodeport-lb
      match:
        any:
          - resources:
              kinds: ["Service"]
      exclude:
        any:
          - resources:
              namespaces: ["kube-system", "kyverno"]
      validate:
        message: "默认不允许 NodePort 或 LoadBalancer，请使用已批准的入口。"
        deny:
          conditions:
            any:
              - key: "{{ request.object.spec.type || 'ClusterIP' }}"
                operator: Equals
                value: NodePort
              - key: "{{ request.object.spec.type || 'ClusterIP' }}"
                operator: Equals
                value: LoadBalancer
```

## 变更策略：注入 imagePullSecrets 与历史版本上限

通过 `patchStrategicMerge` 给 Pod 加入 `regcred` 引用，并将 Deployment 的 `revisionHistoryLimit` 设为 `5`。Secret 必须事先存在于对应命名空间；添加引用不会自动创建或同步 Secret。

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: inject-defaults
spec:
  background: false
  rules:
    - name: inject-imagepullsecrets
      match:
        any:
          - resources:
              kinds: ["Pod"]
      exclude:
        any:
          - resources:
              namespaces: ["kube-system", "kyverno"]
      mutate:
        patchStrategicMerge:
          spec:
            imagePullSecrets:
              - name: regcred
    - name: set-revision-history-limit
      match:
        any:
          - resources:
              kinds: ["Deployment"]
      exclude:
        any:
          - resources:
              namespaces: ["kube-system", "kyverno"]
      mutate:
        patchStrategicMerge:
          spec:
            revisionHistoryLimit: 5
```

Deployment 的 `revisionHistoryLimit` 默认是 `10`。本例会将保留上限改成 `5`，也会覆盖用户已经声明的其他值；如果团队允许业务自行选择上限，需要调整规则范围。用服务端 dry-run 查看实际结果。

变更规则会影响最终对象，不能靠 `Audit` 停止变更。即使规则本身不表达“违规拒绝”，Webhook 调用错误或后续验证仍可能使请求失败。与 ArgoCD 共用时，还需处理期望状态与实际状态的差异，见后面的上线与排障章节。

## 变更实战：按命名空间改写 Artifactory 镜像地址

### 跨境镜像拉取与缓存

在跨国企业中，海外 Artifactory（如 `artifactory.example.com`）经常作为统一镜像源，代理 DockerHub、GHCR、Quay 等公共仓库。当业务扩展到中国区时，由于跨境网络延迟，Pod 拉取镜像速度很慢甚至超时。

在中国区 Artifactory（如 `artifactory.example.cn`）配置 Smart Remote Repository，以上游海外 Artifactory 为源缓存镜像。Kyverno 在 Pod 准入时将允许列表中的镜像地址从 `.com` 改为 `.cn`，业务清单可以继续声明原始地址。

策略需要同时满足：

- 自动替换 Pod 中 containers 和 initContainers 的镜像路径
- 仅替换特定仓库（有 Smart Remote 配置的）的镜像，跳过没有 `.cn` 缓存的仓库
- 仅在指定 namespace 中生效，避免影响系统组件
- Kyverno 宕机时不阻塞 Pod 创建（`failurePolicy: Ignore`）

### 选择 CEL 并检查 Webhook 路径

本实战使用较新版本支持的 `policies.kyverno.io/v1` `MutatingPolicy`，以 CEL（Common Expression Language）编写变更逻辑。它与前面历史 Chart 的适用范围不同；这里不把 1.18 作为该策略类型首次引入的版本。

原笔记在 JMESPath `AnyIn` 与多级镜像路径的组合上未达到预期，例如 `artifactory.example.com/my-repo/datadog/agent:7.68.3-jmx`。这里改用 CEL 的 `startsWith()` 和 `exists()`，明确按仓库前缀匹配：

```cel
variables.allowedRepos.exists(repo,
  c.image.startsWith("artifactory.example.com/" + repo + "/")
)
```

原环境还记录过 ClusterPolicy 的 Webhook 未收到预期请求、切换 MutatingPolicy 后生效的现象。排查时应检查实际的 Webhook 配置与匹配条件；本例涉及 `kyverno-resource-mutating-webhook-cfg` 中的 `mpol.validate.kyverno.svc-ignore`。这些名称与现象属于当时的部署记录，不能仅凭策略类型判断请求链是否正常。

CEL 的编译反馈有助于提前发现表达式问题。MutatingPolicy 的 `READY` 状态可以辅助判断策略是否就绪，但还要用实际准入请求检查是否按预期改写。
### 策略设计

#### 用单一策略覆盖目标命名空间

原环境最初通过 Helm `range` 为每个命名空间生成一条 MutatingPolicy，观察到共享 Webhook 的 `namespaceSelector` 被最后一个策略覆盖，只有最后一个命名空间生效。该记录应按当时版本与最终生成的 Webhook 配置排查，不作为所有版本的固定行为。

这个案例改为单一 MutatingPolicy，通过 `matchExpressions` 与 `operator: In` 列出全部目标命名空间，避免重复维护相同的变更逻辑。

#### Policy YAML（Helm 模板）

```yaml
{{- if .Values.kyvernoPolicy }}
{{- if .Values.kyvernoPolicy.targetNamespaces }}
---
apiVersion: policies.kyverno.io/v1
kind: MutatingPolicy
metadata:
  name: mutate-image-registry-cn
spec:
  # Kyverno 宕机时不阻塞 Pod 创建，Pod 会使用原始 .com 路径作为 fallback
  failurePolicy: Ignore
  matchConstraints:
    # 单一 Policy + In 操作符，避免多 policy 的 webhook selector 冲突
    namespaceSelector:
      matchExpressions:
        - key: kubernetes.io/metadata.name
          operator: In
          values:
          {{- range .Values.kyvernoPolicy.targetNamespaces }}
            - {{ . }}
          {{- end }}
    resourceRules:
      - apiGroups: ['']
        apiVersions: ['v1']
        operations: ['CREATE', 'UPDATE']
        resources: ['pods']
  # 仓库白名单：仅替换有 Smart Remote 配置的仓库
  variables:
    - name: allowedRepos
      expression: >-
        [{{- range $i, $repo := .Values.kyvernoPolicy.allowedRepos -}}
        {{ if $i }}, {{ end }}"{{ $repo }}"
        {{- end }}]
  mutations:
    # 替换 containers 中的镜像路径
    - patchType: JSONPatch
      jsonPatch:
        expression: |
          object.spec.containers.map(c,
            c.image.startsWith("artifactory.example.com/") &&
            variables.allowedRepos.exists(repo,
              c.image.startsWith("artifactory.example.com/" + repo + "/")) ?
            JSONPatch{
              op: "replace",
              path: "/spec/containers/" + string(object.spec.containers.indexOf(c)) + "/image",
              value: c.image.replace("artifactory.example.com", "artifactory.example.cn")
            } : null
          ).filter(p, p != null)
    # 替换 initContainers 中的镜像路径（需先判断是否存在）
    - patchType: JSONPatch
      jsonPatch:
        expression: |
          has(object.spec.initContainers) ?
          object.spec.initContainers.map(c,
            c.image.startsWith("artifactory.example.com/") &&
            variables.allowedRepos.exists(repo,
              c.image.startsWith("artifactory.example.com/" + repo + "/")) ?
            JSONPatch{
              op: "replace",
              path: "/spec/initContainers/" + string(object.spec.initContainers.indexOf(c)) + "/image",
              value: c.image.replace("artifactory.example.com", "artifactory.example.cn")
            } : null
          ).filter(p, p != null)
          : []
{{- end }}
{{- end }}
```

#### Values 配置

```yaml
kyvernoPolicy:
  # 分阶段 rollout：先基础设施，再业务 namespace
  targetNamespaces:
    - tools

  # 仅替换有 Smart Remote 缓存的仓库，跳过无缓存的（如 docker-local-sandbox）
  allowedRepos:
    - my-dockerhub-docker-remote
    - my-ghcr-docker-remote
    - my-quay-docker-remote
```

### 验证改写与排除范围

以下命令沿用原环境的对象名称；部署前先确认目标命名空间、镜像仓库与控制器版本。先完成 dry-run 检查，再安排实际重建 Pod。

```bash
# 检查 policy 状态（READY 应为 true）
kubectl get mutatingpolicy
# NAME                       AGE   READY
# mutate-image-registry-cn   1m    true

# 检查 webhook selector 是否正确包含所有目标 namespace
kubectl get mutatingwebhookconfiguration kyverno-resource-mutating-webhook-cfg \
  -o jsonpath='{.webhooks[0].namespaceSelector}' | jq .

# dry-run 测试：目标 namespace 中的白名单 repo（应被替换）
kubectl run test -n tools \
  --image=artifactory.example.com/my-dockerhub-docker-remote/datadog/agent:7.68.3 \
  --dry-run=server -o jsonpath='{.spec.containers[0].image}'
# 输出: artifactory.example.cn/my-dockerhub-docker-remote/datadog/agent:7.68.3

# dry-run 测试：目标 namespace 中的非白名单 repo（不应被替换）
kubectl run test -n tools \
  --image=artifactory.example.com/my-docker-local-sandbox/some-image:latest \
  --dry-run=server -o jsonpath='{.spec.containers[0].image}'
# 输出: artifactory.example.com/my-docker-local-sandbox/some-image:latest

# dry-run 测试：非目标 namespace（不应被替换）
kubectl run test -n default \
  --image=artifactory.example.com/my-dockerhub-docker-remote/datadog/agent:7.68.3 \
  --dry-run=server -o jsonpath='{.spec.containers[0].image}'
# 输出: artifactory.example.com/my-dockerhub-docker-remote/datadog/agent:7.68.3

# 以下重启会影响 tools 中的全部 Deployment，应在批准的变更窗口执行
# rollout restart 后检查 Pod 镜像是否已替换
kubectl rollout restart deployment -n tools
kubectl get pods -n tools \
  -o jsonpath='{range .items[*]}{.metadata.name}: {.spec.containers[*].image}{"\n"}{end}'
```

验证还应覆盖 initContainers，以及目标命名空间中的多个仓库。`failurePolicy: Ignore` 只在 Webhook 调用失败时允许请求继续；Pod 随后仍需能够从原始 `.com` 地址拉取镜像。不要把“准入放行”当作镜像拉取成功。

## 生成策略：为新命名空间下发配额和默认值

新 Namespace 创建后，由两条 generate 规则生成 ResourceQuota 和 LimitRange。它们分别控制命名空间的资源总量、容器的默认 requests 与 limits。

Namespace 本身是集群级资源，应按 `resources.names` 排除 `kube-system`、`kyverno` 和 `default`，不能用命名空间内资源的 `resources.namespaces` 来匹配它。

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: generate-ns-defaults
spec:
  background: false
  rules:
    - name: generate-resourcequota
      match:
        any:
          - resources:
              kinds: ["Namespace"]
      exclude:
        any:
          - resources:
              names: ["kube-system", "kyverno", "default"]
      generate:
        synchronize: true
        apiVersion: v1
        kind: ResourceQuota
        name: default-quota
        namespace: "{{ request.object.metadata.name }}"
        data:
          spec:
            hard:
              requests.cpu: "8"
              requests.memory: 16Gi
              limits.cpu: "16"
              limits.memory: 32Gi
              pods: "50"
    - name: generate-limitrange
      match:
        any:
          - resources:
              kinds: ["Namespace"]
      exclude:
        any:
          - resources:
              names: ["kube-system", "kyverno", "default"]
      generate:
        synchronize: true
        apiVersion: v1
        kind: LimitRange
        name: default-limitrange
        namespace: "{{ request.object.metadata.name }}"
        data:
          spec:
            limits:
              - type: Container
                default:
                  cpu: 500m
                  memory: 512Mi
                defaultRequest:
                  cpu: 100m
                  memory: 128Mi
```

`synchronize: true` 会维护生成资源与策略的对应关系：手动放宽生成的配额可能被恢复，变更应回到策略或其受控输入中完成。生成由控制器处理，需确认背景控制器有对应资源权限；不能把触发 Namespace 创建成功当作下游资源已经就绪。已有 Namespace 的补发属于 generate-existing 场景，不能仅靠 `background: true` 触发。参见 [Generate Rules](https://kyverno.io/docs/policy-types/cluster-policy/generate/)。

## 验证策略与审计报告

### 集群内验证

先查看策略是否成功注册，再提交真实的准入预演：

```bash
kubectl apply -f policies/
kubectl get clusterpolicy
kubectl describe cpol disallow-latest-tag
kubectl apply --dry-run=server -f demoapp.yaml
kubectl get policyreport -A
kubectl get clusterpolicyreport
kubectl describe policyreport -n default
```

`--dry-run=server` 会经过 API Server 的准入链；`--dry-run=client` 无法验证 Kyverno Webhook。对于 `Enforce`，用一个应通过和一个应拒绝的资源确认结果；对于 `Audit`，违规请求也会放行，命令成功不能单独证明合规。dry-run 不持久化资源，不要依赖它生成持久报告或配套资源。

`kubectl describe cpol` 可检查状态、条件及相关事件，不能假定每个版本都显示逐规则命中次数。PolicyReport 用于查看审计结果，报告的聚合粒度随版本和配置变化，不应假设每个命名空间永远只有一份。

生成策略还需在隔离的测试命名空间中检查 ResourceQuota 和 LimitRange 是否就绪；变更策略则检查服务端返回对象中的字段，而不只是命令退出码。

### CI 中离线测试

Kyverno CLI 可在本地或 CI 中预演策略，无需连接集群：

```bash
kyverno test ./policies
kyverno apply ./policies --resource demoapp.yaml
```

`kyverno test` 需要测试清单、资源样本和预期结果，不能只建一个放策略 YAML 的目录。原文的 `--git-branch main` 用于 Git 来源测试的分支选择，本地目录测试不需要此参数。离线测试不能代替集群中的 Webhook、权限、默认值和其他准入控制器联动验证。

样本至少覆盖正常与违规请求、多容器、initContainers、字段缺省、被排除的命名空间，以及有意保留的业务例外。

### 选择后台扫描范围

`background` 控制已有资源的定期检查；它不决定 mutate 和 generate 是否执行。关闭扫描可以减少存量检查负担，但也意味着没有被再次提交的对象不会被本策略盘点。

| 配置 | 新请求 | 已有且未再提交的资源 |
| --- | --- | --- |
| `Audit` + `background: false` | 放行，按报告配置记录 | 不扫描 |
| `Audit` + `background: true` | 放行，按报告配置记录 | 扫描并报告 |
| `Enforce` + `background: false` | 拒绝违规请求 | 不扫描 |
| `Enforce` + `background: true` | 拒绝违规请求 | 扫描并报告，不追溯拒绝或删除 |

需要摸底存量时，可以对合适的验证策略受控开启扫描，观察报告量、API Server、etcd 与控制器负载后再决定长期配置。使用准入身份等仅请求时可用信息的规则，不能直接用于后台扫描。报告行为参见 [Policy Reports](https://kyverno.io/docs/guides/reports/#background-scans)。

## 生产上线与排障

### 上线顺序

1. 固定并核对 Chart 与应用版本，配置控制器高可用、资源保障、PDB 和必要的系统排除，确认 Webhook 注册正常。
2. 将策略、环境输入与测试样本纳入 Git，按独立文件评审；确认业务 Chart 提供所需的资源、标签与探针参数。
3. 验证策略先使用 `Audit`，原文建议观察一至两周；需要盘点存量时明确安排后台扫描，不能只等待已有资源自动出现在报告中。
4. 根据审计结果安排整改和例外，先在测试环境、再按业务命名空间逐条切换为 `Enforce`。已确认的安全基线也要核对系统依赖与恢复路径。
5. 根据风险选择 `failurePolicy`，配置通知和监控，并在切换后用正反样本验证实际行为。
6. 升级安排在低峰窗口，检查 `helm diff`、CRD 变更和版本说明，在测试环境验证后再发布；同时维护紧急变更流程和策略回滚方式。

策略也应备份并保留版本。回滚动作应能定位到具体策略，避免为一个业务例外撤销整套约束。

### 区分 Audit / Enforce 与 Fail / Ignore

`Audit` / `Enforce` 决定不合规请求的处理方式；`failurePolicy` 决定 Webhook 调用失败、超时等情况下如何处理匹配的请求。`Fail` 会拒绝这些请求，`Ignore` 则可能绕过此次策略检查；影响范围取决于 Webhook 和策略的匹配条件。

可以按场景将强安全约束设为 Fail，将可容忍短时绕过的规范或加速功能设为 Ignore。上面的 Artifactory 镜像改写选择 Ignore，只保证 Webhook 故障时允许请求继续，不保证原始镜像地址仍然可达。

升级前应检查控制器可用性、PDB、系统命名空间和已经批准的例外。不要把永久排除整个 CI 服务账号当作通用升级要求；如确需身份例外，按目标版本的配置方式收窄范围、管理权限并定期复核。

### 常见故障排查

| 现象 | 优先检查 | 处理方式 |
| --- | --- | --- |
| 新策略上线后大量流水线失败 | 是否直接启用了 Enforce；Chart 是否暴露了必填参数 | 先审计，安排业务整改后再灰度强制 |
| 系统组件或 Kyverno 自身无法恢复 | 规则的 exclude 与 Webhook 选择器 | 明确排除所需系统范围，并限制这些范围的访问权限 |
| API 查询变慢、报告对象增长 | 扫描范围、报告聚合、规则数量、控制器和 etcd 负载 | 分批扫描与调优；历史报告清理应单独评估，不能仅凭日志批量删除 |
| 客户端 dry-run 成功，部署仍被拦截 | 是否用了 `--dry-run=client`；验证策略当前是 Audit 还是 Enforce | 改用服务端 dry-run，并检查明确的合规预期 |
| ArgoCD 持续 OutOfSync | mutate 后的字段与 Git 中声明是否不同 | 在 Git 中显式声明期望值，或只对受控字段配置差异忽略 |
| 多个命名空间中只有一个发生镜像改写 | MutatingPolicy 状态及实际 Webhook 的 namespaceSelector | 按镜像改写案例检查 selector 合并，必要时使用单策略加 In 列表 |
| Registry 迁移后镜像策略失效 | 域名、仓库允许列表和规则中的固定前缀 | 用稳定域名集中维护，变更时补齐正反测试 |

剪藏原文记录过单副本重启阻塞发布、资源声明强制后上百条流水线失败，以及大量报告对象使 etcd 承压等案例。这些属于作者的环境经验，不能据此认定后台扫描必然压垮集群；应结合实际规模与监控定位。

ArgoCD 的差异忽略与同步行为需要分别配置，参见 [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD同步故障排查]]。多个准入组件共存时，可继续查看 [[Docker-Kubernetes/k8s-security-auth/k8s-Admission-Webhook链冲突排查-Istio-Kyverno-Gatekeeper]]。

## Kyverno 1.18 新特性与策略迁移

> 本节依据 [CNCF 于 2026-05-05 发布的 1.18 公告](https://www.cncf.io/blog/2026/05/05/announcing-kyverno-release-1-18/)，记录该版本当时的变化与迁移计划。

Kyverno 1.18 是项目从 CNCF 毕业后的首个版本。

该版本重点改进 HTTP 调用安全、CLI 测试能力与策略引擎可靠性，并继续推进基于 CEL 的策略类型。

### 主要变化

Kyverno 1.18 带来了以下更新：

- 面向基于 HTTP 的策略执行，提供更强的安全控制，并缓解多个 CVE 问题
- 大幅增强 CLI 能力，用于测试和应用现代策略类型
- 提升策略引擎在性能、可观测性和可扩展性方面的表现
- 增强 policies Helm chart，支持更灵活的自定义配置

公告说明 1.18 没有破坏性变更，同时提醒用户开始迁移 ClusterPolicy；具体升级仍需核对目标版本的发布说明。

### 安全改进

#### 更安全的 HTTP 执行

Kyverno 策略可以通过 HTTP CEL 库调用外部服务。1.18 对此增加了以下防护：

- **阻止列表 / 允许列表强制执行**：默认情况下，loopback、元数据服务等不安全地址会被阻止。用户可以为集群级策略和命名空间级策略配置允许列表和阻止列表。此外，来自命名空间级策略的 HTTP 调用默认被禁用，需要通过配置标志显式开启。这些变更有助于防止 SSRF 类型的滥用。参见 [CVE-2026-4789](https://github.com/advisories/GHSA-rggm-jjmc-3394)。
- **作用域 token 授权**：此前，Kyverno HTTP 调用中包含的 token 可能被用于冒充 Kyverno 控制器。现在，HTTP 调用会携带一个单独的、具备作用域限制的 token，限制外部服务滥用该 token 的权限范围。参见 [CVE-2026-41323](https://github.com/kyverno/kyverno/security/advisories/GHSA-f9g8-6ppc-pqq4)。

### CLI 扩展与开发者体验

#### 扩展策略支持

`kyverno apply` 和 `kyverno test` 命令现在支持：

- Cleanup policies
- HTTP 和 Envoy 授权策略
- MutatingPolicy 中的 mutateExisting 规则
- `--exceptions-with-policies` 标志，用于改进测试工作流

#### 可靠性与易用性改进

本次版本还修复了多个问题，涉及：

- 错误处理与错误报告
- 无集群连接场景下的 CRD 兼容性
- panic、文件句柄泄漏等稳定性问题

### 策略引擎改进

#### 更细粒度的成功事件过滤

新的 `successEventActions` ConfigMap 参数允许用户控制：

- 哪些成功事件会被发出
- 策略报告的噪声程度

#### 性能与可扩展性

关键改进包括：

- admission controller 支持基于内存的 HPA 自动扩缩容
- `/metrics` 端点支持 TLS
- 改进并发处理，降低竞态条件风险

#### CEL 与策略执行增强

- 新增 gzip CEL 库，支持更高级的表达式
- 改进策略变量和条件的编译与求值
- 改善策略类型与执行引擎之间的一致性

### 镜像验证改进

本次版本还对镜像验证能力进行了多项针对性改进：

- 对于 ClusterPolicies，`imageRegistryCredentials.secrets` 现在支持 `namespace/name` 表示法；同时，Pod 级别的 `imagePullSecrets` 会自动被用作镜像仓库凭证。这对于多租户环境很有用，因为每个命名空间通常会管理自己的 pull secrets。
- ImageValidatingPolicy 可靠性修复，包括更好地处理签名时间戳和 TSA 证书链、Notary resolver 修复、正确的 `matchImageReferences` 过滤，以及改进命名空间级策略的 autogen 支持。

### Policies Helm Chart 增强

新增能力包括：

- 在 ValidatingPolicies 中支持 excludes，包括 namespace、subject、resource rules 和 match conditions
- `auditAnnotation` 配置
- 每个策略级别的 annotation 覆盖

### 支持策略更新

1.18 公告宣布采用“main + 1”补丁支持模型（N-1 模型）。

- **当前版本（main）和上一个版本** 会获得补丁支持。补丁范围仅限于严重和高危 CVE，以及其他关键修复。这大约提供 3 个月的社区补丁支持。
- **更早版本** 将不再获得常规更新或修复。

升级计划应结合发布节奏与约 3 个月的补丁支持窗口安排；该窗口不等于所有策略都有统一的迁移截止日期。

### ClusterPolicy 弃用提醒

1.18 公告当时计划在 2026 年稍晚弃用 ClusterPolicy，并给出以下迁移方向。实施时应再核对目标版本的支持状态与功能差异：

| 旧类型 | 新类型 |
|--------|--------|
| ClusterPolicy (validate) | ValidatingPolicy |
| ClusterPolicy (mutate) | MutatingPolicy |
| ClusterPolicy (generate) | GeneratingPolicy |
| ClusterPolicy (imageVerify) | ImageValidatingPolicy |
| CleanupPolicy | DeletingPolicy |

迁移建议：

1. 开始迁移现有策略
2. 使用 CLI 进行充分测试
3. 反馈功能差距或问题

### Roadmap

公告列出的路线图方向包括：

- 持续投入基于 CEL 的策略类型
- 改进策略编写体验
- 在多集群环境中扩展策略能力
- 拓展 AI governance 与策略驱动自动化能力

## 参考资料

- [Kyverno Docs](https://kyverno.io/docs/)、[GitHub Releases](https://github.com/kyverno/kyverno/releases)、[Kyverno Helm Chart](https://artifacthub.io/packages/helm/kyverno/kyverno/)
- [Kyverno 安装与高可用](https://kyverno.io/docs/installation/installation/)、[Validate Rules](https://kyverno.io/docs/policy-types/cluster-policy/validate/)、[Generate Rules](https://kyverno.io/docs/policy-types/cluster-policy/generate/)、[Policy Reports](https://kyverno.io/docs/guides/reports/)
- [Policy Reporter Docs](https://kyverno.github.io/policy-reporter/)、[Kyverno Policy Reporter](https://kyverno.io/docs/kyverno-policy-reporter/)
- [CNCF：Announcing Kyverno release 1.18](https://www.cncf.io/blog/2026/05/05/announcing-kyverno-release-1-18/)
- [CNCF 毕业公告](https://www.cncf.io/announcements/2026/04/02/cloud-native-computing-foundation-announces-kyverno-graduation/)
- [CVE-2026-4789](https://github.com/advisories/GHSA-rggm-jjmc-3394)、[CVE-2026-41323](https://github.com/kyverno/kyverno/security/advisories/GHSA-f9g8-6ppc-pqq4)
- [Kyverno Roadmap](https://github.com/kyverno/kyverno/milestones)
- [补充策略材料：Kyverno 拦坑？策略直接抄](https://mp.weixin.qq.com/s/P07bjN2JFvGnbdtVj-yfQw?scene=1&click_id=49847292)（WAKEUP 技术，2026-10-15；策略与上线经验已按主题合并）
