## K8s部署大模型
优势：
- 资源调度与优化
- 多租户隔离与资源分配
- 弹性伸缩和负载均衡
- 高可用性和故障恢复
- 生态集成和工具链支持
### K8s管理GPU的技术架构
k8s原生不支持调度GPU的，cpu、memory等资源是kubelet从主机上采集之后发给api-server的，默认是不涉及GPU的。
想要k8s支持GPU调度，需要借助工具：
- NVIDIA Device Plugin（把GPU信息发送给kubelet，kubelet发给api-server）
- NVIDIA Container Toolkit（让容器内的应用可以访问主机上的GPU）
- NVIDIA Driver Manager（安装和管理节点上的NVIDIA驱动）
- NVIDIA DCGM（采集GPU性能指标）
### K8s GPU operator
由NVIDIA开发，自动管理所有用于配置GPU需要的工具。

## 1.1 GPU 环境准备

### 1.1.1 GPU 机器申请

若没有 GPU 机器，可以在公有云上临时申请。

- 阿里云： https://aliyun.com/
- 腾讯云： https://cloud.tencent.com/
- 华为云： https://www.huaweicloud.com/

rockylinux9.8，24GB显存，10MB公网固定带宽，100GB磁盘

### 1.1.2 驱动安装

下载地址： https://www.nvidia.com/en-us/drivers/unix/

先确认驱动版本支持目标 GPU，再选择对应的 CPU 架构（Linux x64/AMD64/EM64T 或 Linux aarch64）。本文实验使用 A10 和 `595.104.02` 驱动；不要在不同 GPU 型号上直接照搬驱动版本。

先检查现有环境。已经安装的依赖、已经禁用的 nouveau 可以跳过；`dnf update` 不是安装驱动的必要条件。若当前内核与默认启动内核不同，需要为重启后的内核也安装驱动模块，避免重启后 `nvidia-smi` 失效：

```bash
uname -r
grubby --default-kernel
rpm -q kernel-devel
lsmod | grep nouveau
```

下载完成后，把安装包上传到 GPU 服务器，之后执行如下命令即可：

```bash
# 安装依赖包
dnf install gcc make kernel-devel wget -y
# 升级系统
dnf update -y
# 重启服务器
reboot
# 禁用 Linux 驱动 nouveau
grep "blacklist nouveau" /etc/modprobe.d/blacklist.conf || echo "blacklist nouveau" >> /etc/modprobe.d/blacklist.conf
grep "options nouveau modeset=0" /etc/modprobe.d/blacklist.conf || echo "options nouveau modeset=0" >> /etc/modprobe.d/blacklist.conf
dracut --force /boot/initramfs-$(uname -r).img
dracut --force --omit-drivers nouveau
reboot
# 检查 nouveau 是否关闭
lsmod | grep nouveau # 没有结果说明已经关闭
# 安装驱动
chmod +x NVIDIA-Linux-*.run && ./NVIDIA-Linux-*.run -q -s --no-dkms --no-x-check
# 安装完成后，重启服务器
reboot
```

驱动安装完成后，执行 `nvidia-smi` 命令检查是否安装成功：

```bash
nvidia-smi
```

## 1.2 K8s 环境准备

### 1.2.1 K8s 集群部署

#### 1.2.1.1 基础配置

基本环境配置：所有节点关闭防火墙、selinux、dnsmasq、swap。服务器配置如下：

```bash
systemctl disable --now firewalld
systemctl disable --now dnsmasq
setenforce 0
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/sysconfig/selinux
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/selinux/config
# 关闭 swap 分区
swapoff -a && sysctl -w vm.swappiness=0
sed -ri '/^[^#]*swap/s/^/#/' /etc/fstab
```

配置 yum 源，安装必备工具：

```bash
sed -e 's|^mirrorlist=|#mirrorlist=|g' \
    -e 's|^#baseurl=http://dl.rockylinux.org/$contentdir|baseurl=https://mirrors.aliyun.com/rockylinux|g' \
    -i.bak \
    /etc/yum.repos.d/*.repo
dnf makecache
```

必备工具安装：

```bash
yum install wget jq psmisc vim net-tools telnet yum-utils device-mapper-persistent-data lvm2 git -y
```

#### 1.2.1.2 Runtime 安装

配置安装源：

```bash
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
```

安装 Containerd：

```sh
yum install containerd.io -y

cat <<EOF | sudo tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

sudo sysctl --system

sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
sed -i 's#SystemdCgroup = false#SystemdCgroup = true#g' /etc/containerd/config.toml
sed -i 's#k8s.gcr.io/pause#registry.cn-hangzhou.aliyuncs.com/google_containers/pause#g' /etc/containerd/config.toml
sed -i 's#registry.gcr.io/pause#registry.cn-hangzhou.aliyuncs.com/google_containers/pause#g' /etc/containerd/config.toml
sed -i 's#registry.k8s.io/pause#registry.cn-hangzhou.aliyuncs.com/google_containers/pause#g' /etc/containerd/config.toml
# 启动 Containerd
systemctl daemon-reload
systemctl enable --now containerd
```

#### 1.2.1.3 Kubernetes 部署

配置安装源：

```bash
cat <<EOF | tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.36/rpm/
enabled=1
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.36/rpm/repodata/repomd.xml.key
EOF
```

安装 Kubernetes 组件：

```bash
yum install kubeadm-1.36.0 kubelet-1.36.0 kubectl-1.36.0 -y
systemctl enable --now kubelet
kubeadm config images pull \
  --image-repository registry.cn-hangzhou.aliyuncs.com/google_containers --kubernetes-version 1.36.0
# 初始化集群
NODE_IP="$(ip -4 -o addr show dev eth0 | awk '{print $4}' | cut -d/ -f1)"
test -n "${NODE_IP}"
kubeadm init --apiserver-advertise-address "${NODE_IP}" \
  --image-repository registry.cn-hangzhou.aliyuncs.com/google_containers \
  --cri-socket unix:///run/containerd/containerd.sock \
  --kubernetes-version 1.36.0 \
  --pod-network-cidr 192.168.0.0/16
# 加入其它节点
kubeadm join 192.168.181.134:6443 --token xxx \
    --discovery-token-ca-cert-hash sha256:xxx
```

配置 kubeconfig：

```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

安装 Addons：

```bash
yum install git -y

