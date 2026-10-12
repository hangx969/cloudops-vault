---
title: K8s监控Alertmanager(v0.14.0)
tags:
  - kubernetes
  - monitoring
  - prometheus
  - alertmanager
aliases:
  - Alertmanager部署配置
---

# K8s监控Alertmanager(v0.14.0)


## Alertmanager

### 作用

- 报警：指prometheus将监测到的异常事件发送给alertmanager 
- 通知：alertmanager将报警信息发送到邮件、微信、钉钉等

### 工作流程

1. Prometheus Server监控目标主机上暴露的http接口（这里假设接口A），通过Promethes配置的'scrape_interval'定义的时间间隔，定期采集目标主机上监控数据。
2. 当接口A不可用的时候，Server端会持续的尝试从接口中取数据，直到"scrape_timeout"时间后停止尝试。这时候把接口的状态变为“DOWN”。
3. Prometheus同时根据配置的"evaluation_interval"的时间间隔，定期（默认1min）的对Alert Rule进行评估；当到达评估周期的时候，发现接口A为DOWN，即UP=0为真，激活Alert，进入“PENDING”状态，并记录当前active的时间；
4. 当下一个alert rule的评估周期到来的时候，发现UP=0继续为真，然后判断警报Active的时间是否已经超出rule里的‘for’ 持续时间，如果未超出，则进入下一个评估周期；如果时间超出，则alert的状态变为“FIRING”；同时调用Alertmanager接口，发送相关报警数据。
5. AlertManager收到报警数据后，会将警报信息进行分组，然后根据alertmanager配置的“group_wait”时间先进行等待。等wait时间过后再发送报警信息。
6. 属于同一个Alert Group的警报，在等待的过程中可能进入新的alert，如果之前的报警已经成功发出，那么间隔“group_interval”的时间间隔后再重新发送报警信息。比如配置的是邮件报警，那么同属一个group的报警信息会汇总在一个邮件里进行发送。
7. 如果Alert Group里的警报一直没发生变化并且已经成功发送，等待‘repeat_interval’时间间隔之后再重复发送相同的报警邮件；如果之前的警报没有成功发送，则相当于触发第6条条件，则需要等待group_interval时间间隔后重复发送。

### 部署告警到邮箱

#### 配置邮箱的SMTP和POP3功能

- 在邮箱的设置中，开启POP3/IMAP/SMTP功能，生成授权码。

#### 配置configmap

~~~yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: alertmanager
  namespace: monitor-sa
data:
  alertmanager.yml: |-
    global:
      resolve_timeout: 1m
      smtp_smarthost: 'smtp.163.com:25'
      smtp_from: 'xuhang969@163.com' #指定从哪个邮箱发告警
      smtp_auth_username: 'xuhang969@163.com' #邮箱地址
      smtp_auth_password: '<smtp-auth-code>' #smtp授权码
      smtp_require_tls: false
    route:  #用于配置告警分发策略
      group_by: [alertname] # alertmanager会根据group_by配置将Alert分组
      group_wait: 10s       # 组告警等待时间。也就是告警产生后等待10s再发出去，10s期间如果有同组告警一起发出
      group_interval: 10s    # 上下两组发送告警的间隔时间
      repeat_interval: 30m    # 若产生重复告警，间隔多久再重发一次告警
      receiver: default-receiver  #定义谁来收告警
    receivers:
    - name: 'default-receiver'
      email_configs:
      - to: '1003665363@qq.com' #to后面指定发送到哪个邮箱
        send_resolved: true
~~~

#### 更新prometheus的configmap

- 这个cm中挂进去两个yml文件，prometheus.yml定义了数据采集配置，rules.yml会包含一系列告警规则

~~~yaml
kind: ConfigMap
apiVersion: v1
metadata:
  labels:
    app: prometheus
  name: prometheus-config
  namespace: monitor-sa
