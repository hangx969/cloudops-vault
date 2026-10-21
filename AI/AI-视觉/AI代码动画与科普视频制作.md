---
title: AI 代码动画与科普视频制作：技术栈、风格与 Skill
date: 2026-10-21
tags:
  - AI/可视化
  - AI/视频制作
  - AI/skills
aliases:
  - AI-Animation-Skill
  - AI-Animation-Skill-科普动画
  - Anatomy-Skill-交互模型与科普视频
  - Anatomy 科普视频
  - Anatomy 交互式原理演示
  - 科普动画
  - Claude Opus 5.5 做视频进阶篇，技术栈全拆解丨万字教程
source:
  - https://mp.weixin.qq.com/s/kaZCk5qg0bWvn31xcAb37Q
  - https://mp.weixin.qq.com/s/s53qdw1IvU4Ei77ebuKF9Q
  - https://mp.weixin.qq.com/s/VuJsVTvyNIK8GRTL95n-Qw?scene=1&click_id=1652332932
---

# AI 代码动画与科普视频制作：技术栈、风格与 Skill

用 AI 做动画，可以从 HTML 模板、交互式结构模型入手，也可以直接编写 Canvas、SVG 或 Three.js 场景。几条路线共享一套工作方法：先明确要解释的内容，再选择画面技术和风格，制作可预览的动画，最后录制或逐帧渲染、配音并导出视频。

## 1. 先确定交付形式和讲解方式

### 1.1 文字、图解、交互网页与视频

不同产物适合解决不同的理解障碍：文字便于查阅，图解呈现关系，交互网页支持探索，视频则安排好讲解顺序。

| 形式 | 适合解决的问题 | 组织重点 |
| --- | --- | --- |
| 文字 | 快速查阅定义和说明 | 用词一致、句子清楚，减少歧义 |
| 图解 | 观察组件关系与结构 | 让读者看清组成和联系 |
| 交互式 HTML | 自己操作、拆解和探索 | 操作、模型状态和实时读数一致 |
| 讲解视频 | 按顺序理解一个过程 | 画面、旁白和解释顺序配合 |

例如，机械表交互模型允许读者上发条、观察齿轮或拆开零件；讲解视频还要说明“这是什么零件、发生了什么、为什么发生、它在系统中起什么作用”。已有基础的读者可以直接探索模型，初学者往往还需要旁白安排讲解顺序。

文字说明可借用 ASD-STE100 简化技术英语的清晰写作原则，如限制句长、使用主动语态、同一含义尽量用一致的词语。这些约束也可用于榫卯等结构的说明。中文借用这些原则并不等于符合 ASD-STE100。

### 1.2 代码动画如何成为视频

代码动画由 AI 编写画面和控制逻辑，再由浏览器或动画引擎渲染。以浏览器为例：

1. 把画面写成由时间 `t` 或帧号决定的状态。
2. 浏览器定位到指定时刻并截取画面。若目标是 30 fps，就每隔 `1/30` 秒取一帧。
3. 用 FFmpeg 将帧序列编码为 MP4，并处理旁白、音乐和音效。
4. 抽查关键帧和转场，检查完整成片；有问题时修改代码并重新渲染。

