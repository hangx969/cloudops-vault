---
title: CKS 备考
tags:
  - kubernetes
  - cks
  - certification
  - security
aliases:
  - CKS备考
---

# CKS 备考


## 1 AppArmor

### AppArmor介绍

- k8s文档：[AppArmor - Kubernetes](https://kubernetes.io/docs/tutorials/security/apparmor/)
- AppArmor官网：[AppArmor - Ubuntu Wiki](https://wiki.ubuntu.com/AppArmor/)
- AppArmor（Application Armor）是一种在Linux环境中用于增强系统安全的软件。它通过使用Linux内核的安全模块（LSM）来限制程序的能力，防止系统受到恶意软件或者非授权操作的影响。AppArmor通过定义一套简单的配置文件来指定程序能够访问哪些文件和功能。这种机制被称为强制访问控制（MAC），它与传统的基于用户权限的访问控制（DAC）不同，可以更精细地控制应用程序的行为，提高系统的安全性。与SELinux相比，AppArmor的策略更加简洁易懂，易于配置和管理。
- AppArmor的策略通常定义在 /etc/apparmor.d/ 目录下，每个策略文件对应一个程序，通过规定哪些文件路径可以访问以及可执行哪些操作（如读取、写入、执行、打开网络端口等）来控制程序的行为。目前Apparmor已经整合到了Linux 2.6内核中，Ubuntu系统自带Apparmor。
- Apparmor两种工作模式：
  - Enforcement：配置文件中列出的限制条件会被执行，并对于违反条件的程序进行日志记录
  - Complain：只监控行为并记录到日志中，并不会实际阻止程序的执行。

- 配置文件位置：/etc/apparmor.d目录下
- 访问控制：
  - r(read) \ w(write) \ a(append) \ k(file locking mode) \ l(link mode)
  - 在配置文件中的写法：`/tmp r` 表示对/tmp下的文件可以读取。（没在配置文件中列出的文件，程序是不能访问的）

- 资源限制
  - `set rlimit as<=1M` (限制使用的虚拟内存)

- 网络限制
  - network `\[\[domain]\[type]\[protocol]]`
  - 允许对所有网络进行操作：`network,`
  - 允许在IPv4下使用TCP协议：`network inet tcp.`


### Task

- 在cluster的工作节点上，实施位于/etc/apparmor.d/nginx_apparmor的现有的apparmor配置文件。编辑位于/home/candidate/KSSH00401/nginx-deploy.yaml的现有清单文件以应用AppArmor配置文件。最后，应用清单文件并创建其中指定的Pod。

### Answer

- 文档:kubernetes.io 搜apparmor

~~~sh
kubectl config use-context KSSH00401
#先去工作节点，查看apparmor配置文件
sudo kubectl get nodes
ssh kssh00401-worker1
sudo -i
#查看apparmor配置文件是为了获取profile的名称
cat /etc/apparmor.d/nginx_apparmor 
#...
profile nginx-profile  flags=(attach_disconnected) {
#... profile后面的nginx-profile是这个配置的名称，
#后面apparmor_status | grep nginx-profile 要用到
#yaml文件的annotations也要用到

#安静模式（不输出信息）加载或更新名为 nginx_apparmor 的 AppArmor 配置文件
apparmor_parser -q /etc/apparmor.d/nginx_apparmor 
#查看apparmor配置文件是否生效(profile的名字是在nginx_apparmor文件里面定义的)
apparmor_status | grep nginx
#exit退出工作节点，回到login node署pod

kubectl config use-context KSSH00401
sudo vim /home/candidate/KSSH00401/nginx-deploy.yaml 
#新增deploy.spec.template.metadata.annotqations。
annotations:
  container.apparmor.security.beta.kubernetes.io/hello: localhost/nginx-profile
  ##hello是pod里container的名称，nginx-profile是apparmor_status解析出来的结果

sudo kubectl apply -f /home/candidate/KSSH00401/nginx-deploy.yaml
~~~

> [!warning] 注意
> - cat /etc/apparmor.d/nginx_apparmor配置文件中查看profile的名称
> - yaml文件中的deployments.spec.template.metadata.annotations中写annotation
> - annotation中的container name记得要改
> - annotations的格式是container name后面的: 跟一个空格

## 2 kube-bench基准测试

### kube-bench介绍

- kube-Bench是一款针对Kubernetes的安全检测工具

### Task

context：针对kubeadm创建的cluster运行CIS基准测试工具时，发现了多个必须解决的问题。


- task：通过配置修复所有问题并重新启动受影响的组件以确保新设置生效。

- 修复针对kubelet发现的所有以下违规行为

  - Ensure that the anonymous-auth argument is set to false  

  - Ensure that the -authorization-mode argument is not set to AlwaysAllow 
  - 尽可能使用Webhook 身份验证/授权

- 修复针对etcd发现的以下违规行为：

  - Ensure that the --client-cert-auth argument is set to true

### Answer

- 官网搜索：kubelet configuration

~~~sh
#切换到指定集群节点
kubectl config use-context KSSH00201
sudo kubectl get nodes
ssh kscs00201-master
sudo -i
~~~

- 修改master节点kubelet文件

~~~sh
#master节点上，编辑kubelet文件来配置以上参数
vim /var/lib/kubelet/config.yaml 
~~~

- 原始文件如下：

~~~yaml
#原始文件内容如下：
apiVersion: kubelet.config.k8s.io/v1beta1
authentication:
  anonymous:
    enabled: true
  webhook:
    cacheTTL: 0s
    enabled: false
  x509:
    clientCAFile: /etc/kubernetes/pki/ca.crt
authorization:
  mode: AlwaysAllow
  webhook:
    cacheAuthorizedTTL: 0s
    cacheUnauthorizedTTL: 0s
cgroupDriver: systemd
#.........
~~~

- 修改后内容如下：

~~~yaml
apiVersion: kubelet.config.k8s.io/v1beta1
authentication:
  anonymous: 
    enabled: false #改为false
  webhook:
    cacheTTL: 0s
    enabled: true #改为true
  x509:
    clientCAFile: /etc/kubernetes/pki/ca.crt
authorization:
  mode: Webhook #改为Webhook
#......
~~~

~~~sh
#修改完重启kubelet
systemctl restart kubelet
~~~

- 修改工作节点kubelet文件，修改内容同master节点。

~~~sh
ssh xianchaonode1
sudo -i
vim /var/lib/kubelet/config.yaml
#修改完重启kubelet
systemctl restart kubelet
#退出工作节点
exit
~~~

- 修改master节点etcd

~~~sh
ssh kscs00201-master
sudo -i
vim /etc/kubernetes/manifests/etcd.yaml
#containers.command下面新增以下参数
- --client-cert-auth=true
~~~

- 修改完重启kubelet

~~~sh
systemctl restart kubelet
#exit退回原始终端，切换集群
kubectl config use-context KSSH00201
kubectl get nodes
#这个过程比较慢，估计需要几分钟才可以启动
~~~

> [!warning] 注意
> - 这些字段可能默认没有，需要自己添加
>
> ~~~yaml
>   anonymous: 
>     enabled: false #改为false
>   webhook:
>     cacheTTL: 0s
>     enabled: true #改为true
> ~~~
>
> - 背过kubelet和etcd配置文件的路径：
>   - **kubelet：/var/lib/kubelet/config.yaml** 
>   - etcd: /etc/kubernetes/manifests/etcd.yaml

## 3 Trivy镜像扫描

### Task

- 使用Trivy开源容器扫描器检测namespace yavin中pod使用的具有严重漏洞的镜像。查找具有High或Critical漏洞的镜像，并删除使用这些镜像的pod。
- Trivy仅预装在cluster的master节点上

### Answer

~~~sh
#自己练习先创建pod
kubectl create ns yavin
kubectl apply -f trivy-1.yaml
kubectl apply -f trivy-2.yaml

#考试环境先切换集群
kubectl config use-context KSRS00101
#原始terminal上面查看pod的镜像
k get po -n yavin -o yaml | grep image:
#到master节点上扫描pod
ssh xianchaomaster1
trivy image --help #查看参数选项
#扫描刚才列出来的镜像
trivy image --skip-db-update -s HIGH,CRITICAL docker.io/library/nginx:1.25 >> scan.log
trivy image --skip-db-update -s HIGH,CRITICAL docker.io/library/redis:7.2 >> scan.log 
#过滤扫描结果,-B 2是把total:前面两行也显示出来
grep -iB 2 total: scan.log
#exit回到原始命令终端，切换到集群环境
kubectl config use-context KSRS00101
#列出pod，找到使用漏洞镜像的pod，删掉
k get po -n yavin
k describe po trivy-1 -n yavin
k delete po trivy-1 -n trivy --force --grace-period=0
~~~

> [!warning] 注意
> - 原始终端才能执行kubectl命令，exit退回到原始终端之后，需要重新执行kubectl use-context切换到集群环境。
> - trivy命令需要ssh登录到master节点才能执行

## 4 sysdig & falco

### 介绍

- Sysdig官网：[Sysdig](https://www.sysdig.org)
  - sysdig的定位是系统监控、分析和排障的工具

- Falco 是一个云原生运行时安全系统，可与容器和原始 Linux 主机一起使用。它由 Sysdig 开发，是 Cloud Native Computing Foundation（云原生计算基金会）的一个沙箱项目。
  - Falco 的工作方式是查看文件更改、网络活动、进程表和其他数据是否存在可疑行为，然后通过可插拔后端发送警报。
  - 通过内核模块或扩展的 BPF 探测器在主机的系统调用级别检查事件。
  - Falco 包含一组丰富的规则，您可以编辑这些规则以标记特定的异常行为，并为正常的计算机操作创建允许列表。


### Task

- 使用运行时检测工具检测在属于Pod redis的单个容器中频繁产生和执行异常的进程。 
- cluster的工作节点上已经安装了sysdig和falco
- 使用你选择的工具（包括任何未预装的工具），至少分析容器120s，使用过滤器检查新生成和执行的进程。在/opt/KSRS00101/events/details中存储一个事件文件，其中包含检测到的事件，每行一个，格式如下所示：
  - timestamp,uid or namespace, processName
  - 以下是格式的正确的事件文件：
    - 18:18:18.688688688,root,init
    - 18:18:19.688688688,nobody,init

### Answer

~~~sh
#自己环境中练习时，创建pod
k apply -f redis.yaml

#切换集群环境
kubectl config use-context KSRS00101
k get po
k get po redis-deployment-5b569f968-86h8n -o yaml | grep containerID
#复制containerID前12位即可
2d3affbe35b4

#去工作节点上用sysdig检查。
ssh xianchaonode1
sudo -i 
#用下面命令查看sysdig里面的变量叫啥
sysdig -l | grep time #找到 evt.time，作为输出字段
sysdig -l | grep uid #找到 user.uid，作为输出字段
sysdig -l | grep name #找到 proc.name，作为输出字段
sysdig -l | grep container #找到container.id作为filter条件
#containerd的路径可以先查找一下：
find / -name "containerd.sock" #/run/containerd/containerd.sock
#就用上面的变量名来组成输出格式
sysdig -M 120 -p "%evt.time,%user.uid,%proc.name" --cri unix:///run/containerd/containerd.sock container.id=2d3affbe35b4 > /opt/KSRS00101/events/details

#-p：指定打印事件时使用的格式
#-M: 多少秒后停止收集
# evt.time: 事件发生的时间
# user.uid: 用户uid
# proc.name: 生成事件的进程名字
# container.id: 根据容器id过滤

#如果details中没输出数据，可以尝试改成container name
#sysdig -M 120 -p "*%evt.time,%user.uid,%proc.name" --cri unix:///run/containerd/containerd.sock container.name=redis > /opt/KSRS00101/events/details
~~~

> [!warning] 注意
> 一定去工作节点上运行sysdig，因为pod跑在工作节点上，在控制节点上sysdig没有输出的。

## 5 service account

### Task

Context：

- ServiceAccount不得自动挂载API凭据，ServiceAccount名称必须以“-sa”结尾。
- 清单文件/home/candidate/KSCH00301/pod-manifest.yaml中指定的pod由于ServiceAccount指定错误而无法调度。

Task：

- 首先，在现有 namespace dev 中创建一个名为 database-sa 的新ServiceAccount，确保此ServiceAccount不得自动挂载API凭据。
- 其次，使用 /home/candidate/KSCH00301/pod-manifest.yaml 中的清单文件来创建pod。
- 最后，清理 namespace dev 中任何未使用的 ServiceAccount。

### Answer

- 文档：k8s官网搜configure service account

~~~yaml
#自己环境搭建资源
sudo kubectl create ns dev
#切换集群
kubectl config use-context KSCH00301
sudo -i
#通过dry-run生成yaml文件，--dry-run=client选项，仅生成结果，不发送给api server
kubectl create sa database-sa  -n dev --dry-run=client -o yaml > sa.yaml
vim sa.yaml
apiVersion: v1
kind: ServiceAccount
automountServiceAccountToken: false  #不自动挂载API凭据
metadata:
  creationTimestamp: null
  name: database-sa
  namespace: dev
  
kubectl apply -f sa.yaml
~~~

~~~yaml
#pod yaml文件新增两个字段
vim /home/candidate/KSCH00301/pod-manifest.yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: dev
  name: dev-pod
  namespace: dev
spec:
  automountServiceAccountToken: false 
  serviceAccountName: database-sa
  containers:
  - image: docker.io/xianchao/nginx:v1
    name: nginx
    imagePullPolicy: IfNotPresent

kubectl delete -f /home/candidate/KSCH00301/pod-manifest.yaml
kubectl apply -f /home/candidate/KSCH00301/pod-manifest.yaml
~~~

~~~sh
#先看有哪些sa
kubectl get sa -n dev
#再看有哪些pod
kubectl get po -n dev
#看pod都挂载了哪些sa。这样就找到了没被使用的sa，k delete sa -n dev删掉。
k get po -n dev -o yaml | grep serviceAccountName:
~~~

> [!warning] 注意
> - 创建sa的时候一定注意加上**metadata.namespace**，否则后面的pod创建不出来
> - default这个sa不用删除，会自动生成的。
> - 如果pod删除较慢，直接`kubectl delete po xxx --force --grace-period=0`强制删除

## 6 TLS通信加强

### Task

一个现有的Kubernetes集群，通过更新组件的TLS配置进行安全加固

- 修改API server和etcd之间通信的TLS配置，对于API server
  - 删除对除了TLS1.2及更高版本之外的所有TLS版本的支持
  - 删除对**TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256**之外左右密码套件的支持

- 对于etcd：
  - 删除对于除了TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256之外的所有密码套件的支持

### Answer

- 官网搜：kube-apiserver, ctrl+F搜--tls

~~~sh
#切换集群
kubectl config use-context KSMV00401
k get nodes
#ssh到master节点更改配置
ssh xianchaomaster1
sudo -i
#修改api server参数
vim /etc/kubernetes/manifests/kube-apiserver.yaml
  containers:
  - command:
    - kube-apiserver
    - --tls-min-version=VersionTLS12 #照文档添加这一项。TLS12代表TLS 1.2
    - --tls-cipher-suites=TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 #照文档添加这一项指定的TLS cipher
#重启kubelet
systemctl restart kubelet

#修改etcd配置
vim /etc/kubernetes/manifests/etcd.yaml
spec:
  containers:
  - command:
    - etcd
    - --cipher-suites=TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 #添加这一项
#重启kubelet
systemctl restart kubelet

#exit退出控制节点，到login node上检查
kubectl config use-context KSMV00401
k get nodes -n kube-system
~~~

> [!warning] 注意
> - etcd的参数文档上没有，记住是比apiserver上少了tls（- --cipher-suites）
> - apiserver和etcd的要求的cipher不一定相同，注意甄别。
> - 重启kubelet完之后，可能会花费几分钟才能显示出k get nodes的结果

## 7 NetworkPolicy拒绝所有的ingress+egress流量

### Task

一个默认拒绝（default-deny）的NetworkPolicy可避免在未定义任何其他NetworkPolicy的namespace中意外公开Pod。

- 在namespace development中创建一个名字为denynetwork的default-deny的NetworkPolicy
  - 此新的NetworkPolicy必须拒绝namespace development中的所有ingress+Egress流量。
  - 将新NetworkPolicy应用于在namespace development中运行的所有POD

- 您可以在/home/candidate/KSCS00101/network-policy.yaml中找到模板清单文件

### Answer

- 官网搜networkpolicies --> 搜deny --> 找到 Default deny all ingress and all egress traffic

~~~sh
#自己环境
k create ns development
mkdir -p /home/candidate/KSCS00101/
#切换集群
kubectl config use-context KSCS00101
vim /home/candidate/KSCS00101/network-policy.yaml
#将官网的模板复制进来，加个namespace即可
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: denynetwork
  namespace: development
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress

k apply -f network-policy.yaml
~~~

> [!warning] 注意
> - 看清题目要求的限制的类型，如果是仅限制ingress/egress，从官网复制对应的条目即可：
>   - Default deny all egress traffic
>   - Default deny all ingress traffic
> - “拒绝所有ns development”这个条件，在metadata.namespace这一条就满足了，不需要加namespaceSelector

## 8 NetworkPolicy限制pod之间访问

### Task

- 创建名为pod-access的NetworkPolicy来限制对在namespace development中运行的pod products-service的访问。

- 只允许以下Pod连接到pod products-service：

  1、在namespace qa中的pod
  2、位于任何namespace，带有environment: testing的pod

### Answer

- 官网搜network policies --> The NetworkPolicy resource下面复制模板

~~~sh
#自己环境搭建
sudo kubectl create ns development 
sudo kubectl create ns qa
sudo kubectl apply -f network-1.yaml
sudo kubectl apply -f qa-pod.yaml
sudo kubectl apply -f products-service.yaml

#切换集群
kubectl config use-context KSSH00301
#查看ns qa、product-service的标签
k get ns qa --show-labels #kubernetes.io/metadata.name=qa
k get po product-service -n development --show-labels #app=product
#根据模板创建network policies
~~~

~~~yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: pod-access
  namespace: development
spec:
  podSelector:
    matchLabels:
      app: product
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: qa
  - from: #分开写两个from，逻辑更清楚
    - namespaceSelector: {} #这里注意：题目说了任何namespace下，这里必须加上。
      podSelector: 
        matchLabels:
          environment: testing
~~~

> [!warning] 注意
> - network policies要限制哪个namespace里面的pod被访问，就将其创建到哪个namespace
>
> - labels要改成xxx: xx这种格式
>
> - 如果ns或者po有多个标签，就可以把标签都写上
>
>   ```yaml
>   matchLabels:
>     app: product
>     xxx: xx
>   ```
>
> - “**位于任何namespace，带有environment: testing的pod**”：意味着要写上namespaceSelector: {}
>
> - 写两个from包含两个逻辑，更清楚
>
> - network policy的yaml规则：
>
>   ~~~yaml
>     ingress:
>     - from: 
>       - namespaceSelector: {}
>       - podSelector: #两个杠分开的两个条件是相互独立的or
>           matchLabels:
>             environment: testing
>      - from: 
>        - namespaceSelector: {}
>          podSelector: #同一个杠下面的两行是串联的and
>            matchLabels:
>              environment: testing
>   ~~~
>
>   

## 9 RBAC

### Task

绑定到Pod的serviceAccount的Role授予过度的权限。完成以下任务以降低权限。

- 一个名为web-pod的现有Pod已在namespace db中运行。
- 编辑绑定到Pod的ServiceAccount：test-sa-3的现有Role：
  - 仅允许只对services类型的资源执行get操作。

- 在namespace db中创建一个role：
  - 名为test-role-2
  - 并仅允许只对namespaces类型的资源执行patch操作。

- 创建一个名为test-role-2-binding新RoleBinding，将新创建的 Role绑定到Pod的ServiceAccount
- 不要删除现有RoleBinding。

### Answer

- k8s官网搜RBAC（查看create role和rolebinding的命令）

~~~sh
#自己环境搭建
kubectl create ns db
kubectl create sa test-sa-3 -n db
kubectl apply -f test-sa-3-role.yaml
kubectl create rolebinding test-sa-rolebinding  --role=test-sa-3-role --serviceaccount=db:test-sa-3 --namespace=db
kubectl apply -f web-pod.yaml

#检查一下题目说的pod是否真的挂载了sa
k describe po web-pod -n db
#查看db名称空间之下的所有rolebinding
k get rolebinding -n db
#挨个查看rolebinding，看哪个rolebinding是绑定了题目给的sa:test-sa-3
k get rolebinding -n db test-sa-rolebinding -o yaml
#编辑role的权限
k edit role test-sa-3-role -n db
#resource改成services，verb改成get(如果考试环境没给resources何verbs字段，官网搜roles即可)
  resources:
  - services
  verbs:
  - get

#新创建一个role
kubectl create role test-role-2  -n db --resource=namespaces --verb=patch
#创建rolebinding绑定到service account
k create rolebinding -n db --role=test-role-2 --serviceaccount=db:test-sa-3
~~~

> [!warning] 注意
> 答完题看一下pod的yaml字段是不是有serviceAccountName字段，没有的话要加上。

## 10 kube-apiserver审计日志记录采集

### Task

- 在cluster 中启用审计日志。为此，请启用日志后端，并确保：

  1.日志存储在/var/log/kubernetes/logs.txt中
  2.日志文件能保留5天
  3.最多保留1个旧的审计日志文件

- /etc/kubernetes/logpolicy/sample-policy.yaml提供了基本策略。基本策略位于cluster的master节点上。它仅指定不记录的内容。

- 编辑和扩展基本策略来记录：

  1. RequestResponse级别的namespaces的更改
  2. namespace webapps中 pods 更改的request
  3. Metadata级别的所有namespace中的ConfigMap和Secret的更改

- 
  另外，添加一个全方位的规则以在Metadata级别记录的所有其他请求。不要忘记应用修改后的策略。


### Answer

- 官网搜auditing

~~~sh
#切换集群，ssh到master节点
kubectl config use-context KSRS00602
ssh ksrs00602-master
sudo -i
#编辑auditing policy的yaml文件
vim /etc/kubernetes/logpolicy/sample-policy.yaml
##原始文件不动，按照题目要求，在rules下面的-level字段新增配置即可。可以从官网复制。
#RequestResponse级别的namespaces的更改
  - level: RequestResponse
    resources:
    - group: ""
      # Resource "pods" doesn't match requests to any subresource of pods,
      # which is consistent with the RBAC policy.
      resources: ["namespaces"]
      
#namespace webapps中 pods 更改的request
  - level: Request
    resources:
    - group: "" # core API group
      resources: ["pods"]
    # This rule only applies to resources in the "kube-system" namespace.
    # The empty string "" can be used to select non-namespaced resources.
    namespaces: ["webapp"]
    
#Metadata级别的所有namespace中的ConfigMap和Secret的更改
  # Log configmap and secret changes in all other namespaces at the Metadata level.
  - level: Metadata
    resources:
    - group: "" # core API group
      resources: ["secrets", "configmaps"]
#添加一个全方位的规则以在Metadata级别记录的所有其他请求
  - level: Metadata
~~~

~~~yaml
#修改apiserver - 文档搜kube-apiserver
vim /etc/kubernetes/manifests/kube-apiserver.yaml
#添加参数：
- --audit-policy-file=/etc/kubernetes/logpolicy/sample-policy.yaml #审计策略文件
- --audit-log-path=/var/log/kubernetes/logs.txt  #审计日志文件
- --audit-log-maxage=5   #日志最大保留天数
- --audit-log-maxbackup=1  #审计日志文件最大保留数据

#apiserver的pod上写volume和volumeMounts挂载策略文件和日志文件 - 文档中logs backend字段有参数说明sa
    volumeMounts:
    - name: kubernetes-logs
      mountPath: /var/log/kubernetes/
    - name: kubernetes-policy 
      mountPath: /etc/kubernetes/logpolicy/sample-policy.yaml

volumes:
  - name: kubernetes-policy
    hostPath:  
      type: File
      path: /etc/kubernetes/logpolicy/sample-policy.yaml
  - name: kubernetes-logs
    hostPath:
      type: DirectoryOrCreate
      path: /var/log/kubernetes/

#重启kubelet
systemctl daemon-reload
systemctl restart kubelet
#exit回到login node查看集群状态
~~~

> [!warning] 注意
> - 记得查看kube-apiserver是否配置了volumeMount和volume。log是挂目录，policy是直接挂文件。
>
> - 应用这个audit policy就是systemctl daemon-reload，systemctl restart kubelet
>
> - 也可能抽到这个题：
>   - RequestResponse级别的nodes更改
>   - namespace front-apps中pods更改的request
>   - metadata级别的所有namespace中的ConfigMap和Secret的更改
>
> ~~~yaml
> ##编辑auditing policy的yaml文件
> vim /etc/kubernetes/logpolicy/sample-policy.yaml
> ##原始文件不动，按照题目要求，在rules下面的-level字段新增配置即可。可以从官网复制。
> #RequestResponse级别的nodes的更改
>   - level: RequestResponse
>     resources:
>     - group: ""
>       # Resource "pods" doesn't match requests to any subresource of pods,
>       # which is consistent with the RBAC policy.
>       resources: ["nodes"]
> #namespace front-apps中pods更改的request
>   - level: Request
>     resources:
>     - group: "" # core API group
>       resources: ["pods"]
>     # This rule only applies to resources in the "kube-system" namespace.
>     # The empty string "" can be used to select non-namespaced resources.
>     namespaces: ["front-apps"]
> #metadata级别的所有namespace中的ConfigMap和Secret的更改
>   # Log configmap and secret changes in all other namespaces at the Metadata level.
>   - level: Metadata
>     resources:
>     - group: "" # core API group
>       resources: ["secrets", "configmaps"]
> ~~~

## 11 创建secret

### Task

- 在namespace db中获取名为db1-test的现有secret的内容。
  - 将username字段存储在名为/home/candidate/old-username.txt的文件中，
  - 并将password字段存储在名为/home/candidate/pass.txt文件中
  - 你必须创建这两个文件；它们还不存在。

- 不要在以下步骤中使用/修改先前创建的文件，如果需要，创建新的临时文件。
  - 在db namespace中创建一个名为test-workflow 的新secret，内容如下；
    username: thanos
    password: `<password>`

- 最后，新建一个pod，可以通过卷访问secret test-workflow：
  - pod名： dev-pod
  - namespace: db
  - 容器名：dev-container
  - 镜像：redis:7.2
  - 卷名：dev-volume
  - 挂载路径：/etc/secret

### Answer

- 官网搜secret

~~~sh
#自己环境
kubectl create ns db
kubectl apply -f secret.yaml
#切换集群环境
kubectl config use-context KSMV00201
#创建两个文件
touch /home/candidate/old-username.txt
touch /home/candidate/pass.txt
#获取secret。命令可以在secret文档中，搜json获取
#直接显示出来，手动copy进去也行：kubectl get secret db1-test -n db -o jsonpath='{.data.*}' | base64 -d
kubectl get secret db1-test -n db -o jsonpath='{.data.username}' | base64 -d > /home/candidate/old-username.txt
kubectl get secret db1-test -n db -o jsonpath='{.data.password}' | base64 -d > /home/candidate/pass.txtpass.txt

#创建新secret -- 文档搜secret kubectl --> 搜literal
kubectl create secret generic test-workflow -n db --from-literal=username=thanos --from-literal=password=<password>
~~~

~~~yaml
#创建pod -- 官网在secret页面
vim secret-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: dev-pod
  namespace: db
spec:
  containers:
  - name: dev-container
    image: redis:7.2
    imagePullPolicy: IfNotPresent
    volumeMounts:
    - name: dev-volume
      mountPath: "/etc/secret"
  volumes:
  - name: dev-volume
    secret:
      secretName: test-workflow

k apply -f secret-pod.yaml
~~~

> [!tip] 注意
> 参考官网的secret、Managing Secrets using kubectl两个页面

## 12 dockefile和deployment优化

### Task

- 分析指定的Dockerfile（基于Ubuntu:16.04），修复其中有安全问题的两个命令。
- 分析指定的deployment，修复其中有安全问题的两个字段。
- 如果需要非特权用户执行某些指令，可以采用uid为65535的user nobody

### Answer

- 官网搜security context

~~~sh
#切换集群环境
kubectl config use-context KSSC00301
#修改dockerfile
vim /home/candidate/KSSC00301/Dockerfile
#原内容如下:
FROM ubuntu
USER root
USER root
#修改之后的内容如下： （只改FROM和USER，有几个root都改成nobody）
FROM ubuntu:16.04  
USER nobody
USER nobody
~~~

 ~~~yaml
 #修改deployment
 #内容如下：
 vim /home/candidate/KSSC00301/deployment.yaml
 apiVersion: apps/v1
 kind: Deployment
 metadata:
  name: test
  labels:
    app: dev
    name: dev
 spec:
  replicas: 1
  selector:
    matchLabels:
      app: dev
  template:
    metadata:
      labels:
        app: dev
    spec:
      containers:
      - image: nginx:1.25
        imagePullPolicy: IfNotPresent
        name: nginx
        securityContext: {'capabilities':{'add':['NET_ADMIN'],'drop':['all']},'privileged':True,'readOnlyRootFilesystem':False,'runAsUser':2000}
        
 #修改securityContext内容：
 #'privileged':False
 #'readOnlyRootFilesystem':True
 #'runAsUser':65535
 {'capabilities':{'add':['NET_ADMIN'],'drop':['all']},'privileged':False,'readOnlyRootFilesystem':True,'runAsUser':65535}
 
 k apply -f /home/candidate/KSSC00301/deployment.yaml
 ~~~

> [!warning] 注意
> deployment资源中的spec.selector和template.metadata中的label是否对应了，题目中会出现不对应的情况。

## 13 镜像安全ImagePolicyWebhook

### Task

您必须在cluster的master节点上完成整个考题，所有服务和文件都已被准备好并放置在该节点上。

cluster上设置了容器镜像扫描器，但尚未完全集成到cluster的配置中。完成后，容器镜像扫描器应扫描并拒绝易受攻击的镜像的使用。

- 给定一个目录/etc/kubernetes/controlconf中不完整的配置以及具有HTTPS 端点的https://wakanda:8080/image_policy的功能性容器镜像扫描器：
  - 启用必要的插件来创建镜像策略
  - 校验控制配置并将其更改为隐式拒绝（implicit deny）(在隐式拒绝模式下，除非明确允许，否则所有请求都会被拒绝)
  - 编辑配置以正确指向提供的HTTPS端点。

- 最后，通过尝试部署易受攻击的资源/root/KSSC00202/vulnerable-resource.yml来测试配置是否有效。
- 可以在/var/log/limagepolicy/roadrunner.log找到容器镜像扫描的日志文件

### Answer

- 官网搜:
  - ImagePolicyWebhook （在admission controllers里面）
  - kube-api-server -- 搜admission

~~~sh
#自己环境搭建
mkdir -p /etc/kubernetes/controlconf
touch /etc/kubernetes/controlconf/admission_configuration.json
touch /etc/kubernetes/controlconf/kubeconfig.yaml
#切换集群环境，到master节点上做题
kubectl config use-context KSSC00202
ssh xianchaomaster1
sudo -i

#修改admission controller的配置文件/etc/kubernetes/controlconf/admission_configuration.json
cd /etc/kubernetes/controlconf
vim admission_configuration.json
apiversion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
  - name: ImagePolicyWebhook
    configuration:
      imagePolicy:
        kubeConfigFile: /etc/kubernetes/controlconf/kubeconfig.yaml
        allowTTL: 50
        denyTTL: 50
        retryBackoff: 500
        defaultAllow: false #将true改为false（没有这个字段的话自己加上，官网搜admission，有这个字段的示例）

#修改ImagePolicyWebhook的配置文件/etc/kubernetes/controlconf/kubeconfig.yaml
vim kubeconfig.yaml
clusters:
  - name: name-of-remote-imagepolicy-service
    cluster:
      certificate-authority: /path/to/ca.pem    
      server: https://wakanda:8080/image_policy # 把这里改成题目给的地址

users:
  - name: name-of-api-server
    user:
      client-certificate: /path/to/cert.pem 
      client-key: /path/to/key.pem     
    
#修改apiserver配置
vim /etc/kubernetes/manifests/kube-apiserver.yaml
#添加两项配置，开启admission plugin和admission controller配置文件的位置
- --enable-admission-plugins=NodeRestriction,ImagePolicyWebhook #NodeRestriction是自带的，在后面加上ImagePolicyWebhook即可
- --admission-control-config-file="/etc/kubernetes/controlconf/admission_configuration.json"

#apiserver需要检查是否挂载了配置文件的目录，没有的话，自己写volume和volumeMount挂载进去
...
  volumeMounts:
  - mountPath: /etc/kubernetes/controlconf
    name: config
...
volumes:
- hostPath:
    path: /etc/kubernetes/controlconf
    type: DirectoryOrCreate
  name: config
  
#重启kubelet
systemctl restart kubelet
~~~

~~~sh
#exit回到login node部署示例的pod
kubectl apply -f /root/KSSC00202/vulnerable-resource.yml
~~~

> [!tip] 要点总结
> - admission_configuration里面修改defaultAllow false
> - kubeconfig里面修改扫描器endpoint
> - kube-apiserver.yaml里面：
>   - 添加enable-admission-plugins ImagePolicyWebhook
>   - 添加配置文件路径--admission-control-config-file（写的是json文件）
>   - 添加volume和volumeMounts把存放配置文件的路径挂进去

## 14 修改deploy的security context

### Task

修改运行在namespace app，名为lamp-deployment的现有 Deployment，使其容器：

1. 使用用户ID 10000运行
2. 使用一个只读的根文件系统
3. 禁止特权提升

### Answer

- 官网搜securitycontext

~~~sh
#自己环境搭建
kubectl create ns app
kubectl apply -f  /home/candidate/finer-sunbeam/lamp-deployment.yaml
#切换集群环境
kubectl config use-context KSRS00502
#获取deployment的yaml文件
kubectl get deploy lamp-deployment -n app -o yaml > la.yaml
~~~

~~~yaml
vim la.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lamp-deployment
  namespace: app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: lamp-deployment
  template:
    metadata:
      labels:
         app: lamp-deployment
    spec:
      containers:
      - name: nginx
        image: docker.io/xianchao/nginx:v1
        imagePullPolicy: IfNotPresent
        securityContext:
          runAsUser: 10000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true

k apply -f la.yaml
~~~

> [!warning] 注意
> - securityContext在两个位置都有：
>
>   - po.spec.securityContext
>   - po.spec.containers.securityContext
>
>   这个题就在container字段下面写就行，有几个container就写几个。

## 15 gVisor

### Task

- 该cluster 使用containerd 作为CRI运行时。containerd的默认运行时处理程序是runc。containerd 已准备好支持额外的运行时处理程序runsc（gVisor）
- 使用名为runsc的现有运行时处理程序，创建一个名为untrusted 的 RuntimeClass。更新 namespace client 中的所有 Pod 以在 gVisor（runsc） 上运行。
- 你可以在/home/candidate/KSMV00301/runtime-class.yaml找到一个模板清单文件。

### Answer

- 官网搜：runtime class

~~~sh
#切换集群环境
kubectl config use-context KSMV00301
#创建runtime class
vim /home/candidate/KSMV00301/runtime-class.yaml
# RuntimeClass is defined in the node.k8s.io API group
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  # The name the RuntimeClass will be referenced by.
  # RuntimeClass is a non-namespaced resource.
  name: untrusted 
# The name of the corresponding CRI configuration
handler: runsc
~~~

~~~sh
#获取client ns中的deployment
k get deploy -n client
k get po -n client
#导出deploy的yaml
kubectl get deploy run-client -n client -o yaml > run-deploy.yaml

vim run-deploy.yaml
#在deploy.spec.template.spec.runtimeClassName配置（和containers字段同级）
runtimeClassName: untrusted

#重新部署
k delete -f run-deploy.yaml
k apply -f run-deploy.yaml
~~~

## 16 k8s 准入控制

### Task

Context：集群处于测试目的，已经配置为未经身份验证和未经授权的访问，授予匿名用户cluster-admin的权限。现在要加固安全配置。

- 重新配置cluster的k8s API服务器，以确保只允许经过身份验证和授权的REST请求。
- 使用授权模式Node,RBAC和准入控制器NodeRestriction。
- 删除用户system:anonymous的ClusterRoleBinding来进行清理。注意：所有kubectl配置环境也被配置使用未经身份验证和未经授权的访问。不必更改，但注意一旦完成cluster的安全加固，kubectl的配置将无法工作。
- 可以使用位于cluster的master节点上，cluster原本的kubectl配置文件/etc/kubernetes/admin.conf，以确保经过身份验证的授权的请求仍然被允许。

### Answer

~~~sh
#切换集群
kubectl config use-context KSCH00101
ssh ksch00101-master
#修改apiserver参数
vim /etc/kubernetes/manifests/kube-apiserver.yaml
#原始内容如下：
- --authorization-mode=AlwaysAllow
- --enable-admission-plugins=AlwaysAdmit

#修改成:
- --authorization-mode=Node,RBAC #注意，只保留Node,RBAC这两个，中间是英文状态下的逗号。在最新考试中，这一行默认可能已经有了，但也需要检查确认。
- --enable-admission-plugins=NodeRestriction

systemctl restart kubelet
#exit回到login node，查询clusterrolebinding并删除
kubectl config use-context KSCH00101
k get clusterrolebinding system:anonymous
k delete clusterrolebinding system:anynomous
~~~

> [!warning] 注意
> - apiserver配置修改完之后，login node就用不了kubectl了。按照题目提示，可以在master上：
>
>   `kubectl get nodes --kubeconfig=/etc/kubernetes/admin.conf`继续操作kubectl
