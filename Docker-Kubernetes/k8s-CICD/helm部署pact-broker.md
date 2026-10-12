---
title: Helm 部署 Pact Broker
tags:
  - kubernetes
  - helm
  - pact-broker
aliases:
  - pact-broker部署
---

# Helm 部署 Pact Broker


## 介绍

### 契约测试

微服务的契约测试是一种确保微服务之间通信正确性的方法。在微服务架构中，每个服务都是独立运行的，它们通过轻量级的通信机制（如HTTP/REST API）进行交互。因此，每个服务都需要对外提供一个清晰的接口描述，这就是微服务的契约。

**特性：**

1. **消费者驱动**
   由接口使用方（消费者）定义契约，更贴近实际需求（比如前端团队可以先定义期望的 API 格式）。

2. **解耦测试**
   消费者和提供者可以独立开发测试，只需共享契约文件（无需同时启动两个服务）。

3. **多语言支持**
   支持 Java、Ruby、Go、.NET、JavaScript 等主流语言（像一个多语种翻译官）。

4. **契约管理**
   提供 **Pact Broker** 工具集中管理契约版本（类似合同档案馆）。

**典型使用场景：**

1. 前端和后端并行开发时，提前约定接口格式
2. 微服务频繁迭代时，防止接口变更引发故障
3. 替换服务实现技术栈时（如从 Java 改为 Go），确保接口兼容

### Pact