git clone https://gitee.com/dukuan/k8s-ha-install.git
cd k8s-ha-install/
git checkout manual-installation-v1.36.x
cd single/
# 本文只需要 CNI 和 metrics-server，不批量安装目录中的 Dashboard 等额外组件。
sed -i 's#quay.io/calico/#m.daocloud.io/quay.io/calico/#g' calico.yaml
kubectl apply --server-side -f calico.yaml
kubectl apply --server-side -f comp.yaml
```

镜像代理返回 `502` 时，先确认同版本官方镜像是否能访问，不要直接换成其他版本。例如本次上海节点可以从 Quay 拉取 Calico controller，使用以下命令回退到官方地址：

```bash
kubectl set image deployment/calico-kube-controllers -n kube-system \
  calico-kube-controllers=quay.io/calico/kube-controllers:v3.32.1
kubectl rollout status deployment/calico-kube-controllers -n kube-system --timeout=5m
```

解除污点：

```bash
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
```

查看集群状态：

```bash
kubectl top node
kubectl get node
```

### 1.2.2 GPU Operator 部署

#### 1.2.2.1 Helm 安装

官方安装文档： https://helm.sh/docs/intro/install/
Helm 安装包： https://github.com/helm/helm/releases

安装 Helm：

```bash
# 首先下载安装包
mkdir helm
cd helm
wget https://get.helm.sh/helm-v4.2.2-linux-amd64.tar.gz
ls
tar xf helm-v4.2.2-linux-amd64.tar.gz
mv linux-amd64/helm /usr/local/bin/
helm version
```

创建 Namespace：

```bash
kubectl create ns gpu-operator
kubectl label --overwrite ns gpu-operator pod-security.kubernetes.io/enforce=privileged
```

#### 1.2.2.2 部署 GPU Operator

添加仓库：

```bash
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia \
    && helm repo update
```

下载安装包：

```bash
helm pull nvidia/gpu-operator --version v26.7.2
tar xf gpu-operator-v26.7.2.tgz
cd gpu-operator/
```

国内机器需要修改 values 文件中的仓库地址：

```bash
vim charts/node-feature-discovery/values.yaml

image:
  repository: m.daocloud.io/registry.k8s.io/nfd/node-feature-discovery
```

如果服务器已经按照 1.1.2 安装了 NVIDIA 驱动，需要通过 `driver.enabled=false` 禁止 GPU Operator 重复安装驱动，避免覆盖现有驱动或产生版本冲突。本文固定使用 GPU Operator `v26.7.2`；该版本会识别节点上的 Containerd，Chart 已不再使用旧的 `operator.defaultRuntime` 参数：

```bash
helm install gpu-operator . \
  -n gpu-operator \
  --create-namespace \
  --set driver.enabled=false
```

查看 Pod 状态：

```bash
kubectl get po -n gpu-operator
```

所有 Pod 启动完成后，即可在 Kubernetes 的节点状态中，看到 GPU 资源：

```bash
kubectl get po -n gpu-operator
```

查看 GPU 资源：

```bash
kubectl describe node | grep Allocatable: -A 10
```

**重启后 GPU 资源变为 `0` 的处理：** 如果 `nvidia-device-plugin` 日志出现 `couldn't initialize inotify: too many open files`，说明主机的 inotify 实例数已达到上限。先确认限制和当前用量，再提高限制并重建 device-plugin Pod：

`fs.inotify.max_user_instances` 限制的是同一用户可创建的 inotify 实例数。在没有启用用户命名空间隔离的常见配置下，多个以 root 运行的系统服务和容器会共同消耗宿主机 UID 0 的额度。这与 GPU 显存无关，也不能仅凭 `too many open files` 就认定是 `ulimit -n` 太小；应结合日志触发点、inotify 用量和进程文件描述符限制判断。下面的 FD 统计用于辅助排查，不是精确的去重实例数。

```bash
sysctl fs.inotify.max_user_instances
find /proc/[0-9]*/fd -lname anon_inode:inotify 2>/dev/null | wc -l

echo 'fs.inotify.max_user_instances = 1024' > /etc/sysctl.d/99-kubernetes-inotify.conf
sysctl --system

kubectl delete pod -n gpu-operator -l app=nvidia-device-plugin-daemonset
kubectl wait -n gpu-operator \
  --for=condition=Ready pod \
  -l app=nvidia-device-plugin-daemonset \
  --timeout=180s
kubectl get node -o jsonpath='{.items[0].status.allocatable.nvidia\.com/gpu}{"\n"}'
```

创建 GPU 测试服务：

```bash
tee test.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: cuda-vectoradd
spec:
  restartPolicy: OnFailure
  containers:
  - name: cuda-vectoradd
    image: "nvcr.io/nvidia/k8s/cuda-sample:vectoradd-cuda12.5.0-ubuntu22.04"
    resources:
      limits:
        nvidia.com/gpu: 1
EOF
```

```bash
kubectl create -f test.yaml
```

查看日志：

```bash
kubectl logs cuda-vectoradd
# 确认日志包含 Test PASSED 后删除临时测试 Pod
kubectl delete pod cuda-vectoradd
```

### 1.2.3 动态存储配置

官方文档： https://longhorn.io/docs/1.12.0/deploy/install/install-with-helm/

#### 1.2.3.1 Longhorn

Longhorn 依赖 iSCSI 和 NFS 客户端。Rocky Linux 需要安装 `iscsi-initiator-utils` 和 `nfs-utils`，启用 `iscsid`，并加载 `dm_crypt` 内核模块。将模块写入 `modules-load.d` 后，服务器重启时也会自动加载：

```bash
dnf install iscsi-initiator-utils nfs-utils -y
systemctl enable --now iscsid
modprobe dm_crypt
echo dm_crypt > /etc/modules-load.d/longhorn.conf

# 检查服务和模块状态
systemctl is-active iscsid
lsmod | grep dm_crypt
```

添加 Longhorn Helm 仓库：

```bash
helm repo add longhorn https://charts.longhorn.io
helm repo update
helm pull longhorn/longhorn --version 1.12.0
```

安装 Longhorn：

```bash
tar xf longhorn-1.12.0.tgz
cd longhorn/
# 国内机器，将 global.imageRegistry 设置为 m.daocloud.io/docker.io
# 针对单节点，把默认卷副本数和默认 StorageClass 副本数设为 1
helm install longhorn . \
  -n longhorn-system \
  --create-namespace \
  --set global.imageRegistry=m.daocloud.io/docker.io \
  --set defaultSettings.defaultReplicaCount=1 \
  --set persistence.defaultClassReplicaCount=1
```

查看服务状态：

```bash
kubectl get po -n longhorn-system
```

等待服务启动后，创建 PVC 和 Pod 测试。首先创建 PVC：

