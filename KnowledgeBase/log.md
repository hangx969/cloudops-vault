---
title: 操作日志
tags:
  - knowledgebase/log
date: 2026-04-17
---

# 📋 操作日志

> 仅追加的操作记录——摄入、查询、lint、结构调整。
> 最新条目在最上方。

## [2026-09-12] ingest | Codex Harness 架构

- **来源**：小林 coding《面试官得瑟：“你懂 Codex 的 Harness 架构吗？”》
- **清洗与整理**：去除作者开场、系列宣传和文末引流；保留 App Server、Session、Agent 主循环、上下文管理、StepContext、工具路由与执行、审批/沙箱、状态持久化、长期记忆、Skills/MCP/Hooks 和子 Agent 等技术内容
- **图片**：42 张微信图床图片经 PicGo CLI（GitHub Plus）上传至 `hangx969/upload-images-md`，正文已替换为 `.webp` 图床链接
- **归档**：《面试官得瑟：“你懂Codex的Harness架构吗？”，我笑了：“何止懂？我还看过源码”，他愣了.....》 → `AI/Codex/Codex-Harness架构-任务循环与扩展.md`
- **新建文件**：`KnowledgeBase/sources/codex-harness-architecture-summary.md` — 来源摘要页
- **更新页面**：`KnowledgeBase/entities/Codex.md`、`KnowledgeBase/maps/ai-workflow-map.md`、`KnowledgeBase/INDEX.md`、`AI/index.md`
- **边界说明**：文章是作者基于开源仓库的架构解读，摘要页标明了具体源码行为需以当前 Codex 版本和官方资料为准

## [2026-09-05] ingest | NVIDIA Device Plugin：K8s 识别 GPU

- **来源**：深栈运维，2026-08-28，微信公众号
- **清洗**：去除作者署名、联系方式、赞赏和目录导航；保留 GPU 调度链路、前置依赖、三种部署方式、验证命令、故障排查和运行时行为等技术内容，并规范 Bash 代码块与图片说明
- **归档**：《从零部署 NVIDIA Device Plugin：K8s 识别 GPU 的“第一块敲门砖”》 → `Docker-Kubernetes/k8s-ai-gpu/从零部署 NVIDIA Device Plugin：K8s 识别 GPU 的“第一块敲门砖”.md`
- **新建文件**：`KnowledgeBase/sources/k8s-nvidia-device-plugin-summary.md` — 来源摘要页
- **更新页面**：`KnowledgeBase/sources/k8s-misc-batch-summary.md`、`KnowledgeBase/entities/NVIDIA.md`、`KnowledgeBase/entities/Kubernetes.md`、`KnowledgeBase/maps/kubernetes-map.md`、`KnowledgeBase/INDEX.md`
- **核心知识**：Device Plugin 通过 NVML 发现 GPU 并注册 `nvidia.com/gpu`；Helm、静态 DaemonSet、GPU Operator 三种部署路径；驱动/Toolkit/containerd 前置检查；节点资源、插件日志和 CUDA 测试 Pod 三层验证；常见错误的分层排障顺序

---

## [2026-07-18] ingest | K8s Finalizer 与资源删除机制

- **来源**：WAKEUP技术，2026-07-12，微信公众号剪藏
- **清洗**：去除作者署名/公众号名片/个人主页链接行、文末"微信扫一扫赞赏作者"引导，技术内容完整保留
- **归档**：《K8s Finalizer：那个让资源"删不掉"的隐形守护者》 → `Docker-Kubernetes/k8s-basic-resources/k8s基础-Finalizer与资源删除.md`（Raw Source，人类确认后移入）
- **新建文件**：
  - `KnowledgeBase/concepts/Finalizer.md` — 新建概念页：定义、工作机制、内置/常见 Finalizer、五大"删不掉"场景、诊断修复方法、Operator 中的 Finalizer 编写原则
- **更新文件**：
  - `KnowledgeBase/sources/k8s-basic-resources-batch-summary.md` — 文档数 21→22，新增该文档摘要段落，补充交叉主题发现
  - `KnowledgeBase/concepts/CRD.md`、`KnowledgeBase/concepts/Operator模式.md` — 补充与 Finalizer 的关系交叉引用
  - `KnowledgeBase/maps/kubernetes-map.md` — 总文档数 152→153，核心概念新增 Finalizer，基础资源表格新增"生命周期"行
  - `KnowledgeBase/entities/Kubernetes.md` — 文章总数 152→153，基础资源 21→22 篇，覆盖描述补充 Finalizer
  - `KnowledgeBase/index.md` — 概念页表格新增 Finalizer 行，Docker-Kubernetes 文档数 152→153，K8s 基础资源来源行 21→22

## [2026-06-30] ingest | K8s 容器安全上下文完全指南（Security Context）

- **来源**：老郭a，2026-06-29，微信公众号
- **清洗**：去除作者署名/发布时间行、"先说点实在的"个人叙事段落中的非技术部分、评论区互动引导（"说来听听"）、微信赞赏/目录导航/个人观点声明页脚；还原全部 YAML 代码块格式（原文代码块压缩为单行，全部恢复为正确缩进的多行 YAML），修复错误的代码块语言标识符（makefile/cs/apache/sql → yaml/bash）
- **新建文件**：
  - `Docker-Kubernetes/k8s-security-auth/k8s容器安全上下文完全指南-SecurityContext.md` — 清洗后技术文章
- **更新页面**：
  - `sources/k8s-security-auth-batch-summary.md`：frontmatter 新增 source、文档数 7→8、正文新增 Security Context 小节（11 条关键知识点）
  - `entities/Kubernetes.md`：篇数 151→152、安全与认证 7→8 篇、新增 Security Context 核心要点
  - `maps/kubernetes-map.md`：总篇数 151→152、安全与认证 7→8 篇、列表新增 Security Context
  - `index.md`：安全认证批量摘要 7→8、Kubernetes 实体→152、领域导航→152
- **核心知识**：
  - Security Context 两级配置（Pod 级通用身份 + 容器级特殊权限），容器级覆盖 Pod 级
  - UID/GID 6 个核心字段（runAsUser/runAsGroup/runAsNonRoot/fsGroup/fsGroupChangePolicy/supplementalGroups）
  - fsGroupChangePolicy 生产用 `OnRootMismatch`（减少递归提升启动速度）
  - v1.35 GA：`supplementalGroupsPolicy: Strict` 消除镜像隐式组安全隐患（v1.31 Alpha → v1.33 Beta → v1.35 GA）
  - Capabilities 最佳实践：`drop: ALL` + 按需 add，配合 `allowPrivilegeEscalation: false` + `readOnlyRootFilesystem: true`
  - 特权模式三条铁律：默认禁止、99% 场景用 capabilities 替代、privileged 会让 seccomp 失效
  - allowPrivilegeEscalation 陷阱：hostPath/CSI 卷可能隐式授予 CAP_SYS_ADMIN 导致该字段不生效
  - sysctl 安全列表（v1.32，13 个参数含内核版本要求）
  - seccomp 三种 Profile，生产用 RuntimeDefault 即可
  - Pod 安全标准三级策略（Privileged/Baseline/Restricted），Baseline 允许 13 种 capabilities
  - 6 个常见故障排查场景

---

## [2026-06-30] ingest | shiji-kb：AI 史记知识库与可复用知识图谱构造方法论

- **来源**：01fish（数字人文研究），2026-04-09，微信公众号
- **清洗**：去除作者署名/发布时间行、微信群二维码、个人联系方式、文末署名、"非常期待"社群引流话术；保留全部技术内容（核心成果表、功能特性、26 个 Skill 方法论、使用指南、扩展路线）
- **新建文件**：
  - `AI/代码知识图谱/shiji-kb-AI史记知识库与知识图谱构造方法论.md` — 清洗后技术文章
  - `KnowledgeBase/sources/shiji-kb-knowledge-graph-summary.md` — 来源摘要页
- **更新页面**：
  - `index.md`：AI/工具分区新增条目
  - `AI/index.md`：新增代码知识图谱/目录条目（4→5 篇）
- **核心知识**：
  - shiji-kb 开源项目（baojie/shiji-kb）：一个人 + AI Agent 完成 57 万字古籍全量结构化
  - 18 类 NER 实体标注（人名/地名/官职/时间/朝代等），12,380 词条，99,214 次标注，平均每 6 字 1 个实体
  - 3,185 个事件（11 类）+ 7,652 条关系（9 种类型），98.7% 已标注公元纪年
  - 1,876 条跨章关系（互见/共人/共地/同期），连接分散在不同篇章的同一历史
  - **26 个 Skill 方法论（最有复用价值）**：9 大阶段（校勘→结构分析→实体构建→事件构建→关系构建→本体构建→逻辑推理→SKU 构造→应用构造）
  - 可复用管线：换书只需调参（实体类型/体裁分类/别名规则/年份体系），框架不变
  - 本体构建路径：词表→分类树→OWL/RDF

---

## [2026-05-22] ingest | 为什么 Claude Code 不用 RAG 检索代码，而是 grep

- **来源**：沉默王二，2026-05-20，微信公众号（引用 Boris Cherny 播客、亚马逊论文、Cursor 博客）
- **清洗**：去除作者署名/自我介绍、营销话术、简历模板章节、页脚导航；图片暂保留微信 CDN 链接（待后续 picgo 上传）
- **新建文件**：
  - `AI/ClaudeCode/Claude-Code为什么用grep不用RAG.md` — 清洗后技术文章
- **更新页面**：
  - `entities/Claude-Code.md`：sources +1、覆盖条目 +1
  - `index.md`：AI 领域 127→128
- **核心知识**：
  - Agentic Search 架构：Glob+Grep(ripgrep)+Read 三工具，isConcurrencySafe 可并行，不预建索引
  - RAG 检索代码五大问题：语义相似度对代码不管用（精确匹配 > 语义匹配）、索引同步成本高、安全隐私、搜索精度、依赖链路长
  - ripgrep 性能：SIMD 加速，几万文件仓库 200ms 全文搜索；head_limit 250 行防上下文溢出；"尽力返回"设计
  - Boris Cherny 原话：早期用过 Voyage Embedding RAG，后切换到 Agentic Search "outperformed everything, by a lot"
  - 亚马逊论文实锤（2025.12）：关键词搜索 Agent 达到 RAG 90%+ 性能，代码场景关键词比语义检索还好
  - Cursor 反面论证：混合检索（grep+向量）效果最好，反证 grep 是不可或缺基础能力
  - LLM 作为 Reranker：多轮迭代搜索能力 > RAG 一次检索模式

---

## [2026-05-22] ingest | K8s 集群成本优化方案——FinOps 实战

- **来源**：WAKEUP技术，2026-05-20，微信公众号
- **清洗**：去除作者署名行、公众号推广、页脚营销（赞赏/滑动导航）、列表冗余序号格式
- **新建文件**：
  - `Docker-Kubernetes/k8s-scaling/k8s成本优化方案-FinOps实战.md` — 清洗后技术文章
- **更新页面**：
  - `sources/k8s-scaling-storage-batch-summary.md`：frontmatter 新增 source、文档数 7→8（扩缩容 4→5）、正文新增 FinOps 小节（8 条关键知识点）
  - `entities/Kubernetes.md`：篇数→151、标记"FinOps 成本优化"知识空白已覆盖
  - `maps/kubernetes-map.md`：总篇数→151、扩缩容 4→5 篇
  - `index.md`：扩缩容与存储 7→8、Kubernetes→151、领域导航→151
- **核心知识**：K8s 成本优化五层体系（Right-Sizing/节点效率/调度策略/FinOps 监控/存储网络）；四大浪费黑洞（过度配置 40%/空闲资源 30%/僵尸资源 15%/碎片化 15%）；VPA+HPA 黄金组合；Karpenter vs Cluster Autoscaler 六维对比；Spot 实例砍 60-70%；CronJob 非生产环境定时开关；PriorityClass 资源抢占；OpenCost 成本分摊部署；5 条 Prometheus 成本告警规则；GP3/HDD 存储分级；5 大生产避坑；4 周落地路线图

---

## [2026-05-18] update | Planning with Files Skill 整合进扩展体系

- **来源**：展望未来科技01，2026-05-17，微信公众号
- **操作**：将 Planning with Files（21.4K Star）Skill 推荐整合到 `AI/ClaudeCode/Claude Code 扩展体系.md` 的"Skill/Plugin 推荐"章节中，而非独立文章
- **清洗**：去除营销话术（"封神""爆款神器"等），保留核心技术内容（3 个文件、安装命令、核心价值、支持平台）
- **更新文件**：`AI/ClaudeCode/Claude Code 扩展体系.md` — 在 wshobson/agents 之前新增 OthmanAdi/planning-with-files 章节
- **核心知识**：3 个 Markdown 文件（task_plan/findings/progress）实现文件化规划+外置记忆+错误自动记录，任务成功率 6.7%→96.7%，支持 17+ 平台

---

## [2026-05-17] ingest | code-review-graph 本地代码知识图谱

- **来源**：兔兔AGI（技术极简主义），2026-05-13，微信公众号
- **清洗**：去除作者署名行、SVG 占位图片（4 张）、推荐阅读链接、点赞/转发引导、页脚营销（赞赏/滑动导航）
- **新建文件**：
  - `AI/ClaudeCode/code-review-graph-本地代码知识图谱.md` — 清洗后技术文章
- **更新页面**：
  - `entities/Claude-Code.md`：sources +1、覆盖条目 +1
  - `maps/ai-workflow-map.md`：Claude Code 路径 7→8 步
  - `index.md`：AI 领域 126→127
- **核心知识**：code-review-graph（GitHub 开源）将代码库解析为本地知识图谱（Tree-sitter AST → SQLite 存储 → MCP Server），通过 blast-radius 分析计算变更影响范围的最小文件集合；2900 文件增量索引 2 秒；支持 7 个 AI 平台（Claude Code/Cursor/Codex/Gemini CLI/Kiro/Copilot）；6 个核心 MCP 工具 + 4 个进阶工具；Slash Commands（build-graph/review-delta/review-pr）；daemon 模式多仓库统一管理；Windows 排障指南

---

## [2026-05-17] ingest | OpenClaw K8s 智能运维实战

- **来源**：深栈运维，2026-05-13，微信公众号
- **清洗**：去除作者署名行、微信号推广、页脚营销（赞赏/滑动导航）
- **新建文件**：
  - `AI/OpenClaw/OpenClaw-K8s智能运维实战.md` — 清洗后技术文章
- **更新页面**：
  - `entities/OpenClaw.md`：sources 引用 +1、相关文章 +1、标记"K8s AIOps 集成"知识空白已覆盖
  - `maps/ai-workflow-map.md`：OpenClaw 路径 7→8 步
  - `index.md`：AI 领域 125→126
- **核心知识**：OpenClaw 作为 AI 与 K8s API 的双向桥梁（交互层→网关层→Skill 层→K8s 层四层架构）；三阶段渐进信任建立（只读巡检 4 周→诊断助理 4 周→低风险变更）；OPA 护栏策略完整 Rego 示例（黑名单操作/配额范围验证/副本上限/速率限制）；3 个月 156 次自主变更 99.4% 成功率零安全事故；60 秒诊断+修复完整实战案例（livenessProbe initialDelaySeconds 调整）

---

## [2026-05-17] restructure + ingest | K8s 日志管理三合一（日志基础 + 六种采集方案 + 审计日志）

- **操作**：将两篇现有文章合并，并摄入一篇新文章，三合一为一篇完整的日志管理综合文章
- **合并来源**：
  - `k8s日志管理.md`（kubelet 本地日志管理基础，73 行）
  - `k8s日志采集六种方案深度对比与选型指南.md`（六种采集方案+踩坑+架构推荐，466 行）
- **新增来源**：《K8s审计日志深度实践——从运维利器到合规基石》（WAKEUP技术，2026-05-17）
  - 清洗：去除作者署名/简介/个人主页、页脚营销（赞赏/滑动导航）、列表冗余序号
- **新建文件**：
  - `Docker-Kubernetes/k8s-monitoring-logging/k8s日志管理-采集方案与审计日志.md` — 三合一综合文章（922 行）
- **删除文件**：
  - `Docker-Kubernetes/k8s-monitoring-logging/k8s日志管理.md`（内容已合并）
  - `Docker-Kubernetes/k8s-monitoring-logging/k8s日志采集六种方案深度对比与选型指南.md`（内容已合并）
- **更新页面**：
  - `sources/k8s-monitoring-logging-batch-summary.md`：合并两个旧 source 引用为一个、文档数 23→22、日志管理小节替换为三合一摘要（14 条关键知识点）
  - `maps/kubernetes-map.md`：修复 2 处断链（日志管理/六种方案→合并文件）、监控日志 23→22 篇、总篇数 151→150
  - `entities/Kubernetes.md`：篇数 151→150
  - `concepts/日志系统.md`、`concepts/Observability.md`：修复断链（日志管理→合并文件）
  - `index.md`：监控日志 23→22、Kubernetes 151→150、领域导航 151→150
- **合并后文章结构（9 章）**：
  - 一、K8s 日志基础机制（kubelet 默认策略、日志路径、生命周期、logrotate）
  - 二、日志的三种原生形式（stdout/文件/系统日志）
  - 三、六种采集方案深度对比（DaemonSet/Sidecar/直推/ServiceMesh/OTel/云托管，含完整 YAML）
  - 四、六种方案对比总览表
  - 五、生产环境五大踩坑
  - 六、选型决策树 + 三种推荐架构（PLG/EFK+Kafka/OTel）
  - 七、K8s 审计日志（策略配置、API Server 启用、采集架构、4 个排查场景）
  - 八、审计日志合规与安全（等保 2.0/SOC2、性能优化、OPA 联动）
  - 九、总结（合并推荐表 + 5 条黄金法则）

---

## [2026-05-17] ingest | html-anything — AI 生成 HTML 全场景工具

- **来源**：开源日记，2026-05-17，微信公众号
- **清洗**：去除作者署名行、SVG 占位图片（12 张）、点赞/在看/转发/星标引导、页脚滑动导航
- **新建文件**：
  - `AI/AI-视觉/html-anything-AI生成HTML全场景工具.md` — 清洗后技术文章
- **更新页面**：
  - `index.md`：AI 领域 124→125
- **核心知识**：html-anything（GitHub 2500+ Star）不自带模型，调用本地已有 AI CLI（Claude Code/Cursor/Gemini CLI）；75 套模板覆盖 9 种场景（Web 原型/演示文稿/视频/社交卡片/办公文档等）；20 套演示文稿模板（瑞士国际主义/杂志墨水/小红书柔和/赛博霓虹等）；10 个 Hyperframes 视频帧脚本可渲染 MP4；一键导出微信公众号（CSS 内联）/X/微博/小红书（2× PNG）/知乎（LaTeX→图片）；SSE 流式渲染 + 沙箱 iframe 安全隔离；新增与同目录 ppt-master/html-ppt-skill/AI-Animation-Skill 横向对比表

---

## [2026-05-17] ingest | Confluence 内部 Wiki RAG 知识库增强检索系统

- **来源**：认真做自己（老甄说运维），2026-05-13，微信公众号（本地 HTML 文件摄入）
- **清洗**：去除作者署名行、公众号关注/星标引导、SVG 占位图、谷雨装饰、上一篇/下一篇链接、赞赏/留言 UI 元素；**还原所有被压缩为单行的格式**——2 个 ASCII 架构图、5 个表格、7 个 JSON 代码块、1 个 Python 配置文件、3 个 XML 宏示例、5 个处理流程图、1 个目录树结构，全部从单行恢复为正确缩进的多行格式
- **新建文件**：
  - `AI/Confluence-Wiki-RAG知识库增强检索系统.md` — 清洗后技术文章（639 行）
- **更新页面**：
  - `index.md`：RAG-Agent 分区新增条目、AI 领域 123→124
- **核心知识**：
  - 架构全景：Confluence REST API 采集 → BeautifulSoup 清洗 Storage Format → bge-m3 向量化 → Qdrant 存储 → LiteLLM 网关 → FastAPI 后端 → Vue 前端
  - 6 种数据来源统一处理：正文（page）、评论（comment）、附件（attachment，支持 PDF/docx/xlsx/pptx）、图片（image，多模态模型解析）、draw.io 架构图（drawio，mxCell 节点提取 + 图像解析）、空页面元信息
  - Confluence Storage Format 宏处理：code 宏提取 CDATA → Markdown 代码块、drawio 宏保留占位、info/note/warning 保留内容
  - Chunk 切分策略：优先 Markdown 标题切分、代码块内不按 # 切分（区分注释和标题）、chunk overlap 保留上下文
  - Qdrant 入库：stable_uuid(chunk_id) 保证幂等覆盖、全量入库 vs 单页面入库
  - RAG 服务：Prompt 规则（可溯源不编造、正文优先评论、冲突说明冲突）、来源返回含 preview_url
  - 日常运维一条命令：`python sync_pages_batch.py data/page_ids.txt --mode auto --expand-children`

---

## [2026-05-17] ingest | Claude Code 实现 CI/CD 自动化发布流程

- **来源**：认真做自己（老甄说运维），2026-05-16，微信公众号
- **清洗**：去除作者署名行、公众号关注/星标引导、SVG 占位图片（7 张）、谷雨节气装饰、上一篇链接、微信群/博客推广、赞赏/滑动导航；修复 YAML 代码块格式（原文代码块内无换行，全部还原为正确缩进的多行 YAML）
- **新建文件**：
  - `Docker-Kubernetes/k8s-CICD/Claude-Code实现CICD自动化发布流程.md` — 清洗后技术文章
- **更新页面**：
  - `sources/k8s-CICD-batch-summary.md`：frontmatter 新增 source、文档数 19→20、正文新增 Claude Code CI/CD 小节（7 条关键知识点）
  - `entities/Kubernetes.md`：篇数→151
  - `maps/kubernetes-map.md`：总篇数→151、CI/CD 其他 2→3 篇
  - `index.md`：CI/CD 批量摘要 19→20、Kubernetes→151、领域导航→151
- **核心知识**：GitLab CI 5 阶段 Pipeline（review→build→deploy→release→notify）、Kaniko 无特权构建 + Harbor 推送、kubectl 原生部署 + Istio VirtualService 暴露、Claude MR Review（diff→prompt→LiteLLM→MR 评论）、部署失败 on_failure 自动 RCA（pod describe/events/logs→AI 根因分析）、Release Notes 自动生成（git log→AI 分类→GitLab Releases API）、.claude-call 模板复用、敏感信息全走 GitLab Variables（Masked+Protected）

---

## [2026-05-17] ingest | K8s API Server 深度剖析：请求链路、认证授权与生产调优

- **来源**：WAKEUP技术，2026-05-15，微信公众号
- **清洗**：去除作者署名行、公众号推广、页脚营销（赞赏/滑动导航）、列表冗余序号格式
- **新建文件**：
  - `Docker-Kubernetes/k8s-basic-resources/k8s-APIServer深度剖析-请求链路-认证授权-生产调优.md` — 清洗后技术文章
- **更新页面**：
  - `sources/k8s-basic-resources-batch-summary.md`：frontmatter 新增 source、文档数 20→21、正文新增 API Server 深度剖析小节（11 条关键知识点）
  - `entities/Kubernetes.md`：篇数→150、基础资源→21 篇
  - `maps/kubernetes-map.md`：总篇数→150、基础资源→21 篇、安全行新增 API Server 深度剖析
  - `index.md`：基础资源批量摘要 20→21、Kubernetes 实体→150、领域导航→150
- **核心知识**：请求 7 步链路（认证→授权→变更准入→校验→验证准入→etcd→Watch）、4 种认证插件（X.509/SA Token/OIDC/Webhook）、RBAC 核心逻辑与 `*` 通配符陷阱、准入 Webhook `failurePolicy: Fail` 致命风险、Watch/Informer/SharedInformer 三组件、CRD 与聚合 API Server、生产调优参数表（50→3000+ 节点资源规划）、审计日志完整 Policy、3 条 Prometheus 告警规则、3 个故障排查手册（API Server 无响应/Webhook 死锁/Watch 泄漏 OOM）

---

## [2026-05-15] ingest | CLAUDE.md 最佳实践两篇（21 条指令 + 12 条规则模板）

- **来源**：
  - Mayank Agarwal（@TheAIWorld22），X 长帖，290 万阅读，2026-05-09
  - Mnilax（@Mnilax），X 长帖，30 个代码库实测，2026-05-13
  - 两篇均由公众号 Cf2019 翻译整理
- **清洗**：去除公众号署名行、赞赏/滑动导航、目录导航
- **新建文件**：
  - `AI/ClaudeCode/CLAUDE.md最佳实践-21条指令清单.md` — Mayank 21 条指令（沟通/行为/上下文/记忆/安全五维度）
  - `AI/ClaudeCode/CLAUDE.md最佳实践-12条规则模板.md` — Mnilax 12 条规则（Karpathy 4 条 + 8 条新规则，含翻车现场和实测数据）
- **更新页面**：
  - `entities/Claude-Code.md`：记忆层章节新增 CLAUDE.md 最佳实践摘要（200 行天花板/Karpathy 4 条/Mnilax 12 条/Mayank 21 条）、sources 引用 +2、覆盖条目 +2
  - `maps/ai-workflow-map.md`：Claude Code 路径 5→7 步
  - `index.md`：AI 领域 121→123
- **核心知识**：
  - **Mayank 独有**：MEMORY.md/ERRORS.md 记忆连续性系统、非开发者场景覆盖（写作者/营销人/研究者）、指令 9-11 个人上下文注入
  - **Mnilax 独有**：200 行遵循率天花板实测、Token 预算（4000/任务 30000/会话）、暴露冲突不折中、先读后写、测试验证意图、长任务检查点、约定胜于新奇、显式失败、6 条"试过但放弃的"反面经验
  - **共同**：Karpathy 4 条基础规则、外科手术式修改、不可逆操作确认

---

## [2026-05-15] ingest | OpenTelemetry 实战：统一 Traces/Metrics/Logs

