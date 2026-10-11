---
title: K8s Ceph部署与集成
tags:
  - kubernetes
  - storage/ceph
aliases:
  - K8s Ceph部署
---

# K8s Ceph部署与集成


> [!warning] 生产环境注意
> 生产环境中如果要用ceph，一定要非常专业精通、可以troubleshooting才能去用；而且建议二进制安装在服务器上，不要装在k8s中。否则出问题之后因为ceph是分块存储，数据非常难以还原，有极大的丢失风险。

## ceph简介

### 类型

- ceph是一种开源的分布式的存储系统，包含以下几种存储类型：

  - 块存储（rbd）
    - 块设备可理解成一块硬盘，用户可以直接使用不含文件系统的块设备，也可以将其格式化成特定的文件系统，由文件系统来组织管理存储空间，从而为用户提供丰富而友好的数据操作支持。
    - linux系统中，ls /dev/下有很多块设备文件，这些文件就是我们添加硬盘时识别出来的；
    - *rbd*就是由Ceph集群提供出来的块设备。可以这样理解，sda是通过数据线连接到了真实的硬盘，而rbd是通过网络连接到了Ceph集群中的一块存储区域，往rbd设备文件写入数据，最终会被存储到Ceph集群的这块区域中；
  - 文件系统（cephfs）
    - 用户可以在块设备上创建xfs、ext4等文件系统，Ceph集群实现了自己的文件系统来组织管理集群的存储空间，用户可以直接将Ceph集群的文件系统挂载到用户机上使用。
    - Ceph有了块设备接口，在块设备上完全可以构建一个文件系统，那么Ceph为什么还需要文件系统接口呢？
      - 主要是因为应用场景的不同，Ceph的块设备具有优异的读写性能，但不能多处挂载同时读写（ReadWriteOnce），目前主要用在OpenStack上作为虚拟磁盘，而Ceph的文件系统接口读写性能较块设备接口差，但具有优异的共享性（ReadWriteMany）。

  - 对象存储(RADOS Fateway)
    - Ceph对象存储使用Ceph对象网关守护进程（radosgw），它是一个用于与Ceph存储集群交互的HTTP服务器。由于它提供与OpenStack Swift和Amazon S3兼容的接口，因此Ceph对象网关具有自己的用户管理。 Ceph对象网关可以将数据存储在用于存储来自Ceph文件系统客户端或Ceph块设备客户端的数据的相同Ceph存储集群中。
    - 使用方式就是通过http协议上传下载删除对象（文件即对象）。
    - 有了块设备接口存储和文件系统接口存储，为什么还整个对象存储呢
      - Ceph的块设备存储具有优异的存储性能但不具有共享性，而Ceph的文件系统具有共享性然而性能较块设备存储差，为什么不权衡一下存储性能和共享性，整个具有共享性而存储性能好于文件系统存储的存储呢，对象存储就这样出现了。

> 分布式存储的优点：
>
> - **高可靠：**既满足存储读取不丢失，还要保证数据长期存储。在保证部分硬件损坏后依然可以保证数据安全。
> - **高性能：**读写速度快。
> - **可扩展：**分布式存储的优势就是“分布式”，所谓的“分布式”就是能够将多个物理节点整合在一起形成共享的存储池，节点可以线性扩充，这样可以源源不断的通过扩充节点提升性能和扩大容量，这是传统存储阵列无法做到的。

### 核心组件

在ceph集群中，不管你是想要提供对象存储，块设备存储，还是文件系统存储，所有Ceph存储集群部署都是从设置每个Ceph节点，网络和Ceph存储开始的。 Ceph存储集群至少需要一个Ceph Monitor，Ceph Manager和Ceph OSD（对象存储守护进程）。运行Ceph Filesystem客户端时也需要Ceph元数据服务器。

- Monitors：
  - Ceph监视器（ceph-mon）维护集群状态的映射，包括监视器映射，管理器映射，OSD映射和CRUSH映射。这些映射是Ceph守护进程相互协调所需的关键集群状态。监视器还负责管理守护进程和客户端之间的身份验证。冗余和高可用性通常至少需要三个监视器。

