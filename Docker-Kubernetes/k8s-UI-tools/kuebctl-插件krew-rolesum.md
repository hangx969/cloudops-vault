---
title: "kubectl 插件指南：Krew 安装、常用工具与 RBAC 排查"
tags:
  - kubernetes
  - krew
  - rbac
  - tools
aliases:
  - krew-rolesum
  - kubectl 插件 krew 和 rolesum
  - kubectl 不够用？krew 装 10 插件
date: 2026-10-11
source: "https://mp.weixin.qq.com/s/H0PCEn6yVjbskCUB7hl94g"
---

# kubectl 插件指南：Krew 安装、常用工具与 RBAC 排查

排查 Kubernetes 问题时，常见的任务包括查看资源创建关系、盘点镜像、检查权限和跟踪多个 Pod 的日志。kubectl 插件把这些操作封装成独立命令，Krew 则负责插件的发现、安装、升级和卸载。

常用插件覆盖上下文切换、配置整理、资源关系、镜像检查、RBAC 排查、日志聚合、资源分配和 CI 清单检查。

> [!note] 示例与使用范围
> 命令与输出用于说明插件的字段和使用场景，未在实际集群执行。参数和平台支持请以所用版本的帮助信息为准。

## 插件机制与 Krew 的职责

### kubectl 如何发现插件

kubectl 从 `PATH` 查找名为 `kubectl-xxx` 的可执行文件，再通过 `kubectl xxx` 调用。插件可以是脚本，也可以是编译后的二进制；不需要向 kubectl 注册。

下面的示例创建一个简单插件。写入 `/usr/local/bin` 需要相应权限。

~~~bash
cat > /usr/local/bin/kubectl-hello <<'EOF'
#!/bin/sh
echo "hello from plugin, args: $*"
EOF
chmod +x /usr/local/bin/kubectl-hello
kubectl hello world
# hello from plugin, args: world
~~~