- **来源**：WAKEUP技术，2026-05-13，微信公众号
- **清洗**：去除作者署名行、下期预告、关注引导、页脚营销（滑动导航）、列表冗余序号格式
- **新建文件**：
  - `Docker-Kubernetes/k8s-monitoring-logging/OpenTelemetry实战-统一Traces-Metrics-Logs.md` — 清洗后技术文章
- **更新页面**：
  - `sources/k8s-monitoring-logging-batch-summary.md`：frontmatter 新增 source、文档数 22→23、正文新增 OTel 小节
  - `maps/kubernetes-map.md`：总篇数 148→149、监控日志 22→23 篇、列表新增 OTel
  - `index.md`：监控日志批量摘要 22→23、Kubernetes 实体 148→149、领域导航 148→149
- **核心知识**：OTel Collector 三段式管道（Receivers→Processors→Exporters）、Operator 零代码自动注入、尾部采样四策略、OTel vs Datadog 选型（$3000-8000+/月 vs 开源自主）、LGTM 栈（Loki+Grafana+Tempo+Mimir）、四阶段迁移策略、生产要点（Collector 资源规划/Cardinality 防爆/背压处理/多租户隔离/监控你的监控）

---

## [2026-05-15] ingest | VPA 垂直扩缩容深入：四种模式、推荐算法与 HPA 共存

- **来源**：WAKEUP技术，2026-05-15，微信公众号
- **清洗**：去除作者署名/简介/个人主页、页脚营销（赞赏/滑动导航）、列表冗余序号格式
- **操作方式**：清洗后内容追加到已有文档 `Docker-Kubernetes/k8s-scaling/helm部署vpa.md` 末尾，未新增独立文件
- **新增内容**：
  - 四种 updateMode 对比表（Off/Initial/Auto/Recreate）及生产建议
  - 推荐值算法原理（指数衰减直方图、CPU P95、Memory 高水位、8 天窗口）
  - VPA + HPA 共存三种方案（分离控制维度配置示例）
  - 驱逐风险缓解（PDB 配合、Initial 模式推荐）
  - Prometheus 监控指标 + Grafana Dashboard ID 14588
- **更新页面**：
  - `sources/k8s-scaling-storage-batch-summary.md`：VPA 小节补充四种模式/推荐算法/HPA 共存/驱逐风险要点

---

## [2026-05-13] ingest | K8s 日志采集六种方案深度对比与选型指南

- **来源**：WAKEUP技术，2026-05-11，微信公众号
- **清洗**：去除作者署名行、页脚营销（赞赏/滑动导航）、评论区互动引导、作者简介
- **新建文件**：
  - `Docker-Kubernetes/k8s-monitoring-logging/k8s日志采集六种方案深度对比与选型指南.md` — 清洗后技术文章
- **更新页面**：
  - `sources/k8s-monitoring-logging-batch-summary.md`：frontmatter 新增 source、文档数 21→22
  - `maps/kubernetes-map.md`：总篇数 147→148、监控日志 20→22 篇、列表新增日志选型
  - `index.md`：监控日志批量摘要 21→22、Kubernetes 实体 147→148、领域导航 147→148
- **核心知识**：六种方案（DaemonSet/Sidecar/直推/ServiceMesh/OpenTelemetry/云托管）对比、Fluent Bit 完整配置、5 个生产踩坑、选型决策树、PLG vs EFK+Kafka 架构推荐

---

## [2026-05-13] ingest | RAG PDF 解析难点与主流方案

- **来源**：小橙子（AI Engineer编程），2026-05-09，微信公众号
- **清洗**：去除作者署名行、页脚导航（"继续滑动看下一个"）、列表冗余序号格式
- **新建文件**：
  - `AI/RAG-PDF解析难点与主流方案.md` — 清洗后技术文章
  - `KnowledgeBase/sources/rag-pdf-parsing-summary.md` — 来源摘要页
- **更新页面**：
  - `index.md`：RAG-Agent 分区新增 RAG PDF 解析条目、AI 领域 120→121
- **核心知识**：PDF 格式三种对比（DOCX/HTML/PDF）、三大解析路线（文本提取/OCR/VLM）、Docling/MinerU/Marker-PDF AI 增强框架、7 个常见生产问题处理方案

---

## [2026-05-13] ingest | Hermes Curator — Skill 膨胀治理

- **来源**：AI技术立文，2026-05-07，微信公众号
- **清洗**：去除作者署名行、SVG 占位图片（2 张）、页脚营销（赞赏/滑动导航）
- **新建文件**：
  - `AI/Hermes-agent/Hermes-Curator-Skill膨胀治理.md` — 清洗后技术文章
- **更新页面**：
  - `sources/hermes-agent-batch-summary.md`：frontmatter 新增 source、文档数 3→4、正文新增 Curator 小节
  - `entities/Hermes-Agent.md`：新增 Curator 核心功能条目、sources 引用、覆盖条目；移除"Skill Factory 质量评估"知识空白（已覆盖）
  - `maps/ai-workflow-map.md`：Hermes 路径 3→4 步、来源摘要 3→4 篇
  - `index.md`：Hermes-agent 批量摘要 3→4 篇
- **核心知识**：Curator 四步工作流（监测/降级/复盘/锁定）、Skill 膨胀数学（365→36 条/年）、Skill vs 记忆区别、Agent 四种记忆类型（工作/语义/情景/程序性）

---

## [2026-05-13] ingest | K8s CGroup v2 深度解析：资源隔离原理、迁移实战与避坑指南

- **来源**：WAKEUP技术，2026-05-12，微信公众号
- **清洗**：去除作者署名行、页脚营销（关注/赞赏/滑动导航）、列表序号冗余格式
- **新建文件**：
  - `Docker-Kubernetes/k8s-installation-management/k8s-cgroup-v2深度解析-迁移实战与避坑指南.md` — 清洗后技术文章
  - `KnowledgeBase/sources/k8s-cgroup-v2-summary.md` — 来源摘要页
- **更新页面**：
  - `sources/k8s-installation-management-batch-summary.md`：frontmatter 新增 source、文档数 16→17、正文新增 cgroup v2 小节
  - `entities/Kubernetes.md`：新增 cgroup v2 资源隔离章节、sources 引用、篇数 145→147
  - `entities/containerd.md`：新增核心功能章节（含 cgroup v2 支持说明）、覆盖条目
  - `maps/kubernetes-map.md`：总篇数 146→147、安装运维 16→17 篇、列表新增 cgroup v2
  - `index.md`：安装管理批量摘要 16→17、Kubernetes 实体 146→147、领域导航 146→147
- **核心知识**：cgroup v2 统一层次树、CPU Burst（P99 降 30-50%）、memory.high 双层限制、MemoryQoS（v1.27 Beta）、5 个生产踩坑案例、3 条 Prometheus 告警规则

---

## [2026-05-13] ingest | AI 行业动态：AI 时代 Git 版本管理最佳实践

- **来源**：TRAE 技术专家 小夏，2026-04-28
- **清洗**：去除公众号引流、页脚导航；修复全部代码块格式（错误的语言标识符 xml/sql/kotlin/perl/css/makefile/apache/python/nginx/cs/php → text/bash/markdown/json；恢复代码块内换行）
- **新建文件**：
  - `AI/行业动态/AI时代的Git版本管理最佳实践.md` — 清洗后技术文章
  - `KnowledgeBase/sources/ai-git-best-practices-summary.md` — 来源摘要页
- **更新页面**：
  - `maps/ai-workflow-map.md`：行业动态 2→3 篇
  - `index.md`：行业动态表格新增一行
  - `AI/index.md`：行业动态/ 2→3 篇

---

## [2026-05-13] ingest | AI 行业动态：HTML 取代 Markdown

- **来源**：量子位 QbitAI（Jay），2026-05-12，Anthropic 工程师 Thariq 长文 + Karpathy 回应
- **清洗**：去除公众号引流、广告、AIGC 峰会推广、评论区引导、页脚导航
- **新建文件**：
  - `AI/行业动态/Anthropic工程师力推HTML取代Markdown-Karpathy附议.md` — 清洗后技术文章
  - `KnowledgeBase/sources/html-vs-markdown-summary.md` — 来源摘要页
- **更新页面**：
  - `maps/ai-workflow-map.md`：行业动态 1→2 篇，推荐阅读顺序新增条目
  - `index.md`：行业动态表格新增一行
  - `AI/index.md`：行业动态/ 1→2 篇

---

## [2026-05-11] restructure | Hermes Agent 两篇合并 + KB 同步

- **操作**：将 `Hermes Agent 资源合集` 与 `Hermes满配指南-五大配置模块` 合并为一篇
- **新建文件**：
  - `AI/Hermes-agent/Hermes-Agent-满配指南与生态资源.md` — 合并后文章（八大章节：配置总览 + 五大模块 + 高阶玩法 + 工具增强 + 生态资源）
- **删除文件**：
  - `AI/Hermes-agent/Hermes Agent 资源合集.md`
  - `AI/Hermes-agent/Hermes满配指南-五大配置模块.md`
  - `KnowledgeBase/sources/hermes-config-summary.md`（孤儿摘要页，内容已吸收入 batch summary）
- **更新页面**：
  - `sources/hermes-agent-batch-summary.md`：资源合集条目替换为合并文章，新增五大配置模块要点
  - `entities/Hermes-Agent.md`：sources 4→3、覆盖条目 4→3
  - `maps/ai-workflow-map.md`：Hermes 路径 4 条→3 条
  - `inventory/repository-inventory.md`：Hermes-agent/ 4 篇→3 篇
  - `INDEX.md`：删除 hermes-config-summary 行，更新 batch summary 描述
  - `AI/index.md`：Hermes-agent/ 4→3 篇
  - `AI/HarnessKit.md`：修复因删除产生的断链（资源合集→满配指南与生态资源）

---

## [2026-05-09] ingest | Claude Code+Obsidian 知识管家实践

- **来源**：微信公众号"强西"，2026-05-06 发布
- **清洗**：去除作者署名行、3 个 SVG 占位图片、页脚营销（微信扫一扫赞赏、继续滑动看下一个），保留全部技术内容
- **新建文件**：
  - `AI/Obsidian/obsidian-claude-code-AI知识管家.md` — 清洗后的原始来源文档
  - `KnowledgeBase/sources/obsidian-claude-code-AI知识管家-summary.md` — 来源摘要页
- **更新页面**：
  - `entities/Obsidian.md`：frontmatter 新增 source、覆盖条目新增知识管家文章
  - `entities/Claude-Code.md`：frontmatter 新增 source、覆盖条目新增知识管家文章
  - `maps/ai-workflow-map.md`：总篇数 19→20、Obsidian 节 3→4 篇、新增推荐阅读条目和来源摘要引用
  - `INDEX.md`：新增来源摘要条目、AI 领域篇数 119→120
  - `inventory/repository-inventory.md`：总文档数 298→299、AI 27→28 篇、Obsidian/ 3→4 篇
- **核心知识**：Markdown 是 LLM 母语（Token 效率优 30-50%）、三大 $1B+ 项目殊途同归于 .md（Manus/OpenClaw/Claude Code）、30 分钟四步上手、Karpathy Wiki 模式、自动 backlinks 进阶方向

---

## [2026-05-08] ingest | Helm 部署 RabbitMQ HA

- **来源**：微信公众号"爱踢人生sre"
- **清洗**：去除公众号作者名片、SVG 占位图片、页脚导航（"继续滑动看下一个"）、"微信扫一扫赞赏作者"，保留全部技术内容
- **新建文件**：
  - `Docker-Kubernetes/k8s-db-middleware/helm部署rabbitmq-ha.md` — 清洗后的原始来源文档
  - `KnowledgeBase/sources/rabbitmq-ha-summary.md` — 来源摘要页
- **更新页面**：
  - `sources/k8s-db-middleware-UI-batch-summary.md`：frontmatter 新增 source、文档数 18→19（中间件 10→11）、正文新增 RabbitMQ HA 小节
  - `maps/kubernetes-map.md`：总篇数 145→146、中间件 10→11、列表新增 RabbitMQ HA
  - `INDEX.md`：K8s 中间件批量摘要 18→19、Kubernetes 实体 145→146、领域导航 145→146
  - `inventory/repository-inventory.md`：总文档数 297→298、Docker-Kubernetes 145→146、k8s-db-middleware/ 10→11
- **备注**：aliyun/rabbitmq-ha Chart 版本较旧（1.0.0，RabbitMQ 3.7），需手动修复 API 版本兼容性，生产环境建议评估 bitnami/rabbitmq

---

## [2026-05-07] ingest | Kyverno 1.18 新特性 + Kyverno 实体页

- **来源**：CNCF 官方博客，微信公众号转载
- **清洗**：去除微信公众号图片横幅、KubeCon 广告区块、CNCF 基金会介绍模板、页脚导航（"继续滑动看下一个"），保留全部技术内容与参考链接
- **操作方式**：清洗后的 1.18 新特性内容追加到已有文档 `helm部署kyverno和policy-reporter.md` 末尾，未新增独立文件
- **新建文件**：
  - `KnowledgeBase/sources/kyverno-1.18-summary.md` — 来源摘要页
  - `KnowledgeBase/entities/Kyverno.md` — Kyverno 实体页（新建，CNCF 毕业项目）
- **更新页面**：
  - `Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter.md`：追加 Kyverno 1.18 全部新特性内容
  - `sources/k8s-security-auth-batch-summary.md`：Kyverno 小节新增 1.18 要点
  - `maps/kubernetes-map.md`：安全认证条目标注"含 1.18 新特性"
  - `INDEX.md`：实体表新增 Kyverno，安全认证条目标注含 1.18
  - `inventory/repository-inventory.md`：无文件数变更

---

## [2026-05-06] ingest | Boris Cherny 红杉大会七个判断 + AI 行业动态目录

- **来源**：微信公众号文章（原始视频 https://www.youtube.com/watch?v=SlGRN8jh2RI）
- **清洗**：去除作者署名行、#01 章节标记、AI Maker Summit 广告（419元报名）、SVG 占位图、微信页脚导航，保留全部 7 个行业判断及分析
- **新建目录**：`AI/行业动态/` — AI 行业趋势与洞察专题目录
- **新建文件**：
  - `AI/行业动态/Claude-Code创始人红杉大会七个判断.md` — 清洗后的文章
  - `KnowledgeBase/sources/boris-cherny-sequoia-summary.md` — 来源摘要页
- **更新页面**：
  - `entities/Claude-Code.md`：新增 sources 引用 + 覆盖条目（行业判断 + 摘要）
  - `entities/MCP.md`：新增 sources 引用 + 覆盖条目 + 新增"行业观点"章节（Boris Cherny 的 MCP 定位论述）
  - `maps/ai-workflow-map.md`：新增"AI 行业动态"阅读路径 + 文档表（1 篇）+ 总数 18→19
  - `INDEX.md`：新增"AI/行业动态"来源摘要分区 + AI 领域篇数 118→119
  - `inventory/repository-inventory.md`：新增行业动态/ 子节（1 篇）+ AI 总数 26→27

---

## [2026-05-05] ingest | Harness 实战文章摄入

- **来源**：《Harness 实战：从零搭建最小可用的 Harness 系统》（微信公众号剪藏）
- **清洗**：去除作者署名行、微信赞赏/滑动导航、SVG 占位图，保留全部技术内容（四层架构、三个拦截器完整代码、编排流程、踩坑经验、组件清单表）
- **新建文件**：
  - `AI/ClaudeCode/Claude-Code-Harness实战-最小可用系统.md` — 清洗后的技术文章
  - `KnowledgeBase/sources/harness-system-summary.md` — 来源摘要页
- **更新页面**：
  - `entities/Claude-Code.md`：新增 sources 引用 + 覆盖条目 + 标记 Hooks 知识空白已填补
  - `maps/ai-workflow-map.md`：Claude Code 路径新增第 5 步 + 文档表 4→5 篇 + 总数 17→18
  - `maps/tool-map.md`：Claude Code 相关文档 6→7 篇
  - `INDEX.md`：新增来源摘要条目
  - `inventory/repository-inventory.md`：ClaudeCode/ 4→5 篇

---

## [2026-05-05] ingest | Skill Craft 质检工具文章摄入

- **来源**：《我做了一个 Claude Skill 质检工具：专门解决 Claude Skill 的不触发、乱触发、越用越跑偏》（微信公众号剪藏）
- **清洗**：去除营销文案（01 节引入语、10 节目标受众推荐、11 节关注引导、页脚），保留技术内容（7 类失效模式、三层评估体系、四模式详解）
- **新建文件**：
  - `AI/ClaudeCode/Claude-Skill质检工具-SkillCraft.md` — 清洗后的技术文章
  - `KnowledgeBase/sources/skill-craft-summary.md` — 来源摘要页
- **更新页面**：
  - `entities/Claude-Code.md`：新增 sources 引用 + 覆盖条目
  - `maps/ai-workflow-map.md`：Claude Code 路径新增第 4 步 + 文档表 3→4 篇
  - `maps/tool-map.md`：Claude Code 相关文档 5→6 篇
  - `INDEX.md`：新增来源摘要条目
  - `inventory/repository-inventory.md`：ClaudeCode/ 3→4 篇

---

## [2026-05-05] update | CLAUDE.md 新增原始文章清洗准则

- 在操作流程 Ingest 节新增 Step 0："清洗原始文章"——去除营销内容，仅保留技术内容
- 明确列出需要去除的内容类型：引流话术、关注/转发引导、评论区互动、广告/赞助、页脚导航

---

## [2026-05-05] ingest | Hermes 满配指南文章摄入

- **来源**：《装完 Hermes 一定要配置这五套系统，秒变满配版，能力提升数倍不止》（微信公众号剪藏）
- **清洗**：去除营销文案，保留五大配置模块技术内容及安装命令
- **新建文件**：
  - `AI/Hermes-agent/Hermes满配指南-五大配置模块.md` — 清洗后的技术文章
  - `KnowledgeBase/sources/hermes-config-summary.md` — 来源摘要页
  - `KnowledgeBase/entities/Hermes-Agent.md` — 新建实体页（4 篇文档达到 ≥3 阈值）
- **更新页面**：
  - `sources/hermes-agent-batch-summary.md`：更新实体引用（去掉"无独立实体页"备注）
  - `maps/ai-workflow-map.md`：新增 Hermes Agent 路径（4 篇）+ 相关工具列表
  - `INDEX.md`：新增实体条目 + 来源摘要条目
  - `inventory/repository-inventory.md`：新增 Hermes-agent/ 子节（4 篇）

---

## [2026-05-05] ingest | Obsidian 可视化 Skills 文章摄入

- **来源**：《这个 Skills 让 Obsidian 画图门槛降到了零》（微信公众号剪藏）
- **清洗**：去除营销内容（作者介绍、关注提示、往期推荐、赞赏等），保留技术内容
- **新建文件**：
  - `AI/Obsidian/Obsidian可视化Skills-Excalidraw-Mermaid-Canvas.md` — 清洗后的技术文章
  - `KnowledgeBase/sources/obsidian-visual-skills-summary.md` — 来源摘要页
- **更新页面**：
  - `entities/Obsidian.md`：新增覆盖条目
  - `maps/ai-workflow-map.md`：Obsidian 区块 2→3 篇
  - `maps/tool-map.md`：Obsidian 区块新增文档
  - `INDEX.md`：新增来源摘要条目
  - `inventory/repository-inventory.md`：Obsidian/ 篇数 2→3

---

## [2026-05-05] restructure | Obsidian 知识库文章从 ClaudeCode 目录迁移到独立目录

- **操作**：将 `AI/ClaudeCode/` 中 2 篇 Obsidian 知识库主题文章迁移到新建的 `AI/Obsidian/` 目录
  - `obsidian-claude-搭建个人知识库.md` → `AI/Obsidian/`
  - `karpathy-llm-wiki-改造计划.md` → `AI/Obsidian/`
- **引用修复**：更新 9 个 KB 文件中的 wikilink 路径（entities/Claude-Code、entities/Obsidian、entities/MCP、maps/tool-map、maps/ai-workflow-map、maps/claude-code-openclaw-map、INDEX、inventory/repository-inventory、sources/obsidian-claude-搭建个人知识库-summary）
- **结构调整**：
  - `ai-workflow-map.md`：Claude Code 篇数 5→3，新增 Obsidian 知识库区块（2 篇）
  - `claude-code-openclaw-map.md`：更新目录树和文档计数
  - `repository-inventory.md`：ClaudeCode 篇数 5→3，新增 Obsidian/ 子节（2 篇）
- **目的**：使目录结构更清晰——ClaudeCode/ 保留纯 Claude Code 文章，Obsidian/ 独立存放知识库主题文章

---

## [2026-05-04] ingest | Hermes Agent 架构解析文章

- **来源**：《Hermes Agent全解析：与OpenClaw对比及飞书接入指南 - 飞书官网》
- **操作**：
  - 清理格式后放置到 `AI/Hermes-agent/Hermes Agent全解析-与OpenClaw对比及飞书接入指南.md`
  - 更新 `sources/hermes-agent-batch-summary.md`：文档数 2→3，新增第三篇摘要（五层架构、记忆系统、子代理委托、OpenClaw 六维对比、飞书接入）
  - 更新 `entities/OpenClaw.md`：新增"与 Hermes Agent 的对比"章节
  - 更新 `index.md`：Hermes-agent 覆盖文档数 2→3
- **新增知识点**：Hermes 五层架构、冻结快照记忆、子代理深度限制 2 / 并行 max 3、Hermes vs OpenClaw 六维对比

---

## [2026-05-04] update | 消除孤儿来源页面

- **操作**：为 15 个无入站链接的 sources/ 页面添加来自 entities/concepts/maps 的引用
- **修改文件**：
  - `entities/Claude-Code.md` — +3 refs（基础指南、扩展体系、知识库搭建摘要）
  - `entities/OpenClaw.md` — +2 refs（OpenClaw 批量摘要、多智能体导出摘要）
  - `entities/Terraform.md` — +1 ref（容器管理摘要）
  - `entities/Helm.md` — +1 ref（Terraform Helm Provider）
  - `entities/Slurm.md` — +1 ref（HPC-Cloud-GPU 摘要）
  - `concepts/Python运维开发.md` — +1 ref（Python 批量摘要）
  - `entities/Kafka.md`、`entities/Redis.md`、`entities/MySQL.md` — 各 +1 ref（杂项领域摘要）
  - `maps/linux-ops-map.md` — +2 refs（Linux-Shell、HPC-Cloud-GPU 摘要）
  - `maps/ai-workflow-map.md` — +4 refs（CloudOps-Agent、RAG-Agent、Hermes-agent、k8s-report-skills 摘要）
  - `maps/domain-map.md` — +3 refs（Go、杂项领域、IaC 摘要）
- **影响**：孤儿来源页面从 15 个减少到 0 个

---

## [2026-05-04] update | 修复链接格式问题

- **操作**：修复 Docker Compose 命名不一致（空格 → 连字符）
- **修改文件**：
  - `entities/Docker.md` — 2 处 `Docker Compose` → `Docker-Compose`
  - `sources/docker-batch-summary.md` — 1 处同上
- **说明**：`\|` 在表格内的 wikilink 是正确的 Markdown 转义，非错误，无需修复

---

## [2026-05-04] create | 补建高频缺失概念页面

- **操作**：创建 7 个被多页面引用但不存在的概念页面
- **新增概念页**：
  - [[KnowledgeBase/concepts/StorageClass]] — K8s 动态存储分配（4 处引用）
  - [[KnowledgeBase/concepts/ServiceMesh]] — 服务网格别名页，指向 [[KnowledgeBase/concepts/服务网格]]（3 处引用）
  - [[KnowledgeBase/concepts/高可用架构]] — HA 冗余与故障切换（3 处引用）
  - [[KnowledgeBase/concepts/CRD]] — K8s 自定义资源定义（2 处引用）
  - [[KnowledgeBase/concepts/Operator模式]] — CRD + Controller 模式（2 处引用）
  - [[KnowledgeBase/concepts/RBAC]] — 基于角色的访问控制（2 处引用）
  - [[KnowledgeBase/concepts/联邦集群]] — 多集群联邦管理（2 处引用）
- **更新页面**：[[KnowledgeBase/index|index.md]] — 概念页表格新增 7 行
- **影响**：消除 16 处断链引用

---

## [2026-05-04] ingest | AI 新项目 + IaC Terraform 容器管理

- **操作**：批量摄入 4 个新来源项目到 wiki 编译层
- **新增来源摘要页**：
  - [[KnowledgeBase/sources/cloudops-agent-batch-summary|CloudOps-Agent 批量摘要]] — 57 篇，AI/CloudOps-Agent-项目，三语言智能 OnCall Agent
  - [[KnowledgeBase/sources/rag-agent-batch-summary|RAG-Agent 批量摘要]] — 33 篇，AI/RAG-Agent，Spring Boot + ES 混合检索企业 RAG 系统
  - [[KnowledgeBase/sources/hermes-agent-batch-summary|Hermes-agent 批量摘要]] — 2 篇，AI/Hermes-agent，Hermes Agent 安装与资源合集
  - [[KnowledgeBase/sources/iac-terraform-container-summary|Terraform 容器管理摘要]] — 1 篇，IaC/terraform-container-management
- **更新页面**：
  - [[KnowledgeBase/index|index.md]] — 新增 4 个来源分组，AI 领域篇数 26→118，IaC 领域 2→3
- **影响范围**：AI 领域覆盖率从 12% 提升至 ~90%，IaC 领域新增 Terraform 容器管理专题

---

## [2026-04-23] ingest | External Secrets Operator 进阶

- **来源**：《K8S实战教程 如何使用 External Secrets Operator 管理 Kubernetes密钥》（微信公众号文章）
- **操作**：整合到现有文档 [[Docker-Kubernetes/k8s-security-auth/helm部署external-secrets]]
- **新增内容**：
  - "为什么需要 ESO" 对比表 + 工作原理架构说明 + 核心 CRD 对照表
  - AWS Secrets Manager 集成（第三个 Provider，补充 Azure KV 和 Vault）
  - 进阶用法：精细字段映射、模板渲染、creationPolicy 策略、GitOps 集成
  - 监控与可观测性（Prometheus Metrics、告警）
  - 五方案横向对比（原生 Secret / Sealed Secrets / SOPS / CSI / ESO）
  - 生产落地六步路线
