---
title: 基于Operator部署Redis集群
tags:
  - kubernetes
  - database/redis
aliases:
  - Operator部署Redis集群
---

# 基于operator部署redis集群

## 找到官网

- 进入operator官网找到Redis Operator：[OperatorHub.io | The registry for Kubernetes Operators](https://operatorhub.io/operator/redis-operator)
- 找到Redis Operator的官网：[Redis Operator | Redis Operator](https://ot-redis-operator.netlify.app/docs/)

- 推荐`Cluster模式（集群模式）`去部署redis（或者单节点模式，或者哨兵模式其次，不推荐主从模式replication，在k8s中会有问题，主从切换不是那么很及时）

> - Redis Cluster 是 Redis 的分布式部署模式，可以让多个 Redis 实例以集群的方式运行，从而提供高可用性、水平扩展和数据冗余的能力。Redis  Cluster 通过分片（Sharding ）和复制（Replication）技术，确保数据可以在多个节点之间分布，并且在节点故障时能够自动恢复。
>
>
> - 注意Redis集群**最少也要6个实例**（3主3从），6个已经可以满足大部分需求了。
>
>
> <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202508231625306.png" alt="image-20250823162536219" style="zoom:50%;" />

## helm安装operator

[Installation | Redis Operator](https://ot-redis-operator.netlify.app/docs/installation/installation/#helm-installation)

~~~sh
helm repo add ot-helm https://ot-container-kit.github.io/helm-charts/
helm install redis-operator ot-helm/redis-operator --namespace ot-operators
~~~

装完之后集群里就有RedisCluster这个CRD资源了。

## 部署cluster模式redis集群

参考文档：[Cluster | Redis Operator](https://ot-redis-operator.netlify.app/docs/getting-started/cluster/)

### helm部署

~~~sh
helm install redis-cluster ot-helm/redis-cluster --set redisCluster.clusterSize=3 --namespace ot-operators
~~~

### yaml文件部署

[Cluster | Redis Operator](https://ot-redis-operator.netlify.app/docs/getting-started/cluster/#yaml-installation)

最少只需要一个yaml文件去部署即可，非常简洁，不需要helm去管理。装完之后，集群里面就起来了3主3从的Redis集群了。

~~~yaml
--- 
apiVersion: redis.redis.opstreelabs.in/v1beta1 
kind: RedisCluster 
metadata: 
  name: redis-cluster 
  namespace: public-serivce
spec: 
  clusterSize: 3 # 主节点的数量为3，每个主节点默认配一个副节点
  clusterVersion: v7 
  securityContext: 
    runAsUser: 1000 
    fsGroup: 1000 
  persistenceEnabled: true 
  kubernetesConfig: 
    image: quay.io/opstree/redis:v7.0.15 
    imagePullPolicy: IfNotPresent 
  storage: 
    volumeClaimTemplate: 
      spec: 
        storageClassName: sc-nfs
        accessModes: ["ReadWriteOnce"] 
        resources: 
          requests: 
            storage: 1Gi
~~~

> [!tip] PV权限问题
> Redis pod如果报错pv没有permission的话: 去nfs节点把pv数据目录改成chmod -R 777, chown -R 1000.1000
>
> 本质是因为存储平台没有配置默认权限，需要挨个pod去配置对应的pv目录权限。

## 【可选】添加redis集群密码认证

~~~yaml
--- 
apiVersion: v1 
kind: Secret 
metadata: 
  name: redis-secret 
  namespace: public-service
stringData: 
  password: <password>
type: Opaque 
~~~

更新集群配置：

~~~yaml
--- 
apiVersion: redis.redis.opstreelabs.in/v1beta1 
kind: RedisCluster 
metadata: 
  name: redis-cluster 
  namespace: public-serivce
spec: 
  clusterSize: 3 # 主节点的数量为3，每个主节点默认配一个副节点
  clusterVersion: v7 
  securityContext: 
    runAsUser: 1000 
    fsGroup: 1000 
  persistenceEnabled: true 
  kubernetesConfig: 
    image: quay.io/opstree/redis:v7.0.15 
    imagePullPolicy: IfNotPresent 
    redisSecret: 
      name: redis-secret 
      key: password 
  storage: 
    volumeClaimTemplate: 
      spec: 
        storageClassName: sc-nfs
        accessModes: ["ReadWriteOnce"] 
        resources: 
          requests: 
            storage: 1Gi
~~~

建议在集群创建之前就决定好要不要开启密码认证。

~~~sh
redis-cli -c -a <password>
CLUSTER INFO
~~~

## 测试集群内连接

~~~sh
kubectl exec -ti redis-cluster-leader-0 -n public-service -- bash 
redis-cli
# 查看集群状态
CLUSTER info
# 查看节点状态
CLUSTER NODES
# 创建redis key测试，-c追踪数据写入
redis-cli -c
set a 1
get a
~~~

redis集群是分片存储的模式，一共有16384个槽，三主三从的集群，16384个槽会被分成三份。写数据的时候，数据会被哈希算一下，判断是属于哪个槽的。

## 测试集群外连接

如果需要在K8s外部访问Redis集群**（生产环境不推荐）**，就要把Redis集群暴露出去，此时可以把Service更改为NodePort：

~~~yaml
cat redis-cluster-expose.yaml  
--- 
apiVersion: redis.redis.opstreelabs.in/v1beta1 
kind: RedisCluster 
metadata: 
  name: redis-cluster-expose 
spec: 
  clusterSize: 3 
  clusterVersion: v7 
  securityContext: 
    runAsUser: 1000 
    fsGroup: 1000 
  persistenceEnabled: false 
  kubernetesConfig: 
    service: 
      serviceType: NodePort 
    image: registry.cn-beijing.aliyuncs.com/dotbalo/redis:v7.0.15  
    imagePullPolicy: IfNotPresent 
    redisSecret: 
      name: redis-secret 
      key: password 
...
~~~

因为redis写数据会产生下一跳，跳到另外的节点。所以如果都用pod IP访问，下一跳产生的时候，外部就访问不到集群内部的pod ip。所以改成NodePort方式，都用节点IP:port访问就能访问通了。 

改成NodePort之后，可以在集群外部访问集群内的Redis

~~~sh
redis-cli -c -h 192.168.181.66 -p 31529 -a <password>
~~~

