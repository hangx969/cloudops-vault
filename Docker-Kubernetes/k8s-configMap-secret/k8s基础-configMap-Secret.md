---
title: K8s基础-configMap-Secret
tags:
  - kubernetes
  - k8s-basics
aliases:
  - k8sconfigMapSecret
---

# K8s基础-configMap-Secret


## ConfigMap

我们在部署服务的时候，每个服务都有自己的配置文件，如果一台服务器上部署多个服务：nginx、tomcat、apache等，那么这些配置都存在这个节点上，假如一台服务器不能满足线上高并发的要求，需要对服务器扩容，扩容之后的服务器还是需要部署多个服务：nginx、tomcat、apache，新增加的服务器上还是要管理这些服务的配置，如果有一个服务出现问题，需要修改配置文件，每台物理节点上的配置都需要修改，这种方式肯定满足不了线上大批量的配置变更要求。

所以，k8s中引入了Configmap资源对象，可以挂载到pod中，实现统一的配置管理。

### 概念

Configmap是k8s中的资源对象，用于保存非机密性的配置的，数据可以用key/value键值对的形式保存，也可通过文件的形式保存。

官网地址：[Kubernetes ConfigMap文档](https://kubernetes.io/docs/concepts/configuration/configmap/)

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311151711600.png" alt="image-20231115171130386" style="zoom:67%;" />

#### 应用场景

有哪些配置需要管理：

1. 程序配置文件
2. 环境变量

优势：

1. 使用k8s部署应用，当你将应用配置写进代码中，更新配置时也需要打包镜像，不方便。
2. configmap可以将配置信息和镜像解耦，以便实现镜像的可移植性和可复用性。因为一个configMap其实就是一系列配置信息的集合，可直接注入到Pod中给容器使用。使用微服务架构的话，存在多个服务共用配置的情况，如果每个服务中单独一份配置的话，那么更新配置就很麻烦，使用configmap可以友好的进行配置共享。
3. configmap注入方式有两种，一种将configMap做为存储卷，一种是将configMap通过env中configMapKeyRef注入到容器中。

#### 局限性

- ConfigMap在设计上不是用来保存大量数据的。在ConfigMap中保存的数据不可超过1 MiB。
- 如果你需要保存超出此尺寸限制的数据，可以考虑挂载存储卷或者使用独立的数据库或者文件服务。

### 创建configMap

#### 命令行

```bash
#直接在命令行中指定configmap参数创建，通过--from-literal指定k-v
kubectl create configmap tomcat-config --from-literal=tomcat_port=8080 --from-literal=server_name=myapp.tomcat.com
```

#### 基于文件

```bash
#创建config文件
vim nginx.conf

server {
  server_name www.nginx.com;
  listen 80;
  root /home/nginx/www/
}

#创建一个带自定义key的cm
kubectl create cm cm-www-nginx --from-file=www=./nginx.conf
kubectl describe cm cm-www-nginx

Data
====
www:   #这是key
----   # ---后面是value
server {
  server_name www.nginx.com;
  listen 80;
  root /home/nginx/www/
}

#如果创建的时候不写key名字，默认的key就是文件名
kubectl create cm cm-www-nginx-2 --from-file=./nginx.conf

Data
====
nginx.conf:   #这是key
----   #这是value
server {
  server_name www.nginx.com;
  listen 80;
  root /home/nginx/www/
}
```

#### 基于目录

```bash
#创建目录和配置文件
mkdir cm-dir && cd ./cm-dir
echo "server-id=1" >> my-server.conf
echo "server-id=2" >> my-slave.conf

#创建cm，指定目录，会把目录里面的文件都做成cm
kubectl create configmap cm-mysql-config --from-file=./cm-dir/

Data
====
my-server.conf:
----
server-id=1

my-slave.conf:
----
server-id=2
```

#### 基于yaml文件

单个k-v创建

~~~yaml
apiVersion: v1 
kind: ConfigMap 
metadata: 
  name: basic-config 
data: 
  key1: value1 
  key2: value2 
~~~

多行k-v创建（只有最外层的文件名是key，下面的内容全是value）

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql
  labels:
    app: mysql
data:
  master.cnf: |  # 文件名称后面需要加上 | 以表示此yaml文件中的每一行就是挂载进去的文件的一行
    [mysqld]
    log-bin
    log_bin_trust_function_creators=1
    lower_case_table_names=1
  slave.cnf: |
    [mysqld]
    super-read-only
    log_bin_trust_function_creators=1
```

> [!info] 说明
> 在 Kubernetes 的 ConfigMap 中，`|` 和 `| -` 的主要区别在于它们处理多行字符串的方式。
>
> `|` 是一个块标识符，它会保留换行符和（除最后一行外的）尾随空格。例如：
>
> ```yaml
> data:
>  a.yml: |
>   key1: value1
>   key2: value2
> ```
>
> 这将创建一个字符串，其中包含”key1: value1\nkey2: value2\n”。
>
> `|-` 也是一个块标识符，但它会剥离掉尾随的换行符。例如：
>
> ```yaml
> data:
>  a.yml: |-
>   key1: value1
>   key2: value2
> ```
>
> 这将创建一个字符串，其中包含”key1: value1\nkey2: value2”，注意这里没有尾随的换行符。
>
> 总的来说，`|` 和 `|-` 都用于表示多行字符串，但 `|-` 会删除尾随的换行符。

#### 基于环境变量

有时候一个文件里面保存着标准k-v格式的环境变量，希望转换成cm之后，每个key都是环境变量的name，每个value都是环境变量的value；而不是文件名作为key，所有内容整体作为value。应该怎么做？

~~~sh
tee env-file <<'EOF'  
DB_HOST=localhost 
DB_PORT=3306 
DB_USER=root 
DB_PASS=password
EOF

# 创建cm
kubectl create cm env-cm --from-env-file=env-file
~~~

#### 基于literal创建

直接在命令行传入k-v创建cm。这种方式用得不多，因为环境变量一个一个打字太麻烦。

~~~sh
kubectl create configmap example-config --from-literal=key1=config1 --from
literal=key2=config2 
~~~

### 挂载cm

#### 以文件形式挂载-volume

~~~yaml
#创建cm
apiVersion: v1
kind: ConfigMap
metadata:
  name: cm-mysql
  labels:
    app: mysql
data:
  log: "1"
  lower: "1"
  my.cnf: |
    [mysqld]
    Welcome=helloworld

#创建pod
apiVersion: v1
kind: Pod
metadata:
  name: pod-cm-mysql
spec:
  containers:
  - name: mysql
    image: busybox
    command:
    - "/bin/sh"
    - "-c"
    - "sleep 36000"
    volumeMounts:
    - name: volume-cm-mysql
      mountPath: /tmp/config
  volumes:
  - name: volume-cm-mysql 
    configMap: # 直接把configMap做成卷了 
      name: cm-mysql
~~~

##### 自定义挂载文件名

默认的挂载进容器的文件名就是cm的key名。挂载的时候可以指定文件名：

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-cm-mysql
spec:
  containers:
  - name: mysql
    image: busybox
    command:
    - "/bin/sh"
    - "-c"
    - "sleep 36000"
    volumeMounts:
    - name: volume-cm-mysql
      mountPath: /tmp/config
  volumes:
  - name: volume-cm-mysql 
    configMap: 
      name: cm-mysql
      items: # 在这里指定cm的挂载文件名
      - key: my.cnf
        path: test.cnf
      optional: true # 即使items的key名写错了，也不影响pod启动
~~~

> [!warning] 注意
> 如果cm里面有多个key，并且指定了items，那么只有指定了items的key会被挂进去，没指定的就不挂载进去。所以如果需要挂载所有的key，就指定所有的items。

##### 自定义挂载权限

cm和secret挂载时，默认的挂载权限是644

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-cm-mysql
spec:
  containers:
  - name: mysql
    image: busybox
    command:
    - "/bin/sh"
    - "-c"
    - "sleep 36000"
    volumeMounts:
    - name: volume-cm-mysql
      mountPath: /tmp/config
  volumes:
  - name: volume-cm-mysql 
    configMap: 
      name: cm-mysql
      items: # 在这里指定cm的挂载文件名
      - key: my.cnf
        path: test.cnf
        mode: 0777 # 局部权限，只对单个item配置权限，八进制前面要加0。局部的优先级高于全部的
      optional: true # 即使items的key名写错了，也不影响pod启动
      defaultMode: 0644 # 默认权限，对所有items生效。八进制。
~~~

##### 文件挂载覆盖问题

cm和secret挂载的时候，会直接覆盖掉原目录的内容。所以挂载的时候要注意目录之前有没有文件。

比如要挂载nginx.conf的时候，如果直接挂载到/etc/nginx，就会导致nginx无法启动。

解决：mountPath指定具体的文件路径, subPath指定文件名

~~~yaml
    volumeMounts:
    - name: volume-nginx
      mountPath: /etc/nginx/nginx.conf
      subPath: nginx.conf
~~~

> [!warning] 注意
> 用subPath挂载进去的cm文件，不会热更新

#### 单一挂载环境变量-configMapKeyRef

~~~yaml
#写yaml文件创建cm
apiVersion: v1
kind: ConfigMap
metadata:
  name: cm-mysql
  labels:
    app: mysql
data:
  log: "1" #key是log，value是1
  lower: "1"

#创建pod
apiVersion: v1
kind: Pod
metadata:
  name: mysql-pod
spec:
  containers:
  - name: mysql
    image: busybox
    command: [ "/bin/sh", "-c", "sleep 3600" ]
    env:
    - name: log_bin   # 定义挂载进pod里面的环境变量的名称
      valueFrom: 
        configMapKeyRef:
          name: cm-mysql     #指定configmap的名字
          key: log # 指定configmap中的key
    - name: lower   #定义环境变量lower
      valueFrom:
        configMapKeyRef:
          name: cm-mysql
          key: lower #指定configmap中的key
~~~

> [!tip] 提示
> 这种方式一个一个导入env，不是很灵活。在大部分情况下环境变量很多，需要批量导入。

#### 批量挂载环境变量-envFrom

1. envFrom和env是平级字段，env优先级更高。
2. 这种方式，更改configMap之后，pod不会自动热更新。

~~~yaml
#创建pod
apiVersion: v1
kind: Pod
metadata:
  name: mysql-pod
spec:
  containers:
  - name: mysql
    image: busybox
    command: [ "/bin/sh", "-c", "sleep 3600" ]
    envFrom: # 这个configMap里面所有的k-v都被全部打包做成了环境变量。所以不能在这里直接改变环境变量名称。
    - configMapRef:
        name: myconfigmap
      prefix: DM_ # 这个字段可以给所有挂载进pod的env在key的基础上加一个前缀
  restartPolicy: Never 
~~~

#### 热更新

- 挂载成volume的cm，如果更改cm里面的k-v之后，过几分钟之后（默认5分钟），会自动热加载到pod的volumeMount里面。
- 如果是采用configMapKeyRef或者envFrom注入的cm，如果更改cm，已经挂载进去的env不会自动更新。一开始挂进去什么k-v就还是什么。需要热更新还是得手动删掉pod重建才行。

### 更新configMap

#### 命令行更新

可以通过kubectl edit修改，可以通过yaml文件kubectl apply -f修改，但是修改方式要统一，防止数据不一致。

#### 通过源文件更新

有时候就需要基于某个已存在的配置文件，更新配置文件之后，直接更新对应的configMap。这时候kubectl apply/replace都不行了。可以用dry-run参数基于源配置文件导出新的yaml，再replace

~~~sh
# 示例：修改原配置文件
cat nginx.conf  
user xxx; 
# 先转成yaml再进行replace 
kubectl create cm nginx-conf --from-file=nginx.conf=nginx.conf --dry-run=client -o yaml | kubectl replace -f -
~~~

基于literal的方式类似：

~~~sh
kubectl create configmap example-config --from-literal=key1=config1 --from-literal=key2=config2 --dry-run=client -oyaml | kubectl replace -f -
~~~

## Secret

### 概念

- Secret解决了密码、token、秘钥等敏感数据的配置问题，而不需要把这些敏感数据暴露到镜像或者Pod Spec中。Secret可以以Volume或者环境变量的方式使用。

- 要使用 secret，pod 需要引用 secret。Pod 可以用两种方式使用 secret：作为 volume 中的文件被挂载到 pod 中的一个或者多个容器里，或者当 kubelet 为 pod 拉取镜像时使用。

- kubectl create secret可选参数有三种:
  - generic: 通用类型，通常用于存储密码数据。
  - tls：此类型仅用于存储私钥和证书。
  - docker-registry：若要保存docker仓库的认证信息的话，就必须使用此种类型来创建。
  

- yaml文件中的Secret类型：（k explain secret.type）

  [Secrets | Kubernetes](https://kubernetes.io/docs/concepts/configuration/secret/#secret-types)

  - `Opaque`
    
    通用型，base64编码格式的Secret，用来存储密码、秘钥等。可以通过base64 --decode解码获得原始数据，因此安全性弱。
    
  - `kubernetes.io/dockerconfigjson`
    
    用来存储私有镜像仓库用户名密码的认证信息。和宿主机的/root/.docker/config.json一致，宿主机只要登录过私有镜像库就会产生该文件，记录私有镜像库用户名密码。
    
  - `kubernetes.io/tls`
  
    存储HTTPS域名证书，可以被ingress使用
  
  主要使用上面三种，下面的不太常用
  
  - bootstrap.kubernetes.io/token
  
  - kubernetes.io/basic-auth
  
  - kubernetes.io/service-account-token
  
    用于被 serviceaccount 引用。serviceaccout 创建时 Kubernetes 会默认创建对应的 secret。Pod 如果使用了 serviceaccount，对应的 secret 会自动挂载到 Pod 的 /run/secrets/kubernetes.io/serviceaccount 目录中。 

### 创建通用secret

#### 基于literal

~~~sh
#命令创建secret
kubectl create secret generic mysql-password --from-literal=password=123
# 可以创建多key secret
kubectl create secret generic basic-auth-secret \ 
--from-literal=username=admin \ 
--from-literal=password=<password>
~~~

#### 基于yaml文件

但是预先需要把字符串base64加密一下

~~~yaml
apiVersion: v1 
kind: Secret 
data: 
  ssh-key: ZGFyM2FkYWRhCg== 
metadata: 
  name: secret2 
  namespace: default 
type: Opaque
~~~

可以不预先base64加密，用stringData明文创建就行。这也是更推荐的方式。

~~~yaml
apiVersion: v1 
kind: Secret 
stringData: 
  ssh-key: password 
metadata: 
  name: string-data 
  namespace: default 
type: Opaque 
~~~

#### 基于文件和目录

与configMap相比多了一个generic的指定类型

~~~sh
kubectl create secret generic nginxconf --from-file=conf/nginx.conf
kubectl create secret generic createbydir --from-file=conf/
~~~

### 创建docker-registry类型secret

如果需要拉取私有仓库的镜像，需要给deploy等资源配置镜像仓库的密钥，此时可以先创建镜像仓库的密钥：

~~~sh
kubectl create secret docker-registry myregistrykey \ 
--docker-server=DOCKER_REGISTRY_SERVER \ 
--docker-username=DOCKER_USER \ 
--docker-password=DOCKER_PASSWORD \ 
--docker-email=DOCKER_EMAIL
~~~

- docker-registry：指定Secret的类型
- myregistrykey：Secret名称
- DOCKER_REGISTRY_SERVER：镜像仓库IP:端口号（harbor、阿里云等私有仓库都可以支持）
- DOCKER_USER：镜像仓库用户名，需要有拉取镜像的权限
- DOCKER_PASSWORD：镜像仓库密码
- DOCKER_EMAIL：邮箱信息，可以为空

之后就可以在pod字段添加imagePullSecret，secret里面已经包含了server、username、password。 

~~~yaml
spec: 
  imagePullSecrets: 
  - name: myregistrykey
  containers:
  ......
~~~

### 创建域名证书secret

Secret可以使用kubernetes.io/tls类型管理域名的证书，然后用于Ingress： 

~~~sh
# 生成测试证书 
openssl req -x509 -nodes -days 365 \ 
-newkey rsa:2048 -keyout tls.key -out tls.crt -subj "/CN=test.com" 
# 创建Secret 
kubectl -n default create secret tls nginx-test-tls --key=tls.key --cert=tls.crt 
~~~

tls.key和tls.crt如果是买的证书，在对应网站上可以下载这两个文件。

之后就可以用于ingress配置：

~~~yaml
 tls: 
   - secretName: nginx-test-tls 
~~~

### 挂载secret

与挂载configMap类似

#### 以文件形式挂载

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: nginx-test-cm 
  namespace: default 
  labels: 
    app: nginx-test-cm 
spec: 
  replicas: 1 
  selector: 
    matchLabels: 
      app: nginx-test-cm 
  template: 
    metadata: 
      labels: 
        app: nginx-test-cm 
    spec: 
      containers: 
        - name: nginx-test-cm 
          image: nginx:1.15.12 
          volumeMounts: 
            - name: nginxconfsecret 
              mountPath: /mnt 
      volumes: 
        - name: nginxconfsecret 
          secret: # 与configMap的不同点就在这里，指定是secret
            secretName: nginxconf # 挂载进去的secret文件会被解密
~~~

#### 环境变量挂载

~~~yaml
#pod注入secret
apiVersion: v1
kind: Pod
metadata:
  name: pod-secret
spec:
  containers:
  - name: myapp
    image: nginx
    envFrom: # 批量生成env
    - prefix: SECRET_ 
      secretRef: 
        name: basic-auth-secret # secret自己的name
    env: # 单个挂载env
    - name: USERNAME # 自己指定pod里面的env名字
      valueFrom: 
        secretKeyRef: 
          name: basic-auth-secret # secret自己的name
          key: username # secret里面的key名字
~~~

## 使用secret拉取私有仓库镜像

假设有个镜像在私有仓库中，未使用账号密码是无法拉取镜像的，此时可以在部署资源中，添加docker-registry类型的Secret。 

### 创建secret

~~~sh
kubectl create secret docker-registry myregistrykey \ 
--docker-server=harbor.hanxux.local \ 
--docker-username=admin \ 
--docker-password=Harbor12345 \ 
--docker-email=xxx@qq.com 
~~~

### 创建deployment

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: test 
  namespace: default 
spec: 
  replicas: 1 
  selector: 
    matchLabels: 
      app: test 
template: 
  metadata: 
    labels: 
      app: test 
  spec: 
    containers: 
    - name: test 
      image: harbor.hanxux.local/nginx:v1 
      imagePullSecrets: 
      - name: myregistrykey  
~~~

## cm和secret设置只读

ConfigMap和Secret可以使用immutable字段把资源设置为只读模式，这样就不能在更新data下的任何数据，如果想变更data，需要删除重建。

~~~yaml
apiVersion: v1 
immutable: true 
kind: ConfigMap 
metadata: 
  name: env-cm 
data: 
  DB_HOST: localhost 
  DB_PASS: password 
  DB_PORT: "3306" 
  DB_USER: root
~~~

## K8s 1.35 新特性：EnvFiles（fileKeyRef）

> 来源：[k8s 1.35 版本 Pod环境变量配置](https://mp.weixin.qq.com/s/Nv4qVlJDC_yNO8y8guoGkA)

### 背景

传统方式使用 ConfigMap/Secret 设置环境变量，需要**分别管理**工作负载 Pod 和配置资源，还要确保两者有序更新。对于供应商容器需要的一次性令牌、许可证密钥等临时配置，创建 ConfigMap 又显得过重。

K8s 1.35 引入了 **EnvFiles** 功能：允许 kubelet 直接从 `emptyDir` 卷中的文件加载环境变量，**主容器无需挂载该卷**。典型用法是 initContainer 生成配置文件 → kubelet 在主容器启动时读取并注入。

### 核心机制

使用新的 `fileKeyRef` 字段（与 `configMapKeyRef`、`secretKeyRef` 平级）：

```yaml
apiVersion: v1
kind: Pod
spec:
  initContainers:
  - name: generate-config
    image: busybox
    command: ['sh', '-c', 'echo "CONFIG_VAR=HELLO" > /config/config.env']
    volumeMounts:
    - name: config-volume
      mountPath: /config
  containers:
  - name: app-container
    image: gcr.io/distroless/static
    env:
    - name: CONFIG_VAR
      valueFrom:
        fileKeyRef:             # 新字段：从文件读取环境变量
          path: config.env      # 文件路径（相对于卷根目录）
          volumeName: config-volume  # 引用的卷名
          key: CONFIG_VAR       # 文件中要提取的 key
  volumes:
  - name: config-volume
    emptyDir: {}
```

**要点**：

- `fileKeyRef` 指向一个 emptyDir 卷中的文件，文件格式为标准 `KEY=VALUE`
- 主容器**不需要 volumeMounts**——kubelet 在启动时直接读取文件并注入环境变量
- 文件通常由 initContainer 动态生成，适合运行时才能确定的配置（如从 Vault 拉取密钥、根据节点信息生成配置等）
- 文件生命周期与 Pod 一致（emptyDir），Pod 销毁后自动清理

### 与传统方式对比

| 方式 | 适用场景 | 热更新 | 额外资源 |
|------|----------|--------|----------|
| 直接定义 `env.value` | 固定不变的值（应用名、版本号） | ✗ | 无 |
| `configMapKeyRef` / `envFrom` | 经常变动的配置 | ✗（需重建 Pod） | ConfigMap |
| `secretKeyRef` | 敏感信息（密码、密钥） | ✗（需重建 Pod） | Secret |
| `--from-env-file` → ConfigMap | 批量导入 .env 文件 | ✗（需重建 Pod） | ConfigMap |
| **`fileKeyRef`（1.35 新增）** | 运行时动态生成的配置 | ✗ | 无（emptyDir） |

### 典型应用场景

1. **initContainer 从 Vault/外部服务拉取密钥**，写入 emptyDir → 主容器通过 fileKeyRef 读取
2. **根据节点/集群信息动态生成配置**，避免为每个环境维护单独的 ConfigMap
3. **供应商容器**需要许可证密钥或一次性令牌，不想硬编码也不想创建额外资源

> [!tip] 建议
> K8s 1.35+ 新集群可优先使用 fileKeyRef 替代 ConfigMap 管理环境变量，减少配置资源的维护负担。对于仍在低版本集群的场景，继续使用 ConfigMap + envFrom 的方式。

## 最佳实践

### ConfigMap 和 Secret 操作规范

- 需提前创建ConfigMap和Secret，pod创建是依赖这俩的，必须先创建好
- ConfigMap和Secret必须要和Pod或者是引用它资源在同一个命名空间
- 如果引用了某个key，需要确保引用的Key必须存在
- envFrom、valueFrom 无法热更新环境变量，subPath也是无法热更新的
- envFrom配置环境变量，如果key是无效的，它会忽略掉无效的key
- ConfigMap和Secret最好不要太大（etcd有限制，不能超过1Mi，否则etcd同步数据速度会受到影响）
- ConfigMap和Secret支持热更新，但是程序未必支持！（比如nginx需要重启或者reload才会重新加载配置文件）

### 环境变量管理规范

- **分层管理**：通用配置用 ConfigMap，敏感信息用 Secret，固定不变的值直接在 Pod spec 中定义
- **命名规范**：环境变量名统一使用**大写 + 下划线**（如 `DB_HOST`），代码中一眼可辨识
- **设置默认值**：应用代码中必须给环境变量设置默认值，避免配置缺失导致启动失败
- **文档化**：项目根目录放置 `env.example` 文件，列出所有环境变量及说明，方便新人上手
