
# 企业级私有大模型
## 为什么私有化部署大模型
- 安全合规：有些行业的应用场景中，敏感数据不能上传到公有云。要满足等保合规的要求。
- 场景适配：行业私有数据、知识库通过RAG挂上去，让大模型懂企业内部流程
- 性能可控：调用外部API容易被限流，自己部署可以精确控制、分配性能
- 成本优化：公有云的token是用的越多越贵，长期看是一笔巨大投入；私有化部署是一次性成本，随着业务增长，单次调用成本会低于公有云

## 什么是私有化推理框架
私有化推理框架指的是把大模型部署在自己的服务器/私有云上运行的推理引擎，不依赖厂商的公有云API。
和大模型的区别：

|        | 大模型 (LLM)                       | 推理框架                          |
| ------ | ------------------------------- | ----------------------------- |
| 本质     | 一堆训练好的权重/参数文件                   | 加载并运行这些权重的软件引擎                |
| 决定什么   | 能力上限——知识、推理、生成质量                | 运行效率——速度、并发、显存占用              |
| 例子     | Qwen、DeepSeek、Llama、ChatGLM     | vLLM、SGLang、Ollama、Xinference |
| 能否单独存在 | 不能自己"跑起来"，只是权重文件(.safetensors等) | 没有模型时啥也做不了，是个空壳               |
私有化推理框架解决的问题是："我已经有了模型权重（自己训练的、或下载的开源模型），怎么把它变成一个能扛住高并发、显存不爆、速度够快的线上服务"

## 私有推理框架对比
| 推理框架       | 适用场景                | 吞吐量 | 部署难度       | 显存/内存效率                               | 多模态能力                              | 推荐指数        |
| ---------- | ------------------- | --- | ---------- | ------------------------------------- | ---------------------------------- | ----------- |
| vLLM       | 企业级高并发生产环境、通用大模型服务  | 极高  | 中等         | 极高 (PagedAttention)，解决显存碎片化问题，提高显存利用率 | 支持 LLM、Embedding、Rerank与多模态模型      | 生产环境首选      |
| SGLang     | 复杂 Agent、多轮对话/RAG   | 高   | 中等         | 极高 (RadixAttention)                   | 支持 LLM、Embedding、Rerank与多模态模型      | 复杂任务Agent首选 |
| Ollama     | 个人开发、本地测试、快速原型开发    | 较低  | 极低(一键安装)   | 中等                                    | 主要侧重于文本生成类LLM，多模态功能完善中，目前不支持Rerank | 仅限本地开发/测试   |
| Xinference | 多模型、多任务(文本/图像/语音)部署 | 中等  | 较低(带Web界面) | 中等                                    | 支持 LLM、Embedding、Rerank与多模态模型      | 统一管理平台首选    |
vLLM是企业内部生产环境部署的最优推理框架：具备极高的吞吐量，优化了现存利用率。

## vLLM
vLLM文档： https://docs.vllm.ai/en/stable/usage/ 

全称Virtual Large Language Model，由加州大学伯克利分校发起的开源大模型推理和服务引擎。2023年开源，核心目标是最大化推理吞吐量，降低硬件成本。是目前业界最主流的LLM部署方案之一。
能让同样的显卡跑出更多的并发请求，能让原本跑不起来的模型跑起来。

### 核心技术
- PagedAttention：分页注意力机制，灵感来源于OS的虚拟内存分野机制。
	- 传统推理框架在生成文本时，模型需要借助当前的上下文，这部分记忆数据被称为KV Cache。会为每个请求分配一块连续的显存来存储KV Cache，导致严重的显存碎片浪费。
	- Paged Attention将KV Cache切分为固定大小的Block，允许这些块在显存中非连续的存储、动态分配和复用。该技术将显存利用率从传统的20%-30%提高到95%以上，几乎消除了显存碎片，同时提升了吞吐量。
- Continuous Batching：连续批处理。传统静态批处理要求一个批次中的所有请求必须等待耗时最长的请求完成之后，才能释放资源，这导致了GPU算力闲置。vLLM的连续批处理允许在每个解码步骤中，动态将新到达的请求加入当前批次，已完成的请求立即退出。该技术大幅降低了高并发场景下的首字延迟（TTFT）

> [!note] 相关概念
> [[KnowledgeBase/concepts/KV Cache]]：补充 KV Cache 的 Prefill/Decode 生命周期、显存/带宽瓶颈和集群调度视角。


### 应用场景
- 大规模在线服务：对外提供标准接口，供聊天机器人、智能体使用
- 实时交互应用：代码补全、多轮对话等要求首字延迟TTFT在200ms以内的低延迟场景
- 高并发处理：离线数据标注、批量文本生成、机器翻译等需要最大化GPU利用率的任务。
- 多模态与异构部署：需要多模态、文生图，以及大语言模型在各类易购硬件平台上的推理服务