```bash
tee longhorn-pvc-test.yaml <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: longhorn-redis-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: longhorn
  resources:
    requests:
      storage: 1Gi
EOF
```

```bash
kubectl create -f longhorn-pvc-test.yaml
kubectl get pvc
```

创建测试 Pod：

```bash
tee longhorn-pod-test.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: volume-test
spec:
  containers:
  - name: volume-test
    image: m.daocloud.io/docker.io/library/busybox:1.36.1
    imagePullPolicy: IfNotPresent
    command: ["sh", "-c", "sleep 3600"]
    volumeMounts:
    - name: volv
      mountPath: /data
  volumes:
  - name: volv
    persistentVolumeClaim:
      claimName: longhorn-redis-pvc
EOF
```

```bash
kubectl create -f longhorn-pod-test.yaml
```

写入、读取并验证 Pod 重建后的持久化。以下 PVC 仅用于本次测试，不应存放业务数据；测试完成后删除 Pod 和专用测试 PVC：

```bash
kubectl wait --for=condition=Ready pod/volume-test --timeout=5m
kubectl exec volume-test -- sh -ceu \
  'printf LONGHORN_OK > /data/test.txt; sync; test "$(cat /data/test.txt)" = LONGHORN_OK'
kubectl delete pod volume-test
kubectl create -f longhorn-pod-test.yaml
kubectl wait --for=condition=Ready pod/volume-test --timeout=5m
kubectl exec volume-test -- sh -ceu \
  'test "$(cat /data/test.txt)" = LONGHORN_OK; echo LONGHORN_PERSISTENCE_OK'
kubectl delete pod volume-test
kubectl delete pvc longhorn-redis-pvc
```

## 1.3 模型部署

### 1.3.1 模型文件预下载

环境准备好后，就可以通过 VLLM 部署模型。当前模型已经下载到 Kubernetes 节点的 `/data/models/Qwen3.5-4B`，实际大小约为 8.8 GiB，因此创建一个 12 GiB 的 Longhorn PVC：

```bash
tee qwen35-4b-pvc.yaml <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: qwen35-4b-pvc
  namespace: models
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: longhorn
  resources:
    requests:
      storage: 12Gi # 根据模型实际大小和预留空间进行调整
EOF
```

创建 PVC：

```bash
kubectl create namespace models --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f qwen35-4b-pvc.yaml
kubectl wait --for=jsonpath='{.status.phase}'=Bound \
  pvc/qwen35-4b-pvc -n models --timeout=5m
```

### 模型文件本地导入
如果本地已经有下载好的模型文件：
不要直接向 `/var/lib/longhorn` 写入文件。应创建一个临时 Job，同时将节点上的模型目录以只读 `hostPath` 挂载为源目录，并将 PVC 挂载为目标目录。Job 完成复制。

```bash
tee model-import-job.yaml <<'EOF'
apiVersion: batch/v1
kind: Job
metadata:
  name: qwen35-4b-model-import
  namespace: models
spec:
  backoffLimit: 0
  template:
    spec:
      nodeSelector:
        kubernetes.io/hostname: MODEL_NODE_PLACEHOLDER
      restartPolicy: Never
      containers:
        - name: importer
          image: m.daocloud.io/docker.io/library/busybox:1.36.1
          command: ["sh", "-ceu"]
          args:
            - |
              target=/target/Qwen/Qwen3.5-4B

              if [ -e "${target}" ] && [ -n "$(ls -A "${target}" 2>/dev/null)" ]; then
                echo "目标目录非空，停止以避免覆盖已有模型"
                exit 1
              fi

              mkdir -p "${target}"
              cp -a /source/. "${target}/"
              sync

              (
                cd /source
                find . -type f -exec sha256sum {} \; | sort
              ) > /tmp/source.sha256

              (
                cd "${target}"
                find . -type f -exec sha256sum {} \; | sort
              ) > /tmp/target.sha256

              cmp /tmp/source.sha256 /tmp/target.sha256
              echo "模型复制及 SHA256 校验完成"
              du -sh "${target}"
              find "${target}" -type f | wc -l
          volumeMounts:
            - name: local-model
              mountPath: /source
              readOnly: true
            - name: model-storage
              mountPath: /target
      volumes:
        - name: local-model
          hostPath:
            path: /data/models/Qwen3.5-4B
            type: Directory
        - name: model-storage
          persistentVolumeClaim:
            claimName: qwen35-4b-pvc
EOF
```

创建导入 Job 并等待完成：

```bash
# 单节点实验：从实际节点标签读取 hostname，不要照搬其他 ECS 的节点名。
MODEL_NODE="$(kubectl get nodes -o jsonpath='{.items[0].metadata.labels.kubernetes\.io/hostname}')"
test -n "${MODEL_NODE}"
sed "s/MODEL_NODE_PLACEHOLDER/${MODEL_NODE}/g" model-import-job.yaml \
  | kubectl apply -f -
kubectl wait --for=condition=complete \
  job/qwen35-4b-model-import -n models --timeout=30m
```

查看复制和 SHA256 校验结果：

```bash
kubectl logs job/qwen35-4b-model-import -n models
```

确认成功后删除临时 Job 及其 Pod，但保留 PVC 中的模型文件：

```bash
kubectl delete job qwen35-4b-model-import -n models
kubectl get pvc qwen35-4b-pvc -n models
```

后续部署将该 PVC 挂载到 `/data/modelscope` 后，模型路径仍为 `/data/modelscope/Qwen/Qwen3.5-4B`。本地源目录应保留到模型服务启动和推理验证成功后，再根据磁盘空间情况决定是否删除。

### 1.3.2 部署模型

文档： https://docs.vllm.ai/en/latest/deployment/k8s/

- 仅部署一个模型时，用 YAML 部署即可
- 如果有分布式计算、模型微调、调度等需求，可以用一些开源框架比如KServe，llm-d等： https://docs.vllm.ai/en/latest/deployment/integrations/kserve/

确认模型 PVC 已经处于 `Bound` 状态：

```bash
kubectl get pvc qwen35-4b-pvc -n models
```

- 创建 `qwen35-vllm.yaml`，在同一个多文档 YAML 中定义 Secret、Deployment 和 Service。Secret 中只保留 `VLLM_API_KEY_PLACEHOLDER` 占位符，应用时在内存中替换，真实 API Key 不写入文章或 YAML 文件。
- 镜像入口点已经是 `vllm serve`，因此通过 `args` 传入参数。vLLM 0.23.0 弃用了 `--model`，模型路径必须作为 `args` 的第一个位置参数。
- 本地模型通过 PVC 挂载，并设置 `HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1`，避免启动时重新从网络下载模型。GPU 设备交给 Device Plugin 分配，不硬编码 `CUDA_VISIBLE_DEVICES`。
- 单节点只有一块 GPU，且 PVC 为 `ReadWriteOnce`，Deployment 使用 `Recreate`，避免 RollingUpdate 时新旧 Pod 争用同一块 GPU 和 PVC：

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: vllm-api-key
  namespace: models
