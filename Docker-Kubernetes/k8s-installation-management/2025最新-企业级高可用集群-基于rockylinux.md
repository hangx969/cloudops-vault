---
title: 2025最新-企业级高可用集群-基于rockylinux
tags:
  - kubernetes
  - k8s-installation
  - 高可用
  - rockylinux
aliases:
  - 企业级高可用集群
  - kubeadm高可用安装
---

# 2025最新-企业级高可用集群-基于rockylinux


## 企业级高可用集群架构设计

### 架构图

![image-20251004212113888](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202510042121022.png)

1. 控制节点:

   - 只要上了生产,一定就是3个,不能是1个。因为后期扩容控制节点会非常麻烦甚至无法扩容。
   - 3 Master已经可以应对95%以上的场景,足够用了,无需再多。
   - 如果前期负载小(10-20个微服务),宁愿没有工作节点,直接部署在master上,后期负载上来再扩工作节点。

2. 控制节点前端负载均衡:

   - 软件负载均衡,可以用keepalived+haproxy/nginx的方案

   - 有硬件支持的话用F5代理,直接代理apiserver的6443端口负载均衡
   - 在公有云上一般不需要keepalived和haproxy,直接用公有云的SLB

3. 工作节点:一开始上3-5个,够用,后面负载高了随时动态扩容。

### 控制节点资源配置

| 工作节点数量  | 控制节点数量 | 控制节点配置    | Etcd节点配置                  | Master & Etcd                                  | 备注                                                                            |
| ------- | ------ | --------- | ------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------------- |
| 0-100   | 3      | /         | /                         | 8C + 32G + 128G SSD<br />或者:4C + 8G + 128G SSD | 1. Etcd和Master部署到一起<br />2. SSD必备,etcd对硬盘性能要求非常高。对空间要求不高(2万个pod大概也就占20G etcd) |
| 100-250 | 3      | /         | /                         | 16C + 32G + 128G SSD                           | 1. 能支撑2万个pod级别 <br />2. Etcd和Master部署到一起也是可以的                                 |
| 250-500 | 3      | 16C + 32G | 8C + 32G + (512G SSD * 5) |                                                | 1. Etcd和Master分开部署<br />2. Etcd拆成5个节点,跨机房部署,容忍挂2个节点                           |

### 工作节点资源配置

1. 可以理解为无状态的,数量、CPU、内存可以随时扩容。
2. 推荐单节点配置:(8C + 32G) / (16C + 64G)
3. 最低节点数:3个。两个风险太高:如果一个挂了,pod全飘到另一个节点上扛不住。

总之,生产环境搭建集群,最低需要3主3从6个节点。

### 磁盘划分

#### 控制节点

| 根分区(100G) | Etcd数据盘(100G NVME SSD) | 数据盘(500G SSD)                                           |
| -------------- | --------------------------- | ------------------------------------------------------------ |
| /              | /var/lib/etcd               | /data, /var/lib/kubelet, /var/lib/containers                 |
| 存储系统数据   | 需要高性能                  | 1. 可以把磁盘分成三个区,分别挂到三个目录<br />2. 也可以只挂到/data下,创建两个目录软链到kubelet和containers【推荐】 |

#### 工作节点

| 根分区(100G) | 数据盘(500G SSD)                                           |
| -------------- | ------------------------------------------------------------ |
| /              | /data, /var/lib/kubelet, /var/lib/containers                 |
|                | 只挂到/data下,创建两个目录软链到kubelet和containers【推荐】 |

### 网络划分

网段划分非常重要,属于软件层面的划分,如果划分不合适的话可能需要重建集群。

下面三个网段不能有任何冲突。

|      | 节点网段                         | Service网段                                                  | Pod网段                  |
| ---- | -------------------------------- | ------------------------------------------------------------ | ------------------------ |
| 网段 | 192.168.40.0/24                  | 10.96.0.0/16                                                 | 172.16.0.0/16            |
| 来源 | 局域网分配的                     | CNI插件划分的                                                | controller-manager划分的 |
| 备注 | 一般节点网段都是已经提前划分好的 | 保留IP:<br />1. CoreDNS Service IP:**10.96.0.10** (svc网段的第10个IP)<br />2. API Server Service IP:**10.96.0.1**(svc网段的第1个IP) |                          |

注意:

1. 上面三个内网网段可以互相替换。

   - 假如节点网段已经分配172.16,那么可以Pod网段给192.168,svc网段给10.96
   - 假如节点网段已经占了192.168和172.16,那么只能用10.96划分给pod和svc,可以用子网掩码来划分两个子网。一般pod会比svc的ip需求多一些。直接问大模型怎么划分。

2. 注意内网网段是固定有限的:

   > 1. **A类私有地址段**:`10.0.0.0/8`
   >    - IP范围:10.0.0.0 - 10.255.255.255
   >    - 子网掩码:255.0.0.0
   >    - 可用地址数:约1677万个
   > 2. **B类私有地址段**:`172.16.0.0/12`
   >    - IP范围:172.16.0.0 - 172.31.255.255
   >    - 子网掩码:255.240.0.0
   >    - 可用地址数:约104万个
   > 3. **C类私有地址段**:`192.168.0.0/16`
   >    - IP范围:192.168.0.0 - 192.168.255.255
   >    - 子网掩码:255.255.0.0
   >    - 可用地址数:约6.5万个

   所以192.0.0.0/16这样的网段,是包含了一部分公网IP的,不能用作k8s网段,会和公网IP冲突。

3. 对于keepalived的VIP:

   - 不能和公司内网IP重复,需要用一个不存在的,并且属于局域网内的IP。提前ping一下,ping不通才能用。
   - 私有云上搭建需要问管理员是否支持VIP。(比如某些Openstack集群可能不支持VIP)

## 企业级高可用架构落地实战

### 节点准备

1. 实验用,准备3台VMWare VM作为Master,每台:
   - 4C4G
   - 一块自带的40G硬盘
   - 加一块10G盘,给etcd用
   - 加一块40G盘,作为数据盘

2. 准备2台VM作为Node,每台:
   - 4C4G
   - 一块自带的40G盘
   - 加一块40G盘作为数据盘

```sh
fdisk -l # 查看新增磁盘
```

### 实验环境规划

| 主机名  | IP                              | 备注                                                         |
| ------- | ------------------------------- | ------------------------------------------------------------ |
| m01~m03 | 192.168.40.190 ~ 192.168.40.192 | master节点*3                                                 |
| n01~n03 | 192.168.40.193 ~ 192.168.40.195 | worker节点*3                                                 |
| /       | 192.168.40.199                  | keepalived VIP<br />注:<br />1. 不能和公司内网IP重复,需要用一个不存在的,并且属于局域网内的IP。提前ping一下,ping不通才能用。<br />2. 私有云上搭建需要问管理员是否支持VIP |

| 配置信息    | 备注                                                         |
| ----------- | ------------------------------------------------------------ |
| OS Version  | Rocky Linux 9                                                |
| containerd  | latest                                                       |
| kubernetes  | 1.17+都适用。<br />注意:生产环境建议用小版本>5的,比如1.28.5以后才建议用于生产环境 |
| Pod网段     | 172.16.0.0/16                                                |
| Service网段 | 10.96.0.0/16                                                 |

### 节点磁盘挂载

实验中都用fdisk直接分区,也可以用LVM创建逻辑卷来挂载。

#### 挂载etcd数据盘

Master节点才需要这个配置

```sh
mkdir -p /var/lib/etcd
# etcd盘可以直接新建分区划给etcd
fdisk /dev/sd
n
p
w

# 格式化
mkfs.xfs /dev/sd

# 持久挂载
blkid /dev/sd

tee -a /etc/fstab <<'EOF'
UUID=xxx    /var/lib/etcd     xfs    defaults    0 0
EOF

systemctl daemon-reload && mount -a
df -Th
```

#### 挂载data盘

Master和Worker节点都要配置

```sh
mkdir -p /data
fdisk /dev/sd
n
p
w

# 格式化
mkfs.xfs /dev/sd

# 持久挂载
blkid /dev/sd

tee -a /etc/fstab <<'EOF'
UUID=xxx    /data    xfs    defaults    0 0
EOF

systemctl daemon-reload && mount -a
df -Th
```

创建kubelet和containers目录和软链:

```sh
mkdir -p /data/kubelet
mkdir -p /data/containers
ln -s /data/kubelet /var/lib/kubelet
ln -s /data/containers /var/lib/containers
```

### 基本配置

所有节点更改主机名:

```sh
hostnamectl set-hostname m01
```

所有节点更改hosts

```sh
tee -a /etc/hosts <<'EOF'
192.168.40.190   m01
192.168.40.191   m02
192.168.40.192   m03
192.168.40.193   n01
192.168.40.194   n02
192.168.40.195   n03
EOF
```

所有节点配置默认yum源:

```sh
sed -e 's|^mirrorlist=|#mirrorlist=|g' \
    -e 's|^#baseurl=http://dl.rockylinux.org/$contentdir|baseurl=https://mirrors.aliyun.com/rockylinux|g' \
    -i.bak \
    /etc/yum.repos.d/rocky-*.repo

dnf makecache
yum makecache
```

安装epel源并替换为清华epel源:

```sh
dnf install yum-utils
dnf install https://mirrors.tuna.tsinghua.edu.cn/epel/epel-release-latest-9.noarch.rpm
dnf install https://mirrors.tuna.tsinghua.edu.cn/epel/epel-next-release-latest-9.noarch.rpm
```

```sh
sed -e 's|^metalink=|#metalink=|g' \
    -e 's|^#baseurl=|baseurl=|g' \
    -e 's|https\?://download\.fedoraproject\.org/pub/epel|https://mirrors.tuna.tsinghua.edu.cn/epel|g' \
    -e 's|https\?://download\.example/pub/epel|https://mirrors.tuna.tsinghua.edu.cn/epel|g' \
    -i.bak /etc/yum.repos.d/epel{,-testing}.repo

# 禁用 epel-cisco-openh264.repo
sed -i "s/enabled=1/enabled=0/g" /etc/yum.repos.d/epel-cisco-openh264.repo

# 清除并重建缓存
dnf clean all
dnf makecache
```

> [!info] 由于无法同步,所有 EPEL 镜像站都不包含 EPEL Cisco OpenH264 仓库(epel-cisco-openh264.repo),如果不需要可手动将其改为 enabled=0。
>
> 参考文档:[在Rocky Linux 9上启用EPEL和Remi仓库](https://www.rockylinux.cn/notes/zai-rocky-linux-9-shang-qi-yong-epel-he-remi-cang-ku.html)

所有节点安装基本软件包:

```sh
yum update -y
yum install -y yum-utils device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo libaio-devel vim ncurses-devel autoconf automake epel-release openssh-server telnet coreutils iputils iproute nmap-ncat jq psmisc git bash-completion rsyslog
```

所有节点关闭防火墙、selinux、swap、dnsmasq,开启rsyslog:

```sh
systemctl disable --now firewalld
systemctl disable --now dnsmasq

setenforce 0
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/sysconfig/selinux

systemctl enable --now rsyslog

swapoff -a && sysctl -w vm.swappiness=0
sed -ri '/^[^#]*swap/s@^@#@' /etc/fstab
systemctl daemon-reload && mount -a
```

所有节点安装ntpdate:(实际生产使用中发现chrony没有ntpdate可靠)

```sh
dnf install -y epel-release
dnf config-manager --set-enabled epel
dnf install ntpsec
```

所有节点同步时间并配置上海时区:

```sh
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
echo 'Asia/Shanghai' > /etc/timezone
ntpdate time2.aliyun.com

# 加入到crontab
crontab -e
*/5 * * * * /usr/sbin/ntpdate time2.aliyun.com
```

所有节点配置limit:

```sh
ulimit -SHn 65535
tee -a /etc/security/limits.conf <<'EOF'
* soft nofile 65536
* hard nofile 131072
* soft nproc 65535
* hard nproc 655350
* soft memlock unlimited
* hard memlock unlimited
EOF
```

m01免密登录其他节点(安装过程中的各种配置文件均在m01上操作),集群管理也在m01上操作

```sh
ssh-keygen -t rsa
for i in m01 m02 m03 n01 n02 n03;do ssh-copy-id -i .ssh/id_rsa.pub $i;done
```

### 内核优化

所有节点安装ipvsadm:

```sh
yum install -y ipvsadm ipset sysstat conntrack libseccomp
```

所有节点配置ipvs模块:

```sh
modprobe -- ip_vs
modprobe -- ip_vs_rr
modprobe -- ip_vs_wrr
modprobe -- ip_vs_sh
modprobe -- nf_conntrack
```

所有节点创建/etc/modules-load.d/ipvs.conf,并配置开机自动加载:

```sh
tee /etc/modules-load.d/ipvs.conf <<'EOF'
ip_vs
ip_vs_lc
ip_vs_wlc
ip_vs_rr
ip_vs_wrr
ip_vs_lblc
ip_vs_lblcr
ip_vs_dh
ip_vs_sh
ip_vs_fo
ip_vs_nq
ip_vs_sed
ip_vs_ftp
nf_conntrack
ip_tables
ip_set
xt_set
ipt_set
ipt_rpfilter
ipt_REJECT
ipip
EOF
```

```sh
systemctl enable --now systemd-modules-load.service
# 如有报错可以忽略
```

所有节点内核优化配置:【针对4C4G虚拟机】

```sh
cat <<EOF > /etc/sysctl.d/k8s.conf
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
fs.may_detach_mounts = 1
net.ipv4.conf.all.route_localnet = 1
vm.overcommit_memory = 1
vm.panic_on_oom = 0
fs.inotify.max_user_watches = 89100
fs.file-max = 52706963
fs.nr_open = 52706963
net.netfilter.nf_conntrack_max = 2310720

net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_probes = 3
net.ipv4.tcp_keepalive_intvl = 15
net.ipv4.tcp_max_tw_buckets = 36000
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_max_orphans = 327680
net.ipv4.tcp_orphan_retries = 3
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 16384
net.ipv4.tcp_timestamps = 0
net.core.somaxconn = 16384
EOF
```

加载新参数:

```sh
modprobe br_netfilter
modprobe nf_conntrack
sysctl --system
reboot
# 检查内核模块是否加载
lsmod | grep --color=auto -e ip_vs -e nf_conntrack
```

### 高可用组件安装

> [!warning] 注意
> 1. 如果安装的不是高可用集群,不需要安装haproxy和keepalived
> 2. 公有云上自建集群,用公有云的SLB服务即可代替haproxy和keepalived。因为公有云大多数不支持keepalived VIP漂移

所有master节点上安装:

```sh
yum install -y haproxy keepalived
```

#### 配置haproxy

所有master节点配置haproxy:

```sh
mkdir /etc/haproxy
# 清空原配置,添加新配置
tee /etc/haproxy/haproxy.cfg <<'EOF'
global
  maxconn 2000
  ulimit-n 16384
  log 127.0.0.1 local0 err
  stats timeout 30s
defaults
  log global
  mode http
  option httplog
  timeout connect 5000
  timeout client 50000
  timeout server 50000
  timeout http-request 15s
  timeout http-keep-alive 15s

frontend k8s-master
  bind 0.0.0.0:16443
  bind 127.0.0.1:16443
  mode tcp
  option tcplog
  tcp-request inspect-delay 5s
  default_backend k8s-master

backend k8s-master
  mode tcp
  option tcplog
  option tcp-check
  balance roundrobin
  default-server inter 10s downinter 5s rise 2 fail 2 slowstart 60s maxconn 250 maxqueue 256 weight 100
  server k8s-master01  192.168.40.190:6443  check
  server k8s-master02  192.168.40.191:6443  check
  server k8s-master03  192.168.40.192:6443  check
EOF
```

> 注意这段配置:
>
> server k8s-master01  192.168.40.190:6443  check
> server k8s-master02  192.168.40.191:6443  check
> server k8s-master03  192.168.40.192:6443  check
>
> 只关心实际IP地址,实际主机名不是k8s-master01也没关系,只要IP地址正确即可

#### 配置keepalived

注意修改三个字段:

```sh
interface ens160 # 主机网卡名
mcast_src_ip 192.168.40.130 # 当前节点的IP
virtual_ipaddress {
    192.168.40.199 # VIP的地址
}
```

##### Master01配置

```sh
mkdir /etc/keepalived
# 清空原配置,添加新配置
tee /etc/keepalived/keepalived.conf <<'EOF'
! Configuration File for keepalived
global_defs {
    router_id LVS_DEVEL
    script_user root
    enable_script_security
}
vrrp_script chk_apiserver {
    script "/etc/keepalived/check_apiserver.sh"
    interval 5
    weight -5
    fall 2
    rise 1
}
vrrp_instance VI_1 {
    state MASTER
    interface ens160
    mcast_src_ip 192.168.40.190
    virtual_router_id 51
    priority 101
    advert_int 2
    authentication {
        auth_type PASS
        auth_pass K8SHA_KA_AUTH
    }
    virtual_ipaddress {
        192.168.40.199
    }
    track_script {
        chk_apiserver
    }
}
EOF
```

##### Master02配置

```sh
mkdir /etc/keepalived
# 清空原配置,添加新配置
tee /etc/keepalived/keepalived.conf <<'EOF'
! Configuration File for keepalived
global_defs {
    router_id LVS_DEVEL
    script_user root
    enable_script_security
}
vrrp_script chk_apiserver {
    script "/etc/keepalived/check_apiserver.sh"
    interval 5
    weight -5
    fall 2
    rise 1
}
vrrp_instance VI_1 {
    state MASTER
    interface ens160
    mcast_src_ip 192.168.40.191
    virtual_router_id 51
    priority 101
    advert_int 2
    authentication {
        auth_type PASS
        auth_pass K8SHA_KA_AUTH
    }
    virtual_ipaddress {
        192.168.40.199
    }
    track_script {
        chk_apiserver
    }
}
EOF
```

##### Master03配置

```sh
mkdir /etc/keepalived
# 清空原配置,添加新配置
tee /etc/keepalived/keepalived.conf <<'EOF'
! Configuration File for keepalived
global_defs {
    router_id LVS_DEVEL
    script_user root
    enable_script_security
}
vrrp_script chk_apiserver {
    script "/etc/keepalived/check_apiserver.sh"
    interval 5
    weight -5
    fall 2
    rise 1
}
vrrp_instance VI_1 {
    state MASTER
    interface ens160
    mcast_src_ip 192.168.40.192
    virtual_router_id 51
    priority 101
    advert_int 2
    authentication {
        auth_type PASS
        auth_pass K8SHA_KA_AUTH
    }
    virtual_ipaddress {
        192.168.40.199
    }
    track_script {
        chk_apiserver
    }
}
EOF
```

##### 健康检查文件

所有Master节点添加keepalived健康检查文件:

```sh
tee /etc/keepalived/check_apiserver.sh <<'EOF'
#!/bin/bash
err=0
for k in $(seq 1 3)
do
    check_code=$(pgrep haproxy)
    if [[ $check_code == "" ]]; then
        err=$(expr $err + 1)
        sleep 1
        continue
    else
        err=0
        break
    fi
done

if [[ $err != "0" ]]; then
    echo "systemctl stop keepalived"
    /usr/bin/systemctl stop keepalived
    exit 1
else
    exit 0
fi
EOF
```

添加权限:

```sh
chmod +x /etc/keepalived/check_apiserver.sh
```

#### 启动服务

所有Master节点启动服务

```sh
systemctl daemon-reload
systemctl enable --now haproxy
systemctl enable --now keepalived
```

#### 测试VIP

所有Master和Worker节点测试VIP:

```sh
# ping必须全通
ping 192.168.40.199 -c 4
# telnet端口必须全通:出现 ] 说明是通的
telnet 192.168.40.199 16443
```

> [!warning] 如果ping不通且telnet没有出现 ] ,则认为VIP不通,不可继续安装
> 需要排查keepalived的问题,比如防火墙和selinux,haproxy和keepalived的状态,监听端口等。排查步骤:
>
> 1.	确认VIP是否正确
> 2.	所有节点查看防火墙状态必须为disable和inactive:systemctl status firewalld
> 3.	所有节点查看selinux状态,必须为disable:getenforce
> 4.	master节点查看haproxy和keepalived状态:systemctl status keepalived haproxy
> 5.	master节点查看监听端口:netstat -lntp
>
> 如果以上都没有问题,需要确认:
>
> 1.	是否是公有云机器
> 2.	是否是私有云机器(类似OpenStack)
> 3.	上述公有云一般都是不支持keepalived,私有云可能也有限制,需要和自己的私有云管理员咨询

