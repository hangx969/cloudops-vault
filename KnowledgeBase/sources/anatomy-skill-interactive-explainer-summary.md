---
title: AI 代码动画与科普视频制作来源摘要
tags:
  - knowledgebase/source
  - AI/可视化
  - AI/skills
date: 2026-10-21
aliases:
  - Anatomy Skill 来源摘要
  - AI 代码动画来源摘要
---

# AI 代码动画与科普视频制作来源摘要

## 元信息

- **原始文档**：[[AI/AI-视觉/AI代码动画与科普视频制作]]
- **外部来源**：[罗佳 Rodya 的技术栈教程](https://mp.weixin.qq.com/s/kaZCk5qg0bWvn31xcAb37Q)，2026-10-20；[AI-Animation-Skill 模板文章](https://mp.weixin.qq.com/s/s53qdw1IvU4Ei77ebuKF9Q)；[卡兹克、tashi 的 Anatomy 文章](https://mp.weixin.qq.com/s/VuJsVTvyNIK8GRTL95n-Qw?scene=1&click_id=1652332932)，2026-10-15
- **领域**：AI 可视化、代码动画、交互式解释与科普视频
- **摄入日期**：2026-10-21；Anatomy 材料于 2026-10-20 首次摄入，本次合并更新

## 摘要

文章按交付形式、画面技术、制作路线、风格选型与验收组织三份材料。先解释由时间或帧号驱动画面、逐帧截图和编码的流程，再介绍 22 种技术与工具，以及 HTML 模板和 Anatomy 结构模型两条路线。保留 16 类视频的实现拆解、可复制提示词、安装命令、声音与素材方法，并收录作者的生成耗时、额度和配音体验。

## 关键知识点

1. 浏览器代码动画可以由时间或帧号决定画面，再逐帧渲染和编码；普通 HTML 播放或录屏并不自动满足确定性渲染要求。
2. 画面技术包括 HTML/CSS/SVG、Canvas、p5.js、WebGL 与 Three.js；时间轴可由 HyperFrames、Remotion 或其他引擎组织。文章将四张代码图片转录为可复制片段，保留其环境前提。
3. AI-Animation-Skill 提供 26 个 Level2、4 个基础演示和 14 个流程图模板，先生成基础 HTML，再选模板重构；输出 HTML，可进一步录制。
4. Anatomy 通过结构、运动及同一模型驱动的读数解释原理；交互图形可交付为 HTML、SVG 或组件，讲解编排、配音和视频制作需要后续完成。
5. 16 类场景同时给出风格和技术栈关键词，覆盖知识讲解、资讯、产品、数据、科研、城市、档案、水墨、绘本、广告、社媒、像素、片头与数学动画。
6. 旁白、配乐、节拍分析、素材生成与编码需要分别处理。人应试听音色和发音，核对数据、尺寸、原理及素材授权。
7. 原 Anatomy 记录保留机械表、发动机、显卡、TCP、刹车、榫卯及 Transformer 会话案例。约 5 分钟视频消耗周额度约 1%、生成约 1.5 小时等数字均为作者经验，不能推广为固定成本。
8. 文字、图解、交互网页和视频适用于不同学习问题；借用 ASD-STE100 的清晰写作原则不等于中文说明符合该标准。

## 涉及的概念与实体

- [[KnowledgeBase/concepts/提示词工程]]
- [[KnowledgeBase/entities/Claude-Code]]
- [[KnowledgeBase/entities/OpenClaw]]
- [[KnowledgeBase/maps/ai-workflow-map]]

## 值得注意

- Anatomy 的输出边界、AI-Animation-Skill 的模板流程、HyperFrames 的时间轴与环境要求、Remotion 的帧控制与随机数原则已对照项目文档；未安装这些 Skill，也未复现视频生成。
- 11 张技术图表和代码示意图迁移至 PicGo GitHub Plus；示例视频截图按要求省略。机械表视频的完整提示词在原材料中不可见，未补写。
- 模型名称、推理档位、会员额度、耗时、中文支持评价及旧商业价格按原文记录保留并标明边界；原作者的效果评价和同事反馈不能替代技术核查。
- Transformer 案例中的会话限制触发机制未独立核实。Anatomy 与模板动画已整合到同一原始文档，分别按交互结构和模板路线展开。
- 本摘要沿用此前 Anatomy 摘要的路径，覆盖范围已扩展到整篇合并文章；相关学习方法见 [[AI/行业动态/Karpathy-大模型输出理解技巧-文字图解网页视频]]。
