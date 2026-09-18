# Changelog

## 0.2.0

### Compute Optimization
- 将多轮 Content Analysis / Visual Copy / Visual Planner 合并为一次 Master Analysis。
- AI 仅输出结构化 `master_analysis.json`，后续交给确定性脚本执行。
- 素材扫描、媒体信息、代理、时间线、重试、状态、QA 尽量程序化。

### Semantic Matching Engine
- 新增 `asset_index.json`。
- 文件名作为高权重语义信息。
- 支持 `ACTION / PROCESS / RESULT / BEFORE / AFTER` 阶段识别。
- 使用 action/object/software/stage/filename/order 进行确定性评分。
- 匹配分低于阈值时禁止硬配素材，回退到 Slide / Motion。

### Visual Design Engine
- 新增固定 Design Tokens。
- 新增 Layout Library，不再让模型自由排每一页。
- 默认提供 Light Minimal / Dark Tech 两套设计系统。
- Visual Hammer 独立为核心模板。
- 增加信息密度规则：连续高密度画面后优先插入低密度视觉。
- 统一截图、图片、AI 图的 Media Treatment。

### Execution Layer
- 新增 FFmpeg 代理、裁切、标准化、静音检测等执行脚本。
- 新增 Remotion VisualSlot 渲染器。
- 新增 `compile_plan.py` 和 `render_slots.py`。
- 新增 Master Analysis schema 和 Timeline schema。

### Safety / Reliability
- 保留 AI Video 强制人工审批 Gate。
- 保留 bounded retry / checkpoint / fallback / circuit breaker。
- AI Video 付费失败后禁止自动重试。

## 0.1.0
- 初版工作流骨架。
