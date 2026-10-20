---
title: Claude Code 扩展体系
tags:
  - AI
  - claude-code
  - MCP
  - skills
  - plugin
  - slash-command
aliases:
  - CC扩展体系
  - Claude Code Extensions
---

# Claude Code 扩展体系

Claude Code 的核心竞争力不只是对话和代码生成，更在于它的**四层扩展机制**。这四层机制各有定位，组合起来构成一个可编排、可沉淀、可分发的智能工作流系统。

| 层级 | 机制 | 本质 | 触发方式 | 注入方式 |
|------|------|------|---------|---------|
| 1 | **MCP** | 外部工具桥梁 | 自动（AI 判断需要时调用） | tool call |
| 2 | **Skills** | 自动触发的能力包 | 自动（匹配用户意图） | system prompt |
| 3 | **Slash Commands** | 手动触发的工作流 | 手动（`/命令名`） | user message |
| 4 | **Plugin** | 打包分发容器 | — | 包含以上所有 |

**一句话总结**：MCP 是"手"（操作外部世界），Skills 是"肌肉记忆"（自动响应），Slash Commands 是"快捷键"（手动触发），Plugin 是"安装包"（打包分发）。

单个 Skill 是能力，多个 Skill 编排是流程，Skill + MCP + SubAgent 是智能体。

---

# 一、MCP（Model Context Protocol）

MCP 是连接 AI 模型与外部工具、数据源的标准化桥梁协议。通过 MCP Server，Claude Code 可以调用文件系统、数据库、API、浏览器等外部资源。

- **协议模型**：Client（Claude Code）↔ Server（MCP 进程），通过 stdio 通信
- **安装方式**：`claude mcp add <name> -- <command>` 或在 JSON 配置文件中声明
- **配置位置**：用户全局 `~/.claude/settings.json` 或项目级 `.claude/settings.json`

---

## 常用 MCP 服务器

### context7

**场景**：查最新框架文档（Next.js 15、React 19）、API 参数和用法确认、库的最佳实践和陷阱、版本迁移指南。

