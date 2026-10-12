---
title: 部署轻量级 K8S 平台 - K3S
tags:
  - kubernetes
  - k3s
aliases:
  - k3s部署
---

# 部署轻量级 K8S 平台 - K3S


## 边缘计算

![image-20240514212240562](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202405142122675.png)

- 边缘计算也称为边缘处理，是一种将服务器放置在本地设备（数据源）附近的网络技术，解决数据传输的延迟问题。这样的处理方式是在传感器附近或者设备产生数据的位置进行的，因此称之为边缘。“边缘”特指计算资源在地理分布上更加靠近数据源，而远离云数据中心的资源节点。典型的边缘计算分为物联网（例如：智慧城市，智能家居，大型商店等）和非物联网（例如：游戏，CDN 等）场景。
- 应用场景：在无人驾驶中，如果将传感器数据上传到云计算中心将会增加实时处理难度，并且受到网络制约，因此无人驾驶主要依赖车内计算单元来识别交通信号和障碍物，并且规划路径

## K3S介绍

- k3s是经过CNCF认证的由Rancher公司开发维护的一个轻量级的 Kubernetes 发行版，内核机制还是和 k8s 一样，但是剔除了很多外部依赖以及 K8s 的 alpha、beta 特性，同时改变了部署方式和运行方式，目的是轻量化 K8s，简单来说，K3s 就是阉割版 K8s，消耗资源极少。它主要用于**边缘计算、物联网**等场景。K3s 具有以下特点：
  - 安装简单，占用资源少，只需要512M内存就可以运行起来；
  - apiserver、scheduler等组件全部简化，并以进程的形式运行在节点上。把**控制节点程序都打包到一个二进制文件**里面，每个程序只需要占用100M内存；
  - 使用基于sqlite3的轻量级存储后端作为默认存储机制。同时支持使用etcd3、MySQL 和PostgreSQL作为存储机制；
  - 默认使用 local-path-provisioner 提供本地存储卷；默认安装了Helm controller 和 Traefik Ingress controller；
  - 所有control-plane组件的操作都**封装在单个二进制文件和进程中**，使K3s具有自动化和管理包括证书分发在内的复杂集群操作的能力。
  - 减少外部依赖，操作系统只需要安装较新的内核（centos7.6就可以，不需要升级内核）以及支持cgroup即可，k3s安装包已经包含了containerd、Flannel、CoreDNS。非常方便地一键式安装，不需要额外安装Docker、Flannel等组件。

- 与此同时，Rancher 中国团队推出了一款针对 K3s 的效率提升工具：**AutoK3s**。只需要输入一行命令，即可快速创建 K3s 集群并添加指定数量的 master 节点和 worker 节点。
- k3s和k8s具体有多大的差别：在实际的应用部署中，几乎没有任何差异，至少到目前为止，大部分所遇到的场景，k8s能满足的，k3s也能满足。

## K3S架构

- 单master架构
  - 控制节点（在K3s里叫做server node)，数据存储使用 sqlite 并内置在了控制节点上。
  - 每个 agent 节点都注册到同一个 server 节点。K3s 用户可以通过调用server节点上的K3s API来操作资源。

![image-20240514220329156](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202405142203219.png)

- 多master架构
  - K3s Server 节点：两个或者更多的server节点将为 Kubernetes API 提供服务并运行其他 control-plane 服务
  - 外部数据库：外部数据存储（与单节点 k3s 设置中使用的嵌入式 SQLite 数据存储相反）

### 应用案例

![image-20240514221358017](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202405142213092.png)

- 传感器是个小型服务器作为工作节点，上面也跑着操作系统，装着k3s，配置不需要很高，跑一些环境检测的应用。 

## 部署K3S-基于k8s-1.20

### 环境规划

- Linux 的内核版本在3.10以上，每台服务器上至少要有1G的内存空间，硬盘中可用的存储空间必须大于500 MB。
- 虚机配置：
  - centos7.6，4Gib内存/6vCPU/100G硬盘，开启处理器-虚拟化引擎里面的虚拟化配置。（rockylinux也可以）

- 集群配置

| k3s集群角色 | IP             | 安装的组件 |
| ----------- | -------------- | ---------- |
| Server节点  | 192.168.40.200 | K3s server |
| Agent节点   | 192.168.40.138 | K3s agent  |

### 配置系统

- 与K8S的初始化步骤相同
- 配置yum源
- 关掉防火墙
- 关掉selinux
- 修改内核参数
- 关掉swap交换分区

### 安装containerd

~~~sh
#在server和agent上安装containerd
yum install containerd -y
systemctl start containerd --now
~~~

