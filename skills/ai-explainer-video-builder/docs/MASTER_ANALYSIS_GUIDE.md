# Master Analysis 生成指南

Master Analysis 是 V0.2 唯一主要语义规划步骤。

输入：

- `config/analysis_packet.json`
- `content_analysis/transcript.json`
- 必要时：仅含义不清的素材 contact sheets
- Rule Profile

输出：

- `content_analysis/master_analysis.json`

## 强约束

1. 不要为了“用上用户素材”而硬配。
2. 口播说操作时，match_query.stage 应为 ACTION/PROCESS。
3. 口播说结果时，match_query.stage 应为 RESULT/AFTER。
4. Visual Hammer 优先 1–4 个中文字/极短词。
5. 屏幕文案不是完整口播转写。
6. Slide 只选择 `layout_library.json` 中存在的 layout。
7. 两个连续高密度画面后，如果内容允许，下一段优先低密度视觉。
8. AI Image 只用于真实素材和信息设计都不足的场景。

## 示例 section

```json
{
  "id": "S04",
  "source_start": 42.1,
  "source_end": 50.7,
  "keep": true,
  "content_type": "DEMO",
  "importance": "A",
  "transcript": "接下来把准备好的PDF资料直接拖进去。",
  "concept": "上传资料",
  "cleanup_tags": [],
  "visual": {
    "preferred_type": "SCREEN",
    "layout": "screen_focus",
    "headline": "上传资料",
    "body": [],
    "density": "medium",
    "motion": "Fade",
    "ai_image_prompt": "",
    "match_query": {
      "action": "上传",
      "object": "PDF资料",
      "software": "NotebookLM",
      "stage": "ACTION",
      "keywords": ["上传", "PDF", "资料"]
    }
  }
}
```