- 官网链接：[Pact Broker K8s 文档](https://docs.pact.io/pact_broker/kubernetes/readme)
- github地址：[Pact Broker Chart GitHub](https://github.com/pact-foundation/pact-broker-chart)

**Pact 工具的核心逻辑**

想象你（消费者）和餐馆（提供者）通过外卖平台合作：

1. **消费者测试**（你的角度）
   - 你模拟向餐馆下单：`POST /order {菜品: "鱼香肉丝", 数量: 2}`
   - 你期望餐馆返回：`{订单号: "123", 预计送达时间: "30分钟"}`
   - Pact 会记录这个交互过程，生成一份 **契约文件**（类似订单合同）

2. **提供者测试**（餐馆角度）
   - 餐馆用这份契约文件验证自己的接口：
     - 是否接受正确的请求格式？
     - 返回的数据结构是否匹配？
   - 如果验证通过，说明双方约定有效（就像餐馆确认能按约定出餐）

## 下载

~~~sh
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add pact-broker https://pact-foundation.github.io/pact-broker-chart/
helm repo update pact-broker
helm pull pact-broker/pact-broker --version 1.1.0
~~~

## 配置

添加ingress配置：

~~~yaml
#添加ingress配置
# Ingress parameters
ingress:
  # -- ingress.enabled Enable the creation of the ingress resource
  enabled: true

  # -- ingress.className Name of the IngressClass cluster resource which defines which controller will implement the resource (e.g nginx)
  className: "nginx-default"

  # -- ingress.annotations Additional annotations for the Ingress resource
  annotations:
    nginx.ingress.kubernetes.io/auth-url: "http://oauth2-proxy.oauth2-proxy.svc.cluster.local/oauth2/auth"
    nginx.ingress.kubernetes.io/auth-signin: "https://oauth2proxy.hanxux.local/oauth2/start?rd=https%3A%2F%2Fpact-broker.hanxux.local"

  # -- host Hostname to be used to expose the route to access the Pact Broker
  host: "pact-broker.hanxux.local"

  # Ingress TLS parameters
  tls:

    # -- ingress.tls.enabled Enable TLS configuration for the host defined at `ingress.host` parameter
    enabled: true

    # -- ingress.tls.secretName The name to which the TLS Secret will be called
    secretName: "pact-broker-tls-cert-secret"
~~~

pgsql的password用自定义的：

~~~yaml
# PostgreSQL [chart configuration](https://github.com/bitnami/charts/blob/master/bitnami/postgresql/values.yaml)
postgresql:

  # -- Switch to enable or disable the PostgreSQL helm chart
  enabled: true

  # The authentication details of the Postgres database
  auth:

    # -- Name for a custom user to create
    username: bn_broker

    # -- Password for the custom user to create
    password: ""

    # -- Name for a custom database to create
    database: bitnami_broker

    # -- Name of existing secret to use for PostgreSQL credentials
    existingSecret: "pact-pg-local-passwd" #这个secretname需要自己指定

    # The secret keys Postgres will look for to retrieve the relevant password
    secretKeys:

      # -- The key in which Postgres well look for, for the admin password, in the existing Secret
      adminPasswordKey: passwd # key name要自己指定

      # -- The key in which Postgres well look for, for the user password, in the existing Secret
      userPasswordKey: passwd # key name要自己指定

      # -- The key in which Postgres well look for, for the replication password, in the existing Secret
      replicationPasswordKey: passwd # key name要自己指定
~~~

## 安装

~~~sh
helm diff upgrade pact-broker -n observability \
pact-broker/pact-broker \
--version 1.1.0 \
-f values.yaml
#--set global.postgresql.auth.password=$PSSWD
~~~

## 升级

注意由于我们安装的时候是采用默认的postgres password，不是使用已有password，所以升级的时候会被要求提供这个数据库password，获取方式如下：

[Pact Broker 配置详情](https://docs.pact.io/pact_broker/kubernetes/readme#configuration-and-installation-details)

~~~sh
export POSTGRES_PASSWORD=$(kubectl get secret --namespace "observability" pact-broker-postgresql --kubeconfig $KUBECONFIG -o jsonpath="{.data.postgres-password}" | base64 -d)

helm upgrade -i pact-broker -n observability \
oci://${{ env.harborURL }}/${{ env.harborProjectName }}/$helmRepoName/$helmChartName \
--set postgresql.auth.password=$POSTGRES_PASSWORD \
--version $helmChartVersion \
-f ./base/external/pact-broker/values.yaml \
--history-max 5 \
--insecure-skip-tls-verify \
--kubeconfig $KUBECONFIG
~~~

> 本地部署的时候遇到pgsql无法认证的问题：
>
> 1. 如果开启了pgsql,采用自动生成数据库密码的方式（把postgresql.auth.password和existingSecret都置空），部署时会报错：
>
>    ~~~sh
>    Error: UPGRADE FAILED: cannot patch "pact-broker" with kind Deployment: Deployment.apps "pact-broker" is invalid: [spec.template.spec.containers[0].env[9].valueFrom.secretKeyRef.name: Invalid value: "": a lowercase RFC 1123 subdomain must consist of lower case alphanumeric characters, '-' or '.', and must start and end with an alphanumeric character (e.g. 'example.com', regex used for validation is '[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*'), spec.template.spec.containers[0].env[9].valueFrom.secretKeyRef.key: Required value]
>    ~~~
>
> 2. 如果开启pgsql，采用自己指定secret的方式（把postgresql.auth.password置空，existingSecret填secret name），pipeline需要这么写：
>
>    ~~~yaml
>          - name: Upgrade pact-broker
>            run: |
>              export helmChartVersion=${{env.pactVersion}}
>              export helmRepoName='pact-broker'
>              export helmChartName='pact-broker'
>
>              if kubectl get secret pact-pg-local-passwd -n observability --kubeconfig $KUBECONFIG 2>&1; then
>                PASSWD=$(kubectl get secret pact-pg-local-passwd -n observability --kubeconfig $KUBECONFIG -o jsonpath="{.data.passwd}" | base64 --decode)
>
>                helm upgrade -i pact-broker -n observability \
>                  oci://${{ env.harborURL }}/${{ env.harborProjectName }}/$helmRepoName/$helmChartName \
>                  --version $helmChartVersion \
>                  -f ./base/external/pact-broker/values.yaml \
>                  --history-max 5 \
>                  --insecure-skip-tls-verify \
>                  --kubeconfig $KUBECONFIG \
>                  --set postgresql.auth.password=$PASSWD
>              else
>                PASSWD=$( openssl rand -base64 10 )
>                kubectl create secret generic pact-pg-local-passwd --from-literal=passwd=$PASSWD --namespace=observability --kubeconfig $KUBECONFIG
>
>                helm upgrade -i pact-broker -n observability \
>                  oci://${{ env.harborURL }}/${{ env.harborProjectName }}/$helmRepoName/$helmChartName \
>                  --version $helmChartVersion \
>                  -f ./base/external/pact-broker/values.yaml \
>                  --history-max 5 \
>                  --insecure-skip-tls-verify \
>                  --kubeconfig $KUBECONFIG
>              fi;
>    ~~~
>
>    部署时不会报错，但是完成后pact-broker pod会报错连接不上pgsql，密码认证失败。问题暂时未解决。
>
> 3. 本地部署暂时采用直接在values.yaml里设置pgsql密码(postgresql.auth.password随便写了一个，existingSecret置空)。
>
>    但是helm upgrade的时候又会遇到报错：**The secret "pact-broker-postgresql" does not contain the key "user-password"。**
>
>    猜测可能是这个helm chart有bug，明明设置为不用existingSecret，他还是要去检测userPasswordKey字段，所以无奈之下手动创建了一个secret，将existingSecret设成这个secret，手动把需要的两个key加进去：
>
>    ~~~sh
>    kubectl create secret generic pact-broker-postgresql-secret \
>      --from-literal=admin-password=<password> \
>      --from-literal=user-password=<password> \
>      -n observability
>    ~~~
>
>    ~~~yaml
>    postgresql:
>      # -- Switch to enable or disable the PostgreSQL helm chart
>      enabled: true
>      # The authentication details of the Postgres database
>      auth:
>        # -- Name for a custom user to create
>        username: bn_broker
>        # -- Password for the custom user to create
>        password: "<password>"
>        # -- Name for a custom database to create
>        database: bitnami_broker
>        # -- Name of existing secret to use for PostgreSQL credentials
>        existingSecret: "pact-broker-postgresql-secret"
>        # The secret keys Postgres will look for to retrieve the relevant password
>        secretKeys:
>          # -- The key in which Postgres well look for, for the admin password, in the existing Secret
>          adminPasswordKey: admin-password
>          # -- The key in which Postgres well look for, for the user password, in the existing Secret
>          userPasswordKey: user-password
>    ~~~