## AI原生网关Litellm
大模型技术爆发，实际业务中面临一个痛点：API碎片化问题。
目前市面上有上百家大模型供应商，每一家的API格式、认证方式、参数定义、错误码等都不相同。应用如果要同时接入多家模型，开发者要写好多套代码，维护成本很高。

Litellm是BerriAI开发的一款开源工具，本质上是一个统一的AI网关）（LLM Gateway）和SDK中间层。
提供了一个万能转接头，通过标准化的OpenAI格式接口，允许开发者用同一套代码无缝调用超过100种主流大语言模型。

Litellm分为两种模式：
- 客户端（Python SDK）：
	- 一个轻量级的客户端工具，可以直接集成在应用程序内部，充当一个翻译层，用于将模型的请求自动转换为各厂商期望的请求格式。
	- 当程序基于标准的OpenAI格式发起请求时，SDK会在底层自动进行参数映射，将请求转换为Anthropic、Ollma等各家厂商期望的格式。
	- 无状态的，无需开发者关心内部逻辑，降低模型的适配难度
- 服务端（Proxy Server）：
	- 一个独立的网关服务部署，可以使用Docker和K8s部署，位于应用于模型提供商之间。
	- 位于业务应用和底层的模型供应商之间。提供开箱即用的代理能力：API key管理、日志管理、控制速率限制等
	- 默认使用PostgreSQL作为后端数据库
这两种模式的结合，让大模型的集成和管理变得简单。

<u>为什么不用传统网关而用AI网关？</u>
- 智能调度：传统网关是基于TCP/HTTP请求的，而Litellm内置专为LLM设计的智能路由引擎，当首选模型超时或者宕机时，自动无缝切换到备用模型，保障业务连续性
- 成本优化：传统网关无法理解token，无法追踪。LiteLLM可以实现实时监控Token消耗，支持对不同团队、不同项目设置费用上限，超额自动拒绝请求，防止账单失控
- 统一鉴权：实际业务中，真实的API Key往往散落在各个团队的代码里，存在泄漏风险。LiteLLM通过虚拟密钥管理权限，内部统一将虚拟密钥转换为展示的api key，业务团队只能接触到虚拟密钥。方便权限管理和统一回收。
- 安全过滤：AI网关支持在请求进入模型之前进行敏感内容过滤，数据脱敏等；在模型返回之后，进行内容过滤和合规审查。

# 大模型私有化部署环境准备
## 流程
1. GPU上架/申请GPU服务器
2. 系统安装，GPU驱动安装
3. Docker安装
4. vLLM镜像下载
5. 模型下载
6. 计算模型显存
7. 启动模型

模型下载：
- 魔塔： https://www.modelscope.cn/models 
- HuggingFace： https://huggingface.co/models

vLLM文档： https://docs.vllm.ai/en/stable/

## 计算显存占用
如何计算启动一个模型需要的显存：

基本公式：
- 总显存 = 模型权重显存 + KV Cache显存 + 其他系统开销
- 模型权重显存 = 参数量（B）* 精度系数
- 精度系数 = 精度 / 8 （常见精度：BF16/FP16/FP8/INT8/INT4）
- 单并发KV Cache显存 = 2 * 层数（Layers）* 隐藏维度（Hidden Size）* 上下文长度 * 精度字节数
综上，总显存详细公式：
- 总显存 = 参数量（B）* 精度 /8 + 2 * 层数 * 隐藏维度 * 上下文长度 * 精度字节数 * 并发数 + 5GB
- 实际应用场景中，每次请求用的上下文长度是不知道的，并发数也是不确定的，所以业内提供了一个速算公式

<u>速算公式：总显存 = 参数量（B）* 精度 / 8 + 最大上下文K * 0.3～0.5GB + 5GB</u>

- 最大上下文是模型启动的时候设置的，固定值。
- 小模型（32B以下）用0.3，大模型（32B以上）用0.5
- 这个速算结果只是能让模型启动，可以正常问答的值。
- 如果实际场景中并发很高，或者需要大的上下文（高的KV Cache），建议压测一下，根据能不能抗住，再提高显存。

示例：
- Qwen3.6-27B-BF16 16K上下文 。显存需求：27 * 16 / 8 + 16 * 0.5 + 5 = 67GB
- Qwen3.6-27B-FP8 16K上下文。显存需求：27 * 8 /8 + 16 * 0.5 + 5 = 40GB

## 机器准备
可以在公有云上租一台GPU机器：rockylinux9.8，24GB显存，10MB公网固定带宽，100GB磁盘

