import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

export type Tokens = {
  background:string; surface:string; text_primary:string; text_secondary:string; accent:string; border:string; shadow:string;
  radius:number; safe_margin_x:number; safe_margin_y:number; title_size:number; hammer_size:number; body_size:number; caption_size:number;
  font_family:string; motion:{enter_frames:number;exit_frames:number;scale_from:number;slide_px:number};
};

export type VisualSlotProps = {
  visualType:string;
  layout:string;
  headline:string;
  body:string[];
  tokens:Tokens;
  leftTitle?:string;
  rightTitle?:string;
  value?:string;
};

const card=(t:Tokens):React.CSSProperties=>({
  background:t.surface,border:`1px solid ${t.border}`,borderRadius:t.radius,
  boxShadow:`0 18px 60px ${t.shadow}`,padding:'48px 54px'
});

const baseText=(t:Tokens):React.CSSProperties=>({fontFamily:t.font_family,color:t.text_primary,margin:0});

export const VisualSlot:React.FC<VisualSlotProps>=(p)=>{
  const frame=useCurrentFrame(); const {fps}=useVideoConfig(); const t=p.tokens;
  const enter=spring({frame,fps,config:{damping:22,stiffness:120,mass:0.7}});
  const opacity=interpolate(frame,[0,t.motion.enter_frames],[0,1],{extrapolateRight:'clamp'});
  const y=(1-enter)*t.motion.slide_px; const scale=t.motion.scale_from+(1-t.motion.scale_from)*enter;
  const motionStyle:React.CSSProperties={opacity,transform:`translateY(${y}px) scale(${scale})`};

  const body=p.body||[];
  const common=<div style={{...motionStyle,width:'100%'}}>
    <div style={{...baseText(t),fontSize:t.title_size,fontWeight:750,lineHeight:1.08,letterSpacing:'-0.04em'}}>{p.headline}</div>
  </div>;

  let content:React.ReactNode=common;

  if(p.visualType==='HAMMER' || p.layout==='hammer_center'){
    content=<div style={{...motionStyle,textAlign:'center',width:'100%'}}>
      <div style={{...baseText(t),fontSize:t.hammer_size,fontWeight:850,lineHeight:0.95,letterSpacing:'-0.06em'}}>{p.headline}</div>
      {body[0]&&<div style={{...baseText(t),color:t.text_secondary,fontSize:t.caption_size,marginTop:38}}>{body[0]}</div>}
    </div>;
  } else if(p.layout==='comparison_50_50' || p.layout==='comparison_70_30'){
    const left=body.slice(0,Math.ceil(body.length/2)); const right=body.slice(Math.ceil(body.length/2));
    content=<div style={{...motionStyle,width:'100%'}}>
      <div style={{...baseText(t),fontSize:66,fontWeight:760,marginBottom:48}}>{p.headline}</div>
      <div style={{display:'grid',gridTemplateColumns:p.layout==='comparison_70_30'?'7fr 3fr':'1fr 1fr',gap:34}}>
        <div style={card(t)}><div style={{...baseText(t),fontSize:34,color:t.text_secondary,marginBottom:24}}>{p.leftTitle||'以前'}</div>{left.map((x,i)=><div key={i} style={{...baseText(t),fontSize:44,fontWeight:650,margin:'20px 0'}}>{x}</div>)}</div>
        <div style={{...card(t),border:`2px solid ${t.accent}`}}><div style={{...baseText(t),fontSize:34,color:t.accent,marginBottom:24}}>{p.rightTitle||'现在'}</div>{right.map((x,i)=><div key={i} style={{...baseText(t),fontSize:44,fontWeight:700,margin:'20px 0'}}>{x}</div>)}</div>
      </div>
    </div>;
  } else if(p.layout==='steps_vertical'){
    content=<div style={{...motionStyle,width:'100%'}}><div style={{...baseText(t),fontSize:66,fontWeight:760,marginBottom:42}}>{p.headline}</div>
      <div style={{display:'grid',gap:20}}>{body.map((x,i)=><div key={i} style={{...card(t),display:'flex',alignItems:'center',gap:30,padding:'28px 36px'}}><div style={{fontFamily:t.font_family,color:t.accent,fontSize:32,fontWeight:800,width:64}}>{String(i+1).padStart(2,'0')}</div><div style={{...baseText(t),fontSize:42,fontWeight:620}}>{x}</div></div>)}</div>
    </div>;
  } else if(p.layout==='flow_center'){
    content=<div style={{...motionStyle,width:'100%',textAlign:'center'}}><div style={{...baseText(t),fontSize:66,fontWeight:760,marginBottom:56}}>{p.headline}</div>
      <div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:24}}>{body.map((x,i)=><React.Fragment key={i}><div style={{...card(t),padding:'30px 38px',minWidth:220}}><div style={{...baseText(t),fontSize:36,fontWeight:680}}>{x}</div></div>{i<body.length-1&&<div style={{fontSize:54,color:t.accent}}>→</div>}</React.Fragment>)}</div>
    </div>;
  } else if(p.layout==='data_big_number'){
    content=<div style={{...motionStyle,width:'100%',textAlign:'center'}}><div style={{...baseText(t),fontSize:240,fontWeight:880,letterSpacing:'-0.06em',color:t.accent}}>{p.value||p.headline}</div>{body[0]&&<div style={{...baseText(t),fontSize:48,fontWeight:620,marginTop:25}}>{body[0]}</div>}</div>;
  } else if(p.layout==='list_three'){
    content=<div style={{...motionStyle,width:'100%'}}><div style={{...baseText(t),fontSize:70,fontWeight:780,marginBottom:48}}>{p.headline}</div><div style={{display:'grid',gridTemplateColumns:`repeat(${Math.max(1,Math.min(body.length,3))},1fr)`,gap:28}}>{body.slice(0,3).map((x,i)=><div key={i} style={{...card(t),minHeight:250,display:'flex',flexDirection:'column',justifyContent:'space-between'}}><div style={{fontFamily:t.font_family,fontSize:28,color:t.accent,fontWeight:800}}>0{i+1}</div><div style={{...baseText(t),fontSize:44,fontWeight:700,lineHeight:1.15}}>{x}</div></div>)}</div></div>;
  } else {
    content=<div style={{...motionStyle,maxWidth:1450}}><div style={{...baseText(t),fontSize:t.title_size,fontWeight:800,lineHeight:1.05,letterSpacing:'-0.045em'}}>{p.headline}</div>{body.map((x,i)=><div key={i} style={{...baseText(t),fontSize:t.body_size,color:t.text_secondary,marginTop:26,lineHeight:1.32}}>{x}</div>)}</div>;
  }

  return <AbsoluteFill style={{background:t.background,padding:`${t.safe_margin_y}px ${t.safe_margin_x}px`,display:'flex',alignItems:'center',justifyContent:'center',overflow:'hidden'}}>{content}</AbsoluteFill>;
};