#### 快照

完成keepalived测试之后,可以把所有VM关机拍快照。

### Runtime安装

如果安装的版本低于1.24,选择Docker和Containerd均可,高于1.24建议选择Containerd作为Runtime,不再推荐使用Docker作为Runtime。

#### 安装docker和containerd

所有节点安装docker和containerd:

```sh
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
yum clean all && yum makecache
yum install docker-ce containerd -y
```

【可选】启动docker:(可以无需启动Docker,只需要配置和启动Containerd即可)

```sh
systemctl enable docker --now
# 配置docker镜像加速器,k8s所有节点均按照以下配置
tee /etc/docker/daemon.json <<'EOF'
{
 "registry-mirrors":["https://docker.m.daocloud.io"]
}
EOF
#重启docker:
systemctl daemon-reload && systemctl restart docker && systemctl status docker
```

#### 配置containerd

1. 首先配置Containerd所需的模块(所有节点):

```sh
cat <<EOF | tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF
```

2. 所有节点加载模块:

```sh
modprobe -- overlay
modprobe -- br_netfilter
```

3. 所有节点,配置Containerd所需的内核:

```sh
cat <<EOF | tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF
```

4. 所有节点加载内核:

```sh
sysctl --system
```

5. 所有节点生成containerd配置文件:

```sh
mkdir -p /etc/containerd
containerd config default | tee /etc/containerd/config.toml
```

6. 修改containerd配置的pause镜像和Cgroup:

```sh
sed -i 's#SystemdCgroup = false#SystemdCgroup = true#g' /etc/containerd/config.toml
sed -i 's#k8s.gcr.io/pause#registry.cn-hangzhou.aliyuncs.com/google_containers/pause#g'  /etc/containerd/config.toml
sed -i 's#registry.gcr.io/pause#registry.cn-hangzhou.aliyuncs.com/google_containers/pause#g'  /etc/containerd/config.toml
sed -i 's#registry.k8s.io/pause#registry.cn-hangzhou.aliyuncs.com/google_containers/pause#g'  /etc/containerd/config.toml
```

7. 【可选】如果有连接harbor的需求,更改配置文件的这一部分:

```toml
    [plugins."io.containerd.grpc.v1.cri".registry]
      config_path = ""

      [plugins."io.containerd.grpc.v1.cri".registry.auths]

      [plugins."io.containerd.grpc.v1.cri".registry.configs]
        [plugins."io.containerd.grpc.v1.cri".registry.configs."harbor.hanxux.local".tls]
            insecure_skip_verify = true
            ca_file = ""
            cert_file = ""
            key_file = ""
        [plugins."io.containerd.grpc.v1.cri".registry.configs."harbor.hanxux.local".auth]
            username = "admin"
            password = "Harbor12345"

      [plugins."io.containerd.grpc.v1.cri".registry.headers]

      [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
         [plugins."io.containerd.grpc.v1.cri".registry.mirrors."harbor.hanxux.local"]
            endpoint = ["http://harbor.hanxux.local"]
          [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
             endpoint = ["https://docker.m.daocloud.io"]
```

8. 所有节点启动Containerd,并配置开机自启动:

```sh
systemctl daemon-reload
systemctl enable --now containerd
```

9. 【可选】`crictl`是一个命令行工具,用来验证 CRI 兼容性。若报错没有安装 `crictl`,可以执行:

```sh
VERSION="1.25.0"
curl -L -o /usr/local/bin/crictl "https://github.com/kubernetes-sigs/cri-tools/releases/download/v${VERSION}/crictl-v${VERSION}-linux-amd64.tar.gz"
tar zxvf /usr/local/bin/crictl -C /usr/local/bin
chmod +x /usr/local/bin/crictl
```

10. 所有节点配置crictl客户端连接的运行时位置:

```sh
cat > /etc/crictl.yaml <<EOF
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 10
debug: false
EOF
```

```sh
systemctl restart containerd
# 验证配置
containerd --version
crictl info
```

11. 检查containerd插件情况

```sh
ctr plugin ls
# 下面这两项都要是ok才行
io.containerd.snapshotter.v1          overlayfs                linux/amd64    ok
io.containerd.grpc.v1                 cri                      linux/amd64    ok
```

### K8s组件安装

1. 所有节点配置源:==注意这里需要更改k8s版本号,只用写minor version,不用写patch版本==

```sh
cat <<EOF | tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.33/rpm/
enabled=1
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.33/rpm/repodata/repomd.xml.key
EOF
```

2. 所有节点安装kubelet、kubectl、kubeadm:==注意版本需要对应k8s版本号==

```sh
yum clean all && yum makecache
yum install kubeadm-1.33* kubelet-1.33* kubectl-1.33* -y
```

3. 所有节点开机自启动kubelet:(由于还未初始化,没有kubelet的配置文件,此时kubelet无法启动,无需关心)

```sh
systemctl daemon-reload
systemctl enable --now kubelet
```

4. 【离线安装方法】如果安装报找不到指定的源,可以按照下面的网址,下载指定版本的rpm文件,传到linux机器:

   - [阿里云k8s仓库](https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.33)
   - [阿里云k8s rpm x86_64](https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.33/rpm/x86_64/?spm=a2c6h.25603864.0.0.7ced7af3l8FcI0)

   基于上面下载到linux机器的rpm文件,手动安装:`rpm -ivh ./*`

### 集群初始化

1. 以下操作在Master01节点执行。集群初始化只在master01执行一遍,其余节点都是join过来的。

```sh
vim kubeadm-config.yaml
```

