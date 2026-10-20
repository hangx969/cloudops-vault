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

Claude Code 除了对话和代码生成，还提供 MCP、Skills、Slash Commands 和 Plugin 四层扩展机制，用于编排、复用和分发工作流。

| 层级 | 机制 | 本质 | 触发方式 | 注入方式 |
|------|------|------|---------|---------|
| 1 | **MCP** | 外部工具桥梁 | 自动（AI 判断需要时调用） | tool call |
| 2 | **Skills** | 自动触发的能力包 | 自动（匹配用户意图） | system prompt |
| 3 | **Slash Commands** | 手动触发的工作流 | 手动（`/命令名`） | user message |
| 4 | **Plugin** | 打包分发容器 | — | 包含以上所有 |

单个 Skill 提供一项能力，多个 Skill 可编排成流程；结合 MCP 和 SubAgent，可构建智能体。

---

# 一、MCP（Model Context Protocol）

MCP 是连接 AI 模型与外部工具、数据源的标准协议。通过 MCP Server，Claude Code 可以访问文件系统、数据库、API 和浏览器等资源。

- **协议模型**：Client（Claude Code）↔ Server（MCP 进程），通过 stdio 通信
- **安装方式**：`claude mcp add <name> -- <command>` 或在 JSON 配置文件中声明
- **配置位置**：用户全局 `~/.claude/settings.json` 或项目级 `.claude/settings.json`

---

## 常用 MCP 服务器

### context7

**场景**：查询最新框架文档（Next.js 15、React 19）、确认 API 参数和用法、了解库的最佳实践、常见问题与版本迁移方法。

