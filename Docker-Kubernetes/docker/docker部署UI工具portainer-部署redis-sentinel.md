---
title: Docker部署Portainer与Redis-Sentinel
tags:
  - docker
  - container
  - portainer
  - redis
aliases:
  - Portainer部署
  - Redis-Sentinel部署
---

# Docker部署Portainer与Redis-Sentinel


Reference: [Portainer与Redis-Sentinel部署参考](https://mp.weixin.qq.com/s/pkpDv1nBjiEiCMeGPSwPeA)

## 部署portainer工具

- docker-compose部署

~~~sh
tee portainer.yml <<"EOF"
version: "3"
services:
  portainer:
    image: portainer/portainer:latest
    container_name: portainer
    ports:
    - "9876:9000"
    volumes:
    - /app/portainer/data:/data
    - /var/run/docker.sock:/var/run/docker.sock
EOF
#后台启动
docker-compose -f portainer.yml up -d
#rocky linux中,docker-compose变成了docker compose
~~~

- 访问宿主机IP:9876端口(username: admin, passwd: `<password>`)
- 点击local进行本地容器管理。更多文档参考:[Portainer官方文档](https://www.portainer.io/take-5)

## portainer添加environment

- 在rocky-1机器部署了portainer,想去监控rocky-2机器上的容器。可以在portainer UI上找到Settings - Environments - Add Environment - 选择docker Standalone - 进入environment wizard
- 在被监控的rocky-2上pull一个agent镜像(根据wizard的提示)- 起一个agent容器 - name和environment address上填入rocky-2的地址,点击connect即可

## 基于Portainer安装redis-sentinel

### 环境准备

- 基于一台服务器完成一主二从+三个哨兵的部署架构,最终效果是:
  - 当主节点更新数据之后,从节点数据也会进行同步。
  - 当我们将主节点手动停止之后,哨兵就会选举出新的master继续进行工作。

### 主从复制部署

- 部署主从结构时，我们仍使用docker-compose创建名为redis-cluster.yml的文件，配置主从信息：
  - 安全起见，建议尽量不要使用6379作为对外暴露的端口号；即使使用6379，也尽量设置安全的密码，避免被人植入挖矿程序。

~~~yaml
tee redis-cluster.yml <<'EOF'
version: '3'
services:
  # 主节点
  master:
    image: redis
    # 主节点名称
    container_name: redis-master
    # 设置redis登录密码、从节点连接主节点的密码
    command: redis-server --requirepass 123456 --masterauth 123456
    ports:
    # 对外暴露端口号为16379
    - 16379:6379
  # 从节点
  slave1:
    image: redis
    container_name: redis-slave-1
    ports:
    # 对外暴露端口号为16380
    - 16380:6379
    # 启动redis 从属于容器名为 redis-master的redis,端口号为容器端口号而不是对外映射端口号,设置连接密码,连接主节点的密码
    command:  redis-server --slaveof redis-master 6379 --requirepass 123456 --masterauth 123456
  # 从节点2
  slave2:
    image: redis
    container_name: redis-slave-2
    ports:
    - 16381:6379
    command: redis-server --slaveof redis-master 6379 --requirepass 123456 --masterauth 123456
EOF
~~~

~~~sh
docker-compose -f redis-cluster.yml up -d
~~~

- 容器启动后，可以在portainer中查看master容器的log，也可以直接用console功能connect进入容器，尝试设置一个键值对

  (202408:docker 26版本与portainer 2.19版本不兼容,console用不了)

  ~~~SH
  #用redis-cli认证
  redis-cli
  auth 123456
  ping
  set user_name xiaoming

  #console进入从节点查看数据
  keys *
  get user_name
  ~~~

### 创建redis-sentinel专用网络驱动

为了统一管理redis-sentinel并将其与其他容器隔离，我们在部署sentinel前需要基于Portainer创建自定义bridge网络。创建名为redis-sentinel的bridge网络，将主从节点和哨兵节点关联起来，并与docker中的其他容器隔离。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202408141503188.png" alt="image-20240814150337050" style="zoom: 50%;" />

- portainer -- network -- add network
- 输入名称为redis-sentinel,其余默认 -- create network

- 重点来了,我们的redis主从节点现在都处于默认的网络驱动中,我们必须手动将其配置到redis-sentinel网络中
  - 点击容器列表,找到我们的主从节点容器,然后分别进入他们的管理列表最下方,找到network选项,在network列表中找到redis-sentinel选择join network即可。

### 创建哨兵

- 配置3个哨兵配置文件

~~~sh
mkdir -p /app/cloud/redis/sentinel/
cd /app/cloud/redis/sentinel/
~~~

~~~sh
#哨兵1
tee sentinel1.conf <<'EOF'
port 26379
dir /tmp
# master节点在bridge网络中的ip值
sentinel monitor redis-master 172.19.0.2 6379 2
# master节点密码
sentinel auth-pass redis-master 123456
sentinel down-after-milliseconds redis-master 30000
sentinel parallel-syncs redis-master 1
sentinel failover-timeout redis-master 180000
sentinel deny-scripts-reconfig yes
EOF

#哨兵2
tee sentinel2.conf <<'EOF'
port 26380
dir /tmp
# master节点在bridge网络中的ip值
sentinel monitor redis-master 172.19.0.2 6379 2
# master节点密码
sentinel auth-pass redis-master 123456
sentinel down-after-milliseconds redis-master 30000
sentinel parallel-syncs redis-master 1
sentinel failover-timeout redis-master 180000
sentinel deny-scripts-reconfig yes
EOF

#哨兵3
tee sentinel3.conf <<'EOF'
port 26381
dir /tmp
# master节点在bridge网络中的ip值
sentinel monitor redis-master 172.19.0.2 6379 2
# master节点密码
sentinel auth-pass redis-master 123456
sentinel down-after-milliseconds redis-master 30000
sentinel parallel-syncs redis-master 1
sentinel failover-timeout redis-master 180000
sentinel deny-scripts-reconfig yes
EOF
~~~

> [!info] master节点IP地址来源
> 将master节点命名为redis-master,然后网络配置为172.19.0.2这个值是从哪里来的呢?
>
> - 我们点击redis-master即redis主节点容器管理界面,在ip address一栏看到master节点的容器ip地址,因为哨兵节点和主从节点都处于redis-sentinel这个网络中,所以172.19.0.x这个网络是互通的,在bridge模式下配置这个ip地址是完全没有问题的。

~~~yaml
tee redis-sentinel.yml <<'EOF'
version: '3'
services:
  sentinel1:
    image: redis
    # 容器名称
    container_name: redis-sentinel-1
    ports:
    # 端口映射
    - 26379:26379
    # 启动redis哨兵
    command: redis-sentinel /usr/local/etc/redis/sentinel.conf
    volumes:
    # 哨兵1的sentinel.conf和宿主文件位置映射
    - /app/cloud/redis/sentinel/sentinel1.conf:/usr/local/etc/redis/sentinel.conf
  sentinel2:
    image: redis
    container_name: redis-sentinel-2
    ports:
    - 26380:26379
    command: redis-sentinel /usr/local/etc/redis/sentinel.conf
    volumes:
    - /app/cloud/redis/sentinel/sentinel2.conf:/usr/local/etc/redis/sentinel.conf
  sentinel3:
    image: redis
    container_name: redis-sentinel-3
    ports:
    - 26381:26379
    command: redis-sentinel /usr/local/etc/redis/sentinel.conf
    volumes:
    - /app/cloud/redis/sentinel/sentinel3.conf:/usr/local/etc/redis/sentinel.conf
# 重点,将3个哨兵加入到redis-sentinel和主从节点建立联系
networks:
  default:
    external:
      name: redis-sentinel
EOF
~~~

- 启动哨兵集群

~~~sh
docker-compose -f redis-sentinel.yml up -d
~~~

### 测试高可用

- console进入maste节点:`info replication`查看是否为主节点(role:master);同理,进入从节点查看(role:slave)
- 关闭master节点:portainer界面直接stop掉master的容器

- 点入任意一个哨兵日志,可以看到它监控到主节点下线,并快速选举出一个新的节点作为master上线

  ```sh
  +sdown slave 172.19.0.2:6379 172.19.0.2 6379 @ redis-master 172.19.0.4变成了master 6379
  #172.19.0.4变成了master
  ```

- 通过ip地址定位到容器,我们进入容器查看其身份,确实变为master