type: Opaque
stringData:
  api-key: "VLLM_API_KEY_PLACEHOLDER" # 应用时替换，不要把真实密钥提交到 Git
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qwen3-5-4b-deployment
  namespace: models
  labels:
    app: qwen3-5-4b
spec:
  replicas: 1
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: qwen3-5-4b
  template:
    metadata:
      labels:
        app: qwen3-5-4b
    spec:
      containers:
        - name: qwen3-5-4b
          image: registry.cn-beijing.aliyuncs.com/dotbalo/vllm-openai@sha256:3a1e7f5904e1a1192a02aa0086ceaffc33985d7044c7bb25b3a43d61bdbe3ac0
          imagePullPolicy: IfNotPresent
          args:
            - "/data/modelscope/Qwen/Qwen3.5-4B" # PVC 挂载点下的模型目录
            - "--port"
            - "8080"
            - "--served-model-name"
            - "Qwen3.5-4B"
            - "--gpu-memory-utilization"
            - "0.9"
            - "--max-model-len"
            - "16384"
            - "--max-num-batched-tokens"
            - "16384"
          ports:
            - name: http
              containerPort: 8080
          env:
            - name: TZ
              value: "Asia/Shanghai"
            - name: LANG
              value: "C.UTF-8"
            - name: LC_ALL
              value: "C.UTF-8"
            - name: HF_HUB_OFFLINE
              value: "1"
            - name: TRANSFORMERS_OFFLINE
              value: "1"
            - name: VLLM_API_KEY
              valueFrom:
                secretKeyRef:
                  name: vllm-api-key
                  key: api-key
          resources:
            limits:
              nvidia.com/gpu: 1
            requests:
              nvidia.com/gpu: 1
          volumeMounts:
            - name: model-storage
              mountPath: /data/modelscope
              readOnly: true
            - name: dshm
              mountPath: /dev/shm
          startupProbe:
            httpGet:
              path: /health
              port: http
            # 给予最长 15 分钟（900 秒）的启动时间，每 10 秒探测一次
            # 如果 90 次（900/10）探测都失败，容器才会被重启
            failureThreshold: 90
            periodSeconds: 10
            timeoutSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: http
            periodSeconds: 30
            timeoutSeconds: 10
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health
              port: http
            periodSeconds: 15
            timeoutSeconds: 10
            failureThreshold: 3
      volumes:
        - name: model-storage
          persistentVolumeClaim:
            claimName: qwen35-4b-pvc
        - name: dshm
          emptyDir:
            medium: Memory
            sizeLimit: 4Gi
---
apiVersion: v1
kind: Service
metadata:
  name: qwen3-5-4b-service
  namespace: models
spec:
  selector:
    app: qwen3-5-4b
  ports:
    - name: http
      protocol: TCP
      port: 8080
      targetPort: http
  type: NodePort # 非必须
```

生成随机 API Key，在标准输出管道中替换占位符并直接提交给 API Server。由于生成的是十六进制字符串，可以安全地作为 `sed` 替换值；不要直接执行 `kubectl apply -f qwen35-vllm.yaml`，否则会把占位符保存为真实密钥：

```bash
DEPLOYMENT_EXISTS=false
kubectl get deployment qwen3-5-4b-deployment -n models >/dev/null 2>&1 \
  && DEPLOYMENT_EXISTS=true

VLLM_API_KEY="$(openssl rand -hex 32)"
sed "s/VLLM_API_KEY_PLACEHOLDER/${VLLM_API_KEY}/g" qwen35-vllm.yaml \
  | kubectl apply -f -
unset VLLM_API_KEY

# 现有部署轮换 Secret 后，必须重建 Pod 才能读取新的环境变量
if [ "${DEPLOYMENT_EXISTS}" = true ]; then
  kubectl rollout restart deployment/qwen3-5-4b-deployment -n models
fi
unset DEPLOYMENT_EXISTS

kubectl rollout status deployment/qwen3-5-4b-deployment \
  -n models \
  --timeout=15m
```

查看启动状态：

```bash
kubectl get po,pvc,svc -n models -o wide
kubectl logs deployment/qwen3-5-4b-deployment -n models --tail=100
```

模型访问测试。NodePort 由 Kubernetes 动态分配，不要写死示例端口；`enable_thinking=false` 用于让这次连通性测试只返回最终答案：

```bash
NODE_IP="$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')"
NODE_PORT="$(kubectl get service qwen3-5-4b-service \
  -n models \
  -o jsonpath='{.spec.ports[0].nodePort}')"
VLLM_API_KEY="$(kubectl get secret vllm-api-key \
  -n models \
  -o jsonpath='{.data.api-key}' | base64 -d)"

curl -sS "http://${NODE_IP}:${NODE_PORT}/v1/chat/completions" \
  -H "Authorization: Bearer ${VLLM_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-4B",
    "stream": false,
    "temperature": 0,
    "max_tokens": 64,
    "chat_template_kwargs": {"enable_thinking": false},
    "messages": [
      {"role": "user", "content": "只回复：K8S_VLLM_OK"}
    ]
  }'

unset VLLM_API_KEY
```

## 1.4 LiteLLM 高可用落地

![image.png](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260914221055928.png)

### 1.4.1 高可用 Redis 部署

参考文档：

- LiteLLM 配置：https://docs.litellm.com.cn/docs/proxy/config_settings
- Bitnami Redis Helm Chart：https://github.com/bitnami/charts/tree/main/bitnami/redis

需要部署两个相互独立的 Redis Release：

- `redis`：3 个 Redis + Sentinel Pod，用作 LiteLLM 响应缓存（`litellm_settings.cache` 和 `cache_params`）。
- `redis-single`：单节点 Redis，用作 LiteLLM 路由限流（`router_settings`）和跨 Pod 协调。本文将它与响应缓存分开配置。

> [!NOTE]
> 本文是单节点 K8s 集群。3 个 Sentinel Pod 可以处理 Redis 进程或 Pod 故障，但都运行在同一台 ECS 上，无法提供节点级高可用；Longhorn 卷副本数同样应保持为 `1`。

先创建命名空间和两个独立的认证 Secret。下面的命令只在 Secret 不存在时生成密码，重复执行不会静默轮换已有密码：

```bash
kubectl create namespace litellm --dry-run=client -o yaml | kubectl apply -f -