- **决策**：已有 external-secrets 部署文章覆盖 Azure KV + Vault，新文章补充架构原理和进阶特性，合并避免内容分裂

---

## [2026-04-23] ingest | kubelogin OIDC 认证

- **来源**：《K8S工具推荐：告别复杂认证！Kubernetes登录神器kubelogin指南》（微信公众号文章）
- **操作**：整合到现有文档 [[Docker-Kubernetes/k8s-installation-management/k8s多集群kubeconfig管理]]，新增"OIDC 认证：kubelogin"章节
- **新增内容**：
  - kubelogin 核心特性（浏览器登录、短期令牌、自动刷新、加密存储）
  - 安装方式（brew / choco / krew）
  - kubeconfig exec 模式配置示例
  - 适用场景（企业 SSO、多团队共享、合规审计）
- **决策**：原文内容较轻，不足以独立成文，整合到已有 kubeconfig 管理文章中更自然

---

## [2026-04-23] ingest | Client-Go K8s 客户端开发

- **来源**：《初始K8S客户端工具Client-Go》（微信公众号文章）
- **操作**：创建 [[Go/client-go-K8s客户端开发]] 新文章
- **新增内容**：
  - client-go 简介、用途、核心功能
  - 客户端初始化（集群内外双模式）
  - CRUD 完整代码示例（Create / Update 冲突重试 / List / Delete 三种策略）
  - Client-Go + Gin 实战：Web API + 模板渲染控制台

---

## [2026-04-23] ingest | ACK 网络规划与成本优化

- **来源**：《踩过网段坑才懂：K8s 网络规划与成本优化的底层逻辑》（微信公众号文章）
- **操作**：创建 [[Aliyun/网络/ACK网络规划与成本优化]] 新文章
- **新增内容**：
  - 网段规划与成本关系（IP 不足→集群重建、CIDR 重叠→跨 AZ 费用、路由膨胀）
  - CIDR 设计最佳实践（分区分段、Pod 大 Service 小、不与 VPC 重叠、多集群留空间）
  - ACK 流量成本优化（单 AZ 优先、控制公网、SLB 精打细算）
  - 网络插件选型：Flannel vs Terway
- **关联更新**：[[KnowledgeBase/entities/Aliyun]] 网络章节补充 ACK 网络规划，知识空白标记更新为"部分填补"

---

## [2026-04-23] ingest | K8s 部署防火墙端口配置

- **来源**：《部署K8S时关闭防火墙被吐槽了，我连夜整理全部需要开放的端口》（微信公众号文章）
- **操作**：创建 [[Docker-Kubernetes/k8s-installation-management/k8s部署防火墙端口配置]] 新文章
- **新增内容**：
  - 生产环境正确做法：保留 firewalld + 精准开放端口（而非关闭防火墙）
  - 各组件端口详解：kubeadm 核心、kubelet、kube-proxy、Calico、Ingress
  - Master / Worker 节点分别的 firewalld 配置命令
  - 端口速查总结表（组件 × Master/Worker × 是否必需）

---

## [2026-04-23] ingest | K8s 1.35 EnvFiles（fileKeyRef）

- **来源**：《k8s 1.35 版本 Pod环境变量配置》（微信公众号文章）
- **操作**：将 K8s 1.35 新特性 EnvFiles 整合到现有文档 [[Docker-Kubernetes/k8s-basic-resources/k8s基础-configMap-Secret]]
- **新增内容**：
  - K8s 1.35 `fileKeyRef` 机制：从 emptyDir 卷文件加载环境变量，主容器无需挂载
  - initContainer 生成配置 → kubelet 启动时注入的工作流
  - 5 种环境变量注入方式对比表
  - 环境变量管理规范（分层管理、命名规范、默认值、文档化）

---

## [2026-04-23] ingest | FinOps 云成本优化实战

- **来源**：《老杨的压箱底的技能聊聊FinOps》（微信公众号文章）
- **操作**：创建 [[Aliyun/资源管理/FinOps-云成本优化实战]] 新文章
- **新增内容**：
  - FinOps 方法论（量化→优化→固化）
  - 多云账单 CLI（阿里云 BSS OpenAPI / 腾讯云 tccli / 华为云 BSS v2）
  - 4 类浪费场景（低 CPU / 闲置 EIP / 存储无生命周期 / K8s 过配）
  - 4 个即时优化动作（夜间关机、降配、冷热分层、包年包月）
  - 预算告警 + Prometheus 账单看板 + Infracost PR 级成本评估
  - 实战案例：三步 30% 降本
- **关联更新**：[[KnowledgeBase/entities/Aliyun]] 资源管理章节补充 FinOps，知识空白标记已填补

---

## [2026-04-23] restructure | AI-视觉目录：提示词抽离 + awesome-design-md 归集

- **操作**：
  1. 从 [[提示词]] 抽离"作图"、"PPT"、"Claude Design 系统提示词"三个视觉设计章节，合并为 [[视觉设计提示词]]
  2. 将 `AI/awesome-design-md/`（67 个品牌 DESIGN.md）整体移入 `AI/AI-视觉/awesome-design-md/`
  3. 原 提示词.md 中保留交叉引用指向新文件
  4. 修复所有 wikilink 引用（README.md 中 67 个品牌链接 + log.md）
- **AI-视觉 目录当前内容**：
  - `AI做PPT-ppt-master.md` — SVG → PPTX 原生生成
  - `AI-Animation-Skill-科普动画.md` — 44 个 HTML 科普动画模板
  - `html-ppt-skill-实测指南.md` — HTML 幻灯片生成系统
  - `视觉设计提示词.md` — 作图/PPT/Claude Design 系统提示词
  - `awesome-design-md/` — 67 个品牌 DESIGN.md 前端设计系统

---

## [2026-04-23] restructure + create | AI-视觉目录整合 + html-ppt-skill

- **来源**：《一句话生成PPT，已经能用了：html-ppt-skill实测指南》（微信公众号文章）
- **操作**：
  1. 创建 `AI/AI-视觉/` 目录，将 PPT/HTML 视觉生成类文章归集
  2. 移动 [[AI/AI-视觉/AI做PPT-ppt-master]] 和 [[AI/AI-视觉/AI-Animation-Skill-科普动画]] 至新目录
  3. 创建 [[AI/AI-视觉/html-ppt-skill-实测指南]] 新文章
  4. 修复所有跨文件 wikilink 引用（OpenClaw 实体、log.md、文章间交叉引用）
- **新增内容**：
  - html-ppt-skill：36 主题 + 31 布局 + 14 deck + 47 动画的 HTML 幻灯片生成系统
  - 3 组实测场景（技术分享 cyberpunk / 融资路演 / 小红书图文）
  - 三款工具（PPT Master / AI-Animation-Skill / html-ppt-skill）横向定位对比

---

## [2026-04-23] create | AI-Animation-Skill HTML 科普动画生成

- **来源**：《扔掉PPT，用这44个HTML动画模板，让AI帮你做科普视频》（微信公众号文章）
- **操作**：创建 [[AI/AI-视觉/AI-Animation-Skill-科普动画]] 新文章
- **新增内容**：
  - 项目简介：单 HTML 文件输出、零依赖、完全离线
  - 与 Gamma / Beautiful.ai 对比表
  - 44 个模板详解（26 PPT Level2 + 4 基础 + 14 流程图动画）
  - 安装使用流程（OpenClaw / WorkBuddy / QClaw）
  - 与 PPT Master 的定位对比
- **关联更新**：[[KnowledgeBase/entities/OpenClaw]] Skills 插件生态补充 AI-Animation-Skill 条目

---

## [2026-04-23] update | Skill 质量治理：7 类失效模式与 Skill Craft

- **来源**：《我做了一个 Claude Skill 质检工具：专门解决 Claude Skill 的不触发、乱触发、越用越跑偏》（微信公众号文章）
- **操作**：将 Skill 失效模式分析和 Skill Craft 工具整合到 [[AI/ClaudeCode/Claude Code 扩展体系]] 的 Skills 章节
- **新增内容**：
  - 7 类系统性失效模式（约束衰减、工具漂移、输出膨胀、依赖链断裂、并行孤岛、触发模糊、幻觉填充）
  - Skill Craft 质检工具 4 种模式（check/fix/create/audit）
  - 3 层评估体系（8 结构模块 + 7 反模式 + 3 完整性原则）
  - fix 模式的 4 类关联检查机制
- **关联更新**：[[KnowledgeBase/entities/Claude-Code]] Skills 章节补充质量治理说明

---

## [2026-04-23] update | Obsidian 微信公众号发布插件

- **来源**：《告别公众号排版烦恼：Obsidian一键发布插件使用指南》（微信公众号文章）
- **操作**：将插件功能、安装配置、使用方法整合到 [[KnowledgeBase/entities/Obsidian]] 的"实用社区插件"章节
- **新增内容**：
  - Wechat Public Platform 插件介绍（作者 ai-chen2050）
  - 7 项核心功能表（上传素材、添加草稿、发布文章、群发消息、下载素材、百家号分发、数据统计）
  - 安装与配置步骤（AppID / AppSecret / IP 白名单）
  - Frontmatter 发布参数示例（封面图三级优先级）
  - 权限说明（个人订阅号 vs 认证公众号）
- **知识空白更新**：移除"Obsidian 插件开发与定制"条目

---

## [2026-04-22] update | Claude Code 并行开发：Git Worktree + 工作流编排 + Routines

- **来源**：《Claude Code 并行开发完全指南：Subagents + Agent Teams + Git Worktree + 工作流编排实战》（微信公众号文章）
- **操作**：将 Git Worktree、工作流编排、Routines 三块新内容整合到 [[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams]]
- **新增内容**：
  - 第三部分：Git Worktree 并行开发（命令、实战、与 Agent Teams 对比选型表）
  - 第四部分：工作流编排（Plan 模式嵌入、5 阶段 Multi-Agent 工作流模板、CLAUDE.md 固化）
  - Routines 定时自动执行（3 种触发方式、配置示例、与 Agent Teams 无人值守流水线）
  - 常见坑汇总（4 类）、全局选型决策表（6 场景）

---

## [2026-04-21] create | Awesome DESIGN.md 前端设计提示词集合

- **来源**：[VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) 仓库
- **操作**：将 67 个品牌的 DESIGN.md 设计系统文件添加到 `AI/AI-视觉/awesome-design-md/` 子目录
- **内容**：每个品牌目录保留 DESIGN.md + README.md + preview.html + preview-dark.html（共 268 个文件）
- **新建**：[[AI/AI-视觉/awesome-design-md/README|导航首页]]，含 DESIGN.md 概念说明、使用方法、按 8 大分类的品牌 wikilink 目录

---

## [2026-04-20] update | Claude Code 扩展体系 - Datadog MCP 配置

- **来源**：《Set Up the Datadog MCP Server 1》（Datadog 官方文档）
- **操作**：在 [[AI/ClaudeCode/Claude Code 扩展体系]] MCP 章节新增 Datadog MCP Server 配置
- **内容**：Claude Code 两种配置方式（远程 HTTP / 本地二进制）、权限要求、Toolset 按需加载机制、18 个 Toolset 完整列表（16 GA + 2 Preview）

---

## [2026-04-20] update | OpenClaw second-brain 知识管理插件

- **来源**：《Openclaw帮你管理个人知识库》（微信公众号文章）
- **操作**：将 second-brain 插件内容整合到 [[OpenClaw-Skills-Plugins]] 的"记忆插件"章节前，新增"个人知识库 - second-brain"章节
- **改动**：安装配置命令、6 种使用场景表格、核心能力总结、与记忆插件的区别说明
- **实体更新**：[[KnowledgeBase/entities/OpenClaw]] Skills 插件生态新增 second-brain 条目

---

## [2026-04-20] update | AI做PPT - ppt-master 补充完整内容

- **来源**：[[Clippings/这才是AI做ppt的正确姿势 ！ 1]]（完整版微信公众号文章）
- **操作**：根据完整原文更新 [[AI/AI-视觉/AI做PPT-ppt-master]]
- **新增内容**：与现有工具对比表（Gamma/Beautiful.ai/Copilot）、SVG→DrawingML 原生转换原理、双文件输出机制、强制顺序生成设计、内置资源数量（20 布局 + 52 可视化 + 6700 图标 + 12 图像后端）、公司模板支持、15 个官方案例（229 页）、作者背景与项目动机

---

## [2026-04-20] create | AI做PPT - ppt-master

- **来源**：《这才是AI做ppt的正确姿势 ！》（微信公众号文章）+ [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) 仓库
- **操作**：在 AI 目录下新建 [[AI/AI-视觉/AI做PPT-ppt-master]] 文章
- **内容**：ppt-master 项目简介、核心特性（多格式/多风格/CRAP 设计原则）、AI 角色系统（Strategist→Executor→Optimizer 管道）、7 步使用流程、技术栈

---

## [2026-04-18] update | Containerd V2 私有仓库配置整合

- **来源**：《V2 版 Containerd 配置私有仓库和镜像加速》（微信公众号文章）
- **操作**：将 V2 版 containerd 私有仓库配置内容整合到 [[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤]] 的 containerd 配置章节
- **改动**：
  - 新增 `config_path` 与 `mirrors` 互斥警告 callout，含 V1/V2 插件路径差异说明
  - 将原有 Harbor 私有仓库示例扩展为两种方式：跳过证书校验（测试环境）+ 自签 CA 证书验证（生产环境推荐）
  - 新增 Authorization header 认证配置和 crictl 验证命令

---

## [2026-04-18] update | K8s Namespace Terminating 强制删除脚本

- **来源**：[[Clippings/实用脚本：强制删除K8s命名空间（Terminating状态）]]（微信公众号文章）
- **操作**：将自动化删除脚本整合到 [[Docker-Kubernetes/k8s-basic-resources/k8s基础-namespace-资源分配]] 的"ns删除后卡在Terminating状态"章节
- **改动**：原有手动步骤保留，新增原理说明 + 完整自动化脚本（含参数交互和结果验证）

---

## [2026-04-18] ingest | Istio Sidecar vs Ambient 模式对比

- **来源**：《Istio Sidecar vs Ambient：不是"谁先进"，而是"谁更省、谁更稳、谁更适合你现在"》（微信公众号文章）
- **操作**：简化整理为 [[Docker-Kubernetes/k8s-networking-service-mesh/Istio-Sidecar-vs-Ambient]]
- **知识库更新**：
  - `entities/Istio.md` — 新增 Sidecar vs Ambient 模块 + sources 引用 + 相关文章链接
  - "可延展方向"中 Ambient Mesh 条目已标记为已覆盖

---

## [2026-04-18] create | OpenClaw Workspace 运维实战文章

- **来源**：《牛逼干货分享！OpenClaw Workspace 运维实战手册》（微信公众号文章，1500+ 行）
- **操作**：简化整理为 [[AI/OpenClaw/OpenClaw-Workspace-运维]]（约 400 行），保留核心运维知识，去除冗余示例和重复内容
- **核心内容**：
  - 配置与内容文件体系分离架构
  - 标准目录布局与多 Agent 环境隔离策略
  - 核心配置文件速查（openclaw.json / TOOLS.md 权限分级）
  - 记忆系统运维（builtin vs qmd、污染处理、清理策略）
  - Skill 三级加载层级
  - 故障排查清单（7 类问题）
  - 备份恢复与灾难恢复（RTO/RPO）
  - 安全加固（权限基线、敏感信息管理、审计日志）
- **知识库更新**：
  - `entities/OpenClaw.md` — 新增 sources 引用 + Workspace 运维模块
  - `index.md` — 新增 OpenClaw Workspace 运维条目

---

## [2026-04-18] update | Claude Code Plugin 新增 obra/superpowers