高可用Master节点配置:([v1beta4参数说明](https://kubernetes.io/docs/reference/config-api/kubeadm-config.v1beta4/))

```yaml
apiVersion: kubeadm.k8s.io/v1beta4
kind: InitConfiguration
bootstrapTokens:
- groups:
  - system:bootstrappers:kubeadm:default-node-token
  token: <bootstrap-token>
  ttl: 24h0m0s
  usages:
  - signing
  - authentication
localAPIEndpoint:
  advertiseAddress: 192.168.181.130 # master01地址
  bindPort: 6443
nodeRegistration:
  criSocket: unix:///var/run/containerd/containerd.sock
  imagePullPolicy: IfNotPresent
  imagePullSerial: true
  name: m01 # hostname
  taints:
  - effect: NoSchedule
    key: node-role.kubernetes.io/control-plane
timeouts:
  controlPlaneComponentHealthCheck: 4m0s
  discovery: 5m0s
  etcdAPICall: 2m0s
  kubeletHealthCheck: 4m0s
  kubernetesAPICall: 1m0s
  tlsBootstrap: 5m0s
  upgradeManifests: 5m0s
---
apiServer:
  certSANs:
  - 192.168.40.199 # VIP
apiVersion: kubeadm.k8s.io/v1beta4
caCertificateValidityPeriod: 876000h0m0s
certificateValidityPeriod: 876000h0m0s
certificatesDir: /etc/kubernetes/pki
clusterName: kubernetes
controlPlaneEndpoint: 192.168.40.199:16443 # VIP
controllerManager: {}
dns: {}
encryptionAlgorithm: RSA-2048
etcd:
  local:
    dataDir: /var/lib/etcd # 设置为提前挂载好的磁盘位置
imageRepository: registry.cn-hangzhou.aliyuncs.com/google_containers
kind: ClusterConfiguration
kubernetesVersion: v1.33.4 # 要与kubeadm version的patch版本保持一致
networking:
  dnsDomain: cluster.local
  podSubnet: 172.16.0.0/16
  serviceSubnet: 10.96.0.0/16
proxy: {}
scheduler: {}
---
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: ipvs
---
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd
```

2. 更新kubeadm文件,把旧版本格式的 kubeadm 配置文件转换成当前版本接受的格式

```sh
kubeadm config migrate --old-config kubeadm-config.yaml --new-config kubeadm-config-new.yaml
# 格式转换完,这个字段会被改。进入kubeadm-config-new.yaml文件,修改这个字段:
timeouts:
  controlPlaneComponentHealthCheck: 4m0s
```

3. 复制到其他master节点:==其他节点配置文件不需要更改,包括IP地址也不需要更改==

```sh
for i in m02 m03; do scp kubeadm-config-new.yaml $i:/root/; done
```

4. 所有Master节点提前下载镜像,可以节省初始化时间:

```sh
kubeadm config images pull --config /root/kubeadm-config-new.yaml
```

5. 在Master01节点初始化集群,初始化以后会在/etc/kubernetes目录下生成对应的证书和配置文件,之后其他Master节点加入Master01即可:==初始化操作仅在master01节点执行,其它任何节点勿操作==

```sh
# 高可用master节点初始化
kubeadm init --config /root/kubeadm-config-new.yaml --upload-certs --ignore-preflight-errors=SystemVerification
# 单master节点初始化
kubeadm init --config /root/kubeadm-config-new.yaml --ignore-preflight-errors=SystemVerification
```

6. 初始化成功以后,控制台输出里面,会产生两个join命令,一个是给control plane用,一个是给data node用:

```sh
kubeadm join 192.168.40.199:16443 --token xxx \
--discovery-token-ca-cert-hash sha256:xxx \
--control-plane --certificate-key xxx

kubeadm join 192.168.40.199:16443 --token xxx \
	--discovery-token-ca-cert-hash xxx
```

#### 加入节点

如果join命令没保存,在master01运行:

```sh
kubeadm token create --print-join-command
```

1. 在Master02和03上运行join命令加入集群(用带--control-plane的join命令,后面加上--ignore-preflight-errors=SystemVerification)
2. 在Worker nodes上运行join命令加入集群(用短的join命令,后面加上--ignore-preflight-errors=SystemVerification)

#### 创建kubeconfig

admin.conf是集群的钥匙,安全起见最好是仅在这一台master上执行。如需在其他节点运行,需要拷贝admin.conf到对应节点。

```sh
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config

# 1. 设置kubectl的alias为k:
whereis kubectl ## kubectl: /usr/bin/kubectl
echo "alias k=/usr/bin/kubectl">>/etc/profile
source /etc/profile

# 2. 设置alias的自动补全:
source <(kubectl completion bash | sed 's/kubectl/k/g')

# 3. 解决每次启动k都会失效,要重新刷新环境变量(source /etc/profile)的问题:在~/.bashrc文件中添加以下代码:source /etc/profile
echo "source /etc/profile" >> ~/.bashrc

# 4. 给alias k也配置补全
tee -a ~/.bashrc <<'EOF'
alias k='kubectl'
complete -o default -F __start_kubectl k
source <(kubectl completion bash)
EOF

# 使命令生效
source ~/.bashrc
```

#### Worker node打标签

```sh
kubectl label nodes node01 node-role.kubernetes.io/work=worker
```

#### 问题排查

如果初始化失败,使用如下命令重置后再次初始化,命令如下(没有失败不要执行):

```sh
kubeadm reset -f ; ipvsadm --clear  ; rm -rf ~/.kube
```

如果多次尝试都是初始化失败,需要看系统日志,CentOS/RockyLinux日志路径:/var/log/messages,Ubuntu系列日志路径/var/log/syslog:

```sh
tail -f /var/log/messages | grep -v "not found"
```

经常出错的原因:

1.	Containerd的配置文件修改的不对,自行参考《安装containerd》小节核对。(一般伴有PLEG报错信息)
2.	kubeadm yaml配置问题,比如非高可用集群忘记修改16443端口为6443
3.	kubeadm yaml配置问题,三个网段有交叉,出现IP地址冲突
4.	VIP不通导致无法初始化成功,此时messages日志会有VIP超时的报错

### 安装网络插件Calico

1. 所有节点禁止NetworkManager管理Calico的网络接口,防止有冲突或干扰:

```sh
cat >>/etc/NetworkManager/conf.d/calico.conf<<EOF
[keyfile]
unmanaged-devices=interface-name:cali*;interface-name:tunl*;interface-name:vxlan.calico;interface-name:vxlan-v6.calico;interface-name:wireguard.cali;interface-name:wg-v6.cali
EOF

systemctl daemon-reload && systemctl restart NetworkManager
```

2. 从官网找到最新版calico的yaml链接(在manifest一栏中找到`Download the Calico networking manifest for the Kubernetes API datastore.`):[Calico安装文档](https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises#install-calico)

3. 下载yaml文件部署

```sh
# 修改calico.yaml中网卡名称
# - name: CLUSTER_TYPE
#   value: "k8s,bgp"
# 找到上面这一段,在它的下面添加网卡名称字段:(指定calico从ens33跨节点通信,不指定的话,会走lo的IP,没办法跨节点通信,也就没办法给pod划分IP)
- name: IP_AUTODETECTION_METHOD
  value: "interface=ens160"

kubectl apply -f calico.yaml
```

```sh
#测试网络访问
kubectl run busybox --image busybox:1.28  --image-pull-policy=IfNotPresent --restart=Never --rm -it -- sh
ping www.baidu.com
nslookup kubernetes.default.svc.cluster.local

# 注:如果是在Mac上运行的虚拟机,uname -m 看到是aarch64架构,busybox:1.28 arm64的镜像可能无法运行起来。换用alpine:latest就行:
kubectl run alpine --image alpine  --image-pull-policy=IfNotPresent --restart=Never --rm -it -- sh
ping www.baidu.com
nslookup kubernetes.default.svc.cluster.local
```

### 配置优化

#### 使用ipvs

将Kube-proxy改为ipvs模式,如果在初始化集群的时候注释了ipvs配置,所以需要自行修改一下:

```sh
# 在master01节点执行:
kubectl edit cm kube-proxy -n kube-system

mode: ipvs

# 更新Kube-Proxy的Pod:
kubectl patch daemonset kube-proxy -p "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"date\":\"`date +'%s'`\"}}}}}" -n kube-system

# 验证Kube-Proxy模式
curl 127.0.0.1:10249/proxyMode
```

#### 延长k8s证书

##### 查看证书过期时间

```sh
#在master节点上执行
openssl x509 -in /etc/kubernetes/pki/ca.crt -noout -text | grep -i Not
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -text | grep -i Not
```

##### 延长证书有效期的脚本

文件命名为:update-kubeadm-cert.sh

```sh
#!/bin/bash
set -o errexit
set -o pipefail
# set -o xtrace

log::err() {
  printf "[$(date +'%Y-%m-%dT%H:%M:%S.%N%z')]: \033[31mERROR: \033[0m$@\n"
}

log::info() {
  printf "[$(date +'%Y-%m-%dT%H:%M:%S.%N%z')]: \033[32mINFO: \033[0m$@\n"
}

log::warning() {
  printf "[$(date +'%Y-%m-%dT%H:%M:%S.%N%z')]: \033[33mWARNING: \033[0m$@\n"
}

check_file() {
  if [[ ! -r  ${1} ]]; then
    log::err "can not find ${1}"
    exit 1
  fi
}

# get x509v3 subject alternative name from the old certificate
cert::get_subject_alt_name() {
  local cert=${1}.crt
  check_file "${cert}"
  local alt_name=$(openssl x509 -text -noout -in ${cert} | grep -A1 'Alternative' | tail -n1 | sed 's/[[:space:]]*Address//g')
  printf "${alt_name}\n"
}

# get subject from the old certificate
cert::get_subj() {
  local cert=${1}.crt
  check_file "${cert}"
  local subj=$(openssl x509 -text -noout -in ${cert}  | grep "Subject:" | sed 's/Subject:/\//g;s/\,/\//;s/[[:space:]]//g')
  printf "${subj}\n"
}

cert::backup_file() {
  local file=${1}
  if [[ ! -e ${file}.old-$(date +%Y%m%d) ]]; then
    cp -rp ${file} ${file}.old-$(date +%Y%m%d)
    log::info "backup ${file} to ${file}.old-$(date +%Y%m%d)"
  else
    log::warning "does not backup, ${file}.old-$(date +%Y%m%d) already exists"
  fi
}

# generate certificate whit client, server or peer
# Args:
#   $1 (the name of certificate)
#   $2 (the type of certificate, must be one of client, server, peer)
#   $3 (the subject of certificates)
#   $4 (the validity of certificates) (days)
#   $5 (the x509v3 subject alternative name of certificate when the type of certificate is server or peer)
cert::gen_cert() {
  local cert_name=${1}
  local cert_type=${2}
  local subj=${3}
  local cert_days=${4}
  local alt_name=${5}
  local cert=${cert_name}.crt
  local key=${cert_name}.key
  local csr=${cert_name}.csr
  local csr_conf="distinguished_name = dn\n[dn]\n[v3_ext]\nkeyUsage = critical, digitalSignature, keyEncipherment\n"

  check_file "${key}"
  check_file "${cert}"

  # backup certificate when certificate not in ${kubeconf_arr[@]}
  # kubeconf_arr=("controller-manager.crt" "scheduler.crt" "admin.crt" "kubelet.crt")
  # if [[ ! "${kubeconf_arr[@]}" =~ "${cert##*/}" ]]; then
  #   cert::backup_file "${cert}"
  # fi

  case "${cert_type}" in
    client)
      openssl req -new  -key ${key} -subj "${subj}" -reqexts v3_ext \
        -config <(printf "${csr_conf} extendedKeyUsage = clientAuth\n") -out ${csr}
      openssl x509 -in ${csr} -req -CA ${CA_CERT} -CAkey ${CA_KEY} -CAcreateserial -extensions v3_ext \
        -extfile <(printf "${csr_conf} extendedKeyUsage = clientAuth\n") -days ${cert_days} -out ${cert}
      log::info "generated ${cert}"
    ;;
    server)
      openssl req -new  -key ${key} -subj "${subj}" -reqexts v3_ext \
        -config <(printf "${csr_conf} extendedKeyUsage = serverAuth\nsubjectAltName = ${alt_name}\n") -out ${csr}
      openssl x509 -in ${csr} -req -CA ${CA_CERT} -CAkey ${CA_KEY} -CAcreateserial -extensions v3_ext \
        -extfile <(printf "${csr_conf} extendedKeyUsage = serverAuth\nsubjectAltName = ${alt_name}\n") -days ${cert_days} -out ${cert}
      log::info "generated ${cert}"
    ;;
    peer)
      openssl req -new  -key ${key} -subj "${subj}" -reqexts v3_ext \
        -config <(printf "${csr_conf} extendedKeyUsage = serverAuth, clientAuth\nsubjectAltName = ${alt_name}\n") -out ${csr}
      openssl x509 -in ${csr} -req -CA ${CA_CERT} -CAkey ${CA_KEY} -CAcreateserial -extensions v3_ext \
        -extfile <(printf "${csr_conf} extendedKeyUsage = serverAuth, clientAuth\nsubjectAltName = ${alt_name}\n") -days ${cert_days} -out ${cert}
      log::info "generated ${cert}"
    ;;
    *)
      log::err "unknow, unsupported etcd certs type: ${cert_type}, supported type: client, server, peer"
      exit 1
  esac

  rm -f ${csr}
}

cert::update_kubeconf() {
  local cert_name=${1}
  local kubeconf_file=${cert_name}.conf
  local cert=${cert_name}.crt
  local key=${cert_name}.key

  # generate  certificate
  check_file ${kubeconf_file}
  # get the key from the old kubeconf
  grep "client-key-data" ${kubeconf_file} | awk {'print$2'} | base64 -d > ${key}
  # get the old certificate from the old kubeconf
  grep "client-certificate-data" ${kubeconf_file} | awk {'print$2'} | base64 -d > ${cert}
  # get subject from the old certificate
  local subj=$(cert::get_subj ${cert_name})
  cert::gen_cert "${cert_name}" "client" "${subj}" "${CAER_DAYS}"
  # get certificate base64 code
  local cert_base64=$(base64 -w 0 ${cert})

  # backup kubeconf
  # cert::backup_file "${kubeconf_file}"

  # set certificate base64 code to kubeconf
  sed -i 's/client-certificate-data:.*/client-certificate-data: '${cert_base64}'/g' ${kubeconf_file}

  log::info "generated new ${kubeconf_file}"
  rm -f ${cert}
  rm -f ${key}

  # set config for kubectl
  if [[ ${cert_name##*/} == "admin" ]]; then
    mkdir -p ~/.kube
    cp -fp ${kubeconf_file} ~/.kube/config
    log::info "copy the admin.conf to ~/.kube/config for kubectl"
  fi
}

cert::update_etcd_cert() {
  PKI_PATH=${KUBE_PATH}/pki/etcd
  CA_CERT=${PKI_PATH}/ca.crt
  CA_KEY=${PKI_PATH}/ca.key

  check_file "${CA_CERT}"
  check_file "${CA_KEY}"

  # generate etcd server certificate
  # /etc/kubernetes/pki/etcd/server
  CART_NAME=${PKI_PATH}/server
  subject_alt_name=$(cert::get_subject_alt_name ${CART_NAME})
  cert::gen_cert "${CART_NAME}" "peer" "/CN=etcd-server" "${CAER_DAYS}" "${subject_alt_name}"

  # generate etcd peer certificate
  # /etc/kubernetes/pki/etcd/peer
  CART_NAME=${PKI_PATH}/peer
  subject_alt_name=$(cert::get_subject_alt_name ${CART_NAME})
  cert::gen_cert "${CART_NAME}" "peer" "/CN=etcd-peer" "${CAER_DAYS}" "${subject_alt_name}"

  # generate etcd healthcheck-client certificate
  # /etc/kubernetes/pki/etcd/healthcheck-client
  CART_NAME=${PKI_PATH}/healthcheck-client
  cert::gen_cert "${CART_NAME}" "client" "/O=system:masters/CN=kube-etcd-healthcheck-client" "${CAER_DAYS}"

  # generate apiserver-etcd-client certificate
  # /etc/kubernetes/pki/apiserver-etcd-client
  check_file "${CA_CERT}"
  check_file "${CA_KEY}"
  PKI_PATH=${KUBE_PATH}/pki
  CART_NAME=${PKI_PATH}/apiserver-etcd-client
  cert::gen_cert "${CART_NAME}" "client" "/O=system:masters/CN=kube-apiserver-etcd-client" "${CAER_DAYS}"

  # restart etcd
  docker ps | awk '/k8s_etcd/{print$1}' | xargs -r -I '{}' docker restart {} || true
  log::info "restarted etcd"
}

cert::update_master_cert() {
  PKI_PATH=${KUBE_PATH}/pki
  CA_CERT=${PKI_PATH}/ca.crt
  CA_KEY=${PKI_PATH}/ca.key

  check_file "${CA_CERT}"
  check_file "${CA_KEY}"

  # generate apiserver server certificate
  # /etc/kubernetes/pki/apiserver
  CART_NAME=${PKI_PATH}/apiserver
  subject_alt_name=$(cert::get_subject_alt_name ${CART_NAME})
  cert::gen_cert "${CART_NAME}" "server" "/CN=kube-apiserver" "${CAER_DAYS}" "${subject_alt_name}"

  # generate apiserver-kubelet-client certificate
  # /etc/kubernetes/pki/apiserver-kubelet-client
  CART_NAME=${PKI_PATH}/apiserver-kubelet-client
  cert::gen_cert "${CART_NAME}" "client" "/O=system:masters/CN=kube-apiserver-kubelet-client" "${CAER_DAYS}"

  # generate kubeconf for controller-manager,scheduler,kubectl and kubelet
  # /etc/kubernetes/controller-manager,scheduler,admin,kubelet.conf
  cert::update_kubeconf "${KUBE_PATH}/controller-manager"
  cert::update_kubeconf "${KUBE_PATH}/scheduler"
  cert::update_kubeconf "${KUBE_PATH}/admin"
  set +e
  grep kubelet-client-current.pem /etc/kubernetes/kubelet.conf > /dev/null 2>&1
  kubelet_cert_auto_update=$?
  set -e
  if [[ "$kubelet_cert_auto_update" == "0" ]]; then
    log::warning "does not need to update kubelet.conf"
  else
    cert::update_kubeconf "${KUBE_PATH}/kubelet"
  fi

  # generate front-proxy-client certificate
  # use front-proxy-client ca
  CA_CERT=${PKI_PATH}/front-proxy-ca.crt
  CA_KEY=${PKI_PATH}/front-proxy-ca.key
  check_file "${CA_CERT}"
  check_file "${CA_KEY}"
  CART_NAME=${PKI_PATH}/front-proxy-client
  cert::gen_cert "${CART_NAME}" "client" "/CN=front-proxy-client" "${CAER_DAYS}"

  # restart apiserve, controller-manager, scheduler and kubelet
  docker ps | awk '/k8s_kube-apiserver/{print$1}' | xargs -r -I '{}' docker restart {} || true
  log::info "restarted kube-apiserver"
  docker ps | awk '/k8s_kube-controller-manager/{print$1}' | xargs -r -I '{}' docker restart {} || true
  log::info "restarted kube-controller-manager"
  docker ps | awk '/k8s_kube-scheduler/{print$1}' | xargs -r -I '{}' docker restart {} || true
  log::info "restarted kube-scheduler"
  systemctl restart kubelet
  log::info "restarted kubelet"
}

main() {
  local node_tpye=$1

  KUBE_PATH=/etc/kubernetes
  CAER_DAYS=36500

  # backup $KUBE_PATH to $KUBE_PATH.old-$(date +%Y%m%d)
  cert::backup_file "${KUBE_PATH}"

  case ${node_tpye} in
    etcd)
	  # update etcd certificates
      cert::update_etcd_cert
    ;;
    master)
	  # update master certificates and kubeconf
      cert::update_master_cert
    ;;
    all)
      # update etcd certificates
      cert::update_etcd_cert
      # update master certificates and kubeconf
      cert::update_master_cert
    ;;
    *)
      log::err "unknow, unsupported certs type: ${cert_type}, supported type: all, etcd, master"
      printf "Documentation:
  example:
    '\033[32m./update-kubeadm-cert.sh all\033[0m' update all etcd certificates, master certificates and kubeconf
      /etc/kubernetes
      ├── admin.conf
      ├── controller-manager.conf
      ├── scheduler.conf
      ├── kubelet.conf
      └── pki
          ├── apiserver.crt
          ├── apiserver-etcd-client.crt
          ├── apiserver-kubelet-client.crt
          ├── front-proxy-client.crt
          └── etcd
              ├── healthcheck-client.crt
              ├── peer.crt
              └── server.crt

    '\033[32m./update-kubeadm-cert.sh etcd\033[0m' update only etcd certificates
      /etc/kubernetes
      └── pki
          ├── apiserver-etcd-client.crt
          └── etcd
              ├── healthcheck-client.crt
              ├── peer.crt
              └── server.crt

    '\033[32m./update-kubeadm-cert.sh master\033[0m' update only master certificates and kubeconf
      /etc/kubernetes
      ├── admin.conf
      ├── controller-manager.conf
      ├── scheduler.conf
      ├── kubelet.conf
      └── pki
          ├── apiserver.crt
          ├── apiserver-kubelet-client.crt
          └── front-proxy-client.crt
"
      exit 1
    esac
}

main "$@"
```

##### 运行脚本

```sh
chmod +x update-kubeadm-cert.sh
./update-kubeadm-cert.sh all

#检查kube-system pod
kubectl get pods -n kube-system

#检查证书有效期
#在master节点上
openssl x509 -in /etc/kubernetes/pki/ca.crt -noout -text | grep -i Not
openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -text | grep -i Not
```

### 【可选】安装其他插件

```sh
# 杜宽老师的Addon仓库
git clone https://gitee.com/dukuan/k8s-ha-install.git
cd k8s-ha-install/
# 查看分支
git branch -a
git checkout manual-installation-v1.33.x # 切换到对应版本的分支(改minorversion数字即可。.x不用改)
cd single/
# 里面有calico、metrics-server、dashboard、krm(杜宽老师开发的多集群管理工具)
kubectl apply -f dashboard-user.yaml dashboard.yaml krm.yaml
# krm默认用户名密码是admin/admin,进去之后在集群管理里面添加集群
```

### 【可选】部署Metrics-server

在新版的Kubernetes中系统资源的采集均使用Metrics-server,可以通过Metrics采集节点和Pod的内存、磁盘、CPU和网络的使用率。

1. 将Master01节点的front-proxy-ca.crt复制到所有Node节点:

```sh
scp /etc/kubernetes/pki/front-proxy-ca.crt k8s-node01:/etc/kubernetes/pki/front-proxy-ca.crt
```

2. 在master01上执行,安装metrics server:

```sh
cd /root/k8s-ha-install/kubeadm-metrics-server
kubectl create -f comp.yaml
```

安装完之后就能用:**kubectl top node** 查看节点资源使用情况。

## 集群可用性验证

1. 节点均正常:

   ```sh
   kubectl get nodes
   ```

2. pod正常:

   ```sh
   kubectl get pods -A
   ```

3. 集群svc、pod、node网段无任何冲突:

   ```sh
   kubectl get svc
   kubectl get po -A -owide | grep coredns
   kubectl get nodes -owide
   # 按上面正常配置,node是192.168,svc是10.96,pod是172.16
   # 具体要看子网掩码的配置
   ```

   如果发现集群网段冲突,只能推翻重建集群。

4. 能够正常创建资源:

   ```sh
   kubectl create deploy cluster-test --image=registry.cn-beijing.aliyuncs.com/dotbalo/debug-tools -- sleep 3600
   ```

5. Pod必须能够解析Service(同namespace和跨namespace)

   ```sh
   # 进入上一步创建的debug-tools pod
   kubectl exec -it <pod-name> --bash
   ```

6. 每个节点都必须要能访问Kubernetes的kubernetes svc 443和kube-dns的service 53

   ```sh
   # ssh到每个节点
   kubectl get svc # 找到默认的kubernetes名称的svc
   curl https://10.96.0.1:443 -k # 出现403 forbidden报错说明网络是通的
   curl https://10.96.0.10:53 -k # 出现(52)empty from server说明网络是通的
   ```

7. Pod和Pod之间可以正常通讯(同namespace和跨namespace;同节点和跨节点)

   ```sh
   # 进入创建的debug-tools pod
   kubectl exec -it <pod-name> --bash
   # 找到同ns和跨ns的两个pod,分别ping pod-IP看看通不通
   # 找到同node和跨node的两个pod,分别ping pod-IP看看通不通
   ```

8. 节点和Pod可以正常通信:在所有节点上ping一个Pod IP看看通不通

## 集群维护

### 节点关机

1. 公司服务器对于关机和异常断电的容忍度还是很高的。
2. 自己笔记本的集群:
   1. 异常断电可能会导致etcd数据丢失,集群起不来,尽量避免。
   2. 尽量避免挂起或者暂停。因为也可能会导致集群故障
   3. 不用了关机就用`shutdown -h now`。关机拍快照还节省空间。

### 节点下线

如果某个节点需要下线,可以使用如下步骤平滑下线:

1. 添加污点禁止调度:

   ```sh
   # 手动自己打污点
   kubectl taint node k8s-node02 offline=true:NoSchedule
   # cordon也可以实现
   kubectl cordon node k8s-node02
   ```

2. 查询节点是否有重要服务,漂移重要服务至其它节点

   ```sh
   kubectl get po -A -owide | grep k8s-node02
   # 假设coredns为重要服务,使用rollout重新调度该服务(如果副本多,也可以直接删除Pod,防止全部pod重建)
   kubectl rollout restart deploy coredns -n kube-system
   ```

3. 确认是否是ingress入口:(ingress-controller或者istio gateway)

   1.	如果就这一个入口,先把入口漂移到其他节点
   2.	如果很多入口,前端有个LB代理,在LB上把这个节点入口下线

4. 使用drain设置为驱逐状态:

   ```sh
   kubectl drain k8s-node02 --ignore-daemonsets --delete-emptydir-data
   ```

5. 再次检查节点上的其它服务,基础组件等

6. 查看有无异常的Pod:有无Pending/非Running状态的Pod

7. 使用delete删除节点:

   ```sh
   kubectl delete node k8s-node02
   ```

8. 节点下线:

   ```sh
   kubeadm reset -f
   systemctl disable --now kubelet
   ```

### 添加节点

1. 一个全新的节点,按照上面的安装步骤,完成基础配置、内核优化、Runtime安装、K8s组件安装
2. Master节点上运行:`kubeadm token create --print-join-command` 打印加入节点命令
3. 新节点上join集群,打上标签`kubectl label nodes node01 node-role.kubernetes.io/work=worker`

## 制作k8s安装需要的离线yum源

> [!info] 要全内网环境安装docker、k8s和相关依赖,需要在内部提供安装k8s、docker需要的yum源。首先需要在联网机器上把镜像拉下来。

### 制作安装docker需要的离线yum源

1、添加docker在线源

```bash
yum-config-manager --add-repo https://download.docker.com/linux/centos/dockerce.repo
```

2、通过如下命令download远程yum源文件,建立本地docker repo库

```bash
yum install --downloadonly --downloaddir=/mnt/docker-ce docker-ce
createrepo -d /mnt/docker-ce
```

3、把/mnt/docker-c下自动下载的rpm打包,传到内网机器,用过如下方法安装:

```bash
rpm -Uvh *.rpm --nodeps --force #这是强制安装当前文件夹中所有的rpm包,忽略依赖去安装
```

### 制作安装k8s命令行工具需要的离线yum源

1、添加k8s在线源

```bash
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg
https://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF
```

2、通过如下命令download远程yum源文件,建立本地k8s repo库

```bash
yum install --downloadonly --resolve kubeadm kubelet kubectl --destdir /mnt/k8s
createrepo -d /mnt/k8s
```

3、把/mnt/k8s下自动下载的rpm打包,传到内网机器,用过如下方法安装:

```bash
rpm -Uvh *.rpm --nodeps --force #这是强制安装当前文件夹中所有的rpm包,忽略依赖去安装
```

### 制作不同版本k8s集群需要的离线镜像

```bash
#如果用docker做容器,按照下面方面制作离线镜像
kubeadm config print init-defaults > kubeadm.yaml
#修改kubeadm.yaml配置文件如下:
imageRepository: registry.cn-hangzhou.aliyuncs.com/google_containers
#上述配置表示,安装k8s需要的镜像要从阿里云镜像仓库拉取

#通过如下命令下载镜像:
kubeadm config images pull --config kubeadm.yaml
#然后把下载好的镜像打包镜像:
docker save -o a.tar.gz registry.aliyuncs.com/google_containers/pause:3.7 jenkins/jenkins:latest ....
#传到内网k8s节点,通过如下命令导出镜像:
ctr -n=k8s.io images import a.tar.gz
docker load -i a.tar.gz
```

```bash
#如果用containerd做容器,按照下面方面制作离线镜像
kubeadm config print init-defaults > kubeadm.yaml
#修改kubeadm.yaml配置文件如下:
imageRepository: registry.cn-hangzhou.aliyuncs.com/google_containers
#上述配置表示,安装k8s需要的镜像要从阿里云镜像仓库拉取
#通过如下命令下载镜像:
kubeadm config images pull --config kubeadm.yaml

ctr -n=k8s.io images ls
#ls出来的的所有镜像做到离线文件里
ctr -n=k8s.io images export k8s1.28.0.tar.gz
#导入到内网环境解压
ctr -n=k8s.io images import k8s1.28.0.tar.gz
```

## Windows下安装kubectl

推荐使用scoop安装:

1. 安装scoop参考[scoop安装helm部分](../helm/helmv3-安装与使用.md)
2. 安装kubectl:`scoop install kubectl kubelogin`

## 安装k9s

- kubectl可视化插件:[k9s GitHub](https://github.com/derailed/k9s)
- 安装指南:[k9s安装指南](https://k9scli.io/topics/install/)

### 在线安装

1. 方法1:via [webi](https://webinstall.dev/) (在现在rockylinux vm上使用的方法)

   ```sh
   curl -sS https://webinstall.dev/k9s | bash
   ```

2. 方法2:在ubuntu上

   ```sh
   wget https://github.com/derailed/k9s/releases/download/v0.40.5/k9s_linux_amd64.deb && apt install ./k9s_linux_amd64.deb && rm k9s_linux_amd64.deb
   ```

3. 方法3:via snap

   ```sh
   snap install k9s --devmode
   ```

### 离线安装

#### 下载安装包

1. 先从github下载amd64版本安装包:[Releases · derailed/k9s](https://github.com/derailed/k9s/releases)
2. 安装包放到/root/下

#### 本地安装脚本

```sh
#!/bin/bash

############################################################
# K9s Local Installation Script
# Modified to install from local tar.gz file instead of downloading
############################################################

# Configuration for local installation
K9S_LOCAL_ARCHIVE="/root/k9s_Linux_amd64.tar.gz"
INSTALL_DIR="$HOME/.local/bin"

# Check if local archive exists, if so use local installation
if [ -f "$K9S_LOCAL_ARCHIVE" ]; then
    echo "Found local k9s archive, installing from: $K9S_LOCAL_ARCHIVE"

    # Create installation directory
    mkdir -p "$INSTALL_DIR"

    # Create temporary directory for extraction
    TEMP_DIR=$(mktemp -d)

    # Extract and install
    echo "Extracting k9s from local archive..."
    tar -xzf "$K9S_LOCAL_ARCHIVE" -C "$TEMP_DIR"

    if [ -f "$TEMP_DIR/k9s" ]; then
        echo "Installing k9s to $INSTALL_DIR/k9s"
        cp "$TEMP_DIR/k9s" "$INSTALL_DIR/k9s"
        chmod +x "$INSTALL_DIR/k9s"

        # Clean up
        rm -rf "$TEMP_DIR"

        echo "k9s installed successfully to $INSTALL_DIR/k9s"
        echo "Make sure $INSTALL_DIR is in your PATH to use k9s command"
        exit 0
    else
        echo "Error: k9s binary not found in archive"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
fi

# Fallback to original webi installation if local archive not found
echo "Local archive not found at $K9S_LOCAL_ARCHIVE, falling back to webi installation..."

export WEBI_PKG='k9s@stable'
export WEBI_HOST='https://webi.sh'
export WEBI_CHECKSUM='adad246e'

#########################################
#                                       #
# Display Debug Info in Case of Failure #
#                                       #
#########################################

fn_show_welcome() { (
    echo ""
    echo ""
    # invert t_task and t_pkg for top-level welcome message
    printf -- ">>> %s %s  <<<\n" \
        "$(t_pkg 'Welcome to') $(t_task 'Webi')$(t_pkg '!')" \
        "$(t_dim "- modern tools, instant installs.")"
    echo "    We expect your experience to be $(t_em 'absolutely perfect')!"
    echo ""
    echo "    $(t_attn 'Success')? Star it!   $(t_url 'https://github.com/webinstall/webi-installers')"
    echo "    $(t_attn 'Problem')? Report it: $(t_url 'https://github.com/webinstall/webi-installers/issues')"
    echo "                        $(t_dim "(your system is") $(t_host "$(fn_get_os)")/$(t_host "$(uname -m)") $(t_dim "with") $(t_host "$(fn_get_libc)") $(t_dim "&") $(t_host "$(fn_get_http_client_name)")$(t_dim ")")"

    sleep 0.2
); }

fn_get_os() { (
    # Ex:
    #     GNU/Linux
    #     Android
    #     Linux (often Alpine, musl)
    #     Darwin
    b_os="$(uname -o 2> /dev/null || echo '')"
    b_sys="$(uname -s)"
    if test -z "${b_os}" || test "${b_os}" = "${b_sys}"; then
        # ex: 'Darwin' (and plain, non-GNU 'Linux')
        echo "${b_sys}"
        return 0
    fi

    if echo "${b_os}" | grep -q "${b_sys}"; then
        # ex: 'GNU/Linux'
        echo "${b_os}"
        return 0
    fi

    # ex: 'Android/Linux'
    echo "${b_os}/${b_sys}"
); }

fn_get_libc() { (
    # Ex:
    #     musl
    #     libc
    if ldd /bin/ls 2> /dev/null | grep -q 'musl' 2> /dev/null; then
        echo 'musl'
    elif fn_get_os | grep -q 'GNU|Linux'; then
        echo 'gnu'
    else
        echo 'libc'
    fi
); }

fn_get_http_client_name() { (
    # Ex:
    #     curl
    #     curl+wget
    b_client=""
    if command -v curl > /dev/null; then
        b_client="curl"
    fi
    if command -v wget > /dev/null; then
        if test -z "${b_client}"; then
            b_client="wget"
        else
            b_client="curl+wget"
        fi
    fi

    echo "${b_client}"
); }

#########################################
#                                       #
#      For Making the Display Nice      #
#                                       #
#########################################

# Term Types
t_cmd() { (fn_printf '\e[2m\e[35m%s\e[39m\e[22m' "${1}"); }
t_host() { (fn_printf '\e[2m\e[33m%s\e[39m\e[22m' "${1}"); }
t_link() { (fn_printf '\e[1m\e[36m%s\e[39m\e[22m' "${1}"); }
t_path() { (fn_printf '\e[2m\e[32m%s\e[39m\e[22m' "${1}"); }
t_pkg() { (fn_printf '\e[1m\e[32m%s\e[39m\e[22m' "${1}"); }
t_task() { (fn_printf '\e[36m%s\e[39m' "${1}"); }
t_url() { (fn_printf '\e[2m%s\e[22m' "${1}"); }

# Levels
t_info() { (fn_printf '\e[1m\e[36m%s\e[39m\e[22m' "${1}"); }
t_attn() { (fn_printf '\e[1m\e[33m%s\e[39m\e[22m' "${1}"); }
t_warn() { (fn_printf '\e[1m\e[33m%s\e[39m\e[22m' "${1}"); }
t_err() { (fn_printf '\e[31m%s\e[39m' "${1}"); }

# Styles
t_bold() { (fn_printf '\e[1m%s\e[22m' "${1}"); }
t_dim() { (fn_printf '\e[2m%s\e[22m' "${1}"); }
t_em() { (fn_printf '\e[3m%s\e[23m' "${1}"); }
t_under() { (fn_printf '\e[4m%s\e[24m' "${1}"); }

# FG Colors
t_cyan() { (fn_printf '\e[36m%s\e[39m' "${1}"); }
t_green() { (fn_printf '\e[32m%s\e[39m' "${1}"); }
t_magenta() { (fn_printf '\e[35m%s\e[39m' "${1}"); }
t_yellow() { (fn_printf '\e[33m%s\e[39m' "${1}"); }

fn_printf() { (
    a_style="${1}"
    a_text="${2}"
    if fn_is_tty; then
        #shellcheck disable=SC2059
        printf -- "${a_style}" "${a_text}"
    else
        printf -- '%s' "${a_text}"
    fi
); }

fn_sub_home() { (
    my_rel=${HOME}
    my_abs=${1}
    echo "${my_abs}" | sed "s:^${my_rel}:~:"
); }

###################################
#                                 #
#       Detect HTTP Client        #
#                                 #
###################################

fn_wget() { (
    # Doc:
    #     Downloads the file at the given url to the given path
    a_url="${1}"
    a_path="${2}"

    cmd_wget="wget -c -q --user-agent"
    if fn_is_tty; then
        cmd_wget="wget -c -q --show-progress --user-agent"
    fi
    # busybox wget doesn't support --show-progress
    # See
    if readlink "$(command -v wget)" | grep -q busybox; then
        cmd_wget="wget --user-agent"
    fi

    b_triple_ua="$(fn_get_target_triple_user_agent)"
    b_agent="webi/wget ${b_triple_ua}"
    if command -v curl > /dev/null; then
        b_agent="webi/wget+curl ${b_triple_ua}"
    fi

    if ! $cmd_wget "${b_agent}" "${a_url}" -O "${a_path}"; then
        echo >&2 "    $(t_err "failed to download (wget)") '$(t_url "${a_url}")'"
        echo >&2 "    $cmd_wget '${b_agent}' '${a_url}' -O '${a_path}'"
        echo >&2 "    $(wget -V)"
        return 1
    fi
); }

fn_curl() { (
    # Doc:
    #     Downloads the file at the given url to the given path
    a_url="${1}"
    a_path="${2}"

    cmd_curl="curl -f -sSL -#"
    if fn_is_tty; then
        cmd_curl="curl -f -sSL"
    fi

    b_triple_ua="$(fn_get_target_triple_user_agent)"
    b_agent="webi/curl ${b_triple_ua}"
    if command -v wget > /dev/null; then
        b_agent="webi/curl+wget ${b_triple_ua}"
    fi

    if ! $cmd_curl -A "${b_agent}" "${a_url}" -o "${a_path}"; then
        echo >&2 "    $(t_err "failed to download (curl)") '$(t_url "${a_url}")'"
        echo >&2 "    $cmd_curl -A '${b_agent}' '${a_url}' -o '${a_path}'"
        echo >&2 "    $(curl -V)"
        return 1
    fi
); }

fn_get_target_triple_user_agent() { (
    # Ex:
    #     x86_64/unknown GNU/Linux/5.15.107-2-pve gnu
    #     arm64/unknown Darwin/22.6.0 libc
    echo "$(uname -m)/unknown $(fn_get_os)/$(uname -r) $(fn_get_libc)"
); }

fn_download_to_path() { (
    a_url="${1}"
    a_path="${2}"

    mkdir -p "$(dirname "${a_path}")"
    if command -v curl > /dev/null; then
        fn_curl "${a_url}" "${a_path}.part"
    elif command -v wget > /dev/null; then
        fn_wget "${a_url}" "${a_path}.part"
    else
        echo >&2 "    $(t_err "failed to detect HTTP client (curl, wget)")"
        return 1
    fi
    mv "${a_path}.part" "${a_path}"
); }

##############################################
#                                            #
# Install or Update Webi and Install Package #
#                                            #
##############################################

webi_bootstrap() { (
    a_path="${1}"

    echo ""
    echo "$(t_task 'Bootstrapping') $(t_pkg 'Webi')"

    b_path_rel="$(fn_sub_home "${a_path}")"
    b_checksum=""
    if test -r "${a_path}"; then
        b_checksum="$(fn_checksum "${a_path}")"
    fi
    if test "$b_checksum" = "${WEBI_CHECKSUM}"; then
        echo "    $(t_dim 'Found') $(t_path "${b_path_rel}")"
        sleep 0.1
        return 0
    fi

    b_webi_file_url="${WEBI_HOST}/packages/webi/webi.sh"
    b_tmp=''
    if test -r "${a_path}"; then
        b_ts="$(date -u '+%s')"
        b_tmp="${a_path}.${b_ts}.bak"
        mv "${a_path}" "${b_tmp}"
        echo "    Updating $(t_path "${b_path_rel}")"
    fi

    echo "    Downloading $(t_url "${b_webi_file_url}")"
    echo "        to $(t_path "${b_path_rel}")"
    fn_download_to_path "${b_webi_file_url}" "${a_path}"
    chmod u+x "${a_path}"

    if test -r "${b_tmp}"; then
        rm -f "${b_tmp}"
    fi
); }

fn_checksum() {
    a_filepath="${1}"

    if command -v sha1sum > /dev/null; then
        sha1sum "${a_filepath}" | cut -d' ' -f1 | cut -c 1-8
        return 0
    fi

    if command -v shasum > /dev/null; then
        shasum "${a_filepath}" | cut -d' ' -f1 | cut -c 1-8
        return 0
    fi

    if command -v sha1 > /dev/null; then
        sha1 "${a_filepath}" | cut -d'=' -f2 | cut -c 2-9
        return 0
    fi

    echo >&2 "    warn: no sha1 sum program"
    date '+%F %H:%M'
}

##############################################
#                                            #
#          Detect TTY and run main           #
#                                            #
##############################################

fn_is_tty() {
    if test "${WEBI_TTY}" = 'tty'; then
        return 0
    fi
    return 1
}

fn_detect_tty() { (
    # stdin will NOT be a tty if it's being piped
    # stdout & stderr WILL be a tty even when piped
    # they are not a tty if being captured or redirected
    # 'set -i' is NOT available in sh
    if test -t 1 && test -t 2; then
        return 0
    fi

    return 1
); }

main() { (
    set -e
    set -u

    WEBI_TTY="${WEBI_TTY:-}"
    if test -z "${WEBI_TTY}"; then
        if fn_detect_tty; then
            WEBI_TTY="tty"
        fi
        export WEBI_TTY
    fi

    if test -z "${WEBI_WELCOME:-}"; then
        fn_show_welcome
    fi
    export WEBI_WELCOME='shown'

    # note: we may support custom locations in the future
    export WEBI_HOME="${HOME}/.local"
    b_home="$(fn_sub_home "${WEBI_HOME}")"
    b_webi_path="${WEBI_HOME}/bin/webi"
    b_webi_path_rel="${b_home}/bin/webi"

    WEBI_CURRENT="${WEBI_CURRENT:-}"
    if test "${WEBI_CURRENT}" != "${WEBI_CHECKSUM}"; then
        webi_bootstrap "${b_webi_path}"
        export WEBI_CURRENT="${WEBI_CHECKSUM}"
    fi

    echo "    Running $(t_cmd "${b_webi_path_rel} ${WEBI_PKG}")"
    echo ""

    "${b_webi_path}" "${WEBI_PKG}"
); }

main
```

#### 安装

```sh
chmod +x k9s-local-install.sh
./k9s0local-install.sh

echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

再新开一个terminal就可以运行K9s了
