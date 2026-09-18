---
name: ai-explainer-video-builder
description: >
  Build an editable explainer/talking-head video project from one primary narrative source
  (video, audio, or script) plus optional screen recordings, images, extra video, brand assets,
  music, SFX, references, and authorized voice reference. Optimized for low model usage:
  one Master Analysis pass, deterministic semantic matching, FFmpeg execution, fixed Remotion
  visual templates, numbered replaceable timeline slots, and bounded fallbacks.
version: 0.2.0
---

# AI Explainer Video Builder v0.2

## Core architecture

Use **Thin Skill + Thick Engine**.

The model should do only work that actually needs semantic judgment:

1. understand the narration once;
2. extract action/object/software/stage anchors;
3. decide the visual intent for each kept section;
4. create short screen copy / Visual Hammer copy.

Do NOT repeatedly re-analyze the same transcript in separate Content Analysis, Visual Copy,
Visual Planner, Asset Matching, and QA passes. Merge them into one **Master Analysis**.

After `master_analysis.json` is written, prefer deterministic scripts for:

- asset matching;
- media probing;
- proxy creation;
- timeline compilation;
- FFmpeg cuts/normalization/concat;
- Remotion rendering;
- retries, timeout, state, fallback and QA.

## Required input

At least one primary narrative source is required:

`video > audio > script`

Project input folders:

```text
01_primary/video/
01_primary/audio/
01_primary/script/
02_screen_recordings/
03_images/
04_extra_videos/
05_references/
06_brand_assets/
07_background_music/
08_sound_effects/
09_voice_reference/
```

Only the primary narrative is required. Everything else is optional.

If video, audio and script are all absent: STOP and tell the user.

## First run / profiles

If no saved Rule Profile exists, run the setup flow and save the result to
`config/rule_profile.json` plus a human-readable summary.

Later runs should offer:

1. use saved profile;
2. use saved profile with temporary overrides;
3. choose another profile;
4. recreate profile.

Workflow modes:

- `full_auto`
- `critical_checkpoints`
- `step_by_step`

`full_auto` never bypasses hard approval gates.

## Stage 1 — deterministic preflight

Run or emulate:

```bash
python engine/doctor.py
python engine/scan_assets.py <project>
```

This creates:

- `config/project_manifest.json`
- `config/asset_index.base.json`
- `config/analysis_packet.json`
- `config/workflow_state.json`

Prefer filenames as strong semantic hints. The user intentionally names recordings/images to help
recognition.

File-name prefixes may include:

- `ACTION_`
- `PROCESS_`
- `RESULT_`
- `BEFORE_`
- `AFTER_`

Do not waste model calls inspecting an asset if its name/folder already makes its meaning clear.
Only inspect ambiguous assets. If visual inspection is required, create one compact contact sheet
instead of repeatedly opening the full video.

## Stage 2 — ONE Master Analysis

Read the narration/transcript plus `config/analysis_packet.json`.

Produce exactly one semantic planning artifact:

`content_analysis/master_analysis.json`

It must validate against:

`schemas/master_analysis.schema.json`

In this single pass, determine for each narration section:

- keep/drop;
- content type;
- importance A/B/C;
- short concept / Visual Hammer candidate;
- visual need;
- semantic match query:
  - action;
  - object;
  - software/context;
  - stage (`BEFORE/ACTION/PROCESS/RESULT/AFTER/UNKNOWN`);
- preferred visual type;
- short screen copy;
- slide/motion template if needed;
- AI-image prompt only when necessary.

Do NOT directly force a supporting asset when confidence is weak. The deterministic matcher chooses
user assets after Master Analysis.

Content tags may include:

`HOOK, BACKGROUND, PROBLEM, CLAIM, EXPLANATION, EXAMPLE, DEMO, STEP, COMPARISON, EVIDENCE, RESULT, SUMMARY, CTA, TRANSITION`

Cleanup tags may include:

`FILLER, RESTART, REDUNDANT, LONG_PAUSE, OFF_TOPIC, FACT_CHECK_REQUIRED`

## Stage 3 — Semantic Matching Engine

Run:

```bash
python engine/semantic_match.py <project>
```

Matching is deterministic and should favor:

1. filename semantics;
2. action/object similarity;
3. stage match;
4. media-type suitability;
5. sequence/order continuity.

Default score weights:

- filename semantics: 0.30
- action/object/software: 0.30
- stage: 0.20
- media-type suitability: 0.10
- sequence/order: 0.10

If best match is below the profile threshold (default `0.65`):

**DO NOT hard-match an unrelated user asset.**

Fallback to:

`SLIDE/HAMMER/MOTION -> AI_IMAGE (if enabled) -> simple neutral visual`

This rule has higher priority than “always use user assets”. User assets are preferred only when
meaningfully relevant.

## Stage 4 — Visual system

Do not let the model freely design each page.

Choose from the fixed Visual Design System in:

- `config/design_tokens.light.json`
- `config/design_tokens.dark.json`
- `config/layout_library.json`

Primary visual types:

- `AROLL`
- `SCREEN`
- `MEDIA`
- `SLIDE`
- `HAMMER`
- `MOTION`
- `AI_IMAGE`

### Visual Hammer

Use a Hammer when a segment has one memorable concept/turning point.

Preferred copy:

- 1–4 Chinese characters / very short words when possible;
- normally max ~8 Chinese characters / short words;
- one main concept only.

Examples: `健康`, `碎`, `整合`, `稳定`, `省事`, `从小事开始`.

### Screen copy

Do not paste narration verbatim by default.

Prefer:

- Hammer;
- Big Statement;
- Comparison;
- Steps;
- List;
- Diagram/Flow;
- Result.

One main idea per screen. If dense, split it.

### Information density rhythm

Avoid long runs of dense information screens.

After two consecutive high-density slots, prefer one lower-density beat when narration permits:

- ARoll;
- Hammer;
- simple image;
- spacious result card.

## Stage 5 — compile / render

After Master Analysis and matching:

```bash
python engine/compile_plan.py <project>
python engine/prepare_narration.py <project>
python engine/render_slots.py <project>
python engine/assemble.py <project>
```

The engine should create numbered replaceable clips:

```text
001_AROLL_hook.mp4
002_HAMMER_省事.mp4
003_SCREEN_upload_pdf.mp4
004_MOTION_5_to_1.mp4
```

The number is timeline order.

Each slot should preserve its planned duration whenever practical so the user can replace a clip in
Premiere / 剪映 / DaVinci without shifting everything after it.

## Visual quality

Default design systems:

### Light Minimal

- off-white/light gray background;
- dark text;
- strong typography hierarchy;
- generous whitespace;
- restrained accent;
- 24–32px-like rounded cards;
- subtle shadow;
- minimal motion.

### Dark Tech

- dark gray/navy background;
- white primary text;
- muted secondary text;
- restrained accent/glow;
- line-based diagrams;
- minimal motion.

Media treatment should be consistent:

- screenshots: rounded container + subtle shadow + clean background;
- AI image: full bleed or framed, slow push/pan;
- vertical image: never stretch; use fit + neutral background treatment;
- result screenshot: center emphasis, optional soft background duplicate.

Use only a small animation vocabulary:

`Fade, Reveal, SlowScale, HorizontalSlide, PathFlow`

## AI image

AI image is a gap-filling capability, not a default.

Good uses:

- abstract concept;
- environment/scene;
- metaphor;
- missing illustrative B-roll.

Do not fabricate:

- software UI;
- evidence screenshots;
- precise charts/data;
- exact branded products when real assets exist.

If unavailable/fails:

`AI_IMAGE -> MOTION/SLIDE`

## AI video — HARD HUMAN GATE

V0.2 does not depend on generative video.

If a future capability/provider makes `AI_VIDEO` available, every invocation requires explicit human
approval, even in Full Auto.

Before generation show:

- slot/time;
- narration;
- reason;
- prompt;
- duration;
- provider/model;
- resolution;
- estimated cost/credits when available;
- fallback.

Allowed decisions:

1. approve;
2. edit prompt then approve;
3. downgrade to AI image + motion;
4. downgrade to slide/motion;
5. skip.

Never automatically retry a paid AI-video generation after failure.

## Voice clone / repair

Use only the user's own voice or a voice they confirm they are authorized to use.

Voice repair priority:

1. cut filler/restart;
2. rebuild from recorded speech if natural;
3. synthesize a replacement line only when needed and authorized.

For repaired talking-head speech, cover with B-roll/slide/screen unless genuine lip sync exists and
was approved.

Do not add new opinions or substantive claims during repair.

## Fail-safe

No task may run forever.

Use bounded retry, timeout, checkpoint and fallback.

Typical retry ceiling:

- local IO: 3
- transcription: 2
- FFmpeg: 2
- Remotion: 2, then static fallback
- AI image: 2, then Motion/Slide
- AI video: no automatic paid retry

Task states:

`PENDING, RUNNING, COMPLETED, FAILED, SKIPPED, WAITING_USER, INTERRUPTED`

If a tool/provider repeatedly fails, circuit-break and downgrade remaining work instead of repeatedly
calling it.

On restart, resume from valid completed checkpoints and do not regenerate valid paid assets.

## Final output

Target structure:

```text
output/
├── 01_final/
│   ├── final_master.mp4
│   └── final_no_subtitles.mp4
├── 02_timeline_clips/
├── 03_audio/
│   ├── narration.wav
│   ├── bgm.wav
│   ├── sfx.wav
│   └── final_mix.wav
├── 04_subtitles/
└── 07_editing_data/
    ├── timeline.csv
    ├── timeline.json
    ├── storyboard.md
    └── exception_report.md
```

If final rendering is not available, deliver the plan/assets/timeline and explicit render status.
Never claim a master video exists if it was not rendered.