- Managers：
  - Ceph Manager守护程序（ceph-mgr）负责跟踪运行时指标和Ceph集群的当前状态，包括存储利用率，当前性能指标和系统负载。 Ceph Manager守护进程还托管基于python的模块来管理和公开Ceph集群信息，包括基于Web的Ceph Dashboard和REST API。高可用性通常至少需要两名Managers。

- Ceph OSD：
  - Ceph OSD（对象存储守护进程，ceph-osd）存储数据，处理数据复制，恢复，重新平衡，并通过检查其他Ceph OSD守护进程来获取心跳，为Ceph监视器和管理器提供一些监视信息。冗余和高可用性通常至少需要3个Ceph OSD。

- MDS：
  - Ceph元数据服务器（MDS，ceph-mds）代表Ceph文件系统存储元数据（即，Ceph块设备和Ceph对象存储不使用MDS）。 Ceph元数据服务器允许POSIX文件系统用户执行基本命令（如ls，find等），而不会给Ceph存储集群带来巨大负担。

## 搭建ceph集群准备工作

### 配置3台主机静态IP

- master1-admin是管理节点 ：192.168.40.7
- node1-monitor是监控节点：192.168.40.8
- node2-osd是对象存储节点：192.168.40.9

~~~ini
#修改/etc/sysconfig/network-scripts/ifcfg-ens33文件，变成如下：
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static
IPADDR=192.168.40.200
NETMASK=255.255.255.0
GATEWAY=192.168.40.2
DNS1=192.168.40.2
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_FAILURE_FATAL=no
IPV6_ADDR_GEN_MODE=stable-privacy
NAME=ens33
DEVICE=ens33
ONBOOT=yes

#修改配置文件之后需要重启网络服务才能使配置生效，重启网络服务命令如下：
service network restart
~~~

### 配置主机名

~~~sh
hostnamectl set-hostname master1-admin && bash
hostnamectl set-hostname node1-monitor && bash
hostnamectl set-hostname node2-osd && bash
~~~

### 配置hosts文件

~~~sh
#3台机器上/etc/hosts中增加：
192.168.40.7   master1-admin  
192.168.40.8   node1-monitor  
192.168.40.9   node2-osd  
~~~

### 配置互相ssh登录

~~~sh
#设置root密码
passwd root
Aa111111111
#以master1-admin为例
ssh-keygen -t rsa
ssh-copy-id master1-admin
ssh-copy-id node1-monitor
ssh-copy-id node2-osd 
~~~

### 关闭防火墙

~~~sh
#3台都执行
systemctl stop firewalld && systemctl disable firewalld
~~~

### 关闭selinux

~~~sh
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
~~~

### 配置ceph源

~~~sh
#3台都执行
yum install -y yum-utils 
yum-config-manager --add-repo https://dl.fedoraproject.org/pub/epel/7/x86_64/ 
yum install --nogpgcheck -y epel-release
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7 
rm /etc/yum.repos.d/dl.fedoraproject.org*
~~~

~~~ini
vim /etc/yum.repos.d/ceph.repo

[Ceph]
name=Ceph packages for $basearch
baseurl=http://mirrors.aliyun.com/ceph/rpm-jewel/el7/x86_64/ 
enabled=1 
gpgcheck=0 
type=rpm-md 
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc 
priority=1
[Ceph-noarch] 
name=Ceph noarch packages 
baseurl=http://mirrors.aliyun.com/ceph/rpm-jewel/el7/noarch/ 
enabled=1 
gpgcheck=0 
type=rpm-md 
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc 
priority=1 
[ceph-source]
name=Ceph source packages 
baseurl=http://mirrors.aliyun.com/ceph/rpm-jewel/el7/SRPMS/ 
enabled=1 
gpgcheck=0 
type=rpm-md 
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc 
priority=1
~~~

### 配置时间同步

~~~sh
service ntpd stop
ntpdate cn.pool.ntp.org

crontab -e
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org

service crond restart
~~~

### 安装基础软件包

~~~sh
yum install -y yum-utils device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat  ipvsadm conntrack ntpdate telnet deltarpm
~~~

## 安装ceph集群

### 安装ceph

~~~sh
#master1-admin上执行，安装ceph-deploy
yum install python-setuptools ceph-deploy -y
#3台上都执行，安装ceph
yum install ceph ceph-radosgw  -y
#确认ceph版本
ceph --version
~~~