![从选题、分镜到逐帧渲染与自检的工作流](https://raw.githubusercontent.com/hangx969/upload-images-md/main/source-image-01.jpg)

完整制作还包括选题与开头设计、逐字稿、分镜、字幕和角标、联网核查、生成插画及统一画风。创作者负责选题、审核脚本和画面、配置音乐；Agent 承担查资料、写代码、调用素材工具、渲染与自检。

30 fps 只是示例，具体项目可以采用其他帧率。HTML 录屏也不自动等于确定性逐帧渲染：后者需要可定位的时间轴或帧号，并控制随机数和素材加载状态。Remotion 要求动画由帧号驱动，随机效果应使用固定种子；直接依赖实时 CSS 动画或 `Math.random()` 可能使并行渲染结果不一致。[Remotion 动画说明](https://www.remotion.dev/docs/troubleshooting/css-animations)、[随机数说明](https://www.remotion.dev/docs/using-randomness)

真人、舞蹈等内容也可以交给视频生成模型，再由代码处理抠像、字幕和场景包装。Minimax、Seedance 等视频模型可用于这条混合路线，具体分工需要按作品确定。

## 2. 画面、时间轴、声音与导出：22 种技术和工具

①～㉒ 分别标识画面技术、视频引擎、声音、素材和环境工具，后面的风格案例用这些编号表示组合。难度星级和花费等级采用罗佳 Rodya 的经验估计，仅供比较制作门槛；实际成本还要计入 Agent 额度、渲染时间和第三方服务费用。

### 2.1 浏览器画面技术

| 编号 | 技术 | 参考难度 / 花费 | 用途 |
| --- | --- | --- | --- |
| ① | HTML / CSS / SVG | ★ / 低 | 网页界面、文字排版和矢量图形 |
| ② | Canvas 2D | ★ / 低 | 像素、手绘、插画、图表等平面画面 |
| ③ | p5.js + p5.brush | ★★ / 低 | 艺术绘图，配合笔刷插件模拟彩铅、水彩等笔触 |
| ④ | WebGL 着色器 | ★★★ / 中 | 逐像素计算胶片颗粒、CRT 扫描线、晕染、发光等效果 |
| ⑤ | Three.js | ★★★ / 中 | 搭建浏览器 3D 场景，让镜头在空间中推拉、环绕 |

![浏览器画面技术对比](https://raw.githubusercontent.com/hangx969/upload-images-md/main/ai-code-video-20261021-02-b0ffd38eae.jpg)

HTML/CSS/SVG 和 Canvas 适合入门，可以先在 Claude 网页聊天中生成代码，再到浏览器预览。着色器常叠加在 Canvas 或 Three.js 上，用来处理材质和光效，但会增加渲染成本。在 @xilo2991 的一次 3 秒、90 帧像素画面测试中，Canvas 渲染耗时 7 秒，加入着色器后为 48 秒；这个结果只反映该画面和测试环境。

#### Canvas 2D：由时间直接计算一帧

Canvas 提供填色、画线、画圆和写字等操作。下面把画线进度与圆的位置都写成时间 `t` 的函数：

```javascript
const ctx = c.getContext('2d');
window.render = (t) => {
  ctx.fillStyle = '#f4efe4';
  ctx.fillRect(0, 0, 640, 360);
  ctx.strokeStyle = '#1c2024';
  ctx.lineWidth = 6;
  ctx.beginPath();
  const end = 640 * Math.min(t / 2, 1);
  for (let x = 0; x <= end; x += 4)
    ctx.lineTo(x, 200 + 70 * Math.sin(x / 50));
  ctx.stroke();
  ctx.fillStyle = '#c8402c';
  ctx.beginPath();
  ctx.arc(60 + 260 * t, 90, 26, 0, Math.PI * 2);
  ctx.fill();
};
```

这段局部代码假定 `c` 是已有的 640×360 Canvas。分别调用 `render(0.5)`、`render(1)` 和 `render(2)`，就能得到线条逐渐延长、圆向右移动的三帧。

![Canvas 2D 时间函数与三帧渲染示意](https://raw.githubusercontent.com/hangx969/upload-images-md/main/ai-code-video-20261021-03-122d2878e9.jpg)

像素风、手绘本、水墨、剪纸和白板讲解，都可以在这个基础上细化笔触、颜色与纸张效果。

#### Three.js：搭建场景、材质、灯光和相机

Three.js 中先摆好物体、配置材质与灯光，再让相机观察场景。下面的示例使用 Three.js r170，三层板子随时间分离，相机同时环绕。

```javascript
const renderer = new THREE.WebGLRenderer({ canvas: c, antialias: true });
renderer.shadowMap.enabled = true;
const scene = new THREE.Scene();
scene.background = new THREE.Color('#2a2c30');
const camera = new THREE.PerspectiveCamera(35, 16 / 9, 0.1, 100);
const colors = ['#d9d4c9', '#3b7d5a', '#686c73'];
const layers = colors.map((color, i) => {
  const mesh = new THREE.Mesh(
    new THREE.BoxGeometry(2.4, 0.25, 1.4),
    new THREE.MeshStandardMaterial({ color, roughness: 0.6 }));
  mesh.castShadow = true;
  scene.add(mesh);
  return mesh;
});
const floor = new THREE.Mesh(new THREE.PlaneGeometry(20, 20),
  new THREE.ShadowMaterial({ opacity: 0.35 }));
floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true;
scene.add(floor);
const key = new THREE.DirectionalLight('#ffe8cc', 2.5);
key.position.set(3, 6, 2); key.castShadow = true;
scene.add(key, new THREE.HemisphereLight('#cfe0ff', '#202020', 1));
window.render = (t) => {
  layers.forEach((m, i) => m.position.y = 0.3 + i * (0.3 + 0.5 * t));
  camera.position.set(6 * Math.cos(0.6 * t), 3, 6 * Math.sin(0.6 * t));
  camera.lookAt(0, 0.9, 0);
  renderer.render(scene, camera);
};
```

代码假定已经加载 `THREE` 并准备好 Canvas，完整工程还需要管理画布尺寸和渲染环境。Canvas 直接绘制平面笔画，Three.js 则通过场景、相机、材质和光照生成画面；两者都能制作精细作品，选择取决于空间关系和视觉需求。

![Three.js 场景代码与拆分动画示意](https://raw.githubusercontent.com/hangx969/upload-images-md/main/ai-code-video-20261021-04-5df21fa0c5.jpg)

### 2.2 视频框架与引擎

框架可以处理时间轴、预览和导出，让 Agent 更集中地编写画面；相应地，需要先准备项目环境。

| 编号 | 工具 | 参考难度 / 花费 | 用途 |
| --- | --- | --- | --- |
| ⑥ | HyperFrames | ★★ / 低 | 用 HTML 写视频，以时间轴和轨道安排内容；HeyGen 开源 |
| ⑦ | Remotion | ★★★ / 低，商用需核对授权 | 用 React 写视频，按帧计算，适合长片和系列化复用 |
| ⑧ | Manim | ★★★ / 低 | Python 数学动画，公式和几何推导 |
| ⑨ | Motion Canvas / Revideo | ★★★ / 低 | TypeScript 讲解动画与程序化视频路线 |
| ⑩ | Blender | ★★★★★ / 高 | 专业三维软件，可通过 blender-mcp 或 Python 脚本操作，安装和渲染门槛较高 |

![视频框架与引擎对比](https://raw.githubusercontent.com/hangx969/upload-images-md/main/ai-code-video-20261021-05-0aff7c3eba.jpg)

#### HyperFrames：按时间和轨道安排素材

HyperFrames 在网页元素上增加时间属性：`data-start` 表示开始秒数，`data-duration` 表示持续秒数，`data-track-index` 表示轨道。视频、标题和音乐可以分别占用一条轨道；GSAP 等动画库提供可定位的动画，框架负责逐帧渲染。

下面是时间轴部分的代码。运行前需要加载 GSAP，并准备好 `intro.mp4` 和 `music.wav`：

```html
<div id="stage" data-composition-id="launch" data-start="0"
     data-width="1920" data-height="1080">
  <video class="clip" data-start="0" data-duration="6"
         data-track-index="0" src="intro.mp4" muted playsinline></video>
  <h1 id="title" class="clip" data-start="1" data-duration="4"
      data-track-index="1">Launch day</h1>
  <audio data-start="0" data-duration="6" data-track-index="2"
         data-volume="0.5" src="music.wav"></audio>
  <script>
    const tl = gsap.timeline({ paused: true });
    tl.from("#title", { opacity: 0, y: 40, duration: 0.8 }, 1);
    window.__timelines = window.__timelines || {};
    window.__timelines.launch = tl;
  </script>
</div>
```

标题从第 1 秒开始出现，在 0.8 秒内淡入并上移；背景视频和音乐持续 6 秒。项目的安装与时间轴写法可对照 [HyperFrames 官方说明](https://github.com/heygen-com/hyperframes#how-it-works)。截至 2026-10-21，当前 README 标明 Node.js 22+，不要把其他工程的 Node 20+ 要求直接套用过来。

![HyperFrames 代码与时间轴示意](https://raw.githubusercontent.com/hangx969/upload-images-md/main/ai-code-video-20261021-06-f51aa4676f.jpg)

#### Remotion：由帧号计算组件状态

Remotion 将视频表示为 React 组件，通过 `useCurrentFrame()` 获取当前帧，再用 `interpolate()` 计算透明度、位置或大小。下面的标题在第 0～30 帧间淡入：

```tsx
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';

export const Title = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 1]);
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
      <h1 style={{opacity}}>Launch day</h1>
    </AbsoluteFill>
  );
};
```

在 `Root.tsx` 中注册 Composition，以下为注册片段，需在项目中导入 `Composition` 和 `Title`：

```tsx
<Composition id="Title" component={Title}
  durationInFrames={150} fps={30} width={1920} height={1080} />
```

150 帧、每秒 30 帧，对应 5 秒。第 0、15、30 帧分别是透明、半透明和完全显示。按帧组织内容便于精确修改文字、位置，也便于为字幕和数据建立检查。

![Remotion 帧号驱动的淡入示意](https://raw.githubusercontent.com/hangx969/upload-images-md/main/ai-code-video-20261021-07-95910c3c9b.jpg)

HyperFrames 的写法接近在时间轴上摆素材；Remotion 以 React 组件和帧号组织画面，适合几分钟的长片和反复复用风格的系列。Blender 则适合进一步追求三维质感，但环境和渲染成本更高。

### 2.3 配乐、节拍与配音

| 编号 | 方法 | 参考难度 / 费用方式 | 用途与注意事项 |
| --- | --- | --- | --- |
| ⑪ | 代码合成配乐和音效 | ★ / 免费工具 | 用 Python、NumPy 按频率计算波形，制作鼓点、钢琴或点击声 |
| ⑫ | 节拍分析与卡点 | ★★ / 免费工具 | 用 librosa 分析节拍和重音，让转场与音乐节奏配合 |
| ⑬ | AI 配乐 | ★★ / 订阅 | 如用 Suno 生成整段背景音乐 |
| ⑭ | TTS 配音 | ★★ / 按量 | 如用火山引擎豆包语音合成；建议整段生成，避免逐句拼接 |

![配乐、节拍与配音方案对比](https://raw.githubusercontent.com/hangx969/upload-images-md/main/ai-code-video-20261021-08-f2b41d4838.jpg)

响度数字和波形可以辅助检查声音；音色、节奏、英文发音和音量关系仍需戴耳机试听，不能只看自动验收结果。

### 2.4 外部素材与生成素材

| 编号 | 方法 | 参考难度 / 费用方式 | 适用内容 |
| --- | --- | --- | --- |
| ⑮ | 截图 / 录屏 | ★ / 免费工具 | 网页、社交帖子等；可由浏览器自动化截取 |
| ⑯ | 生图 | ★★ / 按张 | 用 Seedream、即梦、Midjourney 等生成插画；《江月何年》采用了这条路线 |
| ⑰ | 视频模型 + 抠像 | ★★★ / 按秒，参考成本最高 | 用 Grok、即梦等生成真人或舞蹈绿幕片段，代码负责抠像和包装 |

![截图、生图与视频模型素材路线](https://raw.githubusercontent.com/hangx969/upload-images-md/main/ai-code-video-20261021-09-f09d7e471f.jpg)

卫星影像、档案扫描、点云和建筑数据等案例还需要可靠的真实资料。素材授权、数据出处、尺寸与数值应跟随项目保留，不能因为画面由代码生成就省略来源核对。

### 2.5 环境与导出工具

| 编号 | 工具 | 用途 |
| --- | --- | --- |
| ⑱ | FFmpeg | 帧序列编码、混音、抠像、测量响度 |
| ⑲ | Node.js | 运行 HyperFrames、Remotion 等工程 |
| ⑳ | Python + uv | 处理数据、合成声音、运行辅助脚本与管理环境 |
| ㉑ | Playwright | 驱动浏览器并截图；逐帧流程还需要主动定位时间 |
| ㉒ | Git | 下载和管理开源项目、Skill |

![环境与导出工具分工](https://raw.githubusercontent.com/hangx969/upload-images-md/main/ai-code-video-20261021-10-2c38aa84b9.jpg)

可以把下面的环境准备请求发给 Agent。具体依赖和版本以选中的项目为准：

```text
帮我检查这台电脑有没有装 Node.js、ffmpeg、Python、uv 和 git，缺哪个就帮我装上，装完告诉我各自的版本号。
```

## 3. 模板路线：AI-Animation-Skill

### 3.1 工作流与输出

AI-Animation-Skill 把科普文本转成 HTML 演示动画，运行在 OpenClaw、WorkBuddy、QClaw 等 Agent 环境中。模板使用 HTML5、CSS3 和 JavaScript，没有第三方前端框架依赖，动画包括 CSS Animation、Keyframes、3D Transform 和 Canvas 粒子。最轻量的模板为 331 行。

传统制作通常经过写稿、制作 PPT、调整动画、录屏和剪辑；这条路线先由 Agent 生成基础 HTML，再按模板重构，最后录制。这里的“生成 PPT”指生成演示页面，最终输出为 HTML。

1. 默认模式：输入科普文本，要求“帮我生成 PPT”；先生成基础 HTML，再从 26 个 Level2 模板中选型并重构。
2. 可选模式：完成第一步后要求“生成流程图”；从 14 个 Animation 模板中选型，把已有 HTML 改成平面 UI 风格。
3. 两种产物可以配合使用：演示版用于完整讲解，流程图版用于回顾。

生成的 HTML 可在浏览器中播放，再全屏录制。部分浏览器可按 F11 全屏，具体快捷键因系统和浏览器而异；录制工具可用 OBS、Windows 的 Win+G 或浏览器插件。使用本地素材的页面可离线播放，Agent 生成过程和外部资源是否联网需要另外确认。

模板及工作流说明见 [AI-Animation-Skill 项目](https://github.com/Unclecheng-li/AI-Animation-Skill)。

### 3.2 44 个模板如何选择

模板分为 26 个 PPT Level2、4 个 PPT 基础模板和 14 个 Animation 流程图模板。Level2 是优先选择，按概念解释、案例、问题分析、方案对比和总结等内容结构分为 9 个系列。

| 系列 | 数量 | 适用内容 | 特点 |
| --- | --- | --- | --- |
| 1 | 1 | 概念引入、对比 | VS 对比卡片、SVG 流程图 |
| 2 | 1 | 概念定义、层级结构 | 13 种动画 |
| 3 | 3 | 轻量、步骤、极简 | 3-3 模板为 331 行 |
| 4 | 3 | 案例、实验、代码 | 含代码雨动画 |
| 5 | 4 | 警示、失败、危险 | 5-4 模板含 15 种动画、13 页 |
| 6 | 4 | 护栏、架构、反馈 | 6-2 为红绿 VS 对比，含 15 种动画 |
| 7 | 4 | 追踪、上下文、Doom Loop | 7-2 含 17 种动画 |
| 8 | 3 | 辩论、对比、融合 | 8-3 含 30 组 VS 对比 |
| 9 | 3 | 总结、共识、精炼 | 9-3 共 5 页 |

4 个 PPT 基础模板用于 Level2 不适用时回退，原项目推荐 PPT-Generate-3。14 个流程图模板默认推荐 RNN-3 分层卡片；专用模板包括 LSTM-1（三阶段门控）、word2vec-1（词向量的语义身份证）和 GPU（计算节点架构）。

### 3.3 安装与平台

AI-Animation-Skill 可配合 OpenClaw、腾讯 WorkBuddy、QClaw 和摩尔线程 AIBOOK 等 Agent 环境使用。以 WorkBuddy 为例，安装步骤如下：

```bash
# 1. 下载源码
git clone https://github.com/Unclecheng-li/AI-Animation-Skill.git

# 2. 复制到 skills 目录
cp -r AI-Animation-Skill ~/.workbuddy/skills/

# 3. 重启 WorkBuddy
```

OpenClaw 可通过 ClawHub 安装，具体入口以平台当前提供的包为准。

### 3.4 与演示工具的定位对比

下表中的商业工具功能和评价属于历史使用记录，适合了解定位差异；中文效果、导出能力和套餐需按当前产品确认。

| 维度 | AI-Animation-Skill | Gamma | Beautiful.ai |
| --- | --- | --- | --- |
| 费用 | MIT 模板开源；Agent 费用另计 | 商业在线服务 | 商业在线服务 |
| 中文 | 模板按中文内容设计 | 有译文不自然的使用反馈 | 早期使用记录为不支持中文 |
| 网络 | 本地 HTML 与本地资源可离线播放 | 在线使用 | 在线使用 |
| 输出 | 单 HTML 文件，用于播放和录制 | PDF / PPTX / 网页 | PDF / PPTX |
| 动画 | 原生 CSS 动画、3D Transform 等 | 网页过渡效果 | 智能排版动画 |
| 可定制性 | 可直接修改代码 | 有限 | 中等 |
| 目标场景 | 科普、教学、技术演示 | 通用演示 | 企业商务演示 |

历史使用记录中的套餐价格为 Gamma Plus 8 美元/月、Beautiful.ai Pro 45 美元/月；当时 Gamma 免费版功能受限，Beautiful.ai 没有免费版。这些价格不代表现价，选型时需重新核对套餐、中文支持和导出能力。

与 [[AI/AI-视觉/AI做PPT-ppt-master|PPT Master]] 的区别更直接：

| 维度 | AI-Animation-Skill | PPT Master |
| --- | --- | --- |
| 输出格式 | HTML 动画 | 原生可编辑 PPTX |
| 目标场景 | 科普视频录制 | 专业演示文稿 |
| 使用平台 | OpenClaw / WorkBuddy | Claude Code / Cursor / VS Code |
| 编辑方式 | 修改 HTML 代码 | PowerPoint 原生编辑 |
| 中文设计 | 模板原生面向中文 | 通用多语言 |
| 适合人群 | 科普创作者、教育工作者 | 企业、咨询与专业演示人员 |

这套模板偏简洁技术科普，缺少企业级品牌管控，采用单人工作流，没有实时协作功能。44 个模板对营销、品牌和广告场景的覆盖也有限。

## 4. 结构模型路线：Anatomy

### 4.1 用零件和运动解释原理

Anatomy 让 Agent 把技术概念做成可操作的装置，再通过零件、结构和运动说明工作方式。机械表案例允许上发条、观察齿轮和拆解；劳斯莱斯 Trent 970 发动机案例通过 1/4 剖面展示风扇、压气机、燃烧室和涡轮。

抽象概念也可以借助具体机构解释。例如，“缓存未变就跳过工作”可表示为弹子锁：每颗弹子都匹配时锁芯才转动。画面上的数字与零件运动来自同一个计算模型，避免读数和动画各说各话。

Raptor 2 试车台的 SVG 与 WebGL 分层实现，以及检查管线穿插的例子，见 [[#5.5 机械原理、技术概念图解]]。

![Anatomy Raptor 2 点火结构示意](https://raw.githubusercontent.com/hangx969/upload-images-md/main/ai-code-video-20261021-15-e1ab2fecb8.jpg)

![Anatomy Raptor 2 拆分结构示意](https://raw.githubusercontent.com/hangx969/upload-images-md/main/ai-code-video-20261021-16-d59642deb0.jpg)

图示：Anatomy 仓库的 Raptor 2 交互模型，MIT。

这类图形适合机器、仪器和工具，不擅长人物或精确地图。交付可以是独立 HTML、SVG 或组件，带 WebGL 效果；它的核心产物是交互图形。配音、编排讲解和视频录制是后续制作步骤。[Anatomy 输出说明](https://github.com/wheresryan22/anatomy#what-it-makes)

### 4.2 安装与交互提示词

可以直接向 Agent 发送安装请求：

```text
帮我安装一下这个skill：https://github.com/wheresryan22/anatomy/tree/main
```

也可以使用项目给出的 CLI：

```bash
npx skills add wheresryan22/anatomy -g
```

机械表的交互演示提示词为：

```text
/anatomy explain how a mechanical watch keeps time, interactive
```

### 4.3 从交互模型制作讲解视频

交互模型展示了零件如何运动，讲解视频还要解释每个零件的作用和动作原因。在卡兹克、tashi 介绍的机械表案例中，交互模型进一步配上了讲解、旁白和音效，制作过程如下：

1. 指定学习主题、受众和讲解深度，并要求视频配有旁白。机械表案例使用 Opus 5.5、高推理强度。
2. 先安排解释顺序：识别零件，说明当前动作、原因及其在整个系统中的作用。讲到某个组件时，让画面展示或高亮它。
3. 把交互动作整理成可重复播放的动画，再录制或逐帧截取。可以用 Playwright 驱动浏览器，再完成视频编码和声音处理。
4. 人工检查旁白。机械表第一版采用 macOS 自带语音合成，制作者认为声音不自然，随后改用火山配音，一次完成调整。

交互模型需要检查操作、零件运动和读数；配音视频还要检查讲解顺序、旁白、音效和成片节奏。

### 4.4 案例与讲解顺序

下面列出卡兹克、tashi 分享的制作案例。时长、模型设置和效果评价均为当时的使用记录。

| 案例 | 设置与时长 | 讲解和体验 |
| --- | --- | --- |
| 机械表 | Opus 5.5，高推理强度；第一版 2 分 22 秒，更换配音后 2 分 21 秒 | 按零件、作用、关系和计时原理组织；制作者观察到齿轮啮合，并有对应音效，认为比单看动画更适合初学者 |
| 显卡 | 1 分 45 秒，记录为一次生成、无修改 | 按一次画面生成过程组织，讲到组件时展示或高亮 |
| 显卡简化版 | Sonnet 5.5，高推理强度；2 分 8 秒 | 制作者认为自学已经够用 |
| TCP 三次握手 | Opus 5.5，Ultra，要求详细讲解；5 分 16 秒 | 制作者及一位通信专业同事评价较好，但部分英文发音有问题 |
| 刹车构造 | 4 分 26 秒，未单独说明模型设置 | 展示该方法在刹车结构科普中的应用 |
| 榫卯 | HTML 演示 1 分 29 秒，Anatomy 讲解视频 2 分 18 秒；HTML 页面使用 Opus 5.5 | 同一主题分别展示交互探索与按顺序讲解，两份产物均记录为一次生成 |

显卡视频的讲解顺序值得复用：

1. 显卡用来做什么。
2. 包含哪些组件。
3. 这些组件如何组装。
4. 一帧画面如何计算出来。
5. 显卡为什么计算得快。
6. 画面如何连续动起来。
7. 显卡如何散热。
8. 输入和输出分别是什么。

这些评价反映个人使用体验。机械关系、参数、计算过程和旁白中的技术细节仍需核对。

### 4.5 额度、耗时与限制

卡兹克、tashi 分享的制作记录可以用来估算等待时间和额度需求：

- 约 5 分钟的 TCP 三次握手视频，消耗约为其 200 美元 Claude Max 会员周额度的 1%；其他约 5 分钟的视频也大致在这一比例。
- 使用 Opus 5.5、Ultra 推理强度制作约 5 分钟视频，耗时约 1.5 小时。
- 模型选择上，卡兹克、tashi 建议：对外发布、追求精细零件时可尝试更强模型与较高推理强度；只用于自学时，可以先做简单版本，再决定是否细化。

这些消耗只反映具体任务和当时的产品配置，不能作为固定成本。额度与等待时间也需要分别考虑。Anatomy 的零件规划、几何构建、检查和局部审阅都要花时间；项目也说明了这类制作过程较慢。[Anatomy 限制说明](https://github.com/wheresryan22/anatomy#limits)

在卡兹克、tashi 记录的一次 Transformer 演示中，Agent 尝试训练小模型，随后会话受到限制；制作者将其理解为敏感行为判定。具体触发机制不明确，不能据此推导一般规则。

## 5. 按内容选择技术栈与视觉风格

下面按 16 类内容说明技术栈与风格的组合。除 Anatomy 与数学推导外，14 类样片由 LemoLab 制作，来自 [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar)，采用 CC BY 4.0；Anatomy 示例采用 MIT。实现细节依据罗佳 Rodya 的源码分析。

选择风格时要同时说明两类信息：画面、运动和声音是什么样；用什么技术实现笔触、材质和镜头。例如，水墨风既需要“宣纸、五种墨色、大面积留白”，也需要“Canvas 笔刷引擎、WebGL 晕染”。只指定“水墨风”通常不足以约束实现。


### 5.1 知识科普、讲解课

样片：LemoLab《Einstein in Your Pocket》（白板讲解风格）· [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) · CC BY 4.0

讲手机怎么知道你在哪：GPS、原子钟，和相对论每天多出的 38 微秒。仓库标注的适用场景：讲解、网课、科学。

实现与风格：

- 技术栈：② Canvas 2D。讲解类最重要的是“一笔一笔写出来”，每一笔的粗细、抖动、起笔墨点都要逐点控制，Canvas 最直接。墨水用正片叠底（multiply）叠加，重叠的地方自然变深，像真马克笔。
- 风格：一块光面白板，所有内容按真实书写顺序写出来；不画手，马克笔自己悬空移动；镜头在白板上移动，不切镜头；每一笔都有声音。

提示词：

```text
【风格】光面白板、按书写顺序一笔一笔写、不画手和光标、镜头在白板区域之间移动，不切镜头、留旧字残影

【技术栈】Canvas 2D、墨水 multiply 叠加、笔画加手抖和起笔墨点、单线字体按笔顺书写、数字先用 Python 算好
```

门槛：★★，花费低。Claude 网页版就能做。

### 5.2 新闻资讯、热点解读

样片：LemoLab《地图上还写着海》（卫星简报风格）· [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) · CC BY 4.0 · 卫星影像：Landsat，公有领域

卫星照着地图去找咸海，找到的却是沙漠。仓库标注的适用场景：气候与环境、调查与新闻解读、地理与历史。

实现与风格：

- 技术栈：② Canvas 2D 画标注线，④ WebGL2 着色器画地面。多张不同分辨率的卫星图嵌套在一起，镜头从太空一路推到地面；年份切换做成一道扫描线扫过画面；“分析师灰”的调色也是着色器算的。
- 风格：地面是真实卫星影像，调成冷灰，只在故事转折处恢复彩色；细白的测量线；每屏只说一个发现；一个连续镜头完成从太空到地面。

提示词：

```text
【风格】真实卫星影像、分析师冷灰调色、细白测量线、每屏一个发现、从太空推到地面的连续镜头、高度读数和比例尺

【技术栈】Canvas 2D 画标注层、WebGL2 着色器画地面、多级分辨率影像嵌套、扫描线切换年份、标注随地理坐标移动
```

门槛：★★★，花费中。难点是找到授权干净的影像。

### 5.3 软件产品：教程、功能发布

样片：LemoLab《Clawd Moves In》（活体实机录屏风格）· [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) · CC BY 4.0

看起来像真实的软件录屏，其实每个窗口、菜单、按钮都是重画的。一个像素小人在高清界面里“演”软件在做什么。仓库标注的适用场景：产品教程、功能发布、新手引导。

实现与风格：

- 技术栈：① HTML/CSS/SVG。软件界面本来就是网页元素，直接用它重画，字在任何缩放下都清晰，镜头可以推到任何地方。小人站在哪里，是每帧从页面的真实布局里量出来的，不是手写坐标。
- 风格：像真录屏，但全是重画的；界面浮在桌面壁纸上；低分辨率的像素小人和高清界面形成反差；光标代表用户，小人代表软件。

提示词：

```text
【风格】像真实录屏、名称和快捷键与真实产品一致、像素吉祥物演出软件在做什么、光标是用户，不画手

【技术栈】HTML/CSS/SVG 重画界面，不用截图、位置从 DOM 布局测量、弹簧动画、界面变化卡在音乐节拍上、快速甩镜头加运动模糊
```

门槛：★★，花费低。

### 5.4 硬件产品：发布、电商详情页

样片：LemoLab《二十一键》（产品拆解风格）· [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) · CC BY 4.0 · 键盘设计文件：foostan/crkbd，CC BY 4.0

一把开源键盘在一次环绕中逐层拆开，镜头钻到电路板背面看主控和灯珠，再合拢，把真实尺寸标在实物上。仓库标注的适用场景：硬件发布、电商产品页、技术参数讲解。

实现与风格：

- 技术栈：⑤ Three.js＋④ 着色器后期。外壳直接导入 3D 设计文件，电路板上每一条走线都按设计文件画成贴图；塑料、金属、电路板各用一套物理材质；先按两倍大小渲染再缩小，再加环境光遮蔽、景深、辉光。
- 风格：像产品摄影：暖色主光、冷色轮廓光、深灰无缝背景；各层沿一根轴浮起；零件名用细引线标在零件上；镜头一直在动，外面环绕、里面贴近。

提示词：

```text
【风格】影棚产品摄影、暖主光＋冷轮廓光、沿一根轴逐层拆开、引线标注在零件上、镜头持续环绕，不停

【技术栈】Three.js、MeshPhysicalMaterial 物理材质、导入 STEP 设计文件、HDRI 反射、2 倍超采样、环境光遮蔽＋物理景深＋辉光、尺寸只用文件里的数字
```

STEP 是设计源文件格式，制作前需要明确从设计文件到浏览器模型的转换或加载链路。Three.js 官方建议优先采用 glTF/GLB 工作流。[模型加载说明](https://github.com/mrdoob/three.js/blob/dev/manual/pages/loading-3d-models.html)

门槛：★★★★，花费高。这类 3D 风格对图形计算能力要求较高，渲染时间也更长；具体硬件要求需按工程核对。

### 5.5 机械原理、技术概念图解

示例：anatomy · raptor-engine · [Anatomy](https://github.com/wheresryan22/anatomy) · MIT

Raptor 2 火箭发动机挂在试车台上点火；鼠标悬停时，它拆成 11 个部件悬在立柱之间。仓库附带检查程序，用于核查管线在静止、拆开和中间过渡状态中的穿插。

实现与风格：

- 技术栈：① SVG 等轴测＋④ WebGL 着色器。发动机和试车台是 SVG：每个零件是实心体，侧面按朝向分四种明暗，从后往前画。尾焰是着色器画的，夹在前后两层 SVG 中间，用同一个相机，所以像长在图里。anatomy 产出的是可交互网页，做成视频要再用 ㉑ Playwright 逐帧录制。
- 风格：核心思路是物件本身就是解释：不画方框和箭头，而是发明一台真实的机器，让它的工作方式就是这个概念。比如“缓存没变就跳过”画成一把弹子锁：每颗弹子都对上了，锁芯才转。

提示词：

```text
【风格】不画方框箭头，发明一台机器来解释、几十个小而精确的零件、等轴测实心零件、只有一个零件用强调色、卡片式构图＋实时读数

【技术栈】SVG 等轴测、四种明暗从后往前画、先写至少 40 个零件的清单、火焰水光用 WebGL 着色器，夹在两层 SVG 之间、效果淡入淡出不硬切、用 Playwright 录制成视频
```

门槛：★★★，花费中。装 Skill 很简单，难在录制成视频。它擅长机器、仪器、工具，不擅长人物和精确地图。

### 5.6 数据报告：数据新闻、年报

样片：LemoLab《两条螺旋》（数据实物化风格）· [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) · CC BY 4.0 · 数据：IRENA 2026（经 Our World in Data），CC BY 4.0

十二年的风电和光伏装机，一片代表 10 吉瓦，绕着胡桃木表盘叠成两条螺旋。仓库标注的适用场景：年报与 ESG、投资者沟通、能源与气候统计。

实现与风格：

- 技术栈：⑳ Python 先把数据下载、算好；⑤ Three.js 用实例化一次渲染上千块薄片。每片随机错开几毫米、厚度差一点、中间留细缝，看起来才像真的叠起来；亚克力用透射材质，金属反射环境光。
- 风格：一个单位就是一块实物，规则在屏幕上说一次；数据增长是一块块放上去，不是缩放变形；最后镜头拉远，整张图变成一件装置。

提示词：

```text
【风格】一个单位＝一块实物、数据增长是一块块放上去、影棚光、浅景深、结尾拉远成装置、每个数字标出处

【技术栈】Python 处理数据存成 JSON、Three.js 实例化渲染、每块随机错位留缝、PBR 材质，亚克力用透射、环境光遮蔽＋物理景深
```

如果只要平面图表，同一仓库的“数据叙事”风格用纯 ② Canvas 2D：米色纸、红蓝铅笔、手写批注。

门槛：★★★，花费中；平面图表 ★★，花费低。

### 5.7 科研与工程实证

样片：LemoLab《林下的田》（点云测绘风格）· [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) · CC BY 4.0

激光点云把一片森林的树冠一层层剥掉，地面上露出当年农田的石墙。全片用了近 479 万个真实的激光扫描点。仓库标注的适用场景：考古与遗产、林业与环境、基建与场地勘测。

实现与风格：

- 技术栈：⑳ Python 下载和处理公开点云；⑤ Three.js 渲染，点的位置先压缩再进浏览器，几百万个点也跑得动；④ 自己写的着色器负责“剥开”：一个切割平面穿过点云，前面的点变亮、上面的点抬起淡出、后面的地表显形。
- 风格：近黑背景，点云悬浮在黑暗里；只有扫描前沿发光；测量线发丝一样细；整片一个连续运镜，从点云里“穿过去”。

提示词：

```text
【风格】真实点云，点不能被挪动、近黑底色，只有扫描前沿发光、按地面、植被、建筑分层剥开、发丝细的测量线、一个连续运镜穿过点云

【技术栈】Python 处理点云、Three.js 渲染点、自写着色器做切割平面、距离场画测量线、每个数字写进 FACTS.md，标明测量值
```

门槛：★★★★，花费高。难点在于找到授权干净的公开数据。

### 5.8 城市、地产与文旅

样片：LemoLab《被炸平的城市怎样长回来》（白模投影风格）· [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) · CC BY 4.0 · 建筑数据：3DBAG，CC BY 4.0

投影机把数据一层层打在鹿特丹的白色城市模型上：1940 年前留下的楼、后来几十年填满的空地、新长起来的塔楼。仓库标注的适用场景：城市规划与地产、展览展厅、城市数据与历史。

实现与风格：

- 技术栈：⑤ Three.js＋④ 着色器。建筑用荷兰公开的城市三维数据按比例拉伸；数据不是涂在模型上，而是作为光写进材质计算，所以只照亮朝向投影机的墙面；太阳按当地纬度和真实日期算位置，影子是真实投下的。
- 风格：暗房展台上的纯白模型；投影一次只打一层数据，每层回答上一层的问题；开灯开场，关灯数据登场，再开灯收尾。

提示词：

```text
【风格】纯白体块模型，立在暗房展台上、数据作为投影的光打上去、一次一层、开灯—关灯—开灯的结构

【技术栈】Three.js、公开建筑数据按比例拉伸，不编造、投影写进材质着色器，不贴图、真实太阳位置和阴影贴图、物理景深＋辉光＋暗角
```

门槛：★★★～★★★★，花费中到高。

### 5.9 历史、档案与纪录片

样片：LemoLab《差两秒》（档案灯台风格）· [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) · CC BY 4.0 · 档案：美国国会图书馆，公有领域

电报说莱特兄弟最长一次飞了 57 秒，报纸照登；放大镜下，玻璃底片和国会图书馆的记录说是 59 秒。仓库标注的适用场景：品牌历史与周年、纪录片与档案讲解、博物馆藏品故事。

实现与风格：

- 技术栈：② Canvas 2D 画圈注和读数，④ WebGL2 着色器画光学效果：灯箱从下面透光、玻璃底片的银盐色调、放大镜的枕形畸变和色边，都是逐像素算的。
- 风格：真实档案物件躺在冷白灯箱上；放大镜落下，镜片里的东西“活”过来；每件物件带真实的馆藏编号；只用一种信号色，不加做旧滤镜。

提示词：

```text
【风格】真实档案扫描件、冷白灯箱，光从下面透上来、放大镜里物件活过来、真实馆藏编号、一种信号色，不做旧

【技术栈】Canvas 2D 标注层、WebGL2 着色器做透光和放大镜畸变、物件按真实尺寸摆放、编号和出处写进 FACTS.md
```

门槛：★★★，花费中。

### 5.10 国风、节日与民俗

样片：LemoLab《The Swordsman and the River》（中国水墨风格）· [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) · CC BY 4.0

侠客踏水过江，一剑断流。仓库标注的适用场景：武侠、文化品牌、诗词。

实现与风格：

- 技术栈：② Canvas＋④ WebGL2 着色器。Canvas 里写了一个笔刷引擎：每一笔有几十根笔毛，墨量沿笔画递减，断开的地方就是飞白。湿笔交给着色器做晕染和边缘积墨；宣纸纹理也是着色器现算的，不用图片。
- 风格：宣纸上的写意水墨；墨分五色，只有印章一处红；不勾轮廓线，形体靠饱含墨的笔触；大面积留白；画面是“画出来”的，不是切出来的。

提示词：

```text
【风格】写意水墨、墨分焦浓重淡清五色、只有印章一处朱红、没骨，不勾轮廓线、飞白、大面积留白

【技术栈】Canvas 笔刷引擎（笔毛、墨量递减、飞白）、湿笔用 WebGL2 着色器做晕染和边缘积墨、宣纸纹理程序化生成、墨用透明度乘到纸上
```

门槛：★★★，花费中。同一仓库还有红色窗花剪纸、皮影戏、纸雕灯影，适合春节、神话和中秋题材。

### 5.11 儿童绘本、睡前故事

样片：LemoLab《The Moon Can't Sleep》（蜡笔儿童绘本风格）· [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) · CC BY 4.0

月亮失眠了，小女孩爬上屋顶给它唱摇篮曲。仓库标注的适用场景：绘本、睡前故事、儿童学习。

实现与风格：

- 技术栈：② Canvas＋④ WebGL2 着色器。每层蜡笔记录颜色和下笔压力，着色器只在纸纹凸起的地方留下蜡：轻压是零星颗粒，重压接近实心。水彩单独一层，遇到蜡会被排开。这种“材料感”是算出来的，不是加滤镜。
- 风格：一页正在被画出来的绘本；孩子的透视，颜色涂出线外；每条线轻轻“沸腾”，像每帧重画了一遍；最后刷一遍水彩收尾。

提示词：

```text
【风格】正在被画出来的绘本页、孩子的透视，涂出线外、线条轻微沸腾、最后刷水彩揭晓、旁白就是书页上的字

【技术栈】Canvas 画笔触、WebGL2 着色器模拟蜡粘在纸纹凸起处、压力决定颗粒多少、水彩被蜡排开、纸纹固定在纸面上
```

门槛：★★～★★★，花费低到中。

### 5.12 品牌广告、MV、情感短片

样片：LemoLab《The Colour of Rain》（油画厚涂风格）· [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) · CC BY 4.0

灰色雨中的广场，第一把红伞撑开，圆舞曲把整个广场刷上颜色。仓库标注的适用场景：音乐 MV、艺术与文化、情感广告。

实现与风格：

- 技术栈：② Canvas＋④ WebGL2 着色器。先把每个场景画成明暗清楚的扁平插画，再转成一道道刮刀笔触；着色器把颜料当成高度场，让光从侧面扫过，颜料的起伏才看得见。2 倍超采样，故意不加胶片颗粒，免得压缩吃掉刀痕。
- 风格：调色刀厚涂；大块平整、边缘锋利的色面；先保证明暗，再追求质感；只有故事里该动的东西动。

提示词：

```text
【风格】调色刀厚涂、大块锋利色面、侧光扫过颜料起伏、缩略图也一眼看懂、静止的颜料不动

【技术栈】先画明暗扁平插画再转笔触、笔触不跨形状分组、WebGL2 高度场侧光、2 倍超采样，不加颗粒
```

门槛：★★～★★★，花费低到中。有真人出镜的 MV，可以先用 ⑰ 视频模型生成绿幕人物，再让 Claude 抠像、用代码做场景。

### 5.13 搞笑、萌宠与社媒短片

样片：LemoLab《胖橘案卷》（复古半调案卷风格）· [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) · CC BY 4.0

橘猫胖橘被立案审查：测试重力、凌晨跑酷，最后无罪释放。仓库标注的适用场景：幽默、萌宠、社媒短片。

实现与风格：

- 技术栈：① SVG 排版标题和图章，② Canvas 画网点和纸张。阴影不用渐变，全用网点，几层网点用不同角度叠印；角色加一点“线条沸腾”的抖动，文字和网点不加。
- 风格：复古印刷案卷；奶油色档案纸、错位的大标题、啪地盖下的图章；用官僚的严肃感讲鸡毛蒜皮的事；每 2–4 秒一张卡片。

提示词：

```text
【风格】复古印刷案卷、网点叠印、错位粗体大标题、橡皮图章、严肃口吻讲小事、每 2–4 秒一张卡片

【技术栈】SVG 排文字和图章、Canvas 画网点，不用渐变、多层网点不同角度叠印、纸纹乘在最上层、只给角色加线条抖动
```

门槛：★★，花费低。

### 5.14 游戏预告、像素与怀旧

样片：LemoLab《The Last Save Point》（16-bit 像素 RPG 风格）· [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) · CC BY 4.0

勇士在最终 Boss 门前存档，存档画面闪回一路冒险。仓库标注的适用场景：游戏预告、回顾、怀旧。

实现与风格：

- 技术栈：② Canvas 2D。画面先画在 320×180 的小画布上，再整数倍放大到 1080p、关掉平滑，每个像素才是清楚的小方块；颜色只从约 32 色的调色板里取，渐变用抖动点阵代替；镜头只按整数像素移动。
- 风格：像 90 年代中期的主机 RPG：对话框逐字打出、菜单、存档、芯片音乐；角色只有几帧动画，表情交给头像框；用游戏自己的系统讲故事。

提示词：

```text
【风格】90 年代主机 RPG、对话框逐字打出、菜单和存档画面、芯片音乐、认真不恶搞

【技术栈】Canvas 2D、320×180 画布整数倍放大，关闭平滑、固定调色板、Bayer 抖动代替渐变、镜头整数像素移动
```

门槛：★，花费低。像素风是最适合新手练手的类型。

### 5.15 片头、活动开场与品牌视觉

样片：LemoLab《The Velvet Cipher》（60s 间谍片头风格）· [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) · CC BY 4.0

一部虚构的 1964 年间谍片的片头：剪纸人影追一把被偷的钥匙，几何碎片最后拼成片名。仓库标注的适用场景：片头、活动开场、预告片。

实现与风格：

- 技术栈：② Canvas 2D＋opentype.js。字形用 opentype.js 取出轮廓再“剪”一遍；每个形状的边缘加一点低频抖动，像手剪的，而且剪一次就缓存，移动时边缘不会乱跳；纸片之间留细缝、投小阴影。
- 风格：四色剪纸平涂，没有渐变；人物是侧面剪影；字就是画面结构；铜管乐的每一声重音都是剪辑点。

提示词：

```text
【风格】60 年代片头、四色剪纸平涂、侧面剪影人物、文字当成建筑和道具、重音即剪辑点

【技术栈】Canvas 2D、opentype.js 取字形轮廓、边缘手剪抖动并缓存、纸片间留缝和小阴影、颗粒在 ffmpeg 里加
```

门槛：★★，花费低。

### 5.16 数学与理科推导

这一类 lemo-opuscar 和 anatomy 都没有专门的风格，例子是 3Blue1Brown：Manim 就是这个 YouTube 频道的作者为自己的视频写的。

实现与风格：

- 技术栈：⑧ Manim。你只写画面里有哪些对象、它们怎么变化，中间过程由 Manim 自动算出来；公式用 LaTeX 排版，非常精准，缺点是风格偏素。
- 风格：深色背景、干净的几何和公式；每一步只出现一个新东西，旧的东西变形成新的；同一个量始终同一种颜色。

提示词：

```text
【风格】深色背景、每步只出现一个新东西、公式在原位变形、同一个量始终同一种颜色、节奏慢

【技术栈】Manim 社区版、MathTex 排公式、Transform 变形、数值先用 Python 算好、先低画质预览再出 1080p
```

门槛：★★★，花费低。Manim 需要装 Python 和 LaTeX 环境。

### 5.17 把主题、风格与技术栈拼成完整请求

把主题、时长、画幅、风格、技术栈和预览要求写在同一条请求里，例如：

```text
做一支 45 秒的横屏短片，讲张若虚《春江花月夜》里“江畔何人初见月”这一句。

【风格】写意水墨：墨分焦浓重淡清五色，只有印章一处朱红；没骨，不勾轮廓线，形体靠饱含墨的笔触；快笔留飞白；画面大面积留白，东西是一笔笔画出来的，不切镜头。

【技术栈】用 Canvas 写一个笔刷引擎（笔毛、墨量递减、飞白）；湿笔交给 WebGL2 着色器做晕染和边缘积墨；宣纸纹理在着色器里程序化生成；墨用透明度乘到纸上。

开工前先给我分镜表和 3 张关键帧，确认后再渲整片。
```

先确认分镜和关键帧，可以在完整渲染前检查讲解顺序与风格。下面汇总 16 类内容的技术组合，编号对应第 2 节，星级表示参考难度。

![16 类视频的技术栈与难度速查](https://raw.githubusercontent.com/hangx969/upload-images-md/main/ai-code-video-20261021-27-0f962322de.jpg)

## 6. Skill 选型与安装

模板演示可选 AI-Animation-Skill，结构拆解可选 Anatomy；需要完整的视频制作流程时，再按预览方式、时间轴、风格库和配音需求选择下面的工具。

### 6.1 xilo-opus-video：先比较方案和预览

参考门槛：★，花费低，适合通用入门。它先提供三个风格差异较大的方案，每个方案配一张预览图；选定后逐个镜头制作，并按内部评分要求检查到每项 8 分以上再交付。评分是流程中的自检，不能替代内容核对。

把下面的请求发给 Agent：

```text
帮我安装这个 Skill：https://github.com/Kianzzz/xilo-opus-video
```

### 6.2 HyperFrames 官方 Skill：用 HTML 安排时间轴

参考门槛：★★，花费低。包含 20 多个场景，覆盖无人出镜讲解、动态图形、音乐驱动视频、产品发布、幻灯片转视频等，适合资讯和软件产品类内容。

```bash
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
```

### 6.3 Remotion 官方 Skill：长片与系列化工程

参考门槛：★★，花费低。12 个 Skill 覆盖建项目、渲染、字幕、多媒体和地图等能力。适合希望在 Remotion 中持续复用组件、字幕和视觉风格的项目。

```bash
npx skills add remotion-dev/skills
```

### 6.4 lemo-opuscar：风格库与完整制作指南

参考门槛：★★★，花费中高。lemo-opuscar 同时提供风格库和制作流程：

- 51 种影片风格，每种有风格提示词和一支纯代码样片。
- 导演指南与技术指南：前者处理故事、节奏、镜头和自检，后者处理逐帧渲染、配音、配乐与混音。
- 声音流程：中文配音用 edge-tts，英文用 Kokoro，再用 Whisper 校对；配乐结合免费真乐器采样库和代码合成。
- 自定义风格：选择一个已有风格修改、命名，先制作 15～30 秒测试片。

```bash
claude plugin marketplace add lemomo-ai/lemo-opuscar
claude plugin install lemo-opuscar@lemolab
```

安装后的请求示例：

```text
用油画厚涂风格做一支 30 秒的片子，讲我家那只每天在窗台等我下班的橘猫。
```

开工前，流程会集中确认主题中无法自行决定的问题、是否有自备配音与音乐、是否先看分镜。按项目维护者的经验，一条片约需 30～60 分钟，token 用量不小；依赖 Node 20+、FFmpeg 和 Python 3.11+。开发环境为 macOS，Windows 可采用 WSL；3D 和大量着色器效果还需评估图形计算资源。

具体环境以 [lemo-opuscar 当前要求](https://github.com/lemomo-ai/lemo-opuscar#before-you-start) 为准，不能与其他工程混用版本下限。

### 6.5 creator-style-kit：竖屏资讯风格

@threeaus 的项目包含 18 套 9:16 竖屏风格，基于 HyperFrames。每套定义字体、配色、动效、音效与构图，适合资讯视频，还需要配合脚本和配音 API。参考门槛：★★★，花费中。

```bash
git clone https://github.com/threeaus/creator-style-kit.git
```

### 6.6 lanshu-create-ai-presenter-video：数字人与风格化讲解

岚叔的项目支持数字人讲解，或 12 种风格化讲解，包含配音与自动验收。需要相应配音或数字人服务；参考门槛：★★★，花费中到高。

```bash
git clone https://github.com/cclank/lanshu-create-ai-presenter-video.git ~/.claude/skills/lanshu-create-ai-presenter-video
```

### 6.7 weilanx-claude-videos：将持续创作流程沉淀为 Skill

这是一个 Remotion 工程，内含 8 个 Skill：一个用于拆解已有视频风格，另外 7 个面向给定选题后的整套制作。适合持续制作知识短视频，并逐步积累自己的制作流程。参考门槛：★★★★，花费中。

```bash
git clone https://github.com/Azure12355/weilanx-claude-videos.git
```

## 7. 渲染前后检查什么

几种路线最终都需要检查内容、画面和声音：

1. **脚本与事实**：明确受众和解释深度，核对术语、关键原理、数据出处与尺寸。科研、地图和档案题材保留数据与素材授权记录，必要时使用 `FACTS.md` 记录数值来源。
2. **分镜与画面**：先看关键帧，再检查运动、转场、字幕以及零件关系。结构精细或齿轮看似啮合，并不能证明机械或物理原理正确。
3. **时间控制**：需要逐帧渲染时，确认画面由时间或帧号决定，随机效果可重现；将交互动作安排成可播放过程。
4. **配音与混音**：人工试听，检查音色、英文发音、语速、节拍以及旁白、背景音乐、音效的音量关系。
5. **成片与成本**：完整观看导出结果，分别记录 Agent 额度、外部 API 费用、生成等待时间和本地渲染时间。

需要复刻某个作品时，应先识别它实际使用的技术栈和素材，而不是仅凭“由 Claude 制作”判断。可以查阅创作者公开的源码和制作说明，或直接向创作者了解实现方法。

## 8. 来源与延伸阅读

### 8.1 项目与工具

- [AI-Animation-Skill](https://github.com/Unclecheng-li/AI-Animation-Skill)：HTML 科普演示工作流，MIT。
- [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar)、[样片画廊](https://lemomo-ai.github.io/lemo-opuscar/)：文中 LemoLab 样片的主要来源，样片按 CC BY 4.0 署名；代码许可与具体素材许可需分别核对。
- [xilo-opus-video](https://github.com/Kianzzz/xilo-opus-video)、[Anatomy](https://github.com/wheresryan22/anatomy)：预览优先的制作流程、交互式原理模型。
- [HyperFrames](https://github.com/heygen-com/hyperframes)、[Remotion](https://github.com/remotion-dev/remotion)、[Remotion 官方 Skill](https://github.com/remotion-dev/skills)：浏览器代码视频框架。
- [Manim 原项目](https://github.com/3b1b/manim)、[Manim 社区版](https://github.com/ManimCommunity/manim)：数学与几何动画；第 5.16 节提示词使用社区版。
- [Motion Canvas](https://github.com/motion-canvas/motion-canvas)、[Revideo](https://github.com/redotvideo/revideo)、[blender-mcp](https://github.com/ahujasid/blender-mcp)：讲解动画及三维操作路线。
- [p5.brush](https://github.com/acamposuribe/p5.brush)、[ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase)：笔刷与代码动画相关资源。
- [creator-style-kit](https://github.com/threeaus/creator-style-kit)、[lanshu-create-ai-presenter-video](https://github.com/cclank/lanshu-create-ai-presenter-video)、[weilanx-claude-videos](https://github.com/Azure12355/weilanx-claude-videos)：竖屏风格、讲解视频和系列制作工程。
- [awesome-opus-5-5-videos](https://github.com/athemeroy/awesome-opus-5-5-videos)、[awesome-ai-motion](https://github.com/guanmo-ai/awesome-ai-motion)：案例合集。

### 8.2 制作案例与经验

- [@xilo2991：零基础入门 Opus 5.5 做视频](https://x.com/xilo2991/status/2104912748794589515)：包含着色器渲染耗时从 7 秒变为 48 秒的测试记录。
- [@threeaus：如何用 Claude / DeepSeek 做资讯类视频](https://x.com/threeaus/status/2112394912029409410)。
- [@AI_DVD6：两条 AI 知识短片，都破了 13 万播放](https://x.com/AI_DVD6/status/2111273399943057458)。
- [@zureA255062：Opus 5.5 抖音起号万字教程](https://x.com/zureA255062/status/2111642497927798995)。