data:
  prometheus.yml: |
    rule_files:
    - /etc/prometheus/rules.yml
    alerting:
      alertmanagers:
      - static_configs:
        - targets: ["localhost:9093"] #后续会把prometheus和alertmanager部署到同一个pod里面，通过localhost通信。
    global:
      scrape_interval: 15s
      scrape_timeout: 10s
      evaluation_interval: 1m 
    scrape_configs:
    - job_name: 'kubernetes-node'
      kubernetes_sd_configs:
      - role: node
      relabel_configs:
      - source_labels: [__address__]
        regex: '(.*):10250'
        replacement: '${1}:9100'
        target_label: __address__
        action: replace
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
    - job_name: 'kubernetes-node-cadvisor'
      kubernetes_sd_configs:
      - role:  node
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
      - target_label: __address__
        replacement: kubernetes.default.svc:443
      - source_labels: [__meta_kubernetes_node_name]
        regex: (.+)
        target_label: __metrics_path__
        replacement: /api/v1/nodes/${1}/proxy/metrics/cadvisor
    - job_name: 'kubernetes-apiserver'
      kubernetes_sd_configs:
      - role: endpoints
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https
    - job_name: 'kubernetes-service-endpoints'
      kubernetes_sd_configs:
      - role: endpoints
      relabel_configs:
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scheme]
        action: replace
        target_label: __scheme__
        regex: (https?)
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_service_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
      - action: labelmap
        regex: __meta_kubernetes_service_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_service_name]
        action: replace
        target_label: kubernetes_name 
    - job_name: 'kubernetes-pods'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - action: keep
        regex: true
        source_labels:
        - __meta_kubernetes_pod_annotation_prometheus_io_scrape
      - action: replace
        regex: (.+)
        source_labels:
        - __meta_kubernetes_pod_annotation_prometheus_io_path
        target_label: __metrics_path__
      - action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        source_labels:
        - __address__
        - __meta_kubernetes_pod_annotation_prometheus_io_port
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - action: replace
        source_labels:
        - __meta_kubernetes_namespace
        target_label: kubernetes_namespace
      - action: replace
        source_labels:
        - __meta_kubernetes_pod_name
        target_label: kubernetes_pod_name
    - job_name: 'kubernetes-etcd'
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/k8s-certs/etcd/ca.crt
        cert_file: /var/run/secrets/kubernetes.io/k8s-certs/etcd/server.crt
        key_file: /var/run/secrets/kubernetes.io/k8s-certs/etcd/server.key
      scrape_interval: 5s
      static_configs:
      - targets: ['192.168.40.180:2379']
  rules.yml: |
    groups:
    - name: example
      rules:
      - alert: apiserver的cpu使用率大于80%
        expr: rate(process_cpu_seconds_total{job=~"kubernetes-apiserver"}[1m]) * 100 > 80
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}组件的cpu使用率超过80%"
      - alert:  apiserver的cpu使用率大于90%
        expr: rate(process_cpu_seconds_total{job=~"kubernetes-apiserver"}[1m]) * 100 > 90
        for: 2s
        labels:
          severity: critical
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}组件的cpu使用率超过90%"
      - alert: etcd的cpu使用率大于80%
        expr: rate(process_cpu_seconds_total{job=~"kubernetes-etcd"}[1m]) * 100 > 80
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}组件的cpu使用率超过80%"
      - alert:  etcd的cpu使用率大于90%
        expr: rate(process_cpu_seconds_total{job=~"kubernetes-etcd"}[1m]) * 100 > 90
        for: 2s
        labels:
          severity: critical
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}组件的cpu使用率超过90%"
      - alert: kube-state-metrics的cpu使用率大于80%
        expr: rate(process_cpu_seconds_total{k8s_app=~"kube-state-metrics"}[1m]) * 100 > 80
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "{{$labels.instance}}的{{$labels.k8s_app}}组件的cpu使用率超过80%"
          value: "{{ $value }}%"
          threshold: "80%"      
      - alert: kube-state-metrics的cpu使用率大于90%
        expr: rate(process_cpu_seconds_total{k8s_app=~"kube-state-metrics"}[1m]) * 100 > 0
        for: 2s
        labels:
          severity: critical
        annotations:
          description: "{{$labels.instance}}的{{$labels.k8s_app}}组件的cpu使用率超过90%"
          value: "{{ $value }}%"
          threshold: "90%"      
      - alert: coredns的cpu使用率大于80%
        expr: rate(process_cpu_seconds_total{k8s_app=~"kube-dns"}[1m]) * 100 > 80
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "{{$labels.instance}}的{{$labels.k8s_app}}组件的cpu使用率超过80%"
          value: "{{ $value }}%"
          threshold: "80%"      
      - alert: coredns的cpu使用率大于90%
        expr: rate(process_cpu_seconds_total{k8s_app=~"kube-dns"}[1m]) * 100 > 90
        for: 2s
        labels:
          severity: critical
        annotations:
          description: "{{$labels.instance}}的{{$labels.k8s_app}}组件的cpu使用率超过90%"
          value: "{{ $value }}%"
          threshold: "90%"      
      - alert: kube-proxy打开句柄数>600
        expr: process_open_fds{job=~"kubernetes-kube-proxy"}  > 600
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}打开句柄数>600"
          value: "{{ $value }}"
      - alert: kube-proxy打开句柄数>1000
        expr: process_open_fds{job=~"kubernetes-kube-proxy"}  > 1000
        for: 2s
        labels:
          severity: critical
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}打开句柄数>1000"
          value: "{{ $value }}"
      - alert: kubernetes-schedule打开句柄数>600
        expr: process_open_fds{job=~"kubernetes-schedule"}  > 600
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}打开句柄数>600"
          value: "{{ $value }}"
      - alert: kubernetes-schedule打开句柄数>1000
        expr: process_open_fds{job=~"kubernetes-schedule"}  > 1000
        for: 2s
        labels:
          severity: critical
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}打开句柄数>1000"
          value: "{{ $value }}"
      - alert: kubernetes-controller-manager打开句柄数>600
        expr: process_open_fds{job=~"kubernetes-controller-manager"}  > 600
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}打开句柄数>600"
          value: "{{ $value }}"
      - alert: kubernetes-controller-manager打开句柄数>1000
        expr: process_open_fds{job=~"kubernetes-controller-manager"}  > 1000
        for: 2s
        labels:
          severity: critical
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}打开句柄数>1000"
          value: "{{ $value }}"
      - alert: kubernetes-apiserver打开句柄数>600
        expr: process_open_fds{job=~"kubernetes-apiserver"}  > 600
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}打开句柄数>600"
          value: "{{ $value }}"
      - alert: kubernetes-apiserver打开句柄数>1000
        expr: process_open_fds{job=~"kubernetes-apiserver"}  > 1000
        for: 2s
        labels:
          severity: critical
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}打开句柄数>1000"
          value: "{{ $value }}"
      - alert: kubernetes-etcd打开句柄数>600
        expr: process_open_fds{job=~"kubernetes-etcd"}  > 600
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}打开句柄数>600"
          value: "{{ $value }}"
      - alert: kubernetes-etcd打开句柄数>1000
        expr: process_open_fds{job=~"kubernetes-etcd"}  > 1000
        for: 2s
        labels:
          severity: critical
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}打开句柄数>1000"
          value: "{{ $value }}"
      - alert: coredns
        expr: process_open_fds{k8s_app=~"kube-dns"}  > 600
        for: 2s
        labels:
          severity: warnning 
        annotations:
          description: "插件{{$labels.k8s_app}}({{$labels.instance}}): 打开句柄数超过600"
          value: "{{ $value }}"
      - alert: coredns
        expr: process_open_fds{k8s_app=~"kube-dns"}  > 1000
        for: 2s
        labels:
          severity: critical
        annotations:
          description: "插件{{$labels.k8s_app}}({{$labels.instance}}): 打开句柄数超过1000"
          value: "{{ $value }}"
      - alert: kube-proxy
        expr: process_virtual_memory_bytes{job=~"kubernetes-kube-proxy"}  > 2000000000
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "组件{{$labels.job}}({{$labels.instance}}): 使用虚拟内存超过2G"
          value: "{{ $value }}"
      - alert: scheduler
        expr: process_virtual_memory_bytes{job=~"kubernetes-schedule"}  > 2000000000
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "组件{{$labels.job}}({{$labels.instance}}): 使用虚拟内存超过2G"
          value: "{{ $value }}"
      - alert: kubernetes-controller-manager
        expr: process_virtual_memory_bytes{job=~"kubernetes-controller-manager"}  > 2000000000
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "组件{{$labels.job}}({{$labels.instance}}): 使用虚拟内存超过2G"
          value: "{{ $value }}"
      - alert: kubernetes-apiserver
        expr: process_virtual_memory_bytes{job=~"kubernetes-apiserver"}  > 2000000000
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "组件{{$labels.job}}({{$labels.instance}}): 使用虚拟内存超过2G"
          value: "{{ $value }}"
      - alert: kubernetes-etcd
        expr: process_virtual_memory_bytes{job=~"kubernetes-etcd"}  > 2000000000
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "组件{{$labels.job}}({{$labels.instance}}): 使用虚拟内存超过2G"
          value: "{{ $value }}"
      - alert: kube-dns
        expr: process_virtual_memory_bytes{k8s_app=~"kube-dns"}  > 2000000000
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "插件{{$labels.k8s_app}}({{$labels.instance}}): 使用虚拟内存超过2G"
          value: "{{ $value }}"
      - alert: HttpRequestsAvg
        expr: sum(rate(rest_client_requests_total{job=~"kubernetes-kube-proxy|kubernetes-kubelet|kubernetes-schedule|kubernetes-control-manager|kubernetes-apiservers"}[1m]))  > 1000
        for: 2s
        labels:
          team: admin
        annotations:
          description: "组件{{$labels.job}}({{$labels.instance}}): TPS超过1000"
          value: "{{ $value }}"
          threshold: "1000"   
      - alert: Pod_restarts
        expr: kube_pod_container_status_restarts_total{namespace=~"kube-system|default|monitor-sa"} > 0
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "在{{$labels.namespace}}名称空间下发现{{$labels.pod}}这个pod下的容器{{$labels.container}}被重启,这个监控指标是由{{$labels.instance}}采集的"
          value: "{{ $value }}"
          threshold: "0"
      - alert: Pod_waiting
        expr: kube_pod_container_status_waiting_reason{namespace=~"kube-system|default"} == 1
        for: 2s
        labels:
          team: admin
        annotations:
          description: "空间{{$labels.namespace}}({{$labels.instance}}): 发现{{$labels.pod}}下的{{$labels.container}}启动异常等待中"
          value: "{{ $value }}"
          threshold: "1"   
      - alert: Pod_terminated
        expr: kube_pod_container_status_terminated_reason{namespace=~"kube-system|default|monitor-sa"} == 1
        for: 2s
        labels:
          team: admin
        annotations:
          description: "空间{{$labels.namespace}}({{$labels.instance}}): 发现{{$labels.pod}}下的{{$labels.container}}被删除"
          value: "{{ $value }}"
          threshold: "1"
      - alert: Etcd_leader
        expr: etcd_server_has_leader{job="kubernetes-etcd"} == 0
        for: 2s
        labels:
          team: admin
        annotations:
          description: "组件{{$labels.job}}({{$labels.instance}}): 当前没有leader"
          value: "{{ $value }}"
          threshold: "0"
      - alert: Etcd_leader_changes
        expr: rate(etcd_server_leader_changes_seen_total{job="kubernetes-etcd"}[1m]) > 0
        for: 2s
        labels:
          team: admin
        annotations:
          description: "组件{{$labels.job}}({{$labels.instance}}): 当前leader已发生改变"
          value: "{{ $value }}"
          threshold: "0"
      - alert: Etcd_failed
        expr: rate(etcd_server_proposals_failed_total{job="kubernetes-etcd"}[1m]) > 0
        for: 2s
        labels:
          team: admin
        annotations:
          description: "组件{{$labels.job}}({{$labels.instance}}): 服务失败"
          value: "{{ $value }}"
          threshold: "0"
      - alert: Etcd_db_total_size
        expr: etcd_debugging_mvcc_db_total_size_in_bytes{job="kubernetes-etcd"} > 10000000000
        for: 2s
        labels:
          team: admin
        annotations:
          description: "组件{{$labels.job}}({{$labels.instance}})：db空间超过10G"
          value: "{{ $value }}"
          threshold: "10G"
      - alert: Endpoint_ready
        expr: kube_endpoint_address_not_ready{namespace=~"kube-system|default"} == 1
        for: 2s
        labels:
          team: admin
        annotations:
          description: "空间{{$labels.namespace}}({{$labels.instance}}): 发现{{$labels.endpoint}}不可用"
          value: "{{ $value }}"
          threshold: "1"
    - name: 物理节点状态-监控告警
      rules:
      - alert: 物理节点cpu使用率
        expr: 100-avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) by(instance)*100 > 90
        for: 2s
        labels:
          severity: ccritical
        annotations:
          summary: "{{ $labels.instance }}cpu使用率过高"
          description: "{{ $labels.instance }}的cpu使用率超过90%,当前使用率[{{ $value }}],需要排查处理" 
      - alert: 物理节点内存使用率
        expr: (node_memory_MemTotal_bytes - (node_memory_MemFree_bytes + node_memory_Buffers_bytes + node_memory_Cached_bytes)) / node_memory_MemTotal_bytes * 100 > 90
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{ $labels.instance }}内存使用率过高"
          description: "{{ $labels.instance }}的内存使用率超过90%,当前使用率[{{ $value }}],需要排查处理"
      - alert: InstanceDown
        expr: up == 0
        for: 2s
        labels:
          severity: critical
        annotations:   
          summary: "{{ $labels.instance }}: 服务器宕机"
          description: "{{ $labels.instance }}: 服务器延时超过2分钟"
      - alert: 物理节点磁盘的IO性能
        expr: 100-(avg(irate(node_disk_io_time_seconds_total[1m])) by(instance)* 100) < 60
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{$labels.mountpoint}} 流入磁盘IO使用率过高！"
          description: "{{$labels.mountpoint }} 流入磁盘IO大于60%(目前使用:{{$value}})"
      - alert: 入网流量带宽
        expr: ((sum(rate (node_network_receive_bytes_total{device!~'tap.*|veth.*|br.*|docker.*|virbr*|lo*'}[5m])) by (instance)) / 100) > 102400
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{$labels.mountpoint}} 流入网络带宽过高！"
          description: "{{$labels.mountpoint }}流入网络带宽持续5分钟高于100M. RX带宽使用率{{$value}}"
      - alert: 出网流量带宽
        expr: ((sum(rate (node_network_transmit_bytes_total{device!~'tap.*|veth.*|br.*|docker.*|virbr*|lo*'}[5m])) by (instance)) / 100) > 102400
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{$labels.mountpoint}} 流出网络带宽过高！"
          description: "{{$labels.mountpoint }}流出网络带宽持续5分钟高于100M. RX带宽使用率{{$value}}"
      - alert: TCP会话
        expr: node_netstat_Tcp_CurrEstab > 1000
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{$labels.mountpoint}} TCP_ESTABLISHED过高！"
          description: "{{$labels.mountpoint }} TCP_ESTABLISHED大于1000%(目前使用:{{$value}}%)"
      - alert: 磁盘容量
        expr: 100-(node_filesystem_free_bytes{fstype=~"ext4|xfs"}/node_filesystem_size_bytes {fstype=~"ext4|xfs"}*100) > 80
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{$labels.mountpoint}} 磁盘分区使用率过高！"
          description: "{{$labels.mountpoint }} 磁盘分区使用大于80%(目前使用:{{$value}}%)"