### 安装K3S

- rancher文档：[快速入门指南 | K3s](https://docs.k3s.io/zh/quick-start)

~~~sh
#server节点上
curl -sfL http://rancher-mirror.rancher.cn/k3s/k3s-install.sh | INSTALL_K3S_MIRROR=cn sh -
#如果国内网络以上命令不行的话，手动安装
#上传k3s1.20.6安装包到server节点和agent节点，上传k3s-install.sh
ctr images import k3s1.20.6.tar.gz
INSTALL_K3S_VERSION=v1.20.6+k3s1 && INSTALL_K3S_MIRROR=cn && sh k3s-install.sh
#验证安装
k3s kubectl get nodes
#kubectl get nodes也行
k3s kubectl get pods -n kube-system
#部署完成之后，上面所有kube-system的进程都由 k3s 这个 service 来创建管理：
systemctl status k3s
ss -antulp | grep 6443 #apiserver
ss -antulp | grep 10250 # kubelet
ss -antulp | grep 10251 #scheduler
ss -antulp | grep 10252 #controller manager
#这些控制平面组件都由同一个进程管理
~~~

### 扩容agent节点

- 提取join token

~~~sh
#添加worker节点。在这些节点上安装K3s之后，需要一个join token。Join token存在于master节点的文件系统上。复制并将它保存。
cat /var/lib/rancher/k3s/server/node-token
~~~

- 扩容agent节点

~~~sh
#在agent节点上执行如下，把work节点加入k3s:
curl -sfL http://rancher-mirror.rancher.cn/k3s/k3s-install.sh | INSTALL_K3S_MIRROR=cn K3S_URL=https://192.168.40.200:6443 K3S_TOKEN=<k3s-node-token>  sh -
~~~

- 查看agent节点

~~~sh
#server node上
k3s kubectl get nodes
#给工作节点打标签
kubectl label node rancher node-role.kubernetes.io/worker=worker
#agent节点由k3s-agent管理
systemctl status k3s-agent
~~~

### 卸载k3s集群

- [Uninstalling K3s | K3s](https://docs.k3s.io/zh/installation/uninstall)

~~~sh
#server节点
/usr/local/bin/k3s-uninstall.sh
#agent节点
/usr/local/bin/k3s-agent-uninstall.sh
~~~

## 部署k3s-基于k8s最新版

### 环境规划

| k3s集群角色 | IP             | 安装的组件 | 主机名  |
| ----------- | -------------- | ---------- | ------- |
| Server节点  | 192.168.40.160 | K3s server | kserver |
| Agent节点   | 192.168.40.161 | K3s agent  | kagent  |

### 配置系统

- 修改主机名
- 关掉并禁用firewalld防火墙
- 关掉selinux
- 配置hosts文件
- 配置ssh互信
- 用centos的话，换yum源

~~~sh
mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.backup
wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
~~~

- 配置k8s yum源

~~~sh
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
EOF

cat > /etc/yum.repos.d/kubernetes-1.30.repo <<EOF
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.30/rpm/
enabled=1
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.30/rpm/repodata/repomd.xml.key
EOF
~~~

- 配置containerd yum源

~~~sh
#添加安装containerd需要的yum源
yum-config-manager --add-repo  http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
yum clean all && yum makecache -y
~~~

- 修改内核参数

~~~sh
cat <<EOF > /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
modprobe br_netfilter
sysctl -p /etc/sysctl.d/k8s.conf
~~~

### 安装containerd

~~~sh
yum install  containerd.io-1.6.22 -y #比较稳定的containerd版本
cd /etc/containerd/
vim config.toml
#修改以下内容
#把SystemdCgroup = false修改成SystemdCgroup = true
#把sandbox_image = "k8s.gcr.io/pause:3.6"修改为sandbox_image="registry.aliyuncs.com/google_containers/pause:3.7"
systemctl enable containerd  --now
~~~

### 安装k3s server节点

~~~sh
#server节点上：
curl -sfL https://rancher-mirror.oss-cn-beijing.aliyuncs.com/k3s/k3s-install.sh | INSTALL_K3S_MIRROR=cn sh -
#安装命令会变化，参考官网命令：https://docs.k3s.io/zh/quick-start
#注：安装什么版本是k3s决定的，是在这个安装脚本里面预先定义好的
k3s kubectl get nodes
~~~

### 添加worker节点

~~~sh
#server节点上提取join token
#我们想要添加worker节点。在这些节点上安装K3s，我们需要一个join token。
#Join token存在于master节点的文件系统上。复制并保存：
cat /var/lib/rancher/k3s/server/node-token

#worker节点上 
curl -sfL https://rancher-mirror.oss-cn-beijing.aliyuncs.com/k3s/k3s-install.sh | INSTALL_K3S_MIRROR=cn K3S_URL=https://192.168.40.160:6443 K3S_TOKEN=<token> sh -
k3s kubectl get nodes
~~~

## k3s部署guestbook留言板

### 准备镜像

~~~sh
#master和node解压
ctr -n=k8s.io images import frontend.tar.gz
ctr -n=k8s.io images import redis-master.tar.gz
ctr -n=k8s.io images import redis-slave.tar.gz
~~~

### 部署redis-master

~~~yaml
tee redis-master-deployment.yaml <<'EOF' 
apiVersion: apps/v1 
kind: Deployment
metadata:
  name: redis-master
  labels:
    app: redis
spec:
  selector:
    matchLabels:
      app: redis
      role: master
      tier: backend
  replicas: 1
  template:
    metadata:
      labels:
        app: redis
        role: master
        tier: backend
    spec:
      containers:
      - name: master
        image: docker.io/kubeguide/redis-master:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: redis-master
  labels:
    app: redis
    role: master
    tier: backend
spec:
  ports:
  - port: 6379
    targetPort: 6379
  selector:
    app: redis
    role: master
    tier: backend
EOF
~~~

### 部署redis-slave

~~~yaml
tee redis-slave-deployment.yaml <<'EOF' 
apiVersion: apps/v1 
kind: Deployment
metadata:
  name: redis-slave
  labels:
    app: redis
spec:
  selector:
    matchLabels:
      app: redis
      role: slave
      tier: backend
  replicas: 1
  template:
    metadata:
      labels:
        app: redis
        role: slave
        tier: backend
    spec:
      containers:
      - name: slave
        image: docker.io/kubeguide/guestbook-redis-slave:latest
        imagePullPolicy: IfNotPresent
        env:
        - name: GET_HOSTS_FROM
          value: dns
        ports:
        - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: redis-slave
  labels:
    app: redis
    role: slave
    tier: backend
spec:
  ports:
  - port: 6379
  selector:
    app: redis
    role: slave
    tier: backend
EOF
~~~

### 部署frontend

~~~yaml
tee <<'EOF'
apiVersion: apps/v1 
kind: Deployment
metadata:
  name: frontend
  labels:
    app: guestbook
spec:
  selector:
    matchLabels:
      app: guestbook
      tier: frontend
  replicas: 1
  template:
    metadata:
      labels:
        app: guestbook
        tier: frontend
    spec:
      containers:
      - name: php-redis
        image: docker.io/kubeguide/guestbook-php-frontend:latest
        imagePullPolicy: IfNotPresent
        env:
        - name: GET_HOSTS_FROM
          value: dns
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  labels:
    app: guestbook
    tier: frontend
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30001
  selector:
    app: guestbook
    tier: frontend
EOF
#部署完成可以通过frontend的NodePort查看web-UI页面
~~~

## 部署高可用k3s集群

- 将k3s进行高可用部署。官方提供了两种部署方式，一种是连接外部数据库如：mysql，然后部署多个k3s server端再进行负载均衡，还有一种是官方提供的高可用方式，参考：[K3s 嵌入式 HA 安装](https://docs.rancher.cn/docs/k3s/installation/ha-embedded/_index/)
- k3s配置etcd高可用，参考文档：[K3s HA 嵌入式数据库](https://docs.k3s.io/zh/datastore/ha-embedded)

- 安装2 master 1 worker：

~~~sh
#master1
curl -sfL https://rancher-mirror.oss-cn-beijing.aliyuncs.com/k3s/k3s-install.sh  | K3S_TOKEN=<k3s-token> INSTALL_K3S_MIRROR=cn INSTALL_K3S_EXEC="server" sh -s - --disable=traefik
#master2
curl -sfL https://rancher-mirror.oss-cn-beijing.aliyuncs.com/k3s/k3s-install.sh | K3S_TOKEN=<k3s-token> K3S_URL=https://192.168.40.160:6443 INSTALL_K3S_MIRROR=cn INSTALL_K3S_EXEC="server"  sh -
#master1获取token
cat /var/lib/rancher/k3s/server/node-token
#worker1加入集群
curl -sfL https://rancher-mirror.oss-cn-beijing.aliyuncs.com/k3s/k3s-install.sh | INSTALL_K3S_MIRROR=cn K3S_URL=https://192.168.40.160:6443 K3S_TOKEN=<token>  sh -
~~~