用个人 GitHub 账号登录：[https://context7.com/](https://context7.com/)

**VSCode 扩展**：在扩展界面搜 `@mcp context7`，选择安装。配置文件 JSON 中添加 API Key：

```json
"servers": {
  "io.github.upstash/context7": {
    "type": "stdio",
    "command": "npx",
    "args": [
      "@upstash/context7-mcp@1.0.30"
    ],
    "env": {
      "CONTEXT7_API_KEY": ""
    },
    "gallery": "",
    "version": "1.0.30"
  }
}
```

**Claude Code**：

```sh
claude mcp add context7 -- npx -y @upstash/context7-mcp --api-key ""
```

---

### atlassian

用 Docker 方式安装。安装完成之后，在家目录配置文件中添加进去 Docker 命令和 token，启动 colima 就能自动连接 MCP。

```json
"mcpServers": {
  "atlassian": {
    "type": "stdio",
    "command": "docker",
    "args": [
      "run", "-i", "--rm",
      "-e", "JIRA_URL",
      "-e", "JIRA_USERNAME",
      "-e", "JIRA_PERSONAL_TOKEN",
      "-e", "CONFLUENCE_URL",
      "-e", "CONFLUENCE_USERNAME",
      "-e", "CONFLUENCE_PERSONAL_TOKEN",
      "ghcr.io/sooperset/mcp-atlassian:latest"
    ],
    "env": {
      "JIRA_URL": "",
      "JIRA_USERNAME": "",
      "JIRA_PERSONAL_TOKEN": "",
      "CONFLUENCE_URL": "",
      "CONFLUENCE_USERNAME": "",
      "CONFLUENCE_PERSONAL_TOKEN": ""
    }
  }
}
```

---

### bitbucket

```json
"bitbucket": {
  "type": "stdio",
  "command": "npx",
  "args": [
    "-y",
    "@zhanglc77/bitbucket-mcp-server"
  ],
  "env": {
    "BITBUCKET_BASE_URL": "",
    "BITBUCKET_USERNAME": "",
    "BITBUCKET_TOKEN": ""
  }
}
```

---

### sequential-thinking

深度思考引擎。

**安装**：

```sh
claude mcp add mcp-sequentialthinking-tools -- npx -y mcp-sequentialthinking-tools
```

**场景**：复杂技术选型（微服务 vs 单体、数据库选型）、架构设计决策（分层、模块边界、扩展性）、疑难 bug 根因分析（多因素交叉、隐蔽逻辑）、性能优化策略规划。

**实战案例**："分析为什么我们的订单服务在高峰期会超时,考虑数据库、缓存、网络、并发锁、GC 等所有可能因素"

**效果**：会给出完整的推理链：假设 → 验证 → 排除 → 聚焦 → 验证 → 结论，而不是直接猜一个答案。

---

### memory

长期记忆。

**安装**：

```sh
claude mcp add memory -- npx -y @modelcontextprotocol/server-memory
```

**场景**：记住项目约定（命名规范、错误码、配置路径）、记住团队踩过的坑（某个库的 bug、某个配置的坑）、记住重要决策（为什么选这个方案、权衡了什么）。

**实战案例**：

```
你:"记住:我们的错误码统一用E开头+4位数字,数据库表名用snake_case,Redis key用冒号分隔"
(一周后)你:"帮我设计一个用户登录失败的错误码"
Claude自动调用记忆:"根据你们的规范,应该是E1001这样的格式..."
```

对 Claude 说：

```markdown
"用memory(MCP)记住我们团队的规范:

代码规范:
- 用ESLint + Prettier
- 命名用驼峰(变量)和帕斯卡(组件)

Git规范:
- commit格式:feat/fix/docs: 描述
- PR必须关联issue

技术栈:
- 前端:React 18 + TypeScript + Vite
- 后端:Node.js + Express + PostgreSQL
"
```

验证：下次问问题时，看 Claude 是否会自动调用这些规范。

---

### playwright

浏览器自动化。

```sh
claude mcp add playwright -- npx -y @executeautomation/playwright-mcp-server
```

**场景**：竞品监控、批量截图、自动化测试、数据抓取

**案例**："打开这 5 个竞品官网,截图首页和定价页,保存到 `./analysis/`"

---

### filesystem

本地文件操作。

```sh
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path/to/project
```

**场景**：读写配置、批量处理文件、项目初始化脚本

> [!warning] 注意
> 指定允许访问的路径，避免权限过大。

---

### github
Claude Code 通过官方 GitHub MCP Server 接入 GitHub，可读取/操作 PR、Issue 等。两种配置方式：

**方式 A：远程 HTTP（推荐）**
- 无需 Docker，GitHub 官方托管，配置最简单
- 前提：能访问 `api.githubcopilot.com`；GHES（私有部署）不支持
```bash
claude mcp add-json github '{"type":"http","url":"https://api.githubcopilot.com/mcp","headers":{"Authorization":"Bearer YOUR_GITHUB_PAT"}}'
# 全局可用加 --scope user
```

**方式 B：本地 Docker**
- Token 只在本机流转，不经过任何远程中转；GHES 场景下唯一选择
- 前提：本机需要 Docker 且保持运行
```bash
claude mcp add github -e GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_GITHUB_PAT -- docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server
```

**PAT 权限要求**：Contents / Pull requests / Metadata 至少 Read 权限（fine-grained token）或 `repo`（classic token）

**验证**：`claude mcp list` / `claude mcp get github`

**选型建议**：默认用方式 A，图省心；如果是 GHES 私有部署或公司网络封锁 `api.githubcopilot.com`，切换方式 B。

---

### exa

智能搜索（需要官网 key），依赖 axios 包。

- GitHub：[exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server)
- Exa API Key：[https://dashboard.exa.ai/home](https://dashboard.exa.ai/home)

```sh
claude mcp add exa -e EXA_API_KEY="" -- npx -y exa-mcp-server
```

**场景**：需要搜索最新信息、技术博客、开源项目时，比普通搜索引擎更精准。

**优势**：

- **语义理解更强（Neural Search）**：你可以用自然语言描述你想要的内容（例如："找一篇关于 Transformer 架构的通俗易懂的教程"），它能理解"通俗易懂"和"教程"的含义，而不是只搜这两个词
- **返回结构化数据（Clean Data）**：传统搜索引擎返回的是充满了广告、SEO 废话和复杂 HTML 的网页。Exa 会清洗内容，直接返回**干净的文本**或**结构化数据**，这大大减少了 AI 处理杂乱信息的负担，减少了"幻觉"
- **强大的过滤功能**：它允许你按**域名**（如只搜 github.com）、**日期**、**内容类型**（如 PDF、代码）进行精确过滤
- **不仅是搜索，还能"内容相似推荐"**：你可以给它一个链接，让它找出"与这个网页内容相似的其他网页"，这对于做调研非常有用

---

### deepwiki

深度文档聚合。

```sh
claude mcp add deepwiki -- npx -y mcp-deepwiki
```

**场景**：聚合某个库的完整文档站点，比 context7 更全面但速度慢一些。

---

### drawio

> [!info] 仓库
> [jgraph/drawio-mcp](https://github.com/jgraph/drawio-mcp)

Draw.io 的这个 MCP 工具（`drawio-mcp`），走了一条非常聪明的路子。它不是自己在后台"画"一张图，而是**把 AI 生成的逻辑（Mermaid、CSV、XML）瞬间转换成 Draw.io 的专用链接**。

简单来说，流程变成了这样：

1. 你告诉 AI："画个 OAuth2 流程图"
2. AI 生成结构化数据
3. MCP 工具把数据压缩、编码
4. 浏览器自动弹出一个 Draw.io 编辑页面，图已经画好了，每一个节点都能拖、能改、能换色

根据 GitHub 上的官方文档，这个 MCP Server 目前支持三种核心模式：

- **Mermaid 转图 (`open_drawio_mermaid`)**：这是最常用的。AI 写 Mermaid 逻辑最强，Draw.io 负责渲染和二次编辑，绝配
- **CSV 转图 (`open_drawio_csv`)**：适合画组织架构图、网络拓扑图。你扔给 AI 一堆人员名单和汇报关系，它能瞬间生成树状图
- **XML 原生格式 (`open_drawio_xml`)**：如果你有现成的 Draw.io XML 数据，或者让 AI 学习了 XML 结构，可以直接生成最复杂的图表

**安装**：

```json
"mcpServers": {
  "drawio-mcp": {
    "command": "npx",
    "args": ["-y", "@drawio/mcp"],
    "env": {},
    "type": "stdio"
  }
}
```

**使用**：使用 draw.io MCP 工具 `open_drawio_mermaid` 制作展示 OAuth2 流程的时序图

**导出**：export 成 xml 格式，在 Confluence page 上创建一个 draw.io diagram

---

### datadog

> [!info] 文档
> [Datadog MCP Server Setup](https://docs.datadoghq.com/bits_ai/mcp_server/setup/?tab=claudecode)

**场景**：在 Claude Code 中直接查询 Datadog 的日志、指标、Trace、Dashboard、Monitor、Incident 等可观测性数据，支持 16 个产品 Toolset 按需加载。

**Claude Code 配置**：

```bash
# 方式一：命令行添加（远程 HTTP 认证，会触发 OAuth 登录）
claude mcp add --transport http datadog-mcp https://mcp.datadoghq.com/api/unstable/mcp-server/mcp

# 方式二：本地二进制（适用于远程认证不可用的情况）
curl -sSL https://coterm.datadoghq.com/mcp-cli/install.sh | bash
datadog_mcp_cli login
claude mcp add datadog --scope user -- ~/.local/bin/datadog_mcp_cli
```

也可以直接在 `~/.claude.json` 中添加：

```json
{
  "mcpServers": {
    "datadog": {
      "type": "http",
      "url": "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp"
    }
  }
}
```

**认证方式**：默认使用 OAuth 2.0（远程 HTTP 连接时自动触发浏览器登录）。如果无法走 OAuth 流程（如服务器环境），可以通过 API Key + Application Key 以 HTTP Header 方式认证：

```json
{
  "mcpServers": {
    "datadog": {
      "type": "http",
      "url": "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp",
      "headers": {
        "DD_API_KEY": "<YOUR_API_KEY>",
        "DD_APPLICATION_KEY": "<YOUR_APPLICATION_KEY>"
      }
    }
  }
}
```

> [!tip] 安全建议
> 建议使用 [Service Account](https://docs.datadoghq.com/account_management/org_settings/service_accounts/) 创建的 scoped API Key 和 Application Key，仅赋予所需权限。

> [!warning] 权限
> 需要 Datadog 用户角色具备 `mcp_read` 和 `mcp_write` 权限（Standard Role 默认包含）。除此之外还需要对应资源的标准权限（如读 Monitor 需要 Monitors Read）。如使用自定义角色，需在 [Organization Settings > Roles](https://app.datadoghq.com/organization-settings/roles) 中手动勾选 **MCP Read** 和 **MCP Write**。

**Toolset 机制**：Datadog MCP 支持按产品域选择性加载工具集，通过 URL query 参数 `toolsets` 控制，节省 context window 空间：

```bash
# 默认只加载 core 工具集
https://mcp.datadoghq.com/api/unstable/mcp-server/mcp

# 只加载 APM 和 LLM Observability
https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=apm,llmobs

# 加载全部 GA 工具集（适合支持 tool filtering 的客户端如 Claude Code）
https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=all
```

**可用 Toolset 列表**：

| Toolset | 覆盖范围 | 状态 |
|---------|---------|------|
| `core` | 日志、指标、Trace、Dashboard、Monitor、Incident、Host、Service、Event、Notebook | GA（默认） |
| `alerting` | Monitor 创建/验证/覆盖分析、SLO 搜索 | GA |
| `dashboards` | Dashboard CRUD、Widget Schema 验证 | GA |
| `cases` | Case Management：创建/搜索/更新、关联 Jira | GA |
| `dbm` | Database Monitoring | GA |
| `error-tracking` | Error Tracking | GA |
| `feature-flags` | Feature Flags 管理 | GA |
| `llmobs` | LLM Observability Span 搜索与实验分析 | GA |
| `networks` | Cloud Network Monitoring、Network Device Monitoring | GA |
| `onboarding` | Datadog 引导式配置 | GA |
| `product-analytics` | Product Analytics 查询 | GA |
| `reference-tables` | Reference Tables 管理 | GA |
| `security` | 代码安全扫描、Security Signals/Findings 搜索 | GA |
| `software-delivery` | CI Visibility、Test Optimization | GA |
| `synthetics` | Synthetic Tests | GA |
| `workflows` | Workflow Automation | GA |
| `apm` | APM Trace 深度分析、Span 搜索、Watchdog Insights | Preview |
| `ddsql` | DDSQL 查询（SQL 方言查询 Datadog 数据） | Preview |

---

### 更多 MCP

- 官方列表：[modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
- 社区精选：[wong2/awesome-mcp-servers](https://github.com/wong2/awesome-mcp-servers)（500+ 服务器持续更新，包括 Notion、Slack、Jira、数据库等各种集成）

---

## 配置文件一键添加 MCP

```json
{
  "mcpServers": {
    "atlassian": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "JIRA_URL",
        "-e", "JIRA_USERNAME",
        "-e", "JIRA_PERSONAL_TOKEN",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_USERNAME",
        "-e", "CONFLUENCE_PERSONAL_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "JIRA_URL": "",
        "JIRA_USERNAME": "",
        "JIRA_PERSONAL_TOKEN": "",
        "CONFLUENCE_URL": "",
        "CONFLUENCE_USERNAME": "",
        "CONFLUENCE_PERSONAL_TOKEN": ""
      }
    },
    "bitbucket": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@zhanglc77/bitbucket-mcp-server"],
      "env": {
        "BITBUCKET_BASE_URL": "",
        "BITBUCKET_USERNAME": "",
        "BITBUCKET_TOKEN": ""
      }
    },
    "exa": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": {
        "EXA_API_KEY": "xxx"
      }
    },
    "sequential-thinking": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "mcp-sequential-thinking"]
    },
    "context7": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp", "--api-key", "xxx"]
    },
    "memory": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": ""
      }
    }
  }
}
```

---

## MCP 常用应用组合

| 场景 | 推荐组合 |
| --- | --- |
| 日常开发 | filesystem + github + memory |
| 深度工作 | sequential-thinking + context7 + memory |
| 自动化任务 | playwright + filesystem |
| 学习新技术 | context7 + deepwiki + exa（或 brave-search） |

---

# 二、Skills（技能）

Skills（技能）是自动触发的能力包，2025 年 10 月发布。

> [!info] 官方文档
> [Claude Code Skills](https://code.claude.com/docs/zh-CN/skills)

**和 MCP 的区别**：Skills 的范围更大，Skills 可以调用 MCP。Skills 还可以包含 Python 脚本，功能更灵活丰富。

简单说，**Skills 就是给 Claude 安装的"专业技能包"**。

**技术上**，一个 Skill 就是一个文件夹，里面包含技能的描述、相关脚本、示例代码等等。

比如你搞了一个 `SKILL.md` 文件，里面放了 AI 生成 PPT 固定流程的指令。你给 Claude 说：帮我生成 PPT，这个 Skill 就能激活。你就不需要每次都把你的要求写出来。

---

## 解决痛点

### 痛点 1：重复劳动

- **之前**：每次都像教小孩一样解释规则（"用现在时""50 字以内""说 what 和 why"）
- **现在**：打包成 Skill，说一句话自动应用

### 痛点 2：团队协作混乱

- **场景**：10 个人用 10 种方式让 Claude 生成文档，格式五花八门
- **解决**：
  1. 把 Skill 提交到项目代码库：`.claude/skills/company-doc-generator/`
  2. 团队成员 `git pull` 后自动同步
  3. 全员统一规范

### 痛点 3：知识无法沉淀

- **之前**：老员工调试 API 的技巧藏在脑子里
- **现在**：写成 Skill，新人克隆代码立刻获得团队智慧

---

## 渐进式披露机制（Progressive Disclosure）

这个设计是 Skills 高效的核心。Anthropic 官方术语叫 **Progressive Disclosure**："Claude loads information in stages as needed, rather than consuming context upfront."（按需分阶段加载，而不是一次性占满上下文）。

本质原因：大模型的注意力是稀缺资源，**塞进 context 的每一个 token 都在和当前任务争抢模型的关注度**。如果启动时就把所有可能用到的工作流、模板、示例全塞进上下文，模型处理实际请求时反而抓不到重点。

### 官方三层加载机制

| Level | 加载时机 | Token 成本 | 内容 |
|-------|----------|-----------|------|
| **Level 1（Metadata）** | 永远加载（系统启动时） | **~100 tokens / 每个 Skill** | YAML frontmatter 中的 `name` + `description` |
| **Level 2（Instructions）** | Skill 被触发时 | **< 5K tokens** | SKILL.md 主体内容 |
| **Level 3+（Resources）** | 按需 bash 读取 | 实际无限 | 引用文件、脚本、模板等 |

**字段限制与篇幅建议**：

- `name`：最多 **64 字符**，只能小写字母+数字+连字符，不能含 "anthropic" 或 "claude"
- `description`：最多 **1024 字符**，必须非空，不能含 XML 标签
- `SKILL.md` 主体：控制在 **500 行以内**，接近这个规模就把详细文档、示例和模板拆出去。行数是编写时的拆分标准，不能与 token 数或中文字数固定换算，也不是运行时的硬性截断限制

500 行和下文的一跳引用原则来自 [Anthropic Skill 编写最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#progressive-disclosure-patterns)。

这解释了为什么 Anthropic 鼓励装**多个细分 Skill** 而不是一个臃肿 Skill——50 个 Skill 的 Level 1 总共也才 5K token。

### SKILL.md 的定位：分层引用网络的根节点

`SKILL.md` 是执行入口，也是按需加载资源的索引。按职责将 Skill 分成三层，避免触发信息、执行流程和参考资料混在一起：

| 层级 | 负责什么 | 放什么内容 |
|------|----------|------------|
| `description` | 判断何时触发、何时跳过 | 能力概述、用户会说的触发词、使用条件、跳过条件；不写实现细节 |
| `SKILL.md` 主体 | 执行主逻辑 | 工作流骨架、决策分支、步骤出口条件，以及何时读取哪个资源 |
| 支持资源 | 提供执行时才需要的细节 | `references/` 放参考文档，`scripts/` 放脚本，`assets/` 放模板等资源 |

第三层是资源层的统称，不要求把脚本和模板都塞进 `references/`。主文件保留流程和资源入口，参考文档说明相关细节，避免多处重复维护同一套规则。

凡是"细节填充"——具体的规则案例、模板正文、长篇示例、参考代码——一律不进主文件，全部下沉到 Level 3 的引用文件。**主文件不需要装下所有内容，只需要装下"地图"**。

> [!tip] 主文件保留执行入口
> 可以在 `SKILL.md` 中提供 quick start，再指向表单处理、API 参考等详细文档。判断是否拆分，要看流程是否清楚、细节是否按需加载，不能只看文件短不短。

### SKILL.md 拆分判断标准

| SKILL.md 行数 | 状态 | 建议 |
|---------------|------|------|
| < 200 行 | 较短 | 流程清楚时无需为拆而拆 |
| 200-500 行 | 需要控制增长 | 新增内容前先判断是否应放入支持资源 |
| > 500 行 | 超出本指南的篇幅目标 | 将详细文档、示例和模板拆到支持资源，主文件保留决策和执行步骤 |

**拆分优先级**：
1. **第一刀**：先把**示例和模板**下沉（长但低频访问，最吃 token）
2. **第二刀**：把**详细规则**拆成 `references/rules.md`，主文件只留一句"风格规则见 references/rules.md"
3. **第三刀**：把**长流程**封装成脚本，模型 bash 调用即可

**不要拆的**：决策树——哪个工作流处理哪种请求、判断分支怎么走，这是主文件的命根子，拆出去模型读完主文件就不知道下一步该干嘛。

### 好引用 vs 坏引用

```markdown
# ✅ 好引用（带指路标签）
## 第三步：审稿
按文风规范跑一遍审稿，对照标准见 references/style-guide.md。
关键检查项：开头是否有场景引入、字数是否在 4000-5000 区间。

# ❌ 坏引用（裸文件名）
## 第三步：审稿
详见 references/style-guide.md。
```

好引用告诉模型"为什么去看、看哪几条"，模型可以判断是否真的需要读；坏引用只扔一个文件名，模型要么不读跳过、要么每次全文读浪费 token。

**执行所需的引用链最多一跳**：从 `SKILL.md` 直接指向所需资源，避免把必读资料藏在子文件的下一层引用中。例如，若 `references/A.md` 依赖 `references/B.md`，应在 `SKILL.md` 中直接列出 A、B 的用途和读取条件，避免形成 `SKILL.md → A.md → B.md` 的必读链；循环引用也应消除。

Agent 会按需读取文件，不能假定它会递归展开每条链接。深层引用可能只被预览或遗漏；一跳原则用于降低漏读风险，并不意味着 Agent 在技术上无法继续读取下一层文件。

### 实战演进案例

一个写作 SKILL 文件的三版迭代：

| 指标 | V1（单文件 1900 行） | V3（主文件 612 行 + 引用） |
|------|---------------------|--------------------------|
| 触发时初始 token 注入 | ~14,000 | ~4,500 |
| 单次工作流端到端 token | ~28,000 | ~12,000 |
| "写错风格"频率 | 每 20 次约 1 次 | 几乎归零 |
| 维护成本（改一条规则） | 全文件找位置 | 单子文件改 |

V1 的核心问题：把所有写作规则、文风指南、案例分析、模板、配图规范、上传脚本说明全塞进一个 SKILL.md，远超 500 行的篇幅目标。不同类型文章（公众号/算法/知乎）的规则混在一起互相干扰。V3 虽然已有改善，但主文件仍有 612 行，按本指南还应继续拆分。

V3 的做法：主文件只放触发条件 + 10 步工作流骨架 + 引用索引，其余下沉：
- 文风规范 → `references/style-guide.md`
- 历史范本 → `references/article_*.md`
- 代码逻辑 → `scripts/*.py`
- 配置数据 → `config/*.json`

**Skill 间的 handoff 设计**：文章 SKILL 走到最后一步需要生成视频时，不把视频生成的细节塞进自己的主文件，而是复制视频模板副本、注入 input.md、然后**显式把控制权交给视频 SKILL**。每个 Skill 只懂自己那一摊事，靠"路标"互相衔接。

---

## 组成结构

一个 Skill 文件夹通常包含这几部分：

- **SKILL.md**：核心文件。用 YAML 写元数据（名字、描述），用 Markdown 写详细的指令，告诉 Claude 在什么情况下、以及如何使用这个 Skill
- **scripts/**：存放可执行的 Python、Shell 脚本
- **references/**：存放参考文档（如 API 文档、数据库 Schema、公司政策等），作为给 Claude 看的知识库
- **assets/**：存放资源文件（如 PPT 模板、Logo、项目脚架等），供 Claude 在执行任务时直接使用

---

## 安装

**手动安装**：

- 个人 Skills：`~/.claude/skills/`
- 项目 Skills：`.claude/skills/`
- 创建一个子目录和 skill 同名即可，在子目录中创建 `SKILL.md`

**Marketplace 安装**：

```sh
/plugin marketplace add anthropics/skills
/plugin
```

1. Select **Browse and install plugins**
2. Select **anthropic-agent-skills**
3. Select **document-skills or example-skills**
4. Select **Install now**

**打包与分享**：

Claude 可以打包 skill 变成一个 `xxx.skill` 文件，可以分享给其他人安装。

```sh
# 打包
python3 /path/to/skill-creator/scripts/package_skill.py \
  /path/to/your-skill \
  /output/path

# 安装
# 在 Claude Code 中：Install skill from /path/to/your-skill.skill
```

---

## Skills 实战案例

### 第一层：工程化单点突破（把说明书变技能包）

把最烦人的重复劳动自动化。少写废话提示词，让 Claude 自动识别场景。

#### 简单测试：Pre-commit Review

在 `.claude/skills/` 目录下创建 `pre-commit-check/SKILL.md`：

```markdown
# 名称
pre-commit-check

# 描述
代码提交前的标准检查:格式化、Lint、测试

# 触发
当用户提到"提交""commit""推送"时自动触发

# 执行逻辑
1、运行代码格式化
2、运行Lint检查
3、运行相关测试
4、生成检查报告

# 输出
分级报告:阻断问题、警告问题、通过项
```

#### 案例 1：智能代码审查

`smart-code-review`：

> [!success] 效果
> 以前代码审查靠人工挑毛病，经常遗漏关键问题。现在说"review 这个 PR"，自动按文件类型做专项检查，该找的坑一个不漏。团队线上事故率下降 60%。

```markdown
# 名称
smart-code-review

# 触发
当用户提到"review""审查""检查代码"或准备提交PR时

# 执行逻辑
1、分析变更文件类型和影响范围
2、根据文件类型选择检查项:
- API文件 → 检查鉴权、参数校验、错误处理、API文档
- 数据库迁移 → 检查索引、向后兼容、回滚脚本、性能影响
- 前端组件 → 检查无障碍、性能、状态管理、错误边界
- 配置文件 → 检查敏感信息泄露、环境变量、默认值安全性
3、调用对应SubAgent进行专项审查:
- security-auditor → SQL注入、XSS、CSRF等
- performance-engineer → N+1查询、大对象、内存泄漏
- frontend-developer → 重渲染、bundle大小、懒加载
4、汇总问题并按严重程度分级:
- 阻断级(安全漏洞、数据丢失风险)
- 警告级(性能隐患、可维护性问题)
- 建议级(优化空间、最佳实践)

# 输出
分级报告 + 修复建议 + 参考文档链接
```

#### 案例 2：依赖升级风险评估

`dependency-upgrade-check`：

> [!success] 效果
> 以前升级依赖全靠运气，升了才知道炸不炸。现在每次升级前先跑一遍评估，该注意的点全列出来，升级有底气。

~~~markdown
# 触发
检测到package.json/requirements.txt/go.mod等变更时

# 执行逻辑
1、识别新增、升级、删除的依赖
2、对每个变更依赖:
- 用github MCP查该库的changelog和breaking changes
- 用context7查新版本的API变化
- 扫描项目代码,找出使用该依赖的位置
- 评估影响面(多少文件、是否核心路径)
3、检查依赖树冲突(peerDependencies、版本兼容性)
4、查询CVE数据库,检查已知漏洞
5、生成升级checklist

# 输出
## 升级风险评估
- 高风险依赖(breaking changes多、使用面广)
- 中风险依赖(小改动、局部影响)
- 低风险依赖(bugfix、无API变化)

## 需要人工验证的点
[列出可能出问题的代码位置]

## 建议升级顺序
[从低风险到高风险,逐步验证]

## 回滚预案
[如果升级出问题,怎么快速回退]
~~~

---

### 第二层：编排型工作流（参数化 + 链式调用）

一个技能适配多项目，多个技能串成流水线。

#### 案例：生产事故应急响应

`incident-response`：

> [!success] 效果
> 以前线上出问题，团队一片慌乱，排查靠经验靠猜。现在说"线上订单服务挂了"，5 分钟内给出完整分析 + 3 套止损方案。平均故障恢复时间从 45 分钟降到 12 分钟。

~~~markdown
# 触发
用户说"线上出问题了""紧急""事故"等关键词

# 执行流程(自动并行+串行)
## 阶段1:快速止血(并行执行)
- 调用devops-troubleshooter → 分析日志、定位异常
- 调用performance-engineer → 检查资源使用、是否过载
- 调用database-optimizer → 检查慢查询、锁等待

## 阶段2:根因分析(基于阶段1结果)
- 如果是代码问题 → 调用debugger SubAgent
- 如果是配置问题 → 检查最近的配置变更
- 如果是依赖问题 → 检查上游服务状态
- 如果是资源问题 → 检查流量异常、是否被攻击

## 阶段3:止损方案(基于根因)
- 自动生成3个止损方案:
  1、 最快方案(回滚、降级、限流)
  2、 最稳方案(修复根因,重新发布)
  3、 临时方案(绕过问题点,保持可用)
- 对比每个方案的:恢复时间、风险、副作用

## 阶段4:执行确认
- 输出完整的执行命令和回滚命令
- 标注每步的预期结果和验证方式
- 等待人工确认后才执行

# 输出
## 事故摘要
影响范围、严重程度、开始时间、核心指标变化(错误率、延迟、可用性)

## 根因分析
详细分析,附日志/监控截图链接

## 止损方案对比
3个方案的完整对比表

## 执行清单
一步步操作指令,可复制执行

## 事后改进
如何预防类似问题再次发生
~~~

---

### 第三层：团队智能体（知识沉淀 + 自进化）

#### 案例：技术债追踪助手

> [!success] 效果
> 不再是"想起来就还"，而是每周有明确的 3 个小目标。结合 SonarQube 等专业工具，Skill 负责排优先级和生成报告。

`tech-debt-tracker`：

```markdown
# 名称
tech-debt-tracker

# 描述
每周帮助团队识别和追踪最重要的技术债

# 触发
用户提到"技术债""代码坏味道""重构计划"时

# 执行逻辑
1、集成SonarQube API,获取现有扫描结果
2、按影响面排序(修改频率高 + bug数多 = 优先级高)
3、生成本周TOP 3待还技术债清单
4、每项包含:位置、问题描述、建议方案、预估工作量

# 输出
Markdown周报:
- TOP 3技术债(本周建议优先处理)
- 已还技术债(上周完成的3项)
- 决策记录(为什么选这些,存入memory)
```

---

### 高级：版本治理 + 回滚

**目标**：把 Skills 当团队资产，能升级、能回退、可审计。

**落地做法**：

1. 小范围灰度两版，对比"查出率、耗时、误报率"
2. 确定没问题再全量，有问题立即回滚
3. 预期效果：两周内误报率从 18% 压到 6%

```
team-skills/
  code-review/
    v1.0.0/Skill.md
    v1.1.0/Skill.md
    v2.0.0/Skill.md  # 当前版本
```

---

## Skill 创建指南：四项检查

创建或修改 Skill 时，分别检查触发准确性、结构健壮性、安全可靠性和持续改进。分层与拆分方法见 [[#SKILL.md 的定位：分层引用网络的根节点]] 和 [[#SKILL.md 拆分判断标准]]，下面补充具体的编写与验收做法。

### 触发准确性：description 写清使用边界

`description` 包含三要素：

1. **触发词**：用户会怎样表达需求，例如“review PR”“审查代码”“检查提交”。
2. **使用条件**：什么任务和上下文适合激活，例如已有指定 PR 或待提交的代码变更。
3. **跳过条件**：哪些相近请求不应激活，例如只解释代码审查概念，或要求直接编写功能。

保留简短的能力概述，避免只堆关键词；脚本名、命令、工具调用顺序和内部算法等实现细节放在主体或支持资源中。这样模型选 Skill 时能识别任务边界，不必提前理解整个实现。

```yaml
name: reviewing-code
description: >-
  审查指定 PR 或待提交代码变更中的缺陷与风险。
  当用户提出“review PR”“审查代码”“检查提交”，且存在明确的变更对象时使用。
  不用于仅解释代码审查概念或直接编写新功能的请求。
```

### 结构健壮性：每一步都有出口条件

遵守前文的三层分工、500 行篇幅目标和一跳引用原则。主体中的每个步骤还要写明动作、产出，以及何时继续、停止或转入其他分支。只写“检查”“处理”“验证”，Agent 很难判断任务做到什么程度才算完成。

| 步骤示例 | 预期产出 | 出口条件与失败处理 |
|----------|----------|--------------------|
| 读取输入 | 输入对象与范围清单 | 必填信息齐全才继续；缺失时明确列出缺口，暂停依赖该信息的步骤 |
| 生成方案或草稿 | 可检查的方案、差异或命令 | 产出覆盖已确认范围才继续；有歧义时先澄清 |
| 执行操作 | 实际执行结果 | 前置检查和所需确认通过后执行；失败时报告原因，按预设重试上限处理或停止 |
| 验收交付 | 结果、检查证据与未完成项 | 满足验收标准才标记完成；未通过时进入修正分支或说明阻塞 |

出口条件既包括成功条件，也包括失败、输入不足和需要用户决定的情况，防止流程静默跳步或无限重试。

### 安全可靠性：参数化、确认门与反模式

**避免硬编码敏感信息和环境绑定值**。真实 token、用户 ID、账号等不能写入 Skill 主体、参考文档或配套脚本；凭据从环境变量或凭据管理系统读取，用户 ID 等标识通过参数或运行时查询获得。示例使用占位符，避免将某次运行的身份和配置带入其他任务。

**为不可逆或高影响操作设置 Confirmation Gate**。发布、删除、覆盖重要文件等操作，先完成读取、草拟和必要校验，再展示目标、具体变更或执行命令、影响范围及可用的回退办法；获得用户明确确认后才执行。确认应针对可审阅的结果，不能只问一句“是否继续”。

写文件是否需要单独确认，要看写入的影响和已有授权：临时文件、草稿或用户已明确要求的可回滚编辑，可以按授权执行；会覆盖重要内容、对外发布或超出授权范围的写入，应在执行前停在确认门。不要把所有文件写入都视为不可逆操作，也不要让确认门阻断生成草稿和展示差异的准备工作。

在 Skill 中保留显式的反模式清单，并说明原因，例如：

- 不把凭据、真实用户 ID 等写死在正文、参考文件、脚本或示例中，避免泄露和跨环境误用。
- 不把“讨论方案”“生成草稿”推断为执行授权，避免在用户尚未审阅时产生实际变更。
- 不跳过失败步骤继续宣称完成，也不把工具查不到的信息补成确定事实；应报告失败和证据缺口。
- 不在操作失败后擅自扩大权限、变更范围或绕过确认门，避免把局部失败升级为更大影响。

### 持续改进：对比 Eval，并解释 WHY

每次修改 Skill 后，都跑 `with-skill` 与 `without-skill` 的对比 Eval，检查新增规则是否带来实际收益：

1. 固定测试任务、输入、模型、工具权限和评分标准，分别运行启用与不启用该 Skill 的两组测试。
2. 单独检查触发准确性：用“应该触发”“不应触发”和容易混淆的边界请求，观察误触发与漏触发。
3. 比较任务通过率、输出质量、越权或漏步骤情况，以及耗时和 token 成本；保留输入、输出和检查证据。
4. 修改后重跑同一组用例，并补充新发现的边界案例。改进已有 Skill 时，还可加入旧版本对照，判断新规则是否引入退化。

`with-skill` 与 `without-skill` 用于判断 Skill 相比模型原有能力增加了什么；新旧版本对照用于判断这次修改改善了什么。不能用一次成功演示代替对比评估。

**WHY 优先于堆叠 ALWAYS / NEVER**：解释规则解决什么问题、适用条件和例外，帮助 Agent 在边界情形下判断。例如，“覆盖文件前先展示差异，因为未审阅的覆盖可能丢失用户已有内容”，比只写“永远先确认”更清楚。安全边界仍需明确，原因说明与反模式清单共同约束行为。

对比评估和解释规则原因的做法可参见 [Anthropic 官方 skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)。

---

## Skill 质量治理：7 类失效模式与 Skill Craft

> 来源：[我做了一个 Claude Skill 质检工具](https://mp.weixin.qq.com/s/R2mdJlmrhwGp4CZvcQ7Tgg)
> 工具：[3stoneBrother/skill-craft](https://github.com/3stoneBrother/skill-craft)

### 问题：写出来 ≠ 用得稳

LLM 不是传统程序——你写下的"规则"，模型读到的可能只是"参考意见"。典型现象：Demo 阶段效果好，真实任务就出问题；对话一长，行为越来越飘；Skill 一多，路由边界越来越模糊。

### 7 类系统性失效模式

| # | 失效模式 | 表现 |
|---|---------|------|
| 1 | **约束衰减** | 对话前 5 轮严格执行规则，第 10 轮就变味，"越聊越跑偏" |
| 2 | **工具选择漂移** | 指定工具超时后，自行切换到替代方案，再也不回来 |
| 3 | **输出膨胀** | 要一段简明结论，回你一篇论文；快速消耗上下文，加速约束衰减 |
| 4 | **依赖链断裂** | Step 1 找到 29 个对象，Step 3 只处理了 20 个，9 个无声蒸发 |
| 5 | **并行孤岛** | 子 Agent 各自产出互相矛盾的结论，主 Agent 照单全收不做去重 |
| 6 | **触发模糊** | 用户随口问"方案怎么样"，Skill 误判为"请执行完整流程" |
| 7 | **幻觉填充** | 工具没查到结果，不说"没查到"，而是凭记忆"补一个像样的答案" |

> [!warning] 连锁触发
> 这些模式会互相放大：输出膨胀 → 上下文被挤满 → 约束衰减 → 工具漂移 + 步骤跳过 + 幻觉填充。

### Skill Craft 质检工具

Skill Craft 是面向 Claude Skill 的质量工程工具，覆盖 Skill 的完整生命周期：

| 模式 | 作用 |
|------|------|
| `check` | 评估单个 Skill 的质量（3 层评估体系打分） |
| `fix` | 基于审计结果修复 Skill，并做回归验证（修完重新评估，确认分数提升） |
| `create` | 从零生成结构完整、自带 smoke check 的新 Skill |
| `audit` | 系统层面审计多个 Skill 的路由边界、职责分工、一致性 |

**3 层评估体系**：

1. **8 个结构模块**：触发条件（触发/不触发/歧义处理）、行为准则、工具优先级、输出约束、流程 Checkpoint、依赖链、子 Agent 委派规则、幻觉防护
2. **7 类反模式风险**：结构是否真的能防住对应的失效模式
3. **3 条完整性原则**：
   - **可计数验收**：不写"逐个处理"，写"处理数必须等于总数"
   - **Checkpoint 阻断**：每步有中间输出，防止模型一口气跳到最后
   - **失败路径定义**：必须定义 else 分支，因为没写 else 时模型默认 skip

**fix 模式的关键**：修完后做 4 类关联检查——引用方、对称方、消费方、同层结构是否都同步更新。最常见的坑不是"改错了"，而是"只改了这一处，还有三处应该一起改"。

**安装与使用**：

```sh
# 放入 Skills 目录
cp -r skill-craft ~/.claude/skills/

# 直接对话触发
评估 /path/to/my-skill
```

---

# 三、Slash Commands（斜杠命令）

这是一个简单但极其好用的工具，用于手动标准化。

斜杠命令是手动触发的工作流快捷方式，存在 `.claude/commands/` 目录。

- **本质**：纯 Markdown 定义的多步骤流程，输入 `/命令名` 手动触发
- **API 注入**：作为用户消息扩展，而非系统提示工具（这是与 Skills 的核心区别）

命令内部可以：

- 调用 Skills 自动化检查
- 编排 SubAgents 并行工作
- 执行 MCP 工具链
- 串联 Git 操作

---

## Skills vs Slash Commands

| 对比项 | Skills | Slash Commands |
|--------|--------|---------------|
| 触发方式 | 自动（匹配用户意图） | 手动（`/命令名`） |
| 注入方式 | 作为 system prompt | 作为 user message |
| 适用场景 | 通用能力（代码审查、文档生成） | 固定流程（发版、回滚、入职） |
| 存放位置 | `.claude/skills/` | `.claude/commands/` |

---

## 入门：/powerup 交互式引导

输入 `/powerup` 启动官方提供的交互式功能发现课程。逐个功能引导体验（Shift+Tab 切换权限、`/goal` 自主执行、`/branch` 并行分支等），建议每个新用户都跑一遍。

---

## 内置斜杠命令速查

### 上下文管理

| 命令 | 作用 | 使用技巧 |
|------|------|---------|
| `/context` | 显示彩色网格展示上下文使用状况 | 每完成一轮大改动后看一眼，决定是继续还是先压缩 |
| `/compact` | 压缩对话历史，释放上下文空间 | 可带指令：`/compact 丢掉debug信息，但保留迁移方案的讨论` |
| `/clear` | 清空对话重新开始（保留 CLAUDE.md 配置） | 完成一个完整模块或对话方向需要大调整时使用 |

**使用策略**：修 bug 或小改动用 `/compact` 续命，完成完整模块或方向大调整时用 `/clear` 重启。

### 会话管理

| 命令        | 作用                       | 使用技巧                                  |
| --------- | ------------------------ | ------------------------------------- |
| `/resume` | 恢复之前保存的会话                | 可按名称恢复：`/resume auth-refactor`        |
| `/rename` | 给当前会话命名                  | 开始新任务时先命名，恢复时一目了然                     |
| `/branch` | 从当前对话状态创建并行分支            | 两个方案都想试时，各开一个分支互不干扰，把"试错成本"降到零        |
| `/rewind` | 回滚到对话中更早的某个点（别名 `/undo`） | Agent 改了不该改的文件时，比手动 `git checkout` 高效 |
| `/recap`  | 触发一行会话摘要                 | 中断后回来看一眼"之前在做什么"                      |

### 模型与推理控制

| 命令 | 作用 | 使用技巧 |
|------|------|---------|
| `/model` | 在 Sonnet/Opus/Haiku 之间切换 | 日常编码 Sonnet 够用，复杂架构设计切 Opus，批量改名用 Haiku |
| `/effort` | 设置推理深度（low → max 五级） | low 适合简单查询，high/max 适合并发 bug 分析。仅当前会话生效 |
| `/fast` | Opus 专属加速模式（最高 2.5 倍） | 赶进度时开，达到速率限制自动降速 |

### 代码审查

| 命令 | 作用 | 使用技巧 |
|------|------|---------|
| `/code-review` | 审查当前 diff 的正确性问题 | `--comment` 发到 PR 评论；`--fix` 直接修复；力度分 low/medium/high/max |
| `/diff` | 交互式 diff 查看器 | 比终端 `git diff` 可读性强，尤其多文件改动时 |
| `/simplify` | 专注代码清理（复用/简化/优化） | 不查 bug 只管整洁度，与 `/code-review` 搭配：先查正确性，再清理质量 |

### 自主模式

| 命令 | 作用 | 使用技巧 |
|------|------|---------|
| `/plan` | 进入计划模式，先研究再动手 | 对任务拆解没把握，或团队需先对方案达成共识时使用 |
| `/goal` | 设定完成条件，Agent 自主工作直到条件满足 | 把 Claude Code 从"对话助手"升级为"自主 Agent"，实时显示时间/轮次/token |
| `/batch` | 大规模多文件变更，使用隔离 worktree | 50 个文件统一加 license header、批量 API 版本迁移 |
| `/loop` | 按固定间隔重复运行任务 | `/loop 2m 检查最新issue并自动回复` |

---

## 快捷键

### 权限与模式切换

| 快捷键 | 作用 |
|--------|------|
| **Shift+Tab** | 在权限模式间循环切换（default → acceptEdits → plan → auto） |
| **Option+T** (macOS) / **Alt+T** | 切换 Extended Thinking 开关 |
| **Ctrl+B** | 把正在运行的命令/Agent 放到后台（测试在跑时继续聊别的） |

### 搜索与编辑

| 快捷键 | 作用 |
|--------|------|
| **Ctrl+R** | 反向搜索命令历史（Ctrl+S 切换搜索范围：当前会话/项目/全部） |
| **Ctrl+U** | 清除整个输入缓冲区 |
| **Ctrl+Y** | 恢复 Ctrl+U 清除的内容 |
| **Ctrl+G** | 在外部编辑器中打开当前计划 |
| **Ctrl+L** | 强制全屏重绘并清除输入 |

---

## 三个隐藏关键词

这三个不是斜杠命令，而是在正常对话中嵌入的特殊关键词：

| 关键词 | 效果 | 适用场景 |
|--------|------|---------|
| **ultrathink** | 深度推理模式，无视当前 effort 设置 | debug 多轮找不到根因、架构设计拿不准、并发竞态条件分析 |
| **ultracode** | 触发 Workflow 运行，启动多个子 Agent 并行工作 | 大规模扫描任务（如全项目 API 安全漏洞审查） |
| **ultraplan** | 规划任务交给云端 Claude Code on the web 处理 | 复杂规划任务，本地终端保持空闲继续做其他事 |

**用法**：直接在提示中嵌入即可，不需要额外语法——`ultrathink 分析这段代码的并发问题`。

> [!tip] 日常高频五件套
> `/compact` 管上下文、`/resume` 管会话、`/code-review` 管代码质量、Shift+Tab 管权限、ultrathink 管推理深度。先把这五个用熟，其余按需查。

---

## 推荐资源

| 资源 | 定位 | 地址 |
|------|------|------|
| **learn.shareai.run** | 源码逆向工程拆解 Claude Code 内部架构（20 章，五层架构） | https://learn.shareai.run/zh/ |
| **claude.nagdy.me** | 实用速查手册（命令/CLI 标志/权限模式/环境变量） | https://claude.nagdy.me/learn/slash-commands/ |

---

## 自定义斜杠命令

除了内置命令，Claude Code 支持在 `.claude/commands/` 目录下自定义命令，将团队工作流标准化为一键触发。

### 典型场景

1. `/release` — 完整发版流程（测试 → 构建 → 打 tag → 发布 → 通知）
2. `/security-check` — 安全扫描（依赖漏洞 + 代码审计 + 配置检查）
3. `/perf-audit` — 性能审计（包体积 + 加载时间 + 运行时分析）
4. `/refactor-plan` — 重构规划（架构分析 + 影响评估 + 迁移方案）
5. `/onboard` — 新人入职（克隆仓库 + 环境配置 + 文档导览）
6. `/rollback` — 紧急回滚

---

## 使用示例

### 示例 1：版本发布

**定义命令**：建文件 `.claude/commands/release.md`

```markdown
# 版本发布流程

1、拉最新代码确认版本号
2、触发Skills检查:代码审查、完整测试、资源检查
3、生成changelog
4、预发布测试
5、人工确认
6、正式发布
7、发通知
```

**使用**：直接输入 `/release`

**效果**：整个团队按统一流程走,不会漏步骤。版本发布出错率从 15% 降到 0。

### 示例 2：带确认步骤的发版

在 `.claude/commands/` 目录下创建 `release.md`：

```markdown
# 版本发布流程
你是发布助手,帮助用户安全发布版本。

## 执行步骤
1、确认当前Git分支是main
2、拉取最新代码(git pull)
3、触发Skills:
- pre-commit-check(代码质量)
- test-coverage-check(测试覆盖率>80%)
4、询问版本号(major.minor.patch)
5、生成changelog(基于Git commit)
...

## 每步都需要用户确认
不要自动执行,每步输出命令,等用户确认。
```

验证：输入 `/release`，看是否触发完整流程。

---

# 四、Plugin（插件）

Plugin（插件）是应用级打包容器，用来打包其他四个工具。

一个 Plugin 可以包含：

| 组成 | 数量上限 |
|------|---------|
| Skills | 5 |
| Slash Commands | 10 |
| MCP 服务器 | 3 |
| SubAgents | 2 |
| Hooks | 若干 |

## 适合场景

1. 团队标准化工具打包、快速分享工作流、一键安装完整套件
2. 临时用一次，快速试试某个功能

## 缺点

装太多会卡，而且大部分功能都重复。

> [!tip] 建议
> 个人用全局配置，团队用 Plugins 打包分发。别超过 3 个，够用就行。

---

# Skill/Plugin 推荐

## 官方 Skills仓库：
[anthropics/skills](https://github.com/anthropics/skills.git)

## 开源 Skills 仓库：

- 该项目收集了各种实用 Skill，采用模块化设计。比如文档处理、开发、数据分析、营销、写作创意啥的都有：[ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)、[BehiSecc/awesome-claude-skills](https://github.com/BehiSecc/awesome-claude-skills)
- 传统的 Claude Code Skill 需要你手动记忆和调用，而这个项目通过创新的钩子机制，实现了 Skill 的智能自动触发。当你输入提示或操作文件时，系统会自动分析上下文，并建议最相关的技能：[claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase)
- 强迫 Claude 按高级工程师标准流程工作的 Skills 套件，详见下方"开源 Plugin 推荐"中的 [obra/superpowers](#obra/superpowers) 章节
## 用 Skill 创建 Skill

Anthropic 官方有一个帮助创建 Skill 的 Skill：[skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
告诉 Claude Code 基于当前的 Skill 草稿，调用 skill-creator 来创建一个完整的 skill，名称为 xxx。创建或迭代时，对照 [[#Skill 创建指南：四项检查]] 检查触发、结构、安全与 Eval。

## Obsidian Skill

> [!info] 仓库地址
> [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)

obsidian-skills 直接把 Obsidian 专家集成在 Claude Code 里，仓库包含三个核心技能 Skill：

- **obsidian-markdown**：Obsidian 风格的 Markdown 书写，各种专有格式都支持
- **obsidian-bases**：`.base` 类数据库视图，支持过滤、公式、汇总
- **json-canvas**：`.canvas` 无限画布文件格式，可以实现点、连线、分组

**安装**：

```sh
/plugin marketplace add kepano/obsidian-skills
/plugin install obsidian@obsidian-skills
```

## Excalidraw 手绘架构图Skill

> [!info] 地址
> - GitHub：[github/awesome-copilot - excalidraw-diagram-generator](https://github.com/github/awesome-copilot/blob/main/skills/excalidraw-diagram-generator/)
> - Skills 市场：[skills.sh](https://skills.sh/github/awesome-copilot/excalidraw-diagram-generator) | [skillsmp.com](https://skillsmp.com/zh/skills/github-awesome-copilot-skills-excalidraw-diagram-generator-skill-md)

一句话用自然语言生成可编辑的 **Excalidraw** 手绘风格图。支持流程图、架构图、思维导图、时序图、ER 图、泳道图、类图、数据流图等 9 种图表类型。

**安装**：

```sh
npx skills add https://github.com/github/awesome-copilot --skill excalidraw-diagram-generator
```

**工作原理**：分析需求 → 提取节点与关系 → 匹配 8 个内置模板之一 → 生成符合 Excalidraw 规范的 JSON → 输出 `.excalidraw` 文件（VS Code 安装 Excalidraw 扩展即可直接打开编辑）。

**用法**：直接告诉 Claude `生成一个用户登录流程图`，即自动调用该 Skill 生成 `.excalidraw` 文件。

> [!note]
> 图的质量取决于模型能力，建议搭配较强的大模型使用。Claude Code 和 OpenClaw 都可用。
## obra/superpowers

> [!info] 仓库
> [obra/superpowers](https://github.com/obra/superpowers) — 强迫 AI 按高级工程师标准流程工作的 Skills 套件

Superpowers 的核心理念：**AI 写代码太随意，需要用结构化流程约束它**。安装后 Claude 的行为模式变为：收到需求 → 头脑风暴 → 制定计划 → TDD 写测试 → 写代码通过测试 → 代码审查 → 验证完成。

**强制工作流**（每个阶段必须完成才能进入下一个）：

1. **Brainstorming** — 头脑风暴，拒绝直接写代码，必须先出设计方案并获批准
2. **Git Worktrees** — 在独立分支上创建隔离工作区
3. **Writing Plans** — 将设计拆解为细粒度任务，假设执行者零上下文
4. **Subagent-Driven Development** — 子智能体隔离执行，双阶段审查（规格合规 + 代码质量）
5. **Test-Driven Development** — 强制 RED → GREEN → REFACTOR 循环
6. **Code Review** — 提交前对照计划自查
7. **Finishing Branch** — 验证测试通过，决定合并或 PR

**Skills 全表**：

| 分类 | Skill | 作用 |
|------|-------|------|
| 测试 | test-driven-development | 强制 TDD RED-GREEN-REFACTOR |
| 测试 | writing-skills | 用 TDD 方式编写新 Skill 文档 |
| 调试 | systematic-debugging | 4 阶段根因分析（定位/追踪/防御/条件等待） |
| 调试 | verification-before-completion | 修复后必须彻底验证才能标记完成 |
| 协作 | brainstorming | 想法 → 设计文档，设有 hard-gate 禁止跳过 |
| 协作 | writing-plans | 输出零上下文可执行的详细任务计划 |
| 协作 | executing-plans | 分批执行计划（无子智能体平台的降级方案） |
| 协作 | subagent-driven-development | 子智能体隔离开发 + 双阶段审查 |
| 协作 | dispatching-parallel-agents | 多子智能体并行工作流管理 |
| 协作 | requesting-code-review | 提交前自查清单 |
| 协作 | receiving-code-review | 响应审查反馈的规范流程 |
| 协作 | using-git-worktrees | Git worktree 并行开发 |
| 协作 | finishing-a-development-branch | 分支完成验证与合并/PR 决策 |
| 思维 | collision-zone-thinking | 跨领域概念碰撞产生洞见 |
| 思维 | inversion-exercise | 反转假设发现隐藏约束 |
| 思维 | meta-pattern-recognition | 识别跨领域通用模式 |
| 思维 | scale-game | 极端条件测试暴露本质问题 |
| 思维 | simplification-cascades | 寻找能消除多个组件的简化洞见 |
| 思维 | when-stuck | 卡住时分派到合适的思维技巧 |
| 研究 | tracing-knowledge-lineages | 追溯想法的演进脉络 |
| 架构 | preserving-productive-tensions | 维持多种有效方案，避免过早收敛 |
| 元技能 | using-superpowers | 1% 规则：有丝毫可能就必须调用对应 Skill |

**安装**：

```sh
# Claude Code 官方市场
/plugin install superpowers@claude-plugins-official

# 或通过 Plugin Marketplace
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

> [!note]
> 跨平台支持：除 Claude Code 外还支持 Cursor、Codex、OpenCode、GitHub Copilot CLI、Gemini CLI。

## andrej-karpathy-skills

> [!info] 仓库
> [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) — 仅 2.3K 的 CLAUDE.md 文件，GitHub 全球热榜，46.5K 星。

这个项目把 Andrej Karpathy 观察到的 LLM 编程三大祖传毛病，浓缩成 4 条行为准则，写进 CLAUDE.md 让 Claude Code "乖乖听话"。

**LLM 编码三大痛点**：

1. **默默做错误假设**：不确定的地方不问你，自己猜，猜完接着写，bug 就埋进去了
2. **把简单问题复杂化**：50 行能搞定的事，整出 200 行抽象 API
3. **乱改不相干的代码**：让它修一个函数，它顺便把隔壁的注释删了，格式也"优化"了

**四条核心原则**：

| 原则                        | 要点                                      |
| ------------------------- | --------------------------------------- |
| **Think Before Coding**   | 不确定就问，不要闷头猜。主动说"这里我假设了 X，你确认吗"          |
| **Simplicity First**      | 不加没人要求的功能，不为只用一次的代码建抽象，200 行能写成 50 行就重写 |
| **Surgical Changes**      | 只动必须改的地方，不"顺便优化"相邻代码，不重构没坏的东西           |
| **Goal-Driven Execution** | 给目标而非命令。"添加验证" → "为无效输入写测试，然后让它们通过"     |

**效果判断标准**：
- PR 的 diff 变干净了，没有莫名其妙的格式改动
- 代码第一次就足够简单，不用返工
- Claude 开始在动手之前先问问题
- PR 不再附带一堆"顺手重构"

**安装**：

```sh
# 方式一：Plugin 安装（注册为按需 Skill，不自动生效）
/plugin marketplace add forrestchang/andrej-karpathy-skills
/plugin install andrej-karpathy-skills@karpathy-skills

# 方式二：全局生效（写入用户级 CLAUDE.md，所有项目自动加载）— 推荐
curl -s https://raw.githubusercontent.com/forrestchang/andrej-karpathy-skills/main/CLAUDE.md > ~/.claude/CLAUDE.md

# 方式三：单个项目生效（下载到项目根目录）
curl -o CLAUDE.md https://raw.githubusercontent.com/forrestchang/andrej-karpathy-skills/main/CLAUDE.md

# 方式四：追加到已有项目 CLAUDE.md
echo "" >> CLAUDE.md
curl -s https://raw.githubusercontent.com/forrestchang/andrej-karpathy-skills/main/CLAUDE.md >> CLAUDE.md
```

> [!warning] Plugin 安装 ≠ 自动生效
> 实测发现：方式一（Plugin）安装后，Karpathy 准则只是**注册在可用 Skill 列表中**，不会自动注入 system prompt。只有显式调用 `/karpathy-guidelines` 时才加载——日常编码不会自动约束。
>
> **如果想让准则始终生效，必须写进 CLAUDE.md。** CLAUDE.md 分两级：
> - **用户级** `~/.claude/CLAUDE.md`：全局生效，所有项目自动加载（推荐方式二）
> - **项目级** 项目根目录 `CLAUDE.md`：仅对当前项目生效（方式三/四）
>
> CLAUDE.md 在每次会话启动时自动作为 system prompt 加载，4 条准则会成为 Claude 所有行为的底线约束。
>
> 这揭示了 Skills 的一个重要机制差异：**Skills 是"可用"不是"始终激活"**，而 CLAUDE.md 是"始终激活"。对于行为准则型约束，CLAUDE.md 是唯一可靠的注入方式。

## davila7/claude-code-templates

> [!info] 仓库
> [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) — 500+ 组件的 Claude Code 模板市场，Web 界面：[aitmpl.com](https://aitmpl.com)

一个 CLI 工具 + 组件市场，提供 Agents、Commands、MCPs、Settings、Hooks、Skills、Templates 七大类组件，可按需安装到项目中。

**内置 Plugin 套件**：

| Plugin | 用途 | 包含组件 |
|--------|------|---------|
| **git-workflow** | Git 工作流自动化 | feature/release/hotfix 命令 + git-flow-manager Agent |
| **supabase-toolkit** | Supabase 全流程 | 备份/迁移/性能优化命令 + data-engineer Agent + PostgreSQL/MySQL MCP |
| **nextjs-vercel-pro** | Next.js + Vercel 开发 | 脚手架/组件生成/部署优化命令 + fullstack-developer Agent + Vercel MCP |
| **testing-suite** | 测试自动化 | E2E/单元/集成/视觉测试 |
| **documentation-toolkit** | 文档生成 | API 文档/用户指南/Changelog + technical-writer Agent |
| **performance-optimizer** | 性能优化 | Bundle 分析/缓存/图片优化/懒加载命令 |
| **project-management-suite** | 项目管理 | Sprint 规划/任务拆解/站会/复盘命令 |

**项目模板**：Common（通用）、JavaScript/TypeScript（React/Vue/Angular/Node.js）、Python（Django/Flask/FastAPI）、Ruby。

**安装**：

```sh
# 交互式浏览安装
npx claude-code-templates@latest

# 安装单个组件
npx claude-code-templates@latest --agent development-team/frontend-developer --yes
npx claude-code-templates@latest --command testing/generate-tests --yes

# Plugin 方式安装
/plugin marketplace add https://github.com/davila7/claude-code-templates
/plugin install plugin-name@claude-code-templates

# 安装项目模板
npx claude-code-templates@latest --template=react --yes
```

**附带工具**：`--analytics` 实时监控开发会话、`--chats` 移动端查看对话、`--health-check` 环境诊断、`--plugins` 插件管理面板。

## shanraisshan/claude-code-best-practice

> [!info] 仓库
> [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) — Claude Code 生产级最佳实践参考实现

这个项目不是简单的 Plugin，而是一套**从 Vibe Coding 到 Agentic Engineering 的完整进阶指南**，通过一个 TodoApp 示例项目演示如何用 Claude Code 的全部扩展机制构建生产级工作流。

**4 级进阶路径**：Low → Medium → High → Pro，逐级引入 Claude Code 的配置能力。

**核心架构模式**：**Command → Agent → Skill** 三层编排

| 层级 | 目录 | 作用 |
|------|------|------|
| Commands | `.claude/commands/` | 斜杠命令编排工作流入口 |
| Agents | `.claude/agents/` | 约束工具集 + 预加载 Skills 的专业子智能体 |
| Skills | `.claude/skills/` | YAML frontmatter 定义的可复用领域知识包 |
| Rules | `.claude/rules/*.md` | 路径匹配的自动生效编码规范 |
| Hooks | `.claude/hooks/` | 事件驱动脚本（如提交前通知） |

**进阶工作流**：
- **RPI（Research-Plan-Implement）**：复杂任务的三阶段多智能体协作流程
- **Cross-Model Development**：跨模型协作（规划 / QA / 实现 / 验证分别用不同模型）
- **Phase-Gated Development**：`/plan` 先只读探索设计，再进入编码阶段

**亮点**：
- 5 级配置优先级体系（全局 → 项目 → 本地覆盖）
- Agent 的 `MEMORY.md` 持久化学习机制
- 附带交互式幻灯片演示（`presentation/index.html`）
- 包含 Claude Agent SDK 与 CLI 系统提示词的对比分析报告

## OthmanAdi/planning-with-files

> [!info] 仓库
> [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) — 21.4K Star，MIT 协议，支持 17+ AI 平台

用 AI 做项目时常见的问题：聊着聊着就跑偏、做到一半忘目标、上下文一清空直接重来、反复踩同一个坑。Planning with Files 让 AI 把所有计划、进度、坑点全写成本地 Markdown 文件——文件化规划 + 外置记忆 + 错误自动记录。

**3 个核心文件**：

| 文件 | 用途 |
| --- | --- |
| `task_plan.md` | 任务计划与进度——分阶段任务列表，打勾推进 |
| `findings.md` | 资料、研究、结论——项目过程中的发现和决策记录 |
| `progress.md` | 过程记录、测试、日志——错误记录和执行日志 |

**核心价值**：

- 文件当记忆，关软件 / 清上下文 / 重启电脑都还在
- 先规划再动手，自动分阶段结构化推进
- 自动记坑，AI 下次自动避开，绝不重复犯错
- 清屏 / 重启后自动读取文件恢复进度
- 每一步对照计划，严格对齐目标不跑偏
- 任务成功率从 6.7% → 96.7%

**安装**：

```sh
npx skills add OthmanAdi/planning-with-files --skill planning-with-files -g
```

启动规划模式：`/plan`，AI 会自动生成 3 个核心文件并按计划执行。

> [!note] 支持平台
> Claude Code / Cursor / GitHub Copilot / Gemini / Hermes / Codex / OpenCode 等 17+ 平台。

## wshobson/agents

最大的 Claude Code Plugin Marketplace，详见 [[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams#开源 Agents 推荐|多智能体协作 — 开源 Agents 推荐]]。

```sh
/plugin marketplace add wshobson/agents
/plugin install <plugin-name>@claude-code-workflows
```

## 去AI味 skills
英文版： https://github.com/blader/humanizer/tree/main
中文版： https://github.com/op7418/Humanizer-zh