### 创建monitor节点

~~~sh
#master1-admin上创建一个目录，用于保存 ceph-deploy 生成的配置文件信息
cd /etc/ceph
ceph-deploy new master1-admin node1-monitor node2-osd
ls
#生成了如下配置文件，Ceph配置文件、一个monitor密钥环和一个日志文件
#ceph.conf  ceph-deploy-ceph.log  ceph.mon.keyring
~~~

### 安装ceph-monitor

~~~sh
#把ceph.conf配置文件里的默认副本数从3改成1 。把osd_pool_default_size = 2 加入[global]段，这样只有2个osd也能达到active+clean状态：
vim /etc/ceph/ceph.conf
[global]
fsid = c617a513-0b8e-40a4-ba5a-741bbc9a13d8
mon_initial_members = master1-admin, node1-monitor, node2-osd
mon_host = 192.168.40.7,192.168.40.8,192.168.40.9
auth_cluster_required = cephx
auth_service_required = cephx
auth_client_required = cephx
osd_pool_default_size = 2
mon clock drift allowed = 0.500 
mon clock drift warn backoff = 10

#mon clock drift allowed ，监视器间允许的时钟漂移量，默认值0.05
#这个设置定义了在发出警告之前，监视器的时间漂移必须超过 mon clock drift allowed 的多少倍。这意味着，如果 mon clock drift allowed 是0.500秒，那么只有当监视器的时间漂移超过5秒时，才会发出警告。
~~~

~~~sh
#初始化monitor，收集所有密钥
#master1-admin上
cd /etc/ceph
ceph-deploy mon create-initial
ls *.keyring
~~~

### 部署osd服务

~~~sh
#准备osd，在master1-admin上
cd /etc/ceph/
ceph-deploy osd prepare master1-admin:/dev/sdc
ceph-deploy osd prepare node1-monitor:/dev/sdc 
ceph-deploy osd prepare node2-osd:/dev/sdc

#激活osd，在master1-admin上
ceph-deploy osd activate master1-admin:/dev/sdc1
ceph-deploy osd activate node1-monitor:/dev/sdc1
ceph-deploy osd activate node2-osd:/dev/sdc1

#查看状态：
ceph-deploy osd list master1-admin node1-monitor node2-osd
~~~

### 创建ceph文件系统

- 要使用Ceph文件系统，你的Ceph的存储集群里至少需要存在一个Ceph的元数据服务器(mds)。

#### 创建mds

~~~sh
#master1-admin上
ceph-deploy mds create master1-admin node1-monitor node2-osd
#查看ceph当前文件系统
ceph fs ls   
~~~

> 一个cephfs至少要求两个librados存储池，一个为data，一个为metadata。当配置这两个存储池时，注意：
>
> 1. 为metadata pool设置较高级别的副本级别，因为metadata的损坏可能导致整个文件系统不可用。
> 2. 建议metadata pool使用低延时存储，比如SSD，因为metadata会直接影响客户端的响应速度。

#### 创建osd存储池

~~~sh
#master1-admin上
ceph osd pool create cephfs_data 128
ceph osd pool create cephfs_metadata 128
~~~

> 上面的128是pg_num的值，确定 pg_num 取值是强制性的，因为不能自动计算。下面是几个常用的值：
>
> - 少于 5 个 OSD 时可把 pg_num 设置为 128
>
> - OSD 数量在 5 到 10 个时，可把 pg_num 设置为 512
>
> - OSD 数量在 10 到 50 个时，可把 pg_num 设置为 4096
>
> - OSD 数量大于 50 时，你得理解权衡方法、以及如何自己计算 pg_num 取值
>
> 自己计算 pg_num 取值时可借助 pgcalc 工具：随着 OSD 数量的增加，正确的 pg_num 取值变得更加重要，因为它显著地影响着集群的行为、以及出错时的数据持久性（即灾难性事件导致数据丢失的概率）。

#### 创建文件系统

~~~sh
ceph fs new hangtestfs cephfs_metadata cephfs_data
#查看创建后的cephfs
ceph fs ls
#查看mds节点状态
ceph mds stat 
#查看存储集群状态信息
ceph -s
~~~