~~~

#### 安装alertmanager和prometheus在同一pod

- 对物理机上的etcd certs创建secret，prometheus的配置中增加了对etcd的监控，需要把cert文件挂进去。因为访问etcd需要证书

  ~~~bash
  kubectl -n monitor-sa create secret generic etcd-certs --from-file=/etc/kubernetes/pki/etcd/server.key --from-file=/etc/kubernetes/pki/etcd/server.crt --from-file=/etc/kubernetes/pki/etcd/ca.crt
  ~~~

- 创建pod

~~~yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus-server
  namespace: monitor-sa
  labels:
    app: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
      component: server
    #matchExpressions:
    #- {key: app, operator: In, values: [prometheus]}
    #- {key: component, operator: In, values: [server]}
  template:
    metadata:
      labels:
        app: prometheus
        component: server
      annotations:
        prometheus.io/scrape: 'false'
    spec:
      nodeName: node-1
      serviceAccountName: monitor
      containers:
      - name: prometheus
        image: prom/prometheus:v2.2.1
        imagePullPolicy: IfNotPresent
        command:
        - "/bin/prometheus"
        args:
        - "--config.file=/etc/prometheus/prometheus.yml"
        - "--storage.tsdb.path=/prometheus"
        - "--storage.tsdb.retention=24h"
        - "--web.enable-lifecycle"
        ports:
        - containerPort: 9090
          protocol: TCP
        volumeMounts:
        - name: prometheus-config
          mountPath: /etc/prometheus
        - name: prometheus-storage-volume
          mountPath: /prometheus/
        - name: k8s-certs
          mountPath: /var/run/secrets/kubernetes.io/k8s-certs/etcd/
      - name: alertmanager
        image: prom/alertmanager:v0.14.0
        imagePullPolicy: IfNotPresent
        args:
        - "--config.file=/etc/alertmanager/alertmanager.yml"
        - "--log.level=debug"
        ports:
        - containerPort: 9093
          protocol: TCP
          name: alertmanager
        volumeMounts:
        - name: alertmanager-config
          mountPath: /etc/alertmanager
        - name: alertmanager-storage
          mountPath: /alertmanager
        - name: localtime
          mountPath: /etc/localtime
      volumes:
        - name: prometheus-config
          configMap:
            name: prometheus-config
        - name: prometheus-storage-volume
          hostPath:
           path: /data
           type: Directory
        - name: k8s-certs
          secret:
           secretName: etcd-certs
        - name: alertmanager-config
          configMap:
            name: alertmanager
        - name: alertmanager-storage
          hostPath:
           path: /data/alertmanager
           type: DirectoryOrCreate
        - name: localtime
          hostPath:
           path: /usr/share/zoneinfo/Asia/Shanghai