用个人 GitHub 账号登录：[https://context7.com/](https://context7.com/)

**VSCode 扩展**：在扩展界面搜索 `@mcp context7` 并安装，再在 JSON 配置中添加 API Key：

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

通过 Docker 运行。在家目录的配置文件中加入 Docker 命令和 token，启动 colima 后即可连接 MCP。

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

**场景**：复杂技术选型（微服务 vs 单体、数据库选型）、架构决策（分层、模块边界、扩展性）、疑难 bug 分析（多因素交叉、隐蔽逻辑）、性能优化规划。

**实战案例**：“分析为什么我们的订单服务在高峰期会超时，考虑数据库、缓存、网络、并发锁、GC 等所有可能因素。”

**效果**：输出完整的分析过程：假设 → 验证 → 排除 → 聚焦 → 验证 → 结论。

---

### memory

长期记忆。

**安装**：

```sh
claude mcp add memory -- npx -y @modelcontextprotocol/server-memory
```

**场景**：记住项目约定（命名规范、错误码、配置路径）、团队遇到的问题（库的 bug、配置陷阱）和重要决策（选择原因与权衡）。

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

验证：下次提问时，检查 Claude 是否自动调用了这些规范。

---

### playwright

浏览器自动化。

```sh
claude mcp add playwright -- npx -y @executeautomation/playwright-mcp-server
```

**场景**：竞品监控、批量截图、自动化测试、数据抓取

**案例**：“打开这 5 个竞品官网，截图首页和定价页，保存到 `./analysis/`。”

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
Claude Code 可通过官方 GitHub MCP Server 读取或操作 PR、Issue。支持两种配置方式：

**方式 A：远程 HTTP（推荐）**
- 无需 Docker，由 GitHub 官方托管，配置最简单
- 前提：能访问 `api.githubcopilot.com`；GHES（私有部署）不支持
```bash
claude mcp add-json github '{"type":"http","url":"https://api.githubcopilot.com/mcp","headers":{"Authorization":"Bearer YOUR_GITHUB_PAT"}}'
# 全局可用加 --scope user
```

**方式 B：本地 Docker**
- Token 只在本机流转，不经过远程中转；GHES 场景只能用此方式
- 前提：本机需要 Docker 且保持运行
```bash
claude mcp add github -e GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_GITHUB_PAT -- docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server
```

**PAT 权限要求**：Contents / Pull requests / Metadata 至少 Read 权限（fine-grained token）或 `repo`（classic token）

**验证**：`claude mcp list` / `claude mcp get github`

**选型建议**：默认使用配置更简单的方式 A；GHES 私有部署或公司网络无法访问 `api.githubcopilot.com` 时，改用方式 B。

---

### exa

智能搜索服务，需要官网 key，依赖 axios 包。

- GitHub：[exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server)
- Exa API Key：[https://dashboard.exa.ai/home](https://dashboard.exa.ai/home)

```sh
claude mcp add exa -e EXA_API_KEY="" -- npx -y exa-mcp-server
```

**场景**：搜索最新信息、技术博客和开源项目，检索结果比普通搜索引擎更精准。

**优势**：

- **语义理解（Neural Search）**：支持自然语言检索。例如，搜索“关于 Transformer 架构的通俗易懂的教程”时，会理解“通俗易懂”和“教程”的含义，而不只是匹配字面关键词
- **结构化结果（Clean Data）**：清除网页中的广告、SEO 文案和复杂 HTML，返回干净文本或结构化数据，大幅减少 AI 处理杂乱信息的负担与幻觉
- **精确过滤**：可按域名（如只搜 github.com）、日期、内容类型（如 PDF、代码）筛选结果
- **相似内容检索**：提供一个网页链接，查找内容相似的其他网页，便于调研

---

### deepwiki

深度文档聚合。

```sh
claude mcp add deepwiki -- npx -y mcp-deepwiki
```

**场景**：聚合某个库的完整文档站点，覆盖比 context7 更全面，但速度较慢。

---

### drawio

> [!info] 仓库
> [jgraph/drawio-mcp](https://github.com/jgraph/drawio-mcp)

Draw.io 的 MCP 工具（`drawio-mcp`）将 AI 生成的 Mermaid、CSV、XML 数据转换为 Draw.io 专用链接，在浏览器中打开可编辑的图表。

流程如下：

1. 向 AI 提出需求，例如“画个 OAuth2 流程图”
2. AI 生成结构化数据
3. MCP 工具把数据压缩、编码
4. 浏览器自动打开 Draw.io 编辑页面，可拖动节点、修改内容和配色

根据 GitHub 官方文档，这个 MCP Server 目前支持三种模式：

- **Mermaid 转图 (`open_drawio_mermaid`)**：最常用，由 AI 编写 Mermaid，Draw.io 负责渲染和后续编辑
- **CSV 转图 (`open_drawio_csv`)**：适合组织架构图、网络拓扑图，可根据人员名单和汇报关系生成树状图
- **XML 原生格式 (`open_drawio_xml`)**：支持现有 Draw.io XML，也可让 AI 按其结构生成最复杂的图表

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

**使用**：调用 draw.io MCP 工具 `open_drawio_mermaid`，制作 OAuth2 流程时序图

**导出**：导出为 xml，再在 Confluence 页面创建 draw.io diagram

---

### datadog

> [!info] 文档
> [Datadog MCP Server Setup](https://docs.datadoghq.com/bits_ai/mcp_server/setup/?tab=claudecode)

**场景**：在 Claude Code 中查询 Datadog 日志、指标、Trace、Dashboard、Monitor、Incident 等数据，支持 16 个产品 Toolset 按需加载。

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

**认证方式**：远程 HTTP 连接默认使用 OAuth 2.0，自动打开浏览器登录。无法使用 OAuth 时（如服务器环境），可通过 HTTP Header 传入 API Key 和 Application Key：

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
> 建议通过 [Service Account](https://docs.datadoghq.com/account_management/org_settings/service_accounts/) 创建 scoped API Key 和 Application Key，只授予所需权限。

> [!warning] 权限
> Datadog 用户角色需具备 `mcp_read` 和 `mcp_write` 权限（Standard Role 默认包含），以及对应资源的权限，例如读取 Monitor 需要 Monitors Read。自定义角色需在 [Organization Settings > Roles](https://app.datadoghq.com/organization-settings/roles) 中勾选 **MCP Read** 和 **MCP Write**。

**Toolset 机制**：通过 URL query 参数 `toolsets` 按产品域选择工具集，节省 context window：

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

**和 MCP 的区别**：Skills 的范围更大，既能调用 MCP，也能包含 Python 脚本。

一个 Skill 是包含技能描述、脚本和示例代码等内容的文件夹。

例如，在 `SKILL.md` 中写入生成 PPT 的固定流程后，向 Claude 提出“帮我生成 PPT”即可激活，无需每次重复说明要求。

---

## 解决痛点

### 痛点 1：重复劳动

- **之前**：每次都要重复说明规则（“用现在时”“50 字以内”“说 what 和 why”）
- **现在**：将规则打包成 Skill，一句话即可自动应用

### 痛点 2：团队协作混乱

- **场景**：10 个人用 10 种方式生成文档，格式不统一
- **解决**：
  1. 把 Skill 提交到项目代码库：`.claude/skills/company-doc-generator/`
  2. 团队成员 `git pull` 后自动同步
  3. 全员统一规范

### 痛点 3：知识无法沉淀

- **之前**：老员工调试 API 的经验难以传给新人
- **现在**：将经验写成 Skill，新人克隆代码即可复用

---

## 渐进式披露机制（Progressive Disclosure）

Anthropic 将这种按需分阶段加载的方式称为 **Progressive Disclosure**："Claude loads information in stages as needed, rather than consuming context upfront."（按需分阶段加载，而不是一次性占满上下文）。

上下文和模型注意力有限。启动时载入所有工作流、模板和示例，会分散模型对当前任务的关注。

### 官方三层加载机制

| Level | 加载时机 | Token 成本 | 内容 |
|-------|----------|-----------|------|
| **Level 1（Metadata）** | 永远加载（系统启动时） | **~100 tokens / 每个 Skill** | YAML frontmatter 中的 `name` + `description` |
| **Level 2（Instructions）** | Skill 被触发时 | **< 5K tokens** | SKILL.md 主体内容 |
| **Level 3+（Resources）** | 按需 bash 读取 | 实际无限 | 引用文件、脚本、模板等 |

**字段限制与篇幅建议**：

- `name`：最多 **64 字符**，只能小写字母+数字+连字符，不能含 "anthropic" 或 "claude"
- `description`：最多 **1024 字符**，必须非空，不能含 XML 标签
- `SKILL.md` 主体：控制在 **500 行以内**，接近这一规模就拆出详细文档、示例和模板。行数是拆分参考，不能与 token 数或中文字数固定换算，也不是运行时的硬性截断限制

500 行和下文的一跳引用原则来自 [Anthropic Skill 编写最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#progressive-disclosure-patterns)。

Anthropic 因此鼓励安装多个细分 Skill。50 个 Skill 的 Level 1 合计约 5K token。

### SKILL.md 的定位：分层引用网络的根节点

`SKILL.md` 是执行入口和资源索引。Skill 分为三层，分别负责触发、执行和按需提供资料：

| 层级 | 负责什么 | 放什么内容 |
|------|----------|------------|
| `description` | 判断何时触发、何时跳过 | 能力概述、用户会说的触发词、使用条件、跳过条件；不写实现细节 |
| `SKILL.md` 主体 | 执行主逻辑 | 工作流骨架、决策分支、步骤出口条件，以及何时读取哪个资源 |
| 支持资源 | 提供执行时才需要的细节 | `references/` 放参考文档，`scripts/` 放脚本，`assets/` 放模板等资源 |

第三层统称支持资源，脚本和模板无需都放入 `references/`。主文件保留流程和资源入口，参考文档提供细节，避免重复维护规则。

规则案例、模板正文、长篇示例和参考代码统一放入 Level 3 引用文件，主文件只保留流程与索引。

> [!tip] 主文件保留执行入口
> 在 `SKILL.md` 中提供 quick start，再指向表单处理、API 参考等详细文档。拆分时关注流程是否清楚、细节是否按需加载，不只看文件长短。

### SKILL.md 拆分判断标准

| SKILL.md 行数 | 状态 | 建议 |
|---------------|------|------|
| < 200 行 | 较短 | 流程清楚时无需为拆而拆 |
| 200-500 行 | 需要控制增长 | 新增内容前先判断是否应放入支持资源 |
| > 500 行 | 超出本指南的篇幅目标 | 将详细文档、示例和模板拆到支持资源，主文件保留决策和执行步骤 |

**拆分优先级**：
1. 先拆出**示例和模板**：篇幅长、访问频率低，占用 token 多
2. 再将**详细规则**拆到 `references/rules.md`，主文件只留“风格规则见 references/rules.md”
3. 将**长流程**封装成脚本，供模型通过 bash 调用

**保留决策树**：主文件应写清哪种请求对应哪个工作流、各分支如何处理，模型读完才知道下一步做什么。

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

好的引用说明读取目的和检查重点，模型据此判断是否需要读取；只给文件名，模型要么跳过，要么每次全文读取，浪费 token。

**执行所需的引用链最多一跳**：由 `SKILL.md` 直接索引资源，避免把必读资料藏在下一层。例如，`references/A.md` 依赖 `references/B.md` 时，应在 `SKILL.md` 中分别写明 A、B 的用途和读取条件，避免形成 `SKILL.md → A.md → B.md` 的必读链，也要消除循环引用。

Agent 按需读取文件，不保证递归展开链接。深层引用可能只被预览或遗漏；一跳原则用于减少漏读，并非技术上无法继续读取。

### 实战演进案例

一个写作 SKILL 文件经过三版迭代：

| 指标 | V1（单文件 1900 行） | V3（主文件 612 行 + 引用） |
|------|---------------------|--------------------------|
| 触发时初始 token 注入 | ~14,000 | ~4,500 |
| 单次工作流端到端 token | ~28,000 | ~12,000 |
| "写错风格"频率 | 每 20 次约 1 次 | 几乎归零 |
| 维护成本（改一条规则） | 全文件找位置 | 单子文件改 |

V1 将写作规则、文风指南、案例分析、模板、配图规范和上传脚本说明集中在一个 SKILL.md 中，远超 500 行的篇幅目标；公众号、算法、知乎等不同类型文章的规则相互干扰。V3 已有改善，但主文件仍有 612 行，还应继续拆分。

V3 主文件只保留触发条件、10 步工作流和引用索引，其余拆出：
- 文风规范 → `references/style-guide.md`
- 历史范本 → `references/article_*.md`
- 代码逻辑 → `scripts/*.py`
- 配置数据 → `config/*.json`

**Skill 间的 handoff 设计**：写作 SKILL 最后需要生成视频时，先复制视频模板、注入 input.md，再显式交给视频 SKILL。写作主文件无需包含视频生成细节，各 Skill 只处理自己的任务，通过交接衔接流程。

---

## 组成结构

Skill 文件夹通常包含：

- **SKILL.md**：核心文件，以 YAML 定义名称、描述等元数据，以 Markdown 编写使用条件和执行指令
- **scripts/**：存放可执行的 Python、Shell 脚本
- **references/**：参考文档，如 API 文档、数据库 Schema、公司政策，供 Claude 按需读取
- **assets/**：PPT 模板、Logo、项目脚架等资源，供执行时使用

---

## 安装

**手动安装**：

- 个人 Skills：`~/.claude/skills/`
- 项目 Skills：`.claude/skills/`
- 创建与 skill 同名的子目录，并在其中创建 `SKILL.md`

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

Claude 可将 skill 打包为 `xxx.skill` 文件，分享给其他人安装。

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

将重复操作封装为技能，让 Claude 自动识别场景，减少重复编写提示词。

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
> 人工审查经常遗漏关键问题。提出“review 这个 PR”后，Skill 自动按文件类型专项检查，不遗漏应检查的问题。团队线上事故率下降 60%。

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
> 将依赖评估放在升级之前，完整列出注意事项，避免升级后才发现问题。

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

一个技能适配多个项目，多个技能串联成流水线。

#### 案例：生产事故应急响应

`incident-response`：

> [!success] 效果
> 线上故障原先依赖经验排查。提出“线上订单服务挂了”后，5 分钟内输出完整分析和 3 套止损方案。平均故障恢复时间从 45 分钟降到 12 分钟。

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
> 每周明确 3 个技术债处理目标，结合 SonarQube 等工具，由 Skill 排定优先级并生成报告。

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

**目标**：将 Skills 作为团队资产管理，支持升级、回退和审计。

**落地做法**：

1. 小范围灰度两版，比较查出率、耗时和误报率
2. 确认无误后全量使用，发现问题立即回滚
3. 预期效果：两周内误报率从 18% 降至 6%

```
team-skills/
  code-review/
    v1.0.0/Skill.md
    v1.1.0/Skill.md
    v2.0.0/Skill.md  # 当前版本
```

---

## Skill 创建指南：四项检查

创建或修改 Skill 时，检查触发准确性、结构健壮性、安全可靠性和持续改进。分层与拆分方法见 [[#SKILL.md 的定位：分层引用网络的根节点]] 和 [[#SKILL.md 拆分判断标准]]。

### 触发准确性：description 写清使用边界

`description` 包含三要素：

1. **触发词**：用户会怎样表达需求，例如“review PR”“审查代码”“检查提交”。
2. **使用条件**：适合激活的任务和上下文，例如已有指定 PR 或待提交的代码变更。
3. **跳过条件**：不应激活的相近请求，例如只解释代码审查概念，或要求直接编写功能。

用简短的能力概述说明任务边界，不只堆关键词。脚本名、命令、工具调用顺序和内部算法等实现细节放在主体或支持资源中，模型选 Skill 时无需先理解实现。

```yaml
name: reviewing-code
description: >-
  审查指定 PR 或待提交代码变更中的缺陷与风险。
  当用户提出“review PR”“审查代码”“检查提交”，且存在明确的变更对象时使用。
  不用于仅解释代码审查概念或直接编写新功能的请求。
```

### 结构健壮性：每一步都有出口条件

结构健壮性要落实到四项：

1. **三层职责分开**：`description` 负责何时触发，`SKILL.md` 主体负责执行步骤，`references/` 等支持资源存放详细资料，避免混写。
2. **每一步都有出口条件**：写清动作、产出，以及何时继续、停止或转入其他分支。只写“检查”“处理”“验证”，Agent 难以判断何时完成。
3. **引用链最多一跳**：`SKILL.md` 引用 `references/A.md` 后，A.md 不应再通过引用 `references/B.md` 来提供下一步必读内容。如果需要 B.md，应直接在 `SKILL.md` 中引用它。Agent 按需读取文件，不会仅因 A.md 中有链接就自动加载 B.md，因此不能依赖 `SKILL.md → A.md → B.md` 这样的逐层引用。
4. **`SKILL.md` 主体不超过 500 行**：超过就把详细说明、规则和长篇示例拆到 `references/`，主体只保留执行步骤、判断分支和参考文件入口。

步骤的产出和出口条件可以按下表编写：

| 步骤示例 | 预期产出 | 出口条件与失败处理 |
|----------|----------|--------------------|
| 读取输入 | 输入对象与范围清单 | 必填信息齐全才继续；缺失时明确列出缺口，暂停依赖该信息的步骤 |
| 生成方案或草稿 | 可检查的方案、差异或命令 | 产出覆盖已确认范围才继续；有歧义时先澄清 |
| 执行操作 | 实际执行结果 | 前置检查和所需确认通过后执行；失败时报告原因，按预设重试上限处理或停止 |
| 验收交付 | 结果、检查证据与未完成项 | 满足验收标准才标记完成；未通过时进入修正分支或说明阻塞 |

出口条件应涵盖成功、失败、输入不足和需要用户决定的情况，防止静默跳步或无限重试。

### 安全可靠性：参数化、确认门与反模式

**避免硬编码敏感信息和环境绑定值**。Skill 主体、参考文档和配套脚本不能写入真实 token、用户 ID、账号等。凭据从环境变量或凭据管理系统读取，标识通过参数或运行时查询获取；示例使用占位符，避免泄露或跨环境误用。

**为不可逆或高影响操作设置 Confirmation Gate**。发布、删除、覆盖重要文件前，先完成读取、草拟和必要校验，再展示目标、具体变更或命令、影响范围及可用的回退办法，获得用户明确确认后执行。确认应针对可审阅的结果，不能只问“是否继续”。

文件写入是否需要单独确认，取决于影响和已有授权。临时文件、草稿或用户已明确要求的可回滚编辑，可按授权执行；覆盖重要内容、对外发布或超出授权范围的写入，须先经过确认门。写文件不一定不可逆，生成草稿和展示差异也不应被确认门阻断。

在 Skill 中列出明确的反模式并解释原因，例如：

- 不在正文、参考文件、脚本或示例中写死凭据、真实用户 ID 等，避免泄露和跨环境误用。
- 不把“讨论方案”“生成草稿”当作执行授权，避免未经审阅就产生实际变更。
- 不跳过失败步骤后宣称完成，不把工具查不到的信息补成确定事实；应报告失败和证据缺口。
- 不因操作失败而擅自扩大权限、范围或绕过确认门，避免扩大影响。

### 持续改进：对比 Eval，并解释 WHY

每次修改 Skill 后，运行 `with-skill` 与 `without-skill` 对比 Eval，检查新增规则的实际收益：

1. 固定任务、输入、模型、工具权限和评分标准，分别运行启用与不启用该 Skill 的两组测试。
2. 单独测试触发：覆盖应该触发、不应触发及容易混淆的边界请求，检查误触发和漏触发。
3. 比较任务通过率、输出质量、越权或漏步骤情况、耗时和 token 成本，保留输入、输出和检查证据。
4. 修改后重跑同一组用例，并补充新发现的边界案例。改进已有 Skill 时，可增加旧版本对照，检查是否退化。

`with-skill` 与 `without-skill` 检验 Skill 相对模型原有能力的增益；新旧版本对照检验本次修改的效果。一次成功演示不能替代对比评估。

**WHY 优先于堆叠 ALWAYS / NEVER**：说明规则要解决的问题、适用条件和例外，帮助 Agent 判断边界。例如，“覆盖文件前先展示差异，因为未审阅的覆盖可能丢失用户已有内容”，比“永远先确认”更清楚。安全边界仍须明确，并结合原因说明和反模式清单约束行为。

对比评估和解释规则原因的做法可参见 [Anthropic 官方 skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)。

---

## Skill 质量治理：7 类失效模式与 Skill Craft

> 来源：[我做了一个 Claude Skill 质检工具](https://mp.weixin.qq.com/s/R2mdJlmrhwGp4CZvcQ7Tgg)
> 工具：[3stoneBrother/skill-craft](https://github.com/3stoneBrother/skill-craft)

### 问题：写出来 ≠ 用得稳

LLM 可能只把文本规则当作参考。常见问题是：Demo 阶段表现好，真实任务却出问题；对话变长后行为偏移；Skill 增多后触发边界模糊。

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
> 这些模式会相互放大：输出膨胀 → 上下文被占满 → 约束衰减 → 工具漂移、步骤跳过和幻觉填充。

### Skill Craft 质检工具

Skill Craft 是 Claude Skill 质量工程工具，覆盖完整生命周期：

| 模式 | 作用 |
|------|------|
| `check` | 评估单个 Skill 的质量（3 层评估体系打分） |
| `fix` | 基于审计结果修复 Skill，并做回归验证（修完重新评估，确认分数提升） |
| `create` | 从零生成结构完整、自带 smoke check 的新 Skill |
| `audit` | 系统层面审计多个 Skill 的路由边界、职责分工、一致性 |

**3 层评估体系**：

1. **8 个结构模块**：触发条件（触发/不触发/歧义处理）、行为准则、工具优先级、输出约束、流程 Checkpoint、依赖链、子 Agent 委派规则、幻觉防护
2. **7 类反模式风险**：检查结构能否防住对应的失效模式
3. **3 条完整性原则**：
   - **可计数验收**：将“逐个处理”改为“处理数必须等于总数”
   - **Checkpoint 阻断**：每步提供中间输出，防止跳到最后
   - **失败路径定义**：必须定义 else 分支，未定义时模型会默认跳过

**fix 模式的关键**：修复后检查引用方、对称方、消费方、同层结构这 4 类关联，确保相关位置同步更新，避免只修一处而遗漏其他位置。

**安装与使用**：

```sh
# 放入 Skills 目录
cp -r skill-craft ~/.claude/skills/

# 直接对话触发
评估 /path/to/my-skill
```

---

# 三、Slash Commands（斜杠命令）

斜杠命令将标准化工作流封装为手动触发的快捷方式，保存在 `.claude/commands/` 目录。

- **本质**：纯 Markdown 定义的多步骤流程，输入 `/命令名` 手动触发
- **API 注入**：作为用户消息扩展，区别于 Skills 的系统提示注入

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

输入 `/powerup` 启动官方交互式功能发现课程，逐项体验 Shift+Tab 权限切换、`/goal` 自主执行、`/branch` 并行分支等功能，建议新用户运行一次。

---

## 内置斜杠命令速查

### 上下文管理

| 命令 | 作用 | 使用技巧 |
|------|------|---------|
| `/context` | 显示彩色网格展示上下文使用状况 | 每完成一轮大改动后看一眼，决定是继续还是先压缩 |
| `/compact` | 压缩对话历史，释放上下文空间 | 可带指令：`/compact 丢掉debug信息，但保留迁移方案的讨论` |
| `/clear` | 清空对话重新开始（保留 CLAUDE.md 配置） | 完成一个完整模块或对话方向需要大调整时使用 |

**使用策略**：修 bug 或小改动时用 `/compact` 压缩上下文；完成一个模块或大幅调整方向时，用 `/clear` 重启。

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

这三个特殊关键词直接嵌入正常对话，无需使用斜杠命令：

| 关键词 | 效果 | 适用场景 |
|--------|------|---------|
| **ultrathink** | 深度推理模式，无视当前 effort 设置 | debug 多轮找不到根因、架构设计拿不准、并发竞态条件分析 |
| **ultracode** | 触发 Workflow 运行，启动多个子 Agent 并行工作 | 大规模扫描任务（如全项目 API 安全漏洞审查） |
| **ultraplan** | 规划任务交给云端 Claude Code on the web 处理 | 复杂规划任务，本地终端保持空闲继续做其他事 |

**用法**：直接写入提示，无需额外语法，例如 `ultrathink 分析这段代码的并发问题`。

> [!tip] 日常高频五件套
> 先熟悉这五项：`/compact` 管理上下文，`/resume` 恢复会话，`/code-review` 检查代码质量，Shift+Tab 切换权限，ultrathink 调整推理深度；其他功能按需查阅。

---

## 推荐资源

| 资源 | 定位 | 地址 |
|------|------|------|
| **learn.shareai.run** | 源码逆向工程拆解 Claude Code 内部架构（20 章，五层架构） | https://learn.shareai.run/zh/ |
| **claude.nagdy.me** | 实用速查手册（命令/CLI 标志/权限模式/环境变量） | https://claude.nagdy.me/learn/slash-commands/ |

---

## 自定义斜杠命令

除内置命令外，还可在 `.claude/commands/` 目录定义团队工作流，通过一条命令触发。

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

**定义命令**：创建文件 `.claude/commands/release.md`

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

**效果**：团队按统一流程发布，不遗漏步骤。版本发布出错率从 15% 降到 0。

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

验证：输入 `/release`，检查是否触发完整流程。

---

# 四、Plugin（插件）

Plugin（插件）是应用级容器，用于打包其他四个工具。

一个 Plugin 可以包含：

| 组成 | 数量上限 |
|------|---------|
| Skills | 5 |
| Slash Commands | 10 |
| MCP 服务器 | 3 |
| SubAgents | 2 |
| Hooks | 若干 |

## 适合场景

1. 打包团队标准工具、分享工作流，一键安装完整套件
2. 临时试用某项功能

## 缺点

安装过多会卡顿，大部分功能也重复。

> [!tip] 建议
> 个人使用全局配置，团队通过 Plugins 分发。数量不超过 3 个，按需安装。

---

# Skill/Plugin 推荐

## 官方 Skills仓库：
[anthropics/skills](https://github.com/anthropics/skills.git)

## 开源 Skills 仓库：

- 模块化 Skill 合集，涵盖文档处理、开发、数据分析、营销和创意写作：[ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)、[BehiSecc/awesome-claude-skills](https://github.com/BehiSecc/awesome-claude-skills)
- 传统 Claude Code Skill 需要手动记忆和调用；这个项目通过钩子分析输入提示或文件操作的上下文，自动触发并推荐相关技能：[claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase)
- 按高级工程师标准约束 Claude 工作流程的 Skills 套件，详见下方 [obra/superpowers](#obra/superpowers) 章节
## 用 Skill 创建 Skill

Anthropic 官方提供了用于创建 Skill 的 [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)。
让 Claude Code 根据现有草稿，调用 skill-creator 创建名为 xxx 的完整 skill。创建或迭代时，对照 [[#Skill 创建指南：四项检查]] 检查触发、结构、安全与 Eval。

## Obsidian Skill

> [!info] 仓库地址
> [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)

obsidian-skills 为 Claude Code 提供 Obsidian 支持，包含三个核心 Skill：

- **obsidian-markdown**：编写 Markdown，支持 Obsidian 各种专有格式
- **obsidian-bases**：创建 `.base` 数据库视图，支持过滤、公式和汇总
- **json-canvas**：创建 `.canvas` 无限画布，支持节点、连线和分组

**安装**：

```sh
/plugin marketplace add kepano/obsidian-skills
/plugin install obsidian@obsidian-skills
```

## Excalidraw 手绘架构图Skill

> [!info] 地址
> - GitHub：[github/awesome-copilot - excalidraw-diagram-generator](https://github.com/github/awesome-copilot/blob/main/skills/excalidraw-diagram-generator/)
> - Skills 市场：[skills.sh](https://skills.sh/github/awesome-copilot/excalidraw-diagram-generator) | [skillsmp.com](https://skillsmp.com/zh/skills/github-awesome-copilot-skills-excalidraw-diagram-generator-skill-md)

用一句自然语言生成可编辑的 **Excalidraw** 手绘图，支持流程图、架构图、思维导图、时序图、ER 图、泳道图、类图、数据流图等 9 种类型。

**安装**：

```sh
npx skills add https://github.com/github/awesome-copilot --skill excalidraw-diagram-generator
```

**工作原理**：分析需求 → 提取节点和关系 → 匹配 8 个内置模板之一 → 生成符合 Excalidraw 规范的 JSON → 输出 `.excalidraw` 文件（安装 VS Code 的 Excalidraw 扩展后即可打开编辑）。

**用法**：向 Claude 提出 `生成一个用户登录流程图`，即可自动调用该 Skill，生成 `.excalidraw` 文件。

> [!note]
> 图表质量取决于模型能力，建议使用较强的模型。支持 Claude Code 和 OpenClaw。
## obra/superpowers

> [!info] 仓库
> [obra/superpowers](https://github.com/obra/superpowers) — 按高级工程师标准约束 AI 工作流程的 Skills 套件

Superpowers 用结构化流程约束 AI 编程。安装后，Claude 按以下顺序工作：收到需求 → 头脑风暴 → 制定计划 → TDD 写测试 → 编码并通过测试 → 代码审查 → 验证完成。

**强制工作流**（每个阶段必须完成才能进入下一个）：

1. **Brainstorming** — 先完成头脑风暴和设计方案，获批后才能写代码
2. **Git Worktrees** — 在独立分支上创建隔离工作区
3. **Writing Plans** — 将设计拆为细粒度任务，供零上下文的执行者使用
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

这个项目将 Andrej Karpathy 观察到的 LLM 编程三大问题归纳为 4 条行为准则，写入 CLAUDE.md，约束 Claude Code 的行为。

**LLM 编码三大痛点**：

1. **默默做错误假设**：遇到不确定的信息时自行猜测，继续编码并引入 bug
2. **把简单问题复杂化**：50 行能解决的问题，写成 200 行抽象 API
3. **乱改不相干的代码**：修一个函数时，顺手删除相邻注释或调整格式

**四条核心原则**：

| 原则                        | 要点                                      |
| ------------------------- | --------------------------------------- |
| **Think Before Coding**   | 不确定就问，不要闷头猜。主动说"这里我假设了 X，你确认吗"          |
| **Simplicity First**      | 不加没人要求的功能，不为只用一次的代码建抽象，200 行能写成 50 行就重写 |
| **Surgical Changes**      | 只动必须改的地方，不"顺便优化"相邻代码，不重构没坏的东西           |
| **Goal-Driven Execution** | 给目标而非命令。"添加验证" → "为无效输入写测试，然后让它们通过"     |

**效果判断标准**：
- PR diff 没有无关的格式改动
- 首次提交的代码已足够简单，无需返工
- Claude 动手前先问问题
- PR 不夹带无关重构

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
> 实测发现：方式一（Plugin）只将 Karpathy 准则注册到可用 Skill 列表，不会自动注入 system prompt；只有显式调用 `/karpathy-guidelines` 才加载，日常编码不会自动受其约束。
>
> **要让准则始终生效，必须写入 CLAUDE.md。** CLAUDE.md 分两级：
> - **用户级** `~/.claude/CLAUDE.md`：全局生效，所有项目自动加载（推荐方式二）
> - **项目级** 项目根目录 `CLAUDE.md`：仅对当前项目生效（方式三/四）
>
> CLAUDE.md 在每次会话启动时自动作为 system prompt 加载，使 4 条准则约束 Claude 的所有行为。
>
> Skills 可用不代表始终激活，CLAUDE.md 则始终激活。对行为准则约束，CLAUDE.md 是唯一可靠的注入方式。

## davila7/claude-code-templates

> [!info] 仓库
> [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) — 500+ 组件的 Claude Code 模板市场，Web 界面：[aitmpl.com](https://aitmpl.com)

CLI 工具和组件市场，提供 Agents、Commands、MCPs、Settings、Hooks、Skills、Templates 七类组件，可按需安装到项目。

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

这是一套从 Vibe Coding 到 Agentic Engineering 的完整进阶指南，通过 TodoApp 示例演示如何组合 Claude Code 的全部扩展机制，构建生产级工作流。

**4 级进阶路径**：Low → Medium → High → Pro，逐级引入 Claude Code 配置。

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

Planning with Files 将计划、进度和错误记录写入本地 Markdown 文件，解决任务偏移、遗忘目标、上下文清空后重做和重复犯错等问题。它结合文件化规划、外置记忆与错误自动记录。

**3 个核心文件**：

| 文件 | 用途 |
| --- | --- |
| `task_plan.md` | 任务计划与进度——分阶段任务列表，打勾推进 |
| `findings.md` | 资料、研究、结论——项目过程中的发现和决策记录 |
| `progress.md` | 过程记录、测试、日志——错误记录和执行日志 |

**核心价值**：

- 将文件作为记忆，关闭软件、清空上下文或重启电脑后仍会保留
- 先规划，再自动分阶段推进
- 自动记录错误，AI 下次会避开，绝不重复犯错
- 清屏或重启后自动读取文件，恢复进度
- 每一步对照计划，确保不偏离目标
- 任务成功率从 6.7% → 96.7%

**安装**：

```sh
npx skills add OthmanAdi/planning-with-files --skill planning-with-files -g
```

输入 `/plan` 启动规划模式，AI 自动生成 3 个核心文件并按计划执行。

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