kubectl 把参数交给插件，由插件自行解析。因此，不同插件支持的 `-n`、`--context`、`--as` 等参数可能不同，使用前应查看各自的 `--help`。Kubernetes 官方说明见 [Extend kubectl with plugins](https://kubernetes.io/docs/tasks/extend-kubectl/kubectl-plugins/)。

### Krew 管理什么

Krew 的默认索引是 [krew-index](https://github.com/kubernetes-sigs/krew-index)。每个插件的 manifest 描述版本、支持的平台、下载地址、校验和与安装文件。Krew 根据 manifest 获取安装包，将插件安装到自己的目录，并在 `KREW_ROOT/bin` 中提供可被 kubectl 发现的入口。

`PATH` 需要手动配置，Krew 不会自动修改 shell 配置。查看插件信息：

~~~bash
kubectl krew info tree
# NAME: tree
# URI: https://github.com/ahmetb/kubectl-tree/releases/download/v0.5.0/kubectl-tree_v0.5.0_linux_amd64.tar.gz
# SHA256: 3f0a9c1e6b8d4a...
# DESCRIPTION:
#   Show sub-resources of a Kubernetes API object with ownerReferences.
~~~

上例的版本与输出仅用于说明格式；`SHA256` 已截断，不能用于校验。实际下载时应以当前 manifest 中对应平台的 `URI` 和完整 `SHA256` 为准。

### 凭据与执行边界

插件是本机程序，kubectl 不为它提供沙箱。它可以读取本机文件，包括 kubeconfig 中的凭据。访问集群时通常使用当前 kubeconfig 和认证身份，但插件也可能有自己的配置、身份切换或凭据解析方式。

Krew 索引便于追溯插件来源和安装包，不等于插件代码已经完成安全审计。安装前应检查源码、维护记录、发布包与平台支持；不能只凭 star 数量或索引收录情况判断可信度。

## 安装与维护 Krew

### macOS/Linux 安装

先安装 `git`，然后使用官方安装脚本：

~~~bash
(
  set -x; cd "$(mktemp -d)" &&
  OS="$(uname | tr '[:upper:]' '[:lower:]')" &&
  ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/\(arm\)\(64\)\?.*/\1\2/' -e 's/aarch64$/arm64/')" &&
  KREW="krew-${OS}_${ARCH}" &&
  curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz" &&
  tar zxvf "${KREW}.tar.gz" &&
  ./"${KREW}" install krew
)
~~~

把以下一行写入 Bash 的 `~/.bashrc` 或 Zsh 的 `~/.zshrc`，再打开一个新终端：

~~~bash
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"
~~~

现有笔记中的 Bash 写法如下；使用 Zsh 时把目标文件换成 `~/.zshrc`。

~~~bash
tee -a ~/.bashrc <<'EOF'
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"
EOF
~~~

验证安装并查找插件：

~~~bash
kubectl krew version
# OPTION        VALUE
# GitTag        v0.4.4
# GitCommit     fa4a02c
# IndexURI      https://github.com/kubernetes-sigs/krew-index.git
# BasePath      /root/.krew
# BinPath       /root/.krew/bin

kubectl krew search        # 搜所有可用插件
kubectl krew search ctx    # 按关键字搜
kubectl krew info tree     # 看某个插件的说明
~~~

这里的 `v0.4.4`、提交号与 `/root/.krew` 是示例值，不是版本要求或固定安装路径。安装步骤以 [Krew 官方安装文档](https://krew.sigs.k8s.io/docs/user-guide/setup/install/) 为准。

### Windows 安装

现有笔记通过 Scoop 安装 Helm、kubectl 和 Krew，相关步骤见 [[Docker-Kubernetes/helm/helmv3-安装与使用|Helm v3 安装与使用]]。

该笔记记录的 Krew 可执行文件目录为 `D:\0Software\scoop\apps\krew\current`；实际位置以本机 Scoop 配置为准。需要按官方流程完成 Krew 自安装时，进入 `krew.exe` 所在目录，在命令提示符中执行：

~~~powershell
.\krew install krew
~~~

随后将 `%USERPROFILE%\.krew\bin` 加入 `PATH`，打开新的命令行窗口，运行 `kubectl krew` 检查。官方 Windows 手动安装流程要求管理员权限以创建符号链接。

不同插件支持的平台各不相同。例如，当前 Krew 索引中的 `ctx/ns` 提供 macOS/Linux 脚本，并不覆盖本文所有安装方式中的 Windows 环境；安装前查看 `kubectl krew info <插件名>` 的平台信息。

### GitHub 访问受限与离线安装

Krew 安装插件通常涉及两个独立来源：Git 索引仓库和 manifest 指定的 Release 安装包。只解决其中一项，另一项仍可能超时。

按环境选择以下方法：

1. **使用可用代理。** 在 shell 中配置 `HTTPS_PROXY` 后重试。
2. **使用内网索引和制品库。** 将索引镜像到内网 Git，并同步插件安装包；manifest 的下载地址也需要指向可访问的位置。
3. **使用本地 manifest 与安装包。** 预先下载匹配操作系统和架构的 manifest、归档文件，在目标机器上从本地安装。
4. **直接分发可执行文件。** 下载插件 Release，解压并校验后，将入口命名为 `kubectl-<插件名>`，放入 `PATH` 中。这种安装不由 Krew 记录和升级。

手动放置 Krew 二进制时，以 Linux amd64 为例：

~~~bash
# 1. 从可信 Release 下载对应平台的安装包后解压
tar zxvf krew-linux_amd64.tar.gz
ls -l ./krew-linux_amd64

# 2. 放入自定义目录，入口命名为 kubectl-krew
export KREW_ROOT=/opt/krew
mkdir -p "$KREW_ROOT/bin"
mv ./krew-linux_amd64 "$KREW_ROOT/bin/kubectl-krew"
chmod +x "$KREW_ROOT/bin/kubectl-krew"

# 3. 持久化配置；写入 /etc/profile.d 需要相应权限
echo 'export KREW_ROOT=/opt/krew' >> /etc/profile.d/krew.sh
echo 'export PATH=$KREW_ROOT/bin:$PATH' >> /etc/profile.d/krew.sh
source /etc/profile.d/krew.sh
~~~

这个流程只让 `kubectl krew` 能找到本地程序。普通 `install` 命令仍可能访问远端索引和安装包，不能据此认为已经具备完整离线安装环境。

Krew 支持用本地文件安装插件：

~~~bash
# 两个文件必须来自同一版本，并匹配目标平台
kubectl krew install --manifest=./tree.yaml --archive=./tree.tar.gz
~~~

manifest 中的校验和必须与本地归档一致；不能把截断的示例 SHA256 用于验证。`--no-update-index` 只跳过索引更新，并不会自动提供尚未下载的安装包。参数依据见 [Krew install 实现](https://github.com/kubernetes-sigs/krew/blob/master/cmd/krew/cmd/install.go)。

内网索引使用当前的 `index` 子命令管理：

~~~bash
# 先把实际内网 Git 地址设置为 INTERNAL_KREW_INDEX_URL
kubectl krew index add corp "$INTERNAL_KREW_INDEX_URL"
kubectl krew install corp/tree
kubectl krew index list
~~~

如果需要让内网索引成为 `default`，可以先移除原默认索引，再以 `default` 名称添加内网镜像。详见 [自定义插件索引](https://krew.sigs.k8s.io/docs/user-guide/custom-indexes/)。

### 插件的日常操作

下面包含来源文章涉及的插件，以及现有笔记中的 rolesum。按需求选择安装，也可以一次安装多个：

~~~bash
kubectl krew install ctx ns neat tree get-all images whoami who-can rolesum tail resource-capacity score outdated
kubectl krew upgrade             # 升级全部已安装插件
kubectl krew upgrade ctx         # 升级单个插件
kubectl krew list                # 查看已安装插件及版本
kubectl krew uninstall neat      # 卸载指定插件
kubectl krew update              # 更新本地索引
~~~

安装通常会更新索引；在 CI 中应把插件版本纳入构建和测试记录，避免每次运行都下载不受控的最新版。

## 上下文切换与配置整理

### ctx / ns：切换集群和默认命名空间

`ctx` 和 `ns` 是 kubectx/kubens 通过 Krew 提供的插件入口，用于切换 kubeconfig 的当前 context 和该 context 的默认 namespace。

~~~bash
kubectl krew install ctx ns
~~~

~~~bash
kubectl ctx
# prod-beijing
# prod-shanghai      <- 当前
# staging

kubectl ctx prod-beijing
# Switched to context "prod-beijing".

kubectl ns
# default
# kube-system
# monitoring
# payment            <- 当前

kubectl ns payment
# namespace/payment set as current

kubectl ns -         # 切回上一个命名空间，跟 cd - 一个手感
~~~

`kubectl ns` 会持久化修改 kubeconfig，而不是只改变当前终端的状态。读取同一份 kubeconfig 的其他终端也可能受影响。共享跳板机上应确认各用户是否共用配置；切换后需要恢复时可使用 `kubectl ns -`。

CI 更适合显式指定上下文和命名空间，避免依赖交互式切换产生的状态。更多多集群配置见 [[Docker-Kubernetes/k8s-installation-management/k8s多集群kubeconfig管理|多集群 kubeconfig、kubectx 与 kubens]]；插件文档见 [kubectx/kubens](https://github.com/ahmetb/kubectx)。

### neat：清理 YAML/JSON 中的运行时信息

neat 删除 `status`、部分 metadata、默认值和已知控制器注入信息，让导出的资源更容易阅读。适合整理模板、参考线上配置和比较差异。

~~~bash
kubectl krew install neat
~~~

~~~bash
kubectl get deploy payment-api -o yaml | kubectl neat
# apiVersion: apps/v1
# kind: Deployment
# metadata:
#   name: payment-api
#   namespace: payment
#   labels:
#     app: payment-api
# spec:
#   replicas: 3
#   selector:
#     matchLabels:
#       app: payment-api
#   template:
#     metadata:
#       labels:
#         app: payment-api
#     spec:
#       containers:
#       - name: api
#         image: registry.internal/payment/api:v2.3.1
#         ports:
#         - containerPort: 8080

kubectl get pod payment-api-7d9f8b6c4-x2mnp -o yaml | kubectl neat > pod-template.yaml
kubectl get svc payment-api -o json | kubectl neat
~~~

这类输出需要在复用前审查。neat 会清理一些现场字段，例如已知的 `spec.nodeName`，但不能保证所有资源都能直接 `apply`：Service 的地址、环境相关引用、控制器关系等仍要核对。它整理的是资源清单，也不会把清单转换成 Helm values。

字段处理方式见 [kubectl-neat 文档](https://github.com/itaysk/kubectl-neat/blob/v2.0.4/Readme.md)。

## 资源关系、盘点与镜像检查

### tree：按 ownerReferences 展示资源树

tree 从指定资源向下查找依赖对象，适合查看 Deployment、ReplicaSet、Pod，以及有 ownerReferences 关系的 Operator 资源。

~~~bash
kubectl krew install tree
~~~

~~~bash
kubectl tree deploy payment-api -n payment
# NAMESPACE  NAME                                READY  REASON  AGE
# payment    Deployment/payment-api              -              12d
# payment    ├─ReplicaSet/payment-api-7d9f8b6c4  -              12d
# payment    │ └─Pod/payment-api-7d9f8b6c4-x2mn  True           3h
# payment    │ └─Pod/payment-api-7d9f8b6c4-k9pq  True           3h
# payment    │ └─Pod/payment-api-7d9f8b6c4-b7rt  True           3h

kubectl tree helmrelease redis -n default
# default  HelmRelease/redis
# default  ├─StatefulSet/redis-master
# default  │ └─Pod/redis-master-0
# default  └─ConfigMap/redis-config

kubectl tree pod payment-api-7d9f8b6c4-x2mnp -n payment
~~~

tree 只识别 `ownerReferences`。仅通过 label、Helm 注解或外部流程关联的资源，不一定能组成树；跨集群关系也不会自动连接。示例中的 `HelmRelease → StatefulSet/ConfigMap` 仅在相应控制器设置了 ownerReferences 时才成立，不能理解为所有 Helm 安装都会产生这棵树。

查询自定义资源及其子资源还需要相应读取权限。tree 展示的是指定对象的子资源，不会运行控制器，也不支持 `--run-workload-controllers` 参数。支持的参数见 [kubectl-tree](https://github.com/ahmetb/kubectl-tree/blob/v0.6.0/README.md)。

### get-all：盘点可读取的 API 资源

原生 `kubectl get all` 不包含所有资源类型。get-all 遍历可发现的 API 资源，适合接手陌生集群、迁移前清点资源和检查新建对象。

~~~bash
kubectl krew install get-all
~~~

~~~bash
kubectl get-all -n payment
# NAME                                  NAMESPACE  KIND                 AGE
# payment-api-7d9f8b6c4-x2mnp           payment    Pod                  3h
# payment-api                           payment    Deployment           12d
# payment-api                           payment    Service              12d
# payment-api-config                    payment    ConfigMap            12d
# payment-api-token                     payment    Secret               12d
# payment-api-hpa                       payment    HorizontalPodAutoscaler  12d

kubectl get-all --since 1h            # 只看一小时内新建的，排查"刚才谁动了集群"
kubectl get-all -o wide
~~~

它的“all”仍受 API 可用性、RBAC 和排除配置约束；当前版本默认排除 Event 与 PodMetrics，也可能显示不完整结果。`--since 1h` 按创建时间筛选，不能据此查出“过去一小时谁修改了已有资源”。生产环境应先用 `-n` 限定范围，并关注请求耗时和 Forbidden 信息。

与 neat 结合，可以导出迁移前的配置对照：

~~~bash
kubectl get-all -n payment -o yaml | kubectl neat > payment-backup.yaml
wc -l payment-backup.yaml
# 1842 payment-backup.yaml
~~~

快照中的 `1842` 行只是示例值。这样的清单快照不包含完整应用数据，不保证资源读取的一致时间点、依赖恢复顺序或恢复成功，不能作为完整灾备方案。导出内容还可能含 Secret，需要控制保存和访问范围。

工具选项见 [get-all 使用说明](https://github.com/stackitcloud/kubectl-get-all/blob/v1.4.3/docs/USAGE.md)。

### images：盘点 Pod 引用的镜像

images 从集群中的 Pod 获取容器镜像信息，适合镜像仓库迁移、查找未升级的工作负载和检查外部仓库来源。

~~~bash
kubectl krew install images
~~~

~~~bash
kubectl images -n payment
# 以下是原文镜像表的示意内容，字段与格式以实际版本为准
# Pod                              Container Image
# payment-api-7d9f8b6c4-x2mnp       registry.internal/payment/api:v2.3.1
# payment-api-7d9f8b6c4-x2mnp       registry.internal/envoy/sidecar:1.29.4
# payment-worker-5c8d7b9f4-n4jk     registry.internal/payment/worker:v2.2.9

# 当前 images 插件没有 --filter / --exclude，以下用文本过滤输出
kubectl images -A | rg 'v2[.]2'
kubectl images -A | rg -v 'registry[.]internal/'
~~~

后两条命令用于筛选表格行，也可能保留标题或统计行。插件的位置参数是 Pod 名称正则表达式，不是镜像 tag 过滤器。

查询对象是已有 Pod，不能代表 Git 或 Helm 清单中的全部镜像，也不能把“Pod 引用了该镜像”直接等同于“容器正在健康运行”。全量查询可能较慢，先限定命名空间；参数与输出列见 [kubectl-images](https://github.com/chenjiandongx/kubectl-images/blob/v0.6.5/README.md)。

### outdated：检查容器镜像是否存在更新版本

outdated 收集可读取的 Pod 镜像，并连接镜像仓库比较 tag 或发布时间。它用于评估镜像更新，不检查 Kubernetes 废弃 API。

~~~bash
kubectl krew install outdated
~~~

~~~bash
kubectl outdated
kubectl outdated --context='<上下文名称>'
~~~

查询还受镜像仓库网络、认证与 tag 命名方式影响。内网仓库不可达时，可能无法得到完整结果；发现更新也不意味着可以直接升级，仍要由业务方评估兼容性和发布计划。见 [outdated 使用说明](https://github.com/replicatedhq/outdated/blob/v0.4.1/doc/USAGE.md)。

**集群升级前的 API 检查单独处理。** 检查 `extensions/v1beta1` Ingress、`batch/v1beta1` CronJob 等旧 API 时，应使用相应的废弃 API 检查工具，参见 [[Docker-Kubernetes/k8s-UI-tools/k8s-API检查工具kubent|kubent：废弃 API 检查]]。需要保留现有 Ingress 配置时，可先导出整理：

~~~bash
kubectl get ingress shop-web -o yaml | kubectl neat > ingress-old.yaml
~~~

## RBAC 排查：身份、权限来源与授权结果

这四个命令回答不同的问题，可以组合使用：

| 命令 | 主要回答的问题 | 判断边界 |
| --- | --- | --- |
| `kubectl whoami` | 当前以什么身份访问集群？ | 输出能力受认证方式与插件实现影响 |
| `kubectl rolesum` | 某个主体绑定了哪些角色？ | 汇总 RBAC 角色及绑定 |
| `kubectl who-can` | 哪些主体的 RBAC 规则允许指定操作？ | 需要读取角色与绑定，分析结果可能不完整 |
| `kubectl auth can-i` | 指定身份能否获得该 API 操作的授权？ | 检查授权结果，不执行实际操作或准入流程 |

### whoami：确认当前认证身份

~~~bash
kubectl krew install whoami who-can
kubectl whoami
# kubecfg:admin
~~~

需要查询组信息时，使用插件支持的 `--all`：

~~~bash
kubectl whoami --all
# User:   kubecfg:admin
# Groups:
#         system:masters
#         system:authenticated
~~~

输出是格式示意，具体身份由实际认证配置决定；不要把 kubeconfig 中用户条目的名称当作已经验证的服务端身份。插件文档见 [kubectl-whoami](https://github.com/rajatjindal/kubectl-whoami/blob/v0.0.48/README.md)。

### rolesum：查看主体绑定的角色

rolesum 以可读的层级形式汇总某个 ServiceAccount、User 或 Group 的 RBAC 角色，方便追踪权限从哪个 Role/ClusterRole 和绑定获得。

~~~bash
kubectl krew install rolesum

# 默认主体类型是 ServiceAccount
kubectl rolesum ci-bot -n payment

# 查询 User 或 Group
kubectl rolesum -k User '<用户名>' -n payment
kubectl rolesum -k Group developer -n payment

# 只显示 ClusterRole，忽略命名空间级 Role
kubectl rolesum -c -k Group developer

kubectl rolesum --help
~~~

现有笔记中的 `kubectl rolesum <svc name>` 应理解并修正为 ServiceAccount/主体名称；它不查询 Service 对象。`-n` 指定查询的命名空间范围，`-k` 选择主体类型，`-c` 只显示 ClusterRole。具体参数见 [rolesum 官方用法](https://github.com/Ladicle/kubectl-rolesum#usage)。

### who-can：反查哪些主体具备 RBAC 权限

~~~bash
kubectl who-can delete pods -n payment
# No subjects found with RBAC permissions to delete pods in namespace payment.

kubectl who-can get secrets -n kube-system
# ROLEBINDING                NAMESPACE    SUBJECTS
# system:controller:token-cleaner  kube-system  ServiceAccount/kube-system/token-cleaner
# CLUSTERROLEBINDING          SUBJECTS
# cluster-admin               User/kubecfg:admin
~~~

who-can 需要列出 Role、ClusterRole 及其绑定。权限不足时，看到的角色数据和分析结果可能不完整。它通过 RBAC 规则推导主体，不代表已经验证了其他授权器、准入策略或操作执行结果。

`--as` 改变的是查询请求的身份，不会把 who-can 的输出变成“仅判断这个主体是否有权限”。这项区别尤其影响 ServiceAccount 排查。RBAC 本身是累加授权，不存在 RBAC 显式 deny 规则。工具说明见 [kubectl-who-can](https://github.com/aquasecurity/kubectl-who-can/blob/v0.4.0/README.md)。

### CI 报 Forbidden 时的排查顺序

1. 用 `whoami` 核对当前身份，确认没有把管理员账号的结果当作 CI 账号的结果。
2. 用 `rolesum` 查看目标 ServiceAccount 的角色来源；必要时用 `who-can` 反查拥有该动作的主体。
3. 用 `auth can-i` 查询目标身份的授权结果。
4. 根据所需动作、资源、API group、命名空间和现有绑定，决定是否修改 Role/RoleBinding。

~~~bash
kubectl rolesum ci-bot -n payment
kubectl who-can create deployments -n payment

kubectl auth can-i create deployments -n payment \
  --as=system:serviceaccount:payment:ci-bot
# no
~~~

调用 `--as` 的查询账号需要相应 impersonation 权限；模拟组身份时还应核对组信息。不能仅凭 who-can 和 can-i 的结果一致，就直接扩大角色权限。`auth can-i` 检查授权层，实际创建对象还可能受到准入策略等约束。授权查询与 impersonation 的定义见 [kubectl auth can-i](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_auth/kubectl_auth_can-i/) 和 [用户模拟](https://kubernetes.io/docs/reference/access-authn-authz/user-impersonation/)。

基础概念见 [[KnowledgeBase/concepts/RBAC|RBAC]]。

## 日志排查与资源分配

### tail：聚合多个 Pod 的日志

Krew 中的 tail 对应 [Kail](https://github.com/boz/kail)。它在客户端并发获取匹配 Pod/容器的日志，并随 Pod 集合变化调整跟踪对象，适合灰度发布或多副本服务排错。

~~~bash
kubectl krew install tail
~~~

~~~bash
kubectl tail -n payment -l app=payment-api
# payment-api-7d9f8b6c4-x2mnp › 2026-10-09 22:14:03 GET /api/v1/pay 200 12ms
# payment-api-7d9f8b6c4-k9pq  › 2026-10-09 22:14:03 GET /api/v1/pay 200 9ms
# payment-api-7d9f8b6c4-b7rt  › 2026-10-09 22:14:04 GET /api/v1/pay 503 3021ms

kubectl tail -n payment -l app=payment-api --since 10m
kubectl tail -n payment -l app=payment-api -c sidecar    # 只跟 sidecar 容器
~~~

`-l` 是 Pod 标签选择器，`-n` 是命名空间，`-c` 限制容器名称，`--since` 控制回看的历史时间范围。Pod 数量多时，本机连接数和 API Server 压力都会增加；先缩小标签与命名空间范围。`--since` 不限制持续日志流的速率或并发数。

已有 [[Docker-Kubernetes/k8s-UI-tools/kubectl-可视化插件k9s-stern|k9s 与 stern 笔记]] 介绍了终端 UI 和另一种多 Pod 日志工具，可以结合使用。

### resource-capacity：比较 requests、limits 和实际用量

resource-capacity 对应 kube-capacity，展示节点以及可选 Pod/容器层面的 CPU、内存 requests/limits；`--util` 则增加实际使用量，需要集群中的 metrics-server 正常工作。

~~~bash
kubectl krew install resource-capacity
~~~

~~~bash
kubectl resource-capacity
# 原文输出节选，仅用于识别字段
# NODE              CPU REQUESTS  CPU LIMITS    MEMORY REQUESTS  MEMORY LIMITS
# *                 5600m (35%)   11200m (70%)   12Gi (42%)       24Gi (84%)
# node-bj-prod-01    2100m (52%)   4200m (105%)  4.5Gi (58%)      9Gi (116%)
# node-bj-prod-02    1800m (45%)   3600m (90%)   4Gi (51%)        8Gi (102%)
# node-bj-prod-03    1700m (42%)   3400m (85%)   3.5Gi (45%)      7Gi (90%)

kubectl resource-capacity --pods --util -n payment
~~~

使用 `-n payment` 时，只汇总该命名空间的 Pod，不能把它当作节点上全部工作负载的资源分配量。

读取输出时区分以下几项：

- **requests 分配量**：用于资源调度判断，不是容器当前消耗量。
- **limits 分配量**：配置的使用上限；总和超过节点容量表示存在超售，不表示此刻已经达到该负载。
- **util 使用量**：通过 metrics 获取的现场用量，应结合 `kubectl top` 或监控数据判断。

示例表格中三节点的绝对数可以相加，但汇总百分比与节点百分比推算出的总容量不一致，不能用于实际容量结论。当前版本没有 `--pod-template` 参数，也不会输出 `Allocations for pod template ...: 14`；不能直接计算某份 Deployment 还能调度多少副本。

容量规划仍需要结合工作负载资源需求、节点可分配资源和调度条件。CPU 或内存 limits 超售会增加资源竞争风险，但不能据此认定所有 Pod 一定同时发生 throttle 或 OOM。功能与参数见 [kube-capacity v0.8.0](https://github.com/robscott/kube-capacity/blob/v0.8.0/README.md)。

## 清单检查与 CI 集成

### score：静态检查 Kubernetes 清单

score 对应 kube-score，检查资源 requests/limits、安全上下文、探针、镜像与相关对象配置。它可以在 PR 阶段发现清单中的问题，但不连接实际集群，也不能发现所有运行时故障。

~~~bash
kubectl krew install score
~~~

诊断示意如下；实际检查项、级别与文案以所用版本为准。

~~~bash
kubectl score ./deploy.yaml
# apps/v1/Deployment payment-api
#     [CRITICAL] Container Resources: CPU limit is not set
#     [CRITICAL] Container Resources: Memory limit is not set
#     [CRITICAL] Container Security Context: Container has no configured security context
#     [WARNING]  Pod Probes: Container has the same readiness and liveness probe
# v1/Service payment-api
#     [OK] Service Targets Pod

# 检查目录中的 YAML；警告也返回退出码 1
kubectl score --exit-one-on-warning ./manifests/*.yaml
~~~

镜像 tag 与 pull policy 是不同的检查。kube-score 的显式、非 latest tag 检查不能证明该 tag 不可变，pull policy 的诊断也不能用于判断 tag 是否不可变。

JSON v2 的 grade 在每个对象的 `checks` 数组中。筛选低于 5 分的检查项，需要进入该数组；与来源文章的阈值一样，这会筛出 critical，不包含 grade 为 5 的 warning：

~~~bash
set -o pipefail
kubectl score -o json ./deploy.yaml |
  jq '.[] | {object_name, checks: [.checks[] | select(.grade < 5)]} |
      select(.checks | length > 0)'
~~~

与 jq 等程序组合时，要保留 kube-score 的失败退出码，避免管道最后一个命令成功而使 CI 错误放行。老项目可以先观察默认检查结果，再决定是否启用 `--exit-one-on-warning`。默认模式本身也会在发现 critical 时退出失败。

命令行参数见 [kube-score](https://github.com/zegl/kube-score/blob/v1.20.0/README.md)，JSON 字段见 [JSON v2 数据结构](https://github.com/zegl/kube-score/blob/v1.20.0/renderer/json_v2/api.go)。

### 用注解记录例外规则

`kube-score/ignore` 在对象上忽略指定检查，值是以逗号分隔的规则 ID。以下 Deployment 示例通过注解指定例外规则。

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-api
  namespace: payment
  annotations:
    kube-score/ignore: container-resource-requests-equal-limits,pod-networkpolicy
spec:
  replicas: 3
  selector:
    matchLabels:
      app: payment-api
  template:
    metadata:
      labels:
        app: payment-api
    spec:
      containers:
      - name: api
        image: registry.internal/payment/api:v2.3.1
        resources:
          requests: {cpu: 200m, memory: 256Mi}
          limits:   {cpu: 500m, memory: 512Mi}
        securityContext:
          runAsNonRoot: true
          readOnlyRootFilesystem: true
        readinessProbe:
          httpGet: {path: /healthz, port: 8080}
        livenessProbe:
          httpGet: {path: /healthz, port: 8080}
          initialDelaySeconds: 30
~~~

这个示例只演示注解、资源与安全上下文的写法，不表示它已经通过全部检查。readiness 与 liveness 都访问 `/healthz`，仍可能触发探针检查；忽略两条规则并不会忽略其他问题。`container-resource-requests-equal-limits` 是可选规则，是否生效取决于启用配置。规则定义见 [kube-score 检查清单](https://github.com/zegl/kube-score/blob/v1.20.0/README_CHECKS.md)。

## 生产使用与常见问题

### 来源、安装位置和版本

- **检查来源。** 优先使用可追溯的索引、源码和 Release，核对近期提交、发布记录与审查情况。近半年是否有提交和 release 可作为维护状况线索，但不是安全保证。
- **限定安装位置。** 将插件放在运维机、跳板机或 CI 镜像中，生产控制面和工作节点保持最小安装。
- **分别核对版本。** kubectl 的支持范围通常是相对 kube-apiserver 前后一个 minor；插件的客户端库和 API 支持范围独立于 kubectl，不能假设都会使用 kubectl 本身的 client-go。
- **更新后验证。** 升级 kubectl 时也应检查插件版本和兼容性；`kubectl krew upgrade` 是升级入口，不能代替验证。
- **CI 显式安装。** 把插件预装进基础镜像，或在流水线中显式安装并处理网络失败重试。离线环境应把匹配平台的二进制、manifest 与安装包纳入内部制品库。

kubectl 版本范围依据见 [Kubernetes 版本偏差策略](https://kubernetes.io/releases/version-skew-policy/#kubectl)。

### 多用户共享 KREW_ROOT

默认 `$HOME/.krew` 属于单用户安装。共享目录可按以下方式配置：

~~~bash
export KREW_ROOT=/opt/krew
install -d -o root -g ops -m 0775 /opt/krew
echo 'export KREW_ROOT=/opt/krew; export PATH=$KREW_ROOT/bin:$PATH' > /etc/profile.d/krew.sh
~~~

示例假定 `ops` 组已存在，并由有权限的账号执行。`0775` 允许 `ops` 组成员写入目录，因此写权限只能授予可信的插件维护者：替换共享二进制会影响其他使用者。可以由运维统一升级，避免所有使用者都能修改插件。`KREW_ROOT` 的共享权限与 kubeconfig 凭据的共享是两件事，不能因为共用插件就共用账号凭据。

### 安装成功，但命令找不到

例如 `kubectl krew install ctx` 成功后，`kubectl ctx` 仍报 `unknown command`。依次检查：

1. 用 `kubectl krew list` 确认插件是否登记为已安装。
2. 检查 `KREW_ROOT/bin` 是否在当前 `PATH`，是否只在旧终端中临时配置过。
3. 确认安装和运行使用同一用户、同一 Krew 根目录；使用 sudo 安装可能将文件写入 root 的 HOME。
4. 检查可执行文件入口和插件支持的平台。

Bash 中的 PATH 修复命令：

~~~bash
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"
echo 'export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"' >> ~/.bashrc
~~~

使用 Zsh 时应写入 `~/.zshrc`。默认用户安装流程不需要为了安装 Krew 而使用 sudo；系统级共享目录的创建和维护则由有权限的账号完成。

### 公司网络访问 GitHub 超时

若卡在 `Updating the local copy of plugin index`，先区分索引 Git 访问失败还是 Release 下载失败。代理、内网索引、内网制品库和手工二进制分发的选择见本篇“GitHub 访问受限与离线安装”。

`kubectl krew --index-uri=... ` 不属于当前自定义索引用法，应使用 `kubectl krew index add`；镜像索引时也要处理插件包的下载地址。

### metrics 查询失败

WAKEUP技术记录了一个 Kubernetes 1.29 场景：旧版 resource-capacity 报 `failed to get node metrics: the server could not find the requested resource`，作者将其归因为 metrics API 版本不匹配，并通过升级插件处理：

~~~bash
kubectl krew upgrade resource-capacity
~~~

该案例尚未复现，不能据此认定所有同类错误都由插件版本导致。使用 `--util` 时也要检查 metrics-server、API 可用性和访问权限，再决定是否升级插件。

## 使用检查清单

- [ ] 插件安装在运维机、跳板机或 CI 镜像中，生产节点保持最小安装。
- [ ] 来源、源码、Release 与校验信息可追溯，不运行只有远端安装脚本而无法核对源码的未知插件。
- [ ] 评估项目维护记录；索引登记、star 数量和近期更新均不能代替代码审查。
- [ ] 已确认插件支持本机操作系统、架构及目标集群 API。
- [ ] `PATH` 写入正确的 shell 配置，打开新终端后仍可找到命令。
- [ ] 共享 `KREW_ROOT` 仅由可信维护者写入，凭据仍按用户隔离。
- [ ] kubectl 与 kube-apiserver 的 minor 版本偏差处于支持范围，插件升级经过验证。
- [ ] CI 显式安装或预装插件，处理下载重试、版本记录与非零退出码。
- [ ] 离线安装所需的二进制、manifest、归档与完整校验和已放入可用制品库。
- [ ] 使用 `ctx/ns` 后确认持久化的 kubeconfig 状态，必要时切回原命名空间。
- [ ] who-can/rolesum 的 RBAC 分析使用 `auth can-i` 复核；模拟身份需要相应权限。
- [ ] resource-capacity 的分配量与实际使用量分开解读，metrics 查询正常。
- [ ] 清单导出、日志和镜像查询限定范围；配置快照的 Secret 与恢复边界已经审查。
- [ ] score 的例外注解有明确理由，CI 没有丢失检查工具的失败退出码。

## 插件速查表

| 插件 | 用途 | 高频命令 |
| --- | --- | --- |
| ctx / ns | 切换 context 与默认 namespace | `kubectl ctx`；`kubectl ns payment`；`kubectl ns -` |
| neat | 清理资源 YAML/JSON | <code>kubectl get deploy x -o yaml &#124; kubectl neat</code> |
| tree | 按 ownerReferences 展示子资源 | `kubectl tree deploy payment-api -n payment` |
| get-all | 盘点可读取的 API 资源 | `kubectl get-all -n payment --since 1h` |
| images | 查看 Pod 引用的镜像 | `kubectl images -n payment` |
| outdated | 比较镜像仓库中的更新版本 | `kubectl outdated` |
| whoami | 查看当前认证身份 | `kubectl whoami`；`kubectl whoami --all` |
| rolesum | 汇总主体绑定的 RBAC 角色 | `kubectl rolesum ci-bot -n payment` |
| who-can | 反查拥有指定 RBAC 动作的主体 | `kubectl who-can delete pods -n payment` |
| tail | 聚合匹配 Pod/容器的日志 | `kubectl tail -n payment -l app=payment-api` |
| resource-capacity | 查看 requests/limits 与用量 | `kubectl resource-capacity --pods --util -n payment` |
| score | 静态检查清单 | `kubectl score --exit-one-on-warning ./manifests/*.yaml` |

日常切换与阅读配置可先选 ctx/ns、neat、tree；镜像、日志、权限和资源分配工具按排查任务选择。CI 可以从 score 的默认检查开始，逐步收紧已确认适用的规则。

## 使用边界与参考资料

以下能力与参数以 2026-10-11 查询到的官方资料为准：

| 常见误用或示例 | 正确用法与边界 |
| --- | --- |
| Krew 自动把目录加入 PATH；插件本体都是二进制 | PATH 要手动配置；插件也可以是脚本 |
| `--no-update-index` 可解决离线安装 | 只跳过索引更新；本地安装还需要 manifest、归档及校验信息 |
| `kubectl krew --index-uri=... ` | 自定义索引使用 `index add` 和 `<索引名>/<插件名>` |
| `tree --run-workload-controllers` | tree 不支持此参数，也不会运行工作负载控制器 |
| `images --filter/--exclude`；单命名空间输出却统计“3 namespaces” | 当前插件不提供这些过滤参数；使用文本筛选，并核对命名空间范围与汇总统计是否一致 |
| `outdated --include-unsupported` 与废弃 API 表 | outdated 检查镜像更新；废弃 API 检查另用 kubent 等工具 |
| `resource-capacity --pod-template` 和“可调度 14 个” | 当前插件没有该参数或输出；保留资源分配与用量检查用途 |
| resource-capacity 示例的汇总百分比 | 与所列节点的容量推算不一致，只能用于识别输出字段 |
| `who-can --as=<主体>` 用于判断该主体能否操作 | `--as` 改变查询身份；目标主体的授权结果用 `auth can-i --as=... ` |
| `kubectl rolesum <svc name>` | 默认参数是 ServiceAccount 名称，也可通过 `-k` 查询 User/Group |
| `score -f ... --exit-code-on-warning`；<code>jq '.[] &#124; select(.grade &lt; 5)'</code> | 使用位置文件参数与 `--exit-one-on-warning`；JSON v2 的 grade 在 `checks[]` 中 |
| 相同的 Readiness/Liveness 探针；镜像检查 | 相同探针仍可能告警；镜像 tag 与 pull policy 是不同检查 |
| `--since` 可以限制日志跟踪速率；get-all 能查最近修改者 | `--since` 只限定日志回看时间或资源创建时间，不提供限速或审计结论 |

主要来源：

- [WAKEUP技术：kubectl 不够用？krew 装 10 插件](https://mp.weixin.qq.com/s/H0PCEn6yVjbskCUB7hl94g)，发布于 2026-10-09。
- [Krew GitHub](https://github.com/kubernetes-sigs/krew) 与 [Krew 快速入门](https://krew.sigs.k8s.io/docs/user-guide/quickstart/)。
- [Krew 官方插件索引](https://github.com/kubernetes-sigs/krew-index/tree/master/plugins)：用于核对各插件的仓库、平台和版本。
- 各插件的官方文档与相关实现已在对应章节链接。