for secret_name in redis-sentinel-auth redis-standalone-auth; do
  if ! kubectl get secret "${secret_name}" -n litellm >/dev/null 2>&1; then
    password_file=$(mktemp)
    chmod 600 "${password_file}"
    openssl rand -hex 32 | tr -d '\n' > "${password_file}"
    kubectl create secret generic "${secret_name}" -n litellm \
      --from-file=redis-password="${password_file}"
    shred -u "${password_file}"
  fi
done
```

只有出现磁盘调度失败时才检查以下设置。之前的实验节点根盘仅剩约 17 GiB，低于 Longhorn 默认的 25% 最小剩余空间阈值，创建卷时出现了 `ReplicaSchedulingFailure: disks are unavailable`。磁盘空间充足的新节点不需要降低阈值；遇到这种情况应先确认剩余容量并优先扩容，下面的 `10%` 仅是经确认后的实验环境示例，不是必做步骤：

```bash
kubectl -n longhorn-system get settings.longhorn.io \
  storage-minimal-available-percentage

kubectl -n longhorn-system patch settings.longhorn.io \
  storage-minimal-available-percentage \
  --type=merge -p '{"value":"10"}'
```

> [!WARNING]
> 该设置影响整个 Longhorn 集群，不是 Redis Helm 参数。只有确认磁盘仍有足够空间、且卷确实因 25% 阈值无法调度时才应降低；生产环境应优先扩容磁盘并保留更高的安全余量。

#### Redis Sentinel - 缓存用

使用 Bitnami Redis Chart `28.1.0` 部署 3 个 Redis + Sentinel Pod，Sentinel master set 为 `mymaster`、quorum 为 `2`。每个 Redis 数据 PVC 均从默认的 `8Gi` 调整为 `1Gi`：

```bash
helm upgrade --install redis \
  oci://m.daocloud.io/docker.io/bitnamicharts/redis \
  --version 28.1.0 \
  --namespace litellm \
  --set global.imageRegistry=m.daocloud.io/docker.io \
  --set global.defaultStorageClass=longhorn \
  --set global.security.allowInsecureImages=true \
  --set image.digest=sha256:ffa455a3ad00bccc24dfde113ef55329dde687da242e9feb6ccd2b30eb93e8f3 \
  --set sentinel.image.digest=sha256:97433fd14ea945c164ac514c162e2d2a017e9044fdc7ec46abf12a92f4660770 \
  --set architecture=replication \
  --set sentinel.enabled=true \
  --set sentinel.masterSet=mymaster \
  --set sentinel.quorum=2 \
  --set replica.replicaCount=3 \
  --set master.persistence.storageClass=longhorn \
  --set master.persistence.size=1Gi \
  --set replica.persistence.storageClass=longhorn \
  --set replica.persistence.size=1Gi \
  --set auth.existingSecret=redis-sentinel-auth \
  --set auth.existingSecretPasswordKey=redis-password \
  --wait --timeout 10m
```

`global.security.allowInsecureImages=true` 是 Bitnami Chart 使用自定义镜像仓库时所需的镜像校验开关，并不表示关闭 Redis 密码认证。镜像仍固定到了本次验证通过的不可变 digest。

查看 Pod、Service 和 PVC 状态：

```bash
helm status redis -n litellm
kubectl get sts,pod,svc,pvc -n litellm \
  -l app.kubernetes.io/instance=redis
```

验证 Sentinel master、quorum、replica 数量和读写；测试键会在最后删除，不需要创建临时测试 Pod：

```bash
kubectl exec redis-node-0 -n litellm -c redis -- sh -ceu '
  export REDISCLI_AUTH="$(cat "$REDIS_PASSWORD_FILE")"
  redis-cli --raw -h redis -p 26379 SENTINEL ckquorum mymaster
  master=$(redis-cli --raw -h redis -p 26379 \
    SENTINEL get-master-addr-by-name mymaster | head -n 1)
  test -n "$master"
  printf "Sentinel master: %s\n" "$master"
  redis-cli --raw -h redis -p 26379 SENTINEL replicas mymaster | grep -c "^name$"
  redis-cli --raw -h "$master" SET litellm-sentinel-test ok
  redis-cli --raw -h "$master" GET litellm-sentinel-test
  redis-cli --raw -h "$master" DEL litellm-sentinel-test
'
```

供 LiteLLM 使用的集群内地址为：

- Sentinel：`redis.litellm.svc.cluster.local:26379`
- Sentinel master set：`mymaster`
- Redis 服务：`redis.litellm.svc.cluster.local:6379`

`redis:6379` 的 Service 可能命中 replica。写入应使用 Sentinel 发现的 master 地址，LiteLLM 响应缓存也应按 Sentinel 方式连接。

#### 单节点 Redis - 限流用

使用同一个 Chart 的 `standalone` 架构部署独立 Redis，数据 PVC 同样设置为 `1Gi`：

```bash
helm upgrade --install redis-single \
  oci://m.daocloud.io/docker.io/bitnamicharts/redis \
  --version 28.1.0 \
  --namespace litellm \
  --set global.imageRegistry=m.daocloud.io/docker.io \
  --set global.defaultStorageClass=longhorn \
  --set global.security.allowInsecureImages=true \
  --set image.digest=sha256:ffa455a3ad00bccc24dfde113ef55329dde687da242e9feb6ccd2b30eb93e8f3 \
  --set architecture=standalone \
  --set master.persistence.storageClass=longhorn \
  --set master.persistence.size=1Gi \
  --set auth.existingSecret=redis-standalone-auth \
  --set auth.existingSecretPasswordKey=redis-password \
  --wait --timeout 10m
```

验证状态和读写，随后删除测试键：

```bash
helm status redis-single -n litellm
kubectl get sts,pod,svc,pvc -n litellm \
  -l app.kubernetes.io/instance=redis-single

kubectl exec redis-single-master-0 -n litellm -c redis -- sh -ceu '
  export REDISCLI_AUTH="$(cat "$REDIS_PASSWORD_FILE")"
  redis-cli --raw SET litellm-rate-limit-test ok
  redis-cli --raw GET litellm-rate-limit-test
  redis-cli --raw DEL litellm-rate-limit-test
