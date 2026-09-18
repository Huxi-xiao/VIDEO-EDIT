# VIDEO-EDIT

面向 **Codex / ChatGPT Work 本地工作流** 的口播/教程视频自动制作 Skill。

当前版本：**v0.2.0**

V0.2 的目标不是继续堆功能，而是解决 V0.1 实测中的三个核心问题：

1. 模型算力消耗过高；
2. 口播与用户录屏/图片的匹配不够准确；
3. Slide / Motion 画面缺乏统一的视觉系统。

因此 V0.2 重构为：

> **Thin Skill + Thick Engine**
>
> AI 只做一次高价值语义判断，后续尽量交给 Python / FFmpeg / Remotion 执行。

## 安装

推荐从 GitHub 安装：

```bash
npx skills add https://github.com/Huxi-xiao/VIDEO-EDIT --skill ai-explainer-video-builder
```

如你的 Skill 管理器不支持上述命令，可将：

```text
skills/ai-explainer-video-builder/
```

作为 Skill 目录安装。

## 快速开始

```bash
cd skills/ai-explainer-video-builder
python engine/doctor.py
python engine/init_project.py --name ~/Videos/my-video
python engine/scan_assets.py ~/Videos/my-video
```

然后在 Codex / Work 中：

> 使用 ai-explainer-video-builder 处理当前项目。读取 config/analysis_packet.json，只进行一次 Master Analysis，并按 Rule Profile 继续执行。

完整教程见：

- [安装说明](skills/ai-explainer-video-builder/docs/INSTALL.md)
- [使用说明](skills/ai-explainer-video-builder/docs/USAGE.md)
- [V0.2 架构](skills/ai-explainer-video-builder/docs/ARCHITECTURE.md)

## 关键原则

- 主叙事源：`视频 > 音频 > 文案`
- 用户真实素材优先于生成素材
- 录屏匹配采用“动作 + 对象 + 阶段 + 文件名 + 顺序”评分
- 低置信度不硬配，自动降级为 Slide / Motion
- 视觉页面只从固定 Layout Library 中选择，不让模型自由设计整页
- Visual Hammer 作为高优先级记忆点模板
- AI Video 不是 V0.2 核心依赖
- 任意 AI Video 调用必须人工批准
- 单个任务失败不能拖死整个项目
- 最终输出成片 + 编号独立片段 + 音轨 + 字幕 + Timeline

## 版本

见 [CHANGELOG.md](CHANGELOG.md)。