- **来源**：[obra/superpowers](https://github.com/obra/superpowers)（通过 DeepWiki 获取仓库信息）
- **操作**：从"开源 Skills 仓库"一句话提及扩展为"开源 Plugin 推荐"独立章节，含 22 个 Skill 全表、强制工作流 7 步说明、安装方式
- **内容**：强迫 AI 按高级工程师标准流程工作的 Skills 套件——TDD + 头脑风暴 + 子智能体隔离开发 + 代码审查

---

## [2026-04-18] update | Claude Code Plugin 新增 shanraisshan/claude-code-best-practice

- **来源**：[shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice)（通过 DeepWiki 获取仓库信息）
- **操作**：整理简化后添加到 [[AI/ClaudeCode/Claude Code 扩展体系]] 的"开源 Plugin 推荐"部分
- **内容**：Vibe Coding → Agentic Engineering 进阶指南，Command→Agent→Skill 三层编排模式 + RPI/Cross-Model 等工作流

---

## [2026-04-18] update | Claude Code Plugin 新增 davila7/claude-code-templates

- **来源**：[davila7/claude-code-templates](https://github.com/davila7/claude-code-templates)（通过 DeepWiki 获取仓库信息）
- **操作**：整理简化后添加到 [[AI/ClaudeCode/Claude Code 扩展体系]] 的"开源 Plugin 推荐"部分
- **内容**：500+ 组件的模板市场，含 7 个内置 Plugin 套件（git-workflow、supabase-toolkit、nextjs-vercel-pro 等）+ 多语言项目模板 + 附带工具

---

## [2026-04-18] update | Claude Code Skills 新增 excalidraw-diagram-generator

- **来源**：《用这个 Skill，直接一句话生成手绘架构图，省时省力～》（微信公众号文章，菜鸟教程）
- **操作**：整理简化后添加到 [[AI/ClaudeCode/Claude Code 扩展体系]] 的"各种 Skill 推荐"部分
- **知识库更新**：`entities/Claude-Code.md` 覆盖描述更新

---

## [2026-04-18] update | Openclaw-多智能体 内联代码块替换为 wikilinks

- **来源**：[[AI/OpenClaw/Openclaw-多智能体]]（Raw Source，应用户明确要求修改）
- **操作**：将两个多智能体章节中的内联身份文件和 Skill 文件替换为 wikilinks
  - **"实现多智能体程序开发团队"章节**：12 个内联代码块（architect/pm/frontend-engineer/backend-engineer × AGENTS.md/IDENTITY.md/SOUL.md）→ wikilinks，节省约 13,700 字符
  - **"实现多智能体AIOps团队"章节**：12 个内联代码块（aiops/linux/container/k8s × AGENTS.md/IDENTITY.md/SOUL.md）→ wikilinks
  - **Skills开发**：4 个 Skill 子章节添加 `→ 生成的 Skill 文件：[[AI/agents/xxx/skills/yyy/SKILL.md]]` 链接
- **效果**：文档共减少约 2800 行重复内容，身份文件和 Skill 定义由 `AI/agents/` 目录统一管理

---

## [2026-04-18] ingest | OpenClaw 多智能体定义文件导出

- **来源**：`/Users/hang.xu/Downloads/agents-export-20260417-235735/`（从 [[AI/OpenClaw/Openclaw-多智能体]] 导出）
- **操作**：创建 `AI/agents/` 目录，拷入 8 个智能体完整定义文件集
  - **调度核心**：aiops（AIOps 架构师，纯路由型）
  - **基础设施层**：linux / container / k8s（三个运维执行专家）
  - **开发层**：architect / backend-engineer / frontend-engineer
  - **管理层**：pm（产品经理）
  - 每个智能体含 IDENTITY.md + SOUL.md + AGENTS.md + HEARTBEAT.md
  - 4 个附带 Skills：k8s-install-orchestrator、docker-runtime-install、k8s-cluster-install、rocky-linux10-init
- **知识库更新**：
  - 新建 `sources/openclaw-agents-export-summary.md` — 来源摘要页
  - `entities/OpenClaw.md` — 新增 sources 引用 + 智能体定义文件表格
  - `index.md` — 新增"AI/agents"分区，AI 篇数 18→26
  - `inventory/repository-inventory.md` — 新增 agents 目录盘点

---

## [2026-04-17] create | 自研 k8s-inspect-skills Skill（Shell 版）

- **来源**：基于 [[Docker-Kubernetes/k8s-monitoring-logging/K8s全面巡检脚本-生成HTML健康报告]] 的 Shell 脚本改造
- **新建目录**：`AI/skills/k8s-inspect-skills/`（含 SKILL.md + k8s_inspect.sh）
- **AI 适配改造**：
  - 新增 `--kubeconfig` / `--output-dir` 参数解析
  - 新增集群连接预检（`check_connection`）
  - 日志输出重定向到 stderr，stdout 仅输出结构化摘要 + 报告路径
  - 输出 `INSPECTION SUMMARY` 文本块供 Agent 解析
  - 修复 DaemonSet/Deployment 列格式差异（CoreDNS 误判）和事件字段位移
  - macOS/Linux 日期命令兼容
- **实测**：v1.35.3 集群（3 节点 / 43 Pod / 13 NS / 38 Warning Events）通过
- **知识库更新**：
  - `sources/k8s-report-skills-summary.md` — 扩展为合并摘要页，覆盖 Python + Shell 两个 Skill
  - `entities/Claude-Code.md` — 新增 sources 引用和覆盖列表条目
  - `index.md` — 新增 Shell 版条目，AI 篇数 17→18
  - `inventory/repository-inventory.md` — 新增 k8s-inspect-skills 目录盘点

---

## [2026-04-17] ingest | 自研 k8s-report-skills Skill（Python 版）

- **操作**：创建 `AI/skills/` 自研技能目录，从 `/Users/hang.xu/Downloads/skills/k8s-report-skills/` 拷入首个自研 Skill
- **新建目录**：`AI/skills/k8s-report-skills/`（含 SKILL.md、k8s_inspector.py、requirements.txt、templates/report.html）
- **清理**：删除 SKILL_TEMP.md（第三方 kubectl Skill 模板，与本项目无关）
- **Skill 功能**：Python kubernetes 客户端 + Jinja2 渲染 K8s 集群巡检 HTML 报告（6 大维度：集群信息/节点/Pod/Deployment/存储/事件）
- **知识库更新**：
  - 新建 `sources/k8s-report-skills-summary.md` — 来源摘要页
  - `entities/Claude-Code.md` — 新增 sources 引用和覆盖列表条目
  - `index.md` — 新增"AI/skills（自研 Skills）"分区，AI 篇数 16→17

---

## [2026-04-17] ingest | K8s 全面巡检脚本

- **来源**：《K8s 全面巡检脚本：一键生成炫酷 HTML 健康报告》（微信公众号文章剪藏）
- **操作**：清理网页扒取的混乱格式（转义字符、断行、HTML 残留），整理为标准 Markdown + 干净代码块
- **新建文件**：`Docker-Kubernetes/k8s-monitoring-logging/K8s全面巡检脚本-生成HTML健康报告.md`
  - 7 大巡检模块的完整 Shell 脚本（节点/Pod/资源/证书/网络/组件/事件）
  - HTML 报告模板（深色仪表盘风格）
  - CronJob 定时执行 + Dockerfile + RBAC
  - 钉钉/企微告警集成
- **知识库更新**：
  - `sources/k8s-monitoring-logging-batch-summary.md` — 新增文档摘要，文档数 20→21
  - `index.md` — 更新监控日志摘要描述

---

## [2026-04-17] update | 开源 Plugin 推荐（andrej-karpathy-skills）

- **来源**：《2.3K 小文件拿到 4 万星，它让你的 Claude Code 乖乖听话》 + GitHub 仓库 forrestchang/andrej-karpathy-skills
- **操作**：在 `AI/ClaudeCode/Claude Code 扩展体系.md` Plugin 章节新增"开源 Plugin 推荐"
  - andrej-karpathy-skills（⭐46.5K）：4 条行为准则、3 种安装方式、效果判断标准
  - wshobson/agents：交叉引用到多智能体协作文档
- **知识库更新**：`sources/Claude-Code扩展体系-summary.md` 新增 2 条知识点 + 1 条"值得注意"

---

## [2026-04-17] update | wshobson/agents 开源 Agent 生态摄入

- **操作**：在 `AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams.md` 的"开源 Agents 推荐"章节新增 wshobson/agents 仓库完整介绍
  - 项目定位：72 个插件、112 个 Agent、146 个 Skills、16 个编排器
  - 全部 Agent 分类表（10 大类、112 个 Agent 含模型分配和一行描述）
  - 安装方式和模型分配策略
- **知识库更新**：
  - `sources/多智能体协作-summary.md` — 新增开源 Agent 生态知识点（4 条）
  - `entities/Claude-Code.md` — 更新覆盖列表，标注 wshobson/agents 内容

---

## [2026-04-17] restructure | Claude Code 扩展体系文章合并

- **操作**：将 4 篇独立文章合并为 1 篇 `AI/ClaudeCode/Claude Code 扩展体系.md`
  - 合并来源：`MCP.md`、`Skills.md`、`Slash Command.md`、`Plugin.md`（已删除）
  - 按四层架构重新组织：MCP（外部工具）→ Skills（自动能力包）→ Slash Commands（手动工作流）→ Plugin（打包分发）
  - 新增总览对比表和"一句话总结"帮助快速理解四层定位
- **知识库更新**：
  - 来源摘要页：4 篇旧摘要合并为 `sources/Claude-Code扩展体系-summary.md`（已删除旧文件）
  - 实体页：`entities/Claude-Code.md`、`entities/MCP.md` — 更新 sources 字段和覆盖列表
  - 地图：`maps/claude-code-openclaw-map.md` — 更新知识体系树和共同概念表
  - INDEX.md — 更新来源摘要表格和推荐阅读路径

---

## [2026-04-17] restructure | Subagents + Agent Teams 合并为一篇

- **操作**：将 `AI/ClaudeCode/Subagents.md` 和 `AI/ClaudeCode/Agent Teams.md` 合并为 `AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams.md`
- **删除文件**：`Subagents.md`、`Agent Teams.md`、`sources/Subagents-summary.md`、`sources/AgentTeams-summary.md`
- **新建文件**：`sources/多智能体协作-summary.md`（合并后的摘要页）
- **引用更新**：`entities/Claude-Code.md`、`INDEX.md`、`maps/tool-map.md`、`maps/ai-workflow-map.md`、`maps/claude-code-openclaw-map.md`、`inventory/repository-inventory.md` 中的所有链接已更新

---

## [2026-04-17] ingest | Agent Teams 文档摄入

- **摄入来源**：`AI/ClaudeCode/Agent Teams.md`（基于官方文档 https://code.claude.com/docs/en/agent-teams 撰写的中文使用指南）
- **来源摘要页**：`sources/AgentTeams-summary.md`
- **实体页增强**：`entities/Claude-Code.md` — 新增 5.5 Agent Teams 层级（与 SubAgents 对比表、核心组件说明），更新 sources 字段和覆盖列表，消除"多人协作"知识空白
- **INDEX.md 更新**：AI/ClaudeCode Sources 表格新增 Agent Teams 行

---

## [2026-04-17] restructure | INDEX.md 链接格式改造（wikilink → markdown link）

- **目的**：让 INDEX.md 在 GitHub 上也能点击跳转，同时 Obsidian 中保持可用
- **方案**：仅改造 INDEX.md（导航门面页），其他 wiki 内部页面保持 `[[wikilink]]` 不变
- **改动**：将 INDEX.md 中所有 `[[wikilink|显示名]]` 转换为 `[显示名](relative-path.md)` 格式
  - KnowledgeBase 内部链接使用相对路径：`entities/Docker.md`、`concepts/CICD.md`
  - 原始来源链接使用上级目录：`../AI/ClaudeCode/ClaudeCode基础指南.md`
- **影响范围**：仅 INDEX.md 一个文件，其他 70+ 个 wiki 页面不受影响

---

## [2026-04-17] create | 批量补建高频红链 stub 实体页（11 个）

- **触发**：用户请求补建引用 ≥3 次的实体红链
- **新建 stub 实体页（11 篇）**：
  - `entities/NVIDIA.md`（4 次引用）— GPU 硬件厂商
  - `entities/PBS.md`（4 次引用）— HPC 作业调度系统
  - `entities/containerd.md`（4 次引用）— K8s 默认容器运行时
  - `entities/CUDA.md`（3 次引用）— NVIDIA GPU 计算平台
  - `entities/Calico.md`（3 次引用）— K8s CNI 网络插件
  - `entities/Docker-Compose.md`（3 次引用）— 单机多容器编排工具
  - `entities/Kustomize.md`（3 次引用）— K8s 原生配置管理工具
  - `entities/NFS.md`（3 次引用）— 网络文件系统存储
  - `entities/Nginx.md`（3 次引用）— Web 服务器与反向代理
  - `entities/PostgreSQL.md`（3 次引用）— 开源关系型数据库
  - `entities/Rancher.md`（3 次引用）— K8s 多集群管理平台
- **INDEX.md 更新**：实体表格新增 11 行
- **断链报告更新**：红链从 236 降至 225，有效链接从 370 升至 381（63%）
- 累计实体页：35 个（18 原始 + 6 首次 lint stub + 11 本次 stub）

---

## [2026-04-17] lint | 首次全库健康检查

### 检查结果

| 检查项 | 结果 |
|--------|------|
| 总 wikilink 数 | 609 个唯一目标 |
| 有效链接 | 370 个（61%） |
| 孤儿页面 | 0 个 ✅ |
| 错误分类链接 | 5 个 → 已修复 ✅ |
| 缺失 concepts/ 页面 | 69 个（红链） |
| 缺失 entities/ 页面 | 167 个（红链） |
| 原始来源断链 | 0 个 ✅ |

### 修复操作

1. **修复 5 个错误分类链接**：ArgoCD/Helm/Ingress/Istio/Kubernetes 从 `concepts/` 改为 `entities/`
   - `maintenance/naming-normalization.md`（4 处）
   - `sources/k8s-networking-service-mesh-batch-summary.md`（1 处）

2. **创建 6 个高频引用的 stub 实体页**（引用 ≥5 次）：
   - `entities/Harbor.md`（8 次引用）
   - `entities/Redis.md`（6 次引用）
   - `entities/GitLab.md`（5 次引用）
   - `entities/Kafka.md`（5 次引用）
   - `entities/Loki.md`（5 次引用）
   - `entities/MySQL.md`（5 次引用）

### 剩余红链说明

236 个红链（引用了尚未创建独立页面的概念/实体）属于正常现象：
- 批量摘要中对工具和概念的引用超出了当前实体页覆盖范围
- Obsidian 原生支持红链，可在后续 Ingest 中按需创建页面
- 建议：引用 ≥3 次的概念/实体在后续维护中逐步补建页面

---

## [2026-04-17] ingest | 全库剩余领域摄入（103 篇）

- **摄入来源**：Python(27) + Linux-Shell(24) + AI-OpenClaw(9) + Go(9) + HPC(7) + CloudComputing(7) + GPU-DeepLearning(4) + Database(3) + Middlewares(3) + OS(3) + Networking(2) + IaC(2) + Git(2) + C++(1) + SoftwareTesting(2)
- **来源摘要页（6 篇新建）**：
  - `sources/python-batch-summary.md`（27 篇）
  - `sources/linux-shell-batch-summary.md`（24 篇）
  - `sources/ai-openclaw-misc-batch-summary.md`（9 篇：OpenClaw + Copilot + 提示词）
  - `sources/go-batch-summary.md`（9 篇）
  - `sources/hpc-cloud-gpu-batch-summary.md`（18 篇：HPC + CloudComputing + GPU）
  - `sources/misc-domains-batch-summary.md`（18 篇：Database/Middlewares/OS/Networking/IaC/Git/C++/SoftwareTesting）
- **实体页增强（3 篇）**：
  - `entities/OpenClaw.md`：补充 Skills 生态、Channels、AIOps、多智能体、CoPaw 对比
  - `entities/Terraform.md`：补充三阶段工作流、核心文件结构、ARM Template 对比
  - `entities/Slurm.md`：补充集群架构、4 种安装方式、GPU GRES 调度、Prometheus 监控集成
- **INDEX.md 更新**：Sources 区域新增 6 个领域摘要表格，标记"全部领域已摄入完成"
- 🎉 **里程碑**：全库 17 个领域、~350 篇原始文档已全部摄入 wiki 编译层

---

## [2026-04-17] ingest | Docker-Kubernetes 全量摄入（145 篇）

- **摄入来源**：`Docker-Kubernetes/` 全部子目录，共 145 篇原始文档
- **来源摘要页（10 篇新建，按子目录批量摘要）**：
  - `sources/docker-batch-summary.md`（12 篇）
  - `sources/k8s-basic-resources-batch-summary.md`（20 篇）
  - `sources/k8s-installation-management-batch-summary.md`（16 篇）
  - `sources/k8s-monitoring-logging-batch-summary.md`（20 篇）
  - `sources/k8s-CICD-batch-summary.md`（19 篇）
  - `sources/k8s-networking-service-mesh-batch-summary.md`（7 篇）
  - `sources/k8s-security-auth-batch-summary.md`（7 篇）
  - `sources/k8s-scaling-storage-batch-summary.md`（7 篇）
  - `sources/k8s-db-middleware-UI-batch-summary.md`（18 篇）
  - `sources/k8s-misc-batch-summary.md`（18 篇：Helm/CKA-CKS/KubeBlocks/Harbor/K3S/Velero/GPU）
- **实体页增强（9 篇重写或增强）**：
  - `entities/Kubernetes.md`：从文章索引升级为知识编译页——核心架构、9 大子领域覆盖地图
  - `entities/Docker.md`：补充核心功能、部署实践总结
  - `entities/Helm.md`：补充 v3 架构、OCI 支持、Helm vs Kustomize 对比
  - `entities/ArgoCD.md`：补充架构细节、Image Updater、GitOps 理念
  - `entities/Jenkins.md`：补充 4 种部署方式、企业 DevOps 落地模式
  - `entities/Prometheus.md`：补充数据模型、3 种 HA 模式、联邦架构、5 层监控体系
  - `entities/Grafana.md`：补充统一可视化定位、LGTM 轻量级可观测性栈
  - `entities/Istio.md`：补充数据面/控制面架构、流量管理、企业落地模式
  - `entities/Ingress.md`：补充 hostNetwork 部署、DNS 解析链
- **INDEX.md 更新**：Sources 区域新增 Docker-Kubernetes 10 篇批量摘要表格

---

## [2026-04-17] ingest | Azure 全量摄入（21 篇）

- **摄入来源**：`Azure/` 目录，共 21 篇原始文档
- **来源摘要页**：`sources/azure-batch-summary.md`
- **实体页增强**：
  - `entities/Azure.md`：补充 7 大服务子领域、实践亮点、知识空白
  - `entities/AKS.md`：添加 sources 字段
- **INDEX.md 更新**：Sources 区域新增 Azure 摘要表格

---

## [2026-04-17] ingest | Aliyun 全量摄入（19 篇）

- **摄入来源**：`Aliyun/` 目录（计算/网络/存储/数据库/资源管理），共 19 篇原始文档
- **来源摘要页**：`sources/aliyun-batch-summary.md`
- **实体页增强**：
  - `entities/Aliyun.md`：补充 5 大服务子领域、安全纵深链、与 Azure 对比视角
- **INDEX.md 更新**：Sources 区域新增 Aliyun 摘要表格

---

## [2026-04-17] ingest | AI/ClaudeCode 试点摄入（7 篇）

- **摄入来源**：`AI/ClaudeCode/` 目录下 7 篇原始文档（跳过改造计划元文档）
- **来源摘要页（7 篇新建）**：
  - `sources/ClaudeCode基础指南-summary.md`
  - `sources/MCP配置-summary.md`
  - `sources/Skills-summary.md`
  - `sources/Subagents-summary.md`
  - `sources/Slash-Command-summary.md`
  - `sources/Plugin-summary.md`
  - `sources/obsidian-claude-搭建个人知识库-summary.md`
- **实体页增强（3 篇重写）**：
  - `entities/Claude-Code.md`：从文章索引升级为 7 层架构知识编译页（+sources 字段、核心架构、工作流模式、最佳实践、知识空白）
  - `entities/MCP.md`：补充 10 个 MCP 服务器详细信息、推荐组合、安装方式
  - `entities/Obsidian.md`：补充 3 种 Claude Code 集成方案、知识库架构实践
- **INDEX.md 更新**：Sources 区域从"待摄入"更新为 7 篇摘要表格
- 本次 Ingest 是 Phase 2 试点，验证完整 Ingest 流程

---

## [2026-04-17] restructure | Phase 0 + Phase 1 改造

- 创建 `CLAUDE.md` schema 文件，定义三层架构、页面模板、操作流程
- 创建 `KnowledgeBase/sources/` 目录（原始来源摘要页存放处）
- 创建 `KnowledgeBase/entities/` 目录（工具/平台实体页存放处）
- 创建 `KnowledgeBase/log.md`（本文件）
- 将 18 个实体页从 `concepts/` 拆分到 `entities/`：AKS、Aliyun、ArgoCD、Azure、Claude-Code、Docker、Grafana、Helm、Ingress、Istio、Jenkins、Kubernetes、MCP、Obsidian、OpenClaw、Prometheus、Slurm、Terraform
- 保留 7 个概念页在 `concepts/`：CICD、Observability、Python运维开发、容器运行时、日志系统、服务网格、自动化运维
- 重构 `INDEX.md`，统一使用 `[[wikilink]]` 格式，按 concepts/entities/maps/analysis/maintenance 分类
- 更新所有概念页和实体页的交叉引用链接

---

## [2026-04-16] create | 初始构建知识编译层

- 创建全部知识编译层：盘点(2) + 地图(8) + 概念(25) + 分析(3) + 维护(3)
- 创建 INDEX.md 导航入口


## [2026-04-27] create | 多Agent vs 单Agent架构决策分析

- 创建 `analysis/multi-agent-vs-single-agent.md` 分析页
- 核心论点：多Agent在现阶段很多时候是伪需求，提出信息隔离与并发需求两个决策维度
- 内容涵盖：决策框架表格、信息损失分析、模型注意力论证、多Agent身份切换的真正价值
- 关联页面：`KnowledgeBase/sources/多智能体协作-summary.md`、[[KnowledgeBase/entities/Claude-Code]]
- 更新 INDEX.md 分析报告分类，新增第 4 条条目


## [2026-05-04] lint | 知识库全面健康检查

### 1. 断链检查
- 共检查 2,458 个 wikilink，发现 346 个断链（273 个唯一目标）
- **15 个格式错误链接**：`entities/OpenClaw.md` 和 `entities/Azure.md` 中有尾部反斜杠 `\` 的畸形 wikilink
- **1 个命名不一致**：`Docker Compose`（空格）→ 实际文件名 `Docker-Compose`（连字符）
- **9 个路径错误**：链接指向 `KnowledgeBase/entities/X` 但实际文件在 Raw Source 目录（ECS、VPC、WAF、Fiddler、Landing Zone、OpenStack、RabbitMQ、RocketMQ、VSCode）
- **217 个缺失 KB 页面**：被引用但从未创建的概念/实体页（66 个概念 + 151 个实体），高频缺失：StorageClass(4次)、ServiceMesh(3次)、高可用架构(3次)
- **19 个死链**：`log.md` 中引用的原始剪藏路径，文件已移动或删除

### 2. 孤儿页检查（无入链页面）
- 总计 83 个 wiki 页面，25 个孤儿页（30%）
- concepts/ 和 entities/：**0 孤儿**（核心知识页全部互联良好）
- sources/：11 个孤儿（50%）— 无概念/实体页链回这些摘要
- maps/：5 个孤儿（63%）
- analysis/：4 个孤儿（100%）
- inventory/：2 个孤儿（100%）
- maintenance/：3 个孤儿（100%）

### 3. Raw Source 覆盖检查
- 16 个 Raw Source 目录已 100% 覆盖（Docker-Kubernetes、Aliyun、Azure、Go、Python、Linux-Shell 等）
- **AI/ 目录严重欠缺**：301 个文件仅 37 个被引用（12%覆盖）
  - CloudOps-Agent-项目/（74 文件）：完全未摄入
  - RAG-Agent-项目/（33 文件）：完全未摄入
  - Hermes-agent/（2 文件）：完全未摄入
  - AI-视觉/awesome-design-md/（135 文件）：完全未摄入
- **IaC/**：`terraform-container-management.md` 新增未摄入（1 文件）

### 4. Frontmatter 规范检查
- 80 个 wiki 页面全部通过：title、tags（含 `knowledgebase/*`）、date — **100% 合规**
- **aliases 字段缺失**：58 个文件（72.5%）缺少 aliases

### 5. Index 完整性检查
- index.md 与磁盘文件 **完全同步**：82 个条目全部对应实际文件，无缺失、无多余

### 建议优先修复项
1. 修复 15 个反斜杠畸形链接（OpenClaw.md、Azure.md）
2. 修复 Docker Compose 命名不一致
3. 摄入 AI/ 下新增项目（CloudOps-Agent、RAG-Agent、Hermes-agent）
4. 为 sources/ 页面建立入链（从 concepts/entities 页面链回）
5. 补充高频缺失概念页（StorageClass、ServiceMesh、高可用架构）


---

## [2026-05-05] lint | 文件重命名后断链修复

- **触发**：用户更新了文章标题（`OpenClaw-Skills-插件` → `OpenClaw-Skills-Plugins`，`Hermes Agent全解析-与OpenClaw对比及飞书接入指南` → `Hermes与OpenClaw对比及飞书接入指南`）
- **检查范围**：KnowledgeBase/ 全部 93 个页面，748 个 wikilink

### 1. 断链修复（12 处）

| 文件 | 修复内容 |
|------|----------|
| [[KnowledgeBase/maps/ai-workflow-map.md\|ai-workflow-map]] | `OpenClaw-Skills-插件` → `OpenClaw-Skills-Plugins`（2 处）；Hermes 摘要篇数 2→3 |
| [[KnowledgeBase/maps/claude-code-openclaw-map.md\|claude-code-openclaw-map]] | `OpenClaw-Skills-插件` → `OpenClaw-Skills-Plugins`（3 处：代码块 + 表格） |
| [[KnowledgeBase/inventory/repository-inventory.md\|repository-inventory]] | `OpenClaw-Skills-插件` → `OpenClaw-Skills-Plugins`（2 处） |
| [[KnowledgeBase/sources/hermes-agent-batch-summary.md\|hermes-agent-batch-summary]] | 补全路径 `AI/Hermes-agent/Hermes与OpenClaw对比及飞书接入指南`（frontmatter + 正文，2 处） |
| [[KnowledgeBase/entities/OpenClaw.md\|OpenClaw]] | 补全路径 `AI/OpenClaw/OpenClaw-Skills-Plugins`（frontmatter + 正文，2 处）；补全 `AI/Hermes-agent/` 前缀（1 处） |
| [[KnowledgeBase/sources/ai-openclaw-misc-batch-summary.md\|ai-openclaw-misc-batch-summary]] | 补全路径 `AI/OpenClaw/OpenClaw-Skills-Plugins`（frontmatter + 正文，2 处） |

### 2. 孤儿页检查
- **结果**：0 个孤儿页。所有 93 个 KB 页面至少有 1 个入链（主要来自 INDEX.md 和 maps/）

### 3. 概念覆盖差距（≥3 篇引用但无独立页面）
- Tekton（11 篇）、Ansible（11 篇）、Kyverno（7 篇）、Velero（6 篇）、Skywalking（6 篇）、VPA（6 篇）
- Hermes Agent（5 篇）、RAG（5 篇）、KEDA（5 篇）、HPA（5 篇）
- 飞书/Lark（4 篇）

### 4. 残留历史链接（不修改）
- `log.md` 中 3 处历史记录引用旧文件名（`Hermes Agent全解析-与OpenClaw对比及飞书接入指南`、`[[OpenClaw-Skills-Plugins]]` 短路径），属于历史快照不做修改


---

## [2026-05-05] ingest | HarnessKit — AI 编码智能体统一管理工具

- **来源**：GitHub 仓库 https://github.com/RealZST/HarnessKit（README + API 元数据）
- **操作**：
  - 新建 [[HarnessKit]]：工具介绍文章（功能特性、支持的 Agent、安装使用、安全审计、与其他 AI 工具的关系）
  - 新建 [[KnowledgeBase/sources/harnesskit-summary]]：来源摘要页
  - 更新 [[KnowledgeBase/maps/ai-workflow-map]]：补充阅读列表 + 相关工具
  - 更新 [[KnowledgeBase/INDEX.md]]：新增 HarnessKit 来源摘要条目


---

## [2026-05-09] ingest | Obsidian + Claude Code AI 知识库完整指南（三文合并）

- **来源**：[[AI/Obsidian/obsidian-claude-code-AI知识库完整指南]]
- **操作**：
  - 将三篇文章合并为一篇完整指南：
    - `karpathy-llm-wiki-改造计划`（内部规划文档，含差距分析与行动计划）
    - `obsidian-claude-搭建karpathy-wiki知识库`（工具搭建方法论，含六大操作谱系）
    - `obsidian-claude-code-AI知识管家`（公众号文章，含 Markdown 母语论证与实践判断）
  - 删除三篇原始文件（内容已完整保留在合并文章中）
  - 删除两个旧来源摘要页：`obsidian-claude-搭建个人知识库-summary.md`、`obsidian-claude-code-AI知识管家-summary.md`
  - 新建 [[KnowledgeBase/sources/obsidian-claude-AI知识库完整指南-summary.md]]：合并后的来源摘要
  - 更新 [[KnowledgeBase/index.md]]：替换两个旧条目为一个新条目
  - 更新 [[AI/index.md]]：Obsidian 子目录条目从 4 篇→2 篇，关键入口更新


## [2026-06-05] ingest | 飞书 CLI 画板生成能力

- 清洗并简化原始文章《别画了！用飞书 CLI 真能一句话生成架构图》，去除营销内容，保留技术要点
- 清洗后文章存入 `AI/OpenClaw/飞书CLI画板-一句话生成架构图.md`
- 创建来源摘要页 `KnowledgeBase/sources/feishu-cli-whiteboard-summary.md`
- 更新实体页 `KnowledgeBase/entities/OpenClaw.md`：添加相关文章链接 + Skills 插件生态新增 feishu-whiteboard-themes
- 更新 `KnowledgeBase/index.md`：AI-OpenClaw 分区新增飞书CLI画板条目

## [2026-06-05] ingest | Docker 安全配置与 Capabilities 加固

- 清洗原始文章《Docker 安全配置详解：RockyLinux 9.7 开发容器》，去除营销内容
- 清洗后文章存入 `Docker-Kubernetes/docker/docker安全配置-Capabilities与容器加固.md`
- 创建来源摘要页 `KnowledgeBase/sources/docker-security-capabilities-summary.md`
- 更新实体页 `KnowledgeBase/entities/Docker.md`：新增"安全加固"小节（7 项措施）、添加 sources 引用、标记知识空白部分已覆盖
- 更新 `KnowledgeBase/index.md`：Docker-Kubernetes 分区新增安全加固条目
- 填补知识空白：Docker 安全加固（Seccomp、AppArmor）已有覆盖，仅 rootless 模式尚缺

## [2026-06-05] ingest | K8s 备份与灾备实战

- 清洗原始文章《K8s 集群的"后悔药"...备份与灾备实战全指南》，去除营销内容，保留完整技术要点（三层模型/etcd 实战/Velero 操作/六大避坑/告警规则）
- 清洗后文章存入 `Docker-Kubernetes/k8s-backup-dr/k8s备份与灾备实战-三层容灾架构.md`
- 创建来源摘要页 `KnowledgeBase/sources/k8s-backup-dr-summary.md`
- 更新实体页 `KnowledgeBase/entities/Kubernetes.md`：新增"备份与灾备"小节、添加 sources 引用
- 更新 `KnowledgeBase/index.md`：Docker-Kubernetes 分区新增备份与灾备条目
- 与已有 `k8s集群备份恢复-Velero.md` 形成互补：已有文章侧重 Velero 工具，新文章提供架构层面的三层容灾体系

## [2026-06-06] ingest | K8s PodDisruptionBudget 实战

- 清洗原始文章《K8s PodDisruptionBudget 实战：优雅滚动更新背后的守护神》，去除营销内容
- 清洗后文章存入 `Docker-Kubernetes/k8s-basic-resources/k8s-PodDisruptionBudget实战.md`
- 创建来源摘要页 `KnowledgeBase/sources/k8s-pdb-summary.md`
- 更新实体页 `KnowledgeBase/entities/Kubernetes.md`：声明式资源模型小节新增 PDB 条目、添加 sources 引用
- 更新 `KnowledgeBase/index.md`：K8s 基础资源分区新增 PDB 条目

## [2026-06-06] ingest | VPA 实战补充（合并摄入）

- 分析原始文章《Kubernetes VPA深度解析...完整实战》与已有 `Docker-Kubernetes/k8s-scaling/helm部署vpa.md` 的重复度（~50%），决定合并而非独立摄入
- 提取 4 个独特增量追加到 `Docker-Kubernetes/k8s-scaling/helm部署vpa.md`：
  1. MySQL StatefulSet 实战案例（Off→Initial 渐进式 + 资源节省量化）
  2. 三个避坑点（OOMKill 恶性循环、JVM 应用推荐偏差、Prometheus 数据空洞）
  3. 自定义 Recommender（Prometheus 后端 + 自定义历史窗口）
  4. 渐进式落地四阶段方法论
- 更新来源摘要页 `KnowledgeBase/sources/k8s-scaling-storage-batch-summary.md`：VPA 条目补充增量内容摘要

## [2026-06-06] ingest | K8s 发布策略（蓝绿部署与金丝雀发布）

- 清洗原始文章《蓝绿部署还是金丝雀发布...K8s生产发布再也不翻车》，去除营销内容
- 清洗后文章存入 `Docker-Kubernetes/k8s-CICD/k8s发布策略-蓝绿部署与金丝雀发布.md`
- 创建来源摘要页 `KnowledgeBase/sources/k8s-release-strategy-summary.md`
- 更新概念页 `KnowledgeBase/concepts/CICD.md`：相关文章新增条目、标记"蓝绿/金丝雀"可延展方向已部分覆盖
- 更新 `KnowledgeBase/index.md`：K8s CI/CD 分区新增发布策略条目
- 与已有文章互补：deployment.md 有基础原理，istio.md 有服务网格方案，本文补充 Nginx Ingress 和 Argo Rollouts 两种生产级方案

## [2026-06-06] restructure | Prometheus-Stack 全家桶文章整合

- 将新文章《Prometheus + AlertManager + kube-prometheus 生产级部署完全指南》（131KB）与已有 `Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶.md`（52KB）合并
- 重新设计章节结构为十章 + 附录：
  - 一~七（原有内容重新编号）：概述 → 部署 → Grafana 管理 → CRD 资源 → Target Down 排查 → 告警规则 → AlertManager 配置
  - 八（新增）：参数优化与性能调优（资源规划/TSDB/抓取/AlertManager/Grafana/PromQL/存储/网络 六维度）
  - 九（新增）：高可用与扩展方案（Prometheus HA 架构/Thanos 集成/联邦集群/AlertManager HA/多集群 Remote Write）
  - 十（新增）：故障排查与常见问题（排查命令/5 大常见问题/性能检查清单/备份恢复/生产部署清单）
  - 附录（新增）：PromQL 速查 + 版本兼容参考
- 更新来源摘要页 `KnowledgeBase/sources/k8s-monitoring-logging-batch-summary.md`：扩展摘要描述
- 去重策略：基础概念/Helm 部署/CRD 配置/AlertManager 路由等重复内容保留原有版本（更详细的实操内容），仅追加新文章的独特增量

## [2026-06-06] update | Prometheus-Stack 文章补充缺失内容

- 在 `Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶.md` 补充以下缺失内容：
  1. 一、概述章节：Prometheus 核心特性表 + 四种指标类型 + AlertManager 核心功能表 + 告警生命周期状态机 + kube-prometheus 组件总览 + CRD 速查表 + 整体架构图 + 数据流说明
  2. 六、告警规则章节末尾：Prometheus 自身告警规则（配置重载失败/AlertManager 连接/规则评估/WAL 损坏/存储空间不足等）
  3. 四、CRD 资源章节：常见应用 ServiceMonitor 配置（MySQL/Redis/Kafka/Elasticsearch/PostgreSQL Exporter 完整 YAML + 镜像版本参考）

## [2026-06-06] ingest | Script-Server 脚本 Web 化工具

- 清洗原始文章《Script-Server...》并存入 `Python/script-server-脚本Web化工具.md`
- 创建来源摘要页 `KnowledgeBase/sources/script-server-summary.md`
- 更新 `KnowledgeBase/index.md`：Python 分区新增条目

## [2026-06-06] update | Claude Code Skills 工程化内容整合

- 将《滴滴面试官逗乐了...SKILL.md...5K token》的核心内容简化后整合进 `AI/ClaudeCode/Claude Code 扩展体系.md` 的 Skills 章节
- 扩展"渐进式披露机制"子章节，新增内容：
  1. 官方三层加载机制表（Level 1/2/3 的 token 成本与加载时机）
  2. 官方硬限制（name 64 字符 / description 1024 字符 / SKILL.md < 5K token）
  3. SKILL.md 定位（分层引用网络的根节点，非 prompt 非文档）
  4. 拆分判断标准表（<200 行健康 / >800 行立即重构）
  5. 拆分优先级（示例→规则→长流程，决策树不拆）
  6. 好引用 vs 坏引用 + 子文件不循环引用原则
  7. 实战演进案例（1900 行→612 行，token 从 28K 降到 12K）
  8. Skill 间 handoff 协议设计

## [2026-06-07] ingest | CLAUDE.md 维护工程

- 清洗原始文章《腾讯面试官...CLAUDE.md...init...》并存入 `AI/ClaudeCode/CLAUDE.md维护工程-四层加载与指令预算.md`
- 创建来源摘要页 `KnowledgeBase/sources/claude-md-maintenance-summary.md`
- 更新 `KnowledgeBase/index.md`：AI/ClaudeCode 分区新增条目
- 与已有文章的关系：`12条规则模板.md`（具体规则）和 `21条指令清单.md`（拿来即用指令）侧重内容，本文侧重维护方法论和架构设计，三者互补

## [2026-06-07] restructure | CLAUDE.md 三篇文章合并为完全指南

- 将三篇 CLAUDE.md 相关文章合并为一篇：
  - `AI/ClaudeCode/CLAUDE.md最佳实践-12条规则模板.md`（写什么：Mnilax 12 条规则）
  - `AI/ClaudeCode/CLAUDE.md最佳实践-21条指令清单.md`（怎么写：Mayank 21 条指令）
  - `AI/ClaudeCode/CLAUDE.md维护工程-四层加载与指令预算.md`（怎么管：加载体系+指令预算）
- 合并后文件：`AI/ClaudeCode/CLAUDE.md完全指南-规则-指令-维护工程.md`
- 章节结构：概念 → 四层加载 → 指令预算 → 好坏规则 → 12 条规则模板 → 21 条指令清单 → rules/ 目录 → /init vs /memory → 配置四角色 → 官方结构 → 实战模板
- 创建新来源摘要 `KnowledgeBase/sources/claude-md-complete-guide-summary.md`
- 更新 `KnowledgeBase/index.md`：替换旧条目为新的合并条目
- 旧的三篇原始文件保留未删除，由用户决定是否清理

## [2026-06-07] ingest | Graphify 软件工程知识图谱工具

- 清洗原始文章《开源 AI 编程可查询的软件工程知识图谱：Graphify 完整上手攻略》
- 清洗后文章存入 `AI/Graphify-软件工程知识图谱工具.md`
- 创建来源摘要页 `KnowledgeBase/sources/graphify-summary.md`
- 更新 `KnowledgeBase/index.md`：新增 AI/工具分区

## [2026-06-07] ingest | Kubernetes MCP Server + Dify 智能运维

- 清洗原始文章《AI 接管 Kubernetes 运维——Kubernetes MCP Server》
- 清洗后文章存入 `AI/Kubernetes-MCP-Server-Dify智能运维.md`，保留完整背景说明、四大核心特点详述、四大使用场景、架构图、部署命令（含参数说明）、MCP 连接配置、Agent 完整提示词模板
- 创建来源摘要页 `KnowledgeBase/sources/k8s-mcp-server-dify-summary.md`
- 更新 `KnowledgeBase/index.md`：AI/工具分区新增条目

## [2026-06-07] ingest | AIOps 实战：Golang K8s 智能运维工具链

- 清洗原始文章《AIOps实战：手搓K8s智能运维工具链》
- 清洗后文章存入 `AI/AIOps/AIOps实战-Golang手搓K8s智能运维工具链.md`，保留完整背景说明、三层架构图、Go 源码（client-go 三客户端/OpenAI 适配层）、Function Calling 工作流四步骤、DeepRui 诊断流程四步、传统脚本 vs DeepRui 对比表、技术栈参考资料
- 创建来源摘要页 `KnowledgeBase/sources/aiops-golang-k8s-toolchain-summary.md`
- 更新 `KnowledgeBase/index.md`：AI/工具分区新增条目

## [2026-06-07] ingest | OpenRAG 生产级知识库架构实战

- 清洗原始文章《OpenRAG 生产级知识库架构实战...企业级 RAG 平台》（66KB），去除营销尾部，保留全部 21 章技术内容（42KB）
- 清洗后文章存入 `AI/RAG/OpenRAG生产级知识库架构实战.md`，完整保留：四面分离架构图、文档导入链路设计（含状态机+Worker 职责拆分）、Chunk 元数据模型、OpenSearch Mapping 示例、混合检索代码骨架、Reranker 实现骨架、权限模型（ACL 字段+检索前过滤+生成前复核）、问答服务骨架、K8s 部署拆分 YAML、缓存分层示例、SLI/SLO 指标、演进路线三阶段、真实案例、Agentic RAG 策略、MCP 接入、排坑清单、上线前 Checklist
- 创建来源摘要页 `KnowledgeBase/sources/openrag-production-summary.md`
- 更新 `KnowledgeBase/index.md`：AI/RAG-Agent 分区新增条目

## [2026-06-08] ingest | CodeGraph 代码语义知识图谱

- 清洗原始文章《CodeGraph：给 Claude Code 先画一张代码地图...》并存入 `AI/ClaudeCode/CodeGraph-代码语义知识图谱.md`
- 保留完整内容：问题背景、效果数据（VS Code 实测对比）、核心能力（影响分析/19 种语言/框架路由/本地数据/自动同步）、安装命令、适用场景分析、与 Graphify 的对比表
- 创建来源摘要页 `KnowledgeBase/sources/codegraph-summary.md`
- 更新 `KnowledgeBase/index.md`：AI/ClaudeCode 分区新增条目


## [2026-06-14] ingest | Claude Fable 5 System Prompt

- 摄入 `AI/ClaudeCode/Claude-Fable-5-system-prompt.md`（~125K 字符完整系统提示词）
- 创建来源摘要页 `KnowledgeBase/sources/claude-fable5-system-prompt-summary.md`，提炼 11 个关键知识点：产品定位（Mythos-class）、产品生态（Cowork/Chrome/Excel/PPT Agent）、行为规约（refusal/tone/wellbeing/evenhandedness）、~15 个内置工具、沙箱架构、Artifact 系统、Claudeception、MCP 连接器流程、版权合规硬限制、Skill 强制规则、搜索决策规则
- 更新实体页 `KnowledgeBase/entities/Claude-Code.md`：新增 sources 引用、新增"内部架构（来自 Fable 5 系统提示词）"小节、新增"在本仓库中的覆盖"条目、更新知识空白
- 更新 `KnowledgeBase/index.md`：AI/ClaudeCode 分区新增条目

## [2026-06-14] update | CodeGraph 文件引用检查

- 用户将 `AI/ClaudeCode/CodeGraph-代码语义知识图谱.md` 移动至 `AI/代码知识图谱/CodeGraph-代码语义知识图谱.md`
- 检查所有 wiki 页面引用：均使用短格式 wikilink `[[CodeGraph-代码语义知识图谱]]`，Obsidian 自动按文件名解析，无需修改


## [2026-06-24] lint | 全量健康检查

- 并行执行 6 维度 lint：断链检查、孤儿页、交叉引用、来源时效性、Frontmatter 一致性、模板合规
- 检查 113 个 wiki 页面 + 全库原始来源文件
- 核心发现：234 处断链（主要集中在批量摘要的短路径）、29 孤儿页（核心页 0 孤儿）、122 处缺失交叉引用、4 篇严重过期摘要、4 篇 index.md 缺失条目
- 生成完整报告 `KnowledgeBase/maintenance/lint-report-2026-06-24.md`，含 13 条优先修复清单


## [2026-06-24] lint-fix | 高优先修复

- **断链修复**：`claude-md-complete-guide-summary.md` 引用的 `CLAUDE.md完全指南-规则-指令-维护工程` 文件不存在（三篇合并文件从未创建），改为引用 3 篇独立原始文件：`CLAUDE.md最佳实践-12条规则模板`、`CLAUDE.md最佳实践-21条指令清单`、`CLAUDE.md维护工程-四层加载与指令预算`
- **index.md 同步更新**该条目的引用
- **index.md 补充 4 篇缺失条目**：`claude-md-maintenance-summary`（AI/ClaudeCode 分区）、`k8s-cgroup-v2-summary`（K8s 安装管理分区）、`kyverno-1.18-summary`（K8s 安全认证分区）、`rabbitmq-ha-summary`（K8s 中间件分区）
- **确认 5 处"路径不匹配"为 lint 误报**：均使用短格式 wikilink，Obsidian 按文件名解析正常工作


## [2026-06-28] lint-fix | 批量断链修复 + 模板迁移

### 批量断链修复
- 修复 `cloudops-agent-batch-summary.md` 67 处 + `rag-agent-batch-summary.md` 66 处短路径 wikilink
- 方法：构建 `短文件名→完整相对路径` 映射，Python 正则批量替换
- 效果：两个文件的课程章节链接全部转为全路径格式，零残留

### 7 篇概念页模板迁移
- 页面：CICD、Observability、Python运维开发、容器运行时、日志系统、服务网格、自动化运维
- 操作：
  - Heading 重命名：`在本仓库中的位置`→`在本仓库中的覆盖`、`关联概念`→`与其他概念的关系`、`可延展方向`→`知识空白`
  - 合并 `相关文章` 到 `在本仓库中的覆盖`
  - 新增 `核心要点` section（逐页从定义内容提炼 4-5 个要点）
  - 补充 frontmatter：`sources`、`aliases` 字段

### 10 篇实体页模板迁移
- 页面：AKS、ArgoCD、Grafana、Helm、Ingress、Istio、Jenkins、Prometheus、Slurm、Terraform
- 操作：
  - Heading 重命名：`定义`→`简介`、`编译知识`→`核心功能`、`在本仓库中的位置`→`在本仓库中的覆盖`、`关联概念`→`相关概念与实体`、`可延展方向`→`知识空白`
  - 合并 `相关文章` 到 `在本仓库中的覆盖`
  - 新增 `使用场景` section（逐页提炼 3 个典型场景）
  - 补充 frontmatter：`aliases` 字段


## [2026-06-28] ingest | Git Worktree AI 开发实践指南

- 清洗《Vibe Coding时代的Git Worktree实践指南》（去除微信营销噪音），存入 `AI/ClaudeCode/Git-Worktree-AI开发实践指南.md`
- 保留完整内容：问题分析（AI 上下文丢失）、Worktree 原理、核心原则（一个 AI 会话 = 一个 Worktree）、两个典型场景（紧急修复/多方案并行）、5 个实践踩坑
- 创建来源摘要页 `KnowledgeBase/sources/git-worktree-ai-dev-summary.md`
- 更新 `KnowledgeBase/entities/Claude-Code.md`：新增 sources 引用 + 覆盖条目
- 更新 `KnowledgeBase/index.md`：AI/ClaudeCode 分区新增条目


## [2026-06-28] ingest | K8s 标签与选择器实战

- 清洗《【K8s资源管理】Kubernetes 标签与选择器避坑...》并存入 `Docker-Kubernetes/k8s-basic-resources/k8s基础-pod调度-标签与选择器实战.md`
- 保留完整内容：Labels vs Annotations 区分、`app.kubernetes.io/*` 六件套命名规范、两种选择器用法、5 条 SRE 铁律（含 Deployment selector 不可变、版本标签陷阱、成本归因）、4 个翻车案例（含 kubectl v1.33.0 Null 值修复）
- 创建来源摘要页 `KnowledgeBase/sources/k8s-labels-selectors-summary.md`
- 更新 `KnowledgeBase/index.md`：K8s 基础资源分区新增条目
- 填补知识空白：K8s 基础资源 21 篇批量摘要中缺少 Labels/Selectors 专题


## [2026-06-28] ingest | K8s 容器设计模式（四篇合并）

- 清洗并合并四篇容器设计模式剪藏文章（Sidecar / Init Container / Ambassador / Adapter）
- 存入 `Docker-Kubernetes/k8s-basic-resources/k8s基础-容器设计模式-Sidecar-Init-Ambassador-Adapter.md`
- 保留完整内容：四种模式的核心理念、应用场景、完整 YAML 配置示例、四模式对比表、选型指南
- 新增整合内容：四种模式对比表（运行时机/生命周期/职责/数据流/典型代表）
- 创建来源摘要页 `KnowledgeBase/sources/k8s-container-design-patterns-summary.md`
- 更新 `KnowledgeBase/index.md`：K8s 基础资源分区新增条目


## [2026-06-28] update | Claude Code 扩展体系 - Slash Commands 章节增强

- 从《技术Leader惊了...Claude Code 用得6吗》文章中提取 Slash Commands 实用内容
- 集成到 `AI/ClaudeCode/Claude Code 扩展体系.md` 的「三、Slash Commands」章节
- 新增内容：/powerup 入门引导、内置命令速查（5 大类 17 个命令）、快捷键表（8 个）、三个隐藏关键词（ultrathink/ultracode/ultraplan）、推荐资源（2 个网站）、日常高频五件套
- 原有自定义命令内容保留并重命名为「自定义斜杠命令」子节
- 未单独创建来源摘要页（内容已集成到现有文档中）


## [2026-06-28] ingest | OpenAI Codex config.toml 全量配置参考

- 清洗《OpenAI Codex 可视化配置生成器》并存入 `AI/Codex/Codex-config-toml-全量配置参考.md`
- 保留完整内容：21 个配置分组（基础配置、模型与提供方、审批与沙箱、网络代理、TUI、环境策略、权限 Profiles、MCP Servers、Hooks、Agents、Memories、Apps、Tools、Skills、Plugins、OTel、指令与文档、认证、状态杂项）
- 整理为结构化表格格式，方便速查
- 未创建独立来源摘要页（Codex 领域尚未系统性摄入，待积累更多文档后批量处理）


## [2026-06-28] ingest | Markdown Viewer Skills AI 文档配图

- 清洗《Markdown Viewer：让 AI 写文档时，顺手把图也画了》并存入 `AI/AI-视觉/Markdown-Viewer-Skills-AI文档配图.md`
- 保留完整内容：问题定义（文档配图痛点）、5 类技能（UML/云架构/网络拓扑/数据分析/infocard）、6 种渲染引擎、关键设计点（图是代码块/文档改图也改）、定位与局限分析
- 未创建独立来源摘要页（AI-视觉领域尚未系统性摄入，待积累后批量处理）


## [2026-06-28] ingest | Kubernetes Gateway API 入门

- 清洗《Kubernetes Gateway API 入门： Ingress 的下一代方案》并存入 `Docker-Kubernetes/k8s-networking-service-mesh/k8s-Gateway-API入门-Ingress下一代方案.md`
- 保留完整内容：Ingress 三大局限（annotation 绑定/职责混合/跨 namespace 困难）、Gateway API 核心资源模型（GatewayClass/Gateway/HTTPRoute）、hostname 分层控制、parentRefs/sectionName 绑定机制、完整请求链路、Ingress vs Gateway API 对比表
- 新增整合：Ingress vs Gateway API 对比表（原文无）
- 未创建独立来源摘要页（待积累后与 k8s-networking 批量摘要合并更新）


## [2026-06-28] ingest | effective-html AI 直出 HTML 工具实测

- 清洗《AI别再输出Markdown了，让它直接吐HTML — effective-html 工具实测》并存入 `AI/AI-视觉/effective-html-AI直出HTML工具实测.md`
- 保留完整内容：问题定义（Markdown 无法承载视觉交付）、三个 Skill（html 通用/html-diagram 架构图/html-plan 计划文档）、html-effectiveness 设计范本库（20 个模板）、HTML vs Markdown 各自优势对比
- 新增整合：与同类工具（Markdown Viewer Skills / html-anything / Mermaid）的定位对比表（原文无）


## [2026-06-28] ingest | K8s Backstage 内部开发者平台 IDP 实战

- 清洗《YAML 写到吐？2026 年最火的 K8s 平台工程实战：用 Backstage 打造一站式内部开发者平台》并存入 `Docker-Kubernetes/k8s-installation-management/k8s-Backstage-内部开发者平台IDP实战.md`
- 保留完整内容：平台工程理念（DevOps→IDP）、Backstage 架构（Frontend+Backend+PostgreSQL）、生产部署实战（PostgreSQL StatefulSet + app-config.yaml + Deployment + RBAC）、Software Catalog 实体定义、Software Templates 一键创建服务、TechDocs 代码即文档、8 个插件推荐、5 大生产注意事项、竞品对比表（Backstage vs Port vs Cortex vs OpsLevel）
- 未创建独立来源摘要页（待积累后与 k8s-installation-management 批量摘要合并更新）


## [2026-06-28] ingest | K8s Operator 开发实战 Kubebuilder

- 清洗《通过例子介绍如何从零开发 Kubernetes Operator》并存入 `Docker-Kubernetes/k8s-basic-resources/k8s基础-Operator开发实战-Kubebuilder.md`
- 保留完整内容：Operator 组成（CRD + Controller + Manager）、Kubebuilder 环境搭建、完整 Go 代码（FooSpec/FooStatus CRD 定义 + Reconcile 控制循环 + Pod 事件映射）、运行与测试流程、进阶方向
- 新增整合：Operator 开发工具对比表（Kubebuilder/OperatorSDK/controller-runtime/Metacontroller，原文无）
- 与现有知识网络关联：概念页 Operator模式、CRD，原始文档 k8s基础-自定义CRD资源


## [2026-06-28] ingest | Admission Webhook 链冲突排查

- 清洗《当 Istio、Kyverno、Gatekeeper 三个 Webhook 同时存在，你的集群会发生什么？》并存入 `Docker-Kubernetes/k8s-security-auth/k8s-Admission-Webhook链冲突排查-Istio-Kyverno-Gatekeeper.md`
- 保留完整内容：Admission 链执行顺序（Mutating→Validating）、三组件各自修改范围、3 个生产坑（JSON Patch 路径脆/annotations 整体覆盖/Gatekeeper 拒绝最终对象）、排查三步法（列 Webhook→审计日志→隔离复现）、reinvocationPolicy/failurePolicy 分级策略、6 条编排规范、10 步排查清单
- 与现有知识关联：Kyverno（同目录）、Istio（networking 目录）、Gatekeeper/OPA（策略引擎）


## [2026-06-28] ingest | Loop Engineering 从 Prompt 到自动化流水线

- 清洗《Prompt该退环境了，未来属于Loop Engineering。》并存入 `AI/行业动态/Loop-Engineering-从Prompt到自动化流水线.md`
- 保留完整内容：四次跃迁对比（Prompt→Context→Harness→Loop，各自核心能力与底层学科）、Loop 五组件（定时任务/Worktree/知识体系/MCP/子Agent）、/goal 命令产品化、目标定义灵魂论（管理学视角）、古德哈特定律陷阱（Agent 删测试案例）、四条目标定义框架
- 与现有知识关联：Harness Engineering、Claude Code /goal /loop 命令、Boris Cherny 行业判断


## [2026-06-28] update | K8s 存储文档整合 PVC 扩容/缩容

- 将《【Kubernetes 存储扩容避坑指南】PVPVCStorageClass 在线扩容+缩容真相》整合到 `Docker-Kubernetes/k8s-basic-resources/k8s基础-storage.md` 末尾
- 新增章节「PVC 在线扩容与缩容」，保留完整内容：扩容前三件必查、两种扩容方式（patch/edit）、扩容后验证流程（后端→文件系统两阶段）、缩容不支持的核心限制、v1.34 扩容失败恢复机制、6 条生产环境建议、存储类选型表、常见问题速查表
- 未创建独立来源文件（内容直接整合到现有文档中）


## [2026-06-28] ingest | Understand-Anything 代码知识图谱可视化

- 清洗《55.5k Star！AI代码知识图谱神器开源，让Claude Code一次看懂全仓库》并存入 `AI/代码知识图谱/Understand-Anything-代码知识图谱可视化.md`
- 保留完整内容：问题定义（AI 读不下整仓/传统可视化无语义）、三层架构（Tree-sitter AST→多智能体图谱构建→交互可视化）、安装方式（Claude Code/Cursor/VS Code/Codex）、团队共享图谱（JSON Git 同步 + git-lfs）
- 新增整合：与 CodeGraph、Graphify 的三工具对比表（原文无）
- 放入 AI/代码知识图谱/ 目录，与 CodeGraph、Graphify、code-review-graph 形成完整的代码知识图谱工具群


## [2026-06-28] ingest | ArgoCD 多集群 GitOps 实战

- 清洗《多集群 GitOps 实践：如何用 Argo CD 管理上百个 Kubernetes 集群》并存入 `Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD多集群GitOps实战-ApplicationSet.md`
- 保留完整内容：三层目录模型（应用模板/环境覆盖/集群元数据）、ApplicationSet Generator 选型（Cluster/List/Git/Matrix）、Push vs Pull vs 区域级折中架构（含选型表）、Project 权限隔离（多租户最佳实践）、环境差异分层覆盖（values 拼接模板）、大规模发布节奏控制（6 种手段 + Progressive Sync）、100 集群平台落地架构
- 与现有知识关联：ArgoCD 实体页、联邦集群概念页、CICD 概念页


## [2026-06-28] update | ArgoCD 多集群实战整合生产加固 7 步法

- 将《告别 GitOps 翻车！7 招让 ArgoCD 稳如老狗》整合到 `Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD多集群GitOps实战-ApplicationSet.md` 末尾
- 新增章节「附：生产环境 7 步加固法」：资源限制（含实测数据）、工具选型（Helm vs Kustomize）、源代码与清单库分离（权责+安全）、多实例隔离（Red Hat 推荐）、声明式配置漂移陷阱（All-in Git + argocd app diff + Prometheus 监控）、AppProject 细粒度 RBAC、按需调整不盲套模板
- 更新 frontmatter source 为双来源数组


## [2026-06-28] ingest | TypeScript vs Python AI Agent 时代的语言分层

- 清洗《为什么 AI Agent 时代，TypeScript 正在抢走 Python 的主场？》并存入 `AI/行业动态/TypeScript-vs-Python-AI-Agent时代的语言之争.md`
- 保留完整内容：GitHub/npm/YC 三组数据信号、AI 技术栈两层分工（模型层 Python vs 应用层 TypeScript）、TypeScript 五个结构性优势（类型安全/框架生态/全栈同构/异步原生/边缘部署）、Python 四个不可替代领域、2026 年四大趋势（产品下半场/Agent SDK 标准/全栈工程师岗位/中国公司跟进）


## [2026-06-28] ingest | KEDA vs HPA 2026 终极对比

- 清洗《KEDA vs HPA 2026终极对比：v1.36原生缩零后该选谁？》并存入 `Docker-Kubernetes/k8s-scaling/KEDA-vs-HPA-2026终极对比-v1.36缩零.md`
- 保留完整内容：HPA 三种指标类型与三大硬伤、KEDA 架构（Scaler→HPA 代理模式）与 60+ 内置 Scaler 表、v1.36 HPA Scale-to-Zero（Beta 默认启用）+ External Metrics Fallback、全方位对比矩阵（10 维度）、五场景选型决策树、五大生产避坑（冷启动/认证/冻结/冲突/CRD 兼容）、Prometheus 告警规则
- 与现有知识关联：k8s-HPA-VPA、k8s-基于KEDA的弹性能力、k8s成本优化方案-FinOps实战


## [2026-06-28] update | Kafka 生产避坑整合到 strimzi-kafka 文档

- 将《一个副本没同步引发的"血案"：别再迷信云厂商的默认配置！》整合到 `Docker-Kubernetes/k8s-db-middleware/helm部署strimzi-kafka.md` 末尾
- 新增章节「Kafka 生产避坑：副本同步与云厂商默认配置陷阱」：事故复盘（min.insync.replicas=1 导致数据空洞）、副本同步核心参数详解、生产环境标准配置（Broker/Topic/Producer/监控告警）、通用原则（5 组件坑人默认配置表 + 部署前审查六问 + 三个不要）


## [2026-06-28] ingest | OpenCodeReview 阿里 AI 代码审查工程化

- 整合两篇剪藏文章（OpenCodeReview 详解 + 阿里 Open Code Review 工程化实践）为一篇
- 存入 `AI/行业动态/OpenCodeReview-阿里AI代码审查工程化.md`
- 保留完整内容：AI 代码质量数据（6 组权威报告）、通用 Agent 做 CR 的三个瓶颈、确定性工程骨架 + LLM 语义判断设计哲学、三项关键突破（隔离评审/行号分离/工具收束）、多语言路由/七层质量控制/可追溯、安装使用（三种审查模式）、三种集成方式（Skill/Plugin/命令文件）、CI/CD 集成、审查规则四层优先级、适用场景分析


## [2026-06-28] ingest | Obsidian Vault 模板库合集

- 清洗《Obsidian vault 模板库合集：48 个 GitHub 上的宝藏 vault，下载即用》并存入 `AI/Obsidian/Obsidian-Vault模板库合集-48个宝藏vault.md`
- 保留完整内容：48 个 vault 的 11 大分类表、挑选三原则（活跃度>star/场景对口/先标杆后同类）、5 个推荐 vault 详解（Kepano/Hub/JS Info/DevCookbook/HowToCook）、踩坑清单（3 个避坑）、5 分钟上手流程


## [2026-06-29] ingest | Codex 省 Token 工具实测

- 清洗《Codex 一键省 Token 大法，亲测有效》并存入 `AI/Codex/Codex-省Token工具实测-Ponytail-Headroom-RTK.md`
- 保留完整内容：四个省 Token 工具总览表（Ponytail/穴居人/Headroom/RTK-AI）、Ponytail 详解（YAGNI 理念/判断决策梯子/6 个 Skill/3 个 Hooks/安装方式）、Codex 实测对比（小游戏生成 vs 代码审查两个场景）、官方 Benchmark（前端任务代码行数减少 62-94%）、适用场景分析、背后洞察（教 Agent 学会克制）


## [2026-06-29] update | K8s 故障排查指南整合 DiskPressure 驱逐机制

- 将《Kubernetes 节点突发 DiskPressure事件告警？吃透 Kubelet 驱逐底层原理，告别盲目扩容》整合到 `Docker-Kubernetes/k8s-installation-management/k8s故障排查指南.md` 末尾
- 新增章节「节点 DiskPressure 与 Kubelet 驱逐机制」：认知纠偏（DiskPressure≠磁盘满）、Eviction Manager 底层链路（cAdvisor→阈值判定→GC→驱逐）、三类磁盘监控（NodeFS/ImageFS/ContainerFS）、Inode 耗尽隐患、Pod QoS 驱逐优先级、5 步线上排查流程、6 条生产最佳实践
- 补全了原文件缺失的"节点级故障排查"维度（原有内容只覆盖 Pod/Service/DNS/容器调试）


## [2026-07-18] ingest | Kubernetes v1.37 升级破坏性变更

- 摄入来源：《K8s 1.37 升级生死线》公众号文章
- 清洗并归档至 [[k8s-1.37-升级须知-breaking-changes]]
- 覆盖内容：
  - containerd 1.x → 2.0 强制升级要求和迁移方案
  - cgroup v1 → v2 迁移路径与检查命令
  - kubelet 废弃标志清理（--cgroup-driver 等）
  - DRA Partitionable Devices（GPU 切片调度，Alpha）
  - SELinuxMount 特性默认启用的影响
  - 完整的升级检查清单（升级前/中/后）
- 影响实体：[[KnowledgeBase/entities/Kubernetes]]、[[KnowledgeBase/entities/containerd]]
- 影响概念：[[KnowledgeBase/concepts/cgroup]]、[[KnowledgeBase/concepts/容器运行时]]

## [2026-09-05] lint | 断链检查

- 检查 `KnowledgeBase/` 下 129 个 Markdown 页面，共 3046 个 wikilink。
- 发现严格口径断链 344 条；其中 25 条疑似由 `\|` 转义显示分隔符导致，25 条去掉反斜杠后可解析。
- 生成维护报告：[[KnowledgeBase/maintenance/broken-links-2026-09-05|断链检查报告 2026-09-05]]。


## [2026-09-05] ingest | Codex 两个体验设置

- 清洗《2个设置，让Codex体验翻倍》并归档至 [[AI/Codex/Codex-两个设置提升体验]]。
- 保留技术内容：普通模式主动澄清的 `config.toml` 配置、完整 Juice 检查提示、使用顺序；移除公众号引流与互动话术。
- 新增 `KnowledgeBase/sources/codex-两个设置提升体验-summary.md` 来源摘要和 [[KnowledgeBase/entities/Codex|Codex 实体页]]，并更新 [[KnowledgeBase/maps/ai-workflow-map|AI 工作流专题地图]] 与 `INDEX.md`。
- 将 Juice 相关结论标注为作者经验，避免作为已验证的模型质量指标。

## [2026-09-05] ingest | 删除 PVC 后 PV 数据保护与复用避坑

- 清洗《删 PV 数据没了？避 3 坑》并归档至 `Docker-Kubernetes/k8s-storage/k8s删除PVC后PV数据保护与复用避坑.md`；保留回收策略、PV/PVC 命令、Released 复用、StatefulSet、VolumeSnapshot、恢复 SOP 与 FAQ，移除作者署名和微信赞赏页脚。
- 新增来源摘要：`KnowledgeBase/sources/k8s-pv-pvc-reclaim-policy-summary.md`。
- 更新 `KnowledgeBase/sources/k8s-scaling-storage-batch-summary.md`：文档数 8→9，新增 PV/PVC 生命周期与数据保护小节；Kubernetes 总文档数随本次摄入由 154→155。
- 更新 `KnowledgeBase/concepts/StorageClass.md`、`KnowledgeBase/concepts/Finalizer.md`、`KnowledgeBase/entities/Kubernetes.md`、`KnowledgeBase/maps/kubernetes-map.md`、`KnowledgeBase/index.md` 与 `Docker-Kubernetes/index.md` 的交叉引用、存储文档数和导航。
- 核心知识：动态供给 PV 的 `Delete` 可能销毁底层云盘；修改 StorageClass 不会回溯已有 PV；`Retain` 后的 `Released` PV 复用前必须审查 claimRef 和旧数据；删除重要 PVC 前应确认快照/备份，CSI Finalizer 强制清理需谨慎。

## [2026-09-05] ingest | Docker 镜像无引擎下载与 tar 导出

- 清洗《不依赖本地docker环境 从Docker Hub 下载镜像到本地 并保存为tar镜像文件》并存入 `Docker-Kubernetes/docker/docker无需本地环境从DockerHub下载镜像并保存为tar.md`。
- 保留技术内容：Registry 直接拉取、manifest list/OCI index、多架构与 digest 选择、分层断点续传、Range 限制、指数退避重试、Python 依赖及 `docker load` 导入。
- 新增 [[KnowledgeBase/sources/docker-image-download-summary|来源摘要]]，更新 [[KnowledgeBase/entities/Docker|Docker 实体页]]、Docker 批次摘要、工具/领域地图、文档盘点和 `INDEX.md`。
- 移除正文作者署名、引流话术和免责声明（保留作者元数据）；标注原文 `docker_pull_v2.py` 与示例 `docker_pull.py` 的命名差异。

## [2026-09-06] ingest | KServe + KEDA 基于请求指标自动扩缩容

- 清洗《KServe + KEDA 实战：基于请求指标实现服务自动扩缩容》并归档至 `Docker-Kubernetes/k8s-scaling/KServe+KEDA实战-基于请求指标实现服务自动扩缩容.md`。
- 保留完整技术内容：KEDA 2.17.2、kube-prometheus-stack、KServe InferenceService、HAMi DRA GPU 共享、ServiceMonitor、Prometheus 查询、External Metrics API、持续负载及 `1 -> 2 -> 1` 扩缩容验证；移除作者署名、往期回顾和公众号引流尾段，去除重复/装饰性图片。
- 新增来源摘要：`KnowledgeBase/sources/kserve-keda-request-autoscaling-summary.md`。
- 更新 `KnowledgeBase/sources/k8s-scaling-storage-batch-summary.md`、`KnowledgeBase/entities/Kubernetes.md`、`KnowledgeBase/entities/Prometheus.md`、`KnowledgeBase/maps/kubernetes-map.md`、`KnowledgeBase/INDEX.md` 与 `Docker-Kubernetes/index.md`。
- 核心知识：KServe Predictor → vLLM `/metrics` → Prometheus → KEDA → External Metrics API → HPA；使用 `running + waiting` 请求数作为扩缩容信号，并结合 300 秒缩容稳定窗口完成实测验证。


## [2026-09-06] ingest | 12 个常用 Prompt 与提示词主题库重组

- 摄入《都Agent时代了，我还是想分享给你这12个我最常用的Prompt。》，移除公众号引流、作者宣传、赞赏、装饰图片和重复铺垫，完整保留 12 个可复用 Prompt。
- 将原 [[AI/提示词/提示词|提示词集合]] 重组为入口页，并新增 6 个主题页：需求澄清、学习研究与事实核查、分析决策与解决问题、AI 编程协作、写作与表达、自我探索与人生设计。
- 重复内容按快速版/完整版合并；补充联网能力、95% 启发式阈值、真实人物观点归因和自我探索非诊断用途等使用边界。
- 新增 [[KnowledgeBase/sources/12个常用Prompt-summary|来源摘要]] 与 [[KnowledgeBase/concepts/提示词工程|提示词工程概念页]]，更新 [[KnowledgeBase/maps/ai-workflow-map|AI 工作流专题地图]] 和 KnowledgeBase/index.md。

## [2026-09-06] lint | 提示词摄入后 Wiki 健康检查

- 检查全 vault 850 个 Markdown 文件；KnowledgeBase/ 共 135 个页面、3146 个 wikilink。
- 本次新增或重组的 9 个文件全部存在，新增页面断链 0，KnowledgeBase 页面基础 frontmatter 完整率 135/135。
- 全 Wiki 严格口径发现未解析 wikilink 299 条（246 个唯一目标），其中 log.md 历史记录 26 条；发现孤儿页 28 个，均为既有维护债务。
- 生成 [[KnowledgeBase/maintenance/wiki-lint-2026-09-06|Wiki 健康检查 2026-09-06]]；本次新增概念页和来源摘要均已获得 index 与主题地图入链。


## [2026-09-06] update | 提示词代码块有序列表排版修正

- 修正 [[AI/提示词/提问与需求澄清提示词]]、[[AI/提示词/学习研究与事实核查提示词]]、[[AI/提示词/分析决策与解决问题提示词]] 中代码块内挤在同一行的有序项。
- 将每个编号项拆为独立行，并修复“苏格拉底式问诊”中第 3～5 项的错误粘连与缩进；提示词语义保持不变。
- 扫描 AI/提示词/ 下全部 7 个 Markdown 文件，代码块内未再发现同一行包含多个有序编号的情况。


## [2026-09-06] restructure | AI 代码审查与知识图谱目录重命名

- 用户将目录从 AI/代码知识图谱/ 重命名为 AI/Code review和知识图谱/。
- 更新 AI/index.md 的目录名称与文档数（5→6），修正 CodeGraph 来源摘要中的 Graphify 显式路径。
- 当前知识页已无旧目录路径引用；既有 log.md 中的旧路径作为历史记录保留。

## [2026-09-06] ingest | AI 代码审查验证闭环

- 清洗《用 AI 审核 AI 的代码，踩了一堆坑之后我的方法》并归档至 [[AI/Code review和知识图谱/AI代码审查闭环-验证优先与敏感信息清理]]。
- 保留完整技术内容：Lint/类型检查/单元测试/集成测试/E2E 门禁、独立 Worktree、完整仓库上下文、真实运行验证、安全扫描、敏感信息清理、对抗式测试和项目级审查配置；移除作者宣传和公众号引流。
- 新增 [[KnowledgeBase/sources/ai-code-review-validation-loop-summary|来源摘要]] 与 [[KnowledgeBase/concepts/AI代码审查|AI 代码审查概念页]]。
- 更新 [[KnowledgeBase/entities/Claude-Code]]、[[KnowledgeBase/entities/Codex]]、[[KnowledgeBase/maps/ai-workflow-map|AI 工作流专题地图]]、KnowledgeBase/index.md 和 AI/index.md。
- 将具体审查命令与深度参数标记为需按当前产品版本确认；本次新增链接均可解析。


## [2026-09-06] update | Pod 健康探针重启风暴案例

- 将《一场由健康探针引发的Pod重启风暴——K8s LivenessReadiness Probe配置不当的深度复盘》清洗后追加至 [[Docker-Kubernetes/k8s-basic-resources/k8s基础-pod#探针失效真实案例]]。
- 保留事故数据、错误配置、时间线、Liveness/Readiness/Startup 分工、端点实现、监控排查命令和工程治理措施；移除作者宣传与公众号引流。
- 补充技术校正：探针时间倍数属于经验性建议；示例 Prometheus 指标并非 kubelet 固定指标；PDB 与 HPA 不能直接阻止 Liveness 误杀。
- 新增 [[KnowledgeBase/sources/k8s-probe-restart-storm-summary|来源摘要]]，更新 K8s 基础资源批量摘要、[[KnowledgeBase/entities/Kubernetes]]、[[KnowledgeBase/maps/kubernetes-map|Kubernetes 主题地图]] 和 KnowledgeBase/index.md。


## [2026-09-06] ingest | Kubernetes Volume Health Monitor 存储健康监控

- 清洗《让存储故障现形：Kubernetes Volume Health Monitor 原理与生产接入》，移除作者署名、重复引言、赞赏尾注和排版噪音，归档至 `Docker-Kubernetes/k8s-storage/让存储故障现形：Kubernetes Volume Health Monitor 原理与生产接入.md`。
- 新增来源摘要：[[KnowledgeBase/sources/k8s-volume-health-monitor-summary]]。
- 更新 `k8s-scaling-storage` 批量摘要、Kubernetes 实体、Observability 概念、Prometheus 实体、Kubernetes 专题地图、知识库索引和 Docker-Kubernetes 目录索引。
- 核心知识：4 个 CSI 健康 RPC 分别写入 PVC、Pod 和 CSINode；1.37 Alpha 需要 feature gate 与 CSI 驱动双重支持；Prometheus 告警应区分 `Degraded`/`Inaccessible`，remediation 需带冷却、重试上限和人工确认。

## [2026-09-06] ingest | K8s 1.37 原生 HPA Scale-to-Zero

- 清洗《告别 KEDA：K8s 1.37 原生 HPA Scale-to-Zero 落地实战，空闲 Worker 直接缩到 0》并归档至 `Docker-Kubernetes/k8s-scaling/k8s-1.37原生HPA-Scale-to-Zero实战.md`；保留 `HPAScaleToZero` 原理、External/Object 指标、HPA YAML、冷启动/防抖/就绪探针、六个生产陷阱、监控建议和 KEDA 迁移清单，移除作者宣传、公众号引流、下期预告与赞赏尾段。
- 新增 `KnowledgeBase/sources/k8s-hpa-scale-to-zero-1.37-summary.md`；更新 `KnowledgeBase/sources/k8s-scaling-storage-batch-summary.md`，文档数由 10 篇增至 11 篇（扩缩容 7 篇、存储 4 篇）。
- 更新 `KnowledgeBase/entities/Kubernetes.md`、`KnowledgeBase/entities/Prometheus.md`、`KnowledgeBase/maps/kubernetes-map.md`、`KnowledgeBase/INDEX.md` 和 `Docker-Kubernetes/index.md` 的交叉引用与文档计数。

## [2026-09-06] update | 合并并发 K8s 扩缩容与存储摄入

- 回读时发现同日另有 `Kubernetes Volume Health Monitor` 摄入已合并到 `k8s-scaling-storage` 批量摘要；在保留该变更的基础上，将批量摘要统一校正为 12 篇（扩缩容 7 篇、存储 5 篇）。
- 同步校正 `KnowledgeBase/entities/Kubernetes.md` 与 `KnowledgeBase/maps/kubernetes-map.md` 的 K8s 总文档数为 158 篇，并校正 `KnowledgeBase/INDEX.md` 的 Kubernetes 与扩缩容/存储计数。
- 本次新增的原生 HPA Scale-to-Zero 归档、来源摘要、Prometheus 交叉引用和目标目录文件均保留。


## [2026-09-06] ingest | 大模型精度与量化：FP64 到 NVFP4

- 清洗并归档《一文讲清 FP64、FP32、TF32、BF16、FP16、FP8、INT8、INT4、NVFP4》至 `AI/企业级私有化大模型/大模型精度与量化：FP64到NVFP4.md`；移除作者署名、目录和提示性噪声，保留精度格式、缩放机制、显存估算及训练/推理选择等技术内容。
- 通过 PicGo 上传原文中的 7 张图片，并将归档文档中的图片链接替换为图床地址。
- 新增 [[KnowledgeBase/concepts/混合精度与模型量化]] 与 [[KnowledgeBase/sources/model-precision-quantization-summary|来源摘要]]；更新 [[KnowledgeBase/entities/NVIDIA]]、[[KnowledgeBase/entities/CUDA]]、[[KnowledgeBase/maps/domain-map]] 与 `KnowledgeBase/INDEX.md`。
- 关键边界：文章中的 70B 显存示例仅估算权重，未包含 KV Cache、运行时和系统开销；NVFP4 性能/精度数据保留为来源中的 NVIDIA 评测语境。


## [2026-09-06] ingest | KV Cache 从原理到集群调度

- 读取原始剪藏《KV Cache - 一图看懂 KV Cache：从诞生到集群调度》，清洗后归档至 [[AI/企业级私有化大模型/KV Cache-从原理到集群调度]]。
- 保留完整技术内容：KV Cache 与 Attention、Prefill/Decode、TTFT/TPOT、生命周期、显存估算、HBM/SRAM 带宽瓶颈、Prefix Cache、Prefill/Decode 分离与集群负载均衡；移除作者宣传性署名和尾部引流文案。
- 通过 PicGo 的 githubPlus/github-images 图床上传原文 5 张图片，并将正文图片替换为对应的 `raw.githubusercontent.com/hangx969/upload-images-md/main/20260906154809144.png`～`...148.png` 链接。
- 新增 [[KnowledgeBase/sources/kv-cache-inference-cluster-summary|来源摘要]] 与 [[KnowledgeBase/concepts/KV Cache|KV Cache 概念页]]；更新 vLLM 部署笔记、混合精度概念页、AI/index.md，并在知识库索引和领域地图追加本次新增条目。
- 关键边界：原文 O(n²)→O(n) 与 70B×128K×64 人≈640 GB 等数字是入门级简化/示例；生产容量规划需结合 GQA/MQA、KV 精度、框架块管理、运行时、通信开销与压测。


## [2026-09-07] restructure + ingest | Effective HTML 页面工作流合并

- 经用户授权，将 `AI/AI-视觉/effective-html-AI直出HTML工具实测.md` 的内容按逻辑整合进 `AI/AI-视觉/Effective-HTML-Agent页面工作流.md`；保留第二篇原文件，第一篇新增第二篇来源 URL 和更新时间元数据。
- 合并后的文章统一了两个 Skill 口径：三个核心交付入口（`html` / `html-diagram` / `html-plan`）与六个阶段化 Skill（补充 `html-wireframe` / `html-prototype` / `design-artifact`）；补充 HTML vs Markdown 适用边界、`html-effectiveness` 20 个参考范本、实测交互特性和同类工具定位表。
- 新建 [[KnowledgeBase/sources/effective-html-agent-workflow-summary|Effective HTML Agent 页面制作与 HTML 交付工作流来源摘要]]。
- 更新 [[KnowledgeBase/concepts/提示词工程|提示词工程]]、[[KnowledgeBase/entities/Claude-Code|Claude Code]]、[[KnowledgeBase/entities/Codex|Codex]]、[[KnowledgeBase/maps/ai-workflow-map|AI 工作流专题地图]] 和 `KnowledgeBase/INDEX.md`。


## [2026-09-07] update | Effective HTML 安装兼容说明

- 在合并后的文章和来源摘要中补充 `skills.sh` 登记、Claude Agent Skill 格式、`.claude-plugin` 兼容性及 Claude Desktop 加载方式。

## [2026-09-07] ingest | KServe 部署 vLLM 与 InferenceService

- 读取原始剪藏《一个 Deployment 就能跑 vLLM，为什么还需要 KServe？》，清洗后归档至 [[AI/企业级私有化大模型/一个 Deployment 就能跑 vLLM，为什么还需要 KServe？]]。
- 移除作者宣传、往期回顾、关注转发引导和装饰性尾图；保留 KServe 定位、部署模式选择、cert-manager、Envoy Gateway、KServe 0.18.0、PVC 模型加载、InferenceService YAML、状态验证与 OpenAI 兼容 API 调用等完整技术内容。
- 新增 [[KnowledgeBase/sources/kserve-vllm-inferenceservice-summary|来源摘要]]；更新 [[KnowledgeBase/entities/Kubernetes]]、[[KnowledgeBase/maps/kubernetes-map|Kubernetes 专题地图]]、`AI/index.md` 与 `KnowledgeBase/INDEX.md`。
- 关键边界：vLLM 是推理引擎，KServe 是模型服务编排与控制层；Standard/Knative 属于 InferenceService 部署模式，LLMInferenceService 是独立 API；hostPath PV 仅适合单节点验证。
- `mcp-obsidian` 完成原文读取、新文档写入与日志追加；既有页面因 MCP PATCH 版本不兼容，使用最小本地补丁更新。

## [2026-09-12] ingest | kubectl Client-side Apply 与 Server-side Apply

- 清洗《kubectl apply 背后的真相：为什么 Server-side Apply 正在成为标配》，将技术内容整合进 [[k8s基础-yaml-apply#kubectl apply：Client-side Apply 与 Server-side Apply]]，没有创建重复的主题文章。
- 保留 CSA 三路合并、HPA 静默覆盖案例、SSA 字段所有权、CRD schema、Helm 4 迁移和排障命令；移除关注引导、题库广告和好文推荐。
- 将会被 Obsidian 解析为 HTML 的 `<object>`、`<[]Object>` 类型标记改为行内代码，恢复后续标题与图床图片的 Live Preview 渲染。
- 新增 [[KnowledgeBase/sources/kubectl-server-side-apply-summary|来源摘要]]，并更新 Kubernetes 实体页、基础资源批量摘要、Kubernetes 专题地图和知识库索引。

## [2026-09-12] lint | 未闭合 HTML 标签扫描

- 扫描 vault 中的 Markdown，排除 frontmatter、围栏代码、行内代码、HTML 注释、自闭合标签和允许省略结束标签的元素。
- 修复后的 `k8s基础-yaml.md` 已通过检查；其两张图床图片在 Obsidian Live Preview 中均成功生成图片组件。
- 其余共发现 12 个文件、33 个未闭合标签候选，详见 [[KnowledgeBase/maintenance/unclosed-html-tags-2026-09-12|扫描报告]]；本次按用户要求仅列出，未批量修改这些文件。

## [2026-09-12] update + lint | 修复全库未闭合 HTML 标签

- 使用 Markdown 语法树复核上一轮文本扫描；确认引用块代码围栏中的 `<pdb-name>`、`<module>`、`<<EOF` 等属于误报，因此保留原始可复制命令和代码输出。
- 修复 6 个实际受影响文件中的 12 个标签：AIOps K8s 编排 Skill、Claude Fable 5 system prompt、k9s 快捷键表、kubeadm 配置说明、HPA/CA 命令和 Linux `stat` 命令。
- 精确扫描额外发现并修复第一轮遗漏的 k9s `<esc>` 与 `stat <filename>`；第一轮列出的 7 个代码围栏文件无需修改。
- 全库 Markdown-aware 复扫结果：`FILES=0`、`OPEN=0`、`CLOSE=0`。同步更正 [[KnowledgeBase/maintenance/unclosed-html-tags-2026-09-12|维护报告]] 与知识库索引。


## [2026-09-12] ingest | kubectx/kubens 多集群上下文切换

- 读取原始剪藏《多集群切换乱？用kubectx》，将其技术内容整合进既有 [[Docker-Kubernetes/k8s-installation-management/k8s多集群kubeconfig管理#kubectx 与 kubens：多集群快速切换]]，未在 k8s-basic-resources 下创建重复主题文章。
- 保留并整理 context 原理、跨平台安装、kubectx/kubens 用法、fzf 交互选择、kube-ps1 动态着色、多 kubeconfig 合并和生产防误操作清单。
- 依据 Kubernetes 与 kubectx/kube-ps1 官方文档完成技术校正：KUBECONFIG 同名键采用“第一个文件胜出”；无参数交互选择依赖 fzf；动态颜色使用 `KUBE_PS1_CTX_COLOR_FUNCTION`；移除固定旧版本下载方式。
- 新增 [[KnowledgeBase/sources/kubectx-kubens-multi-cluster-summary|来源摘要]]；更新安装管理批量摘要、Kubernetes 实体、Kubernetes 专题地图、Docker-Kubernetes 入口和知识库索引。
- 在 [[Docker-Kubernetes/k8s-basic-resources/k8s基础-认证-授权-准入#kubeconfig文件]] 增加跨目录入口，确保从用户建议的基础资源主题也能定位到整合文章。


## [2026-09-12] ingest | Kustomize Base 与 Overlay 多环境配置

- 读取原始剪藏《Kustomize 入门：用 Base 和 Overlay 管理 Kubernetes 多环境配置》，清洗后归档至 [[Docker-Kubernetes/k8s-CICD/Kustomize/Kustomize入门-Base与Overlay多环境配置]]。
- 保留多环境配置漂移背景、Kustomize 能力边界、Base/Overlay 模型、六个常用字段、构建/差异检查/部署命令和版本说明；移除作者署名、下篇预告与公众号分类尾注。
- 修复剪藏产生的重复编号、项目符号和无语言代码围栏，并与既有 [[Docker-Kubernetes/k8s-CICD/Kustomize/k8s配置定制工具-kustomize|Kustomize 综合笔记]] 建立关联。
- 新增 [[KnowledgeBase/sources/kustomize-base-overlay-summary|来源摘要]]，补全 [[KnowledgeBase/entities/Kustomize|Kustomize 实体页]]，更新 CI/CD 批量摘要、Kubernetes 实体、Kubernetes 专题地图、工具地图与知识库索引。
- 依据 Kubernetes 官方文档和 Kustomize 当前源码核对版本边界：新项目优先使用 `resources`、`labels`、`patches`；独立版与 `kubectl` 内置版的字段支持应以实际版本为准。

## [2026-09-13] ingest | Dragonfly + Harbor P2P 镜像与大文件分发

- 读取原始剪藏《Dragonfly + Harbor：为什么 AI 集群越来越需要 P2P 镜像分发？》，清洗后归档至 [[Docker-Kubernetes/harbor/Dragonfly与Harbor-P2P镜像分发]]。
- 保留 Harbor 集中拉取瓶颈、文件分块、Peer 交换、新旧 Dragonfly 架构、测试数据、适用场景、优缺点和 AI 模型分发等技术内容；移除作者署名和公众号目录尾注。
- 将剪藏后挤成单行的字符流程图恢复为 15 个 Mermaid 图，并校正 Scheduler 控制面、Peer/Seed Peer 数据面及 Manager 可选部署关系。
- 通过本机 PicGo 的 githubPlus/github-images 配置上传原文 13 张图片，正文已全部替换为 `raw.githubusercontent.com/hangx969/upload-images-md` 图床链接。
- 新增 [[KnowledgeBase/sources/dragonfly-harbor-p2p-distribution-summary|来源摘要]]、[[KnowledgeBase/entities/Dragonfly|Dragonfly 实体页]] 和 [[KnowledgeBase/concepts/P2P分发|P2P 分发概念页]]，补全 [[KnowledgeBase/entities/Harbor|Harbor 实体页]]，并更新 Kubernetes/Docker 实体、专题地图、工具地图及索引。
- 根据 Dragonfly v2 与 Harbor 官方文档补充版本边界：Dragonfly v1 已归档且与 v2 不兼容；Harbor P2P Preheat 依赖外部 P2P 引擎，版本组合需按官方兼容矩阵确认。
- 验证校正：本文实际包含并通过解析的 Mermaid 流程图为 17 个，上述“15 个”以本条为准更正。


## [2026-09-13] ingest | 大模型本地部署 Runtime 选型与离线交付

- 读取原始剪藏《大模型本地部署到底怎么选？Ollama、vLLM、SGLang、vLLM-Omni 一次讲透》，清洗后归档至 [[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]]。
- 将原文 51 个重复、过短的章节收敛为 11 个工程主题，保留 ModelScope 下载、目录规划、rsync/tar、Docker 离线镜像、四种 Runtime、显存参数、容器粒度和模型平台架构等技术内容。
- 将失效的字符流程图恢复为 13 个 Mermaid 图；Obsidian 内置解析验证为 13/13 通过。
- 原始剪藏不含 Markdown/HTML 图片引用或图片 URL；原公众号页面拒绝自动提取，因此本次没有可交给 PicGo 上传的原图，未虚构或替换图片。
- 依据 vLLM、SGLang、vLLM-Omni 与 ModelScope 官方文档补充版本与安全边界：显存比例不是硬隔离、PD 分离需要 KV 传输、Omni 模型支持按版本核对、远程代码仅对可信固定 Revision 启用。
- 新增 [[KnowledgeBase/sources/local-llm-runtime-selection-summary|来源摘要]]、[[KnowledgeBase/entities/Ollama|Ollama]]、[[KnowledgeBase/entities/vLLM|vLLM]] 和 [[KnowledgeBase/entities/ModelScope|ModelScope]] 实体页；同步更新 Docker/CUDA/NVIDIA/KV Cache、AI 与工具地图及知识库索引。
- 验证结果：正文围栏成对、13 个 Mermaid 全部通过解析、新增核心页面无未解析 wikilink、`git diff --check` 通过。

## [2026-09-15] ingest | cert-manager Helm 部署与 TLS 自动化整合

- 读取原始剪藏《K8s cert-manager实战：让TLS证书自动签发和续期》，按证书生命周期主线整合进 [[cert-manager 实战：Helm 部署、TLS 自动签发与续期|cert-manager 实战：Helm 部署、TLS 自动签发与续期]]。
- 合并重复的 cert-manager 定位、Certificate/Ingress 接入和续期说明，同时完整保留 OCI 与本地 Chart 安装、自签名 Pod TLS、HTTP01/DNS01、Cloudflare、Azure DNS Workload Identity、通配符、PKCS#12、Helm 配置管理、故障案例和回滚命令。
- 将原文字符流程重绘为 6 个 Mermaid 图，覆盖人工与自动化流程、资源关系、HTTP01/DNS01 选型、ACME 校验、Staging 到 Production 和自动续期；Obsidian 内置解析器验证为 6/6 通过。
- 新增 [[KnowledgeBase/sources/cert-manager-tls-automation-summary|来源摘要]]、[[KnowledgeBase/entities/Cert-Manager|Cert-Manager 实体页]] 和 [[KnowledgeBase/concepts/证书管理|证书管理概念页]]；同步更新安全认证批量摘要、Kubernetes/Helm/Ingress 实体页、Kubernetes/工具地图与知识库索引。
- 验证结果：目标正文与 3 个新增知识页 frontmatter 可解析、核心页面无未解析 wikilink、代码围栏成对、Obsidian 渲染侧未捕获错误、`git diff --check` 通过；支持页中仍存在历史断链，本次未新增。


## [2026-09-15] restructure | HPA、VPA 与 Scale-to-Zero 三文整合

- 将 `Docker-Kubernetes/k8s-scaling/k8s-HPA-VPA.md`、`helm部署vpa.md` 与 `k8s-1.37原生HPA-Scale-to-Zero实战.md` 整合为一篇主文档，按“选型 → 指标基础 → HPA 原理与实战 → Scale-to-Zero → VPA 部署与实战 → 协同治理”重排章节。
- 保留原有 HPA CPU/内存/PHP 实战、Metrics Server 完整清单、VPA Helm/脚本部署、nginx/hamster/MySQL 案例、推荐算法、自定义 Recommender、Scale-to-Zero 冷启动与 KEDA 迁移等技术内容；合并重复定义和配置。
- 对照官方文档校正 HPA 公式与默认周期、Kubernetes 1.37 `HPAScaleToZero` 状态、Scale-to-Zero 指标目标值，并补充 VPA In-place 模式及 `Auto` 弃用说明。
- 旧的两个文件保留为兼容入口并指向主文档章节；同步更新来源摘要、Kubernetes/Helm/Prometheus 实体页、Kubernetes 地图和 Wiki 索引。
- 验证结果：主文档与兼容入口 frontmatter 可解析，96 条代码围栏成对，20 个 YAML 代码块均通过语法解析，43 个 Markdown 标题被 Obsidian 正确识别；主文档、兼容入口和专项来源摘要均无未解析 wikilink，Obsidian 未捕获渲染错误，`git diff --check` 通过。

## [2026-09-15] restructure | KEDA、HPA 与 KServe 扩缩容文章整合

- 将 `k8s-基于KEDA的弹性能力.md`、`KEDA-vs-HPA-2026终极对比-v1.36缩零.md` 与 `KServe+KEDA实战-基于请求指标实现服务自动扩缩容.md` 的技术内容整合到 [[Docker-Kubernetes/k8s-scaling/k8s-基于KEDA的弹性能力|Kubernetes KEDA 事件驱动自动扩缩容：原理、选型与 KServe 实战]]。
- 按“需求与架构 → HPA/KEDA/Scale-to-Zero 边界 → 资源模型 → 部署 → Cron/RabbitMQ/MySQL/Redis/Kafka → KServe + vLLM → 生产治理”重排章节，保留命令、YAML、指标链路和实测扩缩容过程。
- 依据 Kubernetes 与 KEDA 官方资料校正 `HPAScaleToZero` 为 Kubernetes 1.37 Beta、KEDA 0↔1 与 HPA 1↔N 的职责边界，以及 KEDA fallback 的归属；同步更新 Prometheus、KServe、Kubernetes 地图和索引引用。
- 两篇旧正文的删除已通过 mcp-obsidian 发起，但因当前环境的 MCP 自动审批额度耗尽而暂未执行；待额度恢复后删除：`KEDA-vs-HPA-2026终极对比-v1.36缩零.md`、`KServe+KEDA实战-基于请求指标实现服务自动扩缩容.md`。
- 当前校验：主文档 19 个 YAML 代码块解析通过，围栏成对，Obsidian 识别 59 个标题，无未解析 wikilink，`dev:errors` 无错误，`git diff --check` 通过。


## [2026-09-15] restructure | Istio 文档整合

- 将 `helm安装istio.md`、`k8s部署istio(1.13.1).md`、`Istio-Sidecar-vs-Ambient.md` 合并到 [[Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio|Istio 服务网格：架构、部署与精细化流量治理]]
- 以原 `k8s精细化流量管理-istio` 的 Bookinfo 与流量治理流程为主线，补充 Helm、历史版本部署、Sidecar/Ambient 选型、超时与重试，并修正可执行配置中的字段与缩进
- 删除合并后的三篇旧文，更新 Istio/Helm 实体页、服务网格概念页、主题地图、来源摘要和发布策略交叉引用
- 验证：主文 Frontmatter、27 个 YAML 代码块和代码围栏通过检查；主文无未解析 wikilink；Obsidian 控制台无错误


## [2026-09-15] lint | Istio 文档整合验证

- 目录核对：`k8s-networking-service-mesh/` 共 7 篇，三篇被合并旧文均已删除
- 语法检查：综合指南 Frontmatter 可解析，27 个 YAML 代码块解析通过，Markdown 代码围栏闭合，`git diff --check` 通过
- 链接检查：综合指南及本次更新的 Wiki 页面无未解析链接；`KnowledgeBase/log.md` 保留 1 条指向旧 Sidecar/Ambient 文件的历史操作记录，按日志仅追加规则未回写
- Obsidian 检查：受影响页面元数据已刷新，开发者控制台无错误

## [2026-09-15] restructure | Codex 使用技巧和最佳实践

- 将 5 篇 Codex 文章整合为 `AI/Codex/Codex-使用技巧和最佳实践.md`，按配置基线、需求澄清、Token 优化、HANDOFF 和多 Harness 协作重组，并保留配置字段、命令、实测数据与适用边界
- 删除 5 篇已合并的旧文章；创建新的来源摘要，并将旧体验设置摘要改为已合并跳转页
- 更新 `KnowledgeBase/INDEX.md`、`KnowledgeBase/maps/tool-map.md`、`KnowledgeBase/maps/ai-workflow-map.md` 和 `KnowledgeBase/entities/Codex.md`

## [2026-09-15] restructure | Harbor 部署与使用指南

- 将 Docker Compose 部署、Kubernetes Helm 部署、镜像推拉、containerd 接入、Helm OCI Chart 和 TLS 配置整合到 [[Harbor 部署与使用指南|Harbor 部署与使用指南]]，合并重复内容并标注历史版本及失败实验边界
- 删除已被合并的 `Docker-Kubernetes/harbor/helm部署harbor.md`，同步更新 Harbor、Helm、工具地图和 K8s 杂项来源摘要中的引用

## [2026-09-26] restructure | Azure 故障排查工具

- 将 Browser Trace、Fiddler、IO Monitor、PerfMon/ProcessMon 与 Postman 五篇笔记整合为 [[12_Azure 故障排查工具]]，按浏览器与 HTTP、API、Windows 性能和磁盘 I/O 重排；保留原有 10 张 GitHub 图床图片及技术命令。
- 删除五篇已合并的旧笔记，更新 [[KnowledgeBase/entities/Azure]]、[[KnowledgeBase/maps/cloud-platform-map]]、[[KnowledgeBase/sources/azure-batch-summary]] 和 [[KnowledgeBase/inventory/repository-inventory]] 中的导航与摘要。

## [2026-09-26] restructure | Ubuntu 22.04 Slurm 22.05.11 安装笔记整合

- 将测试环境与 H800 生产环境两篇安装记录整合为 [[HPC/Ubuntu2204-slurm-22.05.11-安装指南]]，分别保留拓扑、完整配置与操作步骤，共用作业测试说明。
- 修正生产环境 Epilog 配置项、`zprodtest` 分区名称、SSH 地址笔误及脚本权限；对仍需现场验证的历史命令和配置标注适用条件。
- 删除两篇旧文，同步更新 HPC 索引、相关笔记引用、Slurm 实体页、来源摘要、地图和盘点数量。

## [2026-09-26] update | Slurm 安装指南安全与示例修订

- 将 [[HPC/Ubuntu2204-slurm-22.05.11-安装指南]] 中的 MUNGE 密钥生成/分发改为一次生成、受限暂存与 `munge:munge 0400` 安装，去除原有世界可写步骤。
- 将 SlurmDBD 数据库权限收敛到 `slurm_acct_db.*`，用口令占位值替换固定示例密码；修正单节点作业命令，并加固 Prolog/Epilog 的路径处理。
- 保留生产 Epilog 基于日志判断抢占的历史逻辑，标明需在目标集群验证。

## [2026-09-26] restructure | Ubuntu 22.04 Slurm 22.05.11 与 23.11.4 安装记录合并

- 将 22.05.11 测试与 H800 生产部署、23.11.4 源码构建 deb 包实验部署合并为 [[HPC/Ubuntu2204-Slurm-安装指南]]；保留各自拓扑、完整配置、命令、环境准备、作业示例与参考资料，合并重复的作业命令说明。
- 修正 23.11.4 原记录中残留的 `;done`，按节点角色使用 `apt` 安装构建包，并将与 `debug`/`uc1` 拓扑不符的验收命令改为可对应当前配置的示例；对 4 GB 与 `RealMemory=5886` 冲突、缺少记账配置等未能核实项保留原值并标注。
- 删除两篇旧文，更新 HPC 索引、Slurm 实体、来源摘要、主题地图与盘点数量，并修复相关笔记引用。

## [2026-09-26] update | Ubuntu 22.04 Slurm 安装指南正文清理

- 清理 [[HPC/Ubuntu2204-Slurm-安装指南]] 中关于来源合并与修订过程的叙述，将相关提醒改写为部署条件、配置差异和现场核对事项。
- 将 `salloc` 的示例输出调整为文中 `cpu` 分区和 `c1` 节点；保留命令、配置、参数与安全边界。

## [2026-09-26] restructure | PBS 笔记合并

- 将 `HPC/PBS-cases.md` 的三则故障案例合并到 `HPC/PBS.md`，统一章节与列表格式，并核对技术表述和图片链接。
- 将原案例页改为跳转页，更新 HPC 目录及知识库中的相关引用；保留受保护 Slurm 原始笔记中的旧链接，由跳转页继续解析。

## [2026-09-26] update | 删除 PBS 案例跳转页

- 按用户授权删除 `HPC/PBS-cases.md`；三则案例已完整合并在 `HPC/PBS.md`。
- 更新 HPC 目录和文档盘点。受保护的 `HPC/CentOS7-slurm23.02-二进制安装.md` 仍含旧链接，待单独授权后修复。

## [2026-09-26] restructure | Linux-Shell 文章合并

- 将 `ssh远程执行多个命令.md` 并入 [[Linux-Shell/ssh连接#远程执行多个命令|SSH 连接]] 并删除旧文；将 [[Linux-Shell/Ubuntu基础操作|Ubuntu 基础操作]] 中重复的安全补丁章节改为指向 [[Linux-Shell/Ubuntu-unattended-upgrade管理|安全补丁专文]]。
- 将 MacBook 笔记中重复的 Oh My Zsh 主题与插件说明集中到 [[Linux-Shell/配置zsh终端|Zsh 终端配置]]；保留 macOS 开发工具内容，整理目录及相关知识库引用。
- 核对并保留 GitHub 图床图片链接；修正 Ubuntu OpenSSH 安装命令、Zsh 配置示例和 unattended-upgrades 默认来源表述。

## [2026-09-26] restructure | Ubuntu 系统管理文章合并

- 将 `Ubuntu-修改启动内核.md`、`Ubuntu安装显卡驱动.md` 和 `Ubuntu-unattended-upgrade管理.md` 的操作内容整合到 [[Linux-Shell/Ubuntu基础操作]]，按 GRUB、NVIDIA 驱动和安全补丁分章，并删除三篇旧文。
- 更新 Linux-Shell 索引、知识库入口、运维地图、来源摘要、文档盘点和 README 的篇数与引用；此前日志保留为历史记录。
- 修正 Nouveau 配置、库路径变量、驱动变体说明，以及自动更新配置和定时任务中的不准确步骤；保留原有命令示例和配置目的。

## [2026-09-26] restructure | Linux 运维实操专题合并

- 将 Zsh、direnv、终端代理、screen、系统信息、inotifywait、nmcli、SSH 和 Samba 九篇操作笔记并入 [[Linux-Shell/Linux-learning-notes#Linux 运维实操专题|Linux 学习笔记的实操专题]]，按主题重排章节并删除旧文；保留三处 GitHub 图床链接。
- 更新 Linux-Shell 索引、知识库入口、来源摘要、专题地图、概念页、文档盘点及其他有效引用；目录现有 11 篇笔记（含索引共 12 个 Markdown 文件）。
- 修正 direnv 的 Zsh hook、inotifywait 执行命令示例、SSH 密钥与 SCP 示例、Azure SSH 端口与防火墙/SELinux 步骤等错误；历史日志保持追加，不改写既有条目。

## [2026-09-28] restructure | Kubernetes 配置与镜像管理文章归档

- 将 ConfigMap/Secret 基础、Config Syncer 和 Reloader 三篇文章归入 `Docker-Kubernetes/k8s-configMap-secret/`。
- 将原 `Docker-Kubernetes/harbor/` 的两篇文章与 Dragonfly Helm 部署文章归入 `Docker-Kubernetes/k8s-image-management/`；Pact Broker 归入 `Docker-Kubernetes/k8s-CICD/`。
- 更新 Docker-Kubernetes 目录、知识库来源摘要、专题地图、实体页和盘点中的现行路径引用。

## [2026-09-28] restructure | Prometheus 原生部署文档合并

- 将 `k8s监控Prometheus(v2.2.1).md` 与 `k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5).md` 合并为 [[Docker-Kubernetes/k8s-monitoring-logging/Kubernetes原生部署Prometheus与Grafana]]，删除重复旧稿；保留 HA、应用 Exporter、Pushgateway、Grafana 与全部 11 个 GitHub 图片 URL。
- 更新 `Docker-Kubernetes/index.md` 及 KnowledgeBase 的 Prometheus、Grafana、Observability、tool-map、来源摘要和目录盘点引用。
- 按官方文档修正原例中的过宽 RBAC、Node Exporter 宿主机采集参数、Prometheus NFS TSDB、Grafana 匿名 Admin 与 PVC 命名空间、Pushgateway 用途和配置热加载说明。

## [2026-09-28] restructure | Grafana v5 与 kube-state-metrics 内容整合

- 将 `Docker-Kubernetes/k8s-monitoring-logging/k8s部署grafana(v5.0.4).md` 的独有内容并入 [[Docker-Kubernetes/k8s-monitoring-logging/Kubernetes原生部署Prometheus与Grafana]]，删除重复的旧版 Grafana Deployment 文档；保留旧版 UI、Dashboard 排障、KSM 监控步骤及 5 个 GitHub 图片 URL。
- 按 kube-state-metrics 上游文档改正旧版工作负载 RBAC 的 `extensions` API 组、部署版本选择及 Service 注解与本文 Prometheus 发现配置的衔接；更正 `docker load -i` 镜像名参数和旧文对 Grafana 告警能力的过时概括。
- 更新 Docker-Kubernetes 目录及 KnowledgeBase 的 Grafana、Observability、工具地图、来源摘要和盘点引用。

## [2026-09-29] lint | 全库健康检查与 README 刷新

- 按 CLAUDE.md 六个维度检查 826 个 Markdown 文件，其中 KnowledgeBase 161 页、3,513 条 wikilink、169 条 Markdown 链接；结果见 [[KnowledgeBase/maintenance/wiki-lint-2026-09-29|Wiki 健康检查 2026-09-29]]。
- 修复 41 条由改名、合并或删除导致的失效链接，每条都经 git 历史确认了唯一现行路径，涉及 INDEX、repository-inventory、kubernetes/cloud-platform/ai-workflow 地图、提示词工程、Claude-Code、Codex 和 Effective HTML 来源摘要；另修复 INDEX 中 4 条在 GitHub 上失效的相对链接。
- INDEX：移除 4 个已删除维护报告的链接，补录 Volume Health Monitor 来源摘要；领域表按 git 实测刷新篇数，并补充 Git、SoftwareTesting、C++；把"全部摄入"的说法改为实际覆盖情况（19 篇未被引用）。
- README：按 git 实测刷新篇数（381 篇笔记、18 个领域、162 个知识库文件），修正 Claude Code 指南链接、`INDEX.md` 文件名、AI 与 Docker-Kubernetes 目录树；`AI/RAG/` 根目录下 3 篇独立文章改计为学习笔记，嵌入内容由 283 篇改为 280 篇。
- 以下问题只记录在报告中，本次未修改：257 条红链、30 条指向已清理剪藏的链接（待约定写法）、14 对需要复核的来源摘要、各页文档计数不一致、frontmatter 和模板缺口，以及原始来源层的链接问题。

## [2026-09-29] update + lint | 按用户确认处理健康检查发现

- 剪藏暂存目录：按用户要求删除知识库与原始来源中的全部引用，包括知识库页面 30 条链接和原始来源 15 个文件。log.md 历史条目中的 93 处路径和链接改写为剪藏标题纯文本，记录的操作事实不变；`.gitignore` 与站点构建脚本中的排除规则保留。
- 篇数：统一为"git 跟踪的 Markdown、不含各目录 index.md"口径，全库共 18 个领域、363 篇学习笔记。已修正 README、INDEX、8 张主题地图、相关实体页与概念页、批量摘要的"文档数量"、领域内容特点分析和 3 篇分析页；Kubernetes 专题地图与工具地图补全了漏列文档；[[KnowledgeBase/inventory/repository-inventory|全库文档盘点]]按当前仓库重新生成。本条取代上一条日志中按含 index.md 口径给出的 381 篇等数字。
- 过时摘要：逐对复核后，删除 `sources/Claude-Code扩展体系-summary.md`、`sources/多智能体协作-summary.md` 以及 AI/OpenClaw 批量摘要中的"提示词"条目，并清理全部引用；其余被标记的摘要经核对未过时，予以保留。
- 页面格式：30 页补 sources，34 页补 aliases；26 个实体页和 23 个来源摘要补齐模板章节，其中批量摘要把"整体概述"改为"摘要"，并新增"关键知识点"和"值得注意"。补写过程中发现 21 处与现行原文矛盾或已过时的说法，均已改正或删除。
- 原始来源断链（用户授权）：修复 Claude Code 基础指南、HPC、Jenkins、Python、K8s 1.33 等笔记中的失效链接、锚点、同名歧义、作者字段和 Typora 本地图片引用；嵌入的 RAG 项目文档未改。
- 孤儿页：删除 `sources/codex-两个设置提升体验-summary.md`；log.md 中指向已删除页面的链接改为行内代码。
- 结果见更新后的 [[KnowledgeBase/maintenance/wiki-lint-2026-09-29|Wiki 健康检查 2026-09-29]]：知识库内只剩 257 条红链；原始来源层只剩 22 条，均在嵌入项目文档中；log.md 中剩 16 条历史链接。

## [2026-09-30] update | 原始笔记明文凭据改为占位符

- 按用户确认，将 3 篇原始笔记中的明文实验凭据改为占位符：[[Docker-Kubernetes/k8s-UI-tools/rancher(v2.6.4)管理k8s集群]] 的 bootstrap 密码、admin 密码和集群导入令牌；[[Azure/Jfrog-artifactory-Azure]] 中 4 处 PostgreSQL 密码；[[Docker-Kubernetes/k8s-CICD/Gitlab/二进制安装Gitlab(17.9.8)]] 的 root 密码。
- 正文中的占位符放进行内代码，避免被当作 HTML 标签隐藏。
- 更新 [[KnowledgeBase/maintenance/wiki-lint-2026-09-29|Wiki 健康检查 2026-09-29]] §8 第 4 条的处理状态。
- 原值仍保留在 git 历史中。


## [2026-10-02] ingest | Terraform 基础系列扩充

- 根据用户明确授权，改写 IaC/terraform 原有基础、容器管理与 terraform-docs 三篇笔记，新增 12 篇正文和 README 学习路线，形成 15 篇正文 + 1 个导航；按 k8s-basic-resources 的专题、完整配置、步骤解释和实验方式组织。
- 搜索 GitHub 学习提纲、社区最佳实践及官方教程代码，并结合 Terraform/Provider 官方文档重写中文内容；逐篇列出出处和版本范围，修正 Docker image_id、Helm 3.x 配置、Azure Backend use_cli 版本及 S3 锁文件示例。
- 新增 14 篇来源摘要并更新容器管理摘要，更新 Terraform 实体页，新增基础设施即代码、Terraform 状态管理、Terraform 模块化概念页和 Terraform 学习地图；仅局部修改总索引、工具/领域地图及杂项摘要中的 Terraform 内容，全库篇数保留为原有日期的盘点快照。
- 40 个页面经 Obsidian 写入后逐篇回读一致；83 个 HCL 代码块通过 Terraform fmt 解析检查，YAML、代码围栏和新增内部链接检查通过，98 个外部链接可访问；最小 Helm Chart 通过离线 lint 和 template 渲染。
- 本次没有运行 terraform init、terraform validate、plan、apply 或原生测试，没有访问云账号和集群；格式/静态检查及 Helm 离线渲染不表示平台部署或业务验收已通过。

## [2026-10-02] update | Terraform 分题写作与统筹验收

- 三名 GPT-6.1 Sol 子 Agent（推理等级 Max）分别修订语言基础、Provider 与 State、模块与项目协作三组内容，共 15 篇文章；父级独立验收后统一写回。学习入口为 [[IaC/terraform/README|Terraform 基础系列学习路线]]。
- 补齐实验变更、预期观察、清理和练习；修正 nullable 默认值、敏感 output 明文读取、moved 与参数替换的边界，并统一模块别名、测试接口及 terraform-docs 调用示例。
- 同步 [[KnowledgeBase/sources/iac-terraform-variables-outputs-summary|变量摘要]]、[[KnowledgeBase/sources/iac-terraform-count-for-each-summary|循环摘要]]、[[KnowledgeBase/sources/iac-terraform-modules-summary|模块摘要]]、[[KnowledgeBase/sources/iac-terraform-docs-summary|文档生成摘要]]。
- 独立检查通过：91 个 HCL 块的格式与两套解析器、96 个 Shell 块的语法、Markdown 围栏/表格/内部链接、跨篇输入输出及 Provider 映射；33 个新增外部来源链接可访问。Helm Chart lint 与副本数 1/2 的离线渲染通过。
- 通过 Obsidian MCP 写回并逐文件读回全部 19 个变更文件，内容与验收稿完全一致。未运行 Terraform init、validate、plan、apply 或 test，未进行云、Docker 或集群部署；terraform-docs 实际生成未验证。

## [2026-10-02] restructure | Terraform 中文标题与学习顺序编号

- 按 [[IaC/terraform/README|系列学习路线]] 将 15 篇正文命名为 `01_terraform_中文名` 至 `15_terraform_中文名`；文件名、正文一级标题和 frontmatter title 一致。
- 同步 README、上级 IaC 索引及知识层引用，共 43 个文档、196 处正文引用；保留技术内容、代码示例、其余元数据和历史日志。
- 逐文件 Obsidian MCP 读回核对通过，15 个旧路径已移除，新增文章路径均可解析；文件排序、标题一致性及 git diff --check 通过。

- Obsidian 阅读视图验收通过：学习路线表格保持三列，编号标题正确显示，15 个新文章路径均能通过元数据缓存解析。

## [2026-10-02] update | Terraform 中文表达润色

- 按 humanizer-zh skill，由三名 GPT-6 Luna 子 Agent（推理等级 High）分组审阅 Terraform 专题的 35 个页面：15 篇正文、README、15 篇来源摘要、实体页、两篇概念页和学习地图；父级逐处验收后写回。
- 11 篇调整了别扭句式、重复说明和含糊指代，其余 24 篇保留原文；退回并修正了候选稿中的无谓扩写及限定条件变化，保留技术原意和确定程度。
- 文件名、标题、frontmatter、代码块、行内代码、表格、链接、数值与列表顺序保持一致；35 个页面经 Obsidian MCP 读回，与验收稿完全一致。
- 本轮仅检查文档内容和变更范围，未运行 Terraform init、validate、plan、apply 或 test。学习入口为 [[IaC/terraform/README|Terraform 基础系列学习路线]]。

## [2026-10-02] update | Terraform 示例改为 AliCloud 生产结构

- 调整 `IaC/terraform/` 的 15 篇正文及 README，以 `alicloud-operations` 的临时权限输入、OSS Bucket/ACL、CMS 告警模块、TFE remote Backend 和 ACK/Kubernetes/Helm 关系替换原平台示例；保留编号、文件名和中文学习顺序。
- 由 3 个 GPT-6 Luna High 子 Agent 分组改写，统筹验收后写回 36 个页面：正文与 README、15 篇来源摘要、Terraform 实体页、2 个概念页、主题地图和 INDEX 的 Terraform 条目。生产片段、脱敏裁剪与教学新增测试/CI 均标明范围；账号、角色、资源 ID、内部域名、联系人及凭据用占位符代替，表达按 humanizer-zh 核对。
- 70 个 HCL、62 个 Shell、3 个普通 YAML 代码块及策略模板语法检查通过；249 个内部引用和 51 个生产路径引用可定位，无生产敏感值命中。ACK 示例 Chart 通过离线 Helm lint 与两组 template 渲染，覆盖副本 1/2、Service 端口 80/8080及 checksum 变化；Obsidian 阅读视图表格和链接检查通过。
- 36 个页面经 MCP 全文写回并逐批回读完全一致，Git diff 空白检查通过。244 份生产参考文件哈希及生产 Git 状态保持原样；未执行 Terraform init/validate/plan/apply/test，未访问 TFE、云端或集群。真实 Provider/API 行为、集群认证、镜像拉取及部署仍未验证。

## [2026-10-03] create | GitHub Pages 构建流程复现文档

- 新增 [[KnowledgeBase/analysis/github-pages-mkdocs-material-quartz|GitHub Pages：MkDocs Material 与 Quartz 4]]，记录两套固定版本、配套文件、完整 GitHub Actions workflow、本地构建与预览、Obsidian 链接适配、旧 URL/锚点兼容及验收步骤；区分已提交的 Quartz 基础方案与尚在审阅的主题。
- 确认 `_site/` 是 Pages 上传所需的网站产物，按请求保留；它与 Quartz 缓存均由 Git 忽略。保持现有触发和发布筛选规则，未修改原始来源或 workflow。
- 通过 Obsidian MCP 写入文章和更新 INDEX，并完整回读核对；按 humanizer-zh 润色正文，保留配置、命令、版本、路径及验证边界。文章 frontmatter、代码围栏、Shell 语法与两份 workflow 的发布约定检查通过，原始 Markdown 校验值未变。
- Material 历史配置在临时副本中通过 strict 构建，生成 411 篇文章、18 个主题，仍有既有链接的 info 提示；Quartz 主题记录引用此前的本地构建和界面验收。本次未触发 GitHub Actions、未提交推送、未执行新的 Pages 部署。

## [2026-10-03] restructure | Pages 构建文档移入 Obsidian 原始来源

- 按用户要求将 `KnowledgeBase/analysis/github-pages-mkdocs-material-quartz.md` 移至 [[AI/Obsidian/github-pages-mkdocs-material-quartz|用 GitHub Actions 发布 Obsidian 笔记：MkDocs Material 与 Quartz 4]]；仅调整分类标签和所在目录的发布说明，9 个代码块、命令、版本与配置保持原样。
- 创建 [[KnowledgeBase/sources/github-pages-mkdocs-material-quartz-summary|GitHub Pages 构建来源摘要]]，更新 INDEX、Obsidian 实体、CI/CD 概念、工具地图、AI 工作流地图、领域地图及全库盘点。当前统计纳入本次迁移文件：学习笔记 377 篇、AI 74 篇、Obsidian 6 篇；历史分析快照保留。
- 通过 Obsidian MCP 写入并逐页完整回读，保留同期间对 AGENTS/CLAUDE 规约入口的更新。移除旧文章文件；历史日志按仅追加规约保留原记录，本条提供迁移后的入口。
- 文件移入原始来源后，在纳入 Git 跟踪时参与现有 Pages 构建；本次未修改 workflow、主题代码或其他原始笔记，未手动运行网站构建与部署。

## [2026-10-03] restructure | 项目规约统一为 AGENTS.md

- 以根目录 [[AGENTS|AGENTS.md]] 为统一规约，完整保留原有规则；[[CLAUDE|CLAUDE.md]] 改为仅一行 `@AGENTS.md`，供 Claude Code 导入。
- 同步 README、知识库入口、Obsidian 与 Claude Code 实体页、Obsidian 与 shiji-kb 来源摘要及 2026-09-29 维护报告中的规约引用，注明来源文章和历史检查当时使用 CLAUDE.md 的背景。
- 通过 MCP 写入并完整回读核对；按修改前快照验证原规则完整保留，7 个 YAML frontmatter、代码围栏、16 处新增规约 wikilink 及新增本地 Markdown 链接检查通过，`git diff --check` 通过。验证范围为静态内容与引用。

## [2026-10-03] update | Pages 构建文档收敛为 Quartz 4

- 按用户要求将 [[AI/Obsidian/github-pages-mkdocs-material-quartz|用 GitHub Actions 发布 Obsidian 笔记：Quartz 4]] 整理为 Quartz 专篇，移除另一套生成器的配置、workflow、本地命令、排障与参考资料，保留导出、构建、预览、主题定制、链接兼容和发布验收流程。文章文件名保留，现有链接继续有效。
- 将固定复现基线更新为已推送的仓库提交 `af3c83afb0616ed996ac8a9841cd713fbb44e109`；Quartz 上游仍为 4.5.2，JSON 与 workflow 示例保持原样，本地命令仅更新仓库基线。同步来源摘要、INDEX、Obsidian 实体、CI/CD 概念、工具地图、AI 工作流地图、领域地图和全库盘点中的相关说明。
- 9 个页面通过 Obsidian MCP 写入并完整回读一致，文章已无旧方案内容；4 个代码块、Shell 语法、frontmatter、25 处相关内部链接和 Git diff 空白检查通过。除指定文章外，674 份原始笔记校验值不变，15 份发布工具及 workflow 文件不变；本轮验证范围为文档内容与静态检查。

## [2026-10-03] restructure | Quartz Pages 文档重命名

- 按用户要求将 `AI/Obsidian/github-pages-mkdocs-material-quartz.md` 重命名为 [[AI/Obsidian/github-pages-quartz|用 GitHub Actions 发布 Obsidian 笔记：Quartz 4]]，文章全文与 4 个代码块保持原样；来源摘要同步重命名为 [[KnowledgeBase/sources/github-pages-quartz-summary|Quartz 4 构建来源摘要]]。
- 更新 INDEX、Obsidian 实体、CI/CD 概念、三份主题地图和全库盘点中的路径引用；通过 Obsidian MCP 创建新文件、完整回读并删除旧文件。历史日志按仅追加规约保留，本条提供新入口。
- 675 份原始笔记的内容校验值（含重命名映射）一致，7 份导航更新仅替换路径，17 处相关导航链接可定位，15 份发布工具与 workflow 文件不变；旧路径只保留在历史日志，Git diff 空白检查通过。

## [2026-10-04] query | 全库文章标题审阅

- 按 humanizer-zh 审阅 856 个 Git 跟踪 Markdown 文件的标题，直接核对现有构建器的 412 个发布文件；候选结合引言与相关章节判断，完整清单包含建议保留与另议项。
- 新增 [[KnowledgeBase/analysis/title-review-2026-10-04|文章标题审阅]] 与 [[KnowledgeBase/maintenance/title-audit-2026-10-04|标题审阅清单]]，同步 INDEX。提出 75 条建议：网页 26 条直接精简、23 条需保留副标题/引言；离线 20 条直接精简、6 条需保留副标题/引言。其余 781 个文件保留或另议，原文章标题等待用户确认后修改。
- 原有数字、版本和百分比保留检查通过；人工核对归因、范围与组件列表，并修正一处候选与来源摘要同名的问题。在线首页和三篇文章返回 HTTP 200，确认两篇存在网页顶部长标题与正文短 H1 并列；12 处明确指向候选文件的章节 wikilink 均指向技术小节。
- 两份报告经 Obsidian MCP 写入并完整读回一致，表格、frontmatter 与内部引用静态检查通过；原文章标题、文件名及 675 份原始来源内容未修改，发布工具和 workflow 与扫描前内容一致。未核验原文性能比例/趋势结论，未执行改题构建、移动端视觉验收、部署或 Git add/commit/push。

## [2026-10-04] update | 按确认方案精简网页标题与同步引用

- 按 [[KnowledgeBase/analysis/title-review-2026-10-04|文章标题审阅]] 当前批准表格更新 49 篇发布文章：26 篇直接精简、23 篇保留必要副标题或引言；47 个 frontmatter title、2 个首行 H1 与表格逐字一致，26 条离线标题建议未执行。
- 同步 41 处对应文章 H1；数字、版本、作者归因、完整产品名、组件和适用条件保留。文件名、发布路径、非标题 metadata、代码和技术小节未改。
- 完成 94 个文件的 305 处关联引用显示文字更新，目标路径保持不变。最终验收期间 6 个非获选页面被同期工作区操作删除，其中 4 个包含已更新的 27 处引用；未恢复这些页面，当前仍存在的 90 个引用文件、278 处更新及 146 处 frontmatter 来源引用通过核对，12 处技术章节链接保持原样。
- 49 篇文章保留 92 个旧标题/H1 兼容锚点，未批量增加 aliases；412 篇发布文章的完整 URL 和旧兼容入口不变。三名 GPT-6.1 Sol Low 子 Agent 分批处理与独立复核，主 Agent 完成验收。
- 写入后完整 Obsidian MCP 读回一致，本地 Quartz 构建、49 篇顶部/列表/搜索标题和旧锚点检查通过，首页与两篇文章的搜索、390 px 窄屏显示抽查通过；366 个非 Markdown 文件未变，Git diff 空白检查通过。已知 9 处排除内容链接提示及既有数学/弃用提示见报告。
- 更新报告执行状态、原题清单说明与 INDEX，本条仅追加历史日志。未执行 Git add/commit/push 或触发 Pages 部署；线上更新尚未验证，原文性能与趋势结论未在本轮核验。

## [2026-10-04] update | 仓库更名为 CloudOps Vault

- 将本地仓库目录更名为 `cloudops-vault`，Git origin 改为 `hangx969/cloudops-vault`；更新 README、Schema 与 Quartz 的站点名称、GitHub 链接和 Pages 路径。
- 同步 Obsidian vault、Codex、Claude 与 VS Code 的本地项目路径配置，保留既有权限和历史会话内容；外部配置备份位于 `/private/tmp/cloudops-vault-migration-backup`。Obsidian Git 已在新目录启用，原有自动备份设置保持不变。
- 1,023 个受保护原始文件的 SHA-256 校验值与迁移前一致；Git SSH 远程访问、配置解析、完整 Quartz 构建、本地首页与文章资源检查、Git diff 空白检查通过。GitHub Pages 部署成功，新地址 `https://hangx969.github.io/cloudops-vault/` 返回 HTTP 200。
- 重启 Codex 后复查通过：38 个历史聊天的目录缓存全部迁移，实际项目注册、当前聊天工作目录和持久化配置均指向新目录，相关配置中的旧路径为 0；数据库完整性检查通过，一次性修复程序已成功结束。

## [2026-10-04] ingest | Karpathy 大模型输出理解技巧

- 新增 [[AI/行业动态/Karpathy-大模型输出理解技巧-文字图解网页视频|Karpathy：让大模型输出更容易理解的四种技巧]]，总结受控语言写作、图解、交互式 HTML 和定制讲解视频，保留 3b1b、ElevenLabs API Key、本地免费语音替代路线及用完即弃的软件产物观点。
- 创建 [[KnowledgeBase/sources/karpathy-llm-output-understanding-summary|来源摘要]]，同步 [[KnowledgeBase/concepts/提示词工程|提示词工程]]、[[KnowledgeBase/maps/ai-workflow-map|AI 工作流专题地图]] 与 INDEX；新增提示词明确标为应用示例。
- 核对原推文正文与 2026-10-02 发布日期，并参考 ASD-STE100 官方介绍区分清晰写作、宽松的“80%”风格提示与正式标准合规。
- 文章与关联页面经 Obsidian MCP 写入并完整回读一致；frontmatter、代码块、新增 wikilink 和空白检查通过，Obsidian 阅读视图中的标题、表格及提示词排版已检查。本次为文档摄入，未执行 HTML 或视频生成。

## [2026-10-04] ingest | Longhorn 轻量块存储文章

- 按用户要求新增 [[Docker-Kubernetes/k8s-storage/开源存储列传第 18 篇 — Longhorn，K8s的轻量块存储|开源存储列传第 18 篇 — Longhorn，K8s的轻量块存储]]；用 humanizer-zh 优化正文表达，清理剪藏编号和系列导航，保留 8 个章节、原始元信息、完整对比表、技术背景、数字、版本与作者判断，原稿保持原样。
- 原文 10 幅 SVG 保留为 6 幅 Mermaid 和 4 幅 PNG；PNG 通过 PicGo CLI 的 GitHub Plus 上传到既有图床，流程图保留原图文字与关系。
- 新增 [[KnowledgeBase/sources/longhorn-block-storage-summary|Longhorn 来源摘要]]，补充 [[KnowledgeBase/concepts/StorageClass]]、[[KnowledgeBase/entities/Rancher]]、[[KnowledgeBase/maps/kubernetes-map]] 与 [[KnowledgeBase/INDEX]] 的来源和入口；保留索引及地图中的同期摄入内容。
- 对原文的每卷 Pod 数量、串行复制链、重建方式、快照空间和故障后果、部署与性能概括，另加带官方引用的折叠校核注释。未执行 Longhorn 部署、迁移、压测或故障演练。
- 校验通过：正文与来源摘要写入后完整 MCP 读回一致；本机 Obsidian 1.13.7 自带 Mermaid 库离线解析、渲染 6/6 通过并逐图查看；4/4 图片返回 HTTP 200 且远端 SHA-256 与本地一致；原稿和已有 6 篇存储文章哈希未变；新增知识库引用、元信息、代码围栏和 Git diff 空白检查通过。


## [2026-10-04] ingest | DeepSeek 3FS 并行文件系统

- 新增 [[Docker-Kubernetes/k8s-storage/DeepSeek 3FS，AI原生的并行文件系统|DeepSeek 3FS，AI原生的并行文件系统]]，用 humanizer-zh 优化正文表达，保留 7 个主章节、4 个技术小节、两张对比表和正文数字；清除剪藏段落序号与系列页脚导航，原始剪藏未修改。
- 原文 9 张内嵌 SVG 导出为 2100 px 宽 PNG，经 PicGo CLI 的 GitHub Plus 上传至图床；9/9 远端图片返回 HTTP 200，内容 SHA-256 与本地一致。独立 SVG 保存在文章的 assets 目录并提供正文链接，仅增加独立文件所需的 XML namespace，原图文字与图形保持一致。
- 正文另列官方资料核对说明，标明 USRBIO/FUSE 与内核参与、CRAQ 读路径、权限与轻量数据集快照、MIT 条件的表述边界；原文观点与核对说明分别标注。
- 新增 [[KnowledgeBase/sources/deepseek-3fs-summary|来源摘要]]，更新 [[KnowledgeBase/concepts/KV Cache]]、[[KnowledgeBase/entities/vLLM]]、[[KnowledgeBase/maps/kubernetes-map|Kubernetes 专题地图]] 与 INDEX；保留同期 Longhorn 等摄入改动，相关导航按当前文件数统计（Docker-Kubernetes 171 篇，k8s-storage 8 篇）。
- 15 个正文、SVG 与关联页面经 Obsidian MCP 写入并完整读回一致；frontmatter、核心 wikilink、SVG XML 与原图一致性、空白检查通过，原始剪藏 SHA-256 未变。Obsidian 阅读视图中 9 张图片均加载成功，11 个技术小节和两张表格可见；未运行 3FS 集群或复现性能基准。

## [2026-10-04] ingest | ArgoCD 同步故障排查

- 新建 [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD同步故障排查|ArgoCD 同步故障排查]]：基础篇已覆盖同步选项、Webhook 和健康机制，多集群实战侧重目录、权限和分发，故将这篇五类故障、案例与检查清单独立归档，并链接现有文章。
- 使用 humanizer-zh 优化中文表达、去除营销话术、规范标题和剪藏列表；保留五类问题、20 组代码示例内容、12 条生产注意事项、三个作者案例和 13 项排查清单。原始剪藏与现有五篇 ArgoCD 文章的 SHA-256 均未变化。
- 按官方文档与代码标注技术校正：三方模型范围、ignoreDifferences/RespectIgnoreDifferences、无效 all 字段与 CLI 参数、已有健康检查、replace/force、prune/delete 保护、Webhook 密钥位置、缓存和队列并发配置。案例数字、效果与归因保留为原文描述，未复现。
- 新增 [[KnowledgeBase/sources/argocd-sync-troubleshooting-summary|来源摘要]]，同步 ArgoCD、CICD、Kubernetes、tool/domain/kubernetes map、CI/CD 批量摘要的增量入口与 INDEX；保留同期已有导航更新，按当前文件核对 ArgoCD 6 篇、CI/CD 25 篇。
- MCP 写入后完整读回一致；10 页 frontmatter、13 个 YAML 与 7 个 Bash 代码块、15 处新页面内部链接/章节锚点及 Application/AppProject/ApplicationSet CRD 字段检查通过，Git diff 空白检查通过。Obsidian 阅读视图已检查开头、末尾 13 个复选项和速查表；清理历史错误缓冲后，本篇检查期间未捕获新错误。未执行 ArgoCD/kubectl 集群命令或部署验证。

## [2026-10-11] restructure | Krew 与 kubectl 插件指南合并

- 使用 humanizer-zh 优化表达，通过 Obsidian MCP 将公众号剪藏与现有 Krew/rolesum 笔记合并到 [[Docker-Kubernetes/k8s-UI-tools/kuebctl-插件krew-rolesum|kubectl 插件指南：Krew 安装、常用工具与 RBAC 排查]]；沿用原路径和别名，按技术用途组织 13 个插件，保留安装步骤、命令、输出示例、完整 Deployment 配置与 14 项检查清单。
- 对照官方索引、文档和代码校订 PATH、离线安装、tree、images、outdated、resource-capacity、score 与 RBAC 语义；将来源输出、版本和未复现案例明确标为示例，记录原文差异与引用。
- 创建 [[KnowledgeBase/sources/kubectl-krew-plugins-summary|来源摘要]]，同步 RBAC 概念页、Kubernetes 实体页与主题地图、UI 批次摘要、知识库入口和文档盘点中的标题。
- 完整读回核对后删除重复剪藏 `kubectl 不够用？krew 装 10 插件.md`，保留其他文章；两篇来源均无图片，无需调用 PicGo 上传。
- 8 个相关页面通过完整 MCP 读回核对；正文 41 个代码块闭合，39 段 Bash 通过语法检查，Deployment YAML 可解析且标签选择器一致；相关 wikilink 与任务范围差异检查通过。已在 Obsidian 阅读视图检查标题、清单和表格，并修正表格管道符显示。未执行集群命令。

## [2026-10-11] ingest | Cluster Autoscaler 节点自动扩缩容

- 使用 humanizer-zh 润色并新增 [[Docker-Kubernetes/k8s-scaling/K8s Cluster Autoscaler：节点自动扩缩容怎么用才靠谱|Cluster Autoscaler 节点自动扩缩容文章]]，保留原文元信息、章节标题、表格数据和 21 个代码块；清理剪藏列表、重复作者和页脚格式，原始剪藏保持原样。
- 新增 [[KnowledgeBase/sources/k8s-cluster-autoscaler-summary|来源摘要]]、[[KnowledgeBase/entities/Cluster Autoscaler|CA 实体页]] 与 [[KnowledgeBase/concepts/自动扩缩容|自动扩缩容概念页]]，同步 [[KnowledgeBase/entities/Kubernetes]]、[[KnowledgeBase/maps/kubernetes-map]] 和 INDEX；保留同期 Krew 摄入更新。
- 核对调度依据、PDB/驱逐保护、版本匹配与 Helm 配置的官方资料；在摘要中记录旧 FinOps 文档“CA 仅缩容空节点”的不一致，旧文未修改。
- 所有写入文件经 Obsidian MCP 完整读回一致；原始剪藏、正文元信息与代码块一致性、37 处新增页面链接、代码围栏和任务范围 Git diff 空白检查通过，日志仅追加。
- 阅读视图检查未完成：界面工具未找到运行中的 Obsidian 应用；未执行 kubectl、Helm 部署、集群扩缩容或回滚。

## [2026-10-11] ingest | StatefulSet Recreate 更新策略整合

- 使用 humanizer-zh 将原始剪藏整理为[[Docker-Kubernetes/k8s-basic-resources/k8s基础-statefulset#Recreate 更新策略（Kubernetes 1.37 Alpha）|StatefulSet 基础笔记的新章节]]，保留原文 4 组代码块、11 个故障案例、分阶段检查、作者报告的案例数字与上线清单；原始剪藏和目标笔记旧正文未修改。
- 单列官方资料核验说明：Recreate 在 1.37 中为 Alpha、默认关闭，需启用两个控制面组件的 StatefulSetRecreateStrategy；rollingUpdate.partition 不可与 Recreate 组合；区分 PVC 保留和 PV 回收策略，并标明启动顺序、init 容器、EndpointSlice 与 Redis 槽位接管案例的适用边界。
- 同步[[KnowledgeBase/sources/k8s-basic-resources-batch-summary|基础资源来源摘要]]、[[KnowledgeBase/maps/kubernetes-map|Kubernetes 专题地图]]和[[KnowledgeBase/INDEX|目录]]；基于各页最新内容更新，保留同期其他摄入改动。
- 正文与三页导航经 Obsidian MCP 完整读回一致，原文代码保留、11 个案例编号、7 个新增章节代码块、5 处新增 wikilink/章节锚点及任务范围 git diff 空白检查通过；日志仅追加。未执行 Kubernetes/Redis 命令或复现作者案例。阅读视图检查未完成：界面工具未能找到运行中的 Obsidian。

## [2026-10-11] update | K8s Cluster Autoscaler 标题

- 将已整理文章的文件名与 frontmatter 标题统一改为 [[Docker-Kubernetes/k8s-scaling/K8s Cluster Autoscaler|K8s Cluster Autoscaler]]，正文和原始剪藏保持原样。
- 同步来源摘要、自动扩缩容概念页、CA 与 Kubernetes 实体页及专题地图中的 9 处路径引用，地图显示名使用新标题；历史日志仅追加，不改写。

## [2026-10-11] update | 清理临时剪藏引用

- 按用户要求移除 StatefulSet 正文和基础资源来源摘要中两处指向临时剪藏的链接；保留作者、日期、技术内容、代码和案例。
- 全 vault 搜索及完整 MCP 读回确认，其他文章未发现此类引用。历史日志中的一个来源链接和一个目录前缀暂未修改：整文件写入与按章节修改均被自动审批拒绝，因日志按规约仅允许追加，待用户明确授权例外后清理。


## [2026-10-11] update | 清理临时剪藏历史引用

- 按用户本次明确授权，清理历史日志中的一个临时剪藏来源链接和一个目录前缀，保留事件文字、文件名及其余历史记录。
- 此前被自动审批拒绝的两处日志修改已通过 Obsidian MCP 完成。