'
```

供 LiteLLM 限流使用的集群内地址为 `redis-single-master.litellm.svc.cluster.local:6379`。

### 1.4.2 高可用 Postgresql 部署

使用 Bitnami `postgresql-ha` Chart `16.3.2`，部署 3 个 PostgreSQL/repmgr 实例和 2 个 Pgpool。数据库名为 `litellm`，每个 PostgreSQL PVC 为 `8Gi`，使用单副本 Longhorn。

> [!WARNING]
> 本次经确认使用 `bitnamilegacy` 的 PostgreSQL `17.6.0` 和 Pgpool `4.6.3` 镜像，仅用于实验。这些公开旧镜像不再获得安全更新，生产环境应选用仍在维护的方案。所有实例都在同一台 ECS 上，不能提供节点级高可用。

先生成认证 Secret。密码不带尾部换行，也不写入 Helm values；已有 Secret 不会被重复生成的密码覆盖：

```bash
kubectl create namespace litellm --dry-run=client -o yaml | kubectl apply --server-side -f -
if ! kubectl get secret postgresql-ha-auth -n litellm >/dev/null 2>&1; then
  secret_dir=$(mktemp -d)
  for key in password repmgr-password admin-password sr-check-password; do
    openssl rand -hex 32 | tr -d '\n' > "${secret_dir}/${key}"
  done
  kubectl create secret generic postgresql-ha-auth -n litellm \
    --from-file="${secret_dir}"
  for key in password repmgr-password admin-password sr-check-password; do
    shred -u "${secret_dir}/${key}"
  done
  rmdir "${secret_dir}"
fi
```

保存为 `postgresql-ha-values.yaml`。单节点使用软反亲和性，不能设置必须分散到不同节点的硬反亲和性：

```yaml
global:
  imageRegistry: m.daocloud.io/docker.io
  security:
    allowInsecureImages: true
postgresql:
  image:
    repository: bitnamilegacy/postgresql-repmgr
    tag: 17.6.0-debian-12-r2
    digest: sha256:9336b076c7f846043872a9eacf8496967c5c3ba9028c80dcd8a81a148a8cfa65
  replicaCount: 3
  podAntiAffinityPreset: soft
  username: postgres
  database: litellm
  existingSecret: postgresql-ha-auth
pgpool:
  image:
    repository: bitnamilegacy/pgpool
    tag: 4.6.3-debian-12-r0
    digest: sha256:663b1cbe74bd10ff963ef43e8cc5dfc4032e11c10c6e72297b6c312434fdef17
  replicaCount: 2
  podAntiAffinityPreset: soft
  existingSecret: postgresql-ha-auth
persistence:
  enabled: true
  storageClass: longhorn
  size: 8Gi
volumePermissions:
  enabled: false
metrics:
  enabled: false
```

下载 Chart 并部署；离线准备时，可将相同的 `.tgz` 和 values 文件上传后直接使用：

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update bitnami
helm pull bitnami/postgresql-ha --version 16.3.2
helm upgrade --install pg ./postgresql-ha-16.3.2.tgz \
  -n litellm -f postgresql-ha-values.yaml

kubectl rollout status statefulset/pg-postgresql-ha-postgresql -n litellm --timeout=15m
kubectl rollout status deployment/pg-postgresql-ha-pgpool -n litellm --timeout=15m
kubectl get sts,deploy,pod,svc,pvc -n litellm
```

通过 Pgpool 连接数据库。密码在 Pod 内读取挂载的 Secret 文件，不作为 `kubectl exec` 的参数传入：

```bash
kubectl exec pg-postgresql-ha-postgresql-0 -n litellm -c postgresql -- bash -ceu '
  export PGPASSWORD="$(cat "$POSTGRES_PASSWORD_FILE")"
  psql -v ON_ERROR_STOP=1 -U postgres -h pg-postgresql-ha-pgpool -d litellm \
    -c "SELECT current_database(), version();"
'
```

再分别查看 3 个实例的实时角色和复制状态。`pg_is_in_recovery()` 为 `f` 的是 primary，为 `t` 的是 standby；primary 的 `pg_stat_replication` 应显示 2 个 `streaming` 连接。这里使用 SQL 验证，避免旧镜像中直接 `kubectl exec repmgr` 时因 UID 缺少 passwd 映射而出现 `could not get current user name`：

```bash
for ordinal in 0 1 2; do
  echo "postgresql-${ordinal}"
  kubectl exec "pg-postgresql-ha-postgresql-${ordinal}" -n litellm -c postgresql -- bash -ceu '
    export PGPASSWORD="$(cat "$POSTGRES_PASSWORD_FILE")"
    psql -U postgres -d postgres \
      -c "SELECT pg_is_in_recovery();" \
      -c "SELECT application_name, state, sync_state FROM pg_stat_replication;"
  '
done
```

LiteLLM 使用的数据库入口为 `pg-postgresql-ha-pgpool.litellm.svc.cluster.local:5432`。

### 1.4.3 部署 LiteLLM

部署 2 个 LiteLLM `v1.105.1` Pod，共用 PostgreSQL 数据库、Sentinel 响应缓存和独立 Redis 路由限流实例。模型后端使用 1.3.2 的集群内 Service，不再填写示例 IP 或 API Key。

先创建 `litellm-auth`，并把模型服务的 API Key 复制到 `litellm` 命名空间。Secret 不能跨命名空间直接引用；真实密钥只提交给 Kubernetes，不写入文章或部署 YAML。`LITELLM_SALT_KEY` 用于加密数据库中的凭据，部署后不要随意轮换：

```bash
if ! kubectl get secret litellm-auth -n litellm >/dev/null 2>&1; then
  secret_dir=$(mktemp -d)
  db_password=$(kubectl get secret postgresql-ha-auth -n litellm \
    -o jsonpath='{.data.password}' | base64 -d)
  printf 'postgresql://postgres:%s@pg-postgresql-ha-pgpool.litellm.svc.cluster.local:5432/litellm' \
    "${db_password}" > "${secret_dir}/DATABASE_URL"
  unset db_password
  printf 'sk-%s' "$(openssl rand -hex 32)" > "${secret_dir}/LITELLM_MASTER_KEY"
  printf 'sk-%s' "$(openssl rand -hex 32)" > "${secret_dir}/LITELLM_SALT_KEY"
  printf admin > "${secret_dir}/UI_USERNAME"
  openssl rand -hex 24 | tr -d '\n' > "${secret_dir}/UI_PASSWORD"
  kubectl create secret generic litellm-auth -n litellm --from-file="${secret_dir}"
  for key in DATABASE_URL LITELLM_MASTER_KEY LITELLM_SALT_KEY UI_USERNAME UI_PASSWORD; do
    shred -u "${secret_dir}/${key}"
  done
  rmdir "${secret_dir}"
fi

if ! kubectl get secret vllm-api-key -n litellm >/dev/null 2>&1; then
  kubectl get secret vllm-api-key -n models -o json \
    | jq 'del(.metadata.uid,.metadata.resourceVersion,.metadata.creationTimestamp,.metadata.managedFields,.metadata.annotations) | .metadata.namespace="litellm"' \
    | kubectl apply -f -
fi
```