~~~

- 创建svc代理alertmanager

  ~~~yaml
  ---
  apiVersion: v1
  kind: Service
  metadata:
    labels:
      name: prometheus
      kubernetes.io/cluster-service: 'true'
    name: alertmanager
    namespace: monitor-sa
  spec:
    selector:
      app: prometheus
    sessionAffinity: None
    type: NodePort
    ports:
    - name: alertmanager
      nodePort: 30066
      port: 9093
      protocol: TCP
      targetPort: 9093
  ~~~

- 可以通过nodeIP:30066端口查看alertmanager的UI界面，也可以通过prometheus的UI界面查看alerts

### 部署告警到钉钉群

#### 创建钉钉机器人

- 打开电脑版钉钉，创建一个群，创建自定义机器人，按如下步骤创建

  [钉钉自定义机器人](https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq)

  [钉钉自定义机器人接入](https://developers.dingtalk.com/document/app/custom-robot-access)

- 创建的机器人如下：

  - 群设置-->智能群助手-->添加机器人-->自定义-->添加

  - 机器人名称：test

  - 接收群组：钉钉报警测试

  - 自定义关键词：cluster1

- 点击智能群助手，可以看到刚才创建的test这个机器人，点击test，就会进入到test机器人的设置界面，拿到webhook

#### 部署钉钉webhook插件

~~~sh
#下载并解压安装包
tar zxvf prometheus-webhook-dingtalk-0.3.0.linux-amd64.tar.gz
#启动插件
cd prometheus-webhook-dingtalk-0.3.0.linux-amd64
nohup ./prometheus-webhook-dingtalk --web.listen-address="0.0.0.0:8060" --ding.profile="cluster1=<webpook>" &
~~~

#### 配置alertmanager的configmap

~~~yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: alertmanager
  namespace: monitor-sa
data:
  alertmanager.yml: |-
    global:
      resolve_timeout: 1m
      smtp_smarthost: 'smtp.163.com:25'
      smtp_from: 'xuhang969@163.com' #指定从哪个邮箱发告警
      smtp_auth_username: 'xuhang969@163.com' #邮箱地址
      smtp_auth_password: '<smtp-auth-code>' #smtp授权码
      smtp_require_tls: false
    route:  #用于配置告警分发策略
      group_by: [alertname] # alertmanager会根据group_by配置将Alert分组
      group_wait: 10s       # 组告警等待时间。也就是告警产生后等待10s再发出去，10s期间如果有同组告警一起发出
      group_interval: 10s    # 上下两组发送告警的间隔时间
      repeat_interval: 30m    # 若产生重复告警，间隔多久再重发一次告警
      receiver: cluster1  #定义谁来收告警
    receivers:
    - name: cluster1
      webhook_configs:
      - url: 'http://192.168.40.180:8060/dingtalk/cluster1/send'
        send_resolved: true
~~~

### 发送告警到企业微信

#### 注册企业微信

- 登陆网址：[企业微信](https://work.weixin.qq.com/)

#### 创建应用

- 找到应用管理，创建应用，拿到应用name、agent id、secret

#### 配置configmap

~~~yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: alertmanager
  namespace: monitor-sa
data:
  alertmanager.yml: |-
    global:
      resolve_timeout: 1m
      smtp_smarthost: 'smtp.163.com:25'
      smtp_from: 'xuhang969@163.com' #指定从哪个邮箱发告警
      smtp_auth_username: 'xuhang969@163.com' #邮箱地址
      smtp_auth_password: '<smtp-auth-code>' #smtp授权码
      smtp_require_tls: false
    route:  #用于配置告警分发策略
      group_by: [alertname] # alertmanager会根据group_by配置将Alert分组
      group_wait: 10s       # 组告警等待时间。也就是告警产生后等待10s再发出去，10s期间如果有同组告警一起发出
      group_interval: 10s    # 上下两组发送告警的间隔时间
      repeat_interval: 30m    # 若产生重复告警，间隔多久再重发一次告警
      receiver: prometheus  #定义谁来收告警
    receivers:
    - name: 'prometheus'
      wechat_configs:
      - corp_id: <企业id>
        to_user: '@all'
        agent_id: 
        api_secret: 
~~~

## 常用监控告警文件

~~~yaml
    groups:
    - name: example
      rules:
      - alert: HighNginxServerRequests
        expr: sum(irate(nginx_server_requests{instance=~"192.168.40.180:9913", code="2xx"}[5m])) by (code)>1000
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "High Nginx Server Requests"
          description: "在最近2s钟时间,nginx服务请求数达到了1000次"
    - name: 物理节点状态-监控告警
      rules:
      - alert: 物理节点cpu使用率
        expr: 100-avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) by(instance)*100 > 20
        for: 2s
        labels:
          severity: ccritical
        annotations:
          summary: "{{ $labels.instance }}cpu使用率过高"
          description: "{{ $labels.instance }}的cpu使用率超过20%,当前使用率[{{ $value }}],需要排查处理" 
      - alert: 物理节点内存使用率
        expr: (node_memory_MemTotal_bytes - (node_memory_MemFree_bytes + node_memory_Buffers_bytes + node_memory_Cached_bytes)) / node_memory_MemTotal_bytes * 100 > 50
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{ $labels.instance }}内存使用率过高"
          description: "{{ $labels.instance }}的内存使用率超过60%,当前使用率[{{ $value }}],需要排查处理"
      - alert: InstanceDown
        expr: up == 0
        for: 2s
        labels:
          severity: critical
        annotations:   
          summary: "{{ $labels.instance }}: 服务器宕机"
          description: "{{ $labels.instance }}: 服务器延时超过2分钟"
      - alert: 物理节点磁盘的IO性能
        expr: 100-(avg(irate(node_disk_io_time_seconds_total[1m])) by(instance)* 100) < 60
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{$labels.mountpoint}} 流入磁盘IO使用率过高！"
          description: "{{$labels.mountpoint }} 流入磁盘IO大于60%(目前使用:{{$value}})"
      - alert: 入网流量带宽
        expr: ((sum(rate (node_network_receive_bytes_total{device!~'tap.*|veth.*|br.*|docker.*|virbr*|lo*'}[5m])) by (instance)) / 100) > 102400
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{$labels.mountpoint}} 流入网络带宽过高！"
          description: "{{$labels.mountpoint }}流入网络带宽持续5分钟高于100M. RX带宽使用率{{$value}}"
      - alert: 出网流量带宽
        expr: ((sum(rate (node_network_transmit_bytes_total{device!~'tap.*|veth.*|br.*|docker.*|virbr*|lo*'}[5m])) by (instance)) / 100) > 102400
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{$labels.mountpoint}} 流出网络带宽过高！"
          description: "{{$labels.mountpoint }}流出网络带宽持续5分钟高于100M. RX带宽使用率{{$value}}"
      - alert: TCP会话
        expr: node_netstat_Tcp_CurrEstab > 1000
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{$labels.mountpoint}} TCP_ESTABLISHED过高！"
          description: "{{$labels.mountpoint }} TCP_ESTABLISHED大于1000%(目前使用:{{$value}}%)"
      - alert: 磁盘容量
        expr: 100-(node_filesystem_free_bytes{fstype=~"ext4|xfs"}/node_filesystem_size_bytes {fstype=~"ext4|xfs"}*100) > 80
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{$labels.mountpoint}} 磁盘分区使用率过高！"
          description: "{{$labels.mountpoint }} 磁盘分区使用大于80%(目前使用:{{$value}}%)"
      - alert: apiserver的cpu使用率大于90%
        expr: rate(process_cpu_seconds_total{job=~"kubernetes-apiserver"}[1m]) * 100 > 0
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}组件的cpu使用率超过80%"
      - alert: 容器内存使用率
        expr: (container_memory_usage_bytes / container_spec_memory_limit_bytes) * 100 > 0
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "High Container Memory Usage"
          description: "Container memory usage is above 90%."
~~~

> - https://github.com/samber/awesome-prometheus-alerts
>
>   这个项目中包含了常见组件的prometheus alerts