## 测试k8s集群挂载ceph rbd

### 安装前置软件

~~~sh
# kubernetes要想使用ceph，需要在k8s的每个node节点安装ceph-common的驱动  。
#把ceph节点上的ceph.repo文件拷贝到k8s各个节点/etc/yum.repos.d/目录下，然后在k8s的各个节点yum install ceph-common -y
scp /etc/yum.repos.d/ceph.repo 192.168.40.4:/etc/yum.repos.d/
scp /etc/yum.repos.d/ceph.repo 192.168.40.5:/etc/yum.repos.d/
scp /etc/yum.repos.d/ceph.repo 192.168.40.6:/etc/yum.repos.d/
#每个k8s节点上安装
yum install ceph-common -y
#在ceph的master1-admin上把ceph配置文件拷贝到k8s node上
scp /etc/ceph/* 192.168.40.4:/etc/ceph/
scp /etc/ceph/* 192.168.40.5:/etc/ceph/
scp /etc/ceph/* 192.168.40.6/etc/ceph/
~~~

### 配置rbd

~~~sh
#master1-admin上
#创建ceph rbd
ceph osd pool create k8srbd1 6 #创建pool，pgnum是6
rbd create rbda -s 1024 -p k8srbd1 #创建1G大小的块设备
rbd feature disable k8srbd1/rbda object-map fast-diff deep-flatten
~~~

### 创建pod挂载ceph rbd

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: po-testrbd
spec:
  containers:
    - name: nginx
      image: nginx
      imagePullPolicy: IfNotPresent
      volumeMounts:
      - name: testrbd
        mountPath: /mnt
  volumes:
    - name: testrbd #注意： k8srbd1下的rbda被pod挂载了，那其他pod就不能占用这个k8srbd1下的rbda了
      rbd:
        monitors:
        - '192.168.40.7:6789'
        - '192.168.40.8:6789'
        - '192.168.40.9:6789'
        pool: k8srbd1
        image: rbda
        fsType: xfs
        readOnly: false
        user: admin
        keyring: /etc/ceph/ceph.client.admin.keyring
~~~

- 注意：rbd设备不能同时被多个pod挂载。例如，创建一个deploy，2个pod挂载同一个rbd设备

  ~~~yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: dep-cephrbd
  spec:
    replicas: 2
    selector:
      matchLabels:
        storage: ceph
    template:
      metadata:
        labels:
          storage: ceph
      spec:
        containers:
        - name: nginx
          image: nginx
          imagePullPolicy: IfNotPresent
          volumeMounts:
          - name: testrbd
            mountPath: /mnt/
        volumes:
        - name: testrbd #注意： k8srbd1下的rbda被pod挂载了，那其他pod就不能占用这个k8srbd1下的rbda了
          rbd:
            monitors:
            - '192.168.40.7:6789'
            - '192.168.40.8:6789'
            - '192.168.40.9:6789'
            pool: k8srbd1
            image: rbda
            fsType: xfs
            readOnly: false
            user: admin
            keyring: /etc/ceph/ceph.client.admin.keyring
  ~~~

- 如果是按照前面直接挂载的方式，两个pod只有1个pod能起来，另一个会提示MountVolume.WaitForAttach failed for volume "testrbd" : rbd image k8srbd1/rbda is still being used。即使设置调度到同一pod也不行。

## 基于ceph rbd生成pv

### 创建secret

~~~sh
#创建ceph-secret这个k8s secret对象，这个secret对象用于k8s volume插件访问ceph集群，获取client.admin的keyring值，并用base64编码，在master1-admin（ceph管理节点）操作
ceph auth get-key client.admin | base64
#创建ceph的secret，在k8s的控制节点操作：
cat secret-ceph.yaml 
apiVersion: v1
kind: Secret
metadata:
  name: ceph-secret
data:
  key: QVFCVFJwdGx4Z2VoTFJBQW9QVkpsb3NvZDl1ZFBTYXRZbThDUGc9PQ== #<上一步生成的key>

kubectl apply -f ceph-secret.yaml
~~~

### 创建osd pool

~~~sh
#创建ceph rbd
ceph osd pool create k8srbd1 6 #创建pool，pgnum是6
rbd create rbda -s 1024 -p k8srbd1 #创建1G大小的块设备
rbd feature disable k8srbd1/rbda object-map fast-diff deep-flatten
~~~

### 创建pv

~~~yaml
apiVersion: v1 
kind: PersistentVolume 
metadata: 
  name: ceph-pv 
spec:   
   capacity:     
     storage: 1Gi   
   accessModes:     
   - ReadWriteOnce   
   rbd:     
         monitors:       
         - '192.168.40.7:6789'
         - '192.168.40.8:6789'
         - '192.168.40.9:6789'    
         pool: k8srbd1     
         image: rbda     
         user: admin     
         secretRef:       
           name: ceph-secret     
         fsType: xfs     
         readOnly: false   
   persistentVolumeReclaimPolicy: Recycle
~~~

### 创建pvc

~~~yaml
kind: PersistentVolumeClaim 
apiVersion: v1 
metadata:   
  name: ceph-pvc 
spec:   
  accessModes:     
  - ReadWriteOnce   
  resources:     
   requests:       
    storage: 1Gi
~~~

### 挂载pvc

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  selector:
    matchLabels:
     app: nginx
  replicas: 2 # tells deployment to run 2 pods matching the template
  template: # create pods using pod definition in this template
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
        volumeMounts:
          - name: ceph-data
            mountPath: "/ceph-data"
      volumes:
      - name: ceph-data
        persistentVolumeClaim:
          claimName: ceph-pvc
~~~

- 做成pv来挂载，就允许同一node上的多pod挂载了：ceph rbd块存储能在同一个node上跨pod以ReadWriteOnce共享挂载；ceph rbd块存储能在同一个node上同一个pod多个容器中以ReadWriteOnce共享挂载
- ceph rbd块存储不能跨node以ReadWriteOnce共享挂载
  - 如果一个使用ceph rdb的pod所在的node挂掉，这个pod虽然会被调度到其它node，但是由于rbd不能跨node多次挂载和挂掉的pod不能自动解绑pv的问题，这个新pod不会正常运行

- 解决办法：

  1，使用能支持跨node和pod之间挂载的共享存储，例如cephfs，GlusterFS等

  2，给node添加label，只允许deployment所管理的pod调度到一个固定的node上。（不建议，这个node挂掉的话，服务就故障了）

## 基于storage class动态生成pv

### ceph配置文件授权

~~~sh
#3台ceph节点和3台k8s节点都执行。sc需要用到。
chmod 777  -R  /etc/ceph/*
mkdir /root/.ceph/
cp -ar /etc/ceph/ /root/.ceph/
~~~

### 安装rbd供应商

~~~sh
#事先上传镜像
docker load -i 
~~~

~~~yaml
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: rbd-provisioner
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: rbd-provisioner
rules:
  - apiGroups: [""]
    resources: ["persistentvolumes"]
    verbs: ["get", "list", "watch", "create", "delete"]
  - apiGroups: [""]
    resources: ["persistentvolumeclaims"]
    verbs: ["get", "list", "watch", "update"]
  - apiGroups: ["storage.k8s.io"]
    resources: ["storageclasses"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["create", "update", "patch"]
  - apiGroups: [""]
    resources: ["services"]
    resourceNames: ["kube-dns","coredns"]
    verbs: ["list", "get"]
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: rbd-provisioner
subjects:
  - kind: ServiceAccount
    name: rbd-provisioner
    namespace: default
roleRef:
  kind: ClusterRole
  name: rbd-provisioner
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: rbd-provisioner
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
- apiGroups: [""]
  resources: ["endpoints"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: rbd-provisioner
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: rbd-provisioner
subjects:
- kind: ServiceAccount
  name: rbd-provisioner
  namespace: default
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rbd-provisioner
spec:
  selector:
    matchLabels:
      app: rbd-provisioner
  replicas: 1
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: rbd-provisioner
    spec:
      containers:
      - name: rbd-provisioner
        image: quay.io/xianchao/external_storage/rbd-provisioner:v1
        imagePullPolicy: IfNotPresent
        env:
        - name: PROVISIONER_NAME
          value: ceph.com/rbd
      serviceAccount: rbd-provisioner
~~~

### 创建ceph secret

~~~sh
#创建ceph-secret这个k8s secret对象，这个secret对象用于k8s volume插件访问ceph集群，获取client.admin的keyring值，并用base64编码，在master1-admin（ceph管理节点）操作
ceph auth get-key client.admin | base64
~~~

~~~yaml
#创建ceph的secret，在k8s的控制节点操作：
apiVersion: v1
kind: Secret
metadata:
  name: ceph-secret-sc
type: "ceph.com/rbd" #secret的type除了可以用内置的，也可以自定义一个string。
data:
  key: QVFCVFJwdGx4Z2VoTFJBQW9QVkpsb3NvZDl1ZFBTYXRZbThDUGc9PQ== #<上一步生成的key>
~~~

~~~sh
#创建ceph pool，只需要创建pool即可，rbd设备会被sc来自动创建
ceph osd pool create k8stest1 6 #创建pool，pgnum是6
~~~

### 创建sc

~~~yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: k8s-rbd
provisioner: ceph.com/rbd #要用provisioner里面env定义的name
parameters:
  monitors: 192.168.40.8:6789,192.168.40.7:6789,192.168.40.9:6789
  adminId: admin
  adminSecretName: ceph-secret-sc
  pool: k8stest1
  userId: admin
  userSecretName: ceph-secret-sc
  fsType: xfs
  imageFormat: "2" #指定了RBD镜像的格式。"2"表示使用第二版的RBD镜像格式，这是一种新的、更加灵活的格式，支持更多的特性，如快照、克隆和层次化存储等
  imageFeatures: "layering" #这个参数指定了RBD镜像的特性。"layering"表示启用了层次化存储特性。层次化存储允许镜像共享相同的数据块，可以节省存储空间，并且可以更快地创建新的镜像和快照。
~~~

> [!warning] K8s 1.20版本兼容问题
> k8s1.20版本通过rbd provisioner动态生成pv会报错:
>
> ```sh
> kubectl logs rbd-provisioner-685746688f-8mbz
> ```
>
> E0418 15:50:09.610071    1 controller.go:1004] provision "default/rbd-pvc" class "k8s-rbd": unexpected error getting claim reference: selfLink was empty, can't make reference
>
> - 报错原因是1.20版本禁用了selfLink，解决方法如下；
>
> - 编辑/etc/kubernetes/manifests/kube-apiserver.yaml，在这里：
>
> ```yaml
> spec:
>  containers:
>  - command:
>    - kube-apiserver
> ```
>
> 添加这一行：
>
> ```yaml
> - --feature-gates=RemoveSelfLink=false
> ```
>
> 重启kubelet
>
> ~~~sh
> systemctl restart kubelet
> ~~~

### 创建pvc

~~~yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: rbd-pvc
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  resources:
    requests:
      storage: 1Gi
  storageClassName: k8s-rbd
~~~

> 在Kubernetes的PersistentVolumeClaim（PVC）定义中，`pvc.spec.volumeMode`字段用于指定所请求的存储卷的访问模式。
>
> `volumeMode`字段有两个可能的取值：
>
> 1. `Filesystem`：这是默认的模式。在这种模式下，Kubernetes会在卷上创建一个文件系统，然后将这个文件系统挂载到Pod中的容器上。
> 2. `Block`：在这种模式下，卷作为裸设备（raw block device）提供给Pod。也就是说，卷不会被格式化，也不会被挂载到Pod中的容器上。而是直接作为块设备提供给容器使用。
>
> 这两种模式的选择取决于你的应用需求。一般来说，大多数应用都会使用`Filesystem`模式，但是一些需要高性能IO或者特殊的文件系统特性的应用可能会选择`Block`模式。

### 创建pod挂载pvc

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    test: rbd-pod
  name: ceph-rbd-pod
spec:
  containers:
  - name: ceph-rbd-nginx
    image: nginx:latest
    imagePullPolicy: IfNotPresent
    volumeMounts:
    - name: ceph-rbd
      mountPath: /mnt
      readOnly: false
  volumes:
  - name: ceph-rbd
    persistentVolumeClaim:
      claimName: rbd-pvc
~~~

## k8s挂载cephfs

### 创建ceph子目录

~~~sh
ceph fs ls
#为了别的地方能挂载cephfs，先创建一个secretfile，在master1-admin上
cat /etc/ceph/ceph.client.admin.keyring |grep key|awk -F" " '{print $3}' > /etc/ceph/admin.secret

#挂载cephfs的根目录(192.168.40.8:6789:/)到集群mon节点下的一个目录，比如/mnt/k8s_data/，因为挂载后，我们就可以直接在k8s_data下面用Linux命令创建子目录了。
mkdir /mnt/k8s_data/
mount -t ceph 192.168.40.8:6789:/ /mnt/k8s_data -o name=admin,secretfile=/etc/ceph/admin.secret
df -h

#在cephfs的根目录里面创建了一个子目录podtest，k8s以后就可以挂载这个目录 
cd /mnt/k8s_data/
mkdir podtest -p
chmod 0777 podtest/ 
~~~

### 创建secret

~~~sh
#将/etc/ceph/ceph.client.admin.keyring里面的key的值转换为base64
cat /etc/ceph/ceph.client.admin.keyring | base64
W2NsaWVudC5hZG1pbl0KCWtleSA9IEFRQlRScHRseGdlaExSQUFvUFZKbG9zb2Q5dWRQU2F0WW04Q1BnPT0K
~~~

~~~yaml
#创建secret
apiVersion: v1
kind: Secret
metadata:
  name: cephfs-secret
data:
  key: W2NsaWVudC5hZG1pbl0KCWtleSA9IEFRQlRScHRseGdlaExSQUFvUFZKbG9zb2Q5dWRQU2F0WW04Q1BnPT0K
~~~

### 创建pv

~~~yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: cephfs-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteMany
  cephfs:
    monitors:
      - 192.168.40.8:6789
    path: /podtest
    user: admin
    readOnly: false
    secretRef:
        name: cephfs-secret
  persistentVolumeReclaimPolicy: Recycle  
~~~

### 创建pvc

~~~yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: cephfs-pvc
spec:
  accessModes:
    - ReadWriteMany
  volumeName: cephfs-pv
  resources:
    requests:
      storage: 1Gi
~~~

### pod挂载pvc

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: cephfs-pod-1
spec:
  containers:
    - image: nginx
      name: nginx
      imagePullPolicy: IfNotPresent
      volumeMounts:
      - name: test-v1
        mountPath: /mnt
  volumes:
  - name: test-v1
    persistentVolumeClaim:
      claimName: cephfs-pvc
~~~

## 基于Rook部署ceph集群

### 安装ceph

参考：[Rook Quickstart Guide](https://rook.github.io/docs/rook/v1.12/Getting-Started/quickstart/#cluster-environments)

- 下载ceph安装包：[rook/rook - GitHub](https://github.com/rook/rook)

~~~sh
unzip rook-master.zip
cd rook-master/deploy/examples/
vim operator.yaml
#修改镜像地址：registry.k8s.io访问速度慢。可以使用阿里云的镜像源：registry.cn-hangzhou.aliyuncs.com/google_containers。
##把下面的镜像地址修改成阿里云的##
# ROOK_CSI_CEPH_IMAGE: "quay.io/cephcsi/cephcsi:v3.7.2"
# ROOK_CSI_REGISTRAR_IMAGE: "registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.7.0"
# ROOK_CSI_RESIZER_IMAGE: "registry.k8s.io/sig-storage/csi-resizer:v1.7.0"
# ROOK_CSI_PROVISIONER_IMAGE: "registry.k8s.io/sig-storage/csi-provisioner:v3.4.0"
# ROOK_CSI_SNAPSHOTTER_IMAGE: "registry.k8s.io/sig-storage/csi-snapshotter:v6.2.1"
# ROOK_CSI_ATTACHER_IMAGE: "registry.k8s.io/sig-storage/csi-attacher:v4.1.0"
##改完之后变成如下##
ROOK_CSI_CEPH_IMAGE: "quay.io/cephcsi/cephcsi:v3.7.2"
ROOK_CSI_CEPH_IMAGE: "registry.cn-hangzhou.aliyuncs.com/google_containers/cephcsi:v3.7.2"   ROOK_CSI_REGISTRAR_IMAGE: "registry.cn-hangzhou.aliyuncs.com/google_containers/csi-node-driver-registrar:v2.7.0"
ROOK_CSI_RESIZER_IMAGE: "registry.cn-hangzhou.aliyuncs.com/google_containers/csi-resizer:v1.7.0"
ROOK_CSI_PROVISIONER_IMAGE: "registry.cn-hangzhou.aliyuncs.com/google_containers/csi-provisioner:v3.4.0"
ROOK_CSI_SNAPSHOTTER_IMAGE: "registry.cn-hangzhou.aliyuncs.com/google_containers/csi-snapshotter:v6.2.1"
ROOK_CSI_ATTACHER_IMAGE: "registry.cn-hangzhou.aliyuncs.com/google_containers/csi-attacher:v4.1.0"
#修改以下字段：
ROOK_ENABLE_DISCOVERY_DAEMON： "true"
#Rook的一个环境变量，用于控制是否启用发现守护程序。发现守护程序是Rook集群中的一个组件，用于检测新的存储设备并将其添加到Rook集群中。
~~~

- 安装rook

~~~sh
kubectl apply -f crds.yaml -f common.yaml -f operator.yaml
kubectl get pods -n rook-ceph
~~~

### 创建ceph集群

- 修改cluster.yaml文件（在/rook-master/deploy/examples/路径下）

~~~yaml
storage:
  useAllNodes: false
  useAllDevices: false
  #deviceFilter:
  config:
    nodes:
      - name: "master1"
        devices:
        - name: "sdb"
      - name: "node1"
        devices:
        - name: "sdb"
      - name: "node2"
        devices:
        - name: "sdb"
#部署
kubectl apply -f cluster.yaml
~~~

字段说明：

- useAllNodes
  - true： Rook 会在所有可用的 Kubernetes 节点上启动存储服务。这意味着每一个 Kubernetes 节点（服务器或虚拟机）都会被用来运行 Ceph 存储服务，从而使整个 Kubernetes 集群的所有节点都参与到存储服务中。
  - false： Rook 只会在指定的 Kubernetes 节点上启动存储服务。这意味着只有你明确选择的节点会被用来运行 Ceph 存储服务，而不是整个集群的所有节点。

- useAllDevices：
  - true： Rook 会在所有可用的存储设备上启动存储服务。这意味着每一个被检测到的存储设备（如硬盘、SSD）都会被用来存储数据，从而充分利用所有可用的存储资源。
  - false： Rook 只会在你指定的存储设备上启动存储服务。这意味着只有你明确选择的存储设备会被用来存储数据，而不是所有可用的存储设备。

- -name:”sdb”: 采用裸盘，即未格式化的磁盘。其中master1, node1, node2新加磁盘sdb，建议最少三个节点，否则后面的试验可能会出现问题

### 安装ceph客户端工具

~~~sh
kubectl apply -f toolbox.yaml -n rook-ceph
#等待pod running
kubectl -n rook-ceph exec -it rook-ceph-tools-6adffg7qzsvg-adv -- bash
ceph status
ceph osd status
ceph df
~~~

### 安装ceph dashboard

- 默认情况下，ceph dashboard已经创建好了，可以在ceph dashboard前面创建一个nodePort类型的Service暴露pod

~~~yaml
tee dashboard.yaml <<'EOF'
apiVersion: v1
kind: Service
metadata:
  labels:
    app: rook-ceph-mgr
    ceph_daemon_id: a
    rook_cluster: rook-ceph
  name: rook-ceph-mgr-dashboard
  namespace: rook-ceph
spec:
  ports:
  - name: http-dashboard
    port: 7000
    protocol: TCP
    targetPort: 7000
  selector:
    app: rook-ceph-mgr
    ceph_daemon_id: a
    rook_cluster: rook-ceph
  sessionAffinity: None
  type: NodePort
EOF
~~~

- 任意节点IP:Nodeport即可查看ceph dashboard

  - username: admin

  - password:

    ```sh
    kubectl -n rook-ceph get secret rook-ceph-dashboard-password -o jsonpath="{['data']['password']}" | base64 --decode && echo
    ```

    