保存以下配置为 `litellm-config.yaml`。响应缓存位于 `litellm_settings.cache_params`，不要写成 `general_settings.cache`；Sentinel 自身和 Redis 数据连接都需要密码。路由限流和跨 Pod 协调使用独立的单节点 Redis：

```yaml
model_list:
  - model_name: Qwen3.5-4B
    litellm_params:
      model: openai/Qwen3.5-4B
      api_base: http://qwen3-5-4b-service.models.svc.cluster.local:8080/v1
      api_key: os.environ/VLLM_API_KEY
litellm_settings:
  cache: true
  cache_params:
    type: redis
    service_name: mymaster
    sentinel_nodes:
      - [redis-node-0.redis-headless.litellm.svc.cluster.local, 26379]
      - [redis-node-1.redis-headless.litellm.svc.cluster.local, 26379]
      - [redis-node-2.redis-headless.litellm.svc.cluster.local, 26379]
    sentinel_password: os.environ/REDIS_SENTINEL_PASSWORD
    password: os.environ/REDIS_SENTINEL_PASSWORD
    ttl: 600
router_settings:
  redis_host: redis-single-master.litellm.svc.cluster.local
  redis_port: 6379
  redis_password: os.environ/REDIS_PASSWORD
general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: os.environ/DATABASE_URL
  database_connection_pool_limit: 10
  coordination_redis:
    host: redis-single-master.litellm.svc.cluster.local
    port: 6379
    password: os.environ/REDIS_PASSWORD
```

创建 ConfigMap：

```bash
kubectl create configmap litellm-config -n litellm \
  --from-file=config.yaml=litellm-config.yaml \
  --dry-run=client -o yaml | kubectl apply -f -
```

先单独执行数据库迁移，避免两个 LiteLLM Pod 同时修改表结构。保存为 `litellm-migrate.yaml`；迁移 Job 和服务使用相同的镜像 digest：

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: litellm-db-migrate
  namespace: litellm
spec:
  backoffLimit: 0
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: ghcr.io/berriai/litellm@sha256:b7b9e2c306343721802253d0dd9436b9634a2eb4e14da7c7cf06c5c7b7530802 # v1.105.1
          imagePullPolicy: IfNotPresent
          args: [--skip_server_startup]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: litellm-auth
                  key: DATABASE_URL
            - name: DISABLE_SCHEMA_UPDATE
              value: "false"
          resources:
            requests:
              cpu: 100m
              memory: 512Mi
            limits:
              memory: 2Gi
```

```bash
kubectl apply -f litellm-migrate.yaml
kubectl wait --for=condition=complete job/litellm-db-migrate -n litellm --timeout=15m
```

保存以下内容为 `litellm-deploy.yaml`。服务 Pod 禁止自动更新数据库 schema，通过 Secret 注入 API Key 和认证信息：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: litellm
  namespace: litellm
spec:
  replicas: 2
  selector:
    matchLabels:
      app: litellm
  template:
    metadata:
      labels:
        app: litellm
    spec:
      containers:
        - name: litellm
          image: ghcr.io/berriai/litellm@sha256:b7b9e2c306343721802253d0dd9436b9634a2eb4e14da7c7cf06c5c7b7530802 # v1.105.1
          imagePullPolicy: IfNotPresent
          args: [--config, /app/config.yaml, --port, "4000", --num_workers, "1"]
          ports:
            - name: http
              containerPort: 4000
          envFrom:
            - secretRef:
                name: litellm-auth
          env:
            - name: VLLM_API_KEY
              valueFrom:
                secretKeyRef:
                  name: vllm-api-key
                  key: api-key
            - name: REDIS_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: redis-standalone-auth
                  key: redis-password
            - name: REDIS_SENTINEL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: redis-sentinel-auth
                  key: redis-password
            - name: STORE_MODEL_IN_DB
              value: "True"
            - name: DISABLE_SCHEMA_UPDATE
              value: "true"
          resources:
            requests:
              cpu: 200m
              memory: 512Mi
            limits:
              memory: 2Gi
          startupProbe:
            httpGet:
              path: /health/liveliness
              port: http
            periodSeconds: 10
            failureThreshold: 60
          readinessProbe:
            httpGet:
              path: /health/readiness
              port: http
            periodSeconds: 10
            timeoutSeconds: 5
          livenessProbe:
            httpGet:
              path: /health/liveliness
              port: http
            periodSeconds: 30
            timeoutSeconds: 5
          volumeMounts:
            - name: config
              mountPath: /app/config.yaml
              subPath: config.yaml
              readOnly: true
      volumes:
        - name: config
          configMap:
            name: litellm-config
---
apiVersion: v1
kind: Service
metadata:
  name: litellm-service
  namespace: litellm
spec:
  selector:
    app: litellm
  ports:
    - name: http
      port: 4000
      targetPort: http
  type: NodePort
```

部署并检查：

```bash
kubectl apply -f litellm-deploy.yaml
kubectl rollout status deployment/litellm -n litellm --timeout=15m
kubectl get pods,svc -n litellm
# 确认迁移和服务启动成功后清理临时迁移 Job
kubectl delete job litellm-db-migrate -n litellm
```

使用实际节点内网 IP 和动态 NodePort 访问。管理后台入口为 `http://<节点内网IP>:<NodePort>/ui`，用户名为 `admin`，密码保存在 `litellm-auth` 的 `UI_PASSWORD` 中；后台创建的虚拟 Key 可用于后续调用。模型 API Base 已在 ConfigMap 中配置，API Key 来自 `vllm-api-key`，无需再填写 `xxxx`。

```bash
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
LITELLM_NODE_PORT=$(kubectl get svc litellm-service -n litellm -o jsonpath='{.spec.ports[0].nodePort}')
read -rs -p 'LiteLLM virtual key: ' LITELLM_VIRTUAL_KEY; echo
curl -fsS "http://${NODE_IP}:${LITELLM_NODE_PORT}/v1/chat/completions" \
  -H "Authorization: Bearer ${LITELLM_VIRTUAL_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{"model":"Qwen3.5-4B","stream":false,"temperature":0,"max_tokens":32,"chat_template_kwargs":{"enable_thinking":false},"messages":[{"role":"user","content":"只回复：K8S_LITELLM_OK"}]}'
unset LITELLM_VIRTUAL_KEY
```

