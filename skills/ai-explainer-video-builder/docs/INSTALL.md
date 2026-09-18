# 安装

## 1. 从 GitHub 安装 Skill

```bash
npx skills add https://github.com/Huxi-xiao/VIDEO-EDIT --skill ai-explainer-video-builder
```

如果当前环境不支持 `npx skills add`，将仓库中的：

```text
skills/ai-explainer-video-builder/
```

作为 Skill 目录安装。

## 2. 本地依赖

基础：

- Python 3.10+
- FFmpeg
- ffprobe

推荐：

- faster-whisper 或 Whisper CLI：本地转录
- Node.js / npm / npx：Remotion 动态视觉
- Pillow：Remotion 不可用时的静态视觉降级

检查：

```bash
python engine/doctor.py
```

安装 Python 轻依赖：

```bash
pip install -r requirements.txt
```

安装 Remotion：

```bash
cd renderer
npm install
cd ..
```

## 3. 关于 AI 图片 / AI 视频

AI 图片：使用当前 Codex / Work 环境中可用的图片能力；没有就自动降级为 Motion / Slide。

AI 视频：不是 V0.2 必需能力。未来即使接入任何视频模型，也必须先人工审批。