## 驱动安装
- 英伟达官网下载最新驱动： https://www.nvidia.com/en-us/drivers/unix/
- 安装依赖：
```sh
# 安装依赖包
dnf install gcc make kernel-devel wget -y
# 升级系统
dnf update -y
# 重启服务器
reboot

# 禁用 Linux 驱动 nouveau，和英伟达官方驱动有冲突
grep "blacklist nouveau" /etc/modprobe.d/blacklist.conf || echo "blacklist nouveau" >> /etc/modprobe.d/blacklist.conf
# 内核中卸载该驱动
grep "options nouveau modeset=0" /etc/modprobe.d/blacklist.conf ||echo "options nouveau modeset=0" >> /etc/modprobe.d/blacklist.conf

dracut --force /boot/initramfs-$(uname -r).img
dracut --force --omit-drivers nouveau
reboot

# 检查 nouveau 是否关闭。没有结果说明已经关闭
lsmod | grep nouveau
# 安装驱动
chmod +x NVIDIA-Linux-*.run && ./NVIDIA-Linux-*.run -q -s --no-dkms --no-x-check 
# 安装完成后，重启服务器
reboot
nvidia-smi
```

## docker安装
```sh
# 关闭防火墙、selinux、dnsmasq、swap
systemctl disable --now firewalld 
systemctl disable --now dnsmasq
setenforce 0
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/sysconfig/selinux
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/selinux/config

# 关闭 swap 分区：
swapoff -a && sysctl -w vm.swappiness=0
sed -ri '/^[^#]*swap/s@^@#@' /etc/fstab

# 更改源及安装必备工具
sed -e 's|^mirrorlist=|#mirrorlist=|g' \
 -e 's|^#baseurl=http://dl.rockylinux.org/$contentdir|baseurl=https://mirrors.aliyun.com/rockylinux|g' \
 -i.bak \
 /etc/yum.repos.d/*.repo
 dnf makecache

yum install -y wget jq psmisc vim net-tools telnet yum-utils device-mapper-persistent-data lvm2 git

# docker安装
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

modprobe overlay
modprobe br_netfilter

cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

sysctl --system
yum install docker-ce -y
systemctl enable --now docker
```

```sh
# 配置Nvidia Runtime，让docker识别GPU
curl -fsSL https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo

# 安装 Toolkit
dnf clean all
dnf makecache
dnf install -y nvidia-container-toolkit
# 生成 Docker 的 Nvidia 运行时
nvidia-ctk runtime configure --runtime=docker

# 查看生成的配置
cat /etc/docker/daemon.json
# 重启 Docker
systemctl restart docker
```

## 模型下载

模型下载：
- 推荐魔塔社区： https://modelscope.cn/ （是阿里云的）
- 建议用modelscope 工具下载。

首先安装 modelscope 工具，推荐 Python 3.12+。
```sh
yum install -y python312
# 用python3.12创建虚拟环境
python3.12 -m venv modelscope
source modelscope/bin/activate
```

安装 modelscope：
```bash
pip install modelscope -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

下载模型，以 Qwen/Qwen3.5-4B 为例：
```bash
modelscope download --model Qwen/Qwen3.5-4B --local_dir /data/models/Qwen3.5-4B
```

查看下载模型文件：

```bash
ls /data/models/Qwen3.5-4B/
```

## 基于vLLM启动大模型
vLLM文档： https://docs.vllm.ai/en/stable/usage/ 

创建模型启动的 docker-compose 文件：
```bash
mkdir /data/modelCompose/Qwen3.5-4B -p
cd /data/modelCompose/Qwen3.5-4B
vim docker-compose.yaml
```

```yaml
version: '3.9'
services:
  qwen3.5-4b:
    shm_size: 16gb # 更改 docker 共享内存
    # m.daocloud.io/docker.io/vllm/vllm-openai:latest
    image: registry.cn-beijing.aliyuncs.com/dotbalo/vllm-openai:latest
    restart: always
    # served-model-name对外发布的名称，和模型名称保持一致
    command: --port 8080 --served-model-name Qwen3.5-4B --model /data/models/Qwen3.5-4B
    # 模型挂载进容器内的路径和外面保持一致即可
    volumes:
      - /data/models/Qwen3.5-4B:/data/models/Qwen3.5-4B
    healthcheck:
      test: ["CMD", "curl", "-s", "http://127.0.0.1:8080"]
      interval: 30s
      timeout: 2s
      retries: 2
      start_period: 60s
    ports:
      - 18080:8080
    environment:
      TZ: Asia/Shanghai
      LANG: C.UTF-8
      LC_ALL: C.UTF-8
      CUDA_VISIBLE_DEVICES: "0"
      NVIDIA_VISIBLE_DEVICES: "all"
    # 把宿主机的所有gpu卡挂载进来  
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
              count: all