### 1.4.4 限流测试

LiteLLM 支持如下三种限流方案：

- **TPM**：每分钟 Token 数量限制
- **RPM**：每分钟请求数量限制
- **Max Parallel Requests**：最大并发量限制

其中 TPM 和 RPM 分为了三个限制方法：

- **Best effort**：系统会尽可能多地处理请求，不强制拦截超出限制的请求
- **Guaranteed**：系统会严格进行限制，确保不超过设定的限制值
- **Dynamic**：动态调整，系统根据实时负载、历史调用等状态，动态调整限制规则

比如限制某个 Key，每分钟最大 Token 为 2000，请求数为 3：

- **TPM Limit**：`2000`
- **TPM Rate Limit Type**：`Dynamic`
- **RPM Limit**：`3`
- **RPM Rate Limit Type**：`Guaranteed throughput`

测试每分钟请求数量限制：

```bash
curl -H "Authorization: Bearer <litellm-virtual-key>" -X POST http://127.0.0.1:31398/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "Qwen3.5-4B","stream": true, "messages": [{"role": "user", "content": "介绍下你自己"}]}'
```

```json
{"error":{"message":"Rate limit exceeded for api_key: 7b41ef1ecb31b286fdb9815a5266c8a232edf059cc02dfdf05a1a38d85f87ab3. Limit type: requests. Current limit: 3, Remaining: 0.","type":"throttling_error","param":null,"code":"429"}}
```

由于请求数量是 Guaranteed，所以会直接拒绝，token 限制为动态的，所以不会被拒绝。调整为 Guaranteed 后会拒绝连接：

```json
{"error":{"message":"Rate limit exceeded for api_key: 7b41ef1ecb31b286fdb9815a5266c8a232edf059cc02dfdf05a1a38d85f87ab3. Limit type: tokens. Current limit: 200, Remaining: 0.","type":"throttling_error","param":null,"code":"429"}}
```

### 1.4.5 缓存命中

同一个问题，连续问会直接返回结果（命中 Redis 缓存，无需重新推理）：

```bash
curl -H "Authorization: Bearer <litellm-virtual-key>" -X POST http://127.0.0.1:31398/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "Qwen3.5-4B","stream": true, "messages": [{"role": "user", "content": "介绍下你自己 2"}]}'
```

流式返回示例（节选）：

```
data: {"id":"chatcmpl-a1c275d854c9c722","object":"chat.completion.chunk","created":1783764514,"model":"Qwen3.5-4B","choices":[{"index":0,"delta":{"role":"assistant","content":"对于用户的问题，首先需要明确我是 Qwen3.5，是通义实验室最新推出的大语言模型。..."}}]}
data: {"id":"chatcmpl-a1c275d854c9c722","object":"chat.completion.chunk","created":1783764514,"model":"Qwen3.5-4B","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}
data: [DONE]
```

## 1.5 GPU 虚拟化

### 1.5.1 HAMI 部署

官方文档： https://project-hami.io/zh/docs/installation/prerequisites

HAMI 管理 GPU 机器，需要先给 GPU 机器添加 `gpu=on` 的标签：

```bash
kubectl label nodes {nodeid} gpu=on
```

HAMI 的安装依赖当前 K8s 的版本，所有先获取当前的 K8s 版本：

```bash
kubectl version
```

安装 HAMI：

```bash
helm repo add hami-charts https://project-hami.github.io/HAMi/
helm pull hami-charts/hami
# 解压安装包，修改镜像配置
sed -i 's#docker.io#m.daocloud.io/docker.io#g' values.yaml
helm install hami . --set scheduler.kubeScheduler.imageTag=v1.35.3 -n kube-system
```

查看启动状态：

```bash
kubectl get pods -n kube-system | grep hami
```

查看注册的 GPU 资源信息：

```bash
kubectl describe node | grep nvidia.com/gpu:
nvidia.com/gpu:     20 # 每个 GPU 卡*10
```

### 1.5.2 GPU 调度测试

创建测试 Pod：

```bash
tee 1-gpu-test.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: hami-gpu-test
  labels:
    app: hami-gpu-test
spec:
  containers:
    - name: hami-gpu-test
      imagePullPolicy: IfNotPresent
      image: registry.cn-beijing.aliyuncs.com/dotbalo/vllm-openai:latest
      command:
        - sh
        - -c
        - nvidia-smi
  restartPolicy: OnFailure
  env:
    - name: TZ
      value: "Asia/Shanghai"
    - name: LANG
      value: "C.UTF-8"
    - name: LC_ALL
      value: "C.UTF-8"
  resources:
    limits:
      nvidia.com/gpu: 1
EOF
```

查看日志：

```bash
kubectl logs -f hami-gpu-test
```

上述分配了 1 个 vGPU，但是为指定显存和核心数，所以会独占一个显卡，和无虚拟化一致。

### 1.5.3 分配指定显存

假如需要控制每个显卡使用的显存大小，可以添加 `gpumem` 参数：

```yaml
resources:
  limits:
    nvidia.com/gpu: 2
    nvidia.com/gpumem: 3000
```

以上代表分配两个显卡，每个显卡分配 3000Mi 显存。创建后查看日志：

```
nvidia-smi
```

注意：`nvidia.com/gpu` 和 `nvidia.com/gpumem` 不能超过物理机真实显卡数量和显存大小。
显存大小也可以按照百分比分配：`nvidia.com/gpumem-percentage: 50`。

### 1.5.4 指定显卡类型调度

HAMI 支持不同显卡级别的调度，比如某个任务需要 A100，可以添加如下注释：

```yaml
metadata:
  annotations:
    nvidia.com/use-gputype: "A100,V100" # 多种类型逗号分割
    # nvidia.com/nouse-gputype: "1080,2080" # 指定黑名单
```

设备类型可以通过 `nvidia-smi` 命令查看：

```bash
nvidia-smi -L
GPU 0: NVIDIA A10 Ada Generation
GPU 1: NVIDIA A10 Ada Generation
```

### 1.5.5 VLLM 测试

修改之前的 vllm 启动文件，添加显存配置：

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
    nvidia.com/gpumem: 30720
  requests:
    nvidia.com/gpu: 1
    nvidia.com/gpumem: 30720
```

修改显存使用率为 0.95：

```yaml
- "--gpu_memory_utilization"
- "0.95"
```

查看启动状态：

```bash
kubectl get po -n models -owide
```

查看显存占用：
```bash
nvidia-smi
```
