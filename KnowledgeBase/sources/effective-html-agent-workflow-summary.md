---
title: Effective HTML Agent 页面制作与 HTML 交付工作流来源摘要
tags:
  - knowledgebase/source
  - ai/ai-visual
  - ai/skills
  - ai/html
date: 2026-09-07
sources:
  - "[[AI/AI-视觉/Effective-HTML-Agent页面工作流]]"
aliases:
  - Effective HTML 来源摘要
  - effective-html 摘要
---

# Effective HTML Agent 页面制作与 HTML 交付工作流来源摘要

## 元信息

- **原始文档**：[[AI/AI-视觉/Effective-HTML-Agent页面工作流]]
- **原始来源**：[Effective HTML 页面工作流](https://mp.weixin.qq.com/s/EWFsQChEmC4aGfuQ1lcpgA)、[effective-html 工具实测](https://mp.weixin.qq.com/s/UpwCCgiK8BkT9P8U74x_Vw)
- **领域**：AI / AI 视觉 / Agent Skills / HTML 交付
- **摄入日期**：2026-09-07

## 摘要

Effective HTML 是面向 Coding Agent 的 HTML Skills 集合，目标不是让 Agent 更快堆出一份页面，而是让它先判断任务类型、分阶段完成页面，并在交付前检查结构、交互状态和视觉一致性。它还改变了 AI 的默认输出形态：在报告、架构图和演示文档等需要“看”的场景中，直接生成浏览器可打开的自包含 HTML，而不是只输出 Markdown 或等待额外渲染的 Mermaid 代码。

HTML 交付按以下顺序展开：先决定 HTML 是否适合作为交付格式，再用设计范本和任务路由确定产物类型，最后按线框、原型、图表和视觉检查逐步完成。

## 关键知识点

1. **解决 AI 页面返工问题**：Agent 往往在结构未定时就加入渐变、阴影、动画，或只实现正常状态而遗漏加载、报错、提交失败、键盘操作和移动端适配。Effective HTML 把这些要求前置为 Skills 中的工作约束。
2. **浏览器即运行时**：输出是自包含 HTML 文件，双击即可打开，不需要额外安装运行环境；页面可以包含排版、交互图表、暗色模式、标签页和状态切换。
3. **HTML 与 Markdown 互补**：HTML 更适合视觉表达、自包含交付和交互；Markdown 更适合 Git diff、纯文本搜索/管道处理以及持续写作编辑。Effective HTML 不是要完全替代 Markdown，而是补足 AI 面向视觉交付的输出格式。
4. **三类核心交付入口**：`html` 负责通用页面生成和任务判断；`html-diagram` 负责架构图及关系图；`html-plan` 负责简洁的项目计划和需求页面。
5. **六个阶段化 Skill**：在页面制作流程中进一步拆分为 `html`、`html-wireframe`、`html-prototype`、`html-diagram`、`html-plan` 和 `design-artifact`，对应任务判断、结构确认、交互原型、图表表达、计划文档和视觉设计。
6. **线框优先**：结构未确定时使用 `html-wireframe`，以灰度、边框和区块表达布局，先比较信息层级、主要按钮位置和移动端排列，再决定颜色和装饰。
7. **原型补齐真实状态**：结构确认后使用 `html-prototype`，把静态页面变成可操作原型，覆盖加载、成功、失败、表单校验、弹窗、键盘操作和响应式适配。
8. **图表先选表达形式**：拓扑关系适合架构图，请求经过多个服务适合时序图，业务步骤适合流程图，运行→报警→恢复适合状态图；确定图形语义后再用 HTML、CSS、SVG 或 Canvas 实现。
9. **视觉设计要匹配场景**：`design-artifact` 约束字体、颜色、布局和动效，避免紫蓝渐变、满屏圆角卡片、黑底荧光色和不必要的动画；已有设计规范时优先复用。
10. **参考范本降低猜测成本**：`html-effectiveness` 参考库（作者 Thariq Shihipar）包含 20 个 HTML 示例，覆盖代码审查报告、设计系统文档、原型动画、流程图、事故报告和功能开关面板等。它们提供的是内容组织和交互呈现范式，不只是 CSS 模板。
11. **实测交互特性**：通用报告可以生成卡片布局、颜色区分、表格对比、暗色模式切换，并在刷新后记住偏好；架构图可以生成全屏 SVG，支持节点点击、数据流动画和请求路径高亮；计划页则强调简洁、清晰和实用。
12. **安装方式与兼容性**：完整安装使用 `npx skills add plannotator/effective-html`；也可以只安装 `html-prototype`、`html-diagram` 或 `html-plan`。Codex 用户还可以通过 `codex plugin marketplace add plannotator/effective-html` 和 `codex plugin add plannotator-effective-html@effective-html` 安装。项目登记在 `skills.sh`，采用 Claude Agent Skill 格式，并兼容 `.claude-plugin`，可在 Claude Desktop 中作为插件加载。
13. **同类工具的边界**：effective-html 面向自包含 HTML 交付；Markdown Viewer Skills 面向 Markdown 中嵌入图表；html-anything 面向任意 HTML 生成；Mermaid 适合简单流程图和时序图，但需要渲染器。

## 涉及的概念与实体

- [[KnowledgeBase/concepts/提示词工程]]：通过任务路由、阶段约束和验证标准减少 Agent 页面返工。
- [[KnowledgeBase/entities/Claude-Code|Claude Code]]：可加载 HTML Skills 和插件的 Coding Agent。
- [[KnowledgeBase/entities/Codex|Codex]]：文章列举的另一种可通过插件使用 Effective HTML 的 Coding Agent。
- [[AI/AI-视觉/Markdown-Viewer-Skills-Markdown中直接画图|Markdown Viewer Skills：AI 文档配图]]：同类的 Markdown 内嵌图表方案。
- [[AI/AI-视觉/html-anything-AI生成HTML全场景工具]]：同类的全场景 HTML 生成工具。
- [[AI/AI-视觉/AI-Animation-Skill-科普动画]]：同属 AI 生成 HTML 视觉交付的相关实践。

## 值得注意

- Skill 的数量有两种口径：三个核心交付入口用于选择产物类型，六个阶段化 Skill 用于组织页面制作过程。入口层与阶段层承担不同职责，数量差异不代表版本冲突。
- HTML 适合作为面向读者的展示和交互层，但不一定适合作为知识库的唯一存储格式。对于需要持续 diff、搜索和编辑的知识内容，Markdown 仍然更合适。
- 架构图“能运行”不等于信息表达正确；应先决定图表要表达的关系和阅读顺序，再选择 SVG、Canvas 或其他实现方式。
