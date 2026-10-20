# AI/ — AI 工具、平台与实践

120+ 篇文档，覆盖 Claude Code、OpenClaw、Hermes Agent 三大 AI 平台及其在运维/知识管理场景中的应用。

## 子目录结构

| 子目录 | 篇数 | 说明 |
|--------|------|------|
| ClaudeCode/ | 5 | Claude Code 基础指南、扩展体系、多智能体协作、Skill 质检、Harness 安全约束 |
| Codex/ | 6 | Codex 配置、Harness 任务循环、上下文与工具执行、交互体验和 Token 优化 |
| OpenClaw/ | 7 | 安装、Channels、Skills 插件、CoPaw、AIOps、多智能体、Ubuntu 环境 |
| Obsidian/ | 2 | AI 知识库完整指南、可视化 Skills |
| Hermes-agent/ | 3 | 满配指南与生态资源、Ubuntu 安装、架构解析与 OpenClaw 对比 |
| AI-视觉/ | 4+67 | PPT Master、HTML 动画、html-ppt-skill + awesome-design-md（67 品牌设计系统） |
| skills/ | 2 套 | 自研 K8s 巡检 Skills（Python 版 + Shell 版） |
| agents/ | 8 个 | OpenClaw 多智能体定义文件（aiops/linux/container/k8s/architect/backend/frontend/pm） |
| CloudOps-Agent-项目/ | 57 | 三语言智能 OnCall Agent（Go/Java/Python） |
| RAG-Agent-项目/ | 33 | 企业 RAG 知识库系统（Spring Boot + ES） |
| Code review和知识图谱/ | 6 | AI 代码审查闭环、CodeGraph、Graphify、code-review-graph、Understand-Anything、shiji-kb 知识图谱构造方法论 |
| 企业级私有化大模型/ | 6 | 模型精度与 KV Cache、vLLM/KServe 部署、本地推理 Runtime 选型与离线交付 |
| 行业动态/ | 3 | Boris Cherny 红杉大会七个判断、HTML 取代 Markdown、AI 时代 Git 版本管理 |
| GithubCopilot/ | 1 | Copilot CLI |

## 关键入口

- [[Claude Code 基础指南]] — Claude Code 入门必读
- [[AI/ClaudeCode/Claude Code 扩展体系]] — MCP/Skills/Slash Commands/Plugin 四层扩展
- [[AI/Codex/Codex-Harness架构-任务循环与扩展]] — Codex Harness 架构：从任务循环到工具执行
- [[AI/OpenClaw/OpenClaw-基础-安装]] — OpenClaw 入门
- [[AI/Obsidian/obsidian-claude-code-AI知识库完整指南|Obsidian + Claude Code：AI 知识库指南]] — Obsidian+Claude Code 知识库完整指南（理念+搭建+操作+计划）
- [[HarnessKit]] — AI 编码智能体统一管理工具

## 知识库导航

→ [[KnowledgeBase/maps/ai-workflow-map]] — AI 工作流专题地图（推荐阅读顺序）


## 企业级私有化大模型

| 文章 | 主题 |
|------|------|
| [[基于docker部署vLLM和LiteLLM私有化大模型]] | vLLM/LiteLLM 私有化部署、权重与 KV Cache 显存规划 |
| [[AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM]] | Kubernetes GPU 服务部署上下文 |
| [[AI/企业级私有化大模型/大模型精度与量化：FP64到NVFP4]] | 数值格式、量化与训练/推理取舍 |
| [[AI/企业级私有化大模型/KV Cache-从原理到集群调度]] | KV Cache 生命周期、显存带宽瓶颈与集群调度 |
| [[AI/企业级私有化大模型/一个 Deployment 就能跑 vLLM，为什么还需要 KServe？\|为何用 KServe 管理 vLLM 推理服务？]] | KServe Standard、Envoy Gateway、PVC 模型加载与 OpenAI 兼容接口实操 |
| [[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]] | Ollama、vLLM、SGLang、vLLM-Omni 选型，模型与镜像离线交付及容器化边界 |


## AI 视觉与科普视频

- [[AI/AI-视觉/Anatomy-Skill-交互模型与科普视频|Anatomy Skill：交互模型与科普讲解视频]] — 用结构模型探索原理，再按学习需要生成带配音的解释；[[KnowledgeBase/sources/anatomy-skill-interactive-explainer-summary|来源摘要]]。
