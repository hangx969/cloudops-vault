---
title: html-ppt-skill - HTML幻灯片生成
tags:
  - AI
  - ppt
  - html
  - skill
aliases:
  - html-ppt-skill
  - HTML幻灯片
---

# html-ppt-skill — HTML 幻灯片生成系统

> 来源：[一句话生成PPT，已经能用了：html-ppt-skill实测指南](https://mp.weixin.qq.com/s?__biz=MzUxNDAxMzQyMw==&mid=2247496098&idx=1&sn=41b4a48a760b8c205993ccdd3e00c451&scene=21)
> 仓库：[lewislulu/html-ppt-skill](https://github.com/lewislulu/html-ppt-skill)

---

## 项目简介

html-ppt-skill 是一套给 AI Agent 准备的静态幻灯片生成系统：输入自然语言，输出 HTML/CSS/JS 幻灯片。不是传统 PPT 软件，也不是 AI 模板站，而是把 PPT 从人工排版对象变成 **AI 可调度的视觉输出能力**。

核心思路：**绕开 PPT 文件格式，用浏览器能理解的 HTML 来表达幻灯片**。浏览器渲染是最成熟的跨平台视觉输出系统，HTML 幻灯片的可控性、可预览性、可导出性都比封闭二进制格式更适合 Agent 调用。

### 内置资源

| 资源类型 | 数量 |
|---------|------|
| 主题 | 36 套 |
| 页面布局 | 31 种 |
| 完整 deck 模板 | 14 套 |
| 动画效果 | 47 种 |

### 项目结构

| 目录 | 作用 |
|------|------|
| `assets/` | 字体、基础样式、主题、运行时脚本 |
| `templates/` | 布局模板 + 完整 deck 模板 |
| `references/` | 主题说明、模板说明、写作约束 |
| `scripts/render.sh` | HTML → PNG 渲染脚本 |

---

## 核心价值

传统做 PPT 流程：想内容 → 选模板 → 改样式 → 补图表 → 调动画 → 导出（6 步）

html-ppt-skill 把第 2~5 步收进 prompt：人给需求 → Agent 决定模板/主题/版式 → 输出 HTML 成品 → 人做最终判断。

**关键转变**：问题从"怎么做一页 PPT"变成"这一页要不要这样表达"——把精力从执行排版挪回判断内容。

---

## 实测场景

### 测试 1：技术分享

```
提示词："做一份 8 页的技术分享 slides，用 cyberpunk 主题"
模板：tech-sharing | 主题：cyberpunk-neon
```

验证了模板骨架和主题系统的分层设计是成立的。

### 测试 2：融资路演

```
提示词："turn this outline into a pitch deck"
模板：pitch-deck | 主题：pitch-deck-vc
```

验证了商业叙事的场景抽象能力——融资路演的节奏、层级和视觉重心能自动排出来。

### 测试 3：小红书图文

```
提示词："做一个小红书图文，9 张，白底柔和风"
模板：xhs-post | 主题：xiaohongshu-white / soft-pastel
```

验证了跨场景迁移能力——从技术分享到商业路演到社交图文，同一套链路都能覆盖。

---

## 与同类工具的定位对比

| 维度 | html-ppt-skill | [[AI/AI-视觉/AI做PPT-ppt-master\|PPT Master]] | [[AI/AI-视觉/AI代码动画与科普视频制作#3. 模板路线：AI-Animation-Skill\|AI-Animation-Skill]] |
|------|---------------|------------|---------------------|
| 输出格式 | HTML/CSS/JS 幻灯片 | 原生 PPTX（DrawingML） | 单 HTML 动画文件 |
| 目标场景 | 通用幻灯片（技术/商业/社交） | 专业演示文稿 | 科普视频录制 |
| 内置资源 | 36 主题 + 31 布局 + 14 deck + 47 动画 | 20 布局 + 52 可视化 + 6700 图标 | 44 个动画模板 |
| 可编辑性 | 修改 HTML 代码 | PowerPoint 原生编辑 | 修改 HTML 代码 |
| 运行平台 | AI Agent（OpenClaw 等） | Claude Code / Cursor / VS Code | OpenClaw / WorkBuddy |
| 核心优势 | 主题+布局+动画最丰富，场景覆盖广 | 输出原生可编辑 PPTX | 科普场景专精，中文原生 |

---

## 适合与不适合

**适合**：
- 需要快速出技术分享稿的人
- 需要把文字提纲变成完整 deck 的人
- 需要做多页图文内容（小红书等）的人

**不适合**：
- 需要输出可编辑 PPTX 的人（→ 用 [[AI/AI-视觉/AI做PPT-ppt-master|PPT Master]]）
- 不接受 HTML 作为中间产物的人
- 没有 AI Agent 本地环境的人
