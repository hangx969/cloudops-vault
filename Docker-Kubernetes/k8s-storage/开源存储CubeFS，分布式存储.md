---
title: K8s分布式存储CubeFS
tags:
  - kubernetes
  - storage
aliases:
  - CubeFS部署
---

# K8s分布式存储CubeFS


## 存储架构对比

### 单节点存储

一种常见但又失败的存储设计：一台存储服务器，挂载了很多磁盘，搭建一个nfs或者其他nas服务提供存储。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202508281559728.png" alt="image-20250828155935532" style="zoom:50%;" />

这种架构存在很多问题：

1. 单点故障，非高可用
   - 如果想再搭一台作为高可用，很难实时同步两台节点的数据；而且故障转移也很困难，大概率转移不过去。

2. 性能瓶颈，数据阻塞
   - 存储服务器的网卡成为网络数据流量的瓶颈，一般只有一个或者两个磁盘承载读写，也会成为瓶颈。

3. 存储有限，扩容复杂
4. 安全性低，容易宕机
5. 功能有限，只支持文件
   - 如果想实现块存储或者对象存储是不支持的

6. 隔离性差，无权限管理

### 分布式存储

生产环境中建议使用分布式存储。分布式存储有以下优势：

1. 支持近乎无限的扩容
   - 可以通过添加节点到集群的方式扩容
   - 扩容后集群会自动balance

2. 支持容错能力和数据冗余
   - 可以配置存储多份文件副本
   - 可以配置文件拆分成多份存储到不同节点上

3. 支持多机房多区域部署
4. 支持负载均衡和并行处理
   - 数据可以在多个节点并行处理，性能更好

5. 支持权限管理和多用户
6. 支持多种文件存储类型
   - 块存储（可以当做一块硬盘直接挂载到某台机器上或者容器内）、对象存储（s3、hadoop等协议）

7. 支持普通硬件设计
   - nfs存储性能就依赖于高性能磁盘，分布式存储可以通过缓存、中间件等，即使在普通硬件上也可以提高性能

### 分布式存储平台

主要对比主流的Ceph和CubeFS：

| 特性       | Ceph                                                         | CubeFS                                                       |
| ---------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 设计目标   | 统一存储解决方案，支持块、对象、文件存储                     | 专注于文件、对象存储                                         |
| 存储类型   | 对象、块、文件系统                                           | 对象、文件系统（目前不支持块存储）                           |
| 扩展性     | 支持超大规模集群，PB-EB级                                    | 支持大规模集群，但是针对中小规模场景优化更好                 |
| 性能       | 大文件性能优秀，小文件性能一般                               | 小文件和大文件性能均优秀                                     |
| 元数据管理 | 基于RADOS分布式存储，元数据分布在OSD中                       | 独立的Metadata节点管理元数据，避免瓶颈                       |
| 部署复杂度 | 需要配置多组件（Monitor、Manager、OSD等）维护比k8s还困难<br />直接部署到k8s较困难，而且对接K8s也需要其它工具支持 | 轻量级，部署简单，适合云原生环境                             |
| 硬件要求   | 对磁盘IO和网络带宽要求较高                                   | 硬件要求相对较低（企业级也要用高性能磁盘和万兆带宽）         |
| 社区活跃度 | 社区庞大、文档丰富、生态成熟                                 | 中文文档齐全（由OPPO开源的）                                 |
| 成熟度     | 技术成熟，已在生产环境中广泛使用                             | 较新的项目，生产环境验证时间较短                             |
| 使用场景   | 通用存储需求，企业级数据中心                                 | 云原生环境、大数据分析、AI训练、容器化等场景，有专门优化。   |
| 兼容性     | 支持多种协议（S3、iSCSI、NFS、HDFS等）                       | 支持多种协议，主要针对对象、文件存储                         |
| 扩展方式   | 水平扩展、支持动态扩展                                       | 水平扩展、支持动态扩展                                       |
| 容错机制   | 多副本嚯纠删码机制                                           | 多副本或纠删码机制（文件经常访问-多副本好一些；不经常访问-纠删码好一些） |

### k8s上落地分布式存储平台

裸机部署分布式存储平台，管理很复杂，而且对故障的承受能力也比较差。

在k8s上部署分布式存储平台，有如下优势：

1. 简化部署和管理
   - 不需要在每台机器上维护配置文件。用helm等工具在k8s上实现IaC，方便管理

