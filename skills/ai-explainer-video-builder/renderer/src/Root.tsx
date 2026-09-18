import React from 'react';
import {Composition} from 'remotion';
import {VisualSlot, VisualSlotProps} from './VisualSlot';

const defaultProps: VisualSlotProps = {
  visualType: 'SLIDE',
  layout: 'statement_left',
  headline: '核心观点',
  body: [],
  tokens: {
    background:'#F7F7F5', surface:'#FFFFFF', text_primary:'#111111', text_secondary:'#696969', accent:'#246BFD',
    border:'#E8E8E5', shadow:'rgba(0,0,0,0.10)', radius:28, safe_margin_x:150, safe_margin_y:100,
    title_size:88, hammer_size:220, body_size:46, caption_size:30,
    font_family:'Inter, PingFang SC, Microsoft YaHei, Noto Sans CJK SC, sans-serif',
    motion:{enter_frames:16,exit_frames:10,scale_from:0.96,slide_px:32}
  }
};

export const Root: React.FC = () => (
  <Composition
    id="VisualSlot"
    component={VisualSlot}
    durationInFrames={1800}
    fps={30}
    width={1920}
    height={1080}
    defaultProps={defaultProps}
  />
);
