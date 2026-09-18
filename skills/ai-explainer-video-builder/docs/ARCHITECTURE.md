# V0.2 架构

## 为什么 V0.1 算力高

V0.1 将 Content Analysis、Concept Extraction、Visual Copy、Visual Planner、Asset Matching、QA 分散成多次模型判断。同一段口播被反复理解。

V0.2 改为：

```text
Transcript + compact Asset Index
             ↓
      ONE Master Analysis
             ↓
      master_analysis.json
             ↓
  Deterministic Semantic Matcher
             ↓
       compile_plan.py
             ↓
 FFmpeg / Remotion / Python Engine
```

模型只负责“机器规则难以可靠完成”的判断。

## Semantic Matching Engine

教程视频不能只按主题匹配素材，还必须匹配阶段：

```text
BEFORE
ACTION
PROCESS
RESULT
AFTER
```

例如：

- “点击生成思维导图” → ACTION 录屏
- “这是最后生成的思维导图” → RESULT 截图

即使都包含“思维导图”，也不能互换。

默认匹配权重：

```text
文件名语义          30%
action/object/context 30%
阶段                 20%
素材类型             10%
顺序连续性           10%
```

低于阈值时不硬配。

## Visual Design Engine

V0.2 不允许模型每一页从零设计。

模型只做：

> 选择 Layout + 填入精简文案。

Renderer 做：

> 应用 Design Tokens + 固定 Layout + 固定 Motion Vocabulary。

### 默认 Layout

- Hammer Center
- Statement Left
- Comparison 50/50
- Comparison 70/30
- Steps Vertical
- Three Points
- Flow Center
- Big Number
- Result Focus
- Media 70/30
- Full Bleed Media
- Screen Focus

### Motion vocabulary

- Fade
- Reveal
- SlowScale
- HorizontalSlide
- PathFlow

## 算力目标

V0.2 的目标不是承诺固定百分比，而是用同一项目 A/B 测试：

- 模型调用次数明显下降
- 同一内容不重复语义分析
- 大量 QA / 状态 / 文件检查转移到代码
- FFmpeg/Remotion 接管确定性执行