2. 自动化运维
3. 一键式动态扩展
   - daemonset实现每个节点的配置相同

4. 故障自愈和高可用性
   - 健康检查、自动故障恢复漂移

5. 云原生生态集成
   - 云原生应用可以直接用CSI对接到存储

## CubeFS介绍

官网：[CubeFS - 云原生分布式存储系统](https://www.cubefs.io/zh/docs/master/overview/introduction.html)

CubeFS是新一代云原生存储产品，目前已经是CNCF毕业的开源项目。兼容S3、POSIX、HDFS等多种访问协议，支持多副本与纠删码两种存储引擎，提供多租户、多AZ部署以及跨区域复制等多种特性。广泛应用于大数据、AI、容器平台、数据库、中间件存算分离、数据共享以及数据保护等场景。

比如大模型服务，部署一个deepseek，671B的参数量，模型文件就得接近上TB。模型文件越多，对存储性能要求越高，放到CubeFS上，吞吐量很优秀，可以支持大模型服务。放到单节点存储上会拖慢大模型速度。

### 特性

1. 多协议：S3、POSIX、HDFS
2. 双引擎：支持多副本和纠删码
3. 多租户：支持多租户隔离和权限分配
4. 可扩展：支持各模块水平扩展、轻松扩展到PB或EB级
5. 高性能：支持多级缓存、支持多种高性能的复制协议。
6. 云原生：自带CSI插件，一键集成到k8s
7. 多场景：大数据分析、机器学习、深度训练、共享存储、对象存储、数据库中间件等。

### 架构

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202508281651643.png" alt="image-20250828165135446" style="zoom:50%;" />

1. Master Node：

   集群管理中枢和请求入口，管理其他节点，分发请求到其他节点

2. Meta Node：

   元数据节点，存储文件metadata：文件名称、存储状态、副本状态等。这些数据都是缓存到内存中的

3. Data Node:

   数据节点，真正存储数据的地方。如果采用副本模式就是Data Node；如果采用纠删码模式就是Blob Node。

4. Object Node：

   CubeFS也是支持S3协议的，object node对外提供s3协议，应用通过object node作为入口访问到对象存储。

## 企业级分布式存储架构设计

### 部署方式

#### 混合部署

混合部署指的是已经有一个现成的k8s集群，已经部署了一些业务应用，再把分布式存储平台也部署上去。

不过是部署在特殊节点上，通过打污点的形式，不让其他应用pod部署上去。

对于CubeFS的挂载，应用可以通过Master节点的service来挂载，或者通过object node来挂载对象存储。

#### 独立部署-基础设施集群

是企业中比较常见、典型、可靠的部署方式：

1. 把一些通用服务单独部署到基础设施集群中（比如CubeFS、prometheus、grafana、ECK等）
2. 应用业务单独部署在业务集群中

基础设施集群中的通用服务怎么对外提供服务？需要看服务是通过什么协议代理的：

1. 通过TCP四层协议代理的，比如mysql、redis：
   - 可以在两个集群中间加一个F5（负载均衡器）
   - 可以把服务通过NodePort暴露

2. 通过HTTP七层协议代理的
   - 可以通过ingress，暴露一个内部域名，只能内网去解析。如果没有内网域名，可以在业务集群的coreDNS上配置自定义解析，解析到基础设施集群的入口。
   - 也可以通过istio ingressGateway暴露域名。

### 资源分配建议

#### 总内存

以CubeFS为例，元数据节点总内存计算规则：每个文件元数据占用空间2KB-4KB。

- 根据文件数量预估：
  - 假设已知的文件数量预估为10亿，则需要的内存KB为：20亿KB
  - 换算为GB：20亿/1024/1024 = 2000GB = 2TB内存

- 根据数据量预估：
  - 假设集群数据总量为10PB = 10240TB = 10737418240MB
  - 通过CubeFS默认分片大小8MB预估，可能需要10737418240/8=1342177280个文件
  - 通过计算规则，需要的内存为：1342177280*2 = 2684354560KB = 2500GB = 2.5TB

#### 服务器硬件

假设需要落地1PB CubeFS存储（需要256G内存）。

常见的配置：一台16硬盘位的存储服务器：

- 每个硬盘位插一个16T的SAS硬盘（目前SAS盘性价比最高），这样一台存储服务器就有256T硬盘空间，四台就能满足1PB了。
- 四个内存槽，每个插上64G内存条，总共256G内存，四台服务器就有约1TB内存了，远超需求量。（内存一般来说是容易满足的，而且服务器内存条也比较便宜，不会成为瓶颈）

如果担心16盘位受到服务器故障影响较大，可以换成8盘位的服务器：

- 每个硬盘位插一个16T的SAS硬盘，8台可以满足1PB。
- 内存槽4个，每个槽插一个32G内存条，8台也是1TB内存，足够用。

所以就把服务器盘位、硬盘容量规划好就行，内存一般不会成为瓶颈。

## CubeFS部署

### 部署架构

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202508281805748.png" alt="image-20250828180510573" style="zoom:50%;" />

- `Master`：资源管理节点，负责维护整个集群的元信息，部署为 StatefulSet 资源。
- `DataNode`：数据存储节点，需要挂载大量磁盘负责文件数据的实际存储，部署为 DaemonSet 资源。
- `MetaNode`：元数据节点，负责存储所有的文件元信息，部署为 DaemonSet 资源。
- `ObjectNode`：负责提供转换 S3 协议提供对象存储的能力，无状态服务，部署为 Deployment 资源。

### 配置标签

CubeFS 安装时会根据这些标签通过`nodeSelector`进行匹配，然后在机器创建起对应的`Pod`。

实验环境下就三个节点，所有节点都用作所有三个角色：

~~~sh
# Master 节点，至少三个，建议为奇数个 
kubectl label node component.cubefs.io/master=enabled --all
# MetaNode 元数据节点，至少 3 个，奇偶无所谓 
kubectl label node component.cubefs.io/metanode=enabled --all
# Dataode 数据节点，至少 3 个，奇偶无所谓 
kubectl label node component.cubefs.io/datanode=enabled --all
# ObjectNode 对象存储节点，可以按需进行标记，不需要对象存储功能的话也可以不部署这个组件 
kubectl label node component.cubefs.io/objectnode=enabled --all
~~~

### 配置数据盘

搭建分布式存储，是需要专门挂载磁盘的。

在配置了`kubectl label node <nodename> component.cubefs.io/datanode=enabled`的数据节点上，对数据盘进行初始化操作。

首先添加一个新盘，然后通过fdisk -l查看：

~~~sh
fdisk -l | grep dev/sd
# Disk /dev/sdb: 6 GiB, 6442450944 bytes, 12582912 sectors
~~~

> [!warning] 磁盘空间要求
> 磁盘可用空间必须大于10G，否则磁盘会被cubeFS标记为ReadOnly，并且空间计算也会不准确。
>
> 参考：[[Bug]: the datanodes is not WRITABLE - Issue #3173](https://github.com/cubefs/cubefs/issues/3173#issuecomment-1986599468)

格式化磁盘并挂载：

~~~sh
# 格式化硬盘 
mkfs.xfs -f /dev/sdb 
# 创建挂载目录，如果机器上存在多个需要挂载的数据磁盘，则每个磁盘按以上步骤进行格式化和挂载磁盘，挂载目录按照data0/data1/../data999的顺序命名 
mkdir /data0 
# 挂载磁盘 
mount /dev/sdb /data0 

# 开机自动挂载
blkid /dev/sdb # 获取磁盘UUID
tee -a /etc/fstab <<'EOF' 
UUID=c94b2053-bf99-4268-8255-bcbe4e6e4b7f   /data0   xfs    defaults  0 0
EOF
mount -a 
~~~

> [!warning] 注意
> 如果有多个数据节点，需要保证每个数据节点的磁盘数量、大小等配置是完全一致的。因为后面配置数据节点的时候，是所有数据节点统一配置的。这样出错的概率小。

### helm安装

官网指南：[CubeFS K8s部署指南](https://www.cubefs.io/zh/docs/master/deploy/k8s.html)

github地址：[cubefs-helm - GitHub](https://github.com/cubefs/cubefs-helm)

#### 下载helm包

~~~sh
git clone https://github.com/cubefs/cubefs-helm.git
~~~

#### 配置values

##### 组件和镜像

~~~yaml
# 临时关闭一些组件 
cd cubefs-helm/cubefs 
vim values.yaml 
  client: false 
  csi: false 
  monitor: false 
  ingress: false 
# 调整组件的镜像地址（如果报错说明镜像源还不支持这些新版镜像，还是用默认的，手动传到节点解压）
image: 
  server: m.daocloud.io/docker.io/cubefs/cfs-server:v3.4.0 
  client: m.daocloud.io/docker.io/cubefs/cfs-client:v3.4.0 
  blobstore: m.daocloud.io/docker.io/cubefs/blobstore:v3.4.0 
  csi_driver: m.daocloud.io/docker.io/cubefs/cfs-csi-driver:v3.4.0 
  csi_provisioner: m.daocloud.io/registry.k8s.io/sig-storage/csi-provisioner:v2.2.2 
  csi_attacher: m.daocloud.io/registry.k8s.io/sig-storage/csi-attacher:v3.4.0 
  csi_resizer: m.daocloud.io/registry.k8s.io/sig-storage/csi-resizer:v1.3.0 
  driver_registrar: m.daocloud.io/registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.5.0 
  grafana: m.daocloud.io/docker.io/grafana/grafana:6.4.4 
  prometheus: m.daocloud.io/docker.io/prom/prometheus:v2.13.1 
  consul: m.daocloud.io/docker.io/library/consul:1.6.1 
~~~

##### 主节点配置

~~~yaml
# 主节点副本数，建议奇数 
master: 
  replicas: 3
  tolerations:
    - key: "node-role.kubernetes.io/control-plane"
      operator: "Equal"
      effect: "NoSchedule"
# 资源请求： 
  resources:
    enabled: true
    requests: 
      memory: "256Mi" 
      cpu: "200m" 
    limits: 
      memory: "2Gi" 
      cpu: "2000m" 
# 生产环境建议： 
    requests: 
      memory: "8Gi" 
      cpu: "2000m" 
    limits: 
      memory: "32Gi" 
      cpu: "8000m"
~~~

##### 元数据节点配置

~~~yaml
metanode: 
  # metanode可用的内存，建议主机内存的80% 
  total_mem: "7516192768" # 这里配置7G
# 资源配置 
  resources:
    enabled: true
    requests: 
      memory: "256Mi" 
      cpu: "200m" 
    limits: 
      memory: "2Gi" 
      cpu: "2000m" 
# 生产环境建议 
  resources:
    enabled: true
    requests: 
      memory: "32Gi" 
      cpu: "2000m" 
    limits: 
      memory: "256Gi" # 要比上面的total_mem的值稍微大一些。比如上面配置了128G，这里配置132G。给一些buffer
      cpu: "8000m" 
~~~

##### 数据节点配置

~~~yaml
# 数据盘配置 
# datanode.disks字段用于配置数据的挂载点，同时可以为每个磁盘保留一定的空间 
  disks:
    # 格式: 挂载点:保留的空间
    # 保留的空间: 单位字节，当磁盘剩余空间小于该值时将不会再在该磁盘上写入数据
    - /data0:536870912
# 资源配置：
  resources:
    enabled: true
    requests: 
      memory: "256Mi" 
      cpu: "200m" 
    limits: 
      memory: "2Gi" 
      cpu: "2000m" 
# 生产环境建议 
    requests: 
      memory: "8Gi" 
      cpu: "2000m" 
    limits: 
      memory: "32Gi" 
      cpu: "8000m" 
~~~

##### 对象存储节点配置

~~~yaml
objectnode: 
  # 对象存储的域名 
  region: "spark" 
# 对象存储的域名。公司内部有域名就用，没有就用这个默认的。
domains: "objectcfs.cubefs.io,objectnode.cubefs.io" 
~~~

#### 安装CubeFS

~~~sh
cd ./cubefs-helm/cubefs
helm upgrade -i cubefs -n cubefs . --create-namespace -f values.yaml 
~~~

> [!bug] 版本Bug
> 2025-08-28 安装的3.3.2.150.0 Release版本，有个bug：
>
> 在`cubefs-helm/cubefs/templates/statefulset-master.yaml`文件的第80行，需要把：
>
> `value: {{ .Value.master.legacy_data_media_type | quote }}` 他的Value加上s：
>
> `value: {{ .Values.master.legacy_data_media_type | quote }}`
>
> 否则会报错：Error: template: cubefs/templates/statefulset-master.yaml:80:30: executing "cubefs/templates/statefulset-master.yaml" at <.Value.master.legacy_data_media_type>: nil pointer evaluating interface {}.master

如果遇到启动失败的，可以在对应的节点上，查看/var/log/cubefs下的日志。

## CubeFS客户端部署使用

官网：[CubeFS CLI概览](https://www.cubefs.io/zh/docs/master/user-guide/cli/overview.html)

### 下载工具包

~~~sh
# 下载地址: https://github.com/cubefs/cubefs/releases/ 
tar xf cubefs-3.5.0-linux-amd64.tar.gz 
cd build/bin 
cp ./cfs-cli /usr/local/bin/
cfs-cli --version
~~~

### 客户端配置

~~~sh
cfs-cli cluster info
# 报错解析不了域名
# 修改配置
vim ~/.cfs-cli.json
# 更改masterAddr为master service的svc ip 
{ 
  "masterAddr": [ 
    "10.99.61.70:17010" 
  ], 
  "timeout": 60 
} 
# 查询集群状态
./cfs-cli cluster info
~~~

### 集群管理

~~~sh
# 查看集群信息
cfs-cli cluster info
# 获取集群状态
cfs-cli cluster stat 
~~~

Metanode的Total为最大可用内存，由所有metanode的MaxMemAvailWeight之和计算得来。

设置卷删除延迟的时间，表示卷被删除多久才会被彻底删除，默认48h，在此之前可以恢复：

~~~sh
cfs-cli cluster volDeletionDelayTime 72 
~~~

### 元数据节点管理

列出所有的元数据节点，包括ID、地址、读写状态及存活状态等：

~~~sh
cfs-cli metanode list
~~~

查看某个节点的详细信息：

~~~sh
cfs-cli metanode info rn1:17210
~~~

### 数据节点管理

列举所有的数据节点，包括ID、地址、读写状态和存活状态： 

~~~sh
cfs-cli datanode list
~~~

展示某个节点的详细信息： 

~~~sh
cfs-cli datanode info rn2:17310
~~~

下线数据节点，下线之后该该节点的数据会自动迁移到其他数据节点。

~~~sh
cfs-cli datanode decommission rn2:17310
# 下线之后，该节点无法查看，可用数据空间也降低
cfs-cli datanode info rn2:17310
cfs-cli cluster stat
~~~

该下线节点的datanode pod不会被删除，删掉pod重建之后，这个数据节点就会重新加入，数据空间恢复。

### 数据卷管理

数据卷可以给服务使用或者挂载到宿主机。如果是外部服务需要使用cubeFS，那就需要创建卷给外部服务用。如果存储是在k8s内部，那么就不需要创建卷了，直接用csi管理。

列出所有的卷：

~~~sh
cfs-cli volume list
~~~

创建一个卷：

~~~sh
# 命令格式：cfs-cli volume create [VOLUME NAME] [USER ID] [flags] 
# user id可以随便写，会自动创建这个用户
cfs-cli volume create volume-test test --capacity 1
~~~

列出卷：

~~~sh
cfs-cli volume list
~~~

查看某个卷的详细信息：

~~~sh
cfs-cli volume info volume-test
~~~

禁用卷、取消禁用

~~~sh
cfs-cli volume set-forbidden volume-test true 
cfs-cli volume info volume-test | grep -i Forbidden 
# 取消禁用
cfs-cli volume set-forbidden volume-test false 
cfs-cli volume info volume-test | grep -i Forbidden
~~~

卷扩容、更新卷：

~~~sh
cfs-cli volume update volume-test --capacity 2
cfs-cli volume list
~~~

添加空间限制（空间满了之后就不允许写入了）：

~~~sh
cfs-cli volume update volume-test --readonly-when-full true 
~~~

删除卷：

~~~sh
cfs-cli volume delete volume-test -y
~~~

## CubeFS用户管理

CubeFS支持多用户，可以为每个用户对每个卷分配不同的权限，同时也可为对象存储提供用户认证。

主要应用场景是对象存储给不同程序去用的时候，不同的卷权限不同，用户名密码也不同。

~~~sh
cfs-cli user create -h 
# 创建用户
cfs-cli user create hangx
# 获取用户信息
cfs-cli user info hangx
# 列举所有用户
cfs-cli user list
# 删除用户
cfs-cli user delete hangx --yes
~~~

## CubeFS挂载测试

如果k8s集群外部裸机或者虚机部署的服务也想挂载cubeFS，也是可以的，挂载完成就等于访问一个本地文件夹一样了。

测试在K8s宿主机挂载cubeFS文件。由于masterAddr可以通过svc访问，就直接用svc地址了。如果对集群外部访问的话需要把master-service这个svc通过NodePort或者域名暴露出去。

客户端安装fuse：

~~~sh
yum install fuse -y 
~~~

cubeFS创建volume：

~~~sh
# 创建卷
cfs-cli volume create volume-test ltptest --capacity 1
~~~

客户端创建配置文件：

~~~sh
cat volume-test-client.conf  
{ 
  "mountPoint": "/volume-test", 
  "volName": "volume-test", 
  "owner": "ltptest", 
  "masterAddr": "10.99.61.70:17010", 
  "logDir": "/cfs/client/log", 
  "logLevel": "info", 
  "profPort": "27510" 
} 
~~~

执行挂载：

~~~sh
# 用的是另一个叫cfs-client的客户端工具
cp /root/cubefs-client/build/bin/cfs-client /usr/local/bin/
cfs-client -c volume-test-client.conf
# 这会：
# 1. 读取配置文件中的集群连接信息
# 2. 通过 FUSE 创建一个虚拟文件系统挂载点
# 3. 将文件系统操作转换为网络请求发送给 CubeFS 集群
df -Th | grep volume-test
~~~

> [!info] 挂载协议
> 这种挂载方式使用的是传统的POSIX。CubeFS 客户端通过 FUSE (Filesystem in Userspace) 提供标准的 POSIX 文件系统语义

测试写入数据：

~~~sh
dd if=/dev/zero of=./testdata bs=1M count=512
dd if=/dev/zero of=./testdata2 bs=128M count=4
# 查看卷使用
cfs-cli volume list
~~~

## CubeFS扩容

### 新加磁盘

如果CubeFS是部署在K8s中的，扩容时需要给每个datanode都添加同样的磁盘。要注意新加的盘要和原来的盘大小、性能、型号一样，这样集群的balance不会受到影响。

~~~sh
# 加完盘进系统，格式化
mkfs.xfs -f /dev/sdc
# 创建挂载目录，如果机器上存在多个需要挂载的数据磁盘，则每个磁盘按以上步骤进行格式化和挂载磁盘，挂载目录按照data0/data1/../data999的顺序命名 
mkdir /data1 
# 挂载磁盘 
mount /dev/sdc /data1
blkid /dev/sdc
tee -a /etc/fstab <<'EOF' 
UUID=f3a1fd89-ff67-4512-b2d3-e914440d4b84   /data0   xfs    defaults  0 0
EOF
mount -a 
~~~

更新helm配置：

~~~yaml
  disks:
    # 格式: 挂载点:保留的空间
    # 保留的空间: 单位字节，当磁盘剩余空间小于该值时将不会再在该磁盘上写入数据
    - /data0:536870912
    - /data1:536870912
~~~

~~~sh
helm upgrade -i cubefs -n cubefs . --create-namespace -f values.yaml
~~~

触发datanode pod重启：

~~~sh
kubectl delete po -n cubefs -l app.kubernetes.io/component=datanode
~~~

查看集群状态：

~~~sh
cfs-cli cluster stat 
~~~

### 基于主机的扩容

基于主机的扩容，需要通过添加datanode节点来完成。  

1. 添加一个新节点（k8s层面先加上），已有节点可以忽略

2. 在新节点上添加和当前配置、数量、大小一样的硬盘，并挂载

3. 在新节点上打`component.cubefs.io/datanode=enabled`标签即可:

   ~~~sh 
   kubectl label node xxx component.cubefs.io/datanode=enabled
   ~~~

## CubeFS对象存储

程序直接连接到存储平台对文件读写操作，不需要挂载、不需要创建PV、PVC。

### 对象存储基本使用

要测试对象存储，可以自己写程序，或者用一些对象存储客户端工具。CubeFS自己没没有提供对象存储的客户端工具，得用别的。

下载Minio对象存储客户端：（Minio也是提供对象存储的平台，但是只提供对象存储。但是不论使用哪个平台，协议都是s3。）

~~~sh
curl https://dl.minio.org.cn/client/mc/release/linux-amd64/mc --create-dirs -o /usr/local/bin/mc
chmod +x /usr/local/bin/mc 
~~~

配置对象存储：添加 MinIO/S3 服务器

~~~sh
# host add test是user的name
# 对象存储的入口：objectnode-service的svc的clusterIP
# 后面是cubefs的user的access key和secret key。这其实就是对象存储的用户名和密码
mc alias set test http://10.104.157.128:1601 NSwS4hTkT43TW903 uY9Hg8IgyW2awnRF3XpaAK8Da91c8RG7
# 查看alias
mc ls test
~~~

> [!info] mc命令版本差异
> 1. **旧版本语法**：`mc config host add` 是旧版本的语法
> 2. **新版本语法**：`mc alias set` 是新版本的正确语法

创建桶：（创建桶的本质就是在cubeFS中创建了一个volume）

~~~sh
mc mb test/buckettest
~~~

查看桶：

~~~sh
mc ls test/
~~~

上传文件：

~~~sh
mc cp cubefs-3.5.0-linux-amd64.tar.gz test/buckettest/ 
# 上传文件夹(不会自动创建目录，需要指定子目录名称)
mc cp templates/ test/buckettest/templates -r
~~~

查看文件：

~~~sh
mc ls test/buckettest/ 
~~~

删除文件：

~~~sh
mc rm test/buckettest/cubefs-3.5.0-linux-amd64.tar.gz 
~~~

删除桶：

~~~sh
mc rb test/buckettest
~~~

删除服务器：

~~~sh
mc alias rm test
~~~

### 对象存储项目管理

为每个项目创建用户：

~~~sh
cfs-cli user create projecta
~~~

添加项目的host：（生产环境使用需要配置域名）

~~~sh
mc config host add projecta http://10.100.82.212:1601 sTnnilRm1YPuohs0 ayIjC5uZYdRmVRFYey8lDy73Whdg716l
~~~

这个项目可能会有很多微服务，这些微服务就共用同一套用户名密码。为每个微服务单独创建不同的桶。（共享数据的微服务就共用同一个桶）

~~~sh
mc mb projecta/appa
~~~

## CubeFS对接K8s

### 部署cubeFS csi

首先给需要使用cubeFS存储的节点打上CSI的标签（一般直接给所有节点打上标签即可）：

~~~sh
kubectl label node component.cubefs.io/csi=enabled --all
~~~

配置values，开启csi安装：

~~~yaml
component: 
  master: true
  datanode: true
  metanode: true
  objectnode: true
  client: false
  csi: true
~~~

执行安装：

~~~sh
helm upgrade -i cubefs -n cubefs . --create-namespace -f values.yaml
~~~

> [!bug] tolerations缩进问题
> 1. 如果values里面配置了tolerations，渲染模板会报错：
>    ~~~sh
>    Error: UPGRADE FAILED: YAML parse error on cubefs/templates/csi-controller-deployment.yaml: error converting YAML to JSON: yaml: line 21: did not find expected key
>       
>    Error: UPGRADE FAILED: YAML parse error on cubefs/templates/csi-node-daemonset.yaml: error converting YAML to JSON: yaml: line 21: did not find expected key
>    ~~~
>
>    cubefs/templates/csi-controller-deployment.yaml
>
>    cubefs/templates/csi-node-daemonset.yaml
>
>    这两个文件都有spec.tolerations字段的缩进问题
>
> 2. 用helm template输出报错的模板：
>
>    ~~~sh
>    helm template cubefs -n cubefs . -f values.yaml --debug > error-template.yaml
>    ~~~
>
> 3. 分析可知模板中的tolerations字段缩进有问题：
>
>    原始文件（错的）
>
>    ~~~yaml
>        {{- with .Values.csi.controller.nodeSelector }}
>          nodeSelector:
>    {{ toYaml . | indent 8 }}
>        {{- end }}
>          {{- with .Values.csi.controller.tolerations }}
>            tolerations:
>          {{ toYaml . | indent 8 }}
>    ~~~
>
>    改为正确缩进：
>
>    ~~~yaml
>        {{- with .Values.csi.controller.nodeSelector }}
>          nodeSelector:
>    {{ toYaml . | indent 8 }}
>        {{- end }}
>        {{- with .Values.csi.controller.tolerations }}
>          tolerations:
>    {{ toYaml . | indent 8 }}
>    ~~~
>
> 4. 改完之后可以成功安装
>
> 5. 在其他模板中又发现了更多缩进错误，我提了一个github issue：[Indent Error found in spec.tolerations for some templates - Issue #53](https://github.com/cubefs/cubefs-helm/issues/53)

### PV/PVC测试

创建pvc:

~~~yaml
apiVersion: v1 
kind: PersistentVolumeClaim 
metadata: 
  name: cubefs-test 
  namespace: default 
spec: 
  accessModes: 
    - ReadWriteMany # Once也可以，单节点读写
  resources: 
    requests: 
      storage: 1Gi
  storageClassName: cfs-sc 
  volumeMode: Filesystem
~~~

创建之后就能看到自动创建了PV。下面可以创建服务来挂载PVC：

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: cfs-csi-demo 
  namespace: default 
spec: 
  replicas: 1 
  selector: 
    matchLabels: 
      app: cfs-csi-demo-pod 
  template: 
    metadata: 
      labels: 
        app: cfs-csi-demo-pod 
    spec: 
      # 只有安装了CSI驱动的才可以挂载存储 
      nodeSelector: 
        component.cubefs.io/csi: enabled
      volumes: 
        - name: mypvc
          persistentVolumeClaim: 
            claimName: cubefs-test
      containers: 
        - name: cfs-csi-demo 
          image: registry.cn-beijing.aliyuncs.com/dotbalo/rabbitmq:3.6.12-management  
          imagePullPolicy: "IfNotPresent" 
          ports: 
            - containerPort: 15672 
              name: "http-server" 
          volumeMounts: 
            - mountPath: "/var/lib/rabbitmq" 
              name: mypvc 
~~~

### 在线扩容

支持不停机扩容，直接把PVC的request改大，等待一段时间就生效了。Pod是不会收到影响的。

~~~yaml
spec: 
  accessModes: 
  - ReadWriteMany 
  resources: 
    requests: 
      storage: 2Gi 
  storageClassName: cfs-sc 
~~~

### CubeFS为基础组件提供存储

#### mysql单实例

单实例手动创建PVC。如果是多实例就需要用集群模式或者主从模式，用helm或者Operator去部署，在模板里面直接写storageclass就行

~~~yaml
apiVersion: v1 
kind: PersistentVolumeClaim 
metadata: 
  name: mysql 
  namespace: default 
spec: 
  resources: 
    requests: 
      storage: 1Gi 
  volumeMode: Filesystem 
  storageClassName: cfs-sc 
  accessModes: 
    - ReadWriteOnce
---
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: mysql 
  namespace: default 
spec: 
  replicas: 1 
  selector: 
    matchLabels: 
      app: mysql 
  strategy:
    type: Recreate # 不能用滚动更新，因为。两个mysql不能同时使用一块存储。
  template: 
    metadata: 
      labels: 
        app: mysql 
      annotations: 
        app: mysql 
    spec: 
      volumes: 
        - name: data 
          persistentVolumeClaim: 
            claimName: mysql 
      containers: 
        - name: mysql 
          image: registry.cn-beijing.aliyuncs.com/dotbalo/mysql:8.0.20 
          ports: 
            - name: tcp-3306 
              containerPort: 3306 
              protocol: TCP 
          volumeMounts: 
            - name: data 
              mountPath: /var/lib/mysql 
          env: 
            - name: MYSQL_ROOT_PASSWORD 
              value: mysql
~~~

### CubeFS为大模型提供存储

CubeFS对AI训练、模型存储及分发、IO加速等需求做了专门优化。所以可以直接把CubeFS作为大模型的数据存储底座。 

很多位置去启动大模型服务，可以共享同一个大模型的存储。

#### ollama

~~~yaml
apiVersion: v1 
kind: PersistentVolumeClaim 
metadata: 
  name: ollama-data 
  namespace: default 
spec: 
  resources: 
    requests: 
      storage: 10Gi
  volumeMode: Filesystem 
  storageClassName: cfs-sc 
  accessModes: 
  - ReadWriteMany 
---
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: ollama 
  namespace: default 
spec: 
  selector: 
    matchLabels: 
      app: ollama 
  replicas: 1 
  template: 
    metadata: 
      labels: 
        app: ollama 
      annotations: 
        app: ollama 
    spec: 
      volumes: 
      - name: data 
        persistentVolumeClaim: 
          claimName: ollama-data 
          readonly: false 
      containers: 
      - name: ollama 
        image: registry.cn-beijing.aliyuncs.com/dotbalo/ollama
        imagePullPolicy: IfNotPresent 
        volumeMounts: 
        - name: data 
          mountPath: /data/models 
          readonly: false 
        env: 
        - name: OLLAMA_MODELS 
          value: /data/models 
~~~

部署完成后进入pod下载模型`ollama pull deepseek-r1:1.5b`

下载完成之后启动模型：`ollama run deepseek-r1:1.5b`