```

通过count: all，让docker能看见所有GPU卡；用CUDA_VISIBLE_DEVICES: "0"指定模型在哪些GPU卡上启动。-- 这是比较推荐的配置

启动模型：

```bash
docker compose up -d
```

查看启动日志和启动状态：

```bash
docker-compose ps
```

模型测试：

```bash
curl -X POST http://127.0.0.1:18080/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "Qwen3.5-4B", "messages": [{"role": "user", "content": "介绍下你自己"}]}'
```

返回示例（节选）：

```json
{"id":"chatcmpl-94d2a83f9d60c6cb","object":"chat.completion","created":1782302487,"model":"Qwen3.5-4B","choices":[{"index":0,"message":{"role":"assistant","content":"...你好！我是通义千问Qwen3.5，是阿里巴巴最新推出的通义实验室研发的**超大规模语言模型**，官方名\"通义千问\"，是阿里巴巴最新推出的通义千问语言模型，旨在为人类提供高质量、可信赖的 AI 服务。我支持**100+ 种语言**，具备**256K 原生长上下文**，支持**256K 上下文窗口**，可以精准处理超长文档或视频内容，还是**高效代码开发能力**（生成、调试、运行），都能灵活运用。..."},"finish_reason":"stop"}],"usage":{"prompt_tokens":13,"total_tokens":798,"completion_tokens":785}}
```

### 限制 GPU 使用率

如果显卡显存较大，而模型较小，建议按量分配显存，这样单卡即可启动多个模型，避免显存的浪费。比如一个48GB的卡，启动一个小模型，如果不加限制，也有可能分配40GB显存，不需要这么多，造成浪费。

配置显存使用率，只需要添加 `--gpu_memory_utilization` 参数即可。假如分配 2 号卡的 95% 给模型使用，只需要配置 `--gpu_memory_utilization 0.95` 的参数即可：

```bash
vim /data/modelCompose/Qwen3.5-4B/docker-compose.yaml

# --port 8080 --served-model-name Qwen3.5-4B --model /data/models/Qwen3.5-4B --gpu_memory_utilization 0.95

cd /data/modelCompose/Qwen3.5-4B/
docker compose down
docker compose up
```

注意如果限制的太小了，模型启动过程中可能会报错显存不够。-- 可以去减小上下文大小（KV cache占用），也可以提高gpu分配率。
### 多卡启动

如果模型较大，单个显卡显存较小，可以使用多个显卡启动一个模型，多卡启动除了可以突破单卡启动的限制外，还能利用多卡并行计算，提升模型推理速度。

配置多卡启动只需要添加 `--tensor-parallel-size` 参数即可，多卡启动也同时支持显存使用率的配置。但是仅支持2^n 的数量（2，4，8，...）

假设使用两个卡启动，配置如下：

```yaml
version: '3.9'
services:
  qwen3.5-4b:
    shm_size: 16gb
    image: m.daocloud.io/docker.io/vllm/vllm-openai:latest
    restart: always
    command: --port 8080 --served-model-name Qwen3.5-4B --model /data/models/Qwen3.5-4B --gpu_memory_utilization 0.95 --tensor-parallel-size 2 # 设置张量并行为2，设置--tensor-parallel-size大于1时，vLLM会将模型的权重进行切分，并将这些分片均匀地分配到指定的多张 GPU 上。在推理时，这些 GPU 会协同计算，共同完成一次任务。
    volumes:
      - /data/models/Qwen3.5-4B:/data/models/Qwen3.5-4B
    healthcheck:
      test: ["CMD", "curl", "-s", "http://127.0.0.1:8080"]
      interval: 30s
      timeout: 2s
      retries: 2
      start_period: 60s
    ports:
      - 18080:8080
    environment:
      TZ: Asia/Shanghai
      LANG: C.UTF-8
      LC_ALL: C.UTF-8
      CUDA_VISIBLE_DEVICES: "0,1" # 使用 0 和 1 卡
      NVIDIA_VISIBLE_DEVICES: "all"
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
              count: all
```

接下来重启即可：

```bash
docker-compose down
docker-compose up -d
```

nvlink让GPU卡直接通信，不通过PCIE。
注意，如果 GPU 机器没有 nvlink（通过 `nvidia-smi topo -m` 命令查询：GPU0链接GPU0的参数不是X），那么建议关闭 P2P 和 IB，添加如下环境变量即可：

```yaml
environment:
  NCCL_IB_DISABLE: "1"  # 禁用点对点通信，GPU之间的数据交换将转为通过系统内存和CPU中转
  NCCL_P2P_DISABLE: "1" # 禁用 IB 网络，让 NCCL 使用最通用的 PCIe 进行通信
