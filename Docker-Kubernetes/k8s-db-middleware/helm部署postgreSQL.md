---
title: Helm部署PostgreSQL
tags:
  - kubernetes
  - database/postgresql
aliases:
  - Helm部署PostgreSQL
---

# Helm部署PostgreSQL


## 介绍

github地址：[charts/bitnami/postgresql at main · bitnami/charts](https://github.com/bitnami/charts/tree/main/bitnami/postgresql)

artifactHub地址：

- 单节点pg：[postgresql 16.7.26 · bitnami/bitnami](https://artifacthub.io/packages/helm/bitnami/postgresql)
- HA pg：[postgresql-ha 16.3.1 · bitnami/bitnami](https://artifacthub.io/packages/helm/bitnami/postgresql-ha)

HA模式比单节点模式多了Pgpool（接入流量）、repmgr（自动切换主从状态）、witness（防止脑裂）等组件，适合用在生产环境上。

## 下载

~~~sh
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update bitnami
helm pull bitnami/postgresql --version 16.7.26 # 这个chart是用来安装单节点pg
helm pull bitnami/postgresql-ha --version 16.3.1 # 这个chart是用来安装HA模式高可用pg
~~~

> [!tip] 提示
> - bitnami/postgresql如果网络问题pull不下来就直接从bitnami github上clone下来源码，里面就有mysql的helm chart。
>
>   ~~~sh
>   git clone https://github.com/bitnami/charts.git
>   ~~~
>
> - 注意需要把charts/bitnami/common目录放到postgresql/charts/目录里面才能组成完整的helm chart，因为common是子chart需要安装。

## 配置-HA模式

> [!warning] 生产环境注意
> - 生产环境中不推荐使用nfs，由于其单点无高可用、性能也有问题。如果k8s中没有配置ceph等分布式储，那就不推荐把数据库等需要持久化数据的服务部署到k8s中。
> - 这里学习环境可以使用nfs。

~~~yaml
global: 
  defaultStorageClass: "sc-nfs" 
  postgresql: 
    password: "<password>" 
    repmgrPassword: "<password>" 
  pgpool: # pgpool可以将查询分发到多个PostgreSQL节点，实现读写分离 
    adminUsername: "" 
    adminPassword: "<password>" 
witness: # 用于提供额外的投票机制，防止脑裂现象。奇数个节点非必须，偶数个节点必须要装。
  create: true
~~~

## 安装

~~~sh
kubectl create ns postgresql
helm upgrade -i postgresql-ha -n postgresql -f values.dev.yaml .
~~~

## 使用

~~~sh
kubectl exec -ti pg-postgresql-ha-postgresql-0 -n postgresql -- bash
psql -h pg-postgresql-ha-pgpool -U postgres
# 创建数据库和表
CREATE DATABASE mydatabase;

\c mydatabase

CREATE TABLE employees ( 
     id SERIAL PRIMARY KEY, 
     name VARCHAR(100), 
     age INT, 
     department VARCHAR(50) 
); 

\d employees

# 查看集群状态
/opt/bitnami/scripts/postgresql-repmgr/entrypoint.sh repmgr -f /opt/bitnami/repmgr/conf/repmgr.conf cluster show
~~~

