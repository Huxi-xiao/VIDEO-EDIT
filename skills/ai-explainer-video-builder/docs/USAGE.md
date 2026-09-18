# 使用说明

## 1. 创建项目

```bash
python engine/init_project.py --name ~/Videos/my-video
```

## 2. 放入素材

三选一必填：

```text
01_primary/video/
01_primary/audio/
01_primary/script/
```

优先级：`video > audio > script`

可选：

```text
02_screen_recordings/
03_images/
04_extra_videos/
05_references/
06_brand_assets/
07_background_music/
08_sound_effects/
09_voice_reference/
```

建议命名：

```text
01_ACTION_上传PDF.mp4
02_ACTION_输入Prompt.mp4
03_RESULT_摘要结果.png
04_RESULT_思维导图.png
```

不强制使用前缀，但越清楚越容易高精度匹配。

## 3. 扫描

```bash
python engine/scan_assets.py ~/Videos/my-video
```

如果是长/4K素材，可选生成代理：

```bash
python engine/proxy.py ~/Videos/my-video
```

如果素材名称含义不清晰，只为这些素材生成 contact sheet：

```bash
python engine/make_contact_sheet.py ~/Videos/my-video
```

## 4. 转录

视频或音频主叙事：

```bash
python engine/transcribe.py ~/Videos/my-video --model small
```

## 5. Master Analysis

在 Codex / Work 中说：

> 使用 ai-explainer-video-builder。读取 config/analysis_packet.json 和 content_analysis/transcript.json。只进行一次 Master Analysis，输出 content_analysis/master_analysis.json，并严格遵循 schema。

这一轮一次完成：

- 内容结构
- 删除/保留判断
- Visual Hammer 候选
- 屏幕文案
- 画面类型
- 素材匹配查询语义
- 模板选择

不要再分别运行多轮“内容分析 / Visual Copy / Visual Planner”。

## 6. 确定性素材匹配

```bash
python engine/semantic_match.py ~/Videos/my-video
```

如果最高素材匹配低于默认 0.65，系统不会硬配错误素材，会改用 Slide/Motion。

## 7. 编译时间线

```bash
python engine/compile_plan.py ~/Videos/my-video
python engine/make_subtitles.py ~/Videos/my-video
python engine/prepare_narration.py ~/Videos/my-video
```

## 8. 渲染

```bash
python engine/render_slots.py ~/Videos/my-video
python engine/assemble.py ~/Videos/my-video
```

## 9. 输出

```text
output/
├── 01_final/
│   ├── final_master.mp4
│   └── final_no_subtitles.mp4
├── 02_timeline_clips/
│   ├── 001_....mp4
│   ├── 002_....mp4
│   └── ...
├── 03_audio/
├── 04_subtitles/
└── 07_editing_data/
    ├── timeline.csv
    ├── timeline.json
    ├── storyboard.md
    └── exception_report.md
```

把 `02_timeline_clips` 按编号导入 Premiere / 剪映 / DaVinci，即可针对单独片段替换和二剪。

## 10. 三种模式

- `full_auto`：除硬审批外连续运行
- `critical_checkpoints`：素材扫描 / 视觉分镜 / 最终预览确认
- `step_by_step`：每阶段确认

AI Video 无论哪种模式都必须人工批准。