```

### 配置上下文

在生产环境中使用模型，建议按需配置上下文，只需要通过 `--max-model-len` 参数即可。指定合理的上下文可以防止显存溢出，也可以有效降低显存的占用。

最大上下文建议根据实际需求进行配置，如果不清楚具体使用多少上下文，可以根据如下场景配置：

- 聊天机器人、问答系统：推荐设置为 4096 ~ 8192 (4k-8k)。
- 中长篇内容生成、摘要：推荐设置为 8192 ~ 16384 (8k-16k)。
- 法律文书分析、代码仓库理解等长文本任务：推荐设置为 16384 ~ 32768 (16k-32k)。
- Openclaw 相关任务：推荐设置为 65536 (64k) 以上。

除了 `--max-model-len` 参数，还需要配置 `--max-num-batched-tokens` 参数配合使用，该参数用于控制单批次处理输入和输出的 token 总和，建议 `max-num-batched-tokens >= max-model-len`，通常配置两个参数相等即可。

比如配置为 64k 上下文（注意配置上下文时，需要计算显存是否足够，如果不够会导致模型无法启动）：
- Qwen3.5-4B, BF16, 64K上下文。显存需求：4 * 16 /8 + 64 * 0.5 + 5 = 45GB

```bash
--port 8080 --served-model-name Qwen3.5-4B --model /data/models/Qwen3.5-4B --gpu_memory_utilization 0.95 --max-model-len 65536 --max-num-batched-tokens 65536
```

启动后，可以看到上下文配置的日志：

```
[model.py:1554] Using max model len 65536
```

### 配置访问秘钥

vllm 启动模型时，支持配置 API Key，防止模型接口泄露，造成 GPU 浪费。配置 API Key 只需要指定 `--api-key` 参数即可：

```bash
--port 8080 --served-model-name Qwen3.5-4B --model /data/models/Qwen3.5-4B --gpu_memory_utilization 0.6 --tensor-parallel-size 2 --max-model-len 65536 --max-num-batched-tokens 65536 --api-key "xxxx"
```

启动后，再次访问模型接口，需要添加请求头，包含api-key：

```bash
curl -H "Authorization: Bearer xxxx" -X POST http://127.0.0.1:18080/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "Qwen3.5-4B","stream": true, "messages": [{"role": "user", "content": "介绍下你自己"}]}'
```

## 基于vLLM部署RAG模型
除了文本生成的大模型，VLLM 也原生支持用于的 Embedding 和 Rerank 模型。Embedding 用于文本向量化，Rerank 用于结果重排。

VLLM 部署 Embedding 和 Rerank 模型和文本生成模型没有明显区别，只需要下载对应的模型，然后启动即可。比如部署 Qwen 系列的 Embedding 和 Rerank 模型，首先下载模型：

```bash
source modelscope/bin/activate
modelscope download --model Qwen/Qwen3-Reranker-4B --local_dir /data/models/Qwen3-Reranker-4B
modelscope download --model Qwen/Qwen3-Embedding-4B --local_dir /data/models/Qwen3-Embedding-4B
```

### Embedding模型部署
创建 Embedding 模型的启动文件 (8k上下文就够了)：
```bash
mkdir /data/modelCompose/Qwen3-Embedding-4B -p
cd /data/modelCompose/Qwen3-Embedding-4B
vim docker-compose.yaml
```

```yaml
version: '3.9'
services:
  qwen3-embedding-4b:
    shm_size: 16gb
    image: registry.cn-beijing.aliyuncs.com/dotbalo/vllm-openai:latest
    restart: always
    command: --port 8080 --served-model-name Qwen3-Embedding-4B --model /data/models/Qwen3-Embedding-4B --gpu_memory_utilization 0.5 --tensor-parallel-size 1 --max-model-len 8192 --max-num-batched-tokens 8192 --api-key xxxx
    volumes:
      - /data/models/Qwen3-Embedding-4B:/data/models/Qwen3-Embedding-4B
    healthcheck:
      test: ["CMD", "curl", "-s", "http://127.0.0.1:8080"]
      interval: 30s
      timeout: 2s
      retries: 2
      start_period: 60s
    ports:
      - 18080:8080
    environment:
      TZ: Asia/Shanghai
      LANG: C.UTF-8
      LC_ALL: C.UTF-8
      CUDA_VISIBLE_DEVICES: "0"
      NVIDIA_VISIBLE_DEVICES: "all"
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
              count: all
```

模型启动后，可以用标准的 `/v1/embeddings` 接口请求模型生成向量：

```bash
curl http://localhost:18080/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer xxxx" \
  -d '{
    "model": "Qwen3-Embedding-4B",
    "input": ["人工智能正在改变世界", "vLLM 是一个高性能推理引擎"]
  }'
