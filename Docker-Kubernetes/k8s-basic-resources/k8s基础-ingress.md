---
title: K8s基础-Ingress
tags:
  - kubernetes
  - k8s-basics
aliases:
  - k8sIngress
---

# Kubernetes Ingress：从 HTTP 路由到灰度发布与故障排查

Service 为应用提供了稳定入口，但多个 Web 服务共用同一个公网地址时，还需要根据域名和 URL 路径分配请求。Ingress 负责描述这类 HTTP/HTTPS 规则，Ingress Controller 则把规则落实为真正的代理行为。理解这两个对象的分工后，TLS、重写、限流和灰度发布就能放回各自的位置。

先说明版本边界：Kubernetes 社区的 ingress-nginx 项目已在 2026 年 3 月退役，停止发布和安全修复。存量实例仍可能继续转发流量，但新部署应选择维护中的 Gateway API 实现或其他受支持的 Ingress Controller，见[官方退役说明](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/)。本文的 ingress-nginx 注解、调优和 v1.1.0 安装清单用于理解存量配置与隔离实验，不应直接用于新建生产入口。

退役的是一个具体控制器实现。Ingress API 本身仍然可用，已冻结功能演进；Gateway API 通过 GatewayClass、Gateway、HTTPRoute 等资源继续发展入口能力，也需要相应控制器，不能仅改资源名称就完成迁移。两者的定位可对照[Kubernetes Ingress 说明](https://kubernetes.io/docs/concepts/services-networking/ingress/)。

本文先解释访问链路，再建立最小路由，逐步加入认证、会话、流式响应、重写和访问控制，随后处理常见故障及灰度发布，最后完成两组历史高可用与 Tomcat 实验。阅读前需要掌握 Pod、Deployment、Service、Namespace 和基本 TCP/IP，并准备有权限的隔离集群、可解析的测试域名或本机 hosts 记录。所有命令都应先核对上下文；域名、IP、镜像和资源名称需与自己的实验保持一致。

## 从网络分层理解 Ingress

### OSI 模型与 HTTP 路由

![image-20231209104609983](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312091046041.png)

定位入口功能时，先关注传输层和应用层。TCP/UDP 提供连接或数据报传输，HTTP 则在连接上携带 Host、路径、请求方法和请求头；同一个 IP:443 上要根据域名与路径选择服务，代理必须具备相应的 HTTP/TLS 处理能力。

### Service 解决稳定入口，HTTP 入口继续处理路由

Service 用 selector 关联一组 Pod，由 EndpointSlice 描述实际后端，再由 kube-proxy 或替代数据平面维护转发。ClusterIP 提供集群内入口，NodePort 和 LoadBalancer 则是常见的外部接入方式。

如果每个 Web 服务都使用独立 NodePort，调用方要记住不同端口，端口与防火墙规则也会增加。四层 Service 可以传输 TLS 流量，但通常不会解密 HTTP 内容，也不会根据 HTTP Host 和 URL 路径选择不同应用。多个域名共用 80/443 时，需要能理解应用层请求的入口代理。

### 四层与七层代理分别依据什么转发

四层负载均衡依据源/目标 IP、端口和协议选择后端，常通过 NAT、直接路由或隧道等机制完成转发。TCP 连接建立后，通常需要维持该连接到同一后端的映射。

七层代理进一步读取 HTTP Host、URL 路径或请求头。例如，同一入口可以将 `/api` 交给 API 服务，将静态页面交给 Web 服务；也可以根据语言或客户端特征选择不同后端。HTTPS 场景若要读取这些 HTTP 信息，需要在相应位置终止 TLS；仅透传加密数据时看不到 URL 路径。

### Ingress：声明请求如何匹配后端

Ingress 是 Kubernetes API 资源，主要描述 HTTP/HTTPS 的域名、路径和后端 Service。例如，把 `shop.example.com/api` 路由到同一 Namespace 中名为 `api` 的 Service。它还可以引用 TLS Secret，但资源本身不会监听端口或转发请求。

![image-20240725225555680](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202407252255843.png)

### Ingress Controller：运行代理并协调配置

Ingress Controller 观察 Ingress、Service、EndpointSlice、Secret 等资源，将它们翻译为代理配置或云负载均衡配置。具体实现可以基于 Nginx、Traefik、HAProxy 等。Istio 的网关也属于应用层入口能力，不能把整个 Istio 归为“OSI 第六层代理”。

以 ingress-nginx 为例，控制器维护 Nginx 配置并在需要时重新加载；调用者修改 Kubernetes 资源即可，不必进入每个 Pod 手工编辑 `nginx.conf`。不同控制器支持的注解与高级功能有差异，本文的 `nginx.ingress.kubernetes.io/*` 不能直接移植到其他实现。

### 规则和实现如何关联

Ingress 的 `spec.ingressClassName` 引用集群级的 IngressClass，由它的 `spec.controller` 标识对应实现。控制器按自身配置处理属于自己的规则。IngressClass 名称并不一定是 `nginx`，应先检查实际安装结果；本文普通实验统一使用 `nginx`，多控制器实验另用 `ngx-ds`。完整资源清单可保存为文件后用 `kubectl apply -f 文件名.yaml` 提交；标注为片段的内容需要合并到指定位置，不能单独 apply。

可以把这几个对象按职责连接起来：Ingress 定义路由，IngressClass 选择实现，控制器维护数据平面，Service 和 EndpointSlice 描述后端。配置更新是否生效，需要结合控制器事件、日志和实际代理配置确认。

### 从部署顺序看资源依赖

#### 流程

1. 部署Ingress controller，我们ingress controller使用的是nginx

2. 创建Pod应用，可以通过控制器创建pod

3. 创建Service，用来分组pod

4. 创建Ingress http，测试通过http访问应用

5. 创建Ingress https，测试通过https访问应用

#### 实际数据流向

使用七层负载均衡调度器ingress controller时，当客户端访问kubernetes集群内部的应用时，数据包走向如下图流程所示：

![image-20231209111616791](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312091116867.png)

> [!warning] 注意
> ingress-nginx 通常通过 Service 对应的后端记录获取 Pod IP，默认可以直接代理到这些地址，而不是先访问 ClusterIP。它并非仅凭标签绕过 Service；`service-upstream` 等配置还可能改变路径。其他控制器的数据路径需按实现确认。

## 入口高可用：先选择暴露方式

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202507172346336.png" alt="image-20250717234628958" style="zoom:50%;" />

入口通常至少需要多个副本和跨节点部署，避免单个 Pod 或节点故障使所有应用不可达。上图是一种“前置负载均衡器 → 专用入口节点 → 应用后端”的架构。具体副本数应由容量和故障域决定，2–3 个节点只是常见起点。

如果使用专用节点，可以打上 `ingress=true` 标签，再为入口 DaemonSet 配置 nodeSelector；也可以用 Deployment 配合反亲和性或拓扑分布约束。DaemonSet 并不是部署入口的唯一方式。

~~~yaml
nodeSelector:
  kubernetes.io/os: linux
  ingress: "true"
~~~

入口本身也要接收集群外的流量，常见方式各有约束：

| 暴露方式 | 适合考虑的条件 | 需要验证的边界 |
| --- | --- | --- |
| LoadBalancer Service | 集群有受支持的云 LB 或裸机 LB 实现 | 健康检查、源 IP、跨节点转发和费用 |
| NodePort Service | 前置 LB 可转发到节点端口，或用于实验 | 节点端口范围、防火墙、外部流量策略 |
| hostNetwork | 希望代理直接绑定节点的 80/443 | 端口冲突、调度隔离、主机网络权限、DNS 策略 |

`hostNetwork: true` 可能减少部分转发步骤，但不能由此断言性能一定最好。它还会使同一节点上的端口竞争更直接，通常需 `dnsPolicy: ClusterFirstWithHostNet`。选型应根据当前受支持控制器和实际压测结果决定；对于已退役的 ingress-nginx，应先规划迁移。

前置 F5、SLB、LVS 或 HAProxy 可以把请求分发给多个健康入口节点，入口域名在生产中通常解析到这个前置 LB。ExternalDNS 可按环境自动管理 DNS，但不是 Ingress 生效的必要条件。测试时可用 hosts 或 `curl --resolve` 指定目标，确保请求中的 Host 与规则一致。

没有前置 LB 的裸机场景也可用 Keepalived 维护 VIP。单个 VIP 通常由一个节点持有，入口节点和前置转发层的容量与故障检测仍需独立评估；后面的完整实验用于说明这种架构，不能把它简单等同于多个后端节点都无法分担流量。

## 创建最小可用的 HTTP 路由

### 准备后端和测试方式

先确认已有控制器和 IngressClass。下面创建 `study-ingress` Namespace，以及后续示例使用的 `nginx` Deployment 和同名 Service。后续章节中的资源清单是独立演示，同名 Ingress 会覆盖之前配置，实验时一次应用一组；`auth.test.com`、`nginx.rewrite.com` 等域名也要指向同一个入口地址。

~~~sh
kubectl get ingressclass
kubectl create namespace study-ingress
kubectl create deployment nginx --image=nginx:stable -n study-ingress
kubectl expose deployment nginx --port=80 --target-port=80 -n study-ingress
kubectl get pods,svc -n study-ingress
~~~

`nginx:stable` 便于说明操作，复现实验应固定已验证的具体版本或摘要。取得入口地址后，可用如下方式同时指定 DNS 和 Host，无须先配置公共 DNS：

~~~sh
# 示例入口IP，请替换成自己的入口地址
curl --resolve nginx.test.com:80:192.168.40.6 http://nginx.test.com/
~~~

### YAML 定义

~~~yaml
apiVersion: networking.k8s.io/v1 # k8s >= 1.22  必须  v1
kind: Ingress
metadata:
  name: nginx-ingress
  namespace: study-ingress
spec:
  ingressClassName: nginx # 指定该 Ingress 被哪个 Controller 解析
  rules:  # 定义路由匹配规则，可以配置多个
  - host: nginx.test.com  # 定义域名
    http:  
      paths: # 详细的路由配置，可以配置多个
      - path: / # 指定 PATH
        pathType: ImplementationSpecific   # 指定匹配规则
        backend: # 指定该路由的后端
          service:
            name: nginx # 访问nginx.test.com/ 就会代理到这个service的80端口
            port:
              number: 80
  # HTTPS 在下一节配置证书后再添加以下字段
  # tls:
  # - hosts:
  #   - nginx.test.com
  #   secretName: ca-secret
~~~

pathType：路径的匹配方式，目前有 ImplementationSpecific、Exact 和 Prefix 方式。

- Exact：精确匹配，比如配置的 path 为/bar，那么/bar/将不能被路由；
- Prefix：前缀匹配，基于以 / 分隔的URL路径。比如 path 为/abc，可以匹配到/abc/bbb等，比较常用的配置；
- ImplementationSpecific：这种类型的路由匹配根据 Ingress Controller 来实现。
  - 具体行为由控制器确定，不能假定一定等同于 Prefix。常规路径优先明确使用 Prefix 或 Exact，正则表达式等实现特性再按控制器要求配置。

### 全局配置与单条路由配置

对于 ingress-nginx，控制器引用的 ConfigMap 通常影响它管理的全部 Ingress，见[ConfigMap 配置](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/configmap/)；Ingress 上的注解则配置相应路由能力，见[Annotations 说明](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/)。部分配置会按 host 合并，因此不能把不同 Ingress 资源视为绝对隔离的配置边界。

### 不配置域名，仅按路径发布

有些时候可能因为公司确实不支持域名或者内部dns解析，但是还是需要一个统一的入口，可以不配域名，只配path，通过controller IP+path来访问：

~~~yaml
apiVersion: networking.k8s.io/v1 # k8s >= 1.22  必须  v1
kind: Ingress
metadata:
  name: nginx-ingress-no-host
  namespace: study-ingress
spec:
  ingressClassName: nginx # 指定该 Ingress 被哪个 Controller 解析
  rules:  # 定义路由匹配规则，可以配置多个
  - http:  
      paths: # 详细的路由配置，可以配置多个
      - path: /no-host # 指定 PATH
        pathType: ImplementationSpecific   # 指定匹配规则
        backend: # 指定该路由的后端
          service:
            name: nginx
            port:
              number: 80
~~~

不设置 host 时，这条规则可匹配到达该入口且路径符合 `/no-host` 的请求，不要求某个特定域名。仍需确保后端本身能处理这个路径；Ingress 不会自动去掉 `/no-host` 前缀。

## 添加 TLS、认证与应用层代理能力

最小 HTTP 路由通了以后，再逐项加入额外能力。每次修改后先确认清单被控制器接受，再验证实际响应；控制器注解无法替代后端本身的认证、会话或协议实现。

### 通过 HTTPS 发布服务

TLS 可以在前置 LB 终止，也可以在入口控制器终止，必要时还可加密入口到后端的链路。应按信任边界设计，不能假设“LB 后面永远走明文即可”。这里演示控制器终止 TLS：证书 Secret 与 Ingress 放在同一 Namespace，证书名称覆盖访问域名。

实验使用带 Subject Alternative Name（SAN）的自签证书，浏览器不会默认信任它。生产证书可由受信任的公共或企业 CA 签发，也可以采用自动签发与续期方案，并非必须购买。

生成证书：

~~~sh
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout tls.key -out tls.crt -subj "/CN=nginx.test.com" -addext "subjectAltName=DNS:nginx.test.com"
kubectl create secret tls ca-secret --cert=tls.crt --key=tls.key  -n study-ingress
~~~

ingress添加tls配置：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  namespace: study-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: nginx.test.com
    http:
      paths:
      - backend:
          service:
            name: nginx
            port:
              number: 80
        path: /
        pathType: ImplementationSpecific
  tls:
    - hosts:
      - nginx.test.com
      secretName: ca-secret
~~~

### 域名添加用户名密码认证

有些开源工具本身不提供密码认证，如果暴露出去会有很大风险，可以在入口增加 Basic Auth。它通过用户名和密码校验限制访问，应配合 HTTPS 使用。RPM 系实验环境可安装提供 htpasswd 的工具包：

~~~sh
yum install httpd-tools -y
~~~

使用 htpasswd 创建 foo 用户的密码：

~~~sh
htpasswd -c auth foo
#New password: 
#Re-type new password: 
#Adding password for user foo
cat auth 
# foo:<password-hash>
~~~

基于之前创建的密码文件创建 Secret：

~~~sh
kubectl create secret generic basic-auth --from-file=auth -n study-ingress
~~~

创建包含密码认证的 Ingress：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-with-auth
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/auth-realm: Please Input Your Username and Password
    nginx.ingress.kubernetes.io/auth-secret: basic-auth # 在这里指定用户名密码的secret
    nginx.ingress.kubernetes.io/auth-type: basic
spec:
  ingressClassName: nginx
  rules:
  - host: auth.test.com
    http:
      paths:
      - path: /
        pathType: ImplementationSpecific
        backend:
          service:
            name: nginx 
            port:
              number: 80
~~~

### 开启会话保持

和 Nginx 一样，Ingress Nginx 也支持基于 cookie 的会话保持。

首先扩容 nginx 服务至多个副本：

~~~sh
kubectl scale deploy nginx --replicas=3 -n study-ingress
~~~

未开启会话保持，同一个主机访问可以看到流量会在三个副本中都有。

通过以下配置，支持并携带同一会话 Cookie 的客户端会倾向于访问同一 Pod；后端不可用或 Cookie 失效时仍可能重新选择：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: 16m
    nginx.ingress.kubernetes.io/affinity: "cookie"
    nginx.ingress.kubernetes.io/session-cookie-name: "route"
    # 过期时间，expires字段是为了兼容旧版浏览器
    nginx.ingress.kubernetes.io/session-cookie-expires: "172800"
    nginx.ingress.kubernetes.io/session-cookie-max-age: "172800"
    # 后端负载扩容后，是否需要重新分配流量，balanced: 重新分配，persistent: 保持粘性
    nginx.ingress.kubernetes.io/affinity-mode: persistent
spec:
  ingressClassName: nginx
  rules: 
  - host: nginx.test.com
    http:
      paths:
      - path: /
        pathType: ImplementationSpecific
        backend:
          service:
            name: nginx
            port:
              number: 80
~~~

同时浏览器的 request headers 会添加一个 Cookie 的属性。

如果需要流量重新分配，更改 `nginx.ingress.kubernetes.io/affinity-mode: balanced` 即可。再次扩容后，就会发现流量会重新分配到其他节点。（persistent 保持已有会话，balanced 有助于扩容后分配流量，需按业务选择）

详细的会话保持配置：[Sticky Sessions - Ingress-Nginx Controller](https://kubernetes.github.io/ingress-nginx/examples/affinity/cookie/)

### 配置流式返回 SSE（代理大模型服务）

本节 `nginx` Service 只表示后端位置，实际实验需换成已实现 SSE 的应用 Service；普通 Nginx 欢迎页不会因为增加注解就变成流式接口。

SSE（Server-Sent Events）通过普通 HTTP 响应持续发送事件，不需要 WebSocket 的协议升级。对于大模型逐段返回等场景，先确认后端使用 `text/event-stream` 并及时 flush，再关闭代理响应缓冲，设置与业务心跳间隔匹配的读超时。下面的超时值用于实验，不是统一的生产推荐：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/proxy-http-version: "1.1"
    nginx.ingress.kubernetes.io/proxy-buffering: "off"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
spec:
  ingressClassName: nginx
  rules: 
  - host: nginx.test.com
    http:
      paths:
      - path: /
        pathType: ImplementationSpecific
        backend:
          service:
            name: nginx
            port:
              number: 80
~~~

可以用 `curl -N` 观察数据是否逐段到达；`-N` 关闭 curl 自身的输出缓冲。如果仍是整段出现，需继续检查应用、前置 LB、压缩或其他代理层。WebSocket 则使用 `Upgrade`/`Connection` 握手，ingress-nginx 对其有专门支持，不应把 Upgrade 头强加给 SSE。有关超时和缓冲的控制器行为见[注解说明](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/#custom-timeouts)。

### 域名重定向 Redirect

在使用 Nginx 作为代理服务器时，Redirect 可用于域名的重定向，比如访问 old.com 被重定向到 new.com。Ingress 也可以实现 Redirect 功能，接下来用 nginx.test.com 作为旧域名，baidu.com 作为新域名进行演示：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/permanent-redirect: https://www.baidu.com
    nginx.ingress.kubernetes.io/permanent-redirect-code: "308" # 本例为永久重定向；临时重定向应使用对应annotation
spec:
  ingressClassName: nginx
  rules: 
  - host: nginx.test.com
    http:
      paths:
      - path: /
        pathType: ImplementationSpecific
        backend:
          service:
            name: nginx
            port:
              number: 80
~~~

使用 `curl -I http://nginx.test.com` 可检查响应状态及 `Location`。本例应返回 308；重定向目标不再经过此处的后端 Service。

### 访问地址重写 Rewrite

对于一个大的项目，前后端分离，后端微服务有很多，共用同一个域名比如nginx.test.com。用户访问是通过path路径去区分访问，比如/api-a到用户中心/api-b到支付中心等。但是后端去开发的时候，并不是按照/api-a、/api-b等接口去开发的，可能留的接口都是/api。这样访问怎么找到每一个微服务？

我们直接去访问/api-a肯定是不行的，因为后端服务根本没有这个名字的接口。我们可以自定义/api-a这个路径，重写为 /api (或者比如开发留的接口就是/，那就重写为/) 就能访问到后端的服务了。如下图：

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202507181955304.png" alt="image-20250718195507023" style="zoom:50%;" />

创建一个应用模拟后端服务：

~~~sh
kubectl create deploy backend-api --image=registry.cn-beijing.aliyuncs.com/dotbalo/nginx:backend-api -n study-ingress
~~~

创建 Service 暴露该应用

~~~sh
kubectl expose deploy backend-api --port 80 -n study-ingress
~~~

创建ingress

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: backend-api
  namespace: study-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: nginx.rewrite.com
    http:
      paths:
      - backend:
          service:
            name: backend-api
            port:
              number: 80
        path: /api-a
        pathType: ImplementationSpecific
~~~

这个示例服务的后端接口留的是 /，而不是/api-a，现在我们直接访问/api-a，浏览器访问会报404。因为pod里面的容器根本没有/api-a接口。人家留的是/接口。

此时需要通过 Ingress Nginx 的 Rewrite 功能，将/api-a 重写为“/”，配置示例如下：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: backend-api
  namespace: study-ingress
  annotations:
    # 告诉Ingress Controller重写请求的目标路径。
    # $2 是一个正则表达式捕获组的引用。匹配到第二个捕获组。
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/use-regex: "true"
spec:
  ingressClassName: nginx
  rules:
  - host: nginx.rewrite.com
    http:
      paths:
      - backend:
          service:
            name: backend-api
            port:
              number: 80
        path: /api-a(/|$)(.*)
        # /api-a - 匹配以 "/api-a" 开头的路径
        # (/|$) - 第一个捕获组：匹配 "/" 或字符串结尾
        # (.*) - 第二个捕获组：匹配后面的任意字符
        pathType: ImplementationSpecific
~~~

| 原始请求路径        | 匹配结果 | 重写后路径    |
| ------------------- | -------- | ------------- |
| `/api-a/users`      | ✅ 匹配   | `/users`      |
| `/api-a/orders/123` | ✅ 匹配   | `/orders/123` |
| `/api-a`            | ✅ 匹配   | `/`           |
| `/api-b/test`       | ❌ 不匹配 | -             |

再次访问 `http://nginx.rewrite.com/api-a`，后端收到的路径应为 `/`。

> [!info] 说明
>
> - 如果希望把/api-a重写为/api，annotation就写`nginx.ingress.kubernetes.io/rewrite-target: /api/$2`
> - 注解附着在 Ingress 资源上。同一 host 中只要使用 use-regex 或 rewrite-target，ingress-nginx 可能对该 host 的其他路径也采用正则匹配；把资源拆开并不必然隔离这种影响。需要同时检查同一 host 下所有 Ingress 的路径顺序和匹配结果，见[正则路径说明](https://kubernetes.github.io/ingress-nginx/user-guide/ingress-path-matching/)。

## 控制访问范围与请求行为

对外入口既要找到正确后端，也要识别请求来源、限制异常流量。以下控制基于入口实际看到的请求信息；前置 LB 的转发头和源地址处理应先确认。

### 限制访问速率

有时候可能需要限制速率以降低后端压力，或者限制单个 IP 每秒的访问速率防止攻击。此时可以使用 Nginx 的 rate limit 进行配置。

首先没有加速率限制，使用 ab 进行访问，Failed 为 0：

~~~sh
ab -A foo:YOUR_LAB_PASSWORD -c 10 -n 100 http://auth.test.com/ | grep requests
# Complete requests: 100
# Failed requests: 0
~~~

添加速率限制，限制只能有一个连接，只需要添加 `nginx.ingress.kubernetes.io/limit-connections` 为 1 即可：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-with-auth
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/auth-realm: Please Input Your Username and Password
    nginx.ingress.kubernetes.io/auth-secret: basic-auth
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/limit-connections: "1"
spec:
  ingressClassName: nginx
  rules:
  - host: auth.test.com
    http:
      paths:
      - backend:
          service:
            name: backend-api
            port:
              number: 80
        path: /
        pathType: ImplementationSpecific
~~~

再次使用 ab 测试，下面是一组示例输出。失败数受突发阈值、时序和副本数影响，不会固定为 67，还应检查响应状态码：

~~~sh
ab -A foo:YOUR_LAB_PASSWORD -c 10 -n 100 http://auth.test.com/ | grep requests:
# Complete requests: 100
# Failed requests: 67
~~~

还有很多其它方面的限制，常用的配置如下：

~~~yaml
# Ingress.metadata.annotations片段，示例值需按业务调整
annotations:
  nginx.ingress.kubernetes.io/limit-rps: "10"
  # 如需按分钟限制，可改用以下配置
  # nginx.ingress.kubernetes.io/limit-rpm: "600"
  nginx.ingress.kubernetes.io/proxy-buffering: "on"
  nginx.ingress.kubernetes.io/limit-rate: "100"
  nginx.ingress.kubernetes.io/limit-whitelist: "192.0.2.0/24"
~~~

限流按控制器副本执行，不是集群全局计数；多个副本或 HPA 会影响总体额度。`limit-connections` 限制并发连接，`limit-rps/rpm` 限制请求速率，`limit-rate` 限制每条连接的响应传输速率。还要确认控制器看到的源 IP，前置 LB 或不可信的转发头可能改变识别结果，见[官方限流说明](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/#rate-limiting)。Basic Auth 应搭配 HTTPS，示例密码不要写入正式脚本或命令历史。

### 黑名单配置

路由级黑名单用于相应 Ingress 的访问控制，注意同一 host 下的合并行为。

使用 `nginx.ingress.kubernetes.io/denylist-source-range` 添加黑名单，支持 IP、网段，多个黑名单逗号分隔：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-with-auth
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/auth-realm: Please Input Your Username and Password
    nginx.ingress.kubernetes.io/auth-secret: basic-auth
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/denylist-source-range: 192.168.181.134,10.0.0.0/24,172.10.0.1
spec:
  ingressClassName: nginx
  rules:
  - host: auth.test.com
    http:
      paths:
      - backend:
          service:
            name: backend-api
            port:
              number: 80
        path: /
        pathType: ImplementationSpecific
~~~

全局黑名单：所有controller代理的ingress都生效

Ingress-nginx 支持全局的黑白名单（全局白名单慎用），只需要在 ingress nginx 的配置文件中添加即可，添加后无需重启Controller，加一个全局黑名单：

~~~sh
kubectl edit cm ingress-nginx-controller -n ingress-nginx
~~~

在该 ConfigMap 的 `data` 中设置：

~~~yaml
data:
  denylist-source-range: "192.168.181.134"
~~~

### 白名单配置

白名单表示只允许某个 IP 可以访问，直接在 yaml 文件中配置即可。比如这个ingress域名想要只允许192.168.181.141 访问，只需要添加一个 `nginx.ingress.kubernetes.io/whitelist-source-range` 注释即可：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-with-auth
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/auth-realm: Please Input Your Username and Password
    nginx.ingress.kubernetes.io/auth-secret: basic-auth
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/whitelist-source-range: 192.168.181.141
spec:
  ingressClassName: nginx
  rules:
  - host: auth.test.com
    http:
      paths:
      - backend:
          service:
            name: backend-api
            port:
              number: 80
        path: /
        pathType: ImplementationSpecific
~~~

### 自定义错误页

每个项目在对外发布时，难免不了会有一些未知的错误，比如 404/502/503 等，为了给客户更加友好的提示，可以使用 default backend 自定义错误页。

先部署一个提供错误页的后端，控制器再把指定错误交给它处理。行为见[Custom Errors 说明](https://kubernetes.github.io/ingress-nginx/examples/customization/custom-errors/)，完整后端清单可从[官方示例](https://github.com/kubernetes/ingress-nginx/blob/main/docs/examples/customization/custom-errors/custom-default-backend.yaml)取得；下载后保存为 `custom-default-backend.yaml` 并核对镜像。

部署default backend：

~~~sh
kubectl create -f custom-default-backend.yaml -n ingress-nginx
# service/nginx-errors created
# deployment.apps/nginx-errors created
kubectl get po -n ingress-nginx
nginx-errors-7486ff48d8-zwz6t    1/1 Running 0 6s
~~~

先创建错误页面 ConfigMap，再将 volumeMounts/volumes 合并到后端 Deployment 的对应位置，以下挂载部分是片段：

~~~yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: custom-error-pages
  namespace: ingress-nginx
data:
  "404": "<html><body><h1>404: Page not found</h1></body></html>"
  "502": "<html><body><h1>502: Bad gateway</h1></body></html>"
  "503": "<html><body><h1>503: Service unavailable</h1></body></html>"
~~~

~~~yaml
# 位于 nginx-error-server 容器下
volumeMounts:
- name: custom-error-pages
  mountPath: /www
  readOnly: true
# 位于 Pod spec 下，与 containers 同级
volumes:
- name: custom-error-pages
  configMap:
    name: custom-error-pages
    items:
    - key: "404"
      path: "404.html"
    - key: "502"
      path: "502.html"
    - key: "503"
      path: "503.html"
~~~

更改 ingress-nginx 的启动参数，支持自定义错误页：

~~~sh
# 若实际用DaemonSet部署，应改为对应的daemonset名称
kubectl edit deployment ingress-nginx-controller -n ingress-nginx
~~~

在控制器容器的 args 中添加：

~~~yaml
- --default-backend-service=ingress-nginx/nginx-errors
~~~

配置 ConfigMap，定义哪些错误码交给自定义错误后端处理：

~~~sh
kubectl edit cm ingress-nginx-controller -n ingress-nginx
~~~

在 data 中设置：

~~~yaml
data:
  custom-http-errors: "404,502,503"
~~~

更新完成以后访问一个不存在的页面，比如之前定义的 nginx.test.com。访问一个不存在的页面 123，就会返回 Error Server 中的页面。

### 根据请求头返回不同页面

比如手机端用户访问，返回手机端页面；电脑端用户访问返回电脑端页面。

下面演示按 User-Agent 跳转移动站点的历史 snippet 方式。User-Agent 可以伪造，不应将它用于安全身份判断。Snippet 可注入原生 Nginx 配置，只有可信的 Ingress 作者才能使用；控制器通常默认关闭 snippet，风险等级也可能阻止配置，不能为跑通实验就在共享生产入口全局放开。安全约束见[allow-snippet-annotations](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/configmap/#allow-snippet-annotations)。更常见的做法是由应用处理站点适配或在受支持网关中实现相应规则。

先准备移动端和桌面端后端。这里用普通 Nginx 页面演示域名跳转，实际服务可换成自己的应用：

~~~sh
kubectl create deployment phone --image=nginx:stable -n study-ingress
kubectl expose deployment phone --port=80 -n study-ingress
kubectl create deployment laptop --image=nginx:stable -n study-ingress
kubectl expose deployment laptop --port=80 -n study-ingress
~~~

创建移动站点的 Ingress：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: phone
  namespace: study-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: m.test.com
    http:
      paths:
      - backend:
          service:
            name: phone
            port:
              number: 80
        path: /
        pathType: ImplementationSpecific
~~~

桌面站点的 Ingress 检测 User-Agent，匹配移动端时重定向到 `m.test.com`：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: laptop
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/server-snippet: |
        set $agentflag 0;
        if ($http_user_agent ~* "(Android|iPhone|WindowsPhone|UC|Kindle)" ){
            set $agentflag 1;
        }
        if ( $agentflag = 1 ) {
            return 301 http://m.test.com;
        }
spec:
  ingressClassName: nginx
  rules:
  - host: test.com
    http:
      paths:
      - backend:
          service:
            name: laptop
            port:
              number: 80
        path: /
        pathType: ImplementationSpecific
~~~

## 先用权重理解灰度发布

- 灰度发布：上线了新版本v2代替v1，但是不会直接把全部流量切到v2。先切10%流量到v2，验证一下；再切50%流量；再切100%到v2。

- 蓝绿发布：v2版本部署之后，直接把流量全切到v2上面去，有问题再切回v1。同时存在两个版本。

> [!tip] 提示
> 灰度发布里面可以通过请求头设置一部分测试用户的流量可以进来，是更加稳妥的做法。

为了观察权重，先准备返回不同内容的 v1/v2 后端，以及指向 v1 的主 Ingress；它们与后面的完整 OpenResty 实验是两种独立演示。以下清单让两个后端分别返回 `Canary v1` 和 `Canary v2`，避免只有注解却没有可比较服务：

~~~yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: canary-pages
  namespace: study-ingress
data:
  v1.html: "Canary v1\n"
  v2.html: "Canary v2\n"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: canary-v1
  namespace: study-ingress
spec:
  replicas: 1
  selector:
    matchLabels:
      app: canary-v1
  template:
    metadata:
      labels:
        app: canary-v1
    spec:
      containers:
      - name: nginx
        image: nginx:stable
        ports:
        - containerPort: 80
        volumeMounts:
        - name: pages
          mountPath: /usr/share/nginx/html/index.html
          subPath: v1.html
      volumes:
      - name: pages
        configMap:
          name: canary-pages
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: canary-v2
  namespace: study-ingress
spec:
  replicas: 1
  selector:
    matchLabels:
      app: canary-v2
  template:
    metadata:
      labels:
        app: canary-v2
    spec:
      containers:
      - name: nginx
        image: nginx:stable
        ports:
        - containerPort: 80
        volumeMounts:
        - name: pages
          mountPath: /usr/share/nginx/html/index.html
          subPath: v2.html
      volumes:
      - name: pages
        configMap:
          name: canary-pages
---
apiVersion: v1
kind: Service
metadata:
  name: canary-v1
  namespace: study-ingress
spec:
  selector:
    app: canary-v1
  ports:
  - port: 80
    targetPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: canary-v2
  namespace: study-ingress
spec:
  selector:
    app: canary-v2
  ports:
  - port: 80
    targetPort: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: canary-main
  namespace: study-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: canary.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: canary-v1
            port:
              number: 80
~~~

再创建相同 host/path、指向 v2 的 Canary Ingress。`canary: "true"` 标识这是分流规则，`canary-weight: "10"` 指定约 10% 的随机权重；正常验证期间保留主 Ingress：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: canary-v2
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "10"
spec:
  ingressClassName: nginx
  rules:
  - host: canary.com # 用的是和v1同一个域名，但是后端svc是v2的svc。标注了是灰度环境，仅接收部分流量。
    http:
      paths:
      - backend:
          service:
            name: canary-v2
            port:
              number: 80
        path: /
        pathType: Prefix
~~~

在没有 Header/Cookie 优先规则且使用默认总权重时，权重 10 对应期望的 v1:v2 约 9:1；少量请求会有随机波动。

可以用ruby脚本测试流量分布：

~~~ruby
# 保存为 test-canary.rb
counts = Hash.new(0)

100.times do
  output = `curl -fsS http://canary.com/`
  version = output[/Canary (v[12])/, 1]
  counts[version || "unexpected"] += 1
end

puts counts
~~~

安装并运行 Ruby（RPM 系实验环境），DNS 或 hosts 需要先指向入口。示例输出仅用于说明抽样波动，不能要求每次恰好 90:10：

~~~sh
yum install ruby -y
ruby test-canary.rb
# {"v1"=>90, "v2"=>10}
ruby test-canary.rb
# {"v1"=>92, "v2"=>8}
ruby test-canary.rb
# {"v1"=>91, "v2"=>9}
~~~

实际使用过程中，v2流量全切过去发现没问题，有两种策略：

1. 将原主版本工作负载更新为已验证版本，再按既定发布流程恢复主路由。这会产生另一轮发布操作，需要继续验证。
2. 保持当前承载流量的版本，把另一组工作负载作为下一次发布目标。采用这种交替方式时，要同步维护主路由与 canary 注解，不能让旧权重规则意外参与下一轮分流。

## 常见问题

### 404 Not Found

404表示路由不存在，通常问题：

1. ingress路径配置不正确
2. ingress的配置没有被controller解析
3. 没使用正确的域名和路径
4. 代理的服务没有该路径的接口，或者GET POST方法不对。

### 413 Request Entity Too Large

上传文件返回 413 时，需要检查入口和后端各层的请求体大小限制。ingress-nginx 的 proxy-body-size 文档默认值为 1m，不是固定 8M；实际值还可能被全局 ConfigMap 或注解覆盖，此时可以通过 `nginx.ingress.kubernetes.io/proxy-body-size` 参数进行更改（也可以在 ConfigMap 中全局添加）。

一般建议在annotation中给每个ingress单独配置。

### 503 Service Unavailable

503  一般是代理的服务不可用导致的，通常问题如下：

1. Ingress 代理配置错误，比如 Service 名字或端口写错
2. Ingress 代理的 Service 不存在
3. Ingress 代理的 Service 后端 Pod 不正常

### 504 Gateway Timeout

504 一般是代理的服务处理请求的时间过长，导致 Nginx 等待超时，此时需要确认服务的处理时长，或者查看服务是否有问题。或者可能是网络不通（比如代理了外部的地址）。

也可以根据调整超时时间：（[Ingress Nginx超时配置](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/#custom-timeouts)）

~~~yaml
annotations:
  nginx.ingress.kubernetes.io/proxy-connect-timeout: "120"
  nginx.ingress.kubernetes.io/proxy-send-timeout: "120"
  nginx.ingress.kubernetes.io/proxy-read-timeout: "120"
~~~

### CORS 跨域报错

有时候某个域名里面可能去代理了一些其他的接口，这些接口可能属于其他的第三方的域名。

如果浏览器有如下报错，说明被跨域给拦截了，可以添加跨域配置。

官方文档：[Ingress Nginx CORS配置](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/#enable-cors)

CORS 是浏览器对响应施加的访问规则。需要由被请求的 API 服务或它的入口返回允许来源，页面一侧的 Ingress 无法替不受控制的第三方服务授权。

~~~yaml
annotations:
  # 允许跨域的请求方法
  nginx.ingress.kubernetes.io/enable-cors: "true"
  # 允许的方法
  nginx.ingress.kubernetes.io/cors-allow-methods: "PUT, GET, POST, OPTIONS, DELETE"
  # 允许携带的请求头
  nginx.ingress.kubernetes.io/cors-allow-headers: "X-Forwarded-For, Xapp123-XPTO"
  # 允许跨域的域名。意思是允许哪个域名跨到你这里来
  nginx.ingress.kubernetes.io/cors-allow-origin: "https://frontend.example.com"
~~~

使用 Cookie 或其他凭据时，应明确允许的 Origin，并检查 `cors-allow-credentials`、预检请求方法和请求头；CORS 放行不能替代 API 认证和授权。

## 集群中部署多套控制器

同一集群可以用不同控制器实例分别承接内网、外网或不同团队的入口。IngressClass 负责规则归属，但多实例本身不会自动实现完整的租户安全隔离。

下面以历史 ingress-nginx 实例演示 class、controller-class 和 leader election 标识的配合。它们的唯一性应在同一集群内规划。

主要启动参数片段：

~~~yaml
containers:
  - name: nginx-ingress-controller
    image: registry.cn-hangzhou.aliyuncs.com/google_containers/nginx-ingress-controller:v1.1.0
    args:
    - /nginx-ingress-controller
    - --ingress-class=ngx-ds
    - --controller-class=example.com/ngx-ds
    - --election-id=ngx-ds-leader
#注意：--ingress-class设置该Ingress Controller可监听的目标Ingress Class标识；
# 同集群不同实例使用不同的class及controller标识；nginx不是保留关键字
# 以下参数还应与对应IngressClass.spec.controller保持一致
~~~


为该实例创建 IngressClass，再由业务 Ingress 引用。实际 Deployment/DaemonSet、RBAC、ConfigMap 和准入 webhook 的名称也需隔离，不能仅改一个启动参数：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  name: ngx-ds
spec:
  controller: example.com/ngx-ds
~~~

创建 Ingress 规则时指定此 class。这里假设 default Namespace 已有名为 tomcat、服务端口为 8080 的 Service；请按自己的后端替换，不要把 Ingress 指向不存在的资源：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-myapp
  namespace: default
spec:
  ingressClassName: ngx-ds
  rules:
  - host: tomcat.lucky.com
    http:
      paths:
      - path: /
        pathType:  Prefix
        backend:
         service:
           name: tomcat
           port:
            number: 8080
~~~

## 存量 ingress-nginx 的性能排查与参数实验

大量请求进入时，入口可能先耗尽 CPU、内存、连接数或文件描述符，后端也可能是瓶颈。调参前先区分“入口处理不过来”与“后端响应慢”，记录 QPS、延迟分位数、错误率、CPU、内存和连接数，并在相同负载条件下逐项对照。对已退役控制器的调优不能替代安全迁移。

### Worker 数量和连接上限

`worker-processes` 控制 worker 数量，ingress-nginx ConfigMap 中对应连接上限的键是 `max-worker-connections`，不能照搬 Nginx 指令名写成 `worker-connections`。下面是参数实验片段；ConfigMap 名称必须与控制器的 `--configmap` 参数一致：

~~~yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ingress-nginx-controller
  namespace: ingress-nginx
data:
  worker-processes: "auto"
  max-worker-connections: "1024"
~~~

例如，4 核节点并不意味着必须固定“CPU 核数减 1”个 worker。还要考虑控制器容器可用的 CPU 配额、其他进程及工作负载。`1024` 只是一组便于观察的实验值，真实上限还受文件描述符、上游连接和内存影响；代理一个请求可能同时占用客户端连接和后端连接，连接数也不能直接当成 QPS。

每条连接占多少内存取决于 TLS、缓冲区、请求体、响应体和模块状态，无法用固定的几百字节或 2 MB 估算所有业务。可以用 JMeter、Gatling、Vegeta、ab 等工具逐步施压，观察进程内存和延迟变化，再调整参数。字段含义与文档默认值见[ConfigMap 参数](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/configmap/#max-worker-connections)。

### 缓存：先确认可缓存内容和实现支持

对于可公开缓存的响应，缓存可以减少后端请求。`proxy-cache-enabled` 和 `nginx.ingress.kubernetes.io/proxy-cache` 并不是社区 ingress-nginx 文档支持的通用开关，写入这些键不能证明缓存生效。应优先在应用、专门缓存代理或受支持网关中配置缓存。

维护历史环境时，Nginx 原生 `proxy_cache_path` 需要在 http 上下文声明缓存区，具体 location 再通过 `proxy_cache` 使用。下面给出受信任隔离实验中的完整关联示例，便于理解与原生指令的对应关系。它依赖允许 snippet 的控制器配置，会扩大 Ingress 作者的权限，不可直接用于多租户生产入口；允许条件、风险级别和过滤规则需核对实际控制器版本。管理员还要预先挂载并授权 `/tmp/nginx-cache` 缓存目录，观察磁盘与内存使用量。

~~~yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ingress-nginx-controller
  namespace: ingress-nginx
data:
  # 仅限可信作者的隔离历史实验，不能作为共享入口默认设置
  allow-snippet-annotations: "true"
  annotations-risk-level: "Critical"
  http-snippet: |
    proxy_cache_path /tmp/nginx-cache levels=1:2 keys_zone=public_cache:10m max_size=100m inactive=10m;
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  namespace: study-ingress
  annotations:
    nginx.ingress.kubernetes.io/configuration-snippet: |
      proxy_cache public_cache;
      proxy_cache_methods GET HEAD;
      proxy_cache_key "$scheme$host$request_uri";
      proxy_cache_valid 200 30s;
      proxy_cache_bypass $http_authorization $http_cookie;
      proxy_no_cache $http_authorization $http_cookie;
spec:
  ingressClassName: nginx
  rules:
  - host: example.com
    http:
      paths:
      - path: /test
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 80
~~~

其中的 `annotations-risk-level` 属于较新版本配置，不应直接拼进后面 v1.1.0 的完整历史安装清单。实验还要确认后端 Cache-Control、Set-Cookie、查询参数和用户身份的语义，不能缓存用户私有响应，也不能关闭默认保护来强行提高命中率。Nginx 指令的完整行为见[官方代理缓存说明](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_cache)。若控制器拒绝 snippet，应使用受支持的缓存实现，不要通过关闭校验绕过限制。

### 长连接复用与对照压测

一组历史观察中，同一应用通过 NodePort 暴露时达到十万级 QPS，经 Ingress 后约为五万级。这个数值未说明完整的硬件、TLS、响应大小和压测参数，只能作为“新增代理层后需要定位开销”的案例，不能推导普遍的性能比例。

维护这类环境时，可对照客户端到入口、入口到后端两段连接的复用。下面是这类案例的参数实验值，不能直接套用为容量配置：

~~~yaml
# 位于控制器ConfigMap的data中，名称以--configmap指定的资源为准
keep-alive: "100"
keep-alive-requests: "110"
upstream-keepalive-connections: "20000"
upstream-keepalive-requests: "110"
upstream-keepalive-timeout: "100"
~~~

`keep-alive` 是客户端空闲连接超时（秒），`keep-alive-requests` 是每条客户端连接的请求数上限；`upstream-keepalive-connections` 控制每个 worker 缓存的空闲上游连接数量，不是总并发上限。把它设成 20000 可能显著消耗文件描述符和内存，需结合 worker 数与后端容量计算。上游请求数与空闲超时则分别控制连接回收条件，详见[上游 keepalive 参数](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/configmap/#upstream-keepalive-connections)。

HTTP 连接复用减少重建开销，但也可能让四层分流集中到少数后端。每次只改变一组参数，比较错误率、延迟和资源占用，才有办法确认改动是否有效。

## 实战：Ingress灰度发布

### 场景一：按 Header 或 Cookie 识别用户

假设线上运行了一套对外提供 7 层服务的 Service A 服务，后来开发了个新版本 Service A’ 想要上线，但又不想直接替换掉原来的 Service A，希望先灰度一小部分用户，等运行一段时间足够稳定了再逐渐全量上线新版本，最后平滑下线旧版本。

这个时候就可以利用 Nginx Ingress 基于 Header 或 Cookie 进行流量切分的策略来发布，业务使用 Header 或 Cookie 来标识不同类型的用户，我们通过配置 Ingress 来实现让带有指定 Header 或 Cookie 的请求被转发到新版本，其它的仍然转发到旧版本，从而实现将新版本灰度给部分用户。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312281017402.png" alt="image-20231228101712175" style="zoom:50%;" />

### 场景二：按比例随机分配请求

假设线上运行了一套对外提供 7 层服务的 Service B 服务，后来修复了一些问题，需要灰度上线一个新版本 Service B’，但又不想直接替换掉原来的 Service B，而是让先切 10% 的流量到新版本，等观察一段时间稳定后再逐渐加大新版本的流量比例直至完全替换旧版本，最后再平滑下线旧版本，从而实现切一定比例的流量给新版本。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312281018356.png" alt="image-20231228101848227" style="zoom:50%;" />


### 分流规则及优先级

先创建指向 v1 的普通 Ingress，再创建相同 host/path、指向 v2 的 Canary Ingress，并在后者设置 `canary: "true"`。常用注解如下，均为 ingress-nginx 实现特性：

| 注解后缀 | 作用 |
| --- | --- |
| `canary-by-header` | 指定请求头名；值为 always 时进入 Canary，never 时不进入 |
| `canary-by-header-value` | 指定请求头的精确匹配值 |
| `canary-by-header-pattern` | 对请求头值进行正则匹配 |
| `canary-by-cookie` | 指定 Cookie 名；always 进入 Canary，never 排除，其他值忽略此规则 |
| `canary-weight` | 按权重随机分配流量，默认总权重为 100；可以另设 canary-weight-total |

完整键均以 `nginx.ingress.kubernetes.io/` 开头，规则优先级为 Header → Cookie → Weight。因此，权重为 0 不会阻止由 Header/Cookie 明确导入的请求，权重为 100 也不会覆盖明确排除的请求。详见[Canary 注解说明](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/#canary)。

A/B 测试通常希望固定分组比较用户行为，金丝雀发布则逐步扩大新版本流量并观察风险，两者都可以使用这些分流机制，但发布是否安全还要看错误率、延迟、业务指标及回滚设计。少量请求的随机结果不会严格等于配置百分比。

### 实验：从两个后端到三种分流方式

本组资源使用 `default` Namespace，与前面的 `study-ingress` 示例分开。实验控制器需支持这些历史注解；`openresty/openresty:centos` 是旧实验镜像，执行前应检查可获取性与兼容性并固定已验证版本，不应直接拿它构建生产镜像。

先创建 v1/v2 两个 Deployment、配置和 Service，返回不同文本以便观察。后续 Header、Cookie、Weight 三组示例使用相同的 `ing-nginx-canary` 名称，按顺序替换实验；换下一组时应移除上一组特定注解，避免被优先级影响。

#### 第一步：搭建 v1 和 v2 两个服务

~~~yaml
#v1
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-nginx-v1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
      version: v1
  template:
    metadata:
      labels:
        app: nginx
        version: v1
    spec:
      containers:
      - name: nginx
        image: "openresty/openresty:centos"
        imagePullPolicy: IfNotPresent
        ports:
        - name: http
          protocol: TCP
          containerPort: 80
        volumeMounts:
        - mountPath: /usr/local/openresty/nginx/conf/nginx.conf
          name: config
          subPath: nginx.conf
      volumes:
      - name: config
        configMap:
          name: cm-nginx-v1
---
apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    app: nginx
    version: v1
  name: cm-nginx-v1
data:
  nginx.conf: |-
    worker_processes  1;
    events {
        accept_mutex on;
        multi_accept on;
        use epoll;
        worker_connections  1024;
    }
    http {
        ignore_invalid_headers off;
        server {
            listen 80;
            location / {
                access_by_lua '
                    local header_str = ngx.say("nginx-v1") -- 指定到根目录的请求返回nginx-v1
                ';
            }
        }
    }
---
apiVersion: v1
kind: Service
metadata:
  name: svc-nginx-v1
spec:
  selector:
    app: nginx
    version: v1
  type: ClusterIP
  ports:
  - port: 80
    protocol: TCP
    name: http
~~~

~~~yaml
#v2
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-nginx-v2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
      version: v2
  template:
    metadata:
      labels:
        app: nginx
        version: v2
    spec:
      containers:
      - name: nginx
        image: "openresty/openresty:centos"
        imagePullPolicy: IfNotPresent
        ports:
        - name: http
          protocol: TCP
          containerPort: 80
        volumeMounts:
        - mountPath: /usr/local/openresty/nginx/conf/nginx.conf #mountPath可以是一个文件
          name: config
          subPath: nginx.conf #用于指定挂载卷中的子路径。可以将卷中的特定目录或文件，而不是整个卷挂载到 Pod 中的容器。
      volumes:
      - name: config
        configMap:
          name: cm-nginx-v2
---
apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    app: nginx
    version: v2
  name: cm-nginx-v2
data:
  nginx.conf: |-
    worker_processes  1;
    events {
        accept_mutex on;
        multi_accept on;
        use epoll;
        worker_connections  1024;
    }
    http {
        ignore_invalid_headers off;
        server {
            listen 80;
            location / {
                access_by_lua '
                    local header_str = ngx.say("nginx-v2") -- 指定根目录的url返回nginx-2
                ';
            }
        }
    }
---
apiVersion: v1
kind: Service
metadata:
  name: svc-nginx-v2
spec:
  type: ClusterIP
  ports:
  - port: 80
    protocol: TCP
    name: http
  selector:
    app: nginx
    version: v2
~~~

#### 第二步：创建主 Ingress

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ing-nginx
spec:
  ingressClassName: nginx
  rules:
  - host: canary.example.com
    http:
      paths:
      - path: /  #配置访问路径；v1规则必须显式提供pathType，本例匹配根路径
        pathType:  Prefix
        backend:  #配置后端服务
         service:
           name: svc-nginx-v1
           port:
            number: 80
~~~

~~~bash
#验证ingress访问后端svc-pod
curl -H "Host: canary.example.com" http://192.168.40.6 #ingress暴露的ip
~~~

#### 第三步：验证 Header 分流

创建 Canary Ingress，指定 v2 版本的后端服务，且加上一些 annotation，实现仅将带有名为 Region 且值为 cd 或 sz 的请求头的请求转发给当前 Canary Ingress，模拟灰度新版本给成都和深圳地域的用户。

在 Canary Ingress 中配置如下：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ing-nginx-canary
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-by-header: "Region"
    nginx.ingress.kubernetes.io/canary-by-header-pattern: "^(cd|sz)$"
spec:
  ingressClassName: nginx
  rules:
  - host: canary.example.com
    http:
      paths:
      - path: /  #配置访问路径；v1规则必须显式提供pathType，本例匹配根路径
        pathType:  Prefix
        backend:  #配置后端服务
         service:
           name: svc-nginx-v2
           port:
            number: 80
~~~

~~~bash
#测试模拟带header的请求
curl -H "Host: canary.example.com" -H "Region: cd" http://192.168.40.6
curl -H "Host: canary.example.com" -H "Region: sz" http://192.168.40.6
curl -H "Host: canary.example.com" http://192.168.40.6
#可以看到，只有header带了Region并且值为cd | sz代理到v2
~~~

#### 第四步：验证 Cookie 分流

先从上一步资源移除 Header 相关注解，否则更高优先级的规则仍会参与分流：

~~~sh
kubectl annotate ingress ing-nginx-canary -n default nginx.ingress.kubernetes.io/canary-by-header- nginx.ingress.kubernetes.io/canary-by-header-pattern-
~~~

Cookie 分流使用指定的 Cookie 名，并要求值为 `always` 或 `never`；仅仅存在 Cookie 不足以保证进入 Canary。其他值会忽略这条规则，继续检查后续规则。

这里以模拟灰度成都地域用户为例，仅将带有名为 user_from_cd 的 cookie 的请求转发给当前 Canary Ingress 。

在 Canary Ingress 中配置如下：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-by-cookie: "user_from_cd"
  name: ing-nginx-canary
spec:
  ingressClassName: nginx
  rules:
  - host: canary.example.com
    http:
      paths:
      - path: /  #配置访问路径；v1规则必须显式提供pathType，本例匹配根路径
        pathType:  Prefix
        backend:  #配置后端服务
         service:
           name: svc-nginx-v2
           port:
            number: 80
~~~

~~~bash
#测试带cookie的请求
curl -s -H "Host: canary.example.com" --cookie "user_from_cd=always" http://192.168.40.6
curl -s -H "Host: canary.example.com" --cookie "user_from_bj=always" http://192.168.40.6
~~~

#### 第五步：验证权重分流

先移除上一步的 Cookie 分流规则，再应用下面的权重清单：

~~~sh
kubectl annotate ingress ing-nginx-canary -n default nginx.ingress.kubernetes.io/canary-by-cookie-
~~~

直接定义需要导入的流量比例，这里以导入 10% 流量到 v2 版本为例。

在 Canary Ingress 的注解中指定权重：

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "10"
  name: ing-nginx-canary
spec:
  ingressClassName: nginx
  rules:
  - host: canary.example.com
    http:
      paths:
      - path: /  #配置访问路径；v1规则必须显式提供pathType，本例匹配根路径
        pathType:  Prefix
        backend:  #配置后端服务
         service:
           name: svc-nginx-v2
           port:
            number: 80
~~~

~~~bash
#测试比例
for i in {1..20}; do curl -H "Host: canary.example.com" http://192.168.40.6; done;
~~~

## 历史完整实验：Nginx + Keepalived 的入口高可用

本组实验使用社区 ingress-nginx v1.1.0 和旧 Linux 环境，目的是说明 hostNetwork、多副本代理、前置 TCP 代理与 VIP 漂移如何协作。完整安装清单中的旧镜像、RBAC 和准入组件不适配所有现代集群，也不再具备持续安全维护；只能在隔离、无敏感数据的历史环境理解和复现。新建入口应选受支持实现。

VIP 漂移要求节点网络允许 VRRP、地址通告及相应的二层邻居更新，公有云不能假设默认支持。提前为两台节点规划地址和网卡，本文沿用 `192.168.40.5`、`192.168.40.6` 及 VIP `192.168.40.8`。前面实验使用的入口地址应按这里的实际拓扑调整。

### 架构示意图

两个工作节点分别运行一个入口 Pod，通过 Deployment、nodeSelector 和 Pod 反亲和性保证分开部署。入口 Pod 使用 hostNetwork，直接监听节点的 80/443。两台节点另外运行前置 Nginx，Keepalived 让其中一台持有 VIP，前置 Nginx 再把请求分发给两台入口。

![image-20231209114749417](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312091147480.png)

### 搭建高可用入口的五个步骤

#### 第一步：准备节点和历史镜像

先给两台实验入口节点加标签，完整清单中的 nodeSelector 会据此限制调度；节点名按实际替换：

~~~sh
kubectl label nodes node-01 node-02 ingress=true
~~~

~~~bash
# 解压历史课件镜像到工作节点；核对归档内部标签与下方清单一致
ctr -n=k8s.io images import ingress-nginx-controllerv1.1.0.tar.gz
ctr -n=k8s.io images import kube-webhook-certgen-v1.1.0.tar.gz
~~~

#### 第二步：部署历史控制器

> [!warning] 注意
> 社区项目名是 `ingress-nginx`，NGINX 自己的控制器属于另一个项目。两者配置和维护周期不同，不能根据名称互换镜像或注解；这里的社区实现已退役。

这份清单基于[历史 baremetal 部署模板](https://github.com/kubernetes/ingress-nginx/tree/main/deploy/static/provider/baremetal)，加入节点选择和必须满足的 Pod 反亲和性；两台目标节点应有足够资源且允许调度。清单中启用 snippet 是旧实验设置，只适用于可信用户的隔离环境。镜像导入归档的文件名不代表其内部镜像标签，应检查 `ctr -n=k8s.io images list` 是否包含清单要求的 controller v1.1.0 和 certgen v1.1.1，缺少时先取得匹配归档。

~~~yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ingress-nginx
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx

---
# Source: ingress-nginx/templates/controller-serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: ingress-nginx
  namespace: ingress-nginx
automountServiceAccountToken: true
---
# Source: ingress-nginx/templates/controller-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: ingress-nginx-controller
  namespace: ingress-nginx
data:
  allow-snippet-annotations: 'true'
---
# Source: ingress-nginx/templates/clusterrole.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
  name: ingress-nginx
rules:
  - apiGroups:
      - ''
    resources:
      - configmaps
      - endpoints
      - nodes
      - pods
      - secrets
      - namespaces
    verbs:
      - list
      - watch
  - apiGroups:
      - ''
    resources:
      - nodes
    verbs:
      - get
  - apiGroups:
      - ''
    resources:
      - services
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingresses
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - ''
    resources:
      - events
    verbs:
      - create
      - patch
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingresses/status
    verbs:
      - update
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingressclasses
    verbs:
      - get
      - list
      - watch
---
# Source: ingress-nginx/templates/clusterrolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
  name: ingress-nginx
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: ingress-nginx
subjects:
  - kind: ServiceAccount
    name: ingress-nginx
    namespace: ingress-nginx
---
# Source: ingress-nginx/templates/controller-role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: ingress-nginx
  namespace: ingress-nginx
rules:
  - apiGroups:
      - ''
    resources:
      - namespaces
    verbs:
      - get
  - apiGroups:
      - ''
    resources:
      - configmaps
      - pods
      - secrets
      - endpoints
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - ''
    resources:
      - services
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingresses
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingresses/status
    verbs:
      - update
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingressclasses
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - ''
    resources:
      - configmaps
    resourceNames:
      - ingress-controller-leader
    verbs:
      - get
      - update
  - apiGroups:
      - ''
    resources:
      - configmaps
    verbs:
      - create
  - apiGroups:
      - ''
    resources:
      - events
    verbs:
      - create
      - patch
---
# Source: ingress-nginx/templates/controller-rolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: ingress-nginx
  namespace: ingress-nginx
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: ingress-nginx
subjects:
  - kind: ServiceAccount
    name: ingress-nginx
    namespace: ingress-nginx
---
# Source: ingress-nginx/templates/controller-service-webhook.yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: ingress-nginx-controller-admission
  namespace: ingress-nginx
spec:
  type: ClusterIP
  ports:
    - name: https-webhook
      port: 443
      targetPort: webhook
      appProtocol: https
  selector:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/component: controller
---
# Source: ingress-nginx/templates/controller-service.yaml
apiVersion: v1
kind: Service
metadata:
  annotations: {}
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: ingress-nginx-controller
  namespace: ingress-nginx
spec:
  type: NodePort
  ipFamilyPolicy: SingleStack
  ipFamilies:
    - IPv4
  ports:
    - name: http
      port: 80
      protocol: TCP
      targetPort: http
      appProtocol: http
    - name: https
      port: 443
      protocol: TCP
      targetPort: https
      appProtocol: https
  selector:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/component: controller
---
# Source: ingress-nginx/templates/controller-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: ingress-nginx-controller
  namespace: ingress-nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: ingress-nginx
      app.kubernetes.io/instance: ingress-nginx
      app.kubernetes.io/component: controller
  revisionHistoryLimit: 10
  minReadySeconds: 0
  template:
    metadata:
      labels:
        app.kubernetes.io/name: ingress-nginx
        app.kubernetes.io/instance: ingress-nginx
        app.kubernetes.io/component: controller
    spec:
      hostNetwork: true
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app.kubernetes.io/name: ingress-nginx
            topologyKey: kubernetes.io/hostname
      dnsPolicy: ClusterFirstWithHostNet
      containers:
        - name: controller
          image: registry.cn-hangzhou.aliyuncs.com/google_containers/nginx-ingress-controller:v1.1.0
          imagePullPolicy: IfNotPresent
          lifecycle:
            preStop:
              exec:
                command:
                  - /wait-shutdown
          args:
            - /nginx-ingress-controller
            - --election-id=ingress-controller-leader
            - --controller-class=k8s.io/ingress-nginx
            - --configmap=$(POD_NAMESPACE)/ingress-nginx-controller
            - --validating-webhook=:8443
            - --validating-webhook-certificate=/usr/local/certificates/cert
            - --validating-webhook-key=/usr/local/certificates/key
          securityContext:
            capabilities:
              drop:
                - ALL
              add:
                - NET_BIND_SERVICE
            runAsUser: 101
            allowPrivilegeEscalation: true
          env:
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
            - name: LD_PRELOAD
              value: /usr/local/lib/libmimalloc.so
          livenessProbe:
            failureThreshold: 5
            httpGet:
              path: /healthz
              port: 10254
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 1
          readinessProbe:
            failureThreshold: 3
            httpGet:
              path: /healthz
              port: 10254
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 1
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
            - name: https
              containerPort: 443
              protocol: TCP
            - name: webhook
              containerPort: 8443
              protocol: TCP
          volumeMounts:
            - name: webhook-cert
              mountPath: /usr/local/certificates/
              readOnly: true
          resources:
            requests:
              cpu: 100m
              memory: 90Mi
      nodeSelector:
        kubernetes.io/os: linux
        ingress: "true"
      serviceAccountName: ingress-nginx
      terminationGracePeriodSeconds: 300
      volumes:
        - name: webhook-cert
          secret:
            secretName: ingress-nginx-admission
---
# Source: ingress-nginx/templates/controller-ingressclass.yaml
# We don't support namespaced ingressClass yet
# So a ClusterRole and a ClusterRoleBinding is required
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: controller
  name: nginx
spec:
  controller: k8s.io/ingress-nginx
---
# Source: ingress-nginx/templates/admission-webhooks/validating-webhook.yaml
# before changing this value, check the required kubernetes version
# https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/#prerequisites
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
  name: ingress-nginx-admission
webhooks:
  - name: validate.nginx.ingress.kubernetes.io
    matchPolicy: Equivalent
    rules:
      - apiGroups:
          - networking.k8s.io
        apiVersions:
          - v1
        operations:
          - CREATE
          - UPDATE
        resources:
          - ingresses
    failurePolicy: Fail
    sideEffects: None
    admissionReviewVersions:
      - v1
    clientConfig:
      service:
        namespace: ingress-nginx
        name: ingress-nginx-controller-admission
        path: /networking/v1/ingresses
---
# Source: ingress-nginx/templates/admission-webhooks/job-patch/serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ingress-nginx-admission
  namespace: ingress-nginx
  annotations:
    helm.sh/hook: pre-install,pre-upgrade,post-install,post-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
---
# Source: ingress-nginx/templates/admission-webhooks/job-patch/clusterrole.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ingress-nginx-admission
  annotations:
    helm.sh/hook: pre-install,pre-upgrade,post-install,post-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
rules:
  - apiGroups:
      - admissionregistration.k8s.io
    resources:
      - validatingwebhookconfigurations
    verbs:
      - get
      - update
---
# Source: ingress-nginx/templates/admission-webhooks/job-patch/clusterrolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ingress-nginx-admission
  annotations:
    helm.sh/hook: pre-install,pre-upgrade,post-install,post-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: ingress-nginx-admission
subjects:
  - kind: ServiceAccount
    name: ingress-nginx-admission
    namespace: ingress-nginx
---
# Source: ingress-nginx/templates/admission-webhooks/job-patch/role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ingress-nginx-admission
  namespace: ingress-nginx
  annotations:
    helm.sh/hook: pre-install,pre-upgrade,post-install,post-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
rules:
  - apiGroups:
      - ''
    resources:
      - secrets
    verbs:
      - get
      - create
---
# Source: ingress-nginx/templates/admission-webhooks/job-patch/rolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ingress-nginx-admission
  namespace: ingress-nginx
  annotations:
    helm.sh/hook: pre-install,pre-upgrade,post-install,post-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: ingress-nginx-admission
subjects:
  - kind: ServiceAccount
    name: ingress-nginx-admission
    namespace: ingress-nginx
---
# Source: ingress-nginx/templates/admission-webhooks/job-patch/job-createSecret.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: ingress-nginx-admission-create
  namespace: ingress-nginx
  annotations:
    helm.sh/hook: pre-install,pre-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
spec:
  template:
    metadata:
      name: ingress-nginx-admission-create
      labels:
        helm.sh/chart: ingress-nginx-4.0.10
        app.kubernetes.io/name: ingress-nginx
        app.kubernetes.io/instance: ingress-nginx
        app.kubernetes.io/version: 1.1.0
        app.kubernetes.io/managed-by: Helm
        app.kubernetes.io/component: admission-webhook
    spec:
      containers:
        - name: create
          image: registry.cn-hangzhou.aliyuncs.com/google_containers/kube-webhook-certgen:v1.1.1
          imagePullPolicy: IfNotPresent
          args:
            - create
            - --host=ingress-nginx-controller-admission,ingress-nginx-controller-admission.$(POD_NAMESPACE).svc
            - --namespace=$(POD_NAMESPACE)
            - --secret-name=ingress-nginx-admission
          env:
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
          securityContext:
            allowPrivilegeEscalation: false
      restartPolicy: OnFailure
      serviceAccountName: ingress-nginx-admission
      nodeSelector:
        kubernetes.io/os: linux
      securityContext:
        runAsNonRoot: true
        runAsUser: 2000
---
# Source: ingress-nginx/templates/admission-webhooks/job-patch/job-patchWebhook.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: ingress-nginx-admission-patch
  namespace: ingress-nginx
  annotations:
    helm.sh/hook: post-install,post-upgrade
    helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded
  labels:
    helm.sh/chart: ingress-nginx-4.0.10
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/version: 1.1.0
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/component: admission-webhook
spec:
  template:
    metadata:
      name: ingress-nginx-admission-patch
      labels:
        helm.sh/chart: ingress-nginx-4.0.10
        app.kubernetes.io/name: ingress-nginx
        app.kubernetes.io/instance: ingress-nginx
        app.kubernetes.io/version: 1.1.0
        app.kubernetes.io/managed-by: Helm
        app.kubernetes.io/component: admission-webhook
    spec:
      containers:
        - name: patch
          image: registry.cn-hangzhou.aliyuncs.com/google_containers/kube-webhook-certgen:v1.1.1
          imagePullPolicy: IfNotPresent
          args:
            - patch
            - --webhook-name=ingress-nginx-admission
            - --namespace=$(POD_NAMESPACE)
            - --patch-mutating=false
            - --secret-name=ingress-nginx-admission
            - --patch-failure-policy=Fail
          env:
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
          securityContext:
            allowPrivilegeEscalation: false
      restartPolicy: OnFailure
      serviceAccountName: ingress-nginx-admission
      nodeSelector:
        kubernetes.io/os: linux
      securityContext:
        runAsNonRoot: true
        runAsUser: 2000
~~~

部署后应在两台目标节点上各运行一个入口 Pod。`ingress-nginx-admission-create-*` 和 `ingress-nginx-admission-patch-*` 是创建证书、更新 webhook 的一次性 Job，不应把它们误认为入口副本。裸清单中的 Helm hook 注解不会由 kubectl 自动执行，Job 会按普通资源创建，失败时需看日志和依赖状态。

> [!warning] 注意
> 访问节点 80 端口被拒绝时，先核对暴露方式。NodePort 应访问实际 nodePort，hostNetwork 才直接占用节点端口；还要检查 Pod 就绪状态、端口冲突、监听地址和防火墙。本实验的 hostNetwork 位于 Deployment.spec.template.spec，与 IngressClass 无关。

#### 第三步：安装前置 Nginx 和 Keepalived

~~~bash
#两个工作节点上安装
yum install  epel-release  nginx keepalived nginx-mod-stream  -y
~~~

~~~bash
#修改nginx配置文件，nginx监听30080端口
vim /etc/nginx/nginx.conf
# 使用sudo或管理员权限编辑配置，不要把系统配置设为所有用户可写

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

stream {

    log_format  main  '$remote_addr $upstream_addr - [$time_local] $status $upstream_bytes_sent';

    access_log  /var/log/nginx/k8s-access.log  main;

    upstream k8s-ingress-controller {
       server 192.168.40.5:80 weight=5 max_fails=3 fail_timeout=30s;   # node-01 IP:PORT
       server 192.168.40.6:80 weight=5 max_fails=3 fail_timeout=30s;  # node-02 IP:PORT
    }
    
    server {
       listen 30080;
       proxy_pass k8s-ingress-controller;
    }

    upstream k8s-ingress-controller-tls {
       server 192.168.40.5:443 max_fails=3 fail_timeout=30s;
       server 192.168.40.6:443 max_fails=3 fail_timeout=30s;
    }

    server {
       listen 30443;
       proxy_pass k8s-ingress-controller-tls;
    }
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

}

#备注：
#server 反向服务地址和端口
#weight 权重
#max_fails 失败多少次，认为主机已挂掉，则踢出
#fail_timeout 踢出后重新探测时间
# 本例30080转发HTTP、30443透传TLS；端口只需合法、未占用且防火墙放行，不要求大于30000
~~~

~~~bash
#主keepalived，暴露VIP 192.168.40.8
vim /etc/keepalived/keepalived.conf

global_defs { 
   notification_email { 
     acassen@firewall.loc 
     failover@firewall.loc 
     sysadmin@firewall.loc 
   } 
   notification_email_from Alexandre.Cassen@firewall.loc  
   smtp_server 127.0.0.1 
   smtp_connect_timeout 30 
   router_id NGINX_MASTER
   enable_script_security
   script_user root
} 

vrrp_script check_nginx {
    script "/etc/keepalived/check_nginx.sh"
    interval 3
    timeout 3
    fall 2
    rise 2
}

vrrp_instance VI_1 { 
    state MASTER 
    interface eth0  # 修改为实际网卡名
    virtual_router_id 51 # 同一主备组保持一致，不同VIP组避免冲突 
    priority 100    # 优先级，备服务器设置 90 
    advert_int 1    # 指定VRRP 心跳包通告间隔时间，默认1秒 
    authentication { 
        auth_type PASS      
        auth_pass 1111 
    }  
    # 虚拟IP,要跟VM在一个网段
    virtual_ipaddress { 
        192.168.40.8/24
    } 
    track_script {
        check_nginx
    } 
}
#vrrp_script：指定检查nginx工作状态脚本（根据nginx状态判断是否故障转移）
#virtual_ipaddress：虚拟IP（VIP）
~~~

~~~bash
#备keepalived
vim /etc/keepalived/keepalived.conf

global_defs { 
   notification_email { 
     acassen@firewall.loc 
     failover@firewall.loc 
     sysadmin@firewall.loc 
   } 
   notification_email_from Alexandre.Cassen@firewall.loc  
   smtp_server 127.0.0.1 
   smtp_connect_timeout 30 
   router_id NGINX_BACKUP
   enable_script_security
   script_user root
} 

vrrp_script check_nginx {
    script "/etc/keepalived/check_nginx.sh"
    interval 3
    timeout 3
    fall 2
    rise 2
}

vrrp_instance VI_1 { 
    state BACKUP 
    interface eth0  # 修改为实际网卡名
    virtual_router_id 51 # 同一主备组保持一致，不同VIP组避免冲突 
    priority 90    # 优先级，备服务器设置 90 
    advert_int 1    # 指定VRRP 心跳包通告间隔时间，默认1秒 
    authentication { 
        auth_type PASS      
        auth_pass 1111 
    }  
    # 虚拟IP,要跟VM在一个网段
    virtual_ipaddress { 
        192.168.40.8/24
    } 
    track_script {
        check_nginx
    } 
}
#vrrp_script：指定检查nginx工作状态脚本（根据nginx状态判断是否故障转移）
#virtual_ipaddress：虚拟IP（VIP）
~~~

本例 HTTP 数据路径为 `VIP:30080 → 前置 Nginx stream → 某入口节点:80 → ingress-nginx → 后端 Pod`。Service 提供后端关联，默认数据路径不必先经过其 ClusterIP；HTTPS 则使用 `VIP:30443 → 节点:443` 透传 TLS。

#### 第四步：让 Keepalived 跟踪前置 Nginx

Keepalived 根据脚本退出码判断健康：0 表示成功，非 0 表示失败。本例连续两次失败进入故障状态，连续两次成功恢复，配置含义见[官方配置手册](https://keepalived.org/documentation/keepalived-conf/)。脚本检测的是前置 Nginx 进程状态，不代表每个后端应用都健康，还需配合 LB 与入口探针。

~~~bash
#!/bin/bash
# Nginx不活跃时尝试启动，再通过退出码向Keepalived报告状态。
if ! /usr/bin/systemctl is-active --quiet nginx; then
    /usr/bin/systemctl start nginx
    sleep 2
fi
/usr/bin/systemctl is-active --quiet nginx
~~~

~~~sh
chown root:root /etc/keepalived/check_nginx.sh
chmod 750 /etc/keepalived/check_nginx.sh
~~~

#### 第五步：检查配置并启动服务

~~~bash
nginx -t
keepalived --config-test
systemctl daemon-reload
systemctl enable nginx keepalived
systemctl start nginx
systemctl start keepalived
~~~

> `systemctl daemon-reload`命令用于重新加载systemd管理器配置。这包括重新加载所有的systemd服务单元。当你修改了任何systemd服务单元的配置文件后，例如`/etc/systemd/system/`目录下的文件，你需要运行这个命令来使改动生效。

## 实验：通过 HTTP 入口发布 Tomcat

有了入口后，再从后端到路由逐步验证。这里使用 `default` Namespace，并沿用历史镜像 `tomcat:8.5.34-jre8-alpine` 演示端口关系；该镜像和 Tomcat 分支属于旧实验环境，生产应换成受支持版本。

### 第一步：创建后端 Service 和 Deployment

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: svc-tomcat
  namespace: default
spec:
  selector:
    app: tomcat
    release: canary
  ports:
  - name: http
    targetPort: 8080
    port: 8080 # HTTP服务端口，由Ingress引用
  - name: ajp
    targetPort: 8009
    port: 8009 # AJP实验端口，不由本例HTTP Ingress转发
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deploy-tomcat
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: tomcat
      release: canary
  template:
    metadata:
      labels:
        app: tomcat
        release: canary
    spec:
      containers:
      - name: tomcat
        image: tomcat:8.5.34-jre8-alpine 
        imagePullPolicy: IfNotPresent  
        ports:
        - name: http
          containerPort: 8080
        - name: ajp
          containerPort: 8009
~~~

### 第二步：创建 HTTP Ingress

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-tomcat
  namespace: default
  # ingressClassName自Kubernetes 1.18引入，优先使用此字段；旧annotation按控制器兼容性处理
spec:
  ingressClassName: nginx
  rules:
  - host: tomcat.hanxux.com
    http:
      paths:
      - backend:
          service:
            name: svc-tomcat
            port:
              number: 8080
        path: / #指定路由，这里是根路由
        pathType: Prefix
~~~

### 第三步：检查控制器生成的配置

~~~bash
kubectl exec -it ingress-nginx-controller-64bdc78c96-mkf2s -n ingress-nginx  -- /bin/sh
cat nginx.conf
#可以看到ingress里面定义的规则，已经定义到ingress controller的nginx规则里面了
server {
                server_name tomcat.hanxux.com ;

                listen 80  ;
                listen [::]:80  ;
                listen 443  ssl http2 ;
                listen [::]:443  ssl http2 ;

                set $proxy_upstream_name "-";

                ssl_certificate_by_lua_block {
                        certificate.call()
                }

                location / {

                        set $namespace      "default";
                        set $ingress_name   "ingress-tomcat";
                        set $service_name   "svc-tomcat";
                        set $service_port   "8080";
                        set $location_path  "/";
                        set $global_rate_limit_exceeding n;
                        # 其余配置省略：这是查看输出的片段，不是完整nginx.conf
~~~

### 第四步：按暴露方式访问

控制器可由 NodePort、LoadBalancer Service 或 hostNetwork 对外暴露，也可以在前面加 LB/VIP。ExternalName 只返回 DNS 别名，不负责把控制器暴露到外网。

如果使用 NodePort，先查看实际端口，下面是历史示例输出：

~~~bash
kubectl get svc -n ingress-nginx
# NAME                       TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)
# ingress-nginx-controller   NodePort   10.105.87.199    <none>        80:31414/TCP,443:31126/TCP
~~~

此时应请求 `节点IP:31414`，并让 Host 匹配 `tomcat.hanxux.com`。若使用本章的 hostNetwork，直接访问对应节点 80 端口；若使用 Keepalived，则请求 VIP 的 30080：

~~~sh
# NodePort示例：节点IP和端口按实际结果替换
curl -H 'Host: tomcat.hanxux.com' http://192.168.40.5:31414/
# 本章Keepalived示例
curl --resolve tomcat.hanxux.com:30080:192.168.40.8 http://tomcat.hanxux.com:30080/
~~~

直接访问 IP 只会携带该 IP 的 Host，无法命中特定域名规则时，控制器可能返回默认后端的 404。可以通过 DNS、hosts 或 curl 的 Host/resolve 参数发送正确域名；不是所有路由都要求配置 hosts 文件。

## 实验：通过 HTTPS 入口发布 Tomcat

TLS Secret、域名和后端 Service 需要对应起来。前面的 Keepalived 配置中，HTTP 是 30080，TLS 透传使用新增的 30443；不能把 HTTPS 请求发送到仅转发 HTTP 的 30080 端口。

### 第一步：创建测试证书

~~~bash
cd /root/
openssl genrsa -out tls.key 2048 #tls.key是私钥
openssl req -new -x509 -key tls.key -out tls.crt -days 365 -subj /C=CN/ST=SH/L=SH/O=CKA/CN=hangx.tomcat.com -addext "subjectAltName=DNS:hangx.tomcat.com" # SAN匹配测试域名
~~~

### 第二步：创建 TLS Secret

~~~bash
kubectl create secret tls secret-tomcat-ingress --cert=tls.crt --key=tls.key -n default
~~~

### 第三步：配置 HTTPS Ingress

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-tomcat-tls
  namespace: default
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    -  hangx.tomcat.com
    secretName: secret-tomcat-ingress
  rules:
  - host: hangx.tomcat.com
    http:
      paths:
      - path: /
        pathType:  Prefix
        backend:
         service:
           name: svc-tomcat
           port:
            number: 8080
~~~

### 第四步：验证 TLS 和后端响应

使用 Keepalived 时，域名指向 VIP 并访问 30443。`--resolve` 同时保证请求 Host 与 TLS SNI 使用目标域名，`--cacert` 信任本次自签证书；不要以长期关闭证书校验替代证书配置。

~~~sh
curl --cacert tls.crt --resolve hangx.tomcat.com:30443:192.168.40.8 https://hangx.tomcat.com:30443/
# 直接使用hostNetwork时，改为入口节点的443
curl --cacert tls.crt --resolve hangx.tomcat.com:443:192.168.40.5 https://hangx.tomcat.com/
~~~

若 TLS 握手失败，先检查端口、Secret、SAN/SNI 和信任链；握手成功但返回 404，应检查 Host/path 与后端接口；返回 503 时再检查 Service 端口、EndpointSlice 和 Pod 就绪状态。按这几层分别验证，可以避免把证书、路由与应用故障混在一起。