```

Input 参数可以是字符串，也可以是列表，向量化后的数据在返回数据的 embedding 参数内：

```json
{"id":"embd-89098f2ed7063712","object":"list","created":1782530142,"model":"Qwen3-Embedding-4B","data":[{"index":0,"object":"embedding","embedding":[-0.0005068916361778975...
```

### Reranker模型部署
创建 Rerank 模型部署文件：
```bash
mkdir /data/modelCompose/Qwen3-Reranker-4B -p
cd /data/modelCompose/Qwen3-Reranker-4B
vim docker-compose.yaml
```

```yaml
version: '3.9'
services:
  qwen3-reranker-4b:
    shm_size: 16gb
    image: registry.cn-beijing.aliyuncs.com/dotbalo/vllm-openai:latest
    restart: always
    command: --port 8080 --served-model-name Qwen3-Reranker-4B --model /data/models/Qwen3-Reranker-4B --gpu_memory_utilization 0.5 --tensor-parallel-size 1 --max-model-len 32768 --max-num-batched-tokens 32768 --api-key xxxx --hf-overrides '{"architectures":["Qwen3ForSequenceClassification"],"classifier_from_token":["yes","no"],"is_original_qwen3_reranker":true}'
    volumes:
      - /data/models/Qwen3-Reranker-4B:/data/models/Qwen3-Reranker-4B
    healthcheck:
      test: ["CMD", "curl", "-s", "http://127.0.0.1:8080"]
      interval: 30s
      timeout: 2s
      retries: 2
      start_period: 60s
    ports:
      - 18080:8080
    environment:
      TZ: Asia/Shanghai
      LANG: C.UTF-8
      LC_ALL: C.UTF-8
      CUDA_VISIBLE_DEVICES: "0"
      NVIDIA_VISIBLE_DEVICES: "all"
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
              count: all
```

由于 Qwen3 系列的 Reranker 模型也属于因果语言模型，也是用来生成文本的，所以 vllm 启动该模型时，默认也是用来当做是文本生成式模型，需要通过 `--hf-overrides` 参数，修改一些默认的配置，把模型转换为序列分类模型，用于重排序。

- `"architectures": ["Qwen3ForSequenceClassification"]`：Qwen3-Reranker 默认类型为 Qwen3ForCausalLM，改为 Qwen3ForSequenceClassification，使其变更为序列分类模型进行启动。
- `"is_original_qwen3_reranker": true`：自动格式化输入。
- `"classifier_from_token": ["yes", "no"]`：告诉 vllm 用 yes 和 no 两个词进行打分。

模型启动后，可以使用标准的 Reranker 接口进行测试：

```bash
curl http://localhost:18080/v1/rerank \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer xxxx" \
  -d '{
    "model": "Qwen3-Reranker-4B",
    "query": "如何修改密码？",
    "documents": [
      "点击设置 > 安全 > 修改密码即可更新凭据",
      "点击忘记密码，然后通过邮箱修改密码？",
      "今天天气不错"
    ]
  }'
```

查看结果得分：

```json
{"id":"score-8e193251b12aa95b","model":"Qwen3-Reranker-4B","usage":{"prompt_tokens":38,"total_tokens":38},"results":[{"index":0,"document":{"text":"点击设置 > 安全 > 修改密码即可更新凭据","multi_modal":null},"relevance_score":0.5528110265731812},{"index":1,"document":{"text":"点击忘记密码，然后通过邮箱修改密码？","multi_modal":null},"relevance_score":0.2518998980522156},{"index":2,"document":{"text":"今天天气不错","multi_modal":null},"relevance_score":0.05458692088723183}]}
```

只获取前几个值，可以添加 `top_n` 参数：

```bash
curl http://localhost:18080/v1/rerank \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer xxxx" \
  -d '{
    "model": "Qwen3-Reranker-4B",
    "query": "如何修改密码？",
    "documents": [
      "点击设置 > 安全 > 修改密码即可更新凭据",
      "点击忘记密码，然后通过邮箱修改密码？",
      "今天天气不错"
    ],
    "top_n": 2
  }'
```

返回结果只包含前 2 条记录及其得分。

## LiteLLM部署和配置
官网： https://docs.litellm.ai/docs/proxy/docker_quick_start
一个liteLLM本身，一个pgsql数据库；如果QPS非常高，或者k8s多副本部署，还需要一个Redis做缓冲和内存共享。
### 部署LiteLLM
创建部署文件：
```bash
mkdir -p litellm
vim docker-compose.yaml
```

```yaml
services:
  litellm:
    image: docker.litellm.ai/berriai/litellm:main-stable
    ports:
      - "4000:4000" # Map the container port to the host, change the host port if necessary
    environment:
      DATABASE_URL: "postgresql://llmproxy:dbpassword9090@db:5432/litellm"
      STORE_MODEL_IN_DB: "True" # allows adding models to proxy via UI
      LITELLM_MASTER_KEY: <litellm-master-key>
    depends_on:
      - db
    healthcheck:
      test:
        - CMD-SHELL
        - python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:4000/health/liveliness')" # Command to execute for health check
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:17.2
    restart: always
    container_name: litellm_db
    environment:
      POSTGRES_DB: litellm
      POSTGRES_USER: llmproxy
      POSTGRES_PASSWORD: dbpassword9090
    #ports:
    #  - "5432:5432"
    volumes:
      - ./data/postgres_data:/var/lib/postgresql/data # Persists Postgres data across container restarts
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -d litellm -U llmproxy"]
      interval: 1s
      timeout: 5s
      retries: 10
```

下载镜像：

```bash
docker compose pull
```

启动 litellm：

```bash
docker compose up -d
```

查看日志：

```bash
docker logs -f litellm-litellm-1
```

接下来通过主机 IP 的 4000 端口的 ui 路径即可访问 litellm，登录页面默认账号密码：

- Username: `admin`
- Password: `<litellm-master-key>`（即部署时配置的 `LITELLM_MASTER_KEY`）
- 登录后即可进入 LiteLLM 管理后台，左侧导航栏包含 AI Gateway（Virtual Keys、Playground、Models + Endpoints、Agentic、MCP Servers、Skills、Guardrails、Policies、Tools）、Observability（Usage、Logs、Guardrails Monitor）、Access Control（Teams、Internal Users、Organizations）等模块。

### 基础使用
#### 添加模型

在 **Models + Endpoints** 页面点击 **Add Model**，按照如下格式添加模型：

- **Provider**：选择 `vllm`
- **LiteLLM Model Name(s)**：`Qwen3.5-4B`
- **Model Mappings**：Public Model Name 与 LiteLLM Model Name 均填写 `Qwen3.5-4B`
- **Mode**：`Chat - /chat/completions`
- **API Base**：`http://10.197.237.72:18080/v1`（填写实际的 vllm 服务地址，同一机器或者内网互通，就写内网IP：宿主机暴露18080端口，加/v1后缀）
- **API Key**：`xxx`（对应 vllm 启动时配置的 `--api-key`，这个不是对外的api key，对外的需要在virtual key中配置）

填写完成后点击 **Test Connect** 测试连接，返回 "Connection to Qwen3.5-4B successful!" 表示测试通过，之后点击 **Add Model** 完成添加。

添加完成后，可以通过 **Playground** 进行测试：在 Configurations 中选择 Virtual UI Session 及对应的 Select Model（如 `Qwen3.5-4B`），即可在右侧对话框中发送测试消息。

同样的方式也可以添加外部的模型，比如添加 deepseek 的模型：

- **Provider**：选择 `Deepseek`
- **LiteLLM Model Name(s)**：`deepseek-v4-pro`
- **Model Mappings**：Public Model Name 与 LiteLLM Model Name 均填写 `deepseek-v4-pro`
- **Mode**：`Chat - /chat/completions`
- **API Key**：填写 deepseek 平台的 API Key

除了直接选择供应商，也可以选择 **OpenAI**，然后手动输入 deepseek 的接口地址同样可行，该方式适用于所有符合 OpenAI 接口的模型：

- **Provider**：选择 `OpenAI`
- **LiteLLM Model Name(s)**：`Custom Model Name (Enter below)` → `deepseek-v4-pro`
- **Model Mappings**：Public Model Name 与 LiteLLM Model Name 均填写 `deepseek-v4-pro`
- **Mode**：`Chat - /chat/completions`
- **API Base**：`https://api.deepseek.com`

#### 虚拟 Key 管理

添加模型后，创建一个虚拟 key，之后就可以通过 LiteLLM 访问后端的模型。

在 **Key Ownership** 中选择 `You`，填写 Key Name（如 `xxxx`），在 Models 中选择授权的模型（如 `Qwen3.5-4B`），点击 **Create Key**。

创建后需要记录生成的 key（离开页面后将无法再次查看）：

```
Virtual Key: <litellm-virtual-key>
```

接下来使用 litellm 通过该 Key 访问已授权的模型（访问liteLLM的接口）：

```bash
# curl -H "Authorization: Bearer <litellm-virtual-key>" -X POST http://127.0.0.1:4000/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "Qwen3.5-4B","stream": true, "messages": [{"role": "user", "content": "介绍下你自己"}]}'
```

### 记录问答详情

模型调用日志可以在可观测性——logs 中查询，但是默认情况下，litellm 未记录模型调用的 request 和 response 数据（显示为空的 `{}`）。

如果需要开启，可以在设置中开启：**Settings → Admin Settings → Logging Settings**，打开 **Store Prompts in Spend Logs** 开关，并配置 **Maximum Spend Logs Retention Period**（如 `7d`），点击 **Save Settings**。

开启后就可以在 Logs 中显示请求详情，包括完整的 Request（model、stream、messages、metadata 等）和 Response（模型回复内容）。

### 团队管理

生产环境中，为了实现更加细粒度的权限管理和成本管控，建议为每个部门、项目组或不同系统等维度创建单独的 team，之后单独分配权限和成本控制。

假设现在希望为开发和测试团队进行细粒度管理，使开发团队只能访问 Qwen3.5-4B 的模型，测试团队只能使用 Deepseek 模型。

首先为两个团队在 litellm 上创建对应的 Team：

- 创建开发团队 `development`，Models 只选择 `Qwen3.5-4B`
- 创建测试团队 `test`，Models 只选择 `deepseek-v4-pro`

创建团队时还可以配置 Max Budget（USD）、Reset Budget（daily/weekly/monthly）、Tokens per minute Limit（TPM）、Requests per minute Limit（RPM）等。

接下来为每个团队分配虚拟 key：在 **Key Ownership** 中选择 `Service Account`，选择对应 Team（如 `test`），填写 Service Account ID（如 `test-team`），Models 选择 `All Team Models`，点击 **Create Key**。

创建 Key 后，测试权限隔离是否正常。首先测试 test 团队的 key 是否可以访问 Qwen3 模型：

```bash
curl -H "Authorization: Bearer <litellm-virtual-key>" -X POST http://127.0.0.1:4000/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "Qwen3.5-4B","stream": true, "messages": [{"role": "user", "content": "介绍下你自己"}]}'
```

```json
{"error":{"message":"team not allowed to access model. This team can only access models=['deepseek-v4-pro']. Tried to access Qwen3.5-4B","type":"team_model_access_denied","param":"model","code":"403"}}
```

提示当前 Key 不能访问 Qwen3.5-4B 模型，更改为 deepseek 模型后问答正常。除了使用 curl 命令，也可以通过 playground 进行测试：选择 test 团队的 Key，Select Model 选择 `deepseek-v4-pro` 会报同样的 403 错误（提示只能访问 `Qwen3.5-4B`，说明该 Key 实际绑定的是开发团队），切换为 `Qwen3.5-4B` 模型后正常问答。

### 团队用户管理

除了利用 ServiceAccount，还可以为每个团队的成员分配账户。比如创建一个测试团队的用户，并且分配该用户的 key：

在 **Access Control → Internal Users** 页面点击 **Invite User**，填写：

- **User Email**：`xxxx@163.com`
- **Global Proxy Role**：`Internal User (View Only) - view their own keys, view their own spend`
- **Team**：`test`

点击 **Invite User** 后生成 Invitation Link，接下来用户可以通过邀请链接登录 LiteLLM，设置密码（如 `password_litellm`）完成 Sign Up。

接下来创建该用户的 key，建议 key name 按照 `team-用户名` 格式命名：

- **Key Ownership**：选择 `Another User`
- **User ID**：`xxxx@163.com`
- **Team**：`test`
- **Key Name**：`test-xxxx`

当前 key 只能访问当前 team 有权限的模型：

```bash
curl -H "Authorization: Bearer <litellm-virtual-key>" -X POST http://127.0.0.1:4000/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "Qwen3.5-4B","stream": true, "messages": [{"role": "user", "content": "介绍下你自己"}]}'
```

```json
{"error":{"message":"team not allowed to access model. This team can only access models=['deepseek-v4-pro']. Tried to access Qwen3.5-4B","type":"team_model_access_denied","param":"model","code":"403"}}
```

此时可以在 Logs 中查到当前用户的访问日志（包括 Type、Status、Session ID、Request ID、Cost、Duration、TTFT、Team Name、Key Hash 等字段）。

### 成本管理

如果想要限制某个用户或者某个团队的模型成本，需要配置每个模型的成本。

在 **Models + Endpoints** 页面选中对应模型（如 `Qwen3.5-4B`），点击 **Edit Settings**，配置：

- **Max Budget (USD)**：`1`（最多可使用的成本为 1 美元）
- **Soft Budget (USD)**：`0.5`（并且达到 0.5 美元发送提示）
- **Soft Budget Alerting Emails**：`xxxx@163.com`

保存后点击 **Save Changes**。

也可以设置按天限制或者按照其它周期限制，**Reset Budget** 支持 `daily`、`weekly`、`monthly`。

接下来发送请求，测试成本管控是否正常：

```bash
curl -H "Authorization: Bearer <litellm-virtual-key>" -X POST http://127.0.0.1:4000/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "Qwen3.5-4B","stream": true, "messages": [{"role": "user", "content": "列举一下北京比较著名的景点有哪些？"}]}'
```

在 **Usage** 页面可以按 Team 查看用量和使用详情，包括 Total Spend、Total Requests、Successful/Failed Requests、Daily Spend、Spend Per Team、Top Virtual Keys、Top Models 等维度的统计。在 **Teams** 列表中也可以看到每个团队的 Spend / Budget（如 `development` 团队 `$0.04 / $1.00`）。

成本达到限制会有如下提示：

```bash
curl -H "Authorization: Bearer xxx" -X POST http://127.0.0.1:4000/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "Qwen3.5-4B","stream": true, "messages": [{"role": "user", "content": "列举一下北京比较著名的景点有哪些？"}]}'
```

```json
{"error":{"message":"Budget has been exceeded! Team=9cbca9c9-53f1-4387-bbb4-a0c8a7b21530 Current cost: 0.03890300000000001, Max budget: 0.02","type":"budget_exceeded","param":null,"code":"429"}}
```